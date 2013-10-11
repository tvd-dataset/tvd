Title: Usage
Date: 2013-10-11 15:00

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
        
