# Best way of hiding the console window
# This should be imported first to get the right console window and hide it early
try:
    from ctypes import windll
    CONSOLE = windll.kernel32.GetConsoleWindow()
except:
    CONSOLE = None
CONSOLE_OPEN = True

def toggle_console():
    if CONSOLE:
        global CONSOLE_OPEN
        if CONSOLE_OPEN:
            windll.user32.ShowWindow(CONSOLE, 0)
            CONSOLE_OPEN = False
        else:
            windll.user32.ShowWindow(CONSOLE, 1)
            CONSOLE_OPEN = True
toggle_console()

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkm
import tkinterweb as tkw

import fpclib
import os, sys, time
import re, json, bs4

import argparse
import codecs
import datetime
import glob
import sqlite3
import threading
import traceback
import urllib
import uuid
import webbrowser
import zipfile

import difflib
try: import Levenshtein
except: pass

from importlib import reload as __reload__
from tooltip import Tooltip

HELP_HTML = """<!doctype html>
<html><body>
    <h1><center>Help</center></h1>
    <p>fpcurator is a collection of tools for performing certain curation tasks easier. There are four sub-tools available. Note that the tool may freeze while performing any task. All debug info on any task is printed to the console that can be shown by clicking "Toggle Log".</p>
    
    <h2>Auto Curator</h2>
    <p>The Auto Curator tool generates a bunch of partial curations based upon a list of urls containing the games to curate. The list of curatable websites is limited the site definitions in the "sites" folder next to the program. To reload all site definitions, press "Reload". To redownload your site definitions, press "Redownload".<br>
    &nbsp;<br>Here are a list of options:
    <ul>
        <li><b>Save</b> - When checked, the auto curator will save it's progress so if it fails from an error, the tool will resume where it left off given the same urls.</li>
        <li><b>Use Titles</b> - When checked, the auto curator will use the titles of curated games instead of randomly generated UUIDs as the names of the folders the curations are put into.</li>
        <li><b>Clear Done URLs</b> - When checked, the auto curator will clear any urls in the list when they are curated. Errored urls will remain in the list.</li>
        <li><b>Notify When Done</b> - When checked, the auto curator will show a message box when it is done curating.</li>
    </ul>
    Here is some basic usage steps:
    <ol>
        <li>Select the options you want, specified by the list above, and set the output directory of these partial curations.</li>
        <li>Paste the urls you want to curate into the text box, one per line.</li>
        <li>Press the "Curate" button to start the curation process.</li>
    </ol>
    </p>
    
    <h2>Download URLs</h2>
    <p>The Download URLs tool downloads and formats a list of files from a list of urls into a collection of organized folders inside the directory specified by "Output Folder". It works in a similar way to cURLsDownloader, but is powered by fpclib. Put all the urls you want to download into the textbox and press "Download".<br>
    &nbsp;<br>Here are a list of options:
    <ul>
        <li><b>Rename "web.archive.org"</b> - When checked, the downloader will put all urls downloaded from the web archive back into their original domains.</li>
        <li><b>Keep URLVars</b> - When checked, the downloader will append url vars present on links being downloaded to the end of the html file. This is only necessary when you have two links to the same webpage that generate different html due to the url vars.</li>
        <li><b>Clear Done URLs</b> - When checked, the downloader will clear any urls in the list when they are downloaded. Errored urls will remain in the list.</li>
        <li><b>Notify When Done</b> - When checked, the downloader will show a message box when it is done downloading.</li>
    </ul>
    Here is some basic usage steps:
    <ol>
        <li>Select the options you want, specified by the list above, and set the output directory of the downloaded folders and files.</li>
        <li>Paste the urls you want to download into the text box, one per line.</li>
        <li>Press the "Download" button to start the download process.</li>
    </ol>
    </p>
    
    <h2>Bulk Search Titles</h2>
    <p>The Bulk Search Titles tool can take a list of titles and a list of urls for those titles and bulk check how likely it is those entries are in Flashpoint. You will need to load the Flashpoint database for it to check through, in addition to providing regexes that will be used to check if entries in Flashpoint have the right Source, Publisher, or Developer that would match a title in the list. Note that this will cache the database for later use, so if you want to reload it you'll need to either delete the file "search/database.tsv" or press "Load" on the database again.<br>
    &nbsp;<br>Here are a list of options:
    <ul>
        <li><b>Priorities</b> - When checked, the searcher will generate a list of numeric priorities and print them into a file named "priorities.txt" next to the program. This is mainly used for copying into a spreadsheet.</li>
        <li><b>Log</b> - When checked, the searcher will generate a more human readable log displaying how likely each it is those games are in Flashpoint.</li>
        <li><b>Strip Subtitles</b> - When checked, titles will be stripped of subtitles when searching for them in Flashpoint.</li>
        <li><b>Exact Url Matches</b> - When unchecked, the searcher will skip checking for exact url matches for a game match in Flashpoint. Normally an exact url match is a very good indicator if a game is curated, but this is optional in case multiple games are on the same url.</li>
        <li><b>Use difflib</b> - When checked, the searcher will use the default python difflib instead of the fast and efficient python-Levenshtein.</li>
    </ul>
    Here is some basic usage steps:
    <ol>
        <li>Select the Flashpoint database, located in your Flashpoint folder under "/Data/flashpoint.sqlite".</li>
        <li>Select the options you want, specified by the list above.</li>
        <li>Type in a source regex that would match the source of any game in Flashpoint that comes from the same location as those in the list. The regex match is case-insensitive.</li>
        <li>Type in a developer/publisher regex that would match the developer/publisher of any game in Flashpoint that comes from the same location as those in the list. Note that developers/publishers are stripped of all non-alphanumeric characters (except semicolons) and are set to lowercase ("Cool-Math-Games.com" becomes "coolmathgamescom"), so the match is case-insensitive.</li>
        <li>Copy and paste the <b>TITLES</b> of entries to search with in the <b>LEFT</b> box, one per line.</li>
        <li>Copy and paste the <b>URLS</b> of entries to search with in the <b>RIGHT</b> box, one per line.</li>
        <li>Press the "Search" button to initiate the search. When the search is done the generated "log.txt" and/or "priorities.txt" files will be automatically opened if you chose to generate them.</li>
    </ol>
    Here's what each of the priorities mean:
    <ul>
    <table>
        <tr><td><b> -1        </b></td><td>Duplicate</td></tr>
        <tr><td><b>  5        </b></td><td>Exact url matches with the source of a game in Flashpoint</td></tr>
        <tr><td><b>  4.9      </b></td><td>Exact url matches ignoring protocol and extra source data (like Via. Wayback)</td></tr>
        <tr><td><b>  4.8      </b></td><td>Title matches with a game that is from the same source/developer/publisher</td></tr>
        <tr><td><b>  4.3      </b></td><td>Title starts the title of a game from the same source/developer/publisher (and is >10 characters long)</td></tr>
        <tr><td><b>  4.0      </b></td><td>Title matches with a game in Flashpoint (may not be accurate for common names of games like Chess)</td></tr>
        <tr><td><b>  3.9      </b></td><td>Title starts the title of a game in Flashpoint (and is >10 characters long)</td></tr>
        <tr><td><b>  3.8      </b></td><td>Title is in the title of a game in Flashpoint (and is >10 characters long)</td></tr>
        <tr><td><b>  3.6-3.8  </b></td><td>This game has a very high (>95%) metric, meaning it matches with another title that probably has 1 or 2 letters different.</td></tr>
        <tr><td><b>  3-3.6    </b></td><td>This game has a medium to high metric (85-95%), meaning it kind of matches with games in Flashpoint but not really.</td></tr>
        <tr><td><b>  1-3      </b></td><td>Basically every other metric (60-85%). 60% is the highest match of garbage letters.</td></tr>
    </table>
    </ul>
    </p>
    
    <h2>Wiki Data</h2>
    <p>The Wiki Data tool provides you with the ability to get a list of all Tags, Platforms, Games, or Animations in Flashpoint. Just select the given page you want the data of and press "Find".</p>
</body></html>"""

