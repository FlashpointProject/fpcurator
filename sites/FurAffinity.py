# Fur Affinity definition.

import fpclib
import re
from pathlib import Path

regex = 'furaffinity.net'
ver = 6

class FurAffinity(fpclib.Curation):
    def get_auth_from_file(self, param_name, clients_file="clients.txt"):
        try: client_data = fpclib.read(clients_file)
        except: client_data = fpclib.read(str(Path(__file__).parent.parent / clients_file))
        param_value = dict([line.split("=",1) for line in client_data.splitlines()]).get(param_name)
        if param_value is None or param_value == '': raise ValueError(clients_file + f' is missing data for "{param_name}=".')
        return param_value
    
    def parse(self, soup):
        download_button = soup.find(class_='download')
        if download_button == None:
            cookie = self.get_auth_from_file('FURAFFINITY_COOKIE')
            if cookie == '':
                raise ValueError("NSFW entry; add a valid user cookie in clients.txt's FURAFFINITY_COOKIE variable.")
            soup = fpclib.get_soup(self.url, headers={"COOKIE": cookie})
            download_button = soup.find(class_='download')
            if download_button == None:
                raise ValueError("NSFW entry; add a valid user cookie in clients.txt's FURAFFINITY_COOKIE variable.")

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