# Addicting Games definition.

import fpclib
import re

regex = 'addictinggames.com'
ver = 6

TAGS = {
    "Shooting": "Action; Shooter",
    "Action": "Action",
    "Puzzle": "Puzzle",
    "Sports": "Sports",
    "Strategy": "Strategy",
    "Downloads": "",
    "Funny": "Joke",
    "Girl Games": "",
    "Car": "Simulation; Driving",
    "Zombie": "Zombie",
    "MMO": "Adventure; MMO",
    "IO Games": "",
    "Card": "Simulation; Card",
    "Clicker": "Arcade; Clicker"
}

HTML_EMBED = """<body>
    <iframe width="100%%" height="100%%" src="%s"></iframe>
</body>
"""

DATA_PARSER = re.compile(r"type: '(.*?)',\s*source: '(.*?)'")
MARKUP_MOVIE = re.compile(r'<param *name="movie" *value="(.*?)"')

class AddictingGames(fpclib.Curation):
    def parse(self, soup):
        self.title = soup.find("h1").text

        # Get Logo
        try: self.logo = fpclib.normalize(soup.find("meta", property="og:image")["content"], keep_prot=True)
        except: pass

        # Get Developer and set Publisher
        try: self.dev = soup.select_one(".author-span > strong").text
        except: pass
        self.pub = "Addicting Games"

        # Get Release Date
        date = soup.select_one(".release-span > strong").text
        self.date = date[-4:] + "-" + fpclib.MONTHS[date[3:6]] + "-" + date[:2]

        # Get Tags
        try: self.tags = TAGS[soup.select(".breadcrumb > a")[1].text]
        except: pass

        # Get Description
        desc = "\n\n".join(i.text for i in soup.select(".instru-blk > h5, .instru-blk > p")).strip()
        if desc.endswith("Game Reviews"):
            desc = desc[:-12].strip()
        self.desc

        # Get Launch Command
        data = DATA_PARSER.search(soup.select(".node-game > script")[1].string)

        url = data[2]
        if url[0] == "/" and url[1] != "/":
            url = "http://www.addictinggames.com" + url

        if data[1] == "flash_file":
            # This is a Flash game
            self.platform = "Flash"
            self.app = fpclib.FLASH
            self.cmd = fpclib.normalize(url)
        elif data[1] == "html5_game_url":
            # This is an HTML5 game
            self.platform = "HTML5"
            self.app = fpclib.FPNAVIGATOR
            self.if_url = fpclib.normalize(url, keep_vars=True)
            self.if_file = fpclib.normalize(url)
            self.cmd = fpclib.normalize(self.src)
        elif data[1] == "markup":
            # Markup games are special
            movie = MARKUP_MOVIE.search(data[2])
            if movie:
                # This is a Flash game
                self.platform = "Flash"
                self.app = fpclib.FLASH
                self.cmd = fpclib.normalize(movie[1])
            else:
                # There might be some html games here, but I'm not sure
                raise ValueError("Can't find swf in markup source")
        else:
            # Unknown type
            raise ValueError("Unknown type '" + data[1] + "'")

    def soupify(self):
        # html5lib is required to parse description correctly.
        return fpclib.get_soup(self.src, "html5lib") or fpclib.get_soup(self.src)

    def get_files(self):
        if self.platform == "HTML5":
            # Download iframe file
            fpclib.download_all((self.if_url,))
            # Replace all references to https with http
            fpclib.replace(self.if_file[7:], "https:", "http:")
            # Create html file for game
            f = self.cmd[7:]
            if f[-1] == "/": f += "index.html"
            fpclib.write(f, HTML_EMBED % self.if_file)
        else:
            # Flash games are downloaded normally
            super().get_files()

    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass