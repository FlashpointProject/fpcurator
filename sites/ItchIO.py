# itch.io site definition (This is just the Unknown site definition but with a few extra kinks)

import fpclib
import re, json

regex = "itch.io"
# Only handles at most two sublevels.
PLATFORM = re.compile('new I\.View(\w+)Game\(')
VIEW_DATA = re.compile('{"url":(.*?{(.*?{.*?}|[^{}]*)*}|[^{}]*)*}')

UNITY_EMBED = """<html>
    <head>
        <title>Title Goes Here</title>
        <style>
            body { background-color: #000000; height: 100%%; margin: 0; }
            #embed { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }
        </style>
    </head>
    <body>
        <div style="%s" id="embed">
            <embed src="%s" bgColor=#000000  width=100%% height=100%% type="application/vnd.unity" disableexternalcall="true" disablecontextmenu="true" disablefullscreen="false" firstframecallback="unityObject.firstFrameCallback();">
        </div>
    </body>
</html>"""

class ItchIO(fpclib.Curation):
    def parse(self, soup):
        # Get title
        self.title = soup.find("h1").text
        try:
            self.logo = soup.select_one(".header.has_image > img")["src"]
        except:
            try:
                self.logo = soup.find("meta", property="og:image")["content"]
            except: pass
        # Get developer
        self.dev = soup.select_one(".on_follow > span").text[7:]
        # Set publisher
        self.pub = "itch.io"

        url = fpclib.normalize(self.src)
        if url[-1] == "/": url = url[:-1]

        # Get launch command and stuff
        script = soup.select_one(".inner_column > script").string
        
        if script:
            platform = PLATFORM.search(script)[1]
            data = json.loads(VIEW_DATA.search(script)[0])

            self.file = data["url"]
            self.platform = platform
            if platform == "Flash":
                self.app = fpclib.FLASH
                self.cmd = fpclib.normalize(data["url"])
                self.embed = ""
            elif platform == "Html":
                self.platform = "HTML5"
                self.app = fpclib.BASILISK
                self.cmd
            elif platform == "Unity":
                self.app = fpclib.UNITY
                self.cmd = url
                self.embed = UNITY_EMBED % (soup.select_one("#unity_drop")["style"], data["url"])
            elif platform == "Java":
                self.app = fpclib.JAVA
                self.cmd = url
                self.embed = str(soup.find("applet"))
            else:
                raise ValueError("Unknown game type found on webpage")
        else:
            raise ValueError("No game found on webpage")
    
    def get_files(self):
        # If there is a file to download, download it
        if self.file:
            fpclib.download_all((self.file,))
        # If there is an embed to create, create it
        if self.embed:
            f = self.cmd[7:]
            fpclib.write(f, self.embed)
            fpclib.replace(f, "https:", "http:")