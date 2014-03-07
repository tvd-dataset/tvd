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

import logging
logging.basicConfig(level=logging.INFO)

import os
import tvd
import sys
from path import path
from tvd.command import \
    Vobcopy, HandBrakeCLI, \
    MEncoder, VobSub2SRT, \
    AVConv, SndFileResample
from tvd.common.dvd import TVSeriesDVDSet
from tvd.common.episode import Episode
import re
import json

PATTERN_DUMP = (
    '{tvd}/{series}/dvd/dump/',
    'Season{season:02d}.Disc{disc:02d}'
)

PATTERN_RIP_VIDEO = (
    '{tvd}/{series}/dvd/rip/video/'
    '{series}.Season{season:02d}.Episode{episode:02d}.mkv'
)

PATTERN_RIP_STREAM = (
    '{tvd}/{series}/dvd/rip/stream/'
    '{series}.Season{season:02d}.Episode{episode:02d}.{format}'
)

PATTERN_RIP_SUBTITLE = (
    '{tvd}/{series}/dvd/rip/subtitles/'
    '{series}.Season{season:02d}.Episode{episode:02d}.{language}.srt'
)

PATTERN_RIP_AUDIO = (
    '{tvd}/{series}/dvd/rip/audio/'
    '{series}.Season{season:02d}.Episode{episode:02d}.{language}.wav'
)

PATTERN_RESOURCE = (
    '{tvd}/{series}/www/{resource}/'
    '{series}.Season{season:02d}.Episode{episode:02d}.json'
)

