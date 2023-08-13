# itch.io site definition (This is just the Unknown site definition but with a few extra kinks)

import fpclib
import re
from html import unescape

regex = "itch.io"
# Only handles at most two sublevels.
PLATFORM = re.compile(r'new I\.View(\w+)Game\(')
VIEW_DATA = re.compile(r'{"url":(.*?{(.*?{.*?}|[^{}]*)*}|[^{}]*)*}')

UNITY_EMBED = """<html>
    <head>
        <title>%s</title>
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
</html>
"""

HTML_EMBED = """<html>
    <head>
        <title>%s</title>
        <style>
            body { background-color: #000000; height: 100%%; %s margin: 0;}
            %s
        </style>
    </head>
    <body><center>
        %s
    </center></body>
</html>
"""
STYLE_IFRAME = """iframe { %s; }"""
IFRAME = """<iframe src="%s"></iframe>"""

class ItchIO(fpclib.Curation):
    def parse(self, soup):
        # Get title
        self.title = soup.find("h1", "game_title").text
        # Get logo
        try:
            self.logo = soup.select_one(".header.has_image > img")["src"]
        except:
            try:
                self.logo = soup.find("meta", property="og:image")["content"]
            except: pass

        # Get devs
        try:
            authors = soup.find("td", text="Authors").parent
            self.dev = [e.text for e in authors.find_all("a")]
        except: pass
        try:
            author = soup.find("td", text="Author").parent
            self.dev = [e.text for e in author.find_all("a")]
        except: pass
        
        # Get Genre/Tags
        self.tags = []
        try:
            tags = soup.find("td", text="Genre").parent
            self.tags = [e.text for e in tags.find_all("a")]
        except: pass
        try:
            tags = soup.find("td", text="Tags").parent
            self.tags += [e.text for e in tags.find_all("a")]
        except: pass
        try:
            tags = soup.find("td", text="Made with").parent
            self.tags += [e.text for e in tags.find_all("a")]
        except: pass
        try:
            tags = soup.find("li", "jam_entry").text[14:]
            edition = re.search(r'\s+\W?\d*$', tags).group(0)
            if edition != None: tags = tags.rstrip(edition)
            self.tags += [tags]
        except: pass
        
        # Get languages
        try:
            lang = soup.find("td", text="Languages").parent
            self.lang = [e["href"][-2:].lower() for e in lang.find_all("a")]
        except: pass
            
        # Set publisher
        self.pub = "itch.io"

        # Release date
        # Currently won't get the date as it only shows up by being logged
        try:
            info_table = soup.select_one(".game_info_panel_widget tbody")
            self.date = fpclib.DP_UK.parse(re.search(r'Published<\/td><td><abbr title="(.+?)"', str(info_table)).group(1))
        except: pass

        # Description
        try:
            desc = re.sub(r'<.*?>', '', repr(soup.select_one('.formatted_description')).replace('<li>', '\r\n•').replace('</tr>', '\r\n').replace('</td><td>', ' ').replace('<br>', '\r\n')).replace('\r\n\r\n', '\r\n').strip('\r\n')
            self.desc = None if desc == 'None' else unescape(desc.replace('\r\n\r\n', '\r\n'))
            print(self.desc)
        except: raise

        # Style
        style = ''
        size = 'width: 100%; height: 100%'
        if '"start_maximized":false' in str(soup):
            try:
                style = re.search(r'background-.*?(?=})', str(soup.find('style'))).group(0).replace('https', 'http')
                size = str(soup.select_one('.game_frame')['style'])
            except: pass
        
        url = fpclib.normalize(self.src)
        if url[-1] == "/": url = url[:-1]

        # Get launch command and stuff
        # First check for html iframe
        placeholder = soup.select_one("div.iframe_placeholder")
        iframe = soup.select_one(".embed_wrapper > div > iframe")
        if placeholder and "data-iframe" in placeholder.attrs:
            self.platform = "HTML5"
            self.app = fpclib.BASILISK
            self.cmd = url
            self.file = ""
            self.embed = HTML_EMBED % (self.title, style, STYLE_IFRAME % size, placeholder["data-iframe"])
        elif iframe:
            self.platform = "HTML5"
            self.app = fpclib.BASILISK
            self.cmd = url
            self.file = ""
            self.embed = HTML_EMBED % (self.title, style, STYLE_IFRAME % size, str(iframe))
        else:
            # No html frame, so check for other potential games
            selem = soup.select_one(".inner_column > script")
            if selem:
                # If script exists on page, try to find the game from the code
                script = selem.string

                platform = PLATFORM.search(script)[1]
                try:
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
                        self.cmd = url # Helps deal with url-locks, I guess
                        self.embed = HTML_EMBED % (self.title, STYLE_IFRAME, IFRAME % fpclib.normalize(data["url"]))
                    elif platform == "Unity":
                        self.app = fpclib.UNITY
                        self.cmd = url
                        self.embed = UNITY_EMBED % (self.title, soup.select_one("#unity_drop")["style"], data["url"])
                    elif platform == "Java":
                        self.app = fpclib.JAVA
                        self.cmd = url
                        self.embed = str(soup.find("applet"))
                    else:
                        raise ValueError("Unknown game type found on webpage")
                except TypeError:
                    # Ok so, the script doesn't work right, and
                    # no iframe on page, so we ain't got a clue about this one
                    raise ValueError("Script found but can't locate game")
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