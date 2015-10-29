FROM tvddataset/base:python3
MAINTAINER Hervé Bredin <bredin@limsi.fr>

RUN pip3 install TVDDummy

ADD . /src
RUN pip3 install -e /src

VOLUME ["/src", "/tvd"]
