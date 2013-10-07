tvd
===

`tvd` stands for `TV Series DVD`.

`tvd` is mostly a Python wrapper around various command line tools and provides an easy way to extract TV series episodes from DVDs, along with multi-lingual audio tracks and subtitles.


Requirements
------------

`tvd` was successfully tested with the following tools:

  * [lsdvd](http://sourceforge.net/projects/lsdvd/)
  * [MPlayer](http://www.mplayerhq.hu/) 
    * `MPlayer 1.1-4.2.1 (C) 2000-2012 MPlayer Team`
  * [MEncoder](http://www.mplayerhq.hu/) 
    * `MEncoder 1.1-4.2.1 (C) 2000-2012 MPlayer Team`
  * [sndfile_resample](http://www.mega-nerd.com/SRC/)
    * `libsamplerate-0.1.8 (c) 2002-2008 Erik de Castro Lopo`
    * [`libsndfile-1.0.25`](http://www.mega-nerd.com/libsndfile/)
  * [vobsub2srt](https://github.com/ruediger/VobSub2SRT)
    * [`tesseract 3.02.02`](https://code.google.com/p/tesseract-ocr)
    * [`leptonica-1.69`](http://www.leptonica.com/)
  * [tessdata](https://code.google.com/p/tesseract-ocr/downloads/list)

Usage
-----


        # initialize DVD
        $ from tvd.tvseries import TVSeriesDVD
        $ series = "TheBigBangTheory"
        $ season = 2 # indicate the season number as I could not
                     # find a way to detect this automatically
        $ first = 1  # indicate the number of the first episode
                     # (for the same reason)
        $ dvd = TVSeriesDVD(series, season, first)
        
        # initialize DVD ripper
        $ from tvd.rip import DVDRip
        $ rip = DVDRip()

        # rip and dump everything in provided directory
        $ dvd.dump(rip, '/where/to/dump/dir/')

        # this should result in the creation of one video file
        # per episode, one audio track per language per episode
        # and subtitle file per language per episode
        # TheBigBangTheory.Season02.Episode{01|02|...}.vob
        # TheBigBangTheory.Season02.Episode{01|02|...}.{en|fr|es|...}.wav
        # TheBigBangTheory.Season02.Episode{01|02|...}.{en|fr|es|...}.srt
        
