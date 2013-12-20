#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013 Camille GUINAUDEAU
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

from tvd.www.www import WebResources
import re
import urllib3
from tvd.common.graph import T
import networkx as nx


class GameOfThrones(WebResources):

    def __init__(self):
        super(GameOfThrones, self).__init__(series=self.__class__.__name__)

    def outline(self, url, source=None, episode=None):
        """
        Parameters
        ----------
        url : str
            URL where resource is available
        source : str, optional
            Textual description of the source of the resource
        episode : Episode, optional
            Episode for which resource should be downloaded
            Useful in case a same URL contains resources for multiple episodes.

        Returns
        -------
        g : AnnotationGraph
        """

        http = urllib3.PoolManager()
        r = http.request('GET', url)

        start_scene = 0
        nb_scene = 0
        word = r.data.split()

        g = nx.MultiDiGraph(uri=str(episode), source=source)

        sp = ""

        for w in word:
            if start_scene == 1:
                sp = sp + " " + str(w)
            if (re.match("<h2><span", w) or re.match("NewPP", w)) and (nb_scene > 0):
                t1 = T()
                t2 = T()
                usp = sp.decode("utf-8")
                sp = usp.encode("ascii", "ignore")
                sp = re.sub(re.compile('<i>', re.I), "", sp)
                sp = re.sub(re.compile('</i>', re.I), "", sp)
                sp = re.sub(re.compile('<a href=\"/wiki/\S{1,15}(_\(*\S{1,15}\)*)*" title=\"\S{1,15}(\s\(*\S{1,15}\)*)*\">',re.I), "", sp)
                sp = re.sub(re.compile('<a href=\"/wiki/\S{1,15}(_\(*\S{1,15}\)*)*" title=\"\S{1,15}(\s\(*\S{1,15}\)*)*\" class=\"mw-redirect\">',re.I), "", sp)
                sp = re.sub(re.compile('<figure class=\"(.*)</figure>',re.I), "", sp)
                sp = re.sub(re.compile('</a>',re.I), "", sp)
                sp = re.sub(re.compile('<!-- NewPP',re.I), "", sp)
                sp = re.sub(re.compile('<p>',re.I), "", sp)
                sp = re.sub(re.compile('</p>',re.I), "", sp)
                sp = re.sub(re.compile('<h2><span',re.I), "", sp)
                g.add_edge(t1, t2, scene="Scene_"+str(nb_scene), speech=sp)
                sp = ""
                start_scene = 0
            if nb_scene > 0 and start_scene == 0 and re.match("<p>", w):
                sp = sp + " " + str(w)
                start_scene = 1
            if re.match("id=\"Scene_(.*)\">Scene", w):
                nb_scene = nb_scene + 1

        return g

    def manual_transcript(self, url, source=None, episode=None):

        http = urllib3.PoolManager()
        r = http.request('GET', url)

        start_scene = 0
        nb_scene = 0
        word = r.data.split()

        g = nx.MultiDiGraph(uri=str(episode), source=source)

        sp = ""

        for w in word:
            if start_scene == 1 and re.match("</div>", w):
                start_scene = 0
            if start_scene == 1:
                nom = (re.search('/>[A-Z][a-z]{1,15} :', w) or (re.search('/>[A-Z]{1,15}:', w)))
                if nom:
                    w = "<START>" + nom.group(0) + ":"
                else:
                    nom = (re.search('/>[A-Z][a-z]{1,15}', w) or (re.search('/>[A-Z]{1,15}', w)))
                    if nom:
                        w = "<START>" + nom.group(0)
                sp = sp + " " + str(w)
            if re.match("class=\"postbody\">", w):
                start_scene = 1

        sp = re.sub(re.compile('<br />', re.I), "", sp)
        sp = re.sub(re.compile('<br <START>/>', re.I), "####", sp)
        sp = re.sub(re.compile('::', re.I), ":", sp)
        sp = re.sub(re.compile('&quot;', re.I), "", sp)
        sp = re.sub(re.compile('\[([a-zA-Z\'\’,\-]{1,50})(\s[0-9a-zA-Z\’\'’“”\(\),;:\.\?!\-\–#{4}]{1,50})*\.*\]', re.UNICODE), "", sp)
        sp = re.sub(re.compile('\[Blackout \/ Opening credits\]', re.UNICODE), "", sp)
        sp = re.sub(re.compile('\/ BLACKOUT', re.UNICODE), "", sp)

        word = re.split('####', sp)
        ok = 0
        for w in word:
            t1 = T()
            t2 = T()
            if ok == 1:
                if re.match("(.*)</div>(.*)", w):
                    w = re.sub(re.compile('</div>(.*)</table>', re.UNICODE), "", w)

                if re.match("(.*): (.*)", w):
                    ligne = re.split(': ', w)
                elif re.match("[A-Z][a-z]{1,15}(.*) : (.*)", w):
                    ligne = re.split(' : ', w)
                elif re.match("[A-Z]{1,15}\s\(\w{1,15}(\s\w{1,15})*\.*\)(.*)", w):
                    ligne = re.split('\) ', w)
                    ligne[0] = ligne[0] + ")"
                elif re.match("[A-Z]{1,15}\s(.*)", w):
                    ligne = re.split(' ', w)

                uligne0 = ligne[0].decode("utf-8")
                ligne0 = uligne0.encode("ascii", "ignore")
                uligne1 = ligne[1].decode("utf-8")
                ligne1 = uligne1.encode("ascii", "ignore")
                g.add_edge(t1, t2, spk=ligne0, speech=ligne1)
            if ok == 0 and (re.match("[a-zA-Z]{1,15}(\s[a-zA-Z]{1,15}){1,2} : (.*)", w) or re.match("[A-Z]{1,15}(\s[A-Z]{1,15})?: (.*)", w)):
                ok = 1
                if re.match("[A-Z]{1,15}: (.*)", w):
                    ligne = re.split(': ', w)
                elif re.match("[A-Z][a-z]{1,15}(.*) : (.*)", w):
                    ligne = re.split(' : ', w)
                elif re.match("[A-Z]{1,15}\s\((to|in\s)+(\s+[a-zA-Z]{1,15}){1,5}\)(.*)", w):
                    ligne = re.split('\) ', w)
                    ligne[0] = ligne[0] + ")"
                elif re.match("[A-Z]{1,15}\s(.*)", w):
                    ligne = re.split(' ', w)
                else:
                    print w

                uligne0 = ligne[0].decode("utf-8")
                ligne0 = uligne0.encode("ascii", "ignore")
                uligne1 = ligne[1].decode("utf-8")
                ligne1 = uligne1.encode("ascii", "ignore")
                g.add_edge(t1, t2, spk=ligne0, speech=ligne1)

        return g
