# fpcurator
fpcurator is a Python and fpclib powered tool for downloading urls, auto-generating curations, bulk searching for already curated games, and listing tags/platforms/games/animations for Flashpoint.

If you don't want to install python to use fpcurator, check the releases page for a standalone executable.

## Basic Usage

Launch the script or executable and choose a tab. You can also drag and drop a list of urls on to the program (if you are using the standalone or have python configured correctly) to quickly automatically curate them. For more detailed help on how to use the program, see the built-in "Help" button.

If you are looking for command line usage, run `fpcurator --help` or `fpcurator.py --help` in the terminal of your choice.

## Adding Site Definitions

By default, fpcurator only supports urls from Coolmath Games and Newgrounds. To add support for other pages, first start by creating a file named `<WebsiteName>.py` inside the `sites` folder next to the script/executable and putting this code inside it:

```python
from __main__ import fpclib
# You can put other imports here, but the standalone only supports importing the following other libraries from __main__ (Other imports require python to be installed on the host machine):

# os, sys, time, re, json,
# bs4, argparse, codecs, datetime, glob,
# sqlite3, threading, traceback, webbrowser, zipfile,
# difflib, and Levenshtein.


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

For information on how to use beautifulsoup, check out the [official documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
For information on how to use fpclib, check out the [official documentation](https://xmgzx.github.io/apps/fpclib/).