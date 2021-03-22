# Y8 definition.
from __main__ import fpclib
from __main__ import re

regex = 'y8.com'

TITLE = re.compile("(.*?) Game - Play online at Y8.com")

class Y8(fpclib.Curation):
    def parse(self, soup):
        try:
            self.title = soup.find("h1").text.strip()
        except:
            # Game has no title, find it in title
            self.title = TITLE.search(soup.select_one("title").text.strip())[1]
        self.logo = soup.find("meta", property="og:image")["content"]
        self.pub = "Y8"
        
        # Get info and description
        info = soup.select(".game-description > div > div > div")
        self.desc = info[0].text.strip()
        # Get date
        date = info[1].select_one(".data").text.strip().split(" ")
        self.date = date[2] + "-" + fpclib.MONTHS[date[1]] + "-" + date[0]
        
        # Acquire tags; I decided to do the lazy thing instead of testing them individually
        self.tags = [i.text for i in soup.select(".tags-list > a > p")]

        url = fpclib.normalize(self.src)

        # Get launch command
        embed = soup.find("embed")
        if embed:
            cmd = embed["src"]
            if "//" in cmd: cmd = fpclib.normalize(cmd)
            elif cmd[0] == "/": cmd = "http://www.y8.com" + cmd
            else: cmd = url + cmd

            end = fpclib.normalize(embed["src"])[-4:]
            if end == ".swf":
                # Flash game
                self.platform = "Flash"
                self.app = fpclib.FLASH
                self.cmd = cmd
            elif end in {".dir", ".dcr", ".dxr"}:
                # Shockwave game
                self.platform = "Shockwave"
                self.app = fpclib.SHOCKWAVE
                self.cmd = '"' + cmd + '"'
            elif end == "ty3d":
                # Unity game
                self.platform = "Unity"
                self.app = fpclib.UNITY
                self.cmd = url + "index.html"
                self.embed = embed.parent.prettify()
                self.unity = cmd
            else:
                raise ValueError("Unknown game type")
        else:
            # External game (hopefully html5)
            self.platform = "HTML5"
            self.app = fpclib.BASILISK

            iframe = soup.select_one("#html5-content")
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