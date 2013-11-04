Title: How do I reproduce the TVD corpus locally?
Date: 2013-10-31 00:00
Slug: how
Author: Herve Bredin

We provide all the necessary scripts to reproduce the TVD corpus, provided that you own the corresponding TV series DVD sets and a computer with a DVD player. 

### Step 1: TVD scripts

```bash
export TVDIR="/where/to/create/TVD/corpus/"
git clone https://github.com/hbredin/tvd.git $TVDIR 
```

### Step 2: TVD box

To ease the process of reproducing the TVD corpus, we provide a virtual machine (a.k.a the TVD box) with all necessary software pre-installed.

  * Install [VirtualBox](www.virtualbox.org) ([4.3](https://www.virtualbox.org/wiki/Downloads))
  * Install [Vagrant](http://www.vagrantup.com/) ([1.3.5](http://downloads.vagrantup.com/tags/v1.3.5))
  * Create and setup TVD box (this may take a while...)
```bash
cd $TVDIR
vagrant up
```
  * Connect to TVD box
```bash
vagrant ssh
```
  You are now connected to the TVD box. 
  The content of its `/vagrant/` directory is synchronized with `$TVDIR` on your machine.

### Step 3: DVD set

Legally acquire the following DVD sets (depending on which TV series you want to focus your research):
  * The Big Bang Theory (season 1)
  * Game of Thrones (season 1)

Copy each disc in `$TVDDIR` using pre-installed `tvd` Python module.

```bash
export SERIES='TheBigBangTheory'  # or 'GameOfThrones'
export SEASON=1                   # first season
export DISC=2                     # disc number 2
python -m tvd.disc --dvd /dev/dvd --series $SERIES --season $SEASON --disc $DISC /vagrant/
```

The above command will copy disc #2 of *The Big Bang Theory* first season DVD set. This is mostly a wraper around [`vobcopy`](http://www.vobcopy.org/) command line tool.

### Step 4: Multi-lingual audio tracks and subtitles

Once DVDs are copied, you can proceed with the extraction of audio tracks and subtitles for all episodes.

```bash
export SERIES='TheBigBangTheory'  # or GameOfThrones
python -m tvd.dvd --series $SERIES --audio --subtitles /vagrant/
```

The above command will extract audio and subtitle tracks from all previously copied DVDs of *The Big Bang Theory*. Subtitles will stored using the TVD file format.


### Step 5: Internet resources

```bash
export SERIES='TheBigBangTheory'  # or GameOfThrones
python -m tvd.www --series $SERIES /vagrant/
```

The above command will crawl resources from the Internet and store them in TVD file format.

### Step 6: Alignments

```bash
export SERIES='TheBigBangTheory'  # or GameOfThrones
python -m tvd.align --series $SERIES /vagrant/
```

The above command will perform alignment between resources.
