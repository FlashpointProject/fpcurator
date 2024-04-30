# Fur Affinity definition.

import fpclib
import re

regex = 'furaffinity.net'
ver = 6

class FurAffinity(fpclib.Curation):
    def parse(self, soup):
        # Get launch command
        self.cmd = 'http:' + soup.find(class_='download').a['href']
        if not self.cmd.endswith(".swf"): raise ValueError("No game found on webpage. Is it a NSFW entry?")

        # Get title
        self.title = soup.select_one(".submission-title").text

        # Get dev and publisher
        self.dev = soup.select_one(".submission-id-sub-container").find("strong").text
        self.publisher = 'Fur Affinity'

        # Get desc
        self.desc = soup.select_one(".submission-description").text.strip()

        # Get date
        self.date = fpclib.DP_US.parse(soup.select_one(".submission-id-sub-container").find(class_='popup_date')['title'])

        # Get platform
        self.platform = 'Flash'
        self.app = fpclib.FLASH

        # Get logo
        self.logo = soup.find('meta', {'property': 'og:image'})['content']