# -*- coding: utf-8 -*-

import re
from pyload.plugin.Crypter import Crypter
from pyload.network.HTTPRequest import BadHeader


class EmbeduploadCom(Crypter):
    __name    = "EmbeduploadCom"
    __type    = "crypter"
    __version = "0.02"

    __pattern = r'http://(?:www\.)?embedupload\.com/\?d=.+'
    __config  = [("use_subfolder"     , "bool", "Save package to subfolder"           , True         ),
                   ("subfolder_per_pack", "bool", "Create a subfolder for each package" , True         ),
                   ("preferedHoster"    , "str" , "Prefered hoster list (bar-separated)", "embedupload"),
                   ("ignoredHoster"     , "str" , "Ignored hoster list (bar-separated)" , ""           )]

    __description = """EmbedUpload.com decrypter plugin"""
    __license     = "GPLv3"
    __authors     = [("zoidberg", "zoidberg@mujmail.cz")]


    LINK_PATTERN = r'<div id="(.+?)".*?>\s*<a href="(.+?)" target="_blank" (?:class="DownloadNow"|style="color:red")>'


    def decrypt(self, pyfile):
        self.html = self.load(pyfile.url, decode=True)
        tmp_links = []

        m = re.findall(self.LINK_PATTERN, self.html)
        if m:
            prefered_set = set(self.getConfig('preferedHoster').split('|'))
            prefered_set = map(lambda s: s.lower().split('.')[0], prefered_set)

            self.logDebug("PF: %s" % prefered_set)

            tmp_links.extend(x[1] for x in m if x[0] in prefered_set)
            self.urls = self.getLocation(tmp_links)

            if not self.urls:
                ignored_set = set(self.getConfig('ignoredHoster').split('|'))
                ignored_set = map(lambda s: s.lower().split('.')[0], ignored_set)

                self.logDebug("IG: %s" % ignored_set)

                tmp_links.extend(x[1] for x in m if x[0] not in ignored_set)
                self.urls = self.getLocation(tmp_links)


    def getLocation(self, tmp_links):
        new_links = []
        for link in tmp_links:
            try:
                header = self.load(link, just_header=True)
                if 'location' in header:
                    new_links.append(header['location'])
            except BadHeader:
                pass
        return new_links
