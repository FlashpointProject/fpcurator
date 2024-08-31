# Y8 definition.

import requests
from bs4 import BeautifulSoup
import fpclib
import re
from html import unescape

regex = 'y8.com'
ver = 6

TITLE = re.compile("(.*?) Game - Play online at Y8.com")

UNITY_EMBED = """<html>
    <head>
        <title>%s</title>
        <style>
            body { background-color: #000000; height: 100%%; margin: 0; }
            embed { width: %spx; height: %spx; }
        </style>
    </head>
    <body>
        <center>
            <div id="embed">
                <embed src="%s" type="application/vnd.unity">
            </div>
        </center>
    </body>
</html>
"""

class Y8(fpclib.Curation):
    def parse(self, soup):
        try:
            self.title = soup.find("h1").text.strip()
        except:
            # Game has no title, find it in title
            self.title = TITLE.search(soup.select_one("title").text.strip())[1]

        try:
            self.logo = soup.find("meta", property="og:image")["content"]
        except: pass

        self.pub = "Y8"

        # Get info and description
        self.desc = soup.select_one("h2.description").text.strip()
        # Get date
        date = soup.select("span.data")[-1].text.strip().split(" ")
        self.date = date[2] + "-" + fpclib.MONTHS[date[1]] + "-" + date[0]

        # Acquire tags; I decided to do the lazy thing instead of testing them individually
        self.tags = [i.text for i in soup.select(".tags-list > a > p")]

        url = fpclib.normalize(self.src)

        # Get launch command
        flash_async_content = soup.find("div", {"data-async-content": True})
        if(flash_async_content):
            soup2 = BeautifulSoup(unescape(flash_async_content.get("data-async-content")), "html.parser")
            flash_embed = soup2.find("embed")
            if flash_embed:
                cmd = flash_embed["src"]
                if "//" in cmd: cmd = fpclib.normalize(cmd)
                elif cmd[0] == "/": cmd = "http://www.y8.com" + cmd
                else: cmd = url + cmd

                end = fpclib.normalize(flash_embed["src"])[-4:]
                if end == ".swf":
                    # Flash game
                    self.platform = "Flash"
                    self.app = fpclib.FLASH
                    self.cmd = cmd
        else:
            embed = soup.find("embed")
            if embed:
                cmd = embed["src"]
                if "//" in cmd: cmd = fpclib.normalize(cmd)
                elif cmd[0] == "/": cmd = "http://www.y8.com" + cmd
                else: cmd = url + cmd
                
                # Shockwave game
                self.platform = "Shockwave"
                self.app = fpclib.SHOCKWAVE
                self.cmd = '"' + cmd + '"'
            else:
                unity_script = soup.find("script", string=lambda t: t and "unityPlayer" in t)
                if(unity_script):
                    # Unity game
                    self.platform = "Unity"
                    self.app = fpclib.UNITY
                    self.cmd = url + "index.html"
                    unity_div = soup.select_one("#unityPlayer")
                    self.unity = fpclib.normalize(re.search(r'https?\:.+?(?=\")', unity_script.text).group(0))
                    self.embed = UNITY_EMBED % (self.title, unity_div['width'], unity_div['height'], self.unity)
                else:
                    # External game (hopefully html5)
                    self.platform = "HTML5"
                    self.app = fpclib.FPNAVIGATOR

                    iframe = soup.select_one("iframe")
                    if not iframe: raise ValueError("Could not find game iframe")

                    if "src" in iframe.attrs:
                        cmd = iframe["src"]
                    else:
                        cmd = iframe["data-src"]

                    if "//" in cmd: cmd = fpclib.normalize(cmd, keep_vars=True)
                    elif cmd[0] == "/": cmd = "http://jayisgames.com" + cmd
                    else: cmd = url + cmd
                    self.cmd = cmd

    def get_files(self):
        if self.platform == "Unity":
            # Unity has an embed file created for it
            f = self.cmd[7:]
            fpclib.write(f, self.embed)
            fpclib.replace(f, "https:", "http:")
            # And the unity file needs to be downloaded
            fpclib.download_all((self.unity,))
        elif self.platform == "Shockwave":
            # Shockwave launch command has quotes around it
            fpclib.download_all((self.cmd[1:-1],))
        else:
            # All other platforms are very simple
            super().get_files()

            if self.platform == "HTML5":
                # If HTML5, replace all instances of https: with http:
                fpclib.replace(self.cmd[7:], "https:", "http:")

    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass

    def soupify(self):
        with requests.get(fpclib.normalize(self.src, True, True, True)) as response:
            return BeautifulSoup(response.content)