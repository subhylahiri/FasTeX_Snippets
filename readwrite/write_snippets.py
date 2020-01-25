"""Write snippets in the relevant form for vscode/latex-utilities/atom

Functions
---------
read_data_json
    Import FasTeX snippet data in internal format.
convert_vscode
    Convert snippet data to VSCode snippet format.
convert_atom
    Convert snippet data to Atom snippet format.
convert_live
    Convert snippet data to VSCode LaTeX-Utilities live snippet format.
convert_vscode
    Convert multiline snippet data to VSCode snippet format
    and single-line snippet data to LaTeX-Utilities live snippet format.
make_snippet_json
    Write snippet data to a `.json` file.
"""
import re
import json
from typing import Union, List, Dict, Optional, Sequence
if __name__ == "__main__":
    import cson
else:
    from . import cson

Body = Union[str, List[str]]
Snippet = Dict[str, Body]
SnippetDict = Dict[str, Snippet]
AtomSnippetDict = Dict[str, SnippetDict]

TAB_STOP = re.compile(r'(?<!\\)\$(\d)')
TEX_OLD = re.compile(r'^\{\\([a-z][a-z]) $')
DOUBLE_DOLLAR = re.compile(r'\\\$(.*)\\\$')


def read_data_json(file_name: str):
    """Read imported snippet data from json file

    Parameters
    ----------
    file_name : str
        Name of internal `.json` file with snippet info.

    Returns
    -------
    snippets : List[Snippet]
        List of snippet objects: dicts with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
        Type: `Snippet = Dict[str, str]` or `Dict[str, List[str]]`.
    """
    with open(file_name, 'r') as file:
        snippets = json.load(file)
    return snippets


def _count_tabs(body: Body) -> int:
    """Count tab stops in snippet body.

    Parameters
    ----------
    body : Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.

    Returns
    -------
    count : int
        Number of distinct tab stops in body.
    """
    if isinstance(body, list):
        return max((_count_tabs(line) for line in body), default=0)
    tabs = TAB_STOP.findall(body)
    return max((int(num) for num in tabs), default=0)


def _body_append(body: Body, addendum: str) -> Body:
    """Add something to end of snippet
    """
    if isinstance(body, list):
        return body + [addendum]
    return body + addendum


def _body_prepend(body: Body, addendum: str) -> Body:
    """Add something to start of snippet
    """
    if isinstance(body, list):
        return [addendum] + body
    return addendum + body


def _convert_body_vsc(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert tab stops for a VSCode snippet

    Parameters
    ----------
    body : Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if isinstance(body, list):
        return [_convert_body_vsc(line, endtab, maxtab) for line in body]
    if endtab or maxtab == 0:
        return body
    return re.sub(fr'[^\\]\${maxtab}', '$0', body)


def convert_one_vsc(snippet: Snippet, prefix: str = '', suffix: str = '',
                    endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to VSCode format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, description.
    """
    maxtab = 0
    if not endtab:
        maxtab = _count_tabs(snippet['body'])
    vsc_prefix = prefix + snippet['prefix'] + suffix
    vsc_body = _convert_body_vsc(snippet['body'], endtab, maxtab)
    return {'prefix': vsc_prefix, 'body': vsc_body,
            'description': snippet['description']}


def convert_all_vscode(snippets: List[Snippet],
                       prefix: str = '', suffix: str = '', endtab: bool = True
                       ) -> SnippetDict:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippets : Dict[str, Snippet]
        Dict of snippet objects: dict with prefix, body, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    """
    vsc_snippets = {}
    for snip in snippets:
        new_snip = convert_one_vsc(snip, prefix, suffix, endtab)
        vsc_snippets[snip['prefix']] = new_snip
    return vsc_snippets


def _help_body_atom(body: str) -> str:
    """Helper for converting body for an Atom snippet"""
    body = body.replace('\\', '\\\\\\\\')
    body = body.replace('"', '\\"')
    return body


def _convert_body_atom(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert body for an Atom snippet

    Parameters
    ----------
    body : Body = str or List[str]
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : Body = str or List[str]
        Body of snippet with tabstops: `if endtab:` `$1`,...,`$n`,
        `else:` `$1`,...,`$n-1`,`$0`.
    """
    if endtab and maxtab:
        body = _body_append(body, f'${maxtab + 1}')
    if isinstance(body, list):
        body = [_help_body_atom(line) for line in body]
        return '\n'.join(body)
    return _help_body_atom(body)


def convert_one_atom(snippet: Snippet, prefix: str = '', suffix: str = '',
                     endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to Atom format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, description.
    """
    maxtab = 0
    if not endtab:
        maxtab = _count_tabs(snippet['body'])
    atom_prefix = prefix + snippet['prefix'] + suffix
    atom_body = _convert_body_atom(snippet['body'], endtab, maxtab)
    return {'prefix': atom_prefix, 'body': atom_body}


def convert_all_atom(snippets: List[Snippet],
                     prefix: str = '', suffix: str = '', endtab: bool = True
                     ) -> AtomSnippetDict:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippets : Dict[str, Snippet]
        Dict of dict of snippet objects: dict with prefix, body.
        `Snippet = Dict[str, str] or Dict[str, List[str]]`.
    """
    atom_snippets = {}
    for snip in snippets:
        new_snip = convert_one_atom(snip, prefix, suffix, endtab)
        atom_snippets[snip['prefix']] = new_snip
    return {'.text.tex.latex': atom_snippets}


def _help_body_live(body: str, endtab: bool = True, maxtab: int = 0) -> str:
    """Convert tab stops for one line of a live snippet

    Parameters
    ----------
    body : str
        Line of body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : str
        Line of body of snippet with tabstops: `if endtab:` `$$1`,...,`$$n`,
        `else:` `$$1`,...,`$$n-1`,`$0`.
    """
    if not endtab or maxtab:
        body = re.sub(fr'[^\\]\${maxtab}', '$0', body)
    body = TAB_STOP.sub('$$\\1', body)
    body = body.replace('\\$1', '$ 1')
    body = body.replace('\\$', '$')
    return body


def _convert_body_live(body: Body, endtab: bool = True, maxtab: int = 0) -> Body:
    """Convert tab stops for a VSCode live snippet

    Parameters
    ----------
    body : str
        Body of snippet with tabstops `$1`,...,`$n`.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    maxtab : int, optional, default: 0
        What is the maximum tabstop, `n`, in the snippet? Unused `if endtab`.

    Returns
    -------
    body : str
        Body of snippet with tabstops: `if endtab:` `$$1`,...,`$$n`,
        `else:` `$$1`,...,`$$n-1`,`$0`.
    """
    if isinstance(body, list):
        lines = [_help_body_live(line, endtab, maxtab) for line in body]
        lines = _body_prepend(lines, '$1')
        return '\\n'.join(lines)
    body = _help_body_live(body, endtab, maxtab)
    return _body_prepend(body, '$1')


def convert_one_live(snippet: Snippet, prefix: str = '', suffix: str = '',
                     endtab: bool = True) -> Snippet:
    """Convert a snippet from internal to VSCode format.

    Parameters
    ----------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, description.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?

    Returns
    -------
    snippet : Snippet = Dict[str, str] or Dict[str, List[str]]
        Snippet object: dict with prefix, body, mode, triggerWhenComplete,
        description and priority.
    """
    maxtab = 0
    if not endtab:
        maxtab = _count_tabs(snippet['body'])
    live_prefix = r'(^|[^\\])' + prefix + snippet['prefix'] + suffix
    live_body = _convert_body_live(snippet['body'], endtab, maxtab)
    return {'prefix': live_prefix, 'body': live_body, 'mode': snippet['mode'],
            'triggerWhenComplete': True, 'description': snippet['description'],
            'priority': len(snippet['prefix'])}


def convert_all_live(snippets: List[Snippet],
                     prefix: str = '', suffix: str = '', endtab: bool = True,
                     ) -> List[Snippet]:
    """Convert list of snippets from internal to VSCode format.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dict with prefix, body, mode, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    prefix : str
        String to prepend to every snippet trigger.
    suffix : str
        String to append to every snippet trigger.
    endtab : bool, optional, default: False
        Do we want a tabstop at the end?
    prefix_m, suffix_m, endtab_m
        Versions of `prefix`, `suffix`, `endtab` for multiline snippets.

    Returns
    -------
    live_snippets : List[Snippet]
        List of snippet objects: dicts with prefix, body, mode,
        triggerWhenComplete, description, priority.
    """
    live_snippets = []
    for snip in snippets:
        new_snip = convert_one_live(snip, prefix, suffix, endtab)
        live_snippets.append(new_snip)
    return live_snippets


def _modern_vsc(snippet: Snippet) -> Snippet:
    """Replace old style TeX with modern LaTeX.

    Replaces snippet with `body = "{\\?? "` with
    `body = "${1|\\text,\\math|}??{$2}"`

    Parameters
    ----------
    snippet : Snippet = Dict[str, Union[str, List[str]]]
        Snippet to modify.

    Returns
    -------
    snippet : Snippet
        Unmodified/modified input.
    """
    if not isinstance(snippet['body'], str):
        return snippet
    match = TEX_OLD.match(snippet['body'])
    if match is None:
        return snippet
    command = match.group(1)
    new_snip = snippet.copy()
    new_snip['mode'] = 'any'
    new_snip['body'] = '${1|\\text,\\math|}' + command + '{$2}'
    return new_snip


def _modern_live(snippet: Snippet) -> (Snippet, Snippet):
    """Replace old style TeX with modern LaTeX.

    Replaces snippet with `body = "{\\?? "`, `mode = "any"` with
    `body = "\\text??{$1}"`, `mode = "text"` and
    `body = "\\math??{$1}"`, `mode = "maths"`

    Parameters
    ----------
    snippet : Snippet = Dict[str, Union[str, List[str]]]
        Snippet to modify.

    Returns
    -------
    snippet : Snippet
        Unmodified input.
    OR

    txt_snippet : Snippet
        Text mode version of snippet.
    mth_snippet : Snippet
        Maths mode version of snippet.
    """
    if not (isinstance(snippet['body'], str) or snippet['mode'] == "any"):
        return snippet
    match = TEX_OLD.match(snippet['body'])
    if match is None:
        return snippet
    command = match.group(1)
    txt_snip = snippet.copy()
    txt_snip['mode'] = 'text'
    txt_snip['body'] = '\\\\text' + command + '{$1}'
    mth_snip = snippet.copy()
    mth_snip['mode'] = 'maths'
    mth_snip['body'] = '\\\\math' + command + '{$1}'
    return txt_snip, mth_snip


def _un_dollar(snippet: Snippet):
    """Replace $...$ with \\(...\\)

    Parameters
    ----------
    snippet : Snippet = Dict[str, Union[str, List[str]]]
        Snippet to modify *in place*.
    """
    body = snippet['body']
    if isinstance(body, list) or DOUBLE_DOLLAR.search(body) is None:
        return
    snippet['body'] = DOUBLE_DOLLAR.sub(r'\(\1\)', body)


def _choose(snippet: Snippet,
            prefix: Sequence[re.Pattern] = (),
            body: Sequence[re.Pattern] = (),
            multiline: bool = True,
            singleline: bool = True) -> bool:
    """Filter an entry in the list of snippets.

    Parameters
    ----------
    snippet : Snippet = Dict[str, Union[str, List[str]]]
        The candidate snippet.
    prefix : Sequence[re.Pattern], optional, default = ()
        Regex patterns to test `snippet['prefix']` against, using `re.match`.
        Excludes `snippet` if *any* of them match.
    body : Sequence[re.Pattern], optional, default = ()
        Regex patterns to test `snippet['body']` against, using `re.search`.
        Excludes `snippet` if *any* of them match.
    multiline : bool, optional, default = True
        Include snippets with multi-line bodies?
    singleline : bool, optional, default = True
        Include snippets with single-line bodies?

    Returns
    -------
    choice : bool
        Include this snippet?
    """
    the_body = snippet['body']
    multi = isinstance(the_body, list)
    if (not multiline) and multi:
        return False
    if (not singleline) and (not multi):
        return False
    if any(rule.match(snippet['prefix']) for rule in prefix):
        return False
    if (not multi) and any(rule.search(the_body) for rule in body):
        return False
    return not any(rule.search(line) for rule in body for line in the_body)


def apply_options(snippets: List[Snippet],
                  prefix: Sequence[re.Pattern] = (),
                  body: Sequence[re.Pattern] = (),
                  **kwds) -> List[Snippet]:
    """Perform cull and modify snippets.

    Run this function on the snippet data, in the internal format, before
    converting to VSCode/Atom formats.

    Parameters
    ----------
    snippets : List[Snippet]
        List of snippet objects: dicts with prefix, body, mode, description.
        Superset of the info needed by: vscode/latex-utilities/atom snippets
        Derived: `multiline = isinstance(body, list)`, `priority = len(prefix)`
        Type: `Snippet = Dict[str, str]` or `Dict[str, List[str]]`.
    prefix : Sequence[re.Pattern], optional, default = ()
        Regex patterns to test `snippet['prefix']` against, using `re.match`.
        Excludes `snippet` if *any* of them match.
    body : Sequence[re.Pattern], optional, default = ()
        Regex patterns to test `snippet['body']` against, using `re.search`.
        Excludes `snippet` if *any* of them match.

    Keywords
    --------
    multiline : bool, optional, default = True
        Include snippets with multi-line bodies?
    singleline : bool, optional, default = True
        Include snippets with single-line bodies?
    textmaths : bool, optional, default = True
        Use text/math modes where available? Only for Live Snippets.
    dollarfix : bool, optional, default = False
        Convert dollar signs in snippets: `$...$ -> \\(...\\)`?
    modern : bool, optional, default = False
        Replace old-fashioned `{\\?? ` with modern versions: `\\text??{$1}` and
        `\\math??{$1}` (e.g. `?? = bf`)? If `textmaths`, create two snippets,
        else create choice tab-stop.
        Creates two snippets. Only for Live Snippets.
    """
    multiline: bool = kwds.pop('multiline', True)
    singleline: bool = kwds.pop('singleline', True)
    textmaths: bool = kwds.pop('textmaths', True)
    dollarfix: bool = kwds.pop('dollarfix', False)
    modern: bool = kwds.pop('modern', False)
    if kwds:
        raise KeyError('Unknown key words: ' + ', '.join(kwds.keys()))
    new_snippets = []
    for snip in snippets:
        if not _choose(snip, prefix, body, multiline, singleline):
            continue
        if not textmaths:
            snip['mode'] = "any"
        if dollarfix:
            _un_dollar(snip)
        if modern:
            if textmaths:
                snip = _modern_live(snip)
                if isinstance(snip, tuple):
                    new_snippets.extend(snip)
                    continue
            else:
                snip = _modern_vsc(snip)
        new_snippets.append(snip)
    return new_snippets


def make_snippet_json(snippets: Union[Snippet, SnippetDict, None] = None,
                      snip_file: str = 'latex.json',
                      live_snippets: Optional[List[Snippet]] = None,
                      live_file: str = 'latexUtilsLiveSnippets.json'):
    """Write snippets in the chosen format to .json files.

    Parameters
    ----------
    snippets : Dict[str, Snippet] or Dict[str, Dict[str, Snippet]]
        Dict of (dict of) snippet objects: dict with prefix, body, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    snip_file : str, optional, default: latex.json
        Name of file for normal snippets.
    live_snippets : List[Snippet], optional
        List of single-line snippet objects: dicts with prefix, body, mode,
        triggerWhenComplete, description, priority.
    live_file : str, optional, default: liveSnippets.json
        Name of file for live snippets.
    """
    if snippets is not None:
        with open(snip_file, 'w') as file:
            json.dump(snippets, file, indent=4)
    if live_snippets is not None:
        with open(live_file, 'w') as file:
            json.dump(live_snippets, file, indent=4)


def make_snippet_cson(snippets: Optional[AtomSnippetDict] = None,
                      snip_file: str = 'snippets.cson'):
    """Write snippets in the chosen format to .json files.

    Parameters
    ----------
    snippets : Dict[str, Dict[str, Snippet]]
        Dict of dict of snippet objects: dict with prefix, body.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    snip_file : str, optional, default: language-latex.cson
        Name of file for normal snippets.
    """
    if snippets is not None:
        with open(snip_file, 'w') as file:
            cson.dump(snippets, file, indent=4, level=-1)


def _main():
    snippet_data = read_data_json('data/data.json')
    snips = convert_all_vscode(snippet_data, prefix=';')
    make_snippet_json(snips)
    snips = convert_all_atom(snippet_data, prefix='')
    make_snippet_cson(snips)
    live_snips = convert_all_live(snippet_data, suffix='  ')
    make_snippet_json(live_snippets=live_snips)
    # live_snips, snips = convert_split(snippet_data, suffix='  ', prefix_m=';')
    # make_snippet_json(snips, live_snippets=live_snips)


if __name__ == "__main__":
    _main()
