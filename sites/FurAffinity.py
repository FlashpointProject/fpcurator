# Fur Affinity definition.

import fpclib
import re

regex = 'furaffinity.net'
ver = 6

# This is a global variable that allows you to grab login-locked games. You'll have to replace it to get those games.
TOKEN_HEADERS = {"COOKIE": ""}

class FurAffinity(fpclib.Curation):
    def parse(self, soup):
        download_button = soup.find(class_='download')
        if download_button == None:
            if TOKEN_HEADERS['COOKIE'] == '':
                raise ValueError("NSFW entry; add a valid user cookie in sites/FurAffinity.py's TOKEN_HEADERS variable, then click the 'Reload' button in fpcurator.")
            soup = fpclib.get_soup(self.url, headers=TOKEN_HEADERS)
            download_button = soup.find(class_='download')
            if download_button == None:
                raise ValueError("NSFW entry; add a valid user cookie in sites/FurAffinity.py's TOKEN_HEADERS variable, then click the 'Reload' button in fpcurator.")

        self.cmd = 'http:' + download_button.a['href']
        if not self.cmd.endswith(".swf"): raise ValueError("No game found on webpage.")

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