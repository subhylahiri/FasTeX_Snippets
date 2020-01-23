"""Write snippets in the relevant form for Atom
"""
from typing import Optional
if __name__ == "__main__":
    import cson
    from write_snippets import read_data_json, convert_atom, SnippetDict
else:
    from . import cson
    from .write_snippets import read_data_json, convert_atom, SnippetDict


def make_snippet_cson(snippets: Optional[SnippetDict] = None,
                      snip_file: str = 'language-latex.cson'):
    """Write snippets in the chosen format to .json files.

    Parameters
    ----------
    snippets : Dict[str, Snippet] or Dict[str, Dict[str, Snippet]]
        Dict of (dict of) snippet objects: dict with prefix, body, description.
        `Snippet =  = Dict[str, str] or Dict[str, List[str]]`.
    snip_file : str, optional, default: language-latex.cson
        Name of file for normal snippets.
    """
    if snippets is not None:
        with open(snip_file, 'w') as file:
            cson.dump(snippets, file, indent=4)


if __name__ == "__main__":
    snippet_data = read_data_json('data/data.json')
    snips = convert_atom(snippet_data, prefix=';')
    make_snippet_cson(snips)
    for x in list(snips['.text.tex.latex'].keys())[:10]:
        print(x)
