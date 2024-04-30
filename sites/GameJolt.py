# Game Jolt definition.

import fpclib
import re, json
from requests import session
from datetime import datetime

regex = 'gamejolt.com'
ver = 6

UNITY_EMBED = """<html>
    <head>
        <title>%s</title>
        <style>
            body { background-color: #000000; height: 100%%; margin: 0; }
            embed { width: %spx; height: %spx; }
        </style>
    </head>
    <body>
        <center>
            <div id="embed">
                <embed src="%s" bgColor=#000000 type="application/vnd.unity" disableexternalcall="true" disablecontextmenu="true" disablefullscreen="false" firstframecallback="unityObject.firstFrameCallback();">
            </div>
        </center>
    </body>
</html>
"""

class GameJolt(fpclib.Curation):
    def parse(self, soup):
        sess = session()
        self.gameId, = re.findall(r'/(\d+)(?:/|$)', self.src)

        req_overview = sess.get('https://gamejolt.com/site-api/web/discover/games/overview/{}?ignore'.format(self.gameId)).json()
        for i in req_overview['payload']['builds']:
            if i['type'] != 'downloadable' and i['type'] != 'html':

                id_ = i['id']
                req_token = sess.post('https://gamejolt.com/site-api/web/discover/games/builds/get-download-url/{}'.format(id_), data='{}').json()
                token, = re.findall(r'token=([^&]+)', req_token['payload']['url'])
                req_download = sess.get('https://gamejolt.net/site-api/gameserver/{}'.format(token)).json()

                # Title
                self.title = req_download['payload']['game']['title']

                # Platform
                self.platform = i['type'].capitalize()
                if self.platform == "Flash":
                    self.app = fpclib.FLASH
                    self.embed = ""
                    self.if_filename = i['primary_file']['filename']
                elif self.platform == "Html":
                    self.platform = "HTML5"
                    self.app = fpclib.FPNAVIGATOR
                    self.embed = ""
                    self.if_filename = 'index.html'
                elif self.platform == "Unity":
                    self.app = fpclib.UNITY
                    self.embed = UNITY_EMBED % (self.title, i['embed_width'], i['embed_height'], i['primary_file']['filename'])
                    self.if_filename = 'index.html'

                # Publisher
                self.pub = 'Game Jolt'

                # Developer
                self.dev = req_download['payload']['game']['developer']['name']

                # Get Desc and Tags
                self.tags = []
                req_overview2 = sess.get('https://gamejolt.com/site-api/web/discover/games/{}'.format(self.gameId)).json()
                desc = json.loads(req_overview2['payload']['game']['description_content'])['content']
                for paragraph in desc:
                    if 'content' in paragraph:
                        for pcontent in paragraph['content']:
                            if 'text' in pcontent:
                                if ('marks' in pcontent and pcontent['marks'][0]['type'] == 'tag') : self.tags += [pcontent['text'][1:]]
                                else: self.desc = '\r\n'.join(((self.desc if self.desc else ""), pcontent['text']))
                            elif 'content' in pcontent:
                                for pparagraph in pcontent['content']:
                                    self.desc = '\r\n'.join(((self.desc if self.desc else ""), (pparagraph['text'] if ('text' in pparagraph) else pparagraph['content'][0]['text'])))
                self.desc = self.desc.replace(' \r\n', ' ').replace('\r\n ', ' ').strip('\r\n')

                # Get Date
                pub_date = i['added_on']
                self.date = datetime.utcfromtimestamp(pub_date/1000).strftime('%Y-%m-%d')

                # Get Logo
                self.logo = req_download['payload']['game']['img_thumbnail']

                # Get File
                req_url = sess.get('https://gamejolt.net/site-api/gameserver/{}'.format(token)).json()
                #print(req_url)
                self.file = req_url['payload']['url']
                self.cmd = 'http://cdn-files.gamejolt.net/data/games/{}/{}'.format(self.gameId, self.if_filename)

    def get_files(self):
        # We will not use the generated link as the launch command, too long
        fpclib.download(self.file, loc='cdn-files.gamejolt.net/data/games/{}/'.format(self.gameId))
        # If there is an embed to create, create it
        if self.embed:
            f = self.cmd[7:]
            fpclib.write(f, self.embed)
            fpclib.replace(f, "https:", "http:")
