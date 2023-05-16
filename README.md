# fpcurator
fpcurator is a Python and fpclib powered tool for downloading urls, auto-generating curations, bulk searching for already curated games, and listing tags/platforms/games/animations for Flashpoint.

If you don't want to install python to use fpcurator, check the releases page for a release. Extract the fpcurator.zip file and run the `fpcurator.bat` file.

**NOTE: Auto curated games should ALWAYS be tested in Flashpoint Core before being submitted.**

## Basic Usage

Launch the script or executable and choose a tab. You can also drag and drop a list of urls on to the program (if you are using the executable or have python configured correctly) to quickly automatically curate them. For more detailed help on how to use the program, see the built-in "Help" button.

When the program launches up, you may be prompted to download the latest site definitions for the Auto Curator. Site definitions (in the `sites` folder of this github) will be automatically updated over time and you will be prompted to update whenever a new update is available.

If you are looking for command line usage, run `fpcurator --help` or `fpcurator.py --help` in the terminal of your choice.

## Auto Curator Website Support

The Auto Curator supports auto curating games from these websites:

- [Addicting Games](https://www.addictinggames.com/) (Flash and HTML5)
- [Construct](https://www.construct.net/) (HTML5)
- [Coolmath Games](https://www.coolmathgames.com/) (HTML5)
- [Deviant Art](https://www.deviantart.com/) (Flash) - \*
- [FreeArcade](http://www.freearcade.com/) (Flash or Java)
- [Fur Affinity](https://www.furaffinity.net/) (SFW Flash)
- [Game Jolt](https://gamejolt.com/) (Flash or Unity)
- [GameGame](https://game-game.com/) (Flash or HTML5)
- [Greenfoot](https://www.greenfoot.org/collections/) (Java)
- [itch.io](https://itch.io/) (Flash, Java, Unity, or HTML5)
- [Jay is games](https://jayisgames.com/) (Flash, Shockwave, Unity, or HTML5)
- [Kongregate](https://www.kongregate.com/) (Flash, Unity, or HTML5)
- [Mathématiques Magiques](http://therese.eveilleau.pagesperso-orange.fr) (Flash)
- [Miniclip](https://www.miniclip.com/) (HTML5)
- [Newgrounds](https://www.newgrounds.com/) (Flash, Unity, or HTML5)
- [Y8](https://www.y8.com/) (Flash, Shockwave, Unity, or HTML5)
- Unknown websites (Flash, Shockwave, Unity, or Java). HTML5 is **NOT** supported. This may not work on every website.

\* - Deviant Art requires a clients.txt file to be present next to the script, executable, or bat file with the contents `DEVIANTART_ID={ID GOES HERE}` and `DEVIANTART_SECRET={SECRET GOES HERE}` on two lines with the `{THING GOES HERE}`s replaced with the respective content.

To add support for other pages not supported by the tool, first start by creating a file named `<WebsiteName>.py` inside the `sites` folder next to the script/executable and putting this code inside it:

```python
import fpclib
# You can put other imports here, but the standalone only supports importing the following other libraries (Other imports besides the standard library require python to be installed on the host machine and the script to be run directly):

# bs4, qfile, googletrans, Levenshtein, and deviantart.

# This is the regex that will be used to match the site url. It is required!
regex = 'website.com'

# Priority that the site has when matching regexes. Higher priorities will be checked first. If left out, it is assumed to be 0.
priority = 0

# "WebsiteName" should be the exact same as the name in <WebsiteName>.py, otherwise fpcurator will complain.
class WebsiteName(fpclib.Curation):
    def parse(self, osoup):
        # "self" is a curation generated from a given matched url (see fpclib.Curation in the fpclib documentation), while osoup is a beautifulsoup object generated from the html downloaded from the given matched url.
        # You'll want to use self.set_meta to set the metadata of the curation based upon the osoup object.
        pass
	# You can also overwrite any other methods of fpclib.Curation here to add custom functionality, including but not limited to:
    # get_files(self) - This method is called after parse() called to get the files specified by the launch commands of the curation and additional apps (by default). Overwrite it if you want to download other files into the curation (like for html files).
    # soupify(self) - called to get osoup for the parse method. Overwrite it if you need to provide specific information (like login info or a captcha token) to a webpage in order to access the page properly.
    # save_image(self, url, file_name) - called both to save the logo and screenshot of the curation based on self.logo and self.ss (only if they are set). This by default does NO error checking, so if you want error checking you'll have to overwrite this function.
```

It is recommended that if you add a site definition you create a pull request to this repo so everyone can use it. When pull requesting an update, make sure you also update `defs.txt` to include your definition and update the timestamp at the top of the file using python's built in `time.time()`.

For information on how to use beautifulsoup, check out the [official documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).

For information on how to use fpclib, check out the [official documentation](https://xmgzx.github.io/apps/fpclib/).
