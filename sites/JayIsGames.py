# Jay is games definition.
from __main__ import fpclib
from __main__ import re

regex = 'jayisgames.com'

DEV = re.compile("(developed|created) by (\w+)", re.I)

class JayIsGames(fpclib.Curation):
    def parse(self, soup):
        self.title = soup.select_one("h1.asset-name").text
        #self.logo = soup.find("meta", property="og:image")["content"] - Just grabs the Jay is games logo, not the game logo
        self.pub = "Jay is games"
        
        self.desc = soup.select_one(".entrybody > p").text
        dev = DEV.search(self.desc)
        if dev: self.dev = dev[2]

        url = fpclib.normalize(self.src)

        # Get launch command
        embed = soup.find("embed")
        if embed:
            cmd = embed["src"]
            if "//" in cmd: cmd = fpclib.normalize(cmd)
            elif cmd[0] == "/": cmd = "http://jayisgames.com" + cmd
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

            iframe = soup.select_one("#game-wrapper > iframe")
            if not iframe: raise ValueError("Could not find game iframe")

            cmd = iframe["src"]
            if "//" in cmd: cmd = fpclib.normalize(cmd)
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