#!/usr/bin/python3
"""Scan for and remove advertising from SRT subtitle files and/or folders"""


class Config:   # pylint: disable=R0903
    """Store global script configuration values."""

    charfixes = {'¶': '♪'}
    patterns = []
    program = 'subnuker'
    results = False
    regex = ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x',
             r'(?<!\.)\.com', r'(?<!\.)\.net', r'(?<!\.)\.org', 'air date', 'caption', 'download',
             'subtitle', 'sync', r'(?<![A-Za-z0-9])www\.', 'âª']
    terms = ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x',
             '.com', '.net', '.org', 'air date', 'caption', 'download',
             'subtitle', 'sync', 'www.', 'âª']
    version = '0.1.dev1'


class SubtitleFile:
    """Process individual subtitle file."""
    def __init__(self, filename, options):
        self.filename = filename
        self.modified = False

        text = self.open()

        if Config.charfixes:
            text = self.fixchars(text)

        self.cells = self.split(text)

        matches = search(self.cells)

        if matches:
            Config.results = True
            deletions = self.prompt(matches, options.autoyes)
            if deletions:
                self.cells = remove_elements(self.cells, deletions)
                self.modified = True

        if self.modified:
            save_file(self.filename, self.cells)

    def fixchars(self, text):
        """Find and replace problematic characters."""
        keys = ''.join(Config.charfixes.keys())
        values = ''.join(Config.charfixes.values())
        fixed = text.translate(str.maketrans(keys, values))
        if fixed != text:
            self.modified = True
            return fixed

    def open(self):
        """Open the subtitle file (detect encoding if necessary)."""
        with open(self.filename, 'rb') as file_open:
            binary = file_open.read()

        try:
            return binary.decode()
        except UnicodeDecodeError:
            from chardet import detect
            encoding = detect(binary).get('encoding')
            try:
                return binary.decode(encoding)
            except LookupError:
                return binary.decode(errors='ignore')

    def prompt(self, matches, autoyes):
        """Prompt user to remove cells from subtitle file."""

        if autoyes:
            return matches

        deletions = []

        for match in matches:
            os.system('clear')
            print(self.cells[match])
            print('----------------------------------------')
            print("Delete cell %s of '%s'?" % (str(match + 1), self.filename))
            response = getch().lower()
            if response == 'y':
                os.system('clear')
                deletions.append(match)
            elif response == 'n':
                os.system('clear')
            else:
                if deletions or self.modified:
                    warning("Not saving changes made to '%s'" % self.filename)
                sys.exit(0)

        return deletions

    def split(self, text):
        """Split text into a list of cells."""

        import re
        if re.search('\n\n', text):
            return text.split('\n\n')
        elif re.search('\r\n\r\n', text):
            return text.split('\r\n\r\n')
        else:
            error("'%s' does not appear to be a 'srt' subtitle file" % self.filename)
            sys.exit(1)


def error(*objs):
    """Print error message to stderr."""

    print('ERROR:', *objs, file=sys.stderr)


# def getch():
#     """Request a single character input from the user."""

#     import subprocess

#     process = subprocess.Popen('read -rn1 && echo "$REPLY"',
#                                executable='/bin/bash',
#                                shell=True,
#                                stderr=subprocess.PIPE,
#                                stdout=subprocess.PIPE)

#     return process.stdout.read().decode().strip()


def getch():
    """Request a single character input from the user."""

    if sys.platform in ['darwin', 'linux']:
        import termios
        import tty
        file_descriptor = sys.stdin.fileno()
        settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, settings)
    elif sys.platform in ['cygwin', 'win32']:
        import msvcrt
        return msvcrt.getwch()


def ismatch(text, pattern):
    """Test whether text contains string or matches regex."""

    if hasattr(pattern, 'search'):
        return pattern.search(text)
    else:
        return pattern in text


def main():
    """Start application."""

    options, arguments = parse()
    srts = prep_files(arguments)

    if not srts:
        error('No valid targets were specified')
        sys.exit(1)

    # load terms from pattern files if necessary
    if options.termfiles:
        Config.terms = open_terms(options.termfiles)

    # compile regex patterns if necessary
    if options.regex:
        if options.termfiles:
            Config.patterns = prep_regex(Config.terms)
        else:
            Config.patterns = prep_regex(Config.regex)
    else:
        Config.patterns = Config.terms

    for srt in srts:
        SubtitleFile(srt, options)

    if not Config.results:
        basenames = [os.path.basename(x) for x in arguments]
        print('Search of', basenames, 'returned no results.')

        # leave the terminal open long enough to read
        if options.gui:
            from time import sleep
            sleep(2)


def open_terms(termfiles):
    """Load files passed via options and return list of terms."""

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
    """Parse command-line arguments. Arguments may consist of any
    combination of directories, files, and options."""

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
        "--regex",
        action="store_true",
        dest="regex",
        help="indicate use of regex matches")
    parser.add_argument(
        "--version",
        action="version",
        version="%s %s" % (Config.program, Config.version))
    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        dest="autoyes",
        help="automatic yes to prompts")
    parser.add_argument(
        action="append",
        dest="targets",
        help=argparse.SUPPRESS,
        nargs="*")

    options = parser.parse_args()
    arguments = options.targets[0]
    return options, arguments


def prep_files(paths):
    """Parses `paths` (which may consist of files and/or directories).
    Removes duplicates, sorts, and returns verified srt files."""

    from batchpath import GeneratePaths
    return GeneratePaths().files(paths, os.W_OK, ['srt'], 0, True)


def prep_regex(patterns):
    """Compile regex patterns."""

    import re
    return [re.compile(pattern) for pattern in patterns]


def remove_elements(target, indices):
    """Remove multiple elements from a list and return result.
    This implementation is faster than the alternative below.
    Also note the creation of a new list to avoid altering the
    original. We don't have any current use for the original
    intact list, but may in the future..."""

    copied = list(target)

    for index in sorted(indices, reverse=True):
        del copied[index]
    return copied


# def remove_elements(target, indices):
#     """Remove multiple elements from a list and return result."""
#     return [e for i, e in enumerate(target) if i not in indices]


def save_file(filename, cells):
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
    with open(filename, 'w') as file_open:
        file_open.write('\n\n'.join(cells))


def search(cells):
    """Return list of cells to be removed."""

    matches = []
    for index, cell in enumerate(cells):
        for pattern in Config.patterns:
            if ismatch(cell, pattern):
                matches.append(index)
                break

    return matches


def warning(*objs):
    """Print warning message to stderr."""

    print('WARNING:', *objs, file=sys.stderr)


import os
import sys

if __name__ == '__main__':
    main()
