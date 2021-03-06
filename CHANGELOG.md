### Version 0.9.6 (2016-03-15)

  - feat: option to hide 'acknowledgments'

### Version 0.9.5 (2015-11-02)

  - feat: switch to pyannote.core 0.4.3
  - feat: pip install tvd[notebook] for notebook visualization
  - fix: Python 3 support for tvd.create

### Version 0.9 (2015-10-27)

  - feat: Python 3 support

### Version 0.8.1 (2015-01-23)

  - fix: fix bug in Episode.for_json

### Version 0.8 (2014-10-29)

  - BREAKING CHANGE: switch to pyannote.core 0.2 new JSON format

### Version 0.7.4 (2014-07-29)

  - feat: easy reproduction with docker

### Version 0.6.2 (2014-07-23)

  - fix: require pyannote.core 0.0.5 (with fixed JSON I/O)

### Version 0.6.1 (2014-06-26)

  - fix: change resource directory to 'metadata'

### Version 0.6 (2014-06-26)

  - BREAKING CHANGE: rename section 'www' section to (more generic) 'resources'
  - feat: get_resource can load from disk
  - fix: several bugs in `tvd.create` reproduction script

### Version 0.5 (2014-05-06)

  - chore: get rid of AnnotationGraph in favor of pyannote.core.Transcription

### Version 0.4.5 (2014-04-30)

  - feat(AnnotationGraph): crop() method for visualizing large graphs
  - fix: IPython Notebook SVG display with "&"
  - fix: T (TAnchored, TFloating) comparisons

### Version 0.4.4 (2014-04-23)

  - fix: missing HTML characters mapping
  - fix: IPython Notebook SVG display with non-ASCII characters

### Version 0.4.1 (2014-04-18)

  - fix: download_as_utf8 converts HTML characters
  - feat: IPython Notebook SVG display

### Version 0.4 (2014-04-16)

  - feat(Plugin): give to Caesar what belongs to Caesar
  - feat: keep track versions of TVD and its plugins
  - feat(Plugin): new download_as_utf8 method takes care of UTF-8 encoding
  - feat(AnnotationGraph): floating time relabelling, pre- and post-alignment

### Version 0.3.1 (2014-04-10)

  - fix: tvd.create argument parsing

### Version 0.3 (2014-04-07)

  - feat: temporally-ordered graph traversal
  - feat: timerange estimation
  - improve: TStart and TEnd jsonification

### Version 0.2.1

  - remove requests dependency

### Version 0.2 (2014-03-24)

  - first public release
