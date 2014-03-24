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

# BUILD-USING: VERSION=`python -m tvd.version`; docker build -t tvd:$VERSION .
# RUN-USING:   docker run -v /path/to/tvd/:/tvd tvd:$VERSION python -m tvd.create --help

FROM ubuntu:12.04
MAINTAINER Herve Bredin (http://herve.niderb.fr)

RUN apt-get update
RUN apt-get -y install wget python-software-properties curl

# install libdvdcss-dev
RUN echo "# VideoLAN repository (libdvdcss)" >> /etc/apt/sources.list
RUN echo "deb http://download.videolan.org/pub/debian/stable/ /" >> /etc/apt/sources.list
RUN echo "deb-src http://download.videolan.org/pub/debian/stable/ /" >> /etc/apt/sources.list
RUN wget -O - http://download.videolan.org/pub/debian/videolan-apt.asc|apt-key add -
RUN apt-get -y update
RUN apt-get -y install libdvdcss-dev

# install vobcopy and lsdvd
# vobcopy is used to copy DVD on disk
# lsdvd is used to list DVD content
RUN apt-get -y install vobcopy lsdvd

# install handbrake-cli
# handbrake is used to extract titles from DVDs
RUN add-apt-repository -y ppa:stebbins/handbrake-releases
RUN apt-get -y update
RUN apt-get -y install handbrake-cli

# install avconv and sndfile-resample
RUN apt-get -y install libav-tools libavcodec-extra-53 samplerate-programs

# install vobsub2srt and mencoder
# mencoder is used to extract vobsub from DVD
# vobsub2srt is used to perform OCR on vobsub to get srt files
RUN add-apt-repository -y ppa:ruediger-c-plusplus/vobsub2srt
RUN apt-get -y update
RUN apt-get -y install vobsub2srt mencoder

# download tesseract data in several language
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.eng.tar.gz /tmp/eng.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.fra.tar.gz /tmp/fra.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.spa.tar.gz /tmp/spa.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.deu.tar.gz /tmp/deu.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.afr.tar.gz /tmp/afr.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ara.tar.gz /tmp/ara.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.aze.tar.gz /tmp/aze.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.bel.tar.gz /tmp/bel.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ben.tar.gz /tmp/ben.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.bul.tar.gz /tmp/bul.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.cat.tar.gz /tmp/cat.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ces.tar.gz /tmp/ces.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.chi_sim.tar.gz /tmp/chi_sim.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.chi_tra.tar.gz /tmp/chi_tra.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.chr.tar.gz /tmp/chr.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.dan.tar.gz /tmp/dan.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ell.tar.gz /tmp/ell.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.enm.tar.gz /tmp/enm.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.epo.tar.gz /tmp/epo.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.epo_alt.tar.gz /tmp/epo_alt.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.equ.tar.gz /tmp/equ.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.est.tar.gz /tmp/est.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.eus.tar.gz /tmp/eus.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.fin.tar.gz /tmp/fin.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.frk.tar.gz /tmp/frk.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.frm.tar.gz /tmp/frm.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.glg.tar.gz /tmp/glg.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.grc.tar.gz /tmp/grc.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.heb.tar.gz /tmp/heb.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.hin.tar.gz /tmp/hin.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.hrv.tar.gz /tmp/hrv.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.hun.tar.gz /tmp/hun.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ind.tar.gz /tmp/ind.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.isl.tar.gz /tmp/isl.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ita.tar.gz /tmp/ita.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.jpn.tar.gz /tmp/jpn.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.kan.tar.gz /tmp/kan.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.kor.tar.gz /tmp/kor.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.lav.tar.gz /tmp/lav.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.lit.tar.gz /tmp/lit.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.mal.tar.gz /tmp/mal.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.mkd.tar.gz /tmp/mkd.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.mlt.tar.gz /tmp/mlt.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.msa.tar.gz /tmp/msa.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.nld.tar.gz /tmp/nld.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.nor.tar.gz /tmp/nor.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.pol.tar.gz /tmp/pol.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.por.tar.gz /tmp/por.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ron.tar.gz /tmp/ron.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.rus.tar.gz /tmp/rus.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.slk.tar.gz /tmp/slk.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.slv.tar.gz /tmp/slv.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.sqi.tar.gz /tmp/sqi.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.srp.tar.gz /tmp/srp.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.swa.tar.gz /tmp/swa.tar.gz
ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.swe.tar.gz /tmp/swe.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.tam.tar.gz /tmp/tam.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.tel.tar.gz /tmp/tel.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.tgl.tar.gz /tmp/tgl.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.tha.tar.gz /tmp/tha.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.tur.tar.gz /tmp/tur.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.ukr.tar.gz /tmp/ukr.tar.gz
# ADD https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.vie.tar.gz /tmp/vie.tar.gz

# extract them all and put them in /tessdata directory
RUN mkdir /tessdata
RUN for archive in /tmp/*.tar.gz; do tar -xzf $archive -C /tmp/; done
RUN mv /tmp/tesseract-ocr/tessdata/* /tessdata/
RUN rm -r /tmp/*.tar.gz /tmp/tesseract-ocr

# install tvd
RUN apt-get -y install python-pip python-dev libxml2-dev libxslt1-dev gfortran
RUN pip install --upgrade pip
RUN pip install tvd

# install tvd plugins
RUN pip install TVDGameOfThrones
RUN pip install TVDTheBigBangTheory

VOLUME ["/tvd", ]
