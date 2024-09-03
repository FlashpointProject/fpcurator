import fpclib
import requests
import re
import bs4

regex = '4399.com'
ver = 7

GAME_URL = re.compile(r"_\d+.htm$")
IS_HTML5 = re.compile(r"var\s+isHTML5\s*=\s*(\d+)", re.IGNORECASE)
SCREENSHOT = re.compile(r'var\s+\w+GamePic\s*=\s*"(.*?)"', re.IGNORECASE)
GAMEPATH = re.compile(r'var\s+\w+GamePath\s*=\s*"(.*?)"', re.IGNORECASE)
DIMS = re.compile(r'var\s+_w\s*=\s*(\d+);?\s*var\s+_h\s*=\s*(\d+)')

HTML_EMBED = """<body>
    <style>
        body { background-color: #16202c; height: 100%%; margin: 0; }
        iframe { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }
    </style>
    <iframe width="%s" height="%s" src="%s"></iframe>
</body>
"""
FLASH_EMBED = """<body>
    <style>
        body { background-color: #16202c; height: 100%%; margin: 0; }
        object { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }
    </style>
    <object type="application/x-shockwave-flash" width="%s" height="%s" data="%s">
        <param name="allowscriptaccess" value="always">
        <param name="allowfullscreen" value="true">
        <param name="allowfullscreeninteractive" value="true">
        <param name="allownetworking" value="all">
        <param name="wmode" value="direct">
    </object>
</body>
"""

class c4399(fpclib.Curation):
    def soupify(self):
        # Correct URL if not on the actual game page
        with requests.get(self.src) as resp:
            soup = bs4.BeautifulSoup(resp.content, "html.parser")
        if not GAME_URL.search(self.src):
            self.src = "https://wwww.4399.com" + soup.select_one(".play > a")["href"]
            with requests.get(self.src) as resp:
                soup = bs4.BeautifulSoup(resp.content, "html.parser")
        return soup

    def parse(self, soup):
        # Basic metadata
        self.title = soup.select_one(".game-des > .name > a").text.strip()
        self.date = soup.select_one(".game-des > .sorts.cf > em:last-of-type").text.strip()[3:]
        self.lang = 'zh'
        self.pub = "4399"

        # Description transformation
        box = soup.select_one("#playmethod > .box-l")
        has_ptex = bool(box.select_one("#p-tex"))
        desc = []
        for tag in box.children:
            # Skip random strings
            if isinstance(tag, bs4.element.NavigableString): continue
            # Grab header elements as is
            if tag.name == "b": desc.append(tag.text.strip() + "\n")
            # Grab content elements as is
            if "content" in tag.get("class"): desc.append(tag.text.strip() + "\n" + "\n")

            # Transform control information (but only if a direct description is not provided)
            if tag.get("id") == "GameKey" and not has_ptex:
                for ul in tag.children:
                    # Skip random strings
                    if isinstance(ul, bs4.element.NavigableString): continue
                    # Loop over each list
                    for li in ul.children:
                        # Skip random strings
                        if isinstance(ul, bs4.element.NavigableString): continue

                        for elem in li.children:
                            # Add text as is
                            if isinstance(elem, bs4.element.NavigableString):
                                desc.append(str(elem)+" ")
                                continue

                            # Only Span elements have their class-name translated to text
                            if elem.name != "span": continue

                            cs = elem.get("class")[0]
                            if not cs: continue
                            if cs.startswith("player"):
                                desc.append("玩家" + cs[6:] + " ")
                            elif cs == "ico_c_arrows":
                                desc.append("Arrow Keys ")
                            elif cs == "ico_c_wasd":
                                desc.append("WASD ")
                            elif cs.startswith("ico_c_"):
                                desc.append(cs[6:].title() + " ")
                            elif elem.text:
                                desc.append(elem.text + " ")

                    # After a list ends add a newline for the next list.
                    desc.append("\n")

        self.desc = ''.join(desc)

        headtxt = str(soup.head)

        # Screenshot
        try:
            self.ss = "https:" + SCREENSHOT.search(headtxt)[1].strip()
        except:
            fpclib.debug("Screenshot not found", 1, pre="[WARN] ")

        # Platform detection (Flash, Unity, and HTML5)
        try:
            is_html = bool(int(IS_HTML5.search(headtxt)[1]))
        except:
            is_html = False
        self.embed = fpclib.normalize(self.src, False)
        self.cdn = "http://sda.4399.com/4399swf" + GAMEPATH.search(headtxt)[1]

        dims = DIMS.search(headtxt)
        self.dims = (dims[1], dims[2])

        if is_html:
            self.platform = "HTML5"
            self.app = fpclib.FPNAVIGATOR
            self.cmd = self.embed
        elif self.cdn.endswith(".swf"):
            self.platform = "Flash"
            self.app = fpclib.FLASH
            self.cmd = self.cdn
            self.add_app("Embedded Page", self.embed, fpclib.FPNAVIGATOR)
        else:
            self.platform = "Unity"
            self.app = fpclib.UNITY
            self.cmd = self.embed

    def get_files(self):
        # Create embed file
        if self.platform == "Flash":
            html = FLASH_EMBED % (self.dims[0], self.dims[1], self.cdn)
        else:
            html = HTML_EMBED % (self.dims[0], self.dims[1], self.cdn)
        fpclib.write(self.embed[self.embed.index("://")+3:], html)

        # Download the game's true embedded file
        fpclib.download_all((self.cdn,), spoof=True)
