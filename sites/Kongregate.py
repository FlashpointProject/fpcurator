# Kongregate definition.

import fpclib
import bs4, re, urllib, uuid, json

regex = 'kongregate.com'
ver = 7 # Made to work with the 2026 site redesign

IF_URL = re.compile(r'[\'"]iframe_url[\'"]:[\'"](.*?)[\'"]')
SWF_URL = re.compile(r'swf_location\s?=\s?[\'\"]\/?\/?(.+?)(\?.+?)?[\'\"]')
GAME_SWF = re.compile(r'[\'"]game_swf[\'"]:[\'"](.*?)[\'"]')
EMBED_UNITY = re.compile(r'kongregateUnityDiv\\\",\s\\\"\/\/(.*?)\\",\s(\d*?),\s(\d*?),')
UUID = re.compile(r'[0-9a-fA-F]{32}')
SIZE = re.compile(r'[\'"]game_width[\'"]:(\d+),[\'"]game_height[\'"]:(\d+)')
GAME_TYPE = re.compile(r'game_type":[\'"](.*)[\'"]')

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
        
        metaJson = soup.find("script", type="application/ld+json").text
        metaJson = json.loads(metaJson)
        
        gameJson = []
        for x in metaJson['@graph']:
            if x['@type'] == "VideoGame" or "VideoGame" in x['@type']:
                gameJson = x
        
        
        self.title = gameJson['name']

        # Get Logo
        try: self.logo = gameJson['image'].split("?")[0]
        except: pass

        # Get Developer and set Publisher
        self.dev = gameJson['author']['name']
        self.pub = "Kongregate"

        # Get Release Date
        self.date = gameJson['datePublished'].split("T")[0]

        # Get description (combination of instructions and description)
        desc = ""
        try:
            howToPlay = soup.find_all("div",{"class":"mb-8 text-left"})[1].text
            
            desc += gameJson['description'] + "\n"
            desc += howToPlay
        
        except:
            desc = gameJson['description']

        self.desc = desc.strip()
        
        
        # get iframe embed
        embedUrl = soup.find("iframe", {"class":"game-embed-iframe"})['src']
        embedData = fpclib.get_soup("https://www.kongregate.com/" + embedUrl)
        
        # Then retrieve the game embed within the iframe embed
        scripts = embedData.find_all("script")
        for x in scripts:
            if "iframeUrl" in x.text:
                if_url = IF_URL.search(x.text)[1]
                self.size = SIZE.search(x.text)
                
                # The game type is referenced directly in the iframeConfig,
                # we can use it to quickly know how to deal with the game
                gameType = GAME_TYPE.search(x.text)[1]
                
                if if_url[:2] == "//":
                    if_url = "http:" + if_url
                
                if if_url[-7:] == "/frame/":
                    if_url = if_url + k_uuid + "/?kongregate_host=www.kongregate.com"
        
        
        if gameType == "flash" or gameType == "unity":
            gameEmbed = fpclib.get_soup(if_url)
            gameScripts = gameEmbed.find_all("script")
            
            for x in gameScripts:
                if "swf_location" in x.text:
                    if_file = SWF_URL.search(x.text)[1]
                elif "kongregateUnityDiv" in x.text:
                    if_file = EMBED_UNITY.search(x.text)[1]

            
        if gameType == "html" or gameType == "iframe":
            self.platform = "HTML5"
            self.app = fpclib.FPNAVIGATOR
            self.cmd = fpclib.normalize(if_url).rsplit("/",1)[0] + "/customKongEmbed.html"
            self.if_url = fpclib.normalize(if_url, keep_vars=True)
            self.if_file = fpclib.normalize(if_url)
        
        elif gameType == "flash":
            self.platform = "Flash"
            self.app = fpclib.FLASH
            self.cmd = fpclib.normalize(if_file)
        
        elif gameType == "unity":
            self.platform = "Unity"
            self.app = fpclib.UNITY
            self.cmd = fpclib.normalize(if_url)
            self.if_url = fpclib.normalize(if_url, keep_vars=True)
            self.if_file = fpclib.normalize(if_file)
        
        else:
            raise ValueError("Unhandled game type. Only Flash, HTML5 and Unity are supported")

            

    def get_files(self):
        if self.platform == "HTML5" or self.platform == "Unity":
            # Download iframe that ought to be embedded
            fpclib.download_all((self.if_file,))
            # Replace all references to https with http
            fpclib.replace(self.if_file[7:], "https:", "http:")
            # Create file to embed swf
            f = self.cmd[7:]
            if f[-1] == "/": f += "index.html"
            
            if self.platform == "HTML5":
                fpclib.write(f, HTML_EMBED % (self.title, self.size[1], self.size[2], self.if_file))
            else: 
                fpclib.write(f, UNITY_EMBED % (self.title, self.size[1], self.size[2], self.if_file))
                #fpclib.download_all((self.if_file,))
        else:
            # Flash games are downloaded normally
            super().get_files()

    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass
