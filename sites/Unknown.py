# This is the catch-all unknown site definition. It might not work right in all cases!

import fpclib
import urllib
import re

regex = "."
ver = 6

priority = -10000

class Unknown(fpclib.Curation):
    def parse(self, soup):
        def check_platform(url, end, cmd):
            if end == ".swf":
                # Flash game
                self.platform = "Flash"
                self.app = fpclib.FLASH
                self.cmd = cmd
            elif end in {".dir", ".dcr", ".dxr"}:
                # Shockwave game
                self.platform = "Shockwave"
                self.app = fpclib.SHOCKWAVE
                self.cmd = '"' + cmd + '"'
            elif end == "ty3d":
                # Unity game
                self.platform = "Unity"
                self.app = fpclib.UNITY
                self.cmd = url
                self.embed = embed.parent.prettify()
                self.unity = cmd
            else:
                raise ValueError("Unknown game type")

        # Get title
        t = soup.find("h1")
        if t: self.title = t.text.strip()
        else:
            t = soup.find("title")
            if t: self.title = t.text.strip()
        if not self.title: self.title = ("(Could not find the title of the curation)")

        # Attempt to get logo
        try: self.logo = soup.find("meta", property="og:image")["content"]
        except: pass

        url = fpclib.normalize(self.src)
        if url[-1] == "/": url += "index.html"

        # HTML5 is not supported, because iframes are unpredictable little things
        embed = soup.find("embed")
        if embed:
            cmd = embed["src"]
            if "//" in cmd: cmd = fpclib.normalize(cmd)
            elif cmd[0] == "/":
                site = urllib.parse.urlparse(url).netloc
                cmd = "http://" + site + cmd
            else: cmd = url + cmd

            end = fpclib.normalize(embed["src"])[-4:]
            check_platform(url, end, cmd)
            if end == "ty3d":
                self.embed = embed.parent.prettify()
        else:
            applet = soup.find("applet")
            if applet:
                # Java game
                self.platform = "Java"
                self.app = fpclib.JAVA
                self.cmd = url
                self.applet = str(applet)
            else:
                for script in soup("script"):
                    # print(script.text)
                    script_search_swf = re.search(r'[\'\"]((https?:\/\/)?[a-z0-9_$&+\.\/:;=?@\s]+?\.(swf|dir|dcr|dxr|unity3d)(\?.+?))[\'\"]', script.text)
                    if script_search_swf:
                        self.platform = "Flash"
                        self.app  = fpclib.FLASH
                        cmd = script_search_swf.group(1)
                        if "//" in cmd: cmd = fpclib.normalize(cmd)
                        elif cmd[0] == "/":
                            site = urllib.parse.urlparse(url).netloc
                            cmd = "http://" + site + cmd
                        check_platform(url, fpclib.normalize(cmd)[-4:], cmd)
                        break

            if not self.cmd:
                raise ValueError("Unknown game type (HTML5 is not supported in generic curations)")

    def get_files(self):
        if self.platform == "Unity":
            # Unity has an embed file created for it
            f = self.cmd[7:]
            fpclib.write(f, self.embed)
            fpclib.replace(f, "https:", "http:")
            # And the unity file needs to be downloaded
            fpclib.download_all((self.unity,))
        elif self.platform == "Shockwave":
            # Shockwave launch command has quotes around it
            fpclib.download_all((self.cmd[1:-1],))
        elif self.platform == "Java":
            # Java needs an embed created much like unity
            f = self.cmd[7:]
            fpclib.write(f, self.applet)
            fpclib.replace(f, "https:", "http:")
            # And the class or jar file needs to be downloaded too... actually nevermind MAD4FP can handle it
        else:
            # Flash is very simple
            fpclib.download_all((self.cmd,))