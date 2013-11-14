#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013 Hervé BREDIN (http://herve.niderb.fr/)
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

# copy DVD on hard drive
# python -m tvd.dvd copy

# extract multi-lingual audio tracks, multi-lingual subtitles, etc.
# python -m tvd.dvd dump

if __name__ == "__main__":

    import os
    import sys
    from argparse import ArgumentParser
    from tvd.dvd.rip import DVDRip
    from tvd.dvd.tvseries import TVSeriesDVD, TVSeriesDVDSet

    parser = ArgumentParser()

    parser.add_argument(
        'input', nargs='+', metavar='DVD', type=str,
        help='path to DVD directory (use more than one for DVD set)'
    )

    parser.add_argument(
        '--output', metavar='DIR', type=str,
        help='path to output directory'
    )

    # === Processing options ==================================================

    # parser.add_argument(
    #     '--video', action='store_true', help='extract video')

    # parser.add_argument(
    #     '--audio', action='store_true', help='extract audio tracks')

    # parser.add_argument(
    #     '--subtitles', action='store_true', help='extract subtitles')

    # parser.add_argument(
    #     '--debug', action='store_true', help='debug mode')

    # parser.add_argument(
    #     '--keep-tmp', action='store_true', help='keep temporary files')

    # === DVD options =========================================================

    dvd = parser.add_argument_group('Information about DVD (set)')

    dvd.add_argument(
        '--series', metavar='NAME', type=str, help='Name of the TV series')
    dvd.add_argument(
        '--season', metavar='N', type=int,
        help='season number in DVD (or DVD set)')
    dvd.add_argument(
        '--first', metavar='NN', type=int, default=1,
        help='first episode number in (first) DVD. defaults to 1.')

    # === Command line tools options ==========================================

    tools = parser.add_argument_group('Command line tools')

    tools.add_argument(
        '--lsdvd', metavar='PATH', type=str,
        help='path to lsdvd', default='lsdvd')

    tools.add_argument(
        '--mplayer', metavar='PATH', type=str,
        help='path to mplayer', default='mplayer')

    tools.add_argument(
        '--mencoder', metavar='PATH', type=str,
        help='path to mencoder', default='mencoder')

    tools.add_argument(
        '--vobsub2srt', metavar='PATH', type=str,
        help='path to vobsub2srt', default='vobsub2srt')

    tools.add_argument(
        '--tessdata', metavar='PATH', type=str,
        help='path to directory containing tessdata subdirectory',
        default=os.environ.get('TESSDATA_PREFIX', '.'))

    tools.add_argument(
        '--resample', metavar='PATH', type=str,
        help='path to sndfile-resample', default='sndfile-resample')

    try:
        args = parser.parse_args()
    except Exception, e:
        sys.exit(e)

    if len(args.input) == 1:
        dvd = TVSeriesDVD(
            args.series, args.season, args.first,
            dvd=args.input[0], lsdvd=args.lsdvd)

    else:
        dvd = TVSeriesDVDSet(
            args.series, args.season, args.input, lsdvd=args.lsdvd)

    rip = DVDRip(
        mplayer=args.mplayer, mencoder=args.mencoder,
        vobsub2srt=args.vobsub2srt, tessdata=args.tessdata,
        sndfile_resample=args.resample)

    dvd.dump(rip, args.output, verbose=True)
