# Free Arcade definition. Only supports Flash and Java.
from __main__ import fpclib
from __main__ import re

regex = 'freearcade.com'

SWF = re.compile("SWFObject\('(.*?)'")
APPLET = re.compile("AppletObject\('(.*?)', '(.*?)', '(.*?)', '(.*?)'")

class FreeArcade(fpclib.Curation):
    def parse(self, soup):
        self.title = soup.select_one("h2 > span").text

        # Get logo
        self.logo = "http://assets.freearcade.com/thumbnails/" + self.title.replace(" ", "") + "-sm.gif"
        # Set publisher
        self.pub = "FreeArcade"
        # Get description
        self.desc = soup.select_one(".game > p").text.replace("\t", "") + \
                    "\n\n" + \
                    soup.select_one(".sidebox > p").text.replace("\t", "")

        # Get platform and launch command
        data = soup.select_one("#gamecontent > script").string

        swf = SWF.search(data)
        if swf:
            # Flash game
            self.platform = "Flash"
            self.app = fpclib.FLASH
            self.cmd = swf[1]
        else:
            applet = APPLET.search(data)
            # Java game
            self.platform = "Java"
            self.app = fpclib.JAVA
            self.cmd = fpclib.normalize(self.src)
            # Save applet
            self.applet = str('<applet code="%s" name="%s" width="%s" height="%s"></applet>' % (applet[1], applet[2], applet[3], applet[4]))
            self.code = applet[1]
            
    
    def get_files(self):
        if self.platform == "Java":
            cmd = self.cmd[7:]
            # Create applet html
            fpclib.write(cmd, self.applet)
            # Download applet code
            fpclib.download_all((cmd[:cmd.rfind("/")+1] + self.code,))
        else:
            super().get_files()
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass