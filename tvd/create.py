#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
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

"""TVD reproduction script -- tvd.niderb.fr

* /list/ mode returns the list of installed TVD plugins.
* /dump/ mode dumps TV series DVDs onto disk.
* /rip/ mode extracts videos, audio tracks and subtitles from dumped DVDs.
* /stream/ mode reencodes videos for streaming.
* /www/ mode downloads resources from the Internet.

Usage:
    create list
    create dump [options] [--dvd=<mount>] [--vobcopy=<p>] <tvd> <series> <season> <disc>
    create rip [options] [--lsdvd=<p> --HandBrakeCLI=<p> --mencoder=<p> --vobsub2srt=<p> --avconv=<p> --tessdata=<p> --sndfile-resample=<p>] <tvd> <series> <season>
    create stream [options] [--avconv=<p>] <tvd> <series>
    create www [options] <tvd> <series>

Arguments:
    <tvd>     Path to TVD root directory.
    <series>  Series plugin (use "create list" to get the list of series plugins).
    <season>  Season number (e.g. 1 for first season).
    <disc>    Disc number (e.g. 1 for first disc).

Options:
    -f --force                Overwrite existing files.
    --verbose                 Be verbose.

    -d <mount> --dvd=<mount>  DVD mount point.
    --vobcopy=<p>             Path to "vobcopy" (in case it is not in PATH).
    --lsdvd=<p>               Path to "lsdvd" (in case it is not in PATH).
    --HandBrakeCLI=<p>        Path to "HandBrakeCLI" (in case it is not in PATH).
    --mencoder=<p>            Path to "mencoder" (in case it is not in PATH).
    --vobsub2srt=<p>          Path to "vobsub2srt" (in case it is not in PATH).
    --tessdata=<p>            Path to "tessdata" directory prefix.
    --avconv=<p>              Path to "avconv" (in case it is not in PATH).
    --sndfile-resample=<p>    Path to "sndfile-resample" (in case it is not in PATH).
"""

import logging

import re
from path import path

import tvd
from tvd import Episode
from tvd.rip import TVSeriesDVDSet, \
    Vobcopy, HandBrakeCLI, MEncoder, \
    VobSub2SRT, AVConv, SndFileResample

# -------------------------------------------------------------------------

def do_dump(
    series, season, disc,
    dvd=None, vobcopy=None, force=False,
    verbose=False
):

    if verbose:
        logging.basicConfig(level=logging.INFO)

    # tools
    vobcopy = Vobcopy(vobcopy=vobcopy)

    # full directory resulting from vobcopy dump
    full_name = path(series.path_to_dump(season, disc))
    logging.info('Dumping to {full_name}'.format(full_name=full_name))

    # make sure it does not exist already
    if full_name.exists() and not force:
        logging.error('{name} already exists'.format(name=full_name))

    else:
        dump_to, name = full_name.splitpath()
        # create 'dump_to' directory if needed
        path(dump_to).makedirs_p()
        # dump
        vobcopy(dump_to, name=name, dvd=dvd)

    # -------------------------------------------------------------------------

def do_rip(
    series, season,
    lsdvd=None, HandBrakeCLI=None, mencoder=None, vobsub2srt=None,
    tessdata=None, avconv=None, sndfile_resample=None, force=False,
    verbose=False
):

    if verbose:
        logging.basicConfig(level=logging.INFO)

    original_language = series.language

    def _audio_cmp((i1, l1), (i2, l2)):
        if l1 == original_language:
            return -1
        if l2 == original_language:
            return 1
        else:
            return cmp(i1, i2)

    # tools
    handbrake = HandBrakeCLI(handbrake=HandBrakeCLI)
    mencoder = MEncoder(mencoder=mencoder)
    vobsub2srt = VobSub2SRT(vobsub2srt=vobsub2srt, tessdata=tessdata)
    avconv = AVConv(avconv=avconv)
    sndfile_resample = SndFileResample(sndfile_resample=sndfile_resample)

    # gather list of disc available for requested series/season
    dump_to, _ = series.path_to_dump(1, 1)
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
        handbrake_to = series.path_to_video(episode)

        logging.info('mkv: {to}'.format(to=handbrake_to))

        # make sure output file does not exist already
        if path(handbrake_to).exists() and not force:
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

            rip_srt_to = series.path_to_subtitles(episode, language=language)

            logging.info('srt: {to}'.format(to=rip_srt_to))

            # make sure output file does not exist already
            if path(rip_srt_to).exists() and not force:
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

            rip_wav_to = series.path_to_audio(episode, language=language)

            logging.info('wav: {to}'.format(to=rip_wav_to))

            # make sure output file does not exist already
            if path(rip_wav_to).exists() and not force:
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

def do_stream(series, avconv=None, force=False, verbose=False):

    if verbose:
        logging.basicConfig(level=logging.INFO)

    avconv = AVConv(avconv=avconv)

    # find all SERIES.Season**.Episode**.mkv files
    # in TVD/SERIES/dvd/rip/
    # and store all corresponding Episode in episodes list
    episodes = []

    dummy = Episode(series=series.__class__.__name__, season=1, episode=1)
    handbrake_to = series.path_to_video(episode)
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
        handbrake_to = series.path_to_video(episode)

        # extract video in series original language
        # in several format (ogg, mp4, webm) for streaming

        stream = 1  # rip mode made sure first audio stream
                    # is in original language

        # -- ogv --
        ogv_to = series.path_to_stream(episode, format='ogv')
        logging.info('ogv: {to}'.format(to=ogv_to))

        # do not re-generate existing file
        if path(ogv_to).exists() and not force:
            logging.error('{to} already exists.'.format(to=ogv_to))

        else:
            # create containing directory if needed
            path(ogv_to).dirname().makedirs_p()
            avconv.ogv(handbrake_to, stream, ogv_to)

        # -- mp4 --
        mp4_to = series.path_to_stream(episode, format='mp4')

        logging.info('mp4: {to}'.format(to=mp4_to))

        # do not re-generate existing file
        if path(mp4_to).exists() and not force:
            logging.error('{to} already exists.'.format(to=mp4_to))

        else:
            # create containing directory if needed
            path(mp4_to).dirname().makedirs_p()
            avconv.mp4(handbrake_to, stream, mp4_to)

        # -- webm --
        webm_to = series.path_to_stream(episode, format='webm')
        logging.info('webm: {to}'.format(to=webm_to))

        # do not re-generate existing file
        if path(webm_to).exists() and not force:
            logging.error('{to} already exists.'.format(to=webm_to))

        else:
            # create containing directory if needed
            path(webm_to).dirname().makedirs_p()
            avconv.webm(handbrake_to, stream, webm_to)

# -------------------------------------------------------------------------

def do_www(series, force=False, verbose=False):

    if verbose:
        logging.basicConfig(level=logging.INFO)

    # loop on all available resources
    for episode, resource_type in series.iter_resources(
        resource_type=None, episode=None, data=False
    ):

        # save resource to PATTERN_RESOURCE in JSON format
        json_to = series.path_to_resource(episode, resource_type)
        logging.info('{episode}: downloading "{resource}".'.format(
            episode=episode, resource=resource_type))

        # do not re-generate existing file
        if path(json_to).exists() and not force:
            logging.info('{episode}: "{resource}" already exists.'.format(
                episode=episode, resource=resource_type))
            continue

        try:
            resource = series.get_resource(resource_type, episode)
        except Exception, e:
            logging.error('{episode}: failed to download "{resource}".'.format(
                episode=episode, resource=resource_type))
            continue

        # create containing directory if needed
        path(json_to).dirname().makedirs_p()
        resource.save(json_to)



# -------------------------------------------------------------------------

def do_list():
    for s in sorted(tvd.series_plugins):
        print s

# -------------------------------------------------------------------------

if __name__ == '__main__':

    from docopt import docopt
    ARGUMENTS = docopt(__doc__, version=tvd.__version__)

    # /list/ mode
    if ARGUMENTS['list']:
        do_list()

    # /dump/ mode
    elif ARGUMENTS['dump']:
        # initialize series plugin
        series = tvd.series_plugins[ARGUMENTS['<series>']](ARGUMENTS['<tvd>'])
        do_dump(
            series, 
            int(ARGUMENTS['season']), 
            int(ARGUMENTS['disc']),
            dvd=ARGUMENTS['--dvd'], 
            vobcopy=ARGUMENTS['--vobcopy'],
            force=ARGUMENTS['--force'],
            verbose=ARGUMENTS['--verbose']
        )

    elif ARGUMENTS['rip']:
        # initialize series plugin
        series = tvd.series_plugins[ARGUMENTS['<series>']](ARGUMENTS['<tvd>'])
        do_rip(
            series, 
            int(ARGUMENTS['season']), 
            lsdvd=ARGUMENTS['--lsdvd'],
            HandBrakeCLI=ARGUMENTS['--HandBrakeCLI'],
            mencoder=ARGUMENTS['--mencoder'],
            vobsub2srt=ARGUMENTS['--vobsub2srt'],
            tessdata=ARGUMENTS['--tessdata'],
            avconv=ARGUMENTS['--avconv'],
            sndfile_resample=ARGUMENTS['--sndfile-resample'],
            force=ARGUMENTS['--force'],
            verbose=ARGUMENTS['--verbose']
        )

    elif ARGUMENTS['stream']:
        # initialize series plugin
        series = tvd.series_plugins[ARGUMENTS['<series>']](ARGUMENTS['<tvd>'])
        do_stream(
            series, 
            avconv=ARGUMENTS['--avconv'],
            force=ARGUMENTS['--force'],
            verbose=ARGUMENTS['--verbose']
        )

    elif ARGUMENTS['www']:
        # initialize series plugin
        series = tvd.series_plugins[ARGUMENTS['<series>']](ARGUMENTS['<tvd>'])
        do_www(
            series, 
            force=ARGUMENTS['--force'],
            verbose=ARGUMENTS['--verbose']
        )
