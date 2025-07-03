# Special Character Handling Instructions for AI System

## CRITICAL: JSON Response Format Requirements

When generating JSON responses, you MUST follow these character replacement rules to prevent JSON parsing failures:

## Required Character Replacements

### Basic Formatting
- Instead of `<br>` → Use `<br>`
- Instead of `<strong>` → Use `<strong>`  
- Instead of `</strong>` → Use `</strong>`
- Instead of `<em>` → Use `<em>`
- Instead of `</em>` → Use `</em>`
- Instead of `<b>` → Use `<b>`
- Instead of `</b>` → Use `</b>`
- Instead of `<i>` → Use `<i>`
- Instead of `</i>` → Use `</i>`

### Critical Quote Characters
- Instead of single quote `'` → Use `<s_quote>`
- Instead of double quote `"` → Use `<d_quote>`  
- Instead of backtick `` ` `` → Use `<tilda>`

### Mathematical Symbols
- Instead of `·` → Use `<cdot>`
- Instead of `×` → Use `<times>`
- Instead of `÷` → Use `<div>`
- Instead of `≠` → Use `<ne>`
- Instead of `≤` → Use `<le>`
- Instead of `≥` → Use `<ge>`
- Instead of `±` → Use `<pm>`
- Instead of `∞` → Use `<infinity>`
- Instead of `π` → Use `<pi>`
- Instead of `√` → Use `<sqrt>`
- Instead of `≈` → Use `<approx>`

### Currency and Special Characters  
- Instead of `$` → Use `<dollar>`
- Instead of `%` → Use `<percent>`
- Instead of `°` → Use `<degree>`
- Instead of `—` → Use `<dash>`
- Instead of `–` → Use `<ndash>`
- Instead of `…` → Use `<ellipsis>`
- Instead of `→` → Use `<arrow_right>`

## EXAMPLES

### ❌ INCORRECT (Will cause JSON parsing to fail):
```json
{
  "solution": "Step 1: Calculate $5 × 3 = 15$.<br><strong>Step 2:</strong> The answer is "correct"."
}
```

### ✅ CORRECT (Will parse successfully):
```json
{
  "solution": "Step 1: Calculate <dollar>5 <times> 3 = 15<dollar>.<br><strong>Step 2:</strong> The answer is <d_quote>correct<d_quote>."
}
```

## WHY THIS IS CRITICAL

The system uses automated JSON parsing that fails when encountering:
1. Unescaped quotes within JSON strings
2. Special Unicode characters that break JSON encoding
3. HTML entities that create parsing ambiguity
4. Mathematical symbols that interfere with JSON structure

## IMPLEMENTATION

This tag system is automatically processed by the `refine_response` function which:
1. Extracts JSON from your response
2. Replaces all custom tags with actual characters
3. Returns properly formatted, parseable JSON

## REMEMBER

- ALWAYS use these tags in your JSON responses
- ESPECIALLY important for "solution" fields which often contain mathematical content
- The system will automatically convert tags to proper characters after JSON parsing
- Failure to follow this will result in complete response parsing failure

## Tags Reference List

All available tags are defined in `/core/utilities/tags_char.json`. When in doubt, use the tag format: `<tagname>` for any special character.