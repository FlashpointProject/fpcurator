# EtoysIllinois definition.

import fpclib

regex = 'etoysillinois.org'
ver = 6

class EtoysIllinois(fpclib.Curation):

    def parse(self, soup):
        newSoup = fpclib.get_soup(self.url, verify=False)

        # Title
        self.title = newSoup.find("h1").text.strip('\r\n')

        # Developer and Publisher
        self.dev = str(newSoup.find("div", attrs={"class":"squeakletInfoBox"})).split('<h2 class="inline">Author:</h2>')[1].split('</p>')[0].strip('\r\n').strip()
        self.pub = 'EtoysIllinois'

        # Platform and App
        self.platform = "Squeak"
        self.app = fpclib.SECURE_PLAYER
        self.launchCommand = 'squeak http://etoysillinois.org/' + newSoup.find('p').findAll('a')[1]['href']

        # Description
        self.desc = str(newSoup.find("div", attrs={"class":"squeakletInfoBox"})).split('<h2 class="inline">Description:</h2>')[1].split('</p>')[0].strip('\r\n').strip().replace('\r\n',' ')

        # Notes
        self.cnotes = "Before running the curation, copy its content files into Flashpoint/Legacy/htdocs and set -extract to the Mount Parameters."

    def get_files(self):
        urlMain = self.launchCommand.replace('squeak http','https')
        location = urlMain.split('://')[1].rsplit('/',1)[0]

        fpclib.download(urlMain, loc=location, verify=False)