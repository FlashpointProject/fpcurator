# Miniclip definition. Only supports HTML5.
from __main__ import fpclib
from __main__ import re, json

regex = 'miniclip.com'

HTML_EMBED = """<body>
    <iframe width="100%" height="100%" src="%s"></iframe>
</body>
"""

GAME_URL = re.compile('game_url: "(.*?)"')

class Miniclip(fpclib.Curation):
    def parse(self, soup):
        # Base everything off of application data, which is hopefully more stable than the webpage format
        data = json.loads(soup.select_one("#jsonLdSchema").string)

        self.title = data["name"]
        self.logo = data["image"]
        self.pub = "Miniclip"
        # This theoretically could be used to generate more accurate tags, but whatever
        self.tags = data["genre"]
        self.date = data["datePublished"][:10]

        # Get Description
        try: self.desc = soup.select_one(".game-description").text.strip()
        except: pass

        # Only HTML5 is supported
        self.platform = "HTML5"
        self.app = fpclib.BASILISK

        # Get file for Launch Command
        url = GAME_URL.search(soup.select(".game-embed-wrapper > script")[1].string)[1]
        if url[0] == "/" and url[1] != "/":
            url = "http://www.miniclip.com" + url
        self.if_url = fpclib.normalize(url)

        self.cmd = fpclib.normalize(self.src)
    
    def get_files(self):
        # Download iframe that ought to be embedded
        fpclib.download_all((self.if_url,))
        # Replace all references to https with http
        fpclib.replace(self.if_url[7:], "https:", "http:")
        # Create file to embed swf
        fpclib.write(self.cmd[7:], HTML_EMBED % self.if_url))
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass