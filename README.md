# FasTeX_Snippets
Snippet version of FasTeX shortcuts for LaTeX, for VSCode and Atom.

This is a port of the FasTeX system of shortcuts to editors that use snippets, 
currently targeting VSCode and Atom.
It is based on the WinEdt version by Bernhard Enders.

- [FasTeX project](http://www.cds.caltech.edu/~fastex/fastex.html)
- [Original documentation](http://www.cds.caltech.edu/~fastex/fastex_docs.html)
- [WinEdt version](http://www.winedt.org/macros/latex/FasTeX.html)

The basic idea is that you type shortcut codes that are replaced with LaTeX.
The shortcuts are made up of lower-case letter and (occasionally) numbers.
This means you can type them without reaching for modifier keys and symbols, 
e.g. the shortcut `bksl` maps to `\`, shortcut `ob` to `{` (open braces) and shortcut `eb` to `}` (end braces).
The shortcuts are fairly systematic: prefix `x` for greek, 
`c` for upper-case, `d` for in dollars,
`h` for superscript, `l` for subscript (high & low), 
`o` for in parentheses, `f` for fraction,...
(the order of the prefixes matters).  
suffix `a` for `a`/`alpha`,..., `u` for unfinished/universal, `mo` for `-1`,...  
so `dxcd` → `$\Delta$` | 
`hct` → `^T` |
`hmo` → `^{-1}` |
(tox` → `(x)`,...  
`lij` → `_{ij}` |
Have a look at the documentation linked to above for more information 
although they have been modernised since.

There are nearly 1600 shortcuts, so I haven't tested them all in this implementation.
I have also mostly stopped using Atom, so those snippets are likely to be very buggy.
Please raise an issue if you find an error.

They usually need a prefix or suffix to prevent them triggering accidentally.
The regular VSCode snippets use `;` as a prefix (creating a word boundary is also necessary) and need `tab` or `enter` to complete.
The Live Snippets do not need a prefix, use `⊔⊔` (double space) as a suffix, and they can complete automatically, if you've set up LaTeX-Utilities that way.
I could not find a way to get prefixes and suffixes to work with Atom, so you need to start a new word to start and hit `tab`/`enter` to complete.
These choices can be customised with the python code in this repo.

## Requirements

- Python ≥ 3.5 (for customising)
- VSCode:
  - [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
  - [LaTeX Utilities](https://marketplace.visualstudio.com/items?itemName=tecosaur.latex-utilities) (for live snippets)
- Atom:
  - [language-latex](https://atom.io/packages/language-latex)

## Installation

You need to copy the snippet JSON/CSON files to your user folder.
You probably want to append them to your existing snippets, rather than overwrite them.

- VSCode, normal snippets  
Copy `latex.json` to your `<user folder>/snippets`.
On Windows `<user folder>` is `%APPDATA%/Code/User` (not `%USERPROFILE%/.vscode`),
on Mac it is `$HOME/Library/Application Support/Code/User`,
on Linux it is `$HOME/.config/Code/User`

- VSCode, Live Snippets  
Copy `latexUtilsLiveSnippets.json` to your `<user folder>` (see VSCode instructions).
If you do not find a file with the same name already there, copying the file will erase all of the default live snippets.
If you want to append instead, you can create a file: in VSCode press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) then start typing `Edit Live Snippets File` and click on the entry when it appears.  
To enable automatic completion, you need `"latex-utilities.liveReformat.enabled": true` in your settings.

- Atom  
Copy `snippets.cson` to your Atom settings folder.
By default, on Windows this is `%userprofile/.atom`. 
on Mac it is `~/.atom`,
on Linux it is `/home/USER/.atom/`.  
If you already have some LaTeX snippets, make sure you combine the old and the new ones under one selector.
[Otherwise](https://flight-manual.atom.io/using-atom/sections/basic-customization/) you will disable the old snippets.

My preference is to use the Live Snippets, overwriting the defaults, and enabling live reformat.

## Customisation

If you open the jupyter notebook `custom.ipynb`, you will see the options listed.
You can make any changes you want and then run the appropriate cells to generate your file.
You might also want to do a bit of editing of `data/data.json` by hand, removing some entries.
