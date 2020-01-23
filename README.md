# FasTeX_Snippets
Snippet version of FasTeX shortcuts for LaTeX, for VS Code and Atom.

This is a port of the FasTeX system of shortcuts to editors that use snippets, 
currently targeting VS Code and Atom.
It is based on the WinEdt version by Bernhard Enders.

- [FasTeX project](http://www.cds.caltech.edu/~fastex/fastex.html)
- [Original documentation](http://www.cds.caltech.edu/~fastex/fastex_docs.html)
- [WinEdt version](http://www.winedt.org/macros/latex/FasTeX.html)

The basic idea is that the shortcuts are made up of lower-case letter and (occasionally) numbers.
This means you can type them without reaching for modifier keys and symbols, 
e.g. `bksl` maps too `\`, `ob` to `{` (open braces) and `eb` to `}` (end braces).
The shortcuts are fairly systematic: prefix `x` for greek, `c` for upper-case, `d` for in dollars,
`h` for superscript, `l` for subscript (high & low), `o` for in parentheses,...
so `dxcd` gives you `$\Delta$`, `hct` gives `^T`, `lij` gives `_{ij}`, `ox` gives `(x)`,....
Have a look at the documentation linked to above for more information.

There are nearly 1600 shortcuts, so I haven't tested them all in this implementation.
Please raise an issue if you find an error.
I have also mostly stopped using Atom, so those snippets are likely to be very buggy.

They usually need a prefix or suffix to prevent them triggering accidentally.
The regular VS Code snippets use `;` as a prefix (creating a word boundary is also necessary) and need `tab` or `enter` to complete.
The Live Snippets use `  ` (double space) as a suffix and they can complete automatically, if you've set up LaTeX-Utilities that way.
I could not find a way to get prefixes and suffixes to work with Atom.
These choices can be customised with the python code in this repo.

## Requirements

- Python ≥ 3.5 (for customising)
- VS Code:
  - [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop)
  - [LaTeX Utilities](https://marketplace.visualstudio.com/items?itemName=tecosaur.latex-utilities) (for live snippets)
- Atom:
  - [language-latex](https://atom.io/packages/language-latex)

## Installation

You need to copy the snippet JSON/CSON files to your user folder.
You probably want to append them to your existing snippets, rather than overwrite them.

- VS Code, normal snippets  
Copy `latex.cson` to your `<user folder>/snippets`.
On Windows `<user folder>` is `%appdata%/Code/User`, not `%userprofile%/.vscode`.
On Mac it is `$HOME/Library/Application Support/Code/User/settings.json`.
On Linux it is `$HOME/.config/Code/User/settings.json`

- VS Code, Live Snippets  
Copy `latexUtilsLiveSnippets.json` to your `<user folder>` (see VS Code instructions).
If you do not find a file with the same name already there, copying the file will erase all of the default live snippets.
If you want to append instead, you can create a file: in VS Code press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) then start typing `Edit Live Snippets File` and click on the entry when it appears.  
To enable automatic completion, you need `"latex-utilities.liveReformat.enabled": true` in your settings.

- Atom  
Copy `snippets.cson` to your Atom settings folder.
By default, on Windows this is `%userprofile/.atom`. 
on Mac it is `~/.atom`,
on Linux it is `/home/USER/.atom/`.  
If you already have some LaTeX snippets, make sure you combine the old and the new ones under one selector.
[Otherwise](https://flight-manual.atom.io/using-atom/sections/basic-customization/) you will disable the old snippets.

My preference is to use the Live Snippets, overwriting the defaults, and enabling live reformat.
