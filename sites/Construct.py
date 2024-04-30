# Construct definition.

import fpclib
import re

regex = 'construct.net'
ver = 6

class Construct(fpclib.Curation):
    def parse(self, soup):
        # Title
        self.title = soup.find("h1").text.strip('\r\n')

        # Developer and Publisher
        self.dev = soup.select_one(".username").text.strip('\r\n')
        self.pub = 'Construct'

        # Platform and App
        self.platform = "HTML5"
        self.app = ':browser-mode:'

        # Tag
        self.tags = ["Construct"]

        # Description
        self.desc = re.sub(r'\n{3,}', '\n\n', soup.select_one(".deInWrap").text.strip('\r\n'))

        # Release date
        self.date = fpclib.DP_UK.parse(soup.select_one(".pubDate").text.replace("Published on ", ""))

        # File
        gameframeurl = soup.select_one("#GameFrame")['data-game-url']
        self.cmd = re.sub(r'(\?.+?)?$', '', gameframeurl.replace('https:', 'http:'));
        self.cmd2 = re.sub(r'^https?:.+?(\/\d+?\/\d+?\/)embed.html.+?$', r'http://construct-arcade.com\g<1>index.html', gameframeurl)

        # Misc
        self.status = "Hacked"
        self.notes = "Changed arcadeembed.js and playgame.js to remove ads and page redirects."

    def get_files(self):
        fpclib.download_all((self.cmd,self.cmd2))
        fpclib.replace(self.cmd[7:], 'https:', 'http:')
        fpclib.replace(self.cmd2[7:], 'https:', 'http:')

        arcadeembedjs = re.search(r'http.+\/(v\d+)\/.+arcadeembed\.js', fpclib.read(self.cmd[7:])).group(0)
        playgamejs = re.search(r'http.+\/(v\d+)\/.+playgame\.js', fpclib.read(self.cmd2[7:])).group(0)
        fpclib.download_all((playgamejs, arcadeembedjs))

        fpclib.replace(playgamejs[7:], '!inFrame', 'false')
        fpclib.replace(arcadeembedjs[7:], '!inFrame', 'false')

        # Not needed
        fpclib.replace(self.cmd[7:], 'http://www.google-analytics.com/analytics.js', '')
        fpclib.replace(arcadeembedjs[7:], '!loggedIn && !fromOfficialSite', 'false')
