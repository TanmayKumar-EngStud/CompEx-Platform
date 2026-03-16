
import os
import re
import json
import time
import asyncio
from collections import deque
from typing import Dict, Any, Optional, Union, List, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

from io_utils import prettify

# Load environment variables
project_root = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

import threading

# ─────────────────────────────────────────────
#  Per-provider RPM limiter (leaky bucket — evenly spaced starts)
# ─────────────────────────────────────────────
class _AsyncRateLimiter:
    """Evenly spaces API call *starts* to stay under the provider RPM cap."""
    def __init__(self, max_calls: int, period: float = 60.0):
        self._interval = period / max_calls
        self._lock = asyncio.Lock()
        self._next_allowed: float = 0.0

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            wait = self._next_allowed - now
            if wait > 0:
                await asyncio.sleep(wait)
            self._next_allowed = time.monotonic() + self._interval


# ─────────────────────────────────────────────
#  Output-token budget tracker (sliding 60-second window)
# ─────────────────────────────────────────────
class _OutputTokenBudget:
    """
    Sliding-window output-token tracker.

    Before each call it checks whether adding `max_tokens` would exceed
    Mercury's 100 K output-tokens/min limit.  If so it waits until old
    entries expire.  After each call it corrects the reservation with the
    actual tokens used.

    Mercury Pay-As-You-Go:  100,000 output tokens / minute.
    We use 90,000 as the safety ceiling (90 % of the hard limit).
    """
    WINDOW = 60.0          # seconds
    SAFETY = 0.90          # fraction of limit we allow ourselves

    def __init__(self, max_output_per_minute: int):
        self._ceiling = int(max_output_per_minute * self.SAFETY)
        self._lock = asyncio.Lock()
        # deque of (mono_timestamp, tokens_reserved)
        self._window: deque = deque()

    def _evict(self, now: float):
        """Remove entries older than the sliding window."""
        cutoff = now - self.WINDOW
        while self._window and self._window[0][0] < cutoff:
            self._window.popleft()

    def _used(self) -> int:
        return sum(t for _, t in self._window)

    async def reserve(self, max_tokens: int) -> int:
        """
        Block until there is budget, then reserve `max_tokens`.
        Returns the index of the reservation so it can be corrected later.
        """
        while True:
            async with self._lock:
                now = time.monotonic()
                self._evict(now)
                if self._used() + max_tokens <= self._ceiling:
                    self._window.append((now, max_tokens))
                    return len(self._window) - 1   # reservation index (not used for correction, that's fine)
                # Calculate how long until the oldest entry expires
                oldest_ts = self._window[0][0]
                wait = (oldest_ts + self.WINDOW) - now + 0.1
            print(f"      {prettify('⏳ Token budget', 'Yellow')}: "
                  f"output-TPM near limit — waiting {wait:.1f}s for quota to refresh...")
            await asyncio.sleep(max(0.5, wait))

    def correct(self, actual_tokens: int, max_tokens: int):
        """
        After a call completes replace the over-estimated reservation
        with the actual token count.  Best-effort — if the window entry
        already expired we just ignore it.
        """
        # Walk backwards and find the most recent max_tokens reservation
        for i in range(len(self._window) - 1, -1, -1):
            ts, reserved = self._window[i]
            if reserved == max_tokens:
                self._window[i] = (ts, actual_tokens)
                return


# ─────────────────────────────────────────────
#  Global state (provider-scoped singletons)
# ─────────────────────────────────────────────
_mercury_rate_limiter: Optional[_AsyncRateLimiter] = None
_mercury_concurrency_sem: Optional[asyncio.Semaphore] = None
_mercury_token_budget: Optional[_OutputTokenBudget] = None

_async_client_instance = None
_client_lock = threading.Lock()
_model_quants = "deepseek-reasoner"
_model_verbal = "deepseek-chat"
_provider_name = "Deepseek"
_active_rate_limiter: Optional[_AsyncRateLimiter] = None

# ── 429 global pause gate ────────────────────
# One lock serialises pause-event registration so concurrent tasks that
# all hit 429 at the same moment only count as ONE pause event, not N.
_global_pause_lock = asyncio.Lock()
_global_pause_until: float = 0.0
_pause_event_count: int = 0          # counts distinct quota-reset cycles
_MAX_PAUSE_EVENTS: int = 3           # hard shutdown after 3 pause events with no progress


def _get_mercury_concurrency_sem() -> asyncio.Semaphore:
    global _mercury_concurrency_sem
    if _mercury_concurrency_sem is None:
        n = int(os.getenv("Mercury_MAX_CONCURRENT", "5"))
        _mercury_concurrency_sem = asyncio.Semaphore(n)
        print(f"{prettify('LLM', 'Cyan')}: Mercury concurrency cap = {n} simultaneous calls")
    return _mercury_concurrency_sem


def _get_mercury_token_budget() -> _OutputTokenBudget:
    global _mercury_token_budget
    if _mercury_token_budget is None:
        # 100 K output tokens / min is the Pay-As-You-Go hard limit
        _mercury_token_budget = _OutputTokenBudget(max_output_per_minute=100_000)
        print(f"{prettify('LLM', 'Cyan')}: Mercury output-TPM budget = 90,000 tokens/min (90% of 100K limit)")
    return _mercury_token_budget


# ─────────────────────────────────────────────
#  Provider detection + client singleton
# ─────────────────────────────────────────────
def get_deepseek_client() -> AsyncOpenAI:
    global _async_client_instance, _model_quants, _model_verbal
    global _provider_name, _active_rate_limiter, _mercury_rate_limiter

    if _async_client_instance is None:
        with _client_lock:
            if _async_client_instance is None:
                active_provider = os.getenv("ACTIVE_provider", "").strip().lower()
                mercury_key = os.getenv("Mercury_API_KEY")
                deepseek_key = os.getenv("Deepseek_API_KEY")
                use_mercury = (active_provider == "mercury") or (not active_provider and mercury_key)

                if use_mercury:
                    api_key = mercury_key
                    if not api_key:
                        raise ValueError("Mercury_API_KEY missing in .env")
                    base_url = os.getenv("API_BASE_URL", "https://api.inceptionlabs.ai/v1")
                    mercury_model = os.getenv("Mercury_Model", "mercury-2")
                    _model_quants = mercury_model
                    _model_verbal = mercury_model
                    _provider_name = "Mercury"

                    # RPM cap from .env, hard ceiling at 999
                    mercury_rpm = min(int(os.getenv("Mercury_RPM", "900")), 999)
                    if _mercury_rate_limiter is None:
                        _mercury_rate_limiter = _AsyncRateLimiter(max_calls=mercury_rpm, period=60.0)
                        print(f"{prettify('LLM', 'Cyan')}: Mercury RPM cap = {mercury_rpm} req/min")
                    _active_rate_limiter = _mercury_rate_limiter

                else:
                    api_key = deepseek_key
                    if not api_key:
                        raise ValueError("Deepseek_API_KEY invalid or missing in .env")
                    base_url = os.getenv("API_BASE_URL", "https://api.deepseek.com")
                    _model_quants = os.getenv("MODEL_Quants", "deepseek-reasoner")
                    _model_verbal = os.getenv("MODEL_Verbal", "deepseek-chat")
                    _provider_name = "Deepseek"
                    _active_rate_limiter = None

                _async_client_instance = AsyncOpenAI(api_key=api_key, base_url=base_url)
                print(f"{prettify('LLM', 'Cyan')}: provider={_provider_name} | "
                      f"base_url={base_url} | quants={_model_quants} | verbal={_model_verbal}")

    return _async_client_instance


def get_deepseek_model(question_type: str) -> Tuple[str, float]:
    """
    Returns (model_name, temperature).
    Mercury only supports temperature 0.5–1.0; values outside that range
    cause BAD REQUEST.  We clamp automatically so .env values stay unchanged.
    """
    get_deepseek_client()  # ensure initialised

    qt_lower = question_type.lower()
    is_quant = any(x in qt_lower for x in [
        "quant", "math", "data sufficiency", "problem solving",
        "numerical", "integrated reasoning", "table", "graph", "chart", "two-part"
    ])

    temp = float(os.getenv("temp_Quants", 0.0)) if is_quant else float(os.getenv("temp_Verbal", 1.5))
    model = _model_quants if is_quant else _model_verbal

    if _provider_name == "Mercury":
        temp = max(0.5, min(1.0, temp))   # Mercury: 0.5–1.0

    return model, temp


# ─────────────────────────────────────────────
#  Session class
# ─────────────────────────────────────────────
class DeepseekSession:
    """Stateful session for a single question generation flow."""

    def __init__(self, question_type: str):
        self.client = get_deepseek_client()
        self.question_type = question_type
        self.model, self.temperature = get_deepseek_model(question_type)
        self.messages = []
        self.system_instructions_set = False

    def set_system_instruction(self, instruction: str):
        if not self.system_instructions_set:
            # For Mercury: append a JSON-output requirement to the system prompt
            # because Mercury doesn't support response_format=json_object.
            if _provider_name == "Mercury":
                instruction = (instruction.rstrip() +
                               "\n\nCRITICAL: You MUST always respond with ONLY valid JSON. "
                               "No markdown fences, no explanation, no preamble. "
                               "Pure JSON only.")
            self.messages.insert(0, {"role": "system", "content": instruction})
            self.system_instructions_set = True

    async def generate_component(self,
                                  instruction_statement: str,
                                  expected_output: Union[str, Dict],
                                  context: Optional[Dict] = None) -> Tuple[Union[str, Dict], Dict]:
        """
        Generates one component in the conversation.

        Rate-limiting strategy for Mercury:
          1. Output-token budget (sliding 60-s window, 90 K ceiling) — blocks
             before each call if we'd exceed Mercury's 100 K output-TPM limit.
          2. Concurrency semaphore — caps simultaneously in-flight calls.
          3. Leaky-bucket RPM gate — evenly spaces call starts.
          4. 429 pause gate — if Mercury still rejects, pause ALL tasks for 65 s
             and retry.  Only distinct pause *events* count toward shutdown
             (5 concurrent tasks hitting 429 at once = 1 event, not 5).
        """
        global _global_pause_until, _pause_event_count

        component_type = context.get('component_type', 'Unknown') if context else 'Unknown'
        max_output = int(os.getenv("Mercury_MAX_OUTPUT_TOKENS", "600")) if _provider_name == "Mercury" else 4096

        # Per-call user message
        json_nudge = (" Respond with ONLY valid JSON — no markdown, no explanation."
                      if _provider_name == "Mercury" else "")
        user_content = (
            f"### focus: STRICTLY generate ONLY the requested {component_type}. "
            f"Do NOT wrap in any root keys. "
            f"Do NOT repeat previous components or generate the whole question structure.{json_nudge}\n"
            f"Expected JSON output format:\n{json.dumps(expected_output, indent=2)}\n\n"
            f"Instruction for {component_type}:\n{instruction_statement}"
        )
        if context and context.get('metadata_content'):
            user_content += f"\n\nMetadata Context:\n{json.dumps(context['metadata_content'], indent=2)}"
        self.messages.append({"role": "user", "content": user_content})

        # Mercury-specific infrastructure
        _concurrency_sem = _get_mercury_concurrency_sem() if _provider_name == "Mercury" else None
        _token_budget   = _get_mercury_token_budget()    if _provider_name == "Mercury" else None

        async def _do_api_call():
            kwargs = {
                "model":       self.model,
                "messages":    self.messages,
                "temperature": self.temperature,
                "stream":      False,
            }
            if _provider_name == "Mercury":
                kwargs["max_tokens"] = max_output
            # response_format=json_object is NOT supported by Mercury — omit it.
            # For Deepseek, use it unless explicitly disabled.
            if _provider_name != "Mercury" and os.getenv("DISABLE_JSON_MODE", "false").strip().lower() != "true":
                kwargs["response_format"] = {"type": "json_object"}
            return await self.client.chat.completions.create(**kwargs)

        # ── Retry loop ────────────────────────────────────────────────
        for attempt in range(1, _MAX_PAUSE_EVENTS + 2):   # one more than max events

            # ① Wait out any active global pause
            now = time.monotonic()
            if _global_pause_until > now:
                wait_secs = _global_pause_until - now
                await asyncio.sleep(wait_secs)

            # ② Output-token budget gate (Mercury only)
            if _token_budget is not None:
                await _token_budget.reserve(max_output)

            # ③ RPM gate
            if _active_rate_limiter is not None:
                await _active_rate_limiter.acquire()

            # ④ Make the call under the concurrency semaphore
            try:
                if _concurrency_sem is not None:
                    async with _concurrency_sem:
                        response = await _do_api_call()
                else:
                    response = await _do_api_call()

                actual_output_tokens = response.usage.completion_tokens

                # Correct the budget reservation with actual tokens used
                if _token_budget is not None:
                    _token_budget.correct(actual_output_tokens, max_output)

                content = response.choices[0].message.content
                parsed_data = self._parse_json(content)
                self.messages.append({"role": "assistant", "content": content})

                stats = {
                    'input_tokens':  response.usage.prompt_tokens,
                    'output_tokens': actual_output_tokens,
                }
                
                # Reset pause events counter on successful request
                global _pause_event_count
                _pause_event_count = 0
                
                return parsed_data, stats

            except Exception as e:
                err_str = str(e)
                is_rate_limit = ('429' in err_str or
                                 'rate_limit' in err_str.lower() or
                                 'rate limit' in err_str.lower())

                if not is_rate_limit:
                    print(f"{prettify(f'LLM Error [{_provider_name}]', 'Red')}: {e}")
                    raise e

                # ── 429 hit ──────────────────────────────────────────
                pause_secs = 65

                # Register a pause EVENT (not per-task — multiple tasks hitting
                # 429 simultaneously count as ONE event, preventing premature shutdown).
                triggered_new_event = False
                async with _global_pause_lock:
                    now_ts = time.monotonic()
                    if now_ts >= _global_pause_until:
                        # This is genuinely a new pause event
                        _global_pause_until = now_ts + pause_secs
                        _pause_event_count += 1
                        triggered_new_event = True

                if triggered_new_event:
                    if _pause_event_count >= _MAX_PAUSE_EVENTS:
                        import time as _time
                        print(f"\n{'='*60}")
                        print(f"  {prettify('SAFETY SHUTDOWN', 'Red', True)}")
                        print(f"  {_pause_event_count} quota-reset cycles failed — Mercury output-TPM")
                        print(f"  is exhausted beyond recovery for this session.")
                        print(f"  ⏳ Wait a few minutes before restarting.")
                        print(f"  🕐 Safe restart: {_time.strftime('%H:%M:%S', _time.localtime(_time.time() + 180))}")
                        print(f"{'='*60}\n")
                        import os as _os
                        _os._exit(1)
                    print(f"\n      {prettify('⏸ 429 PAUSE EVENT', 'Yellow', True)} #{_pause_event_count}/{_MAX_PAUSE_EVENTS}: "
                          f"Mercury output-TPM quota hit — pausing ALL calls for {pause_secs}s. "
                          f"(API Error: {err_str})")

                await asyncio.sleep(pause_secs)

        raise RuntimeError(f"Exhausted pause retries for {component_type}")

    def _parse_json(self, content: str) -> Union[Dict, str]:
        content = content.strip()
        # Strip markdown fences
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Try direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try fixing unescaped backslashes
        try:
            fixed = re.sub(r'\\(?![\\"/bfnrtu])', r'\\\\', content)
            return json.loads(fixed)
        except Exception:
            pass

        # Last resort: extract first JSON object or array
        for pattern in (r'\{.*\}', r'\[.*\]'):
            m = re.search(pattern, content, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group())
                except Exception:
                    pass

        return content
