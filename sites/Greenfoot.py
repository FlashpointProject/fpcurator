# Greenfoot definition.

import fpclib
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests

regex = 'greenfoot.org'

APPLET_EMBED = """<html>
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

class Greenfoot(fpclib.Curation):
    def parse(self, soup):
        #Get Title
        self.title = soup.find("h1").text

        # Get Developer and set Publisher
        self.dev = soup.select_one(".avatar_heading > a").text
        self.pub = "Greenfoot"
        
        # Get Release Date
        date = soup.find("div", "avatar_bar").find("p").text
        if date.find("second") != -1: date = (datetime.today() - timedelta(seconds=re.search(r'^\d*?(?=\s)', date).group(0))).strftime('%Y-%m-%d')
        if date.find("minute") != -1: date = (datetime.today() - timedelta(minutes=re.search(r'^\d*?(?=\s)', date).group(0))).strftime('%Y-%m-%d')
        elif date.find("hour") != -1: date = (datetime.today() - timedelta(hours=re.search(r'^\d*?(?=\s)', date).group(0))).strftime('%Y-%m-%d')
        elif date.find("yesterday") != -1: date = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        elif date.find("days") != -1: date = (datetime.today() - timedelta(days=re.search(r'^\d*?(?=\s)', date).group(0))).strftime('%Y-%m-%d')
        else: date = datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%m-%d')
        self.date = date

        # Get Description
        desc = soup.select_one(".description").text.strip().strip('\r\n')
        if desc != "No description." : self.desc = desc

        # Platform/App/Tag
        self.platform = "Java"
        self.app = fpclib.JAVA
        self.tags = ["Greenfoot"]

        # Get Source
        self.cmd_html = fpclib.normalize(self.src)
        self.cmd = self.cmd_html + "@js_false"

        # Get the opposite (Java/Html) version
        if not "?js=false" in self.src:
            html_soup = soup
            soup = BeautifulSoup(requests.get(self.cmd_html + "?js=false").content, 'html.parser')
        else: html_soup = BeautifulSoup(requests.get(self.cmd_html).content, 'html.parser')
            
        # Get jar url and embed
        #print(str(soup))
        self.java_applet = str(soup.find("applet"))
        #print(self.java_applet)
        self.java_url = "http://www.greenfoot.org" + str(soup.find("applet")['archive'])

        # If the game can be run in a browser, add that as an alt app
        self.html_embed = None
        if(html_soup.text.find("There is no HTML 5 translation of this scenario available") == -1):
            html_embed = html_soup.find("div", "applet_div")
            html_embed.find("div", "scenario_help").decompose()
            html_embed.find('div', id="embed-dialog").decompose()
            self.html_embed = str(html_embed)
            self.js_one = "http://www.greenfoot.org" + str(html_embed.select_one("script")['src'])
            self.js_two = "http://www.greenfoot.org" + str(html_embed.find_all("script")[1]['src'])
            self.add_app("HTML Emulated version", self.cmd_html, path=fpclib.BASILISK)

        if self.html_embed: self.cnotes = "If the applet version does not work, set the platform to HTML5 and have the alt app as the main version (delete %s)" % self.cmd[7:]

    def get_files(self):
        # Download jar
        fpclib.download_all((self.java_url,))
        # Create embed files
        f = self.cmd[7:]
        fpclib.write(f, self.java_applet)
        if self.html_embed:
            fpclib.download_all((self.js_one, self.js_two,))
            fpclib.write(self.cmd_html[7:], self.html_embed)
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass