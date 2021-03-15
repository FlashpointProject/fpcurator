# Site definition for Andkon
from __main__ import fpclib
import re, bs4, requests

regex = 'andkon.com'
priority = 1

REMOVABLES = re.compile(r'[\r\n]')
TAG_REGEX = re.compile(r'(?<=arcade/)[^/]+')
TAGS = {
    'adventureaction': 'Action; Adventure',
    'casino': 'Simulation; Gambling',
    'missiledefender': 'Arcade; Action; Shooter; Tower Defense',
    'mousegames': 'Arcade',
    'obstacles': 'Arcade; Dodge',
    'other': 'Arcade; Other',
    'puzzle': 'Puzzle',
    'racing': 'Arcade; Driving; Racing',
    'shooter': 'Action; Shooter',
    'sport': 'Arcade; Sports',
    'tetris': 'Arcade; Tetris'
}

BAD_NAV_STR = bs4.NavigableString('\n')

class Andkon(fpclib.Curation):
    def parse(self, soup):
        # Get Title
        title = soup.find('h1').text.strip()
        
        # Get Developer and Description
        box_c = soup.select_one('.left').text.strip() + '\n'
        author_index = box_c.find('Author Info:')
        end = box_c.find('\n', author_index+15)
        start = box_c.find('s:') + 2
        
        desc = box_c[start:author_index].strip()
        dev = box_c[author_index+12:end].strip()
        if dev == '?':
            dev = ''
        
        # Determine Tags
        url = self.get_meta('source')
        tags = TAGS[TAG_REGEX.search(url).group(0)]
        
        # Get Game
        obj = soup.find('embed')
        if obj:
            try:
                cmd = url + obj['src']
            except:
                cmd = url + obj['value']
        else:
            obj = soup.find('object')
            cmd = url + obj['data']
        
        # Set meta
        self.set_meta(
            title=title,
            dev=dev,
            pub='Andkon',
            tags=tags,
            tech='Shockwave',
            app=fpclib.SHOCKWAVE,
            cmd=cmd,
            desc=desc
        )
        
        # Get Logo; causes some issues and really isn't that important
        #self.logo = 'http://andkon.com/arcade/ICONS/' + url[url.rfind('/', 0, -1):-1] + '.gif'
    
    # def get_files(self):
        # url = self.get_meta('source')
        # base = url[url.index('://')+3:]
        # applet = self.get_meta('applet')
        # code = applet['code']
        # if not code.endswith('.class'):
            # code += '.class'
        # elif code.endswith('.jar'):
            # raise Exception('WRONG')
        
        # try:
            # jar = applet['archive']
            # if not jar.endswith('.jar'):
                # jar += '.jar'
        # except:
            # jar = ''
        
        # fpclib.make_dir(base, True)
        # fpclib.write('index.html', str(applet))
        
        # with requests.get(url + code) as response:
            # if b'<TITLE>404 Not Found</TITLE>' not in response.content:
                # with open(code, 'wb') as file:
                    # file.write(response.content)
        
        # if jar:
            # with requests.get(url + jar) as response:
                # if b'<TITLE>404 Not Found</TITLE>' not in response.content:
                    # with open(jar, 'wb') as file:
                        # file.write(response.content)