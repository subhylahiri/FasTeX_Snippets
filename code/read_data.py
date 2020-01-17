"""Reading active string data from winedt
"""
import io
import re
import json
import typing as ty

Body = ty.Union[str, ty.List[str]]
Snippet = ty.Dict[str, Body]

TEMPLATE_PRE = (
    r"Assign\('FasTeX','(\S*)'\);" +
    r"Exe\('%b\\Macros\\Active Strings\\FasTeX\\FasTeX_Templates.edt'\);")
INSERT_PRE = r"^BeginGroup;Backspace\(\d+\);Ins\([`'](.*)[`']\);"
LINE_UP = r"LineUp\((\d)\);TrackCaret;"
BACK_ONE = "CharLeft;"
BACK_SOME = r"CharLeft\((\d)\);"
END_GROUP = "EndGroup;$"

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


def escape_body(body: Body) -> Body:
    """Escape special characters in snippets
    """
    if isinstance(body, list):
        return [escape_body(txt) for txt in body]
    return body.replace('$', '\\$')


def make_description(body: Body, trigger: str) -> str:
    """Format description from body
    """
    if isinstance(body, list):
        describe = make_description(body[0], trigger)
        if describe.startswith(('%====', '%----')):
            if trigger.startswith('c'):
                describe = ";".join([x[:10] for x in body])
                return "Divider: " + describe
            return make_description(body[1:], trigger)
        return describe
    return TAB_STOP.sub('', body, count=9).replace('\\$', '$')


def choose_mode(body: Body, trigger: str) -> str:
    """Choose mode for snippet
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
    if any(x in body for x in ('\\math', '_', '^', '\\frac')):
        return "maths"
    return "any"


def read_dat(file_name: str):
    """Read templates dat file
    """
    with open(file_name, mode='r') as text_file:
        text = text_file.readlines()
    return text


def get_template(text: ty.List[str], snip: str) -> ty.List[str]:
    """Find a template snippet in dat file
    """
    try:
        start = text.index(f"{snip}\n") + 1
        stop = text.index(f"-{snip}-\n")
    except ValueError:
        raise
    else:
        return [escape_body(x[:-1]) for x in text[start:stop]]


def next_ini_line(file: io.TextIOBase, check: re.Pattern) -> re.Match:
    """Read next line in ini file
    """
    line = file.readline()
    if not line:
        return None
    match = check.match(line)
    return match


def get_ini_trigger(file: io.TextIOBase) -> str:
    """Get trigger for next snippet
    """
    line_match = next_ini_line(file, TRIGGER)
    if line_match is None:
        return None
    trigger = line_match.group(1)
    return trigger


def get_ini_macro(file: io.TextIOBase) -> str:
    """Get macro for current snippet
    """
    file.readline()
    file.readline()
    line_match = next_ini_line(file, MACRO)
    if line_match is None:
        return None
    macro = line_match.group(1)
    return macro


def get_macro_matches(macro: str,
                      patterns: ty.Sequence[re.Pattern]) -> (re.Match, int):
    """Get match object from macro
    """
    for index, pattern in enumerate(patterns):
        match = pattern.match(macro)
        if match:
            return match, index
    return None, 0


def get_macro_template(macro: str, dat_text: ty.List[str]) -> ty.List[str]:
    """Get template text from macro
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
    # second tab-stop was a winedt bullet - remove
    return body[:-2] + "$2" + body[-1:]


def next_ini_entry(file: io.TextIOBase,
                   dat_text: ty.List[str]) -> ty.Dict[str, Body]:
    """Find next entry in ini file
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


def process_ini(ini_file: str, dat_file: str) -> ty.Dict[str, Snippet]:
    """Read all winedt data
    """
    dat_text = read_dat(dat_file)
    snippets = {}
    with open(ini_file, mode='r') as file:
        snip = next_ini_entry(file, dat_text)
        while snip:
            snippets[snip['prefix']] = snip
            snip = next_ini_entry(file, dat_text)
    return snippets


def write_json(file_name: str, snippets: ty.Dict[str, Snippet]):
    """Write imported snippet data to json file
    """
    with open(file_name, 'w') as file:
        json.dump(snippets, file, indent=4)


if __name__ == "__main__":
    snips = process_ini('data/ActiveStrings-FasTeX.ini',
                        'data/FasTeX_Templates.edt.dat')
    write_json('data/data.json', snips)
    for pref in ['txpf', 'dccd', 'eqtxt', 'xa', 'txt']:
        print(snips[pref])
