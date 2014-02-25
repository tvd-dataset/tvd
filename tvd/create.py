#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 Hervé BREDIN (http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import tvd
import sys
from path import path
from tvd.command import Vobcopy


if __name__ == '__main__':

    from argparse import ArgumentParser, HelpFormatter

    main_parser = ArgumentParser(
        prog=None,
        usage=None,
        description=None,
        epilog=None,
        version=None,
        parents=[],
        formatter_class=HelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True
    )

    # =========================================================================

    commands = ["vobcopy", ]
    tool_parent_parser = ArgumentParser(add_help=False)

    name = '--{command}'
    help = 'path to "{command}" (if installed in non-standard directory)'

    for command in commands:
        tool_parent_parser.add_argument(
            name.format(command=command),
            metavar='PATH',
            type=str,
            default=command,
            help=help.format(command=command)
        )

    # =========================================================================

    series_parent_parser = ArgumentParser(add_help=False)
    help = ''

    series = tvd.get_series()
    choices = [series_name for series_name in series]
    help = 'series'

    series_parent_parser.add_argument(
        'series',
        help=help,
        choices=choices,
        type=str,
    )

    # =========================================================================

    title = ''
    help = ''
    modes = main_parser.add_subparsers(title=title, help=help)

    # =========================================================================
    # "dump" mode
    # =========================================================================

    description = ''
    dump_mode = modes.add_parser(
        'dump',
        description=description,
        parents=[tool_parent_parser, series_parent_parser]
    )

    # -------------------------------------------------------------------------

    def dump_func(args):

        vobcopy = Vobcopy(vobcopy=args.vobcopy)

        # create 'to' directory if needed
        # TVD_DIR/TheBigBangTheory/dvd/copy/
        to = path.joinpath(args.tvd, args.series, 'dvd', 'copy')
        to.makedirs_p()

        # Season01.Disc01
        name = "Season{season:02d}.Disc{disc:02d}"

        dvd = args.dvd if hasattr(args, 'dvd') else None
        vobcopy(
            str(to),
            name=name.format(season=args.season, disc=args.disc),
            dvd=dvd
        )

    # -------------------------------------------------------------------------

    help = 'set season number (e.g. 1 for first season)'
    dump_mode.add_argument('season', metavar='SEASON', type=int, help=help)

    help = 'set disc number (e.g. 1 for first disc)'
    dump_mode.add_argument('disc', metavar='DISC', type=int, help=help)

    help = 'set path to TVD root directory'
    dump_mode.add_argument('tvd', metavar='TVD_DIR', type=str, help=help)

    help = 'path to DVD'
    dump_mode.add_argument('--dvd', metavar='DVD', type=str, help=help)

    dump_mode.set_defaults(func=dump_func)

    # =========================================================================

    try:
        args = main_parser.parse_args()
    except Exception, e:
        sys.exit(e)

    args.func(args)
