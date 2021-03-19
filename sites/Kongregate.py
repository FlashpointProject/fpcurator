# Kongregate definition.
from __main__ import fpclib
from __main__ import bs4, re, urllib, uuid

regex = 'kongregate.com'

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

IF_URL = re.compile('[\'"]iframe_url[\'"]:[\'"](.*?)[\'"]')
SWF_URL = re.compile('[\'"]swfurl[\'"]:[\'"](.*?)[\'"]')
GAME_SWF = re.compile('[\'"]game_swf[\'"]:[\'"](.*?)[\'"]')
UUID = re.compile('[0-9a-fA-F]{32}')
SIZE = re.compile('[\'"]game_width[\'"]:(\d+),[\'"]game_height[\'"]:(\d+)')

HTML_EMBED = """<html>
    <head>
        <title>%s</title>
        <style>
            body { background-color: #000000; height: 100%%; margin: 0; }
            /* Change "embed" to "object" or other if necessary */
            iframe { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }
        </style>
    </head>
    <body>
        <iframe width="%s" height="%s" src="%s"></iframe>
    </body>
</html>
"""

class Kongregate(fpclib.Curation):
    def parse(self, soup):
        k_uuid = str(uuid.uuid4())
        self.title = soup.find("h1", itemprop="name").text

        # Get Logo
        try: self.logo = fpclib.normalize(soup.find("meta", property="og:image")["content"], keep_prot=True)
        except: pass

        # Get Developer and set Publisher
        self.dev = [dev.text.strip() for dev in soup.select(".game_dev_list > li")]
        self.pub = "Kongregate"
        
        # Get Release Date
        date = soup.select_one(".game_pub_plays > p > .highcontrast").text
        self.date = date[-4:] + "-" + MONTHS[date[:3]] + "-" + date[5:7]

        # Get description (combination of instructions and description)
        # idata is inside a script tag and hasn't been inserted yet.
        idata = bs4.BeautifulSoup(soup.select_one("#game_tab_pane_template").string, "html.parser")

        desc = ""
        try:
            desc += "Instructions\n\n" + idata.select_one("#game_instructions > div > .full_text").text[:-9].replace("\t", "")
        except: pass
        try:
            n = idata.select_one("#game_description > div > .full_text").text.replace("\t", "")[:-9]
            if desc: desc + "\n\n"
            desc += "Description\n\n" + n
        except: pass

        self.desc = desc

        # Kongregate makes it slightly difficult to find the launch command, but we'll get there
        # First, find the script next to the would be game frame:
        if_script = soup.select_one("#gameiframe + script").string
        # Next, get the location of the html containing the game frame (using a uuid might help to avoid potential blocks)
        if_url = IF_URL.search(if_script)[1] + k_uuid + "?kongregate_host=www.kongregate.com"
        # Then soupify that new url and find the relavant script data
        scripts = fpclib.get_soup(if_url).select("body > script")

        if len(scripts) > 3:
            # Effectively confirmed, this is a flash game
            self.platform = "Flash"
            self.app = fpclib.FLASH
            gdata = scripts[3].string
            # If game_swf is present, that takes priority
            cmd = GAME_SWF.search(gdata)
            if cmd: cmd = fpclib.normalize(urllib.parse.unquote(cmd[1]))
            else:
                # Otherwise check that there isn't a uuid in the swfurl (if there is, throw an error)
                cmd = fpclib.normalize(SWF_URL.search(gdata)[1])
                if UUID.search(cmd): raise ValueError("swfurl is not a valid game swf")
            self.cmd = cmd
        else:
            # It's not a flash game, so we will embed the html ourselves later
            self.platform = "HTML5"
            self.app = fpclib.BASILISK
            self.cmd = fpclib.normalize(self.src)
            self.if_url = fpclib.normalize(if_url, keep_vars=True)
            self.size = SIZE.search(if_script)
    
    def get_files(self):
        if self.platform == "HTML5":
            # Download iframe that ought to be embedded
            fpclib.download_all((self.if_url,))
            # Replace all references to https with http
            fpclib.replace(self.if_url[7:], "https:", "http:")
            # Create file to embed swf
            fpclib.write(self.cmd[7:], HTML_EMBED % (self.title, self.size[1], self.size[2], fpclib.normalize(self.if_url, keep_vars=True)))
        else:
            # Flash games are downloaded normally
            super().get_files()
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass