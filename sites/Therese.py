# http://therese.eveilleau.pagesperso-orange.fr definition.
import fpclib
import re
import requests
import bs4
from zipfile import ZipFile

regex = 'therese.eveilleau.pagesperso-orange.fr'

class Therese(fpclib.Curation):
    def soupify(self):
        with requests.get(fpclib.normalize(self.src, True, True, True)) as response:
            return bs4.BeautifulSoup(response.content)

    def parse(self, soup):
        self.title = soup.select_one("title").text.strip()

        # Set dev and lang
        self.dev = "Thérèse Eveilleau"
        self.lang = 'fr'

        # Find zip link
        # (+1 to include the / in between the links)
        self.zip_loc = fpclib.normalize(self.src[:self.src.rfind("/")+1])
        self.zip_name = soup.find('a', href=re.compile(r'^\w+.zip$'))["href"]

        # Download zip
        fpclib.download(self.zip_loc + self.zip_name)

        # Get swf location
        self.z = ZipFile(self.zip_name)
        self.cmd = self.zip_loc + self.zip_name + "/" + self.z.namelist()[0]

    def get_files(self):
        # Extract all zip content
        self.z.extractall(self.zip_loc.replace("http://", "") + self.zip_name)

        # Close and delete zip file
        self.z.close()
        fpclib.delete("../../" + self.zip_name)