HEADINGS = ['TABLE OF CONTENTS', 'SUMMARY', 'DUPLICATE NAMES', 'DEFINITELY IN FLASHPOINT', 'PROBABLY IN FLASHPOINT', 'MAYBE IN FLASHPOINT', 'PROBABLY NOT IN FLASHPOINT', 'DEFINITELY NOT IN FLASHPOINT']
TEXTS = {
    'header': 'Search performed on %s\nDISCLAIMER: ALWAYS CHECK THE MASTER LIST AND DISCORD CHANNEL BEFORE CURATING, EVEN IF SOMETHING IS LISTED HERE AS NOT CURATED\n\n',
    'divider': '--------------- %s ---------------\n',
    'line': '-----------------------------------\n',
    'tbc.note': 'Note: use CTRL+F to find these sections quickly.\n\n',
    'info.numerics': ' (%d - %.3f%%)',
    'sum.totalgames': '%d Games Total',
    'sum.titlematch': '%d games match titles',
    'sum.sourcematch': '%d games are from the same source/developer/publisher as the list',
    'sum.either': '%d games match either query',
    'sum.lowmetric': '%d games have a very low similarity metric',
    'sum.priority': '%d games (%.3f%%) probably need curating',
    'sum.priority2': '%d games (%.3f%%) definitely need curating',
    'dup.note': 'These are a list of games that have been omitted from the search because they share the same name with another game in the list',
    'p5.exacturl': 'Exact url matches',
    'p5.partialurl': 'Exact url matches ignoring protocol and extra source data (like Via. Wayback)',
    'p5.titleandsdp': 'Title matches with a game that is from the same source/developer/publisher',
    'p4.titlestartsandssdp': 'Title starts the title of a game from the same source/developer/publisher (and is >10 characters long)',
    'p4.titleonly': 'Title matches',
    'p4.titlestartstitle': 'Title is in the title of a game in Flashpoint (and is >10 characters long)',
    'p4.titleintitle': 'Title is in the title of a game in Flashpoint (and is >10 characters long)',
    'p4.highmetric': 'Has a high similarity metric (>95%)',
    'p3.leftovers': 'Leftovers',
    'p3.leftovers2': 'These are the games that didn\'t match any query',
    'p2.lowmetric': 'Has a low similarity metric (<85%)',
    'p1.verylowmetric': 'Has a very low similarity metric (<75%)'
}

TITLE = "fpcurator v1.4.1"
ABOUT = "Created by Zach K - v1.4.1"

SITES_FOLDER = "sites"

fpclib.DEBUG_LEVEL = 4

AM_PATTERN = re.compile('[\W_]+')
AMS_PATTERN = re.compile('([^\w;]|_)+')

MAINFRAME = None

DEFS_GOTTEN = False

def set_entry(entry, data):
    entry.delete(0, "end")
    entry.insert(0, data)

def printfl(data):
    print(data, end="")
    sys.stdout.flush()

frozen_ui = False
def freeze(subtitle):
    global frozen_ui
    frozen_ui = True
    MAINFRAME.freeze(subtitle)

def unfreeze():
    global frozen_ui
    frozen_ui = False

def edit_file(file):
    webbrowser.open(file)

class Mainframe(tk.Tk):
    def __init__(self):
        # Create window
        super().__init__()
        self.minsize(695, 650)
        self.title(TITLE)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        
        # Add tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=5, pady=5)
        self.tabs.bind("<<NotebookTabChanged>>", self.tab_change)
        
        self.autocurator = AutoCurator()
        self.downloader = Downloader()
        self.searcher = Searcher()
        self.lister = Lister()
        
        self.tabs.add(self.autocurator, text="Auto Curator")
        self.tabs.add(self.downloader, text="Download URLs")
        self.tabs.add(self.searcher, text="Bulk Search Titles")
        self.tabs.add(self.lister, text="Wiki Data")
        
        # Add help and about label
        bframe = tk.Frame(self)
        bframe.pack(expand=False, padx=5, pady=(0, 5))
        
        label = ttk.Label(bframe, text=ABOUT)
        label.pack(side="left")
        help_button = ttk.Button(bframe, text="Help", command=self.show_help)
        help_button.pack(side="left", padx=5)
        log_button = ttk.Button(bframe, text="Toggle Log", command=toggle_console)
        log_button.pack(side="left")
        
        # Add debug level entry
        self.debug_level = tk.StringVar()
        self.debug_level.set(str(fpclib.DEBUG_LEVEL))
        self.debug_level.trace("w", self.set_debug_level)
        dlabel = ttk.Label(bframe, text=" Debug Level: ")
        dlabel.pack(side="left")
        debug_level = ttk.Entry(bframe, textvariable=self.debug_level)
        debug_level.pack(side="left")
        
        # Exists to prevent more than one of a window from opening at a time
        self.help = None
        
        # Load GUI state from last close
        self.load()
        
        # Get autocurator site definitions
        self.autocurator.reload()
        
        # Setup timer for unfreeze events
        self.frozen = False
        self.after(100, self.check_freeze)
    
    def tab_change(self, event):
        tab = self.tabs.select()
        if tab == ".!autocurator":
            self.autocurator.stxt.txt.focus_set()
        elif tab == ".!downloader":
            self.downloader.stxt.txt.focus_set()
        elif tab == ".!searcher":
            self.searcher.stxta.txt.focus_set()
    
    def check_freeze(self):
        if self.frozen and not frozen_ui: self.unfreeze()
        self.after(100, self.check_freeze)
    
    def freeze(self, subtitle):
        self.autocurator.curate_btn["state"] = "disabled"
        self.autocurator.reload_btn["state"] = "disabled"
        self.downloader.download_btn["state"] = "disabled"
        self.searcher.load_btn["state"] = "disabled"
        self.searcher.search_btn["state"] = "disabled"
        self.lister.find_btn["state"] = "disabled"
        #self.lister.stxt.txt["state"] = "disabled"
        
        self.title(TITLE + " - " + subtitle)
        
        self.frozen = True
    
    def unfreeze(self):
        self.autocurator.curate_btn["state"] = "normal"
        self.autocurator.reload_btn["state"] = "normal"
        self.downloader.download_btn["state"] = "normal"
        self.searcher.load_btn["state"] = "normal"
        self.searcher.search_btn["state"] = "normal"
        self.lister.find_btn["state"] = "normal"
        #self.lister.stxt.txt["state"] = "normal"
        
        self.title(TITLE)
        
        self.frozen = False
    
    def show_help(self):
        if not self.help:
            self.help = Help(self)
    
    def set_debug_level(self, name, index, mode):
        dl = self.debug_level.get()
        try:
            fpclib.DEBUG_LEVEL = int(dl)
        except ValueError:
            fpclib.DEBUG_LEVEL = -1
    
    def exit_window(self):
        if not frozen_ui:
            if not CONSOLE_OPEN: toggle_console()
            # TODO: Python can't stop a thread easily, so make sure nothing is running before closing.
            self.save()
            self.destroy()
    
    def save(self):
        autocurator = {}
        downloader = {}
        searcher = {}
        
        data = {"autocurator": autocurator, "downloader": downloader, "searcher": searcher, "debug_level": self.debug_level.get(), "tab": self.tabs.select()}
        
        # Save autocurator data
        autocurator["output"] = self.autocurator.output.get()
        
        autocurator["save"] = self.autocurator.save.get()
        autocurator["silent"] = self.autocurator.silent.get()
        autocurator["titles"] = self.autocurator.titles.get()
        autocurator["clear"] = self.autocurator.clear.get()
        autocurator["show_done"] = self.autocurator.show_done.get()
        
        autocurator["urls"] = self.autocurator.stxt.txt.get("0.0", "end").strip()
        
        # Save downloader data
        downloader["output"] = self.downloader.output.get()
        
        downloader["original"] = self.downloader.original.get()
        downloader["keep_vars"] = self.downloader.keep_vars.get()
        downloader["clear"] = self.downloader.clear.get()
        downloader["show_done"] = self.downloader.show_done.get()
        
        downloader["urls"] = self.downloader.stxt.txt.get("0.0", "end").strip()
        
        # Save searcher data
        searcher["database"] = self.searcher.database.get()
        searcher["sources"] = self.searcher.sources.get()
        searcher["devpubs"] = self.searcher.devpubs.get()
        
        searcher["priorities"] = self.searcher.priorities.get()
        searcher["log"] = self.searcher.log.get()
        searcher["strip"] = self.searcher.strip.get()
        searcher["exact_url"] = self.searcher.exact_url.get()
        searcher["difflib"] = self.searcher.difflib.get()
        
        searcher["titles"] = self.searcher.stxta.txt.get("0.0", "end").strip()
        searcher["urls"] = self.searcher.stxtb.txt.get("0.0", "end").strip()
        
        with open("data.json", "w") as file: json.dump(data, file)
    
    def load(self):
        try:
            with open("data.json", "r") as file: data = json.load(file)
            
            # Set basic data
            self.debug_level.set(data["debug_level"])
            self.tabs.select(data["tab"])
            
            
            autocurator = data["autocurator"]
            downloader = data["downloader"]
            searcher = data["searcher"]
            
            # Load autocurator data
            set_entry(self.autocurator.output, autocurator["output"])
            
            self.autocurator.save.set(autocurator["save"])
            self.autocurator.silent.set(autocurator["silent"])
            self.autocurator.titles.set(autocurator["titles"])
            self.autocurator.clear.set(autocurator["clear"])
            self.autocurator.show_done.set(autocurator["show_done"])
            
            txt = self.autocurator.stxt.txt
            txt.delete("0.0", "end")
            txt.insert("1.0", autocurator["urls"])
            
            # Save downloader data
            set_entry(self.downloader.output, downloader["output"])
            
            self.downloader.original.set(downloader["original"])
            self.downloader.keep_vars.set(downloader["keep_vars"])
            self.downloader.clear.set(downloader["clear"])
            self.downloader.show_done.set(downloader["show_done"])
            
            txt = self.downloader.stxt.txt
            txt.delete("0.0", "end")
            txt.insert("1.0", downloader["urls"])
            
            # Save searcher data
            set_entry(self.searcher.database, searcher["database"])
            set_entry(self.searcher.sources, searcher["sources"])
            set_entry(self.searcher.devpubs, searcher["devpubs"])
            
            self.searcher.priorities.set(searcher["priorities"])
            self.searcher.log.set(searcher["log"])
            self.searcher.strip.set(searcher["strip"])
            self.searcher.exact_url.set(searcher["exact_url"])
            self.searcher.difflib.set(searcher["difflib"])
            
            txt = self.searcher.stxta.txt
            txt.delete("0.0", "end")
            txt.insert("1.0", searcher["titles"])
            
            txt = self.searcher.stxtb.txt
            txt.delete("0.0", "end")
            txt.insert("1.0", searcher["urls"])
            
        except (FileNotFoundError, KeyError): pass

class Help(tk.Toplevel):
    def __init__(self, parent):
        # Create window
        super().__init__(bg="white")
        self.title(TITLE + " - Help")
        self.minsize(445, 400)
        self.geometry("745x700")
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.parent = parent
        
        # Create htmlframe for displaying help information
        txt = tkw.HtmlFrame(self)
        txt.load_html(HELP_HTML)
        txt.pack(expand=True, fill="both")
    
    def exit_window(self):
        self.parent.help = None
        self.destroy()

class AutoCurator(tk.Frame):
    def __init__(self):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(fill="x", padx=5, pady=5)
        
        # Create output folder and curate button
        olabel = tk.Label(tframe, bg="white", text="Output Folder:")
        olabel.pack(side="left", padx=5)
        self.output = ttk.Entry(tframe)
        self.output.insert(0, "output")
        self.output.pack(side="left", fill="x", expand=True)
        folder = ttk.Button(tframe, text="...", width=3, command=self.folder)
        folder.pack(side="left")
        self.curate_btn = ttk.Button(tframe, text="Curate", command=self.curate)
        self.curate_btn.pack(side="left", padx=5)
        
        # Create checkboxes
        cframe = tk.Frame(self, bg="white")
        cframe.pack(padx=5)
        
        self.save = tk.BooleanVar()
        self.save.set(True)
        self.silent = tk.BooleanVar()
        self.silent.set(True)
        self.titles = tk.BooleanVar()
        self.titles.set(True)
        self.clear = tk.BooleanVar()
        self.clear.set(True)
        self.show_done = tk.BooleanVar()
        self.show_done.set(True)
        
        save = tk.Checkbutton(cframe, bg="white", text='Save', var=self.save)
        save.pack(side="left", padx=5)
        #silent = tk.Checkbutton(cframe, bg="white", text="Silent", var=self.silent)
        #silent.pack(side="left", padx=5)
        titles = tk.Checkbutton(cframe, bg="white", text="Use Titles", var=self.titles)
        titles.pack(side="left")
        clear = tk.Checkbutton(cframe, bg="white", text="Clear Done URLs", var=self.clear)
        clear.pack(side="left", padx=5)
        show_done = tk.Checkbutton(cframe, bg="white", text='Notify When Done', var=self.show_done)
        show_done.pack(side="left")
        
        Tooltip(save, text="When checked, the auto curator will save it's progress so if it fails from an error, the tool will resume where it left off given the same urls.")
        #Tooltip(silent, text="")
        Tooltip(titles, text="When checked, the auto curator will use the titles of curated games instead of randomly generated UUIDs as the names of the folders the curations are put into.")
        Tooltip(clear, text="When checked, the auto curator will clear any urls in the list when they are curated. Errored urls will remain in the list.")
        Tooltip(show_done, text="When checked, the auto curator will show a message box when it is done curating.")
        
        # Create site definition display
        dframe = tk.Frame(self, bg="white")
        dframe.pack()
        
        self.defcount = tk.StringVar()
        self.defcount.set("0 site definitions found")
        defcount = tk.Label(dframe, bg="white", textvariable=self.defcount)
        defcount.pack(side="left")
        
        self.reload_btn = ttk.Button(dframe, text="Reload", command=self.reload)
        self.reload_btn.pack(side="left", padx=5)
        self.update_btn = ttk.Button(dframe, text="Redownload", command=self.update_online)
        self.update_btn.pack(side="left")
        
        # Create panel for inputting urls
        lbl = tk.Label(self, bg="white", text="  Put URLs to curate in this box:")
        lbl.pack(fill="x")
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=5)
    
    def folder(self):
        # For changing the output folder
        folder = tkfd.askdirectory()
        if folder:
            self.output.delete(0, "end")
            self.output.insert(0, folder)
    
    def download_defs(data, silent=False):
        print("[INFO] Downloading site definitions from online")
        global DEFS_GOTTEN
        DEFS_GOTTEN = True

        # Delete sites folder if it exists
        fpclib.delete(SITES_FOLDER)
        # Get defs.txt
        fpclib.write(SITES_FOLDER+"/defs.txt", data)
        # Get definition file names from url
        files = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")[1:]
        # Compile file names into urls to download
        urls = ["https://github.com/FlashpointProject/fpcurator/raw/main/sites/" + f for f in files]
        # Download urls
        for i in range(len(urls)):
            fpclib.write(SITES_FOLDER+"/"+files[i], fpclib.read_url(urls[i]))
        
        # Tell the user to restart the program (because python doesn't like to load newly created python files as modules)
        if not silent:
            tkm.showinfo(message="Definitions downloaded. Restart the program to load them. The program will now exit.")
            sys.exit(0)

    def get_defs(silent=False):
        # Query to download site definitions from online.
        global DEFS_GOTTEN
        if not silent and not DEFS_GOTTEN:
            DEFS_GOTTEN = True
            data, odata = None, None
            try:
                data = fpclib.read_url("https://github.com/FlashpointProject/fpcurator/raw/main/sites/defs.txt")
                odata = fpclib.read(SITES_FOLDER+"/defs.txt")
            except: pass

            if data != odata and tkm.askyesno(message="The Auto Curator's site definitions are out of date, would you like to redownload them from online? (you won't be able to use the Auto Curator fully without them)"):
                AutoCurator.download_defs(data, silent)

        defs = []
        priorities = {}
    
        # Parse for site definitions
        fpclib.debug('Parsing for site definitions', 1)
        fpclib.TABULATION += 1
        sys.path.insert(0, SITES_FOLDER)
        for py_file in glob.glob(os.path.join(SITES_FOLDER, '*.py')):
            try:
                name = py_file[py_file.replace('\\', '/').rfind('/')+1:-3]
                m = __import__(name)
                __reload__(m)
                
                priorities[name] = m.priority if hasattr(m, "priority") else 0
                
                defs.append((m.regex, getattr(m, name)))
                fpclib.debug('Found class "{}"', 1, name)
            except Exception as e:
                fpclib.debug('Skipping class "{}", error:', 1, name)
                print()
                traceback.print_exc()
                print()
        sys.path.pop(0)
        
        fpclib.TABULATION -= 1
        
        # Print count of site definitions
        if defs: defs.sort(key=lambda x: priorities[x[1].__name__], reverse=True)
        else:
            if not silent:
                fpclib.debug('No valid site-definitions were found', 1)
        
        return defs
    
    def reload(self):
        # Initialize defs and priorities
        self.defs = AutoCurator.get_defs()
        self.defcount.set(f"{len(self.defs)} site defintitions found")
    
    def update_online(self):
        # Get defs and download
        data = fpclib.read_url("https://github.com/FlashpointProject/fpcurator/raw/main/sites/defs.txt")
        AutoCurator.download_defs(data, False)
    
    def s_curate(output, defs, urls, titles, save, ignore_errs):
        cwd = os.getcwd()
        fpclib.make_dir(output, True)
        errs = fpclib.curate_regex(urls, defs, use_title=titles, save=save, ignore_errs=ignore_errs)
        os.chdir(cwd)
        
        return errs
    
    def i_curate(self):
        txt = self.stxt.txt
        # Get urls and curate them with all site definitions
        urls = [i.strip() for i in txt.get("0.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
        
        errs = AutoCurator.s_curate(self.output.get(), self.defs, urls, self.titles.get(), self.save.get(), self.silent.get())
    
        if self.show_done.get():
            if errs:
                if len(errs) == len(urls):
                    tkm.showerror(message=f"All {len(errs)} urls could not be curated.")
                else:
                    tkm.showinfo(message=f"Successfully curated {len(urls)-len(errs)}/{len(urls)} urls.\n\n{len(errs)} urls could not be downloaded.")
            else:
                tkm.showinfo(message=f"Successfully curated {len(urls)} urls.")
            
        if self.clear.get():
            txt.delete("0.0", "end")
            if errs: txt.insert("1.0", "\n".join([i for i, e, s in errs]))
        
        unfreeze()
    
    def curate(self):
        freeze("AutoCurating URLs")
        threading.Thread(target=self.i_curate, daemon=True).start()

class Downloader(tk.Frame):
    def __init__(self):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(fill="x", padx=5, pady=5)
        
        # Create output folder and curate button
        olabel = tk.Label(tframe, bg="white", text="Output Folder:")
        olabel.pack(side="left", padx=5)
        self.output = ttk.Entry(tframe)
        self.output.insert(0, "output")
        self.output.pack(side="left", fill="x", expand=True)
        folder = ttk.Button(tframe, text="...", width=3, command=self.folder)
        folder.pack(side="left")
        self.download_btn = ttk.Button(tframe, text="Download", command=self.download)
        self.download_btn.pack(side="left", padx=5)
        
        # Create checkboxes
        cframe = tk.Frame(self, bg="white")
        cframe.pack(padx=5)
        #c2frame = tk.Frame(self, bg="white")
        #c2frame.pack(padx=5, pady=5)
        
        self.keep_vars = tk.BooleanVar()
        self.clear = tk.BooleanVar()
        self.clear.set(True)
        self.show_done = tk.BooleanVar()
        self.show_done.set(True)

        self.original = tk.BooleanVar()
        self.original.set(True)
        self.replace_https = tk.BooleanVar()
        self.replace_https.set(True)
        
        original = tk.Checkbutton(cframe, bg="white", text='Rename "web.archive.org"', var=self.original)
        original.pack(side="left")
        keep_vars = tk.Checkbutton(cframe, bg="white", text="Keep URLVars", var=self.keep_vars)
        keep_vars.pack(side="left", padx=5)
        clear = tk.Checkbutton(cframe, bg="white", text="Clear Done URLs", var=self.clear)
        clear.pack(side="left")
        show_done = tk.Checkbutton(cframe, bg="white", text='Notify When Done', var=self.show_done)
        show_done.pack(side="left", padx=5)
        
        Tooltip(original, text="When checked, the downloader will put all urls downloaded from the web archive back into their original domains.")
        Tooltip(keep_vars, text="When checked, the downloader will append url vars present on links being downloaded to the end of the html file. This is only necessary when you have two links to the same webpage that generate different html due to the url vars.")
        Tooltip(clear, text="When checked, the downloader will clear any urls in the list when they are downloaded. Errored urls will remain in the list.")
        Tooltip(show_done, text="When checked, the downloader will show a message box when it is done downloading.")
        
        # Create panel for inputting urls to download
        lbl = tk.Label(self, bg="white", text="  Put URLs to download in this box:")
        lbl.pack(fill="x")
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=5)
    
    def folder(self):
        # For changing the output directory
        folder = tkfd.askdirectory()
        if folder:
            self.output.delete(0, "end")
            self.output.insert(0, folder)
    
    def i_download(self):
        txt = self.stxt.txt
        try:
            links = [i.strip() for i in txt.get("0.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
            if links:
                errs = fpclib.download_all(links, self.output.get() or "output", not self.original.get(), self.keep_vars.get(), True)
                if self.show_done.get():
                    if errs:
                        if len(errs) == len(links):
                            tkm.showerror(message=f"All {len(errs)} urls could not be downloaded.")
                        else:
                            tkm.showinfo(message=f"Successfully downloaded {len(links)-len(errs)}/{len(links)} files.\n\n{len(errs)} urls could not be downloaded.")
                    else:
                        tkm.showinfo(message=f"Successfully downloaded {len(links)} files.")
                    
                if self.clear.get():
                    txt.delete("0.0", "end")
                    if errs:
                        txt.insert("1.0", "\n".join([i for i, e in errs]))
            else:
                tkm.showinfo(message="You must specify at least one url to download.")
        except Exception as e:
            print("[ERR]  Failed to download urls, err ")
            traceback.print_exc()
            tkm.showerror(message=f"Failed to download urls.\n{e.__class__.__name__}: {str(e)}")
        
        unfreeze()
    
    def download(self):
        freeze("Downloading URLs")
        threading.Thread(target=self.i_download, daemon=True).start()

class Searcher(tk.Frame):
    def __init__(self):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(fill="x", padx=5, pady=5)
        
        # Create options for locating the Flashpoint database
        dlabel = tk.Label(tframe, bg="white", text="Database:")
        dlabel.pack(side="left", padx=5)
        self.database = ttk.Entry(tframe)
        self.database.pack(side="left", fill="x", expand=True)
        db = ttk.Button(tframe, text="...", width=3, command=self.get_database)
        db.pack(side="left", padx=(0, 5))
        self.load_btn = ttk.Button(tframe, text="Load", command=self.load)
        self.load_btn.pack(side="left")
        self.search_btn = ttk.Button(tframe, text="Search", command=self.search)
        self.search_btn.pack(side="left", padx=5)
        
        # Create entries for regexs
        rframe = tk.Frame(self, bg="white")
        rframe.pack(fill="x", padx=5)
        
        slabel = tk.Label(rframe, bg="white", text="Source Regex:")
        slabel.pack(side="left", padx=5)
        self.sources = ttk.Entry(rframe)
        self.sources.pack(side="left", expand=True, fill="x")
        dplabel = tk.Label(rframe, bg="white", text="Dev/Pub Regex:")
        dplabel.pack(side="left", padx=5)
        self.devpubs = ttk.Entry(rframe)
        self.devpubs.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        # Create checkboxes
        cframe = tk.Frame(self, bg="white")
        cframe.pack(padx=5)
        
        self.priorities = tk.BooleanVar()
        self.priorities.set(True)
        self.log = tk.BooleanVar()
        self.log.set(True)
        self.strip = tk.BooleanVar()
        self.exact_url = tk.BooleanVar()
        self.exact_url.set(True)
        self.difflib = tk.BooleanVar()
        
        priorities = tk.Checkbutton(cframe, bg="white", text="Priorities", var=self.priorities)
        priorities.pack(side="left")
        log = tk.Checkbutton(cframe, bg="white", text="Log", var=self.log)
        log.pack(side="left", padx=5)
        strip = tk.Checkbutton(cframe, bg="white", text="Strip Subtitles", var=self.strip)
        strip.pack(side="left")
        exact_url = tk.Checkbutton(cframe, bg="white", text="Exact Url Matches", var=self.exact_url)
        exact_url.pack(side="left", padx=5)
        difflib = tk.Checkbutton(cframe, bg="white", text="Use difflib", var=self.difflib)
        difflib.pack(side="left")
        
        Tooltip(priorities, text='When checked, the searcher will generate a list of numeric priorities and print them into a file named "priorities.txt" next to the program. This is mainly used for copying into a spreadsheet.')
        Tooltip(log, text="When checked, the searcher will generate a more human readable log displaying how likely each it is those games are in Flashpoint.")
        Tooltip(strip, text="When checked, titles will be stripped of subtitles when searching for them in Flashpoint.")
        Tooltip(exact_url, text='When unchecked, the searcher will skip checking for exact url matches for a game match in Flashpoint. Normally an exact url match is a very good indicator if a game is curated, but this is optional in case multiple games are on the same url.')
        Tooltip(difflib, text="When checked, the searcher will use the default python library difflib instead of the fast and efficient python-Levenshtein.")
        
        # Panels
        lbl = tk.Label(self, bg="white", text="Put TITLES in the LEFT box and URLS in the RIGHT.")
        lbl.pack(fill="x")
        txts = tk.Frame(self, bg="white")
        txts.pack(expand=True, fill="both", padx=5, pady=(0, 5))
        
        self.stxta = ScrolledText(txts, width=10, height=10, wrap="none")
        self.stxta.pack(side="left", expand=True, fill="both")
        self.stxtb = ScrolledText(txts, width=10, height=10, wrap="none")
        self.stxtb.pack(side="left", expand=True, fill="both")
    
    def get_database(self):
        # For changing the flashpoint database location
        db = tkfd.askopenfilename(filetypes=[("SQLite Database", "*.sqlite")])
        if db:
            self.database.delete(0, "end")
            self.database.insert(0, db)
    
    def s_load(dbloc, silent=False):
        try:
            # Acquire the database!
            db = sqlite3.connect(dbloc)
            c = db.cursor()
            
            # Next, get all required data through a query
            c.execute("select id, lower(title), lower(platform), lower(alternateTitles), lower(developer), lower(publisher), source, language, title from game")
            data = c.fetchall()
            # Then format the data
            for i in range(len(data)):
                datal = data[i]
                data[i] = "\t".join((
                    datal[0], # ID
                    AM_PATTERN.sub('', datal[1]), # Title
                    AM_PATTERN.sub('', datal[2]), # Platform
                    AMS_PATTERN.sub('', datal[3]), # Alternate Titles
                    AMS_PATTERN.sub('', datal[4]), # Developer
                    AMS_PATTERN.sub('', datal[5]), # Publisher
                    datal[6], # Source
                    datal[7], # Language
                    datal[8] # Real Title
                ))
            
            fpclib.write("search/database.tsv", "\n".join(data))
            return True
        except Exception as e:
            print("[ERR]  Failed to load database, err ")
            traceback.print_exc()
            if not silent: tkm.showerror(message=f"Failed to load database. Ensure the the database provided is valid.\n{e.__class__.__name__}: {str(e)}")
        finally:
            if not silent: unfreeze()
        
        return False
    
    def load(self):
        freeze("Loading Database")
        threading.Thread(target=lambda: Searcher.s_load(self.database.get(), False), daemon=True).start()
    
    def search(self):
        freeze("Bulk Searching")
        # Get input data
        try:
            txta = self.stxta.txt
            txtb = self.stxtb.txt
            
            titles = [i.strip() for i in txta.get("0.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
            urls = [i.strip() for i in txtb.get("0.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
            #if urls and len(titles) != len(urls):
            
            # Get options
            PRIORITIES = self.priorities.get()
            LOG = self.log.get()
            STRIP_SUBTITLES = self.strip.get()
            EXACT_URL_CHECK = self.exact_url.get()
            DIFFLIB = self.difflib.get()
            
            threading.Thread(target=lambda: Searcher.s_search(titles, urls, self.database.get(), self.sources.get(), self.devpubs.get(), PRIORITIES, LOG, STRIP_SUBTITLES, EXACT_URL_CHECK, DIFFLIB), daemon=True).start()
        except Exception as e:
            print("Failed to start search, err ")
            traceback.print_exc()
            tkm.showerror(message=f"Failed to get input data.\n{e.__class__.__name__}: {str(e)}")
    
    def s_search(titles, urls, dbloc, src_regex_str, dp_regex_str, PRIORITIES, LOG, STRIP_SUBTITLES, EXACT_URL_CHECK, DIFFLIB, silent_=False):
        try:
            period = time.time()
            printfl('[INFO] Parsing input data...')
            
            if len(titles) != len(urls):
                print('Failed (input count mismatch)')
                if not silent: tkm.showerror(message=f"Input data count mismatch: # of titles is {len(titles)}, while # of urls is {len(urls)}.")
                return
            input_count = len(titles)
            if input_count == 0:
                print('Failed (no data)')
                if not silent: tkm.showerror(message=f"No input data to search with; you must provide at least one title and url to search with.")
                return
            
            # Format input
            for i in range(input_count):
                title = titles[i]
                if STRIP_SUBTITLES:
                    colon = title.find(':')
                    title = title[0, colon]
                titles[i] = AM_PATTERN.sub('', title).lower()
            
            # Get source regex
            try: src_regex = re.compile(src_regex_str, re.I)
            except:
                print('Failed (incorrect source regex)')
                if not silent: tkm.showerror(message=f"Your source regex is formatted incorrectly.")
                return
            # Get devpubs regex
            try: dp_regex = re.compile(dp_regex_str, re.I)
            except:
                print('Failed (incorrect dev/pub regex)')
                if not silent: tkm.showerror(message=f"Your developer/publisher regex is formatted incorrectly.")
                return
            
            print('Done (%.3f secs)' % (time.time() - period))
            
            # Check for duplicates
            period = time.time()
            print('[INFO] Checking for duplicates')
            duplicates = set()
            for i, title in enumerate(titles):
                print('         %d/%d - %d%% Complete' % (i, input_count, int(100 * i / input_count)), end='\r')
                if titles.count(title) > 1: duplicates.add(i)
            
            print('         %d/%d - %d%% Complete (%.3f secs)' % (input_count, input_count, 100, time.time() - period))
            print('         %d duplicates found.' % (len(duplicates)))
            
            
            
            # Load the database
            period = time.time()
            printfl('[INFO] Loading database...')
            fpclib.DEBUG_LEVEL, dl = 0, fpclib.DEBUG_LEVEL
            try:
                raw_data = fpclib.read("search/database.tsv")
            except:
                if dbloc:
                    try:
                        print('Failed')
                        printfl('[INFO] Attempting to load from external database...')
                        if Searcher.s_load(dbloc, silent_): raw_data = fpclib.read("search/database.tsv")
                    except Exception as e:
                        print("Failed (bad read), err")
                        traceback.print_exc()
                        if not silent_: tkm.showerror(message=f"Failed to read database.\n{e.__class__.__name__}: {str(e)}")
                        return
                else:
                    print('Failed (No database)')
                    return
            fpclib.DEBUG_LEVEL = dl
            
            # Split database into full data
            data = [i.split("\t") for i in raw_data.split("\n")]
            data_count = len(data)
            # Further split alternate titles, developers, and publishers
            # Could probably be more optimized, but whatever
            for i in range(len(data)):
                for j in range(3, 6):
                    data[i][j] = data[i][j].split(';')
            print('Done (%.3f secs)' % (time.time() - period))
            
            
            
            # Perform a quick summary check on the data
            period = time.time()
            print('[INFO] Performing summary check')
            
            title_match_count = 0
            sdp_match_count = 0
            title_or_sdp_match_count = 0
            
            sdp_matches = set()
            data_titles = set()
            data_sources = set()
            
            def check_sdp_match(entry):
                if entry[6]: # Check source if available
                    if src_regex.fullmatch(entry[6]): return True
                if entry[4]: # Check developer if available
                    for dev in entry[4]:
                        if dp_regex.fullmatch(dev): return True
                if entry[5]: # Check publisher if available
                    for pub in entry[5]:
                        if dp_regex.fullmatch(pub): return True
                
                return False # This entry does not match with anything
            
            def check_title_match(entry):
                if entry[1]: # Check title if available (if it's not someone did something wrong)
                    if entry[1] in titles: return True
                if entry[3] and entry[3] != [""]: # Check alternate titles if available
                    for alt in entry[3]:
                        if alt in titles: return True
                
                return False # This entry does not match with anything
            
            for i, entry in enumerate(data):
                print('         %d/%d - %d%% Complete' % (i, data_count, int(100 * i / data_count)), end='\r')
                
                sdp_match = check_sdp_match(entry)
                title_match = check_title_match(entry)
                
                if title_match: title_match_count += 1 # If title matches, add to counter
                if sdp_match: # If src, dev, or pub match
                    # Add to counter
                    sdp_match_count += 1
                    # Add titles to list for showing later
                    sdp_matches.add(entry[1])
                    if entry[3] and entry[3] != [""]:
                        for t in entry[3]: sdp_matches.add(t)
                
                if title_match or sdp_match: title_or_sdp_match_count += 1
                
                # Add this entry's titles to data_titles
                data_titles.add(entry[1])
                if entry[3] and entry[3] != [""]:
                    for t in entry[3]: data_titles.add(t)
                
                # Add this entry's source to data_sources
                if entry[6]: data_sources.add(entry[6])
            
            print('         %d/%d - %d%% Complete (%.3f secs)' % (data_count, data_count, 100, time.time() - period))
            print('         %d games match title' % (title_match_count))
            print('         %d games match source/dev/pub' % (sdp_match_count))
            print('         %d games match either' % (title_or_sdp_match_count))
            
            
            
            # Now comes the time to roll up our sleeves and search through the data
            period = time.time()
            period_item = time.time()
            print('[INFO] Performing main search')
            
            data_sources_str = "\n"+"\n".join(data_sources)+"\n"
            sdp_matches_str = "\n"+"\n".join(sdp_matches)+"\n"
            
            duplicate = []
            
            url_matches = []
            partial_url_matches = []
            title_and_sdp_matches = []
            
            title_starts_title_and_sdp_matches = []
            title_matches = []
            title_starts_title = []
            title_in_title = []
            high_metric = []
            
            leftovers = []
            
            low_metric = []
            
            very_low_metric = []
            
            priorities = []
            
            for item in range(input_count):
                print('         %d/%d - %d%% Complete (last took %.3f secs)' % (item, input_count, int(100 * item / input_count), time.time() - period_item), end='\r')
                period_item = time.time()
                
                # Get title and url
                title = titles[item]
                url = urls[item]
                line = title + "\t" + url
                title_is_long = len(title) > 10
                
                # Duplicates get thrown out
                if item in duplicates:
                    duplicate.append(line)
                    priorities.append('-1.0')
                    continue
                
                if url and EXACT_URL_CHECK:
                    # Exact url matches
                    if url in data_sources:
                        url_matches.append(line)
                        priorities.append('5.0')
                        continue
                    
                    # Exact url matches ignoring protocol and extra source data
                    colon = url.find(':')
                    if colon != -1 and colon+3 < len(url):
                        purl = url[colon+3:]
                        if purl+" " in data_sources_str or purl+"\n" in data_sources_str:
                            partial_url_matches.append(line)
                            priorities.append('4.9')
                            continue
                
                # Title matches with games that match part of their source/developer/publisher
                if title in sdp_matches:
                    title_and_sdp_matches.append(line)
                    priorities.append('4.8')
                    continue
                    
                # Later maybe urls matching subfolders without the same domain?
                
                # Title starts another Title (and is >10 characters) that matches part of its source/developer/publisher
                if title_is_long and "\n" + title in sdp_matches_str:
                    title_starts_title_and_sdp_matches.append(line)
                    priorities.append('4.3')
                    continue
                
                # Title matches
                if title in data_titles:
                    title_matches.append(line)
                    priorities.append('4.0')
                    continue
                
                # Title starts another Title (and is >10 characters)
                if title_is_long and "\n" + title in sdp_matches_str:
                    title_starts_title.append(line)
                    priorities.append('3.9')
                    continue
                
                # Title in another Title (and is >10 characters)
                if title_is_long and title in sdp_matches_str:
                    title_in_title.append(line)
                    priorities.append('3.8')
                    continue
                
                # Get similarity metric
                
                # Method with fuzzywuzzy, but fuzzywuzzy wasn't very fuzzy, was he?
                #metric = process.extractOne(name, master_names)[1] / 100
                metric = 0.6
                if DIFFLIB: # It's an option, but an inferior one
                    try: metric = difflib.SequenceMatcher(None, title, difflib.get_close_matches(title, data_titles, 1, 0.6)[0]).ratio()
                    except: pass
                else:
                    for data_title in data_titles:
                        new_metric = Levenshtein.ratio(title, data_title)
                        if new_metric > metric: metric = new_metric
                
                # Has a high similarity metric (>95%)
                if metric > 0.95:
                    high_metric.append((line, metric))
                    priorities.append(str(round(4 * metric - 0.2, 2)))
                    continue
                
                # Has a super low similarity metric (<60%)
                if metric < 0.6:
                    very_low_metric.append((line, metric))
                    priorities.append('1.0')
                    continue
                
                # Has a low similarity metric (<85%)
                if metric < 0.85:
                    if metric < 0.75:
                        very_low_metric.append((line, metric))
                    else:
                        low_metric.append((line, metric))
                    priorities.append(str(round(8 * metric - 3.8, 2)))
                    continue
                
                # Leftovers
                leftovers.append((line, metric))
                priorities.append(str(round(6 * metric - 2.1, 2)))
            
            time_took = time.time() - period
            print('         %d/%d - %d%% Complete (%.3f secs) (avg %.3f secs)' % (input_count, input_count, 100, time_took, time_took / input_count))
            # SUMMARY information
            probables = len(leftovers) + len(low_metric) + len(very_low_metric)
            print('         ' + TEXTS['sum.priority'] % (probables, probables * 100 / input_count))
            print('         ' + TEXTS['sum.priority2'] % (len(very_low_metric), len(very_low_metric) * 100 / input_count))
            print()
            
            # Save information!
            if PRIORITIES:
                printfl("Writing priorities to output file...")
                fpclib.DEBUG_LEVEL, dl = 0, fpclib.DEBUG_LEVEL
                try: fpclib.write("search/priorities.txt", '\n'.join(priorities))
                except: fpclib.DEBUG_LEVEL = dl
                print("Done")
                
                if not silent_: edit_file("search\\priorities.txt")
            if LOG:
                printfl("Writing to log file...")
                fpclib.DEBUG_LEVEL, dl = 0, fpclib.DEBUG_LEVEL
                fpclib.make_dir("search")
                fpclib.DEBUG_LEVEL = dl
                with codecs.open("search/log.txt", 'w', 'utf-8') as log_file:
                    # Sorter for later things
                    sorter = lambda e: e[1]
                    # Sort normal things now
                    duplicate.sort()
            
                    url_matches.sort()
                    partial_url_matches.sort()
                    title_and_sdp_matches.sort()
                    
                    title_starts_title_and_sdp_matches.sort()
                    title_matches.sort()
                    title_starts_title.sort()
                    title_in_title.sort()
                    
                    # Header
                    log_file.write(TEXTS["header"] % (datetime.datetime.now().strftime('%Y-%m-%d')))
                    # Log duplicates
                    dups_text = TEXTS['info.numerics'] % (len(duplicate), 100 * len(duplicate) / input_count)
                    
                    # Log highly likely
                    p5_count = len(url_matches) + len(partial_url_matches) + len(title_and_sdp_matches)
                    p5_text = TEXTS['info.numerics'] % (p5_count, 100 * p5_count / input_count)
                    exacturl_text = TEXTS['p5.exacturl'] + TEXTS['info.numerics'] % (len(url_matches), 100 * len(url_matches) / input_count) + '\n'
                    partialurl_text = TEXTS['p5.partialurl'] + TEXTS['info.numerics'] % (len(partial_url_matches), 100 * len(partial_url_matches) / input_count) + '\n'
                    titleandsdp_text = TEXTS['p5.titleandsdp'] + TEXTS['info.numerics'] % (len(title_and_sdp_matches), 100 * len(title_and_sdp_matches) / input_count) + '\n'
                    
                    # Log likely
                    p4_count = len(title_starts_title_and_sdp_matches) + len(title_matches) + len(title_starts_title) + len(title_in_title) + len(high_metric)
                    p4_text = TEXTS['info.numerics'] % (p4_count, 100 * p4_count / input_count)
                    titlestartsandssdp_text = TEXTS['p4.titlestartsandssdp'] + TEXTS['info.numerics'] % (len(title_starts_title_and_sdp_matches), 100 * len(title_starts_title_and_sdp_matches) / input_count) + '\n'
                    titleonly_text = TEXTS['p4.titleonly'] + TEXTS['info.numerics'] % (len(title_matches), 100 * len(title_matches) / input_count) + '\n'
                    titlestartstitle_text = TEXTS['p4.titlestartstitle'] + TEXTS['info.numerics'] % (len(title_starts_title), 100 * len(title_starts_title) / input_count) + '\n'
                    titleintitle_text = TEXTS['p4.titleintitle'] + TEXTS['info.numerics'] % (len(title_in_title), 100 * len(title_in_title) / input_count) + '\n'
                    highmetric_text = TEXTS['p4.highmetric'] + TEXTS['info.numerics'] % (len(high_metric), 100 * len(high_metric) / input_count) + '\n'
                    
                    # Log middle
                    p3_text = TEXTS['info.numerics'] % (len(leftovers), 100 * len(leftovers) / input_count)
                    leftovers_text = TEXTS['p3.leftovers'] + TEXTS['info.numerics'] % (len(leftovers), 100 * len(leftovers) / input_count) + '\n' + TEXTS['p3.leftovers2'] + '\n'
                    # Log low
                    p2_text = TEXTS['info.numerics'] % (len(low_metric), 100 * len(low_metric) / input_count)
                    lowmetric_text = TEXTS['p2.lowmetric'] + TEXTS['info.numerics'] % (len(low_metric), 100 * len(low_metric) / input_count) + '\n'
                    # Log very low
                    p1_text = TEXTS['info.numerics'] % (len(very_low_metric), 100 * len(very_low_metric) / input_count)
                    verylowmetric_text = TEXTS['p1.verylowmetric'] + TEXTS['info.numerics'] % (len(very_low_metric), 100 * len(very_low_metric) / input_count) + '\n'
                    
                    # Sort
                    high_metric.sort(reverse=True, key=sorter)
                    leftovers.sort(reverse=True, key=sorter)
                    low_metric.sort(reverse=True, key=sorter)
                    very_low_metric.sort(reverse=True, key=sorter)
                    
                    # Table of Contents
                    log_file.write(TEXTS['divider'] % (HEADINGS[0]))
                    log_file.write(TEXTS['tbc.note'])
                    log_file.write(HEADINGS[1] + ' - ' + TEXTS['sum.totalgames'] % (input_count) + '\n')
                    log_file.write(HEADINGS[2] + dups_text + '\n')
                    log_file.write(HEADINGS[3] + p5_text + '\n')
                    log_file.write('  ' + exacturl_text)
                    log_file.write('  ' + partialurl_text)
                    log_file.write('  ' + titleandsdp_text)
                    log_file.write(HEADINGS[4] + p4_text + '\n')
                    log_file.write('  ' + titlestartsandssdp_text)
                    log_file.write('  ' + titleonly_text)
                    log_file.write('  ' + titlestartstitle_text)
                    log_file.write('  ' + titleintitle_text)
                    log_file.write('  ' + highmetric_text)
                    log_file.write(HEADINGS[5] + p3_text + '\n')
                    log_file.write(HEADINGS[6] + p2_text + '\n')
                    log_file.write(HEADINGS[7] + p1_text + '\n')
                    
                    log_file.write('\n')
                    # Summary
                    log_file.write(TEXTS['divider'] % (HEADINGS[1]))
                    log_file.write('\n')
                    log_file.write(TEXTS['sum.totalgames'] % (input_count) + '\n')
                    log_file.write(TEXTS['line'])
                    log_file.write(TEXTS['sum.titlematch'] % (title_match_count) + '\n')
                    
                    #if (not OPTIONS['-r']):
                    log_file.write(TEXTS['sum.sourcematch'] % (sdp_match_count) + '\n')
                    log_file.write(TEXTS['sum.either'] % (title_or_sdp_match_count) + '\n')
                    
                    log_file.write(TEXTS['line'])
                    log_file.write('\n')
                    log_file.write(TEXTS['sum.priority'] % (probables, probables * 100 / input_count) + '\n')
                    log_file.write(TEXTS['sum.priority2'] % (len(very_low_metric), len(very_low_metric) * 100 / input_count) + '\n\n')
                    
                    # Duplicates
                    log_file.write(TEXTS['divider'] % (HEADINGS[2]) + '\n')
                    log_file.write(TEXTS['dup.note'] + dups_text + '\n\n')
                    log_file.write('\n'.join(duplicate))
                    
                    
                    log_file.write('\n\n')
                    # Definitely in Flashpoint
                    log_file.write(TEXTS['divider'] % (HEADINGS[3]))
                    log_file.write('\n# ' + exacturl_text + '\n')
                    log_file.write('\n'.join(url_matches) + '\n')
                    log_file.write('\n# ' + partialurl_text + '\n')
                    log_file.write('\n'.join(partial_url_matches) + '\n')
                    log_file.write('\n# ' + titleandsdp_text + '\n')
                    log_file.write('\n'.join(title_and_sdp_matches) + '\n')
                    
                    
                    log_file.write('\n')
                    # Probably in Flashpoint
                    log_file.write(TEXTS['divider'] % (HEADINGS[4]))
                    log_file.write('\n# ' + titlestartsandssdp_text + '\n')
                    log_file.write('\n'.join(title_starts_title_and_sdp_matches) + '\n')
                    log_file.write('\n# ' + titleonly_text + '\n')
                    log_file.write('\n'.join(title_matches) + '\n')
                    log_file.write('\n# ' + titlestartstitle_text + '\n')
                    log_file.write('\n'.join(title_starts_title) + '\n')
                    log_file.write('\n# ' + titleintitle_text + '\n')
                    log_file.write('\n'.join(title_in_title) + '\n')
                    
                    log_file.write('\n# ' + highmetric_text + '\n')
                    log_file.write('\n'.join(['(%.3f) ' % (metric) + line for line, metric in high_metric]) + '\n')
                    
                    
                    log_file.write('\n')
                    # Maybe in Flashpoint
                    log_file.write(TEXTS['divider'] % (HEADINGS[5]))
                    log_file.write('\n# ' + leftovers_text + '\n')
                    log_file.write('\n'.join(['(%.3f) ' % (metric) + line for line, metric in leftovers]) + '\n')
                    
                    
                    log_file.write('\n')
                    # Probably not in Flashpoint
                    log_file.write(TEXTS['divider'] % (HEADINGS[6]))
                    log_file.write('\n# ' + lowmetric_text + '\n')
                    log_file.write('\n'.join(['(%.3f) ' % (metric) + line for line, metric in low_metric]) + '\n')
                    
                    
                    log_file.write('\n')
                    # Definitely not in Flashpoint
                    log_file.write(TEXTS['divider'] % (HEADINGS[7]))
                    log_file.write('\n# ' + verylowmetric_text + '\n')
                    log_file.write('\n'.join(['(%.3f) ' % (metric) + line for line, metric in very_low_metric]) + '\n')
                    
                print('Done')
                if not silent_: edit_file("search\\log.txt")
        except Exception as e:
            print("[ERR]  Search failed, err ")
            traceback.print_exc()
            tkm.showerror(message=f"Search failed.\n{e.__class__.__name__}: {str(e)}")
        
        if not silent_: unfreeze()

class Lister(tk.Frame):
    def __init__(self):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(padx=5, pady=5)
        
        self.choice = tk.StringVar()
        self.choice.set("Tags")
        c = ttk.Combobox(tframe, textvariable=self.choice, values=["Tags", "Platforms", "Game Master List", "Animation Master List"])
        c.pack(side="left")
        
        self.find_btn = ttk.Button(tframe, text="Find", command=self.find)
        self.find_btn.pack(side="left", padx=5)
        
        clear = ttk.Button(tframe, text="Clear", command=self.clear)
        clear.pack(side="left")
        
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=(0, 5))
    
    def i_find(self):
        txt = self.stxt.txt
        txt.delete("0.0", "end")
        try:
            data = fpclib.get_fpdata(self.choice.get().replace(" ", "_"))
            if data:
                txt.insert("end", "\n".join(data))
            else:
                tkm.showerror(message="Failed to get data from wiki.")
        except Exception as e:
            tkm.showerror(message="Failed to get data from wiki.")
        unfreeze()
    
    def find(self):
        freeze("Gathering Wiki Data")
        threading.Thread(target=self.i_find, daemon=True).start()
    
    def clear(self):
        self.stxt.txt.delete("0.0", "end")

class ScrolledText(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        
        self.txt = tk.Text(self, **kwargs)
        txtV = ttk.Scrollbar(self, orient="vertical", command=self.txt.yview)
        txtH = ttk.Scrollbar(self, orient="horizontal", command=self.txt.xview)
        self.txt.configure(yscrollcommand=txtV.set, xscrollcommand=txtH.set)
        
        self.txt.delete("0.0", "end")
        
        self.txt.grid(row=0, column=0, sticky="nsew")
        txtV.grid(row=0, column=1, sticky="ns")
        txtH.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            print("[INFO] Launching fpcurator GUI variant. Launch the program with the --help flag to see command line usage.")
            MAINFRAME = Mainframe()
            MAINFRAME.mainloop()
        except Exception as e:
            tkm.showerror(message=f"Fatal {e.__class__.__name__}: {str(e)}")
    else:
        # Command line args time!
        parser = argparse.ArgumentParser(description="fpcurator is a bulk tool that makes certain curation tasks easier. There are five modes, -mC (default, autocurator mode), -mG (update site definitions mode), -mD (download urls mode), -mS (bulk search mode), and -mW (get wiki data mode). loc is a file containing urls to do something with, or if -l is set, a url. You can specify as many as you want.")
        
        parser.add_argument("-m", dest='mode', metavar='mode', help="Set the mode specifying what to do with the given urls.", default="C")
        
        parser.add_argument("-b", dest="level", metavar="level", type=int, help="Specifies the debug level to print log data with. Set to 0 for no debug information, -1 for all, 1 for minimum, and 2+ for debug information up to a specific tab level. Not applicable in W mode. Defaults to " + str(fpclib.DEBUG_LEVEL), default=fpclib.DEBUG_LEVEL)
        parser.add_argument("-o", dest='output', metavar='folder', help='Specifies an output folder to put all output data in. This is "output" by default. Not applicable in S or W mode, as S outputs to the search folder and W outputs to the console.')
        parser.add_argument("-l", action='store_true', help="Treat file locations as urls instead of files containing urls. Not applicable in W mode.")
        parser.add_argument("-e", action='store_true', help="Causes the program to stop running the moment an error on the urls occurs. Only applicable in C and D mode.")
        parser.add_argument("-x", action='store_true', help="If this is set and -e is not set, an errors.txt file will be generated with the urls that caused any errors. Only applicable in C and D mode.")
        
        parser.add_argument("-s", action='store_true', help="In C mode, prevents the autocurator from saving it's progress so that if it fails, it will resume where it left off with the same url input. In S mode, it says to strip subtitles from input data.")
        parser.add_argument("-t", action='store_true', help="In C mode, Use randomly generated uuids instead of titles for the name of curation folders. Note that curations with the same title will not overwite each other by default.")
        
        parser.add_argument("-w", action='store_true', help="In D mode, instead of removing the web.archive.org part of urls, keep them in the original wayback folder structure.")
        parser.add_argument("-k", action='store_true', help="In D mode, keeps any url variables at the end of urls being downloaded.")
        
        parser.add_argument("-S", help="In S mode, specifies the regex needed to match sources. When it is not specified, it matches nothing.", default="-^")
        parser.add_argument("-P", help="In S mode, specifies the regex needed to match developers/publishers. When it is not specified, it matches nothing.", default="-^")
        parser.add_argument("-D", action='store_true', help='In S mode, specifies a database to load before searching. You only need to specify this the first time you run a search, as the database is cached in a special format as "search/database.tsv"')
        parser.add_argument("-p", action='store_true', help="In S mode, prevents the generation of a prorities.tsv file in the output directory.")
        parser.add_argument("-r", action='store_true', help="In S mode, prevents the generation of a human readable log.txt file.")
        parser.add_argument("-u", action='store_true', help="In S mode, disables the exact url check.")
        parser.add_argument("-d", action='store_true', help="In S mode, causes the searcher to use the slow default python library difflib.")
        
        parser.add_argument("loc", nargs="+", help='In C, D, and S mode, this is a file containing urls to curate, or if -l is set, a url. You can specify as many as you want. In W mode, it is only a single item specifying the page containing wiki data to grab that will be printed to the console. In S mode (when -l is not set), you must have a line only containing a single "@" character in each file that specifies where the urls of the entries to search for begin. Everything before that character is interpreted as titles, and everything after is interpreted as urls for those titles. In S mode (when -l is set), every other item in the list should be a url and the others should be game titles. In G mode, this just needs to be any text.')
        
        args = parser.parse_args()
        
        # Check for invalid modes
        if args.mode not in ["C", "G", "D", "S", "W"]:
            print("Invalid mode '" + args.mode + "'")
            sys.exit(1)
        
        if args.mode == "G": # G mode is the easiest
            data = fpclib.read_url("https://github.com/FlashpointProject/fpcurator/raw/main/sites/defs.txt")
            AutoCurator.download_defs(data, True)
        elif args.mode == "W": # Wiki mode is easy, just get data
            fpclib.DEBUG_LEVEL, dl = 0, fpclib.DEBUG_LEVEL
            try:
                print("\n".join(fpclib.get_fpdata(args.loc[0])))
            finally:
                fpclib.DEBUG_LEVEL = dl
        else:
            # In all other cases, we need to get the data
            if args.l:
                urls = [url.strip() for url in args.loc if url.strip()]
            else:
                if args.mode == "S":
                    titles = []
                    urls = []
                    for loc in args.loc:
                        try:
                            raw = fpclib.read(loc).replace("\r\n", "\n").replace("\r", "\n").split("@")
                            
                            titles.extend([url.strip() for url in raw[0].split("\n") if url.strip()])
                            urls.extend([url.strip() for url in raw[1].split("\n") if url.strip()])
                        except:
                            fpclib.debug('[ERR]  Invalid file "{}", skipping', 1, loc)
                else:
                    urls = []
                    for loc in args.loc:
                        try:
                            urls.extend([url.strip() for url in fpclib.read_lines(loc) if url.strip()])
                        except:
                            fpclib.debug('[ERR]  Invalid file "{}", skipping', 1, loc)
            
            # Then get output folder
            output = args.output
            if not output:
                output = "search" if args.mode == "S" else "output"
            
            # Set debug level
            fpclib.DEBUG_LEVEL, dl = args.level, fpclib.DEBUG_LEVEL
            
            # Now do stuff
            try:
                if args.mode == "C":
                    # Autocurate urls (default mode)
                    defs = AutoCurator.get_defs(True)
                    if defs:
                        errs = AutoCurator.s_curate(output, defs, urls, not args.t, not args.s, not args.e)
                        if errs and args.x:
                            fpclib.write("errors.txt", [i for i,e,d in errs])
                            fpclib.debug('[INFO] Wrote errored urls to errors.txt file', 1)
                    else:
                        fpclib.debug('[ERR]  No site definitions found', 1)
                    
                elif args.mode == "D":
                    # Download urls
                    errs = fpclib.download_all(links, output, args.w, args.k, not args.e)
                    if errs and args.x:
                        fpclib.write("errors.txt", [i for i,e,d in errs])
                        fpclib.debug('[INFO] Wrote errored urls to errors.txt file', 1)
                    
                elif args.mode == "S":
                    # turn urls into titles and urls
                    if args.l:
                        if len(urls) % 2 == 1:
                            print("[ERR]  Missing url for last title")
                            sys.exit(2)
                        titles = urls[::2] # slice notation makes this easy peasy
                        urls = urls[1::2]
                    
                    Searcher.s_search(titles, urls, args.D, args.S, args.P, not args.p, not args.r, args.s, not args.u, args.d, True)
            finally:
                fpclib.DEBUG_LEVEL = dl
        