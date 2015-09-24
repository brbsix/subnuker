About
=====

This script is intended to scan subtitle files (or folders containing subtitle files) and prompt to remove cells with advertising. Subtitle files may be searched via regular expression or plaintext. The script can handle **srt** subtitle files natively or other formats (**ass**, **srt**, **ssa**, **sub**) via the Python module **aeidon**.

I recommend you check out my project subsystem_. It is used for batch processing of subtitle/video files from the terminal or GUI (i.e. Thunar custom actions or Nautilus actions). It allows you to rapidly do the following in order: rename video file(s), download subtitle file(s), then scan subtitle file(s) with subnuker.


Installation
============

::

  pip3 install --user subnuker

The subnuker package is compatible with Python 3.

subnuker can process **srt** subtitle files right out of the box. If you wish to handle other types of subtitle files, you'll need to install the **aeidon** module.

On Debian/Ubuntu, try:

::

  sudo apt-get install python3-aeidon

Or download the tarball for Gaupol_.
After unpacking, run:

::

  python3 setup.py --user --without-gaupol clean install

Additional information on installing Gaupol is available here:

https://github.com/otsaloma/gaupol/blob/master/README.aeidon.md


Usage
=====

From the command line, run :code:`subnuker --help` to display available options.s

The recommended way to scan any subtitle files (or folders containing subtitles):

::

  subnuker -ar TARGET...

By default, :code:`subnuker` scans subtitles with a built-in list of plaintext search terms or regular expression. :code:`subnuker` can also obtain patterns from multiple pattern files, similar to :code:`grep`'s :code:`--file` option.

::

  subnuker --file PATTERNFILE FILE.srt

The :code:`--aeidon` option indicates the use of the **aeidon** module. The **aeidon** module has full support for all subnuker options. I strongly recommend the use of the :code:`--aeidon` flag to process subtitle files suspected of damage.

::

  subnuker --aeidon FILE.srt

In general, I strongly recommend using the :code:`--regex` flag. The built-in regex "wordlist" will identify almost all advertisements with zero to no false positives. To scan **srt** subtitle files with regular expressions, run the following:

::

  subnuker --regex FILE1.srt FILE2.srt FILE3.srt


License
=======

Copyright (c) 2015 Six (brbsix@gmail.com).

Licensed under the GPLv3 license.

.. _subsystem: https://github.com/brbsix/subsystem

.. _Gaupol: http://home.gna.org/gaupol/download.html
