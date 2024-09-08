# Kongregate definition.

import fpclib
import bs4, re, urllib, uuid

regex = 'kongregate.com'
ver = 6

IF_URL = re.compile(r'[\'"]iframe_url[\'"]:[\'"](.*?)[\'"]')
SWF_URL = re.compile(r'swf_location\s?=\s?[\'\"]\/?\/?(.+?)(\?.+?)?[\'\"]')
GAME_SWF = re.compile(r'[\'"]game_swf[\'"]:[\'"](.*?)[\'"]')
EMBED_UNITY = re.compile(r'kongregateUnityDiv\\\",\s\\\"\/\/(.*?)\\",\s(\d*?),\s(\d*?),')
UUID = re.compile(r'[0-9a-fA-F]{32}')
SIZE = re.compile(r'[\'"]game_width[\'"]:(\d+),[\'"]game_height[\'"]:(\d+)')

UNITY_EMBED = """<html>
    <head>
        <title>%s</title>
        <style>
            body { background-color: #000000; height: 100%%; margin: 0; }
            #embed { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }
        </style>
    </head>
    <body>
        <div style="width: %spx; height: %spx" id="embed">
            <embed src="%s" bgColor=#000000  width=100%% height=100%% type="application/vnd.unity" disableexternalcall="true" disablecontextmenu="true" disablefullscreen="false" firstframecallback="unityObject.firstFrameCallback();">
        </div>
    </body>
</html>
"""

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
        self.title = soup.find("h1", itemprop="name").text.strip()

        # Get Logo
        try: self.logo = fpclib.normalize(soup.find("meta", property="og:image")["content"], keep_prot=True)
        except: pass

        # Get Developer and set Publisher
        self.dev = [dev.text.strip() for dev in soup.select(".game_dev_list > li")]
        self.pub = "Kongregate"

        # Get Release Date
        date = soup.select_one(".game_pub_plays > p > .highcontrast").text
        self.date = date[-4:] + "-" + fpclib.MONTHS[date[:3]] + "-" + date[5:7]

        # Get description (combination of instructions and description)
        # idata is inside a script tag and hasn't been inserted yet.
        idata = bs4.BeautifulSoup(soup.select_one("#game_tab_pane_template").string, "html.parser")

        desc = ""
        try:
            desc += "Description\n" + idata.select_one("#game_description > div > .full_text").text.replace("\t", "")[:-9]
        except: 
            try: desc += "Description\n" + idata.select_one("#game_description > p").text.replace("\t", "")
            except: pass
        try:
            desc += ("\n\n" if desc else "") + "Instructions\n" + idata.select_one("#game_instructions > div > .full_text").text[:-9].replace("\t", "")
        except:
            try: desc += ("\n\n" if desc else "") + "Instructions\n" + idata.select_one("#game_instructions > p").text.replace("\t", "")
            except: pass

        self.desc = desc

        # Get tags
        tags = soup.find_all('a', attrs={'class':'term'})
        if len(tags):
            self.tags = [x.text for x in tags]

        # Kongregate makes it slightly difficult to find the launch command, but we'll get there
        # First, find the script next to the would be game frame:
        if_script = soup.select_one("#gameiframe + script").string
        # Next, get the location of the html containing the game frame (using a uuid might help to avoid potential blocks)
        if_url = IF_URL.search(if_script)[1] + k_uuid + "?kongregate_host=www.kongregate.com"
        # Then soupify that new url and find the relavant script data
        scripts = fpclib.get_soup(if_url).select("body > script")

        if len(scripts) > 3:
            # Effectively confirmed, this is a Flash or Unity game
            gdata = scripts[4].string
            # If game_swf is present, that takes priority
            cmd = GAME_SWF.search(gdata)
            self.platform = "Flash"
            self.app = fpclib.FLASH
            if cmd: cmd = fpclib.normalize(urllib.parse.unquote(cmd[1]))
            else:
                # Otherwise check that there isn't a uuid in the swfurl, or is Unity (if neither, throw an error)
                try:
                    unity_data = EMBED_UNITY.search(gdata)
                    self.if_url = fpclib.normalize(urllib.parse.unquote(unity_data[1]))
                    self.if_file = self.if_url
                    cmd = fpclib.normalize(self.src)
                    self.size = ["", unity_data[2], unity_data[3]]
                    self.platform = "Unity"
                    self.app = fpclib.UNITY
                except:
                    # Otherwise check that there isn't a uuid in the swfurl
                    cmd = fpclib.normalize(SWF_URL.search(gdata)[1])
                    if UUID.search(cmd): raise ValueError("swfurl is not a valid game swf")
                    self.platform = "Flash"
            self.cmd = cmd
        else:
            # It's not a Flash game, so we will embed the html ourselves later
            self.platform = "HTML5"
            self.app = fpclib.FPNAVIGATOR
            self.cmd = fpclib.normalize(self.src)
            self.if_url = fpclib.normalize(if_url, keep_vars=True)
            self.if_file = fpclib.normalize(if_url)
            self.size = SIZE.search(if_script)

    def get_files(self):
        if self.platform == "HTML5" or self.platform == "Unity":
            # Download iframe that ought to be embedded
            fpclib.download_all((self.if_url,))
            # Replace all references to https with http
            fpclib.replace(self.if_file[7:], "https:", "http:")
            # Create file to embed swf
            f = self.cmd[7:]
            if f[-1] == "/": f += "index.html"
            if self.platform == "HTML5": fpclib.write(f, HTML_EMBED % (self.title, self.size[1], self.size[2], self.if_file))
            else: fpclib.write(f, UNITY_EMBED % (self.title, self.size[1], self.size[2], self.if_file))
        else:
            # Flash games are downloaded normally
            super().get_files()

    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass
