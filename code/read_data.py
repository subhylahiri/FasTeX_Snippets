"""Reading active string data from Winedt, convert to JSON

Stores superset of the info needed by: vscode/latex-utilities/atom snippets

Functions
---------
process_ini
    Read all Winedt data.
write_data_json
    Write imported snippet data to .json file.
"""
import io
import re
import json
from typing import Union, List, Dict, Sequence

Body = Union[str, List[str]]
Snippet = Dict[str, Body]

# regex building blocks
TEMPLATE_PRE = (
    r"Assign\('FasTeX','(\S*)'\);" +
    r"Exe\('%b\\Macros\\Active Strings\\FasTeX\\FasTeX_Templates.edt'\);")
INSERT_PRE = r"^BeginGroup;Backspace\(\d+\);Ins\([`'](.*)[`']\);"
LINE_UP = r"LineUp\((\d)\);TrackCaret;"
BACK_ONE = "CharLeft;"
BACK_SOME = r"CharLeft\((\d)\);"
END_GROUP = "EndGroup;$"

# regex for reading Winedt data
TRIGGER = re.compile(r'^STRING="(\S*)  "$')
MACRO = re.compile(r'^  MACRO="\[(.*)\]"$')
TEMPLATE_ONE = re.compile(TEMPLATE_PRE + LINE_UP + "$")
TEMPLATE_ONES = re.compile(TEMPLATE_PRE + LINE_UP + BACK_ONE + "$")
TEMPLATE_ZERO = re.compile(TEMPLATE_PRE + "$")
INSERT_TWO = re.compile(INSERT_PRE + BACK_ONE + BACK_SOME + END_GROUP)
INSERT_ONE = re.compile(INSERT_PRE + BACK_ONE + END_GROUP)
INSERT_ONES = re.compile(INSERT_PRE + BACK_SOME + END_GROUP)
INSERT_ZERO = re.compile(INSERT_PRE + END_GROUP)
TAB_STOP = re.compile(r'(?<!\\)\$\d')

TEMPLATES = (TEMPLATE_ZERO, TEMPLATE_ONES, TEMPLATE_ONE)
INSERTS = (INSERT_ZERO, INSERT_ONE, INSERT_ONES, INSERT_TWO)

# mode recognition
TEXT_START = (
    '\\usepackage',
    '\\new',
    '\\renew',
    '\\leftline',
    '\\rightline',
    '\\doc',
    '\\text',
    '\\section',
    '\\fbox',
)
MATHS_START = (
    '\\frac',
    '\\math',
    '\\operatorname',
    '\\sqrt',
    '\\left',
    '\\right',
    '\\var',
    '\\over',
    '\\wide',
    '\\dot',
    '\\ddot',
    '\\bar',
    '\\bar',
    '\\vec',
    '\\hat',
    '\\tilde',
)


def escape_body(body: Body) -> Body:
    """Escape special characters in snippets.
    
    Parameters
    ----------
    body : str / list[str]
        String with body of snippet.

    Returns
    -------
    body : str / list[str]
        Input with dollar signs escaped.
    """
    if isinstance(body, list):
        return [escape_body(txt) for txt in body]
    return body.replace('$', '\\$')


def make_description(body: Body, trigger: str) -> str:
    """Format description from body of snippet.
    
    Parameters
    ----------
    body : str / list[str]
        String with body of snippet.
    trigger : str
        Trigger string for snippet.

    Returns
    -------
    description : str
        Attempted snippet description.
    """
    if isinstance(body, list):
        describe = make_description(body[0], trigger)
        if describe.startswith(('%====', '%----')):
            if trigger.startswith('c'):
                describe = ";".join([x[:10] for x in body])
                return "Divider: " + describe
            return make_description(body[1:], trigger)
        return describe.lstrip('%&')
    return TAB_STOP.sub('', body, count=9).replace('\\$', '$')


def choose_mode(body: Body, trigger: str) -> str:
    """Choose mode for snippet.
    
    Parameters
    ----------
    body : str / list[str]
        String with body of snippet.
    trigger : str
        Trigger string for snippet.

    Returns
    -------
    mode : str
        Inferred mode of snippet, one of {`text`, `maths`, `any`}.
    """
    if body is None:
        return None
    if isinstance(body, list):
        if trigger.startswith('mx'):
            return "maths"
        return "text"
    if body.count('\\$') >= 2:
        return "text"
    if trigger.startswith('w') and not body.startswith('\\'):
        return "text"
    if trigger.startswith('w') and body.startswith('\\'):
        return "maths"
    if trigger.startswith('o') and body.startswith('('):
        return "maths"
    if trigger.startswith('x'):
        return "maths"
    if any(x in body for x in ('_', '^', '\\frac')):
        return "maths"
    if body.startswith(('\\textstyle', '\\text{}')):
        return "maths"
    if body.startswith(TEXT_START):
        return "text"
    if body.startswith(MATHS_START):
        return "maths"
    return "any"


def read_dat(file_name: str) -> List[str]:
    """Read .dat file containing templates.
    
    Parameters
    ----------
    file_name : str
        Name of Winedt `.dat` file containing multi-line template snippets.
        
    Returns
    -------
    lines : List[str]
        List of text lines from Winedt `.dat` file of multi-line template 
        snippets.
    """
    with open(file_name, mode='r') as text_file:
        text = text_file.readlines()
    return text


def get_template(dat_text: List[str], trigger: str) -> List[str]:
    """Find a template snippet in .dat file.

    Parameters
    ----------
    dat_text : List[str]
        List of text lines from Winedt `.dat` file of multi-line template 
        snippets.
    trigger : str
        Trigger string for snippet.
        
    Returns
    -------
    body : List[str]
        List of text lines for specified snippet body.
    """
    try:
        start = dat_text.index(f"{trigger}\n") + 1
        stop = dat_text.index(f"-{trigger}-\n")
    except ValueError:
        raise
    else:
        return [escape_body(x[:-1]) for x in dat_text[start:stop]]


def next_ini_line(file: io.TextIOBase, check: re.Pattern) -> re.Match:
    """Read next line in .ini file and check match.
    
    Parameters
    ----------
    file : io.TextIO
        Text file object for Winedt active string `.ini` file.
    check : re.Pattern
        Regex pattern to match with next line of `file`.
        
    Returns
    -------
    match: re.Match
        Result of matching next line of `file` against `check`.
    """
    line = file.readline()
    if not line:
        return None
    match = check.match(line)
    return match


def get_ini_trigger(file: io.TextIOBase) -> str:
    """Get trigger for next snippet
    
    Parameters
    ----------
    file : io.TextIO
        Text file object for Winedt active string `.ini` file.
        
    Returns
    -------
    trigger : str
        Trigger string for snippet, spaces stripped.
    """
    line_match = next_ini_line(file, TRIGGER)
    if line_match is None:
        return None
    trigger = line_match.group(1)
    return trigger


def get_ini_macro(file: io.TextIOBase) -> str:
    """Get macro for current snippet
    
    Parameters
    ----------
    file : io.TextIO
        Text file object for Winedt active string `.ini` file.
        
    Returns
    -------
    macro : str
        Contents of Winedt macro for active string.
    """
    file.readline()
    file.readline()
    line_match = next_ini_line(file, MACRO)
    if line_match is None:
        return None
    macro = line_match.group(1)
    return macro


def get_macro_matches(macro: str,
                      patterns: Sequence[re.Pattern]) -> (re.Match, int):
    """Get match object from macro.
    
    Parameters
    ----------
    macro : str
        Contents of Winedt macro for active string.
    patterns : Sequence[re.Pattern]
        Regex pattern to match with next line of `file`.
        
    Returns
    -------
    match: re.Match
        Result of matching `macro` against members of `patterns`.
    index : int
        Index of first `patterns` member that matched `macro.
    """
    for index, pattern in enumerate(patterns):
        match = pattern.match(macro)
        if match:
            return match, index
    return None, 0


def get_macro_template(macro: str, dat_text: List[str]) -> List[str]:
    """Get template text from macro.
    
    Parameters
    ----------
    macro : str
        Contents of Winedt macro for active string.
    dat_text : List[str]
        List of text lines from Winedt `.dat` file of multi-line template 
        snippets.
        
    Returns
    -------
    body : List[str]
        List of text lines for snippet body.
    """
    match, index = get_macro_matches(macro, TEMPLATES)
    if match is None:
        return None
    groups = match.groups()
    trigger = groups[0]
    body = get_template(dat_text, trigger)
    if index == 2:
        line_num = int(groups[1])
        body[-line_num] += "$1"
    if index == 1:
        line_num = int(groups[1])
        body[-line_num] = body[-line_num][:-1] + "$1" + body[-line_num][-1:]
    return body


def get_macro_insert(macro: str) -> str:
    """Get inserted text from macro
    
    Parameters
    ----------
    macro : str
        Contents of Winedt macro for active string.
        
    Returns
    -------
    body : str
        Text of snippet body.
    """
    match, index = get_macro_matches(macro, INSERTS)
    if match is None:
        return None
    groups = match.groups()
    body = escape_body(groups[0])
    if index == 0:
        return body
    if index == 1:
        return body[:-1] + "$1" + body[-1:]
    char_num = int(groups[1])
    if index == 2:
        return body[:-char_num] + "$1" + body[-char_num:]
    body = body[:-char_num-1] + "$1" + body[-char_num-1:]
    # second tab-stop was a Winedt bullet - remove
    return body[:-2] + "$2" + body[-1:]


def next_ini_entry(file: io.TextIOBase,
                   dat_text: List[str]) -> Snippet:
    """Read next entry in .ini file
    
    Parameters
    ----------
    file : io.TextIO
        Text file object for Winedt active string `.ini` file.
    dat_text : List[str]
        List of text lines from Winedt `.dat` file of multi-line template 
        snippets.
        
    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
    """
    trigger = get_ini_trigger(file)
    macro = get_ini_macro(file)
    if trigger is None or macro is None:
        return None
    body = get_macro_template(macro, dat_text)
    if body is None:
        body = get_macro_insert(macro)
    if body is None:
        return None
    # for live snippets
    mode = choose_mode(body, trigger)
    # for VS Code
    describe = make_description(body, trigger)

    return {'prefix': trigger, 'body': body, 'mode': mode,
            'description': describe}


def process_ini(ini_file: str, dat_file: str) -> List[Snippet]:
    """Read all Winedt data

    Parameters
    ----------
    ini_file : str
        Name of Winedt active string `.ini` file.
    dat_file : str
        Name of Winedt `.dat` file containing multi-line template snippets.
        
    Returns
    -------
    snippets : Dict[str, Snippet]
        Dict of snippet objects: dicts with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
        Type: `Snippet = Dict[str, str]` or `Dict[str, List[str]]`.
    """
    dat_text = read_dat(dat_file)
    snippets = []
    with open(ini_file, mode='r') as file:
        snip = next_ini_entry(file, dat_text)
        while snip:
            snippets.append(snip)
            snip = next_ini_entry(file, dat_text)
    return snippets


def write_data_json(file_name: str, snippets: List[Snippet]):
    """Write imported snippet data to .json file

    Parameters
    ----------
    file_name : str
        name of internal `.json` file for snippet info.
    snippets : Dict[str, Snippet]
        List of snippet objects: dicts with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
        Type: `Snippet = Dict[str, str]` or `Dict[str, List[str]]`.
    """
    with open(file_name, 'w') as file:
        json.dump(snippets, file, indent=4)


if __name__ == "__main__":
    snips = process_ini('data/ActiveStrings-FasTeX.ini',
                        'data/FasTeX_Templates.edt.dat')
    write_data_json('data/data.json', snips)
