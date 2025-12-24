"""
    This file will have all the functions and operations regarding json read write, and simple print prettifier as well.
"""

import json
import os
import re
import inspect
from typing import List, Any, Literal, Optional, Iterable
script_dir = os.path.dirname(os.path.abspath(__file__))
ColorName = Literal["Red", "Green",
                    "Yellow", "Blue", "Magenta", "Cyan"]


def extract_blocks(var: str, template: str) -> str:
    """Return the contents of every {{#if_<var>}} … {{/if_<var>}} block."""
    blocks = re.findall(rf'\{{{{#if_{re.escape(var)}\}}\}}(.*?)\{{{{/if_{re.escape(var)}\}}\}}',
                        template, re.S)
    return ''.join(blocks)


def build_template(exam: str,
                   qtype: str,
                   req: str,
                   rand_var: Optional[str],
                   template: str) -> str:
    """Remove every conditional block except those matching exam, qtype, req,
    then append the requested blocks and collapse extra blank lines."""
    # 1. keep only unconditional text
    base = re.sub(r'\{\{#if_.*?\}\}.*?\{\{/if_.*?\}\}',
                  '', template, flags=re.S)
    # 2. collect requested blocks
    blocks = ''.join(
        extract_blocks(v, template)
        for v in (exam, qtype, req, rand_var)
        if v not in (None, '')
    )
    # 3. merge and trim blank lines
    merged = base + blocks
    merged = re.sub(r'\n\s*\n+', '\n', merged)  # collapse ≥2 newlines → 1
    return merged.strip()


def prettify(string: Any, color: ColorName, bold: bool = False):
    """
    ### Follow this color mapping:-
        1. Path: Cyan
        2. Variable: Yellow
        3. Value: Magenta
        4. Error: Red
        5. Success: Green
    """

    prefix = '\033['
    color_map = {
        "Red": "31m",
        "Green": "32m",
        "Yellow": "33m",
        "Blue": "34m",
        "Magenta": "35m",
        "Cyan": "36m"
    }
    b = '1;' if bold else ''
    postfix = prefix + "0m"
    text = str(string)
    return f'{prefix}{b}{color_map[color]}{text}{postfix}'


def get_json(*filenames: str) -> List[Any]:
    """
    give filename directly which is stored in json_files and don't add extension

    Args:

        filename list(str): 
            file name without extension in a list

    Returns:

        data: 
            Python Object
    """

    loaded_data = []
    for filename in filenames:
        file = os.path.join(script_dir, 'json_files', filename+'.json')
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            loaded_data.append(data)
        except FileNotFoundError:
            print(
                f"\033[\1;31mWarning:\033[0m File not found for \033[1;31m'{filename}'\033[0m. Skipping.")
        except json.JSONDecodeError:
            print(
                f"\033[\1;31mWarning:\033[0m Invalid JSON format in \033[1;31m'{filename}.json'\033[0m. Skipping.")
        except Exception as e:
            print(
                f"An unexpected error occurred while processing \033[1;31m'{filename}.json'\033[0m: {e}")
    return loaded_data


QuestionComponent = Literal['QuestionMetadata', 'QuestionText',
                            'QuestionTitle', 'QuestionSolution', 'QuestionOptions/Answer']


def _get_Template(file_path: str,
                  question_component: QuestionComponent,
                  filename: str,
                  exam_type: str,
                  Section_name: str,
                  question_type: str,
                  variable: Optional[str],
                  type: Optional[str] = None,
                  item: Optional[str] = None,
                  rand_var: Optional[str] = None):
    if exam_type is None:
        raise ValueError("exam_type was not mentioned, received None")
    other_file_path = file_path
    # Resolve path based on file extension (check for template/schema subfolders first)
    if filename.endswith('.template'):
        candidate = os.path.join(file_path, 'template', filename)
        file_path = candidate if os.path.exists(candidate) else os.path.join(file_path, filename)
    elif filename.endswith('.schema'):
        candidate = os.path.join(file_path, 'schema', filename)
        file_path = candidate if os.path.exists(candidate) else os.path.join(file_path, filename)
    else:
        file_path = os.path.join(file_path, filename)
    try:
        with open(file_path, 'r') as f:
            component_template = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"component {prettify(question_component, 'Yellow')} -> {prettify(filename, 'Magenta')} not found in component_templates folder inside json_files\nfile_path:- {prettify(file_path, 'Cyan')}")

    if variable not in [None, '']:
        # now from the component template we need to handle these variables.
        if type is None:
            raise ValueError(
                f"Missing metadata type for component {prettify(question_component, 'Yellow')}")
        var_path = os.path.join(other_file_path, f'{type}.json')
        with open(var_path, 'r') as f:
            replaced_value: Any = json.load(f)
        if replaced_value.get(item, None) is None:
            raise ValueError(
                f"the file path: {prettify(var_path, 'Cyan')}\nis not having {prettify(item, 'Red')} as it's primary key\nfor generation of question_component: {prettify(question_component, 'Yellow')}")
        replaced_value = json.dumps(replaced_value.get(item), indent=2)
        component_template = component_template.replace(
            f'<{variable}>', replaced_value)

    # Check both root and template folder for generic template
    generic_template = os.path.join(other_file_path, 'template', 'generic.txt.template')
    if not os.path.exists(generic_template):
        generic_template = os.path.join(other_file_path, 'generic.txt.template')
    try:
        with open(generic_template) as f:
            generic_philosophy_template = f.read()
    except:
        generic_philosophy_template = ''
        pass
    component_template = component_template.replace(
        """{{GENERIC_PHILOSOPHY_TEMPLATE}}""", generic_philosophy_template)
    component_template = build_template(
        exam_type,
        question_type.lower().replace(' ', '_'),
        Section_name.lower().replace(' ', '_'),
        rand_var,
        component_template)
    return component_template


def get_Component_Template(question_component: QuestionComponent,
                           filename: str,
                           exam_type: str,
                           Section_name: str,
                           question_type: str,
                           variable: Optional[str],
                           type: Optional[str] = None,
                           item: Optional[str] = None,
                           rand_var: Optional[str] = None) -> str:
    """
    Provide question component name, filename and get it's respective RAW Data.
        Args: 
            question_component: name of the QuestionComponent
            filename: name of the file given in question_component_types 'file-name'
            exam_type: mention the name of exam as well. 
            variable: variable for that component as string
            type: what Metadata type (only for QuestionMetadata)
            item: what Item from Metadata type (only for QuestionMetadata)

        Returns:
            component_template : returns component template in clean Format.
    """

    file = os.path.join(script_dir, 'json_files', 'component_templates', str.replace(
        question_component, '/', '|'))
    return _get_Template(file_path=file,
                         question_component=question_component,
                         filename=filename,
                         exam_type=exam_type,
                         Section_name=Section_name,
                         question_type=question_type,
                         variable=variable,
                         type=type,
                         item=item,
                         rand_var=rand_var)


def get_Question_Template(question_component: QuestionComponent,
                          filename: str,
                          exam_type: str,
                          Section_name: str,
                          question_type: str,
                          variable: Optional[str],
                          type: Optional[str] = None,
                          item: Optional[str] = None,
                          rand_var: Optional[str] = None):
    file = os.path.join(script_dir, 'json_files',
                        'question_type_templates')
    return _get_Template(file_path=file,
                         question_component=question_component,
                         filename=filename,
                         exam_type=exam_type,
                         Section_name=Section_name,
                         question_type=question_type,
                         variable=None,
                         type=type,
                         item=item,
                         rand_var=rand_var)


def record(value: Any,
           fname: Optional[str] = None,
           addresses: Optional[Iterable[str]] = None):
    """
        For logging, to record any kind of value in json file with file name as **fname** belonging to **addresses** list sequentially
        Root folder is the default address.
    """
    frame = inspect.currentframe()
    caller = frame.f_back if frame else None
    func_name = caller.f_code.co_name if caller else 'unknown'
    if func_name == 'unknown':
        raise ValueError(f"""we are getting an unknown value for func_name.
                            The value is:-
                            {prettify(json.dumps(value, indent= 2), 'Magenta')}
                            fname: {prettify(fname, 'Yellow')}
                         """)
    path_segments = tuple(addresses or ())
    path_segments = tuple(addresses or ())
    base = os.path.join(script_dir, 'log_json_files', func_name, *path_segments)
    os.makedirs(base, exist_ok=True)
    ext = 'txt' if isinstance(value, str) else 'json'
    filename = f'{fname or "record"}.{ext}'
    path = os.path.join(base, filename)
    with open(path, 'w', encoding='utf-8') as f:
        if ext == 'json':
            json.dump(value, f, indent=2, ensure_ascii=False)
        else:
            f.write(str(value))


def append_record(value: Any,
                  fname: str,
                  addresses: Optional[Iterable[str]] = None):
    """
    Appends a record to a JSON list file. If file doesn't exist, creates a new list.
    """
    path_segments = tuple(addresses or ())
    base = os.path.join(script_dir, 'log_json_files', *path_segments)
    os.makedirs(base, exist_ok=True)
    
    filename = f'{fname}.json'
    path = os.path.join(base, filename)
    
    current_data = []
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                current_data = json.load(f)
                if not isinstance(current_data, list):
                    # If existing content is not a list, wrap it or warn
                    print(f"Warning: {path} content is not a list. Converting to list.")
                    current_data = [current_data]
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error reading {path}: {e}. Starting with empty list.")
            current_data = []
            
    current_data.append(value)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)

