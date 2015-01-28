#!/usr/bin/python3
"""Scan for and remove advertising from SRT subtitle files and/or folders"""


class Config:   # pylint: disable=R0903
    """Store global script configuration values."""

    charfixes = {'¶':'♪'}
    program = 'subnuker'
    results = False
    terms = ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x',
             '.com', '.net', '.org', 'air date', 'caption', 'download',
             'subtitle', 'sync', 'www.', 'âª']
    version = '0.1.dev1'


def error(*objs):
    """Print error message to stderr."""

    import sys

    print('ERROR:', *objs, file=sys.stderr)


def getch():
    """Request a single character input from the user."""

    import subprocess

    process = subprocess.Popen('read -rn1 && echo "$REPLY"',
                               executable='/bin/bash',
                               shell=True,
                               stderr=subprocess.PIPE,
                               stdout=subprocess.PIPE)

    return process.stdout.read().decode().strip()


def main():
    """Start application."""

    import os
    import sys

    options, arguments = parse()
    srts = prepfiles(arguments)

    if not srts:
        error('No valid targets were specified')
        sys.exit(1)

    # load terms from pattern files if necessary
    if options.termfiles:
        Config.terms = openterms(options.termfiles)

    for srt in srts:
        processfile(srt)

    if not Config.results:
        basenames = [os.path.basename(x) for x in srts]
        print('Search of', basenames, 'returned no results.')

        # leave the terminal open long enough
        if options.gui:
            from time import sleep
            sleep(2)


def openterms(termfiles):
    """Load files passed via `options` and return list of terms."""

    import sys
    terms = []

    for termfile in termfiles:
        try:
            terms += [l.rstrip('\n') for l in open(termfile)]
        except:     # pylint: disable=W0702
            error("Unable to load pattern file '%s'" % termfile)
            sys.exit(1)

    if terms:
        return terms
    else:
        error('No terms were loaded')
        sys.exit(1)


def parse():
    """
    Parse command-line arguments. Arguments may consist of any
    combination of directories, files, and options.
    """

    import argparse

    parser = argparse.ArgumentParser(
        add_help=False,
        description="Remove spam and advertising from subtitle files.",
        usage="%(prog)s [options] <srt files>")
    parser.add_argument(
        "-f", "--file",
        action="append",
        dest="termfiles",
        help="obtain match terms from FILE")
    parser.add_argument(
        "-g", "--gui",
        action="store_true",
        dest="gui",
        help="indicate use from a GUI")
    parser.add_argument(
        "-h", "--help",
        action="help",
        help=argparse.SUPPRESS)
    parser.add_argument(
        "--version",
        action="version",
        version="%s %s" % (Config.program, Config.version))
    parser.add_argument(
        action="append",
        dest="targets",
        help=argparse.SUPPRESS,
        nargs="*")

    options = parser.parse_args()
    arguments = options.targets[0]
    return options, arguments


def prepfiles(paths):
    """Parses `paths` (which may consist of files and/or directories).
    Removes duplicates, sorts, and returns verified srt files."""

    from batchpath import GeneratePaths
    import os

    return GeneratePaths().files(paths, os.W_OK, ['srt'], 0, True)


def processfile(srt):
    """Open, edit, and save subtitle file (as necessary)."""

    modified = False

    with open(srt) as file_open:
        text = file_open.read()

    # search and replace for problematic characters
    if Config.charfixes:
        keys = ''.join(Config.charfixes.keys())
        values = ''.join(Config.charfixes.values())
        replaced = text.translate(str.maketrans(keys, values))
        if replaced != text:
            modified = True
            text = replaced

    # split srt's text into a list consisting of cells
    cells = text.split('\n\n')

    # iterate over cells and prompt to remove any matches
    for index, cell in enumerate(cells):
        for term in Config.terms:
            if term in cell:
                Config.results = True
                if prompt(srt, cell, index, modified):
                    modified = True
                    cells.pop(index)

    if modified:
        savefile(srt, cells)


def prompt(filename, cell, index, modified):
    """Prompt user to remove cells from subtitle file."""

    import os
    import sys

    os.system('clear')
    print(cell)
    print('----------------------------------------')
    print("Delete cell %s of '%s'?" % (str(index + 1), filename))
    response = getch().lower()
    if response == 'y':
        os.system('clear')
        return True
    elif response == 'n':
        os.system('clear')
        return False
    else:
        if modified:
            warning("Not saving changes made to '%s'" % filename)
        sys.exit(0)


def savefile(srt, cells):
    """Format and save cells."""

    # fix the cell numbering
    for index, cell in enumerate(cells):
        cell_split = cell.split('\n')
        cell_split[0] = str(index + 1)
        cells[index] = '\n'.join(cell_split)

    # add a newline to the last line if necessary
    if not cells[-1].endswith('\n'):
        cells[-1] += '\n'

    # save the rejoined the list of cells
    with open(srt, 'w') as file_open:
        file_open.write('\n\n'.join(cells))


def warning(*objs):
    """Print warning message to stderr."""

    import sys
    print('WARNING:', *objs, file=sys.stderr)


main()
