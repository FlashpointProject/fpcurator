# HentaiFoundry definition.

import fpclib
import re
from pathlib import Path

regex = "hentai-foundry.com"
ver = 6

class HentaiFoundry(fpclib.Curation):
    def parse(self, soup):
        soup = fpclib.get_soup(self.url + "?enterAgree=1")
        download_button = soup.select_one("#picBox .boxbody p a")

        self.cmd = "http:" + download_button["href"]
        if not self.cmd.endswith(".swf"): raise ValueError("No game found on webpage.")

        # Get title
        self.title = soup.select_one("#picBox .boxtitle .imageTitle").text

        # Get dev and publisher
        self.dev = soup.select_one("#picBox .boxtitle a").text
        self.publisher = "Hentai Foundry"

        # Get desc
        self.desc = soup.select_one("#descriptionBox .boxbody .picDescript").text.strip()

        # Get date
        self.date = fpclib.DP_US.parse(soup.select_one("#pictureGeneralInfoBox .boxbody time").text.strip())

        # Get platform
        self.platform = "Flash"
        self.app = fpclib.FLASH
