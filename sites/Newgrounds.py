# Newgrounds definition. Supports HTML5, Flash, and Unity

import fpclib
import json, re, bs4
from os.path import exists

# This is the regex that will be used to match this site. It is required!
regex = 'newgrounds.com'
# This is the minimum minor version of fpcurator required to run this definition.
ver = 6

# Priority that the site has when matching regexes. Higher priorities will be checked first. If left out, it is assumed to be 0.
priority = 0

# You may define as many global variables as you like, though these are not required.
EMBED_CONT = re.compile(r'embedController\((\[.*\])(,\w+)+\);')
HTML_EMBED = re.compile(r'var code = "(.*?)"; } else {')
HTML_FILES = re.compile(r'.*\.(js|html|css|json)$')

# This is the class to use to curate with. It is also required!
class Newgrounds(fpclib.Curation):
    def get_auth_from_file(self, clients_file, param_name):
        try: client_data = fpclib.read(clients_file)
        except: client_data = fpclib.read("./" + clients_file)
        try: return re.search(param_name + r'=(.*?)(\r\n|$)', client_data).group(1)
        except: raise ValueError(clients_file + f' is missing data for "{param_name}=".')

    def parse(self, osoup):
        try:
            self._parse(osoup)
        except:
            print('ue')
            url = self.url if self.url[-1] != "/" else self.url[:-1]
            self._parse(fpclib.get_soup(url + "/format/flash"))

    def _parse(self, soup):
        # Check for login-lock
        try: login_required = "requires a Newgrounds account to play" in soup.select_one(".column").text
        except: login_required = True
        if login_required:
            cookie = self.get_auth_from_file('clients.txt', 'NEWGROUNDS_COOKIE')
            if cookie == '':
                raise ValueError("NSFW entry or limit rate reached; add a valid user cookie in clients.txt's NEWGROUNDS_COOKIE variable.")
            soup = fpclib.get_soup(self.url, headers={"COOKIE": cookie})

        # Get Developer(s)
        devsl = []
        try:
            for div in soup.find('ul', class_='authorlinks').find_all('div', class_='item-details-main'):
                devsl.append(div.find('h4').text.strip())
        except (AttributeError, TypeError):
            pass
        devs = "; ".join(devsl)

        # Get Tags
        try:
            tags = "; ".join(soup.find('div', id='sidestats').find_all('dl')[1].find('a').text.split(' - '))
        except (AttributeError, IndexError, TypeError):
            tags = ""

        # Get content area and header
        content_area = soup.find('div', id='content_area')
        header = content_area.find('h2', itemprop='name')

        # Get Relese Date
        date = content_area.find('meta', itemprop='datePublished')['content'][:10]
        # Get Description and author comments
        desc = content_area.find('meta', itemprop='description')['content'] + '\n'
        a_c = soup.find('div', id='author_comments')
        if a_c:
            desc += '\nAuthor Comments:\n'
            for elem in a_c.children:
                if isinstance(elem, bs4.NavigableString):
                    continue
                if elem.name == 'ul':
                    for li in elem.children:
                        if isinstance(li, bs4.NavigableString):
                            continue
                        desc += '\n  - ' + li.text
                elif elem.name == 'ol':
                    i = 1
                    for li in elem.children:
                        if isinstance(li, bs4.NavigableString):
                            continue
                        desc += '\n  ' + str(i) + '. ' + li.text
                        i += 1
                else:
                    desc += '\n' + elem.text
        # Get Library
        if content_area.find('meta', itemprop='applicationCategory'):
            lib = 'arcade'
        else:
            lib = 'theatre'

        # Get Logo
        try:
            # Get id based on url
            nid = self.url[self.url.rfind("/")+1:]
            self.logo = f"https://picon.ngfiles.com/{nid[:-3]}000/flash_{nid}_card.png"
        except: pass


        # Determine Extreme
        if header['class'] in ['rated-m', 'rated-a']:
            extreme = 'Yes'
        else:
            extreme = 'No'

        # Get embed code
        a = soup.select_one('.portal-barrier a')
        if a:
            nsoup = fpclib.get_soup(a[href])
        else:
            nsoup = soup
        embed_code = EMBED_CONT.search(str(nsoup)).group(1).replace('callback:null', '"callback_function": ""')
        # Embed code found. Now strip it of js functions
        function_loc = embed_code.find('callback:')
        while (function_loc != -1):
            index = function_loc + 20
            nest = 1
            while (nest != 0):
                lb = embed_code.find('{', index)
                rb = embed_code.find('}', index)
                if (lb == -1 or rb < lb):
                    nest -= 1
                    index = rb + 1
                else:
                    nest += 1
                    index = lb + 1
            embed_code = embed_code[:function_loc] + '"callback_function": "function() ' + embed_code[function_loc+19:index].replace('\\', '\\\\').replace('"', '\\"') + '"' + embed_code[index:]
            function_loc = embed_code.find('callback:')
        # Load the stripped embed code as json
        embeds_list = json.loads(embed_code)
        # Get best embed (prefers Flash)
        embed = embeds_list[0]
        for e in embeds_list:
            if 'Flash' in e['description']:
                embed = e
                break
        # Get Platform, Application Path, and Launch Command
        if 'Flash' in embed['description']:
            platform = 'Flash'
            app = fpclib.FLASH
            cmd = fpclib.normalize(embed['url'])
        elif 'Unity File' in embed['description']:
            # Basic data
            platform = 'Unity'
            app = fpclib.UNITY
            cmd = fpclib.normalize(self.get_meta("source"))
            # Setup html file
            style = 'body { background-color: #000000; height: 100%; margin: 0; }\n            embed { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }'
            unity_file = fpclib.normalize(embed['url'])
            html_embed = '<embed src="%s" width="%s" height="%s" type="application/vnd.unity" disableexternalcall="true" disablecontextmenu="true" disablefullscreen="false" firstframecallback="unityObject.firstFrameCallback();" />' % (unity_file, embed['width'], embed['height'])
            html = '<html>\n    <head>\n        <title>%s</title>\n        <style>\n            %s\n        </style>\n    </head>\n    <body>\n        %s\n    </body>\n</html>' % (header.text, style, html_embed)
            # Save for writing
            self.set_meta(html=html, unity_file=unity_file)
        else:
            # Basic data
            platform = 'HTML5'
            app = fpclib.FPNAVIGATOR
            cmd = fpclib.normalize(self.get_meta('source'))
            # Setup html file
            style = 'body { background-color: #000000; height: 100%; margin: 0; }\n            div { position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: auto; }'
            html_embed = HTML_EMBED.search(embed['callback_function']).group(1).replace('\\n', ' ').replace('\\t', '').replace('\\"', '"').replace('\\\\', '\\').replace('\\/', '/').replace('https:', 'http:')
            html = '<html>\n    <head>\n        <title>%s</title>\n        <style>\n            %s\n        </style>\n    </head>\n    <body>\n        %s\n    </body>\n</html>' % (header.text, style, html_embed)
            # Save for writing
            self.set_meta(html=html, embed_url=fpclib.normalize(embed['url']))

        # Set meta
        self.set_meta(
            title=header.text,
            lib=lib,
            dev=devs,
            pub='Newgrounds',
            date=date,
            extreme=extreme,
            tags=tags,
            platform=platform,
            desc=desc,
            app=app,
            cmd=cmd
        )

    def get_files(self):
        html = self.get_meta('html')
        if html:
            cmd = self.get_meta('cmd')
            fpclib.write(cmd[cmd.index('://')+3:], html)

            platform = self.get_meta('platform')
            if platform == 'HTML5':
                fpclib.download_all([self.get_meta('embed_url')+'/index.html'])
            elif platform == 'Unity':
                fpclib.download_all([self.get_meta('unity_file')])

            # Replace all instances of https with http
            fpclib.replace(fpclib.scan_dir('', HTML_FILES)[0], 'https:', 'http:')
        else:
            super().get_files()

    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass