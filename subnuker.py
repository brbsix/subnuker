#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Remove advertising from subtitle files

This script is intended to scan subtitle files (or folders containing subtitle
files) and prompt to remove cells with advertising. Subtitle files may be
searched via regular expression or text matches. The script can handle srt
subtitle files natively or other formats (ass, srt, ssa, sub) via the aeidon
Python package.
"""

__program__ = 'subnuker'
__version__ = '0.4.1'


# --- BEGIN CODE --- #

import os
import sys


class Config:   # pylint: disable=R0903
    """Store global script configuration values."""

    charfixes = {'¶': '♪'}
    results = False
    regex = ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x',
             r'(?<!\.)\.com', r'(?<!\.)\.net', r'(?<!\.)\.org',
             'air date', 'caption', 'download', 'subtitle', 'sync',
             'TVShow', r'(?<![A-Za-z0-9])www\.', 'âª']
    terms = ['1x', '2x', '3x', '4x', '5x', '6x', '7x', '8x', '9x',
             '.com', '.net', '.org', 'air date', 'caption', 'download',
             'subtitle', 'sync', 'TVShow', 'www.', 'âª']

    # Used for storing parsed options/arguments
    arguments = None
    options = None

    # Used for storing loaded terms or compiled regex)
    patterns = []


class AeidonProject:
    """Process individual subtitle files with python3-aeidon."""
    def __init__(self, filename):
        try:
            import aeidon
        except ImportError:
            prerequisites()
            sys.exit(1)

        self.filename = filename
        self.project = aeidon.Project()  # pylint: disable=W0201

        self.open()

        self.fixchars()

        matches = self.search()

        if matches:
            Config.results = True
            deletions = self.prompt(matches)
            if deletions:
                self.project.remove_subtitles(deletions)

        if self.modified:
            self.save()

    def fixchars(self):
        """Replace characters or strings within subtitle file."""
        for key in Config.charfixes:
            self.project.set_search_string(key)
            self.project.set_search_replacement(Config.charfixes[key])
            self.project.replace_all()

    @property
    def modified(self):
        """Check whether subtitle file has been modified."""
        return True if self.project.main_changed > 0 else False

    def open(self):
        """Open the subtitle file into an Aeidon project."""
        try:
            self.project.open_main(self.filename)
        except UnicodeDecodeError:
            try:
                from chardet import detect
            except ImportError:
                error("Please install python module 'chardet'.")
                sys.exit(1)

            encoding = detect(open(self.filename, 'rb').read()).get('encoding')

            try:
                self.project.open_main(self.filename, encoding)
            except UnicodeDecodeError:
                error("'%s' encountered a fatal encoding error" %
                      self.filename)
                sys.exit(1)
            except:  # pylint: disable=W0702
                open_error(self.filename)

        except:  # pylint: disable=W0702
            open_error(self.filename)

    def prompt(self, matches):
        """Prompt user to remove cells from subtitle file."""

        if Config.options.autoyes:
            return matches

        deletions = []

        for match in matches:
            os.system('clear')
            print(self.project.main_file.read()[match].main_text)
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

    def save(self):
        """Save subtitle file."""
        try:
            self.project.save_main()
        except:  # pylint: disable=W0702
            error("Unable to save '%s'" % self.filename)
            sys.exit(1)

    def search(self):
        """Search srt in project for cells matching list of terms."""

        matches = []
        for pattern in Config.patterns:
            matches += self.termfinder(pattern)

        return sorted(set(matches), key=int)

    def termfinder(self, pattern):
        """Search srt in project for cells matching term."""

        if Config.options.regex:
            self.project.set_search_regex(pattern)
        else:
            self.project.set_search_string(pattern)

        matches = []
        while True:
            try:
                if len(matches) == 0:
                    matches.append(self.project.find_next()[0])
                else:
                    last = matches[-1]
                    new = self.project.find_next(last + 1)[0]
                    if new != last and new > last:
                        matches.append(new)
                    else:
                        break
            except StopIteration:
                break

        return matches


class SrtProject:
    """Process individual srt files."""
    def __init__(self, filename):
        self.filename = filename
        self.modified = False

        text = self.open()

        if Config.charfixes:
            text = self.fixchars(text)

        self.cells = self.split(text)

        matches = self.search()

        if matches:
            Config.results = True
            deletions = self.prompt(matches)
            if deletions:
                self.cells = remove_elements(self.cells, deletions)
                self.modified = True

        if self.modified:
            self.save()

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
            except:  # pylint: disable=W0702
                open_error(self.filename)
        except:  # pylint: disable=W0702
            open_error(self.filename)

    def prompt(self, matches):
        """Prompt user to remove cells from subtitle file."""

        if Config.options.autoyes:
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

    def save(self):
        """Format and save cells."""

        # fix the cell numbering
        for index, cell in enumerate(self.cells):
            cell_split = cell.splitlines()
            cell_split[0] = str(index + 1)
            self.cells[index] = '\n'.join(cell_split)

        # add a newline to the last line if necessary
        if not self.cells[-1].endswith('\n'):
            self.cells[-1] += '\n'

        # save the rejoined the list of cells
        with open(self.filename, 'w') as file_open:
            file_open.write('\n\n'.join(self.cells))

    def search(self):
        """Return list of cells to be removed."""

        matches = []
        for index, cell in enumerate(self.cells):
            for pattern in Config.patterns:
                if ismatch(cell, pattern):
                    matches.append(index)
                    break

        return matches

    def split(self, text):
        """Split text into a list of cells."""

        import re
        if re.search('\n\n', text):
            return text.split('\n\n')
        elif re.search('\r\n\r\n', text):
            return text.split('\r\n\r\n')
        else:
            error("'%s' does not appear to be a 'srt' subtitle file" %
                  self.filename)
            sys.exit(1)


def error(*objs):
    """Print error message to stderr."""

    print('ERROR:', *objs, file=sys.stderr)


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


def main(args=None):
    """Start application."""

    Config.options, Config.arguments = parse(args)

    if Config.options.aeidon:
        start_aeidon()
    else:
        start_srt()

    if not Config.results:
        basenames = [os.path.basename(os.path.abspath(x)) for x in Config.arguments]
        print('Search of', basenames, 'returned no results.')

        # leave the terminal open long enough to read message
        if Config.options.gui:
            from time import sleep
            sleep(2)


def open_error(filename):
    """Display a generic error message upon failure to open file."""
    error("Unable to open '%s'" % filename)
    sys.exit(1)


def parse(args):
    """Parse command-line arguments. Arguments may consist of any
    combination of directories, files, and options."""

    import argparse

    parser = argparse.ArgumentParser(
        add_help=False,
        description="Remove spam and advertising from subtitle files.",
        usage="%(prog)s [options] <srt files>")
    parser.add_argument(
        "-a", "--aeidon",
        action="store_true",
        dest="aeidon",
        help="use python3-aeidon to process subtitles")
    parser.add_argument(
        "-f", "--file",
        action="append",
        dest="file",
        help="obtain matches from FILE")
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
        "-r", "--regex",
        action="store_true",
        dest="regex",
        help="indicate use of regex matches")
    parser.add_argument(
        "--version",
        action="version",
        version="%s %s" % (__program__, __version__))
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

    options = parser.parse_args(args)
    arguments = options.targets[0]

    return options, arguments


def pattern_logic_aeidon():
    """Return patterns to be used for searching subtitles via aeidon."""

    if Config.options.file:
        return prep_patterns(Config.options.file)
    elif Config.options.regex:
        return Config.regex
    else:
        return Config.terms


def pattern_logic_srt():
    """Return patterns to be used for searching srt subtitles."""

    if Config.options.file and Config.options.regex:
        return prep_regex(prep_patterns(Config.options.file))
    elif Config.options.file:
        return prep_patterns(Config.options.file)
    elif Config.options.regex:
        return prep_regex(Config.regex)
    else:
        return Config.terms


def prep_files(paths, extensions):
    """Parses `paths` (which may consist of files and/or directories).
    Removes duplicates, sorts, and returns verified srt files."""

    from batchpath import GeneratePaths

    filenames = GeneratePaths().files(paths, os.W_OK, extensions, 0, True)

    if filenames:
        return filenames
    else:
        error('No valid targets were specified')
        sys.exit(1)


def prep_patterns(filenames):
    """Load pattern files passed via options and return list of patterns."""

    patterns = []

    for filename in filenames:
        try:
            patterns += [l.rstrip('\n') for l in open(filename)]
        except:  # pylint: disable=W0702
            error("Unable to load pattern file '%s'" % filename)
            sys.exit(1)

    if patterns:
        return patterns
    else:
        error('No terms were loaded')
        sys.exit(1)


def prep_regex(patterns):
    """Compile regex patterns."""

    import re
    return [re.compile(pattern) for pattern in patterns]


def prerequisites():
    """Display information about obtaining the aeidon module."""
    url = "http://home.gna.org/gaupol/download.html"
    debian = "sudo apt-get install python3-aeidon"
    other = "python3 setup.py --user --without-gaupol clean install"

    error("The aeidon module is missing!")
    stderr("\nTry '{0}' or the appropriate command for your package manager."
           .format(debian))
    stderr("\nYou can also download the tarball for gaupol @ {0} which "
           "includes aeidon. After downloading, unpack and run '{1}'."
           .format(url, other))


def remove_elements(target, indices):
    """Remove multiple elements from a list and return result.
    This implementation is faster than the alternative below.
    Also note the creation of a new list to avoid altering the
    original. We don't have any current use for the original
    intact list, but may in the future..."""

    copied = list(target)

    for index in reversed(indices):
        del copied[index]
    return copied


# def remove_elements(target, indices):
#     """Remove multiple elements from a list and return result."""
#     return [e for i, e in enumerate(target) if i not in indices]


def start_aeidon():
    """Prepare filenames and patterns then process subtitles with aeidon."""

    extensions = ['ass', 'srt', 'ssa', 'sub']
    Config.filenames = prep_files(Config.arguments, extensions)

    Config.patterns = pattern_logic_aeidon()

    for filename in Config.filenames:
        AeidonProject(filename)


def start_srt():
    """Prepare filenames and patterns then process srt subtitles."""

    extensions = ['srt']
    Config.filenames = prep_files(Config.arguments, extensions)

    Config.patterns = pattern_logic_srt()

    for filename in Config.filenames:
        SrtProject(filename)


def stderr(*objs):
    """Print message to stderr."""
    print(*objs, file=sys.stderr)


def warning(*objs):
    """Print warning message to stderr."""

    print('WARNING:', *objs, file=sys.stderr)
