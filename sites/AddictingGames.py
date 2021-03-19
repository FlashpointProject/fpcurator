# Kongregate definition.
# 
from __main__ import fpclib
from __main__ import re

regex = 'addictinggames.com'

MONTHS = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07", 
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"
}

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

DATA_PARSER = re.compile("type: '(.*?)',\s*source: '(.*?)'")
MARKUP_MOVIE = re.compile('<param *name="movie" *value="(.*?)"')

class AddictingGames(fpclib.Curation):
    def parse(self, soup):
        self.title = soup.find("h1").text

        # Get Developer and set Publisher
        try: self.dev = soup.select_one(".author-span > strong").text
        except: pass
        self.pub = "Addicting Games"

        # Get Release Date
        date = soup.select_one(".release-span > strong").text
        self.date = date[-4:] + "-" + MONTHS[date[3:6]] + "-" + date[:2]

        # Get Tags
        try: self.tags = TAGS[soup.select(".breadcrumb > a")[1].text]
        except: pass

        # Get Description
        self.desc = "\n\n".join(i.text for i in soup.select(".instru-blk > h5, .instru-blk > p")).strip()

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
            self.app = fpclib.BASILISK
            self.if_url = url
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
        return fpclib.get_soup(self.src, "html5lib")

    def get_files(self):
        if self.platform == "HTML5":
            # Create html file for game
            fpclib.write(self.cmd[7:], fpclib.read_url(self.if_url))
            # Replace all references to https with http
            fpclib.replace(self.cmd[7:], "https:", "http:")
        else:
            # Flash games are downloaded normally
            super().get_files()
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass