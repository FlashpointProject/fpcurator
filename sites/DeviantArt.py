# DeviantArt definition.

from html import unescape
import fpclib
import re, deviantart

regex = 'deviantart.com'

# Monkey patching because library is missing filename in a def, and mature_content on another
def download_deviation_with_filename(self, deviationid):
    response = self._req('/deviation/download/{}'.format(deviationid))
    return {
        'src' : response['src'],
        'filename' : response['filename']
    }
deviantart.Api.download_deviation = lambda self, deviationid: download_deviation_with_filename(self, deviationid)

def get_gallery_folder(self, username="", folderid="", mode="popular", offset=0, limit=10):
        if not username and self.standard_grant_type == "authorization_code":
            response = self._req('/gallery/{}'.format(folderid), {
                "mode":mode,
                "offset":offset,
                "limit":limit
            })
        else:
            if not username:
                raise DeviantartError("No username defined.")
            else:
                response = self._req('/gallery/{}'.format(folderid), {
                    "username":username,
                    "mode":mode,
                    "offset":offset,
                    "limit":limit,
                    "mature_content":"true"
                })

        deviations = []

        for item in response['results']:
            d = deviantart.deviation.Deviation()
            d.from_dict(item)
            deviations.append(d)

        if "name" in response:
            name = response['name']
        else:
            name = None

        return {
            "results" : deviations,
            "name" : name,
            "has_more" : response['has_more'],
            "next_offset" : response['next_offset']
        }
deviantart.Api.get_gallery_folder = lambda self, username, folderid, offset, limit, mode="popular": get_gallery_folder(self, username, folderid, mode, offset, limit)

DA_CLIENT = None
DESC_REPLACEMENTS = [
    (r'<a(.+?)href="(https:..www.deviantart.com.users.outgoing\?)?(.+?)"(.+?)>',  r'\3'),
    (r'<img (.+?)alt="(.+?)"(.+?)\/>',  r'\2'),
    (r'\s?<br(\s\/)?>', '\n'),
    (r'\s?&nbsp;\s?', ''),
    (r'\n?(<ul>)?<li>', '\n• '),
    (r'<\/?(.+?)>', ''),
    (r'\s?\n\n\n\s?', '\n\n')
]

class DeviantArt(fpclib.Curation):
    def parse(self, soup):
        DA_CLIENT = self.setup_api_from_file('clients.txt')
        
        uuid = soup.find("meta", property="da:appurl")["content"][23:]
        swfurl = DA_CLIENT.download_deviation(uuid)
        try: swfurl = DA_CLIENT.download_deviation(uuid)
        except: raise ValueError(self.src + ': Work is not downloadable. UUID '+ uuid)
        if not swfurl['filename'].endswith('.swf'):
            raise self.InvalidFileError(self.src + " is not a Flash deviation.")
        metadata = DA_CLIENT.get_deviation_metadata(uuid)[0]

        # Get Title
        self.title = metadata['title']

        # Get Logo
        try: self.logo = soup.find("link", {"as":"image"})["href"]
        except: raise

        # Get Developer and set Publisher
        self.dev = str(metadata['author'])
        self.pub = "DeviantArt"
        
        # Get Release Date
        self.date = soup.find("time")['datetime'][:10]

        # Get description
        originalDescription = metadata['description']
        for old, new in DESC_REPLACEMENTS:
            originalDescription = re.sub(old, new, originalDescription)
        originalDescription = unescape(originalDescription).strip('\n').strip()
        self.desc = originalDescription

        self.cmd = "http://api-da.wixmp.com/_api/download/" + swfurl["filename"]
        self.if_url = swfurl['src']
        self.if_filename = swfurl['filename']

        self.platform = "Flash"
        self.app = fpclib.FLASH

    def get_files(self):
        # We will not use the generated link as the launch command, too long
        fpclib.download(self.if_url, loc='api-da.wixmp.com/_api/download/', name=self.if_filename)
    
    def save_image(self, url, file_name):
        # Surround save image with a try catch loop as some logos cannot be gotten.
        try:
            fpclib.download_image(url, name=file_name)
        except: pass

    def setup_api_from_file(self, dafilename):
        # Get Client's id and secret
        client_data = fpclib.read(dafilename)

        try:
            client_id = re.search(r'DEVIANTART_ID=(.*?)(\r\n|$)', client_data).group(1)
            client_secret = re.search(r'DEVIANTART_SECRET=(.*?)(\r\n|$)', client_data).group(1)
        except: raise ValueError(dafilename +' is missing one more parameters (ID=[client_id]\\nSECRET=[client_secret]).')
        
        # Connect to DeviantArt
        try: da = deviantart.Api(client_id, client_secret)
        except: raise ValueError('Could not setup DeviantArt API.')
        return da