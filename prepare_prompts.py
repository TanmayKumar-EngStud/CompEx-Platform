import os
from typing import List, Any
import random
import json
import re

from io_utils import get_json, prettify
from generator import GenQ

warn = prettify('⚠️ Warning:', 'Yellow')
sp_char = ['*']
sp = None

exam_definition, qt_info, prompt_component_info = get_json(
    'exam_definition', 'question_type_info', 'prompt_component_info')


class PromptPrep:
    # Bucket Elimination Data
    true_data = prompt_component_info
    dummy_data = {}  # Working copy
    usage_counts = {
        "themes": {},
        "topic": {},
        "theme-count": 0,
        "topic-count": 0
    }

    @staticmethod
    @staticmethod
    def __pick_vocab_level(difficulty: int) -> int:
        weights = {1: [60, 30, 10],
                   2: [45, 35, 20],
                   3: [30, 40, 30],
                   4: [20, 35, 45],
                   5: [10, 30, 60]}
        return random.choices([1, 2, 3], weights=weights[difficulty])[0]

    @staticmethod
    def _must_get(d: dict, key: str, source: str) -> dict:
        """Return d[key] or raise respective error"""
        try:
            return d[key]
        except:
            raise ValueError(
                f"{prettify(key, 'Magenta')} missing from {prettify(source,'Cyan')}") from None

    @staticmethod
    def __extract_keywords_from_nomenclature(nomenclature: str) -> List[str]:
        """Return all words found between  < ... >  in order."""
        return re.findall(r'<([^<>]+)>', nomenclature)

    @staticmethod
    def __selective_component_info(prompt_component: str, question_type: str):
        """Returns the list of desired element of that component from DUMMY DATA"""
        PromptPrep._init_buckets()
        
        def ___fetch_correct_key():
            """Handles special characters in main Key"""
            base = prompt_component
            for sfx in (['']+sp_char):
                key = base + sfx
                if PromptPrep.dummy_data.get(key, None):
                    if sfx in sp_char:
                        sp = sfx
                    return key
            # Fallback to true data just to check existence if dummy is empty/refilled?
            # Actually if dummy is empty, we should refill it.
            # But here we assume init_buckets handled it.
            raise ValueError(
                f"{prettify('Error:', 'Red', True)} `{prettify(prompt_component, 'Green')}` of {prettify(question_type, 'Magenta')} and it's variants were not found in 'dummy_data' (init failed?)\n ")

        def ___handle_dict_list(selected_component_list: Any):
            """
            it handles prompt_component_list type (both dict and normal list)
            """
            def ____get_favorable_component_list(items: List[str]) -> List[str]:
                if items is None:
                    return []
                    
                if sp in [None]:
                     return [x for x in items if '*' not in x]
                else:
                    return [x for x in items if '*' in x]

            if isinstance(selected_component_list, dict):
                # Return KEYS for dicts, but we need to supply the DICT itself later for subpicking
                favorable = ____get_favorable_component_list(list(selected_component_list.keys()))
                return {k: selected_component_list[k] for k in favorable}
            else:
                return ____get_favorable_component_list(selected_component_list)

        prompt_component_found = ___fetch_correct_key()
        prompt_component_list = []
        
        # We need to iterate over the list in dummy data
        # Note: prompt_component_info structure is top-level keys like "questionTopic" -> list of dicts
        
        # KEY CHANGE: We are accessing DUMMY DATA now
        for prompt_component_options in PromptPrep.dummy_data[prompt_component_found]:
            if question_type in prompt_component_options['QuestionType']:
                # extracting the actual list/content
                content = prompt_component_options['list']
                processed_content = ___handle_dict_list(content)
                
                if isinstance(processed_content, list):
                    prompt_component_list.extend(processed_content)
                elif isinstance(processed_content, dict):
                     # For dicts, we might need to merge or return list of keys?
                     # Existing logic returned a combined dict or list. 
                     # Let's preserve the processed dict structure for the caller
                     if isinstance(prompt_component_list, list):
                         prompt_component_list = {} # Convert to dict if we find dict content
                     prompt_component_list.update(processed_content)
                     
        return prompt_component_list

    @staticmethod
    def _selective_metadata_info(question_type: str) -> dict:
        """returns dictionary of lists mentioning category of metadata"""
        PromptPrep._init_buckets()
        metadataTypes = PromptPrep.dummy_data['metadataType']
        returning_dict = {}
        for metadata in metadataTypes:
            if question_type in metadata['QuestionType']:
                returning_dict[metadata['category']] = metadata['list']
        return returning_dict

    @staticmethod
    def _init_buckets():
        """Initialize or Reset Dummy Data from True Data"""
        import copy
        if not PromptPrep.dummy_data:
            PromptPrep.dummy_data = copy.deepcopy(PromptPrep.true_data)

    @staticmethod
    def _get_bucket_choice(options: list, category: str = "generic", parent_block: dict = None, list_key: str = None) -> str:
        """
        Bucket Elimination Selection:
        1. Select from passed options (which should be from DUMMY data).
        2. Update Usage Counts.
        3. Eliminate if Threshold met (Theme >= 2, Topic >= Proportion).
        """
        PromptPrep._init_buckets()
        
        if not options:
             # Logic to refill if empty is handled by recursive fetch or upper reset
             return ""

        choice = random.choice(options)
        
        # --- Update Counts & Check Elimination ---
        if category == "theme":
            PromptPrep.usage_counts["theme-count"] += 1
            current_count = PromptPrep.usage_counts["themes"].get(choice, 0) + 1
            PromptPrep.usage_counts["themes"][choice] = current_count
            
            # Theme Limit: Remove after 2 uses
            if current_count >= 2:
                if parent_block and list_key and list_key in parent_block:
                     if choice in parent_block[list_key]:
                          parent_block[list_key].remove(choice)
                elif isinstance(options, list):
                     # Try direct removal if options is the mutable list ref
                     if choice in options:
                        options.remove(choice)

        elif category == "topic":
            PromptPrep.usage_counts["topic-count"] += 1
            if choice not in PromptPrep.usage_counts["topic"]:
                PromptPrep.usage_counts["topic"][choice] = {"count": 0, "proportion": 0}
            
            PromptPrep.usage_counts["topic"][choice]["count"] += 1
            
            # Proportion Check Logic would go here
            # For now, we rely on random selection from the pool
        
        return choice

    @staticmethod
    def _nomenclature_to_prompt_mapping(nomenclature: str, question_type: str, difficulty_level: int) -> tuple[str, str, dict]:
        """Returns appropriate prompt of that nomenclature using Bucket Elimination, and a formatted instruction string."""
        
        # Detect Child Context from raw nomenclature BEFORE replacements
        is_child_context = 'child-focused_skill' in nomenclature or 'child' in question_type.lower()

        prompt_components = PromptPrep.__extract_keywords_from_nomenclature(
            nomenclature)
        # Maintaining order and allowing duplicates (e.g., multiple source_info in MSR)
        # EXCLUDE mandatory categories that are handled by manual mapping
        prompt_components = [c for c in prompt_components if c not in {
            'difficulty', 'vocabulary', 'questionTheme', 'questionTopic', 
            'child-focused_skill', 'focused_skill', 'TC_QuestionType', 'RC_QuestionType'
        }]

        # Determine Category for counting/elimination
        def _get_category(comp_name):
            if 'theme' in comp_name.lower(): return 'theme'
            if 'topic' in comp_name.lower(): return 'topic'
            return 'generic'
        
        selected_components = {
            'Theme': None,
            'Topic': None,
            'Sub-topic/Focused Skill': None
        }

        # --- MANDATORY CATEGORY MAPPING ---
        # 1. Theme
        if 'questionTheme' in nomenclature:
            theme_options = PromptPrep.__selective_component_info('questionTheme', question_type)
            selected_theme = PromptPrep._get_bucket_choice(theme_options, category='theme')
            selected_components['Theme'] = selected_theme
            nomenclature = nomenclature.replace('<questionTheme>', selected_theme)
        
        # 2. Topic
        if 'questionTopic' in nomenclature:
            topic_options = PromptPrep.__selective_component_info('questionTopic', question_type)
            # Handle possible dict structure for topics
            if isinstance(topic_options, dict):
                topic_keys = list(topic_options.keys())
                selected_topic = PromptPrep._get_bucket_choice(topic_keys, category='topic')
                
                # Handle Sub-topic
                sub_choices = topic_options[selected_topic]
                sub_options = list(sub_choices.keys()) if isinstance(sub_choices, dict) else list(sub_choices)
                selected_sub = PromptPrep._get_bucket_choice(sub_options, category='topic')
                
                selected_components['Topic'] = selected_topic
                selected_components['Sub-topic/Focused Skill'] = selected_sub
                
                # Replace topic in nomenclature (handle potential sub-topic placeholders if any)
                display_topic = f"{selected_topic} > - <sub-questionTopic - {selected_sub}" if 'sub-questionTopic' in nomenclature else selected_topic
                nomenclature = nomenclature.replace('<questionTopic>', display_topic)
            else:
                selected_topic = PromptPrep._get_bucket_choice(topic_options, category='topic')
                selected_components['Topic'] = selected_topic
                nomenclature = nomenclature.replace('<questionTopic>', selected_topic)

        # 3. Skill (Verbal / Child)
        for skill_tag in ['focused_skill', 'child-focused_skill', 'TC_QuestionType', 'RC_QuestionType']:
             if skill_tag in nomenclature:
                skill_options = PromptPrep.__selective_component_info(skill_tag, question_type)
                selected_skill = PromptPrep._get_bucket_choice(skill_options, category='topic')
                selected_components['Sub-topic/Focused Skill'] = selected_skill
                # Consistency: Use Skill as Topic for Verbal if Topic is empty
                if not selected_components.get('Topic'):
                    selected_components['Topic'] = selected_skill
                nomenclature = nomenclature.replace(f'<{skill_tag}>', selected_skill)

        for prompt_component in prompt_components:
            prompt_component_list = PromptPrep.__selective_component_info(
                prompt_component, question_type)
            selected_value = ""
            
            category = _get_category(prompt_component)

            if isinstance(prompt_component_list, dict):
                # 1. Pick Main Topic
                topic_options = list(prompt_component_list.keys())
                # Pass the list for selection, but removal will be global lookup
                selected_choice = PromptPrep._get_bucket_choice(topic_options, category=category)
                if not selected_choice:
                    topic_options = list(prompt_component_list.keys()) # Refresh
                    selected_choice = random.choice(topic_options) # Fallback

                sub_choices = prompt_component_list[selected_choice]
                suffix = selected_choice[-1]
                if suffix in sp_char:
                    sp = suffix
                selected_value += f"{selected_choice}"
                
                # Store Main Selection (PROTECTED)
                label = 'Theme' if category == 'theme' else 'Topic'
                if not selected_components.get(label):
                    selected_components[label] = selected_choice

                # 2. Pick Sub-Topic
                subs = f"sub-{prompt_component}"
                
                if isinstance(sub_choices, dict):
                     sub_options = list(sub_choices.keys())
                     selected_sub_choice = PromptPrep._get_bucket_choice(sub_options, category='topic') # Subtopics usually topics
                else:
                     sub_options = list(sub_choices)
                     selected_sub_choice = PromptPrep._get_bucket_choice(sub_options, category='topic')

                selected_value += f"> - <{subs} - {selected_sub_choice}"
                # Update Skill if it's currently None
                if selected_components.get('Sub-topic/Focused Skill') is None:
                    selected_components['Sub-topic/Focused Skill'] = selected_sub_choice
                
                if isinstance(sub_choices, dict):
                    pass 

                nomenclature = nomenclature.replace(
                    prompt_component, selected_value)
            else:
                try:
                    # Flat list case
                    selected_value = PromptPrep._get_bucket_choice(prompt_component_list, category=category)
                except Exception as e:
                     # Fallback
                    print(f"Bucket selection failed: {e}")
                    selected_value = random.choice(prompt_component_list)
                
                # PROTECTED assignment to selected_components
                if 'theme' in prompt_component.lower():
                    if not selected_components.get('Theme'):
                        selected_components['Theme'] = selected_value
                elif 'skill' in prompt_component.lower():
                    if not selected_components.get('Sub-topic/Focused Skill'):
                        selected_components['Sub-topic/Focused Skill'] = selected_value
                else:
                    # Generic component (like Style) should NOT overwrite Topic if Topic already exists
                    if not selected_components.get('Topic'):
                        selected_components['Topic'] = selected_value

                # --- Graph Randomization Injection ---
                is_graph_tag = any(term in selected_value.lower() for term in ['graph', 'chart'])
                display_value = selected_value
                if is_graph_tag:
                    graph_types = prompt_component_info.get('graphTypes', [])
                    if graph_types:
                        selected_graph = random.choice(graph_types)
                        display_value = f"{selected_value} ({selected_graph})"
                        if 'Graph Types' not in selected_components:
                            selected_components['Graph Types'] = []
                        selected_components['Graph Types'].append(selected_graph)

                nomenclature = nomenclature.replace(
                    f"<{prompt_component}>", f"<{display_value}>", 1)
                    
        nomenclature = nomenclature.replace('<difficulty>', f'<{difficulty_level}>').replace(
            '<vocabulary>', f'<{PromptPrep.__pick_vocab_level(difficulty_level)}>')
        
        # --- Dichotomous Type Logic ---
        dichotomous_pair = None
        # Check if question type is dichotomous
        dichotomous_registry = prompt_component_info.get('dichotomousPairs', [])
        for entry in dichotomous_registry:
            if question_type in entry.get('QuestionType', []):
                dichotomous_pair = random.choice(entry.get('list', []))
                break
        
        if dichotomous_pair:
             selected_components['dichotomous-type'] = {
                 "positive": dichotomous_pair['positive'],
                 "negative": dichotomous_pair['negative']
             }
             # Add to nomenclature for the model to see
             label = dichotomous_pair.get('label', 'Yes/No')
             nomenclature += f" - <Dichotomous Type: {label}>"

        # Build Explicit Instruction String
        instruction_parts = [
            "[IMPORTANT]: Make sure to fulfil the following request:",
            "*Constraint*: The 'question' text MUST NOT exceed 60 words."
        ]
        if 'Theme' in selected_components:
            instruction_parts.append(f"*Theme*: {selected_components['Theme']}")
        if 'Topic' in selected_components:
            instruction_parts.append(f"*Topic*: {selected_components['Topic']}")
        if 'Sub-topic/Focused Skill' in selected_components:
            instruction_parts.append(f"*Sub-topic/Focused Skill*: {selected_components['Sub-topic/Focused Skill']}")
        if 'Graph Types' in selected_components:
            instruction_parts.append(f"*Requested Visuals*: {', '.join(selected_components['Graph Types'])}")
            
        instruction_str = " ".join(instruction_parts)
        
        # --- Fail-Fast Tag Validation ---
        q_meta = qt_info.get(question_type, {}).get('type', 'simple')
        
        # Override: If nomenclature implies child (has child skill) or type explicitly says child
        if is_child_context:
            q_meta = 'child'
        
        missing = []
        
        if q_meta in ['simple', 'parent']:
            if not selected_components.get('Theme'): missing.append('Theme')
            if not selected_components.get('Topic'): missing.append('Topic')
        elif q_meta == 'child':
            if not selected_components.get('Sub-topic/Focused Skill'):
                missing.append('Sub-topic/Focused Skill')
        
        if missing:
            raise ValueError(f"CRITICAL: Prompt Mapping failed for {prettify(question_type, 'Magenta')}. "
                             f"Missing mandatory tag categories: {prettify(missing, 'Red')}. "
                             f"Current Tags: {selected_components}")

        return nomenclature, instruction_str, selected_components
        # now for every exam we are having external data.

    @staticmethod
    def _get_child_count(nomenclature: str, question_type: str, parent_prompt: str, child_info: dict) -> int:
        default_value = 2
        if (child_info.get('child-count', None)):
            return child_info.get('child-count')
            
        # Parse [Label: <Placeholder>] from nomenclature
        # Matches [Type: <RC_QuestionType>] -> ('Type', 'RC_QuestionType')
        nomenclature_pairs = re.findall(r'\[([^:]+):\s*<([^>]+)>\]', nomenclature)
        nom_map = {label.strip(): placeholder.strip() for label, placeholder in nomenclature_pairs}
        
        # Parse [Label: Value] from parent_prompt
        # Matches [Type: RC-M] -> ('Type', 'RC-M')
        # Uses greedy match for values but respects closing ]
        prompt_pairs = re.findall(r'\[([^:]+):\s*([^\]]+)\]', parent_prompt)
        prompt_map = {label.strip(): value.strip() for label, value in prompt_pairs}

        child_question_count_keys = get_json('child_question_count')[0].keys()
        
        # Find which placeholder in nomenclature corresponds to a key in child_question_count
        target_placeholder = None
        for placeholder in nom_map.values():
            if placeholder in child_question_count_keys:
                target_placeholder = placeholder
                break
        
        if not target_placeholder:
             # Default fallback if no dependent count identifier found
             return default_value
             
        # Find the Label for this Placeholder
        target_label = next((k for k, v in nom_map.items() if v == target_placeholder), None)
        
        if not target_label or target_label not in prompt_map:
             # Should not happen if prompt follows nomenclature
             print(f"{warn} Could not find label '{target_label}' in generated prompt for child count lookup.")
             return default_value
             
        selected_value = prompt_map[target_label]
        
        child_count_data = get_json('child_question_count')[0]
        for option in child_count_data[target_placeholder]:
             if option['value'] == selected_value:
                 return option['count']

        raise ValueError(
            f"{warn} child count for {prettify(target_placeholder, 'Yellow')} : {prettify(selected_value, 'Magenta')} was not found, issue is in {prettify('child_question_count.json','Cyan')}'s formatting\nThis is the prompt that we got:-\n\t{prettify(parent_prompt, 'Green')}")

    @staticmethod
    def _remove_extra_and_shuffle_created_prompts(section_prompt_dictionary: str, extras: int):
        if extras < 0:
            raise ValueError(
                f"Due to some reason, the total number of prompts generated is being less, received\n\t{prettify('extras', 'Yellow')}: {prettify(extras, 'Red')} for section {prettify(section_prompt_dictionary['section'], 'Red', True)}\ncheck if total count of all total question types is not less then it's respective total in {prettify('exam_definition.json', 'Cyan')}")
        # here we need to find all the prompts that are simple in nature
        # selected_random_question_types =random.choice(section_prompt_dictionary)