if __name__ == '__main__':

    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    description = (
        'dump    dump DVD onto disk.\n'
        'rip     extract video, audio and subtitle tracks\n'
        'www     download metadata from the web\n'
        'stream  prepare video for streaming (optional)\n'
    )

    main_parser = ArgumentParser(
        prog=None,
        usage=None,
        description=description,
        epilog=None,
        version=None,
        parents=[],
        formatter_class=RawDescriptionHelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True
    )

    # =========================================================================
    # parent parser with all command line tool options

    commands = [
        "vobcopy",
        "lsdvd",
        "HandBrakeCLI",
        "mencoder",
        "vobsub2srt",
        "avconv",
        "sndfile-resample",
    ]
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

    help = 'path to the parent directory of your "tessdata" directory'
    tool_parent_parser.add_argument(
        '--tessdata',
        metavar='PATH',
        type=str,
        help=help,
        default=os.getenv('TESSDATA_PREFIX')
    )

    # =========================================================================
    # parent parser allowing to select among all available series plugin

    series_parent_parser = ArgumentParser(add_help=False)

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
    # parent parser allowing to set TVD root directory and the 'force' flag

    tvd_parent_parser = ArgumentParser(add_help=False)

    help = 'set path to TVD root directory'
    tvd_parent_parser.add_argument(
        'tvd', metavar='TVD_DIR', type=str, help=help)

    help = 'force overwrite of existing files'
    tvd_parent_parser.add_argument(
        '--force', action='store_true', help=help)

    # =========================================================================

    modes = main_parser.add_subparsers()

    # =========================================================================
    # "dump" mode
    # =========================================================================

    description = 'Dump DVD onto disk'
    dump_mode = modes.add_parser(
        'dump',
        description=description,
        parents=[tvd_parent_parser, tool_parent_parser, series_parent_parser],
    )

    # -------------------------------------------------------------------------

    def dump_func(args):

        # tools
        vobcopy = Vobcopy(vobcopy=args.vobcopy)

        # mount point where vobcopy should look for the DVD
        dvd = args.dvd if hasattr(args, 'dvd') else None

        # directory where vobcopy will dump the DVD directory
        dump_to = PATTERN_DUMP[0].format(tvd=args.tvd, series=args.series)

        # example: Season01.Disc01
        name = PATTERN_DUMP[1].format(season=args.season, disc=args.disc)

        # full directory resulting from vobcopy dump
        full_name = '{to}/{name}'.format(to=dump_to, name=name)
        logging.info('Dumping to {full_name}'.format(full_name=full_name))

        # make sure it does not exist already
        if path(full_name).exists() and not args.force:
            logging.error('{name} already exists'.format(name=full_name))

        else:
            # create 'dump_to' directory if needed
            path(dump_to).makedirs_p()
            # dump
            vobcopy(dump_to, name=name, dvd=dvd)

    # -------------------------------------------------------------------------

    help = 'set season number (e.g. 1 for first season)'
    dump_mode.add_argument('season', metavar='SEASON', type=int, help=help)

    help = 'set disc number (e.g. 1 for first disc)'
    dump_mode.add_argument('disc', metavar='DISC', type=int, help=help)

    help = 'path to DVD'
    dump_mode.add_argument('--dvd', metavar='DVD', type=str, help=help)

    dump_mode.set_defaults(func=dump_func)

    # =========================================================================
    # "rip" mode
    # =========================================================================

    description = 'Rip previously dumped DVDs in all available languages'
    rip_mode = modes.add_parser(
        'rip',
        description=description,
        parents=[tvd_parent_parser, tool_parent_parser, series_parent_parser]
    )

    # -------------------------------------------------------------------------

    def rip_func(args):

        # comparison function used to make sure
        # audio tracks in original language is first
        series = tvd.get_series()[args.series]()
        original_language = series.language

        def _audio_cmp((i1, l1), (i2, l2)):
            if l1 == original_language:
                return -1
            if l2 == original_language:
                return 1
            else:
                return cmp(i1, i2)

        # tools
        lsdvd = args.lsdvd
        handbrake = HandBrakeCLI(handbrake=args.HandBrakeCLI)
        mencoder = MEncoder(mencoder=args.mencoder)
        vobsub2srt = VobSub2SRT(
            vobsub2srt=args.vobsub2srt,
            tessdata=args.tessdata
        )
        avconv = AVConv(avconv=args.avconv)
        sndfile_resample = SndFileResample(
            sndfile_resample=args.sndfile_resample)

        # gather list of disc available for requested series/season
        dump_to = PATTERN_DUMP[0].format(tvd=args.tvd, series=args.series)
        disc_pattern = 'Season{season:02d}.Disc*'.format(season=args.season)
        dvds = path(dump_to).listdir(pattern=disc_pattern)
        dvds = [str(d) for d in dvds]

        logging.debug('Found {number:d} DVDs'.format(number=len(dvds)))
        for d, dvd in enumerate(dvds):
            logging.debug('{d} - {dvd}'.format(d=d+1, dvd=dvd))

        # create TV series DVD set
        seasonDVDSet = TVSeriesDVDSet(
            args.series, args.season, dvds, lsdvd=lsdvd)

        for episode, dvd, title in seasonDVDSet.iter_episodes():

            logging.info('Ripping {episode}'.format(episode=episode))

            dump_to = dvd.dvd

            # get audio tracks as [(1, 'en'), (2, 'fr'), ...]
            audio = list(title.iter_audio())

            # move audio tracks in original language at the beginning
            audio.sort(cmp=_audio_cmp)

            # get subtitle tracks as [1, 2, 3, 4, 5, ...]
            subtitles = [index for index, _ in title.iter_subtitles()]

            # rip episode into .mkv
            handbrake_to = PATTERN_RIP_VIDEO.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode
            )

            logging.info('mkv: {to}'.format(to=handbrake_to))

            # make sure output file does not exist already
            if path(handbrake_to).exists() and not args.force:
                logging.error(
                    '{name} already exists'.format(name=handbrake_to))

            else:
                # create containing directory if needed
                path(handbrake_to).dirname().makedirs_p()
                # rip title into mkv
                handbrake.extract_title(
                    dump_to, title.index, handbrake_to,
                    audio=audio, subtitles=subtitles
                )

            # extract subtitles
            for index, language in title.iter_subtitles():

                rip_srt_to = PATTERN_RIP_SUBTITLE.format(
                    tvd=args.tvd,
                    series=episode.series,
                    season=episode.season,
                    episode=episode.episode,
                    language=language
                )

                logging.info('srt: {to}'.format(to=rip_srt_to))

                # make sure output file does not exist already
                if path(rip_srt_to).exists() and not args.force:
                    logging.error('{s} already exists'.format(s=rip_srt_to))

                else:
                    # create containing directory if needed
                    path(rip_srt_to).dirname().makedirs_p()
                    try:
                        # extract .sub and .idx
                        mencoder_to = str(path(rip_srt_to).splitext()[0])
                        mencoder.vobsub(
                            dump_to, title.index, language, mencoder_to)
                        # ... to srt
                        vobsub2srt(mencoder_to, language)
                    except Exception:
                        logging.error('srt: {to} FAILED'.format(to=rip_srt_to))

            # extract audio tracks
            for stream, (index, language) in enumerate(audio):

                rip_wav_to = PATTERN_RIP_AUDIO.format(
                    tvd=args.tvd,
                    series=episode.series,
                    season=episode.season,
                    episode=episode.episode,
                    language=language
                )

                logging.info('wav: {to}'.format(to=rip_wav_to))

                # make sure output file does not exist already
                if path(rip_wav_to).exists() and not args.force:
                    logging.error('{w} already exists'.format(w=rip_wav_to))

                else:
                    # create containing directory if needed
                    path(rip_wav_to).dirname().makedirs_p()
                    # .wav --> .raw.wav
                    avconv_to = path(rip_wav_to).splitext()[0] + '.raw.wav'
                    avconv_to = str(avconv_to)
                    # extract raw audio
                    avconv.audio_track(handbrake_to, stream+1, avconv_to)
                    # sndfile-resample avconv_to --> rip_wav_to
                    sndfile_resample.to16kHz(avconv_to, rip_wav_to)

    # -------------------------------------------------------------------------

    help = 'set season number (e.g. 1 for first season)'
    rip_mode.add_argument('season', metavar='SEASON', type=int, help=help)

    rip_mode.set_defaults(func=rip_func)

    # =========================================================================
    # "stream" mode
    # =========================================================================

    description = 'Encode previously ripped episodes into mp4/webm/ogv formats'
    stream_mode = modes.add_parser(
        'stream',
        description=description,
        parents=[tvd_parent_parser, tool_parent_parser, series_parent_parser]
    )

    # -------------------------------------------------------------------------

    def stream_func(args):

        avconv = AVConv(avconv=args.avconv)

        # find all SERIES.Season**.Episode**.mkv files
        # in TVD/SERIES/dvd/rip/
        # and store all corresponding Episode in episodes list
        episodes = []

        handbrake_to = PATTERN_RIP_VIDEO.format(
            tvd=args.tvd, series=args.series,
            season=1, episode=1
        )
        mkvs = path(handbrake_to).dirname().listdir()

        p = re.compile(
            '{series}.Season([0-9][0-9]).Episode([0-9][0-9]).mkv'.format(
                series=args.series)
        )
        for mkv in mkvs:
            m = p.search(mkv)
            if m is None:
                continue
            season, episode = m.groups()
            episode = Episode(
                series=args.series, season=int(season), episode=int(episode))
            episodes.append(episode)

        logging.debug('Found {number:d} episodes'.format(number=len(episodes)))
        for e, episode in enumerate(episodes):
            logging.debug('{e:d} - {episode}'.format(e=e+1, episode=episode))

        # process every episode
        for episode in episodes:

            # path to mkv file
            handbrake_to = PATTERN_RIP_VIDEO.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode
            )

            # extract video in series original language
            # in several format (ogg, mp4, webm) for streaming

            stream = 1  # rip mode makes sure first audio stream
                        # is in original language

            # -- ogv --
            ogv_to = PATTERN_RIP_STREAM.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode,
                format='ogv'
            )

            logging.info('ogv: {to}'.format(to=ogv_to))

            # do not re-generate existing file
            if path(ogv_to).exists() and not args.force:
                logging.error('{to} already exists.'.format(to=ogv_to))

            else:
                # create containing directory if needed
                path(ogv_to).dirname().makedirs_p()
                avconv.ogv(handbrake_to, stream, ogv_to)

            # -- mp4 --
            mp4_to = PATTERN_RIP_STREAM.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode,
                format='mp4'
            )

            logging.info('mp4: {to}'.format(to=mp4_to))

            # do not re-generate existing file
            if path(mp4_to).exists() and not args.force:
                logging.error('{to} already exists.'.format(to=mp4_to))

            else:
                # create containing directory if needed
                path(mp4_to).dirname().makedirs_p()
                avconv.mp4(handbrake_to, stream, mp4_to)

            # -- webm --
            webm_to = PATTERN_RIP_STREAM.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode,
                format='webm'
            )
            logging.info('webm: {to}'.format(to=webm_to))

            # do not re-generate existing file
            if path(webm_to).exists() and not args.force:
                logging.error('{to} already exists.'.format(to=webm_to))

            else:
                # create containing directory if needed
                path(webm_to).dirname().makedirs_p()
                avconv.webm(handbrake_to, stream, webm_to)

    # -------------------------------------------------------------------------

    stream_mode.set_defaults(func=stream_func)

    # =========================================================================
    # "www" mode
    # =========================================================================

    description = 'Download metadata resources'
    www_mode = modes.add_parser(
        'www',
        description=description,
        parents=[tvd_parent_parser, tool_parent_parser, series_parent_parser]
    )

    # -------------------------------------------------------------------------

    def www_func(args):

        # initialize series plugin
        series = tvd.get_series()[args.series]()

        # loop on all available resources
        for episode, resource_type, resource in series.iter_resources(
            resource_type=None, episode=None, update=True
        ):

            # save resource to PATTERN_RESOURCE in JSON format

            json_to = PATTERN_RESOURCE.format(
                tvd=args.tvd,
                series=episode.series,
                season=episode.season,
                episode=episode.episode,
                resource=resource_type,
            )
            logging.info('www: {to}'.format(to=json_to))

            # do not re-generate existing file
            if path(json_to).exists() and not args.force:
                logging.error('{to} already exists.'.format(to=json_to))
            else:
                # create containing directory if needed
                path(json_to).dirname().makedirs_p()
                with open(json_to, mode='w') as f:
                    json.dump(
                        resource.json(), f,
                        skipkeys=False, ensure_ascii=True, check_circular=True,
                        allow_nan=True, cls=None, indent=None, separators=None,
                        encoding='utf-8', default=None, sort_keys=False
                    )

    # -------------------------------------------------------------------------

    www_mode.set_defaults(func=www_func)

    # =========================================================================

    try:
        args = main_parser.parse_args()
    except Exception, e:
        sys.exit(e)

    args.func(args)
