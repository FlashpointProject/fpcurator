# fpcurator
fpcurator is a Python and fpclib powered tool for downloading urls, auto-generating curations, bulk searching for already curated games, and listing tags/platforms/games/animations for Flashpoint.

If you don't want to install python to use fpcurator, check the releases page for a standalone executable.

## Basic Usage

To curate a list of urls, create a text file and put all the urls you want to curate into that file (one per line). After that, you should be able to drag and drop the file onto the AutoCurator script/executable and it will attempt to create partial curations for every file in the list. By default, the curations will be put in a folder named `output`, and any failed urls will be put into a file named `errors.txt`.

If you want to change _how_ the script works, change any of the settings in the `options.ini` file.

## Adding Site Definitions

By default, fpcurator only supports urls from Coolmath Games and Newgrounds. To add support for other pages, first start by creating a file named `<WebsiteName>.py` inside the `sites` folder next to the script/executable and putting this code inside it:

```python
from __main__ import fpclib
# You can put other imports here, but the standalone only supports importing the following other libraries from __main__: sys, glob, os, logging, codecs, json, re, bs4, zipfile. Other imports require python to be installed on the host machine.

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
```

For information on how to use beautifulsoup, check out the [official documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/).
For information on how to use fpclib, check out the [official documentation](https://xmgzx.github.io/apps/fpclib/).