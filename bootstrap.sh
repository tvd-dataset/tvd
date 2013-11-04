
cd /vagrant

# DVD CSS
echo "# VideoLAN repository (libdvdcss)" >> /etc/apt/sources.list
echo "deb http://download.videolan.org/pub/debian/stable/ /" >> /etc/apt/sources.list
echo "deb-src http://download.videolan.org/pub/debian/stable/ /" >> /etc/apt/sources.list
wget -O - http://download.videolan.org/pub/debian/videolan-apt.asc|apt-key add -
apt-get -y update
apt-get -y install libdvdcss-dev

# vobcopy
apt-get -y install vobcopy

# lsdvd
apt-get -y install lsdvd

# mplayer / mencoder
apt-get -y install mplayer
apt-get -y install mencoder

# vobsub2srt
apt-get -y install python-software-properties
add-apt-repository ppa:ruediger-c-plusplus/vobsub2srt
apt-get -y update
apt-get -y install vobsub2srt

# download tessdata in several languages
apt-get -y install curl
mkdir tessdata
export TESSVERSION='3.02'
# for LANG in afr ara aze bel ben bul cat ces chi_sim chi_tra chr dan deu ell eng enm epo epo_alt equ est eus fin fra frk frm glg grc heb hin hrv hun ind isl ita jpn kan kor lav lit mal mkd mlt msa nld nor pol por ron rus slk slv spa sqi srp swa swe tam tel tgl tha tur ukr vie
for LANG in fra eng spa
do
    echo "Downloading $LANG Tesseract models from Google..."
    curl -s https://tesseract-ocr.googlecode.com/files/tesseract-ocr-$TESSVERSION.$LANG.tar.gz > /tmp/$LANG.tar.gz;
    tar xzf /tmp/$LANG.tar.gz -C /tmp/;
    rm /tmp/$LANG.tar.gz;
    cp /tmp/tesseract-ocr/tessdata/* tessdata/;
    rm -rf /tmp/tesseract-ocr;
done

# sndfile-resample
apt-get -y install samplerate-programs

# python stuff
apt-get -y install python-pip
apt-get -y install python-dev
apt-get -y install libxml2-dev
apt-get -y install libxslt1-dev
apt-get -y install gfortran
pip install numpy

# tvd scripts
python setup.py develop



# # banyan
# apt-get -y install g++
# pip install banyan
