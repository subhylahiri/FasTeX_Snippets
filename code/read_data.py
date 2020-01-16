"""Reading active string data from winedt
"""
import io
import re
import typing as ty

Snippet = ty.Union[str, ty.List[str]]

TEMPLATE_PRE = (
    r"Assign\('FasTeX','(\S*)'\);" +
    r"Exe\('%b\\Macros\\Active Strings\\FasTeX\\FasTeX_Templates.edt'\);")
INSERT_PRE = r"^BeginGroup;Backspace\(\d+\);Ins\([`'](.*)[`']\);"

TRIGGER = re.compile(r'^STRING="(\S*)  "$')
MACRO = re.compile(r'^  MACRO="\[(.*)\]"$')
TEMPLATE_ONE = re.compile(TEMPLATE_PRE + r"LineUp\((\d)\);TrackCaret;$")
TEMPLATE_ZERO = re.compile(TEMPLATE_PRE + "$")
INSERT_TWO = re.compile(INSERT_PRE + r"CharLeft;CharLeft\((\d)\);EndGroup;$")
INSERT_ONE = re.compile(INSERT_PRE + "CharLeft;EndGroup;$")
INSERT_ONES = re.compile(INSERT_PRE + r"CharLeft\((\d)\);EndGroup;$")
INSERT_ZERO = re.compile(INSERT_PRE + "EndGroup;$")

TEMPLATES = (TEMPLATE_ZERO, TEMPLATE_ONE)
INSERTS = (INSERT_ZERO, INSERT_ONE, INSERT_ONES, INSERT_TWO)

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
        return text[start:stop]


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
    """Get match text from macro"""
    for index, pattern in enumerate(patterns):
        match = pattern.match(macro)
        if match:
            return match, index
    return None, 0


def get_macro_template(macro: str, dat_text: ty.List[str]) -> ty.List[str]:
    """Get template text from macro"""
    match, _ = get_macro_matches(macro, TEMPLATES)
    if match is None:
        return None
    groups = match.groups()
    trigger = groups[0]
    snippet = get_template(dat_text, trigger)
    if len(groups) == 2:
        line_num = int(groups[1])
        snippet[-line_num] += "$1"
    return snippet


def get_macro_insert(macro: str) -> str:
    """Get template text from macro"""
    match, index = get_macro_matches(macro, INSERTS)
    if match is None:
        return None
    groups = match.groups()
    snippet = groups[0]
    if index == 0:
        return snippet
    if index == 1:
        return snippet[:-1] + "$1" + snippet[-1:]
    char_num = int(groups[1])
    if index == 2:
        return snippet[:-char_num] + "$1" + snippet[-char_num:]
    snippet = snippet[:-char_num-1] + "$1" + snippet[-char_num-1:]
    return snippet[:-1] + "$2" + snippet[-1:]


def next_ini_entry(file: io.TextIOBase,
                   dat_text: ty.List[str]) -> ty.Dict[str, Snippet]:
    """Find next entry in ini file
    """
    trigger = get_ini_trigger(file)
    macro = get_ini_macro(file)
    if trigger is None or macro is None:
        return None
    snippet = get_macro_template(macro, dat_text)
    if snippet:
        description = snippet[0]
    else:
        snippet = get_macro_insert(macro)
        description = snippet
    if snippet is None:
        return None
    return {'prefix': trigger, 'body': snippet, 'description': description}


def process_ini(ini_file: str, dat_file: str) -> ty.List[ty.Dict[str, Snippet]]:
    """Read all winedt data"""
    dat_text = read_dat(dat_file)
    snippets = []
    with open(ini_file, mode='r') as file:
        snip = next_ini_entry(file, dat_text)
        while snip:
            snippets.append(snip)
            snip = next_ini_entry(file, dat_text)
    return snippets


if __name__ == "__main__":
    snips = process_ini('../data/ActiveStrings-FasTeX.ini',
                        '../data/FasTeX_Templates.edt.dat')
