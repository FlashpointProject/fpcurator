# Game-Game definition.

import fpclib
import re

regex = 'game-?game.com'

SWF = re.compile(r'<object\s+data="(.*?)"')

class GameGame(fpclib.Curation):
    def parse(self, soup):
        # Get Title
        self.title = soup.select_one(".teaser h2.header").text.strip()
        
        # Get Description
        try: self.desc = soup.select_one(".teaser text").text.strip()
        except: pass
        
        # Get Logo
        try: self.logo = soup.select_one(".teaser img")["src"]
        except: pass
        
        # Platform specific
        e = soup.select_one("#gamecontainer > noindex")
        if e:
            self.platform = "HTML5"
            self.app = fpclib.BASILISK
            self.cmd = fpclib.normalize(e.iframe["src"])
        else:
            self.platform = "Flash"
            self.app = fpclib.FLASH
            self.cmd = fpclib.normalize(SWF.search(soup.select_one("section > script").string)[1])