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
import functools
import pyperclip
import googletrans
import glob
import importlib
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

HELP_HTML = """<!doctype html>
<html><body>
    <h1><center>Help</center></h1>
    <p>fpcurator is a collection of tools for performing certain curation tasks easier. There are four sub-tools available. Note that the tool may freeze while performing any task. All debug info on any task is printed to the console that can be shown by clicking "Toggle Log".</p>
    
    <h2>Auto Curator</h2>
    <p>The Auto Curator tool generates a bunch of partial curations based upon a list of urls containing the games to curate. The list of curatable websites is limited the site definitions in the "sites" folder next to the program. To reload all site definitions, press "Reload". To redownload your site definitions, press "Redownload".<br>
    <b>NOTE: Auto curated games should ALWAYS be tested in Flashpoint Core before being submitted.</b>
    &nbsp;<br>Here are a list of options:
    <ul>
        <li><b>Save</b> - When checked, the auto curator will save it's progress so if it fails from an error, the tool will resume where it left off given the same urls.</li>
        <li><b>Use Titles</b> - When checked, the auto curator will use the titles of curated games instead of randomly generated UUIDs as the names of the folders the curations are put into.</li>
        <li><b>Clear Done URLs</b> - When checked, the auto curator will clear any urls in the list when they are curated. Errored urls will remain in the list.</li>
        <li><b>Notify When Done</b> - When checked, the auto curator will show a message box when it is done curating.</li>
    </ul>
    Here are some basic usage steps:
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
    Here are some basic usage steps:
    <ol>
        <li>Select the options you want, specified by the list above, and set the output directory of the downloaded folders and files.</li>
        <li>Paste the urls you want to download into the text box, one per line.</li>
        <li>Press the "Download" button to start the download process.</li>
    </ol>
    </p>
    
    <h2>Game Finder</h2>
    <p>The Game Finder is an extension of the default searching feature present in Flashpoint already. Type a search query into the "Query" box and press "Search" or Enter to search for those entries within the Flashpoint database of your choice. Make sure you pick the Infinity or Ultimate database ("FlashpointFolder/Data/flashpoint.sqlite") rather than the Core one.<br>
    &nbsp;<br>
    There are buttons available to export values you have selected in the list (use Ctrl+Click or Shift+Click to select multiple) into a playlist or to just copy their titles/uuids.
    &nbsp;<br>
    Overall, the search feature works in exactly the way the default Flashpoint Search Bar does, with a few changes:
    <ul>
        <li>String search parts now require internal quotes to be escaped: <code>""game""</code> is wrong, but <code>"\\"game\\""</code> is right.</li>
        <li>Instead of using the ":" comparison operator, you may also use the "=" or "~" operators in it's place. The "=" sign checks for an exact match to the provided text (which may be in quotes) while the "~" checks for an like match to an SQL LIKE string. These operators may also be used on keywords alone: <code>="Game"</code> and <code>=Game</code> do the same thing (check that the name of a game is exactly "Game"), but the first can accept spaces inside it.</li>
        <li>Queries can be separated by an <code>OR</code> keyword that does exactly what you think it does. e.g., find all action or adventure games: <code>#Action OR #Adventure</code>. If you want to search for the text "or" exactly, just use lowercase letters as the search is case-insensitive.</li>
        <li><code>AND</code> is now a keyword that basically does nothing, since two search terms right next to each other are assumed to be "AND" joined unless there's an "OR" between them. Note that you cannot group AND and OR conditions with parentheses. If you want to search for the text "and" exactly, just use lowercase letters as the search is case-insensitive.</li>
        <li>The @ prefix now matches any of developer, publisher, or source instead of just developer. This means you'll get more results that you're looking for.</li>
        <li>If you don't provide a field to match, the program will automatically assume you are searching for a title keyword. This will also search through alternate titles. You can also use <code>title:"thing here"</code> instead of <code>thing here</code> to exclude alternate title searching.</li>
        <li>The prefixes "alt", "tags", "genre", "genres", "ser", "dev", "pub", "src", "url", "tech", "mode", "ver", "v", "date", "lang", "desc", "app", and "cmd" are available to be used in place of their longer counterparts like launchCommand and applicationPath to make searching easier.</li>
    </ul>
    </p>

    <h2>Curation DeDuper</h2>
    <p>When pointed to a folder containing a bunch of curations, the curation deduper will show you (generally) how likely it is that each of them individually is in Flashpoint. Make sure the database is set to the Infinity/Ultimate database and not the Core one. The deduper first checks to see if the launch command is already in Flashpoint, then it checks the source url, and finally it checks the title. Only launch command and source url matches are confirmed duplicates. If any of your curations are from the same exact source as a game in Flashpoint, they will be marked as duplicates; turn off this feature with the checkbox if you are curating games from a disk or someplace that has multiple games per the same source (should not happen with normal games, which ought to use the webpage url)
    &nbsp;<br>Here are some basic usage steps:
    <ol>
        <li>Set the database to your Infinity/Ultimate database.</li>
        <li>Set the curations folder to your Curations/Working folder, wherever that may be (hopefully it's in Core).</li>
        <li>Select whether or not to check sources.</li>
        <li>Press the check button to check for duplicates.</li>
        <li>Select the items you want to delete and delete them, or copy their titles so you can search in Flashpoint or fpcurator for duplicates.</li>
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
    Here are some basic usage steps:
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

FIELDS = {
    "alt": "alternateTitles",
    "#": "tags",
    "tag": "tags",
    "genre": "tags",
    "genres": "tags",
    "ser": "series",
    "dev": "developer",
    "pub": "publisher",
    "src": "source",
    "url": "source",
    "!": "platform",
    "tech": "platform",
    "mode": "playMode",
    "ver": "version",
    "v": "version",
    "date": "releaseDate",
    "lang": "language",
    "desc": "description",
    "app": "applicationPath",
    "cmd": "launchCommand"
}
# This uuid uniquely defines fpcurator. (there is a 0 on the end after the text)
UUID = '51be8a01-3307-4103-8913-c2f70e64d83'

TITLE = "fpcurator v1.5.0"
ABOUT = "Created by Zach K - v1.5.0"
VER = 5

SITES_FOLDER = "sites"

fpclib.DEBUG_LEVEL = 4

AM_PATTERN = re.compile(r'[\W_]+')
AMS_PATTERN = re.compile(r'([^\w;]|_)+')
INV = re.compile(r'[^\w ]+')
QPARSER = re.compile(r'\s*(-)?(?:(@|#|!)(:|=|~)?|(\w*)(:|=|~))?(?:"([^"\\]+|\\\\|\\.)*"|([^\s]+))')
SPACES = re.compile(r'\s+')

MAINFRAME = None

DEFS_GOTTEN = False

def set_entry(entry, data):
    entry.delete(0, "end")
    entry.insert(0, data)

def printfl(data):
    print(data, end="", flush=True)

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

def print_err(pre="", start=1, e=None):
    if e:
        tb_lines = traceback.format_exception(e.__class__, e, e.__traceback__)
    else:
        tb_lines = traceback.format_exception(*sys.exc_info())
    
    lines = []
    for tb_line in tb_lines[start:]:
        for line in tb_line.split("\n"):
            if line:
                if line[0] == " ": lines.append(line[2:])
                else: lines.append(line)

    for line in lines:
        print(pre + line)

class Mainframe(tk.Tk):
    def __init__(self):
        # Create window
        super().__init__()
        self.minsize(695, 650)
        self.title(TITLE)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        
        # Cross-window variables
        self.database = tk.StringVar()
        
        # Add tabs
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=5, pady=5)
        self.tabs.bind("<<NotebookTabChanged>>", self.tab_change)
        
        self.autocurator = AutoCurator(self)
        self.downloader = Downloader(self)
        self.searcher = Searcher(self)
        self.ssearcher = SingleSearcher(self)
        self.deduper = DeDuper(self)
        self.lister = Lister(self)
        
        self.tabs.add(self.autocurator, text="Auto Curator")
        self.tabs.add(self.downloader, text="Download URLs")
        self.tabs.add(self.ssearcher, text="Game Finder")
        self.tabs.add(self.deduper, text="Curation DeDuper")
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
        self.save()
        
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
        elif tab == ".!singlesearcher":
            self.ssearcher.queryx.focus_set()
        elif tab == ".!deduper":
            self.focus_set()
        self.save()
    
    def check_freeze(self):
        if self.frozen and not frozen_ui: self.unfreeze()
        self.after(100, self.check_freeze)
    
    def freeze(self, subtitle):
        self.autocurator.curate_btn["state"] = "disabled"
        self.autocurator.reload_btn["state"] = "disabled"
        self.downloader.download_btn["state"] = "disabled"
        self.searcher.load_btn["state"] = "disabled"
        self.searcher.search_btn["state"] = "disabled"
        self.ssearcher.search_btn["state"] = "disabled"
        self.deduper.search_btn["state"] = "disabled"
        self.lister.find_btn["state"] = "disabled"
        #self.lister.stxt.txt["state"] = "disabled"
        if self.ssearcher.lbox: self.ssearcher.lbox.search_btn["state"] = "disabled"
        self.ssearcher.export_btn["state"] = "disabled"
        self.ssearcher.export_all_btn["state"] = "disabled"
        
        self.title(TITLE + " - " + subtitle)
        
        self.frozen = True
    
    def unfreeze(self):
        self.autocurator.curate_btn["state"] = "normal"
        self.autocurator.reload_btn["state"] = "normal"
        self.downloader.download_btn["state"] = "normal"
        self.searcher.load_btn["state"] = "normal"
        self.searcher.search_btn["state"] = "normal"
        self.ssearcher.search_btn["state"] = "normal"
        self.deduper.search_btn["state"] = "normal"
        self.lister.find_btn["state"] = "normal"
        #self.lister.stxt.txt["state"] = "normal"
        if self.ssearcher.lbox: self.ssearcher.lbox.search_btn["state"] = "normal"
        self.ssearcher.export_btn["state"] = "normal"
        self.ssearcher.export_all_btn["state"] = "normal"
        
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
            # TODO: Python can't stop a thread easily, so make sure nothing is running before closing.
            if not CONSOLE_OPEN: toggle_console()
            if self.ssearcher.lbox: self.ssearcher.lbox.exit_window()
            self.save()
            self.destroy()
    
    def save(self):
        autocurator = {}
        downloader = {}
        searcher = {}
        ssearcher = {}
        deduper = {}
        
        data = {"autocurator": autocurator, "downloader": downloader, "searcher": searcher, "ssearcher": ssearcher, "deduper": deduper, "debug_level": self.debug_level.get(), "tab": self.tabs.select(), "database": self.database.get()}
        
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
        searcher["sources"] = self.searcher.sources.get()
        searcher["devpubs"] = self.searcher.devpubs.get()
        
        searcher["priorities"] = self.searcher.priorities.get()
        searcher["log"] = self.searcher.log.get()
        searcher["strip"] = self.searcher.strip.get()
        searcher["exact_url"] = self.searcher.exact_url.get()
        searcher["difflib"] = self.searcher.difflib.get()
        
        searcher["titles"] = self.searcher.stxta.txt.get("0.0", "end").strip()
        searcher["urls"] = self.searcher.stxtb.txt.get("0.0", "end").strip()
        
        # Save ssearcher data
        ssearcher["lib"] = self.ssearcher.library.get()
        ssearcher["query"] = self.ssearcher.query.get()
        ssearcher["lquery"] = self.ssearcher.lquery.get().strip()
        ssearcher["rdata"] = self.ssearcher.rdata
        
        # Save deduper data
        deduper["src_chk"] = self.deduper.src_chk.get()
        deduper["curations"] = self.deduper.curations.get()
        deduper["rdata"] = self.deduper.rdata
        
        with open("data.json", "w") as file: json.dump(data, file)
    
    def load(self):
        try:
            with open("data.json", "r") as file: data = json.load(file)
            
            # Set basic data
            self.debug_level.set(data["debug_level"])
            self.tabs.select(data["tab"])
            self.database.set(data["database"])
            
            
            autocurator = data["autocurator"]
            downloader = data["downloader"]
            searcher = data["searcher"]
            ssearcher = data["ssearcher"]
            deduper = data["deduper"]
            
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
            
            # Load downloader data
            set_entry(self.downloader.output, downloader["output"])
            
            self.downloader.original.set(downloader["original"])
            self.downloader.keep_vars.set(downloader["keep_vars"])
            self.downloader.clear.set(downloader["clear"])
            self.downloader.show_done.set(downloader["show_done"])
            
            txt = self.downloader.stxt.txt
            txt.delete("0.0", "end")
            txt.insert("1.0", downloader["urls"])
            
            # Load searcher data
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
            
            # Load ssearcher data
            self.ssearcher.library.set(ssearcher["lib"])
            self.ssearcher.query.set(ssearcher["query"])
            self.ssearcher.lquery.set(ssearcher["lquery"])
            self.ssearcher.set_results(ssearcher["rdata"])
            
            # Load deduper data
            self.deduper.src_chk.set(deduper["src_chk"])
            set_entry(self.deduper.curations, deduper["curations"])
            self.deduper.set_results(deduper["rdata"])
            
        except (FileNotFoundError, KeyError):
            # On first launch, check if in Flashpoint "Utilities" folder and set default data if so
            dirs = [d for d in os.getcwd().replace("\\", "/").split("/") if d]
            try:
                if dirs[-2].lower() == "utilities" and "flashpoint" in dirs[-3].lower():
                    #self.database.set("../Data/flashpoint.sqlite")
                    set_entry(self.autocurator.output, "../../Curations/Working")
                    set_entry(self.deduper.curations, "../../Curations/Working")
            except:
                pass

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
    def __init__(self, parent):
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
                m = importlib.import_module(name)
                importlib.reload(m)
                
                priorities[name] = m.priority if hasattr(m, "priority") else 0
                if getattr(m, "ver", VER) <= VER:
                    defs.append((m.regex, getattr(m, name)))
                    fpclib.debug('Found definition "{}"', 1, name)
                else:
                    fpclib.debug('Definition "{}" is not supported. Update fpcurator!', 1, name)
            except:
                fpclib.debug('Skipping definition "{}", error:', 1, name)
                print_err("  " * fpclib.TABULATION + "         ", 2)
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
        
        # Print errors
        if errs:
            print("[ERR]  These urls failed to be curated:")
            for url, e, _ in errs:
                print(f"         {url}:")
                print_err("           ", 3, e)
        
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
    def __init__(self, parent):
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
            print_err("         ")
            tkm.showerror(message=f"Failed to download urls.\n{e.__class__.__name__}: {str(e)}")
        
        unfreeze()
    
    def download(self):
        freeze("Downloading URLs")
        threading.Thread(target=self.i_download, daemon=True).start()

class Searcher(tk.Frame):
    def __init__(self, parent):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(fill="x", padx=5, pady=5)
        self.parent = parent
        
        # Create options for locating the Flashpoint database
        dlabel = tk.Label(tframe, bg="white", text="Database:")
        dlabel.pack(side="left", padx=5)
        self.database = ttk.Entry(tframe, textvariable=parent.database)
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
        if db: self.parent.database.set(db)
    
    def s_load(dbloc, silent=False):
        try:
            # Acquire the database!
            db = sqlite3.connect(dbloc)
            c = db.cursor()
            
            # Next, get all required data through a query
            c.execute("select id, lower(title), lower(platform), lower(alternateTitles), lower(developer), lower(publisher), source, language, title from game")
            data = c.fetchall()
            db.close()
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
            print_err("         ")
            if not silent: tkm.showerror(message=f"Failed to load database. Ensure the the database provided is valid.\n{e.__class__.__name__}: {str(e)}")
        finally:
            if not silent: unfreeze()
        
        return False
    
    def load(self):
        freeze("Loading Database")
        threading.Thread(target=lambda: Searcher.s_load(self.parent.database.get(), False), daemon=True).start()
    
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
            
            threading.Thread(target=lambda: Searcher.s_search(titles, urls, self.parent.database.get(), self.sources.get(), self.devpubs.get(), PRIORITIES, LOG, STRIP_SUBTITLES, EXACT_URL_CHECK, DIFFLIB), daemon=True).start()
        except Exception as e:
            print("Failed to start search, err ")
            print_err("  ")
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
                        print_err("  ")
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
            print()
        except Exception as e:
            print("[ERR]  Search failed, err ")
            print_err("         ")
            tkm.showerror(message=f"Search failed.\n{e.__class__.__name__}: {str(e)}")
        
        if not silent_: unfreeze()

class SingleSearcher(tk.Frame):
    def __init__(self, parent):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(padx=5, pady=5, fill="x")
        
        self.parent = parent
        
        # Create options for locating the Flashpoint database
        dlabel = tk.Label(tframe, bg="white", text="Database:")
        dlabel.pack(side="left", padx=5)
        self.database = ttk.Entry(tframe, textvariable=parent.database)
        self.database.pack(side="left", fill="x", expand=True)
        db = ttk.Button(tframe, text="...", width=3, command=self.get_database)
        db.pack(side="left")
        self.search_btn = ttk.Button(tframe, text="Search", command=self.search)
        self.search_btn.pack(side="left", padx=5)
        
        # Create searching fields
        mframe = tk.Frame(self, bg="white")
        mframe.pack(fill="both", padx=5)
        
        # Library
        self.library = tk.StringVar()
        self.library.set("All*")
        lib_lbl = tk.Label(mframe, bg="white", text="Library:")
        lib_lbl.pack(side="left", padx=5)
        lib = ttk.Combobox(mframe, width=10, textvariable=self.library, values=["All*", "Arcade*", "Theatre*", "All", "Arcade", "Theatre"])
        lib.pack(side="left")
        
        # Query
        self.query = tk.StringVar()
        qlabel = tk.Label(mframe, bg="white", text="Query:")
        qlabel.pack(side="left", padx=5)
        self.queryx = ttk.Entry(mframe, textvariable=self.query)
        self.queryx.pack(side="left", fill="x", expand=True)
        self.queryx.bind('<Return>', lambda e: self.search())
        more_btn = ttk.Button(mframe, text="...", width=3, command=self.open_large_box)
        more_btn.pack(side="left", padx=(0, 5))
        
        # Large Query
        self.lquery = tk.StringVar()
        self.lbox = None
        
        # Buttons for copying results
        bframe = tk.Frame(self, bg="white")
        bframe.pack(padx=5, pady=(5, 0))
        
        copy_btn = ttk.Button(bframe, text="Copy Selected UUIDs", command=self.copy_uuids)
        copy_btn.pack(side="left", padx=(0, 5))
        copy_all_btn = ttk.Button(bframe, text="Copy All UUIDs", command=lambda: self.copy_uuids(True))
        copy_all_btn.pack(side="left")
        copy_t_btn = ttk.Button(bframe, text="Copy Selected Titles", command=self.copy_titles)
        copy_t_btn.pack(side="left", padx=5)
        copy_all_t_btn = ttk.Button(bframe, text="Copy All Titles", command=lambda: self.copy_titles(True))
        copy_all_t_btn.pack(side="left")
        
        bframe2 = tk.Frame(self, bg="white")
        bframe2.pack(pady=5)
        
        self.export_btn = ttk.Button(bframe2, text="Export Selected to New Playlist", command=self.export)
        self.export_btn.pack(side="left", padx=5)
        self.export_all_btn = ttk.Button(bframe2, text="Export All to New Playlist", command=lambda: self.export(True))
        self.export_all_btn.pack(side="left")
        
        # Result count
        self.rcount = tk.StringVar()
        self.rcount.set("0 entries found")
        rcount = tk.Label(self, bg="white", textvariable=self.rcount)
        rcount.pack(padx=5)
        
        # Results treeview
        self.rdata = []
        self.results = ScrolledTreeview(self, columns=("Platform", "Source", "Library"), widths=(50, 50, 50, 50), command=self.sort_results)
        self.results.pack(padx=5, pady=(0, 5), fill="both", expand=True)
    
    def get_database(self):
        # For changing the flashpoint database location
        db = tkfd.askopenfilename(filetypes=[("SQLite Database", "*.sqlite")])
        if db: self.parent.database.set(db)
    
    def open_large_box(self):
        if not self.lbox: self.lbox = BigQuery(self)
    
    def sort_results(self, i):
        self.rdata.sort(key=lambda x: x[i+1].lower())
        self.set_results(self.rdata)
        
    def set_results(self, results):
        self.rdata = results
        
        self.results.delete(*self.results.get_children())
        for i, result in enumerate(self.rdata):
            self.results.insert("", index="end", iid=i, text=result[1], values=tuple(result[2:]))
        
        self.rcount.set(str(len(self.rdata)) + " entries found")
    
    def get_results(self, all, pos=0):
        items = []
        if all:
            items = [entry[pos] for entry in self.rdata]
        else:
            for s in self.results.selection():
                items.append(self.rdata[int(s)][pos])
        return items
    def copy_titles(self, all=False):
        titles = self.get_results(all, 1)
        if titles: pyperclip.copy('\n'.join(titles))
    def copy_uuids(self, all=False):
        uuids = self.get_results(all)
        if uuids: pyperclip.copy('\n'.join(uuids))
    def export(self, all=False):
        uuids = self.get_results(all)
        if uuids:
            try:
                con = sqlite3.connect(self.parent.database.get())
            except Exception as e:
                if not silent: tkm.showerror(message=f"Could not connect to database, {e.__class__.__name__}: {str(e)}")
                print("[ERR]  Could not connect to database, err:")
                print_err("         ")
                return
            
            cur = con.cursor()
            
            def create_playlist(lib):
                # Create playlist
                pid = uuid.uuid4()
                cur.execute("INSERT OR REPLACE INTO playlist VALUES (?, '!Search Results!', 'Exported search results gathered from fpcurator.', 'fpcurator', '', ?, 0)", (pid, lib))
                # Delete existing items in the playlist (if they exist, which they shouldn't)
                cur.execute("DELETE FROM playlist_game WHERE playlistId = ?", (pid,))
                # Insert items into playlist
                cur.executemany("INSERT INTO playlist_game (playlistId, 'order', notes, gameId) VALUES (?, ?, '', ?)", [(pid, i, uuid) for i, uuid in enumerate(uuids)])
            
            lib = self.library.get()
            if lib[-1] == "*": tlib = lib[:-1].lower()
            else: tlib = lib.lower()
            if tlib == "all":
                create_playlist("arcade")
            elif tlib == "arcade":
                create_playlist("arcade")
            elif tlib == "theatre":
                create_playlist("theatre")
            tkm.showinfo(message='Exported search results to playlist "!Search Results!".')
            
            con.commit()
            con.close()
    
    def parse_query(cur, query, lib, silent=False):
        if not query.strip(): return ""
        
        if lib[-1] == "*":
            tlib = lib[:-1].lower()
            extremewhere = "(NOT extreme) AND "
        else:
            tlib = lib.lower()
            extremewhere = ""
        
        if tlib == "all": libwhere = ""
        else: libwhere = "library = '" + INV.sub("", tlib) + "' AND "
        
        # Start by tokenizing query
        tquery = SPACES.sub(" ", query).strip()
        tokens = []
        i, l = 0, len(tquery)
        while i < l:
            m = QPARSER.match(tquery, i)
            if not m: return "" # For now
            tokens.append(m)
            i = m.span()[1]
        # Next turn tokens into string list
        sql = []
        args = []
        
        i, l = 1, len(tokens)
        
        if not SingleSearcher.parse_token(cur, sql, args, tokens[0]): return ""
        while i < l:
            if tokens[i][0].strip() == "AND": pass
            elif tokens[i][0].strip() == "OR":
                sql.append("OR")
                if not SingleSearcher.parse_token(cur, sql, args, tokens[i+1]): return ""
                i += 1
            else:
                sql.append("AND")
                if not SingleSearcher.parse_token(cur, sql, args, tokens[i]): return ""
            i += 1
        
        # Join and return sql
        return f"SELECT id, title, platform, source, library FROM game WHERE {libwhere}{extremewhere}({' '.join(sql)})", args
    
    def parse_token(cur, sql, args, token):
        # Check invert
        if token[1]: invert = "NOT ("
        else: invert = "("
        
        # Get regex parts
        mode = token[3] or token[5] or ":"
        
        field = token[2] or token[4]
        if field in FIELDS: field = FIELDS[field]
        
        data = token[7]
        if not data: data = token[6].replace("\\\\", "\\").replace('\\"', '"')
        
        if field in {"no", "not", "missing", "has", "is"}:
            tfield = AM_PATTERN.sub("", data) # Sanatize the input
            if tfield in FIELDS: tfield = FIELDS[tfield]
            
            if bool(token[1]) != (field == "has" or field == "is"):
                sql.append(f"NOT ({tfield} = '' OR {tfield} = 0)")
            else:
                sql.append(f"({tfield} = '' OR {tfield} = 0)")
        elif field == "tags":
            comps = []
            tags = [t.strip() for t in data.split(";")]
            for tag in tags:
                cur.execute("SELECT tagId FROM tag_alias WHERE name = ?", (tag,))
                try: tagID = cur.fetchone()[0]
                except: return False
                comps.append("tagId = ?")
                args.append(tagID)
            # There's definitely a better way to search tags but whatever
            sql.append(f"{invert}EXISTS (SELECT tagId FROM game_tags_tag tags WHERE game.id = tags.gameId AND ({' OR '.join(comps)})))")
        elif mode == ":":
            comps = []
            if field == "@":
                for keyword in data.strip().split(" "):
                    comps.append("(developer LIKE ? OR publisher LIKE ? OR source LIKE ?)")
                    key = f'%{keyword}%'
                    args.extend((key, key, key))
            elif not field:
                for keyword in data.strip().split(" "):
                    comps.append(f"(title LIKE ? OR alternateTitles LIKE ?)")
                    key = f'%{keyword}%'
                    args.extend((key, key))
            else:
                for keyword in data.strip().split(" "):
                    comps.append(field + " LIKE ?")
                    args.append(f'%{keyword}%')
            sql.append(invert + ' AND '.join(comps) + ")")
        elif mode == "=":
            if field == "@":
                sql.append(invert + "developer = ? OR publisher = ? OR source = ?)")
                args.extend((data, data, data))
            elif not field:
                # Alternate titles are yikes man
                sql.append(invert + "title = ? OR alternateTitles = ? OR alternateTitles LIKE ? OR alternateTitles LIKE ? OR alternateTitles LIKE ?)")
                args.extend((data, data, '%; '+data, data+'; %', '%; '+data+'; %'))
            else:
                sql.append(invert + field + " = ?)")
                args.append(data)
        elif mode == "~":
            if field == "@":
                sql.append(invert + "developer LIKE ? OR publisher LIKE ? OR source LIKE ?)")
                args.extend((data, data, data))
            elif not field:
                sql.append(invert + "title LIKE ? OR altnerateTitles LIKE ? )")
                args.extend((data, data))
            else:
                sql.append(invert + field + " LIKE ?)")
                args.append(data)
        
        return True
    
    def execute_search(cur, sql, args, callback, silent=False):
        print("[INFO] Attempting to search through the Flashpoint database")
        try:
            cur.execute(sql, args)
            data = cur.fetchall()
            if callback: callback(data)
        
            if not silent: unfreeze()
            return data
        except Exception as e:
            if not silent: tkm.showerror(message=f"Could not complete search, {e.__class__.__name__}: {str(e)}")
            print("[ERR]  Could not complete search, err:")
            print_err("         ")
            if not silent: unfreeze()
    
    def search(self, large=False, silent=False):
        try:
            con = sqlite3.connect(self.parent.database.get())
        except Exception as e:
            if not silent: tkm.showerror(message=f"Could not connect to database, {e.__class__.__name__}: {str(e)}")
            print("[ERR]  Could not connect to database, err:")
            print_err("         ")
            return
        
        cur = con.cursor()
        try:
            if large:
                sql = SingleSearcher.parse_query(cur, self.lquery.get().strip(), self.library.get())
            else:
                sql = SingleSearcher.parse_query(cur, self.query.get().strip(), self.library.get())
        except Exception as e:
            sql = ""
            print_err()
        
        if sql:
            #print(sql[0])
            #print(sql[1])
            freeze("Finding Flashpoint Games")
            SingleSearcher.execute_search(cur, sql[0], sql[1], self.set_results, False)
            #threading.Thread(target=lambda: SingleSearcher.i_search(db, sql, False), daemon=True).start()
        else:
            self.set_results([])
        con.close()

class BigQuery(tk.Toplevel):
    def __init__(self, parent):
        # Create big query thing
        super().__init__()
        self.minsize(200, 200)
        self.geometry("450x350")
        self.title(TITLE + " - Large Search Box")
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.parent = parent
        
        self.stxt = ScrolledText(self, nohsb=True, width=1, height=1)
        self.stxt.txt.delete("0.0", "end")
        self.stxt.txt.insert("0.0", self.parent.lquery.get())
        self.stxt.pack(padx=5, pady=5, expand=True, fill="both")
        
        self.search_btn = ttk.Button(self, text="Search", command=self.search)
        self.search_btn.pack(padx=5, pady=(0, 5))
        if frozen_ui: self.search_btn["state"] = "disabled"
    
    def exit_window(self):
        self.parent.lquery.set(self.stxt.txt.get("0.0", "end"))
        self.parent.lbox = None
        self.destroy()
    
    def search(self):
        self.parent.lquery.set(self.stxt.txt.get("0.0", "end"))
        self.parent.search(True)

TEMP_RESULTS = None
class DeDuper(tk.Frame):
    def __init__(self, parent):
        # Create panel
        super().__init__(bg="white")
        self.parent = parent
        
        # Create options for locating the Flashpoint database
        tframe = tk.Frame(self, bg="white")
        tframe.pack(padx=5, pady=5, fill="x")
        
        dlabel = tk.Label(tframe, bg="white", text="Database:")
        dlabel.pack(side="left", padx=5)
        self.database = ttk.Entry(tframe, textvariable=parent.database)
        self.database.pack(side="left", fill="x", expand=True)
        db = ttk.Button(tframe, text="...", width=3, command=self.get_database)
        db.pack(side="left")
        self.search_btn = ttk.Button(tframe, text="Check", command=self.search)
        self.search_btn.pack(side="left", padx=5)
        
        # Create options for curations folder
        tframe2 = tk.Frame(self, bg="white")
        tframe2.pack(padx=5, fill="x")
        
        olabel = tk.Label(tframe2, bg="white", text="Curations Folder:")
        olabel.pack(side="left", padx=5)
        self.curations = ttk.Entry(tframe2)
        self.curations.pack(side="left", fill="x", expand=True)
        folder = ttk.Button(tframe2, text="...", width=3, command=self.folder)
        folder.pack(side="left", padx=(0, 5))
        #self.refresh_btn = ttk.Button(tframe2, text="Refresh", command=self.refresh)
        #self.refresh_btn.pack(side="left", padx=5)
        
        # Label for important information
        lbl = tk.Label(self, bg="white", text='IMPORTANT: Click another tab besides "Curate" before pressing "Check".')
        lbl.pack(padx=5, pady=5)
        
        # Buttons for copying/modifying results
        bframe = tk.Frame(self, bg="white")
        bframe.pack(padx=5)
        
        self.src_chk = tk.BooleanVar()
        self.src_chk.set(True)
        src_chk = tk.Checkbutton(bframe, bg="white", text="Check Source", var=self.src_chk)
        src_chk.pack(side="left")
        Tooltip(src_chk, text="When checked, the deduper will check to see if the source url is in the database. Turn this off if you have multiple games per the same source (like from a local disk)")
        
        del_btn = ttk.Button(bframe, text="Delete Selected Curations", command=self.delete_cur)
        del_btn.pack(side="left", padx=5)
        del_dup_btn = ttk.Button(bframe, text="Delete Definite Duplicates", command=lambda: self.delete_cur(True))
        del_dup_btn.pack(side="left")
        
        bframe2 = tk.Frame(self, bg="white")
        bframe2.pack(padx=5, pady=5)
        
        copy_btn = ttk.Button(bframe2, text="Copy Selected Titles", command=self.copy_cur)
        copy_btn.pack(side="left", padx=5)
        copy_match_btn = ttk.Button(bframe2, text="Copy Selected Match's UUID", command=self.copy_match)
        copy_match_btn.pack(side="left")
        
        # Results treeview
        self.rdata = []
        self.results = ScrolledTreeview(self, columns=("Duplicate", "Message",))
        self.results.pack(padx=5, pady=(0, 5), fill="both", expand=True)
        
        # Update
        self.update = False
        self.after(100, self.check_update)
    
    def get_database(self):
        # For changing the flashpoint database location
        db = tkfd.askopenfilename(filetypes=[("SQLite Database", "*.sqlite")])
        if db: self.parent.database.set(db)
    def folder(self):
        # For changing the output folder
        folder = tkfd.askdirectory()
        if folder: set_entry(self.curations, folder)
    
    def delete_cur(self, dups=False):
        if dups:
            for i in range(len(self.rdata)-1, -1, -1):
                data = self.rdata[i]
                if data[3] == "Yes":
                    fpclib.delete(data[0])
                    del self.rdata[i]
        else:
            sels = self.results.selection()
            if sels:
                for sel in reversed(sels):
                    isel = int(sel)
                    fpclib.delete(self.rdata[isel][0])
                    del self.rdata[isel]
        self.set_results(self.rdata)
    def copy_cur(self):
        data = [self.rdata[int(sel)][2] for sel in self.results.selection()]
        if data: pyperclip.copy("\n".join(data))
    def copy_match(self):
        data = [self.rdata[int(sel)][1] for sel in self.results.selection()]
        if data: pyperclip.copy("\n".join(data))
    
    def check_update(self):
        if self.update:
            self.set_results(self.rdata)
            self.update = False
        self.after(100, self.check_update)
    def set_results(self, results):
        self.rdata = results
        
        self.results.delete(*self.results.get_children())
        for i, result in enumerate(results):
            self.results.insert("", index="end", iid=i, text=result[2], values=tuple(result[3:]))
    
    def i_search(folder, db, src_chk, ui=None):
        try:
            con = sqlite3.connect(db)
        except Exception as e:
            if ui: tkm.showerror(message=f"Could not connect to database, {e.__class__.__name__}: {str(e)}")
            print("[ERR]  Could not connect to database, err:")
            print_err("         ")
            return
        
        if not folder:
            if silent: pass
            else: tkm.showerror(message="You must specify a folder containing curations to check through.")
            return
        
        print("[INFO] Deduping curations")
        fpclib.TABULATION += 1
        fpclib.DEBUG_LEVEL, dl = 1, fpclib.DEBUG_LEVEL
        results = []
        cur = con.cursor()
        for cf in glob.glob(folder+"/*"):
            loc = max(cf.rfind("/"), cf.rfind("\\"))+1 # Funny how if nether are found it goes to the beginning of the string (-1+1=0)
            fname = cf[loc:]
            fpclib.debug("Found curation {}", 1, fname)
            
            if fname[0] != "_":
                try:
                    c = fpclib.load(cf)
                    x, dup, msg = DeDuper.find_msg(c, cur, src_chk)
                    results.append((cf, x, c.title, dup, msg))
                except:
                    print_err("           ")
        
        fpclib.TABULATION -= 1
        fpclib.DEBUG_LEVEL = dl
        
        con.close()
        
        if ui:
            ui.rdata = results
            ui.update = True
            unfreeze()
    
    def find_msg(c, cur, src_chk):
        platform = c.platform
        
        # Check launch command
        cmd = c.cmd
        if cmd and len(cmd) > 7:
            cmd = cmd[7:]
            cur.execute(
                "SELECT id FROM game WHERE platform = ? AND (launchCommand LIKE ? OR launchCommand LIKE ? OR launchCommand LIKE ?)",
                (platform, "%"+cmd, "%"+cmd+"?%", "%"+cmd+'"%')
            )
            x = cur.fetchone()
            if x: return x[0], "Yes", "Launch command found"
        
        # Check source url
        if src_chk:
            src = c.src
            if src and len(src) > 7:
                src = src[7:]
                cur.execute(
                    "SELECT id FROM game WHERE platform = ? AND (source LIKE ? OR source LIKE ?)",
                    (platform, "%"+src, "%"+src+' %')
                )
                x = cur.fetchone()
                if x: return x[0], "Yes", "Source url found"
        
        # Check title and alternate titles
        if c.title:
            titles = [c.title]
            alts = c.alts
            if alts:
                if type(alts) == str:
                    for alt in alts.split(";"):
                        salt = alt.strip()
                        if salt:
                            titles.append(salt)
                else:
                    for alt in alts:
                        salt = alt.strip()
                        if salt:
                            titles.append(salt)
            
            # Exact title match
            for title in titles:
                cur.execute(
                    "SELECT id FROM game WHERE platform = ? AND (title = ? OR alternateTitles = ? OR alternateTitles LIKE ? OR alternateTitles LIKE ? OR alternateTitles LIKE ?)",
                    (platform, title, title, '%; '+title, title+'; %', '%; '+title+'; %')
                )
                x = cur.fetchone()
                if x: return x[0], "Probably", "Exact title found"
            
            # Partial title match
            for title in titles:
                comps, args = [], [platform]
                for keyword in SPACES.sub(" ", title.strip()).split(" "):
                    comps.append('(title LIKE ? OR alternateTitles LIKE ?)')
                    key = f'%{keyword}%'
                    args.extend((key, key))
                cur.execute("SELECT id FROM game WHERE platform = ? AND " + ' AND '.join(comps), args)
                x = cur.fetchone()
                if x: return x[0], "Probably", "Title parts found"
        
        return None, "Not Likely", ""
    
    def search(self):
        freeze("DeDuping Curations")
        folder = self.curations.get()
        db = self.parent.database.get()
        src_chk = self.src_chk.get()
        if folder and db:
            threading.Thread(target=lambda: DeDuper.i_search(folder, db, src_chk, self), daemon=True).start()

class Lister(tk.Frame):
    def __init__(self, parent):
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
        except:
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
        nohsb = False
        if "nohsb" in kwargs:
            nohsb = kwargs["nohsb"]
            del kwargs["nohsb"]
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.txt = tk.Text(self, **kwargs)
        self.txt.delete("0.0", "end")
        self.txt.grid(row=0, column=0, sticky="nsew")
        
        txtV = ttk.Scrollbar(self, orient="vertical", command=self.txt.yview)
        self.txt.configure(yscrollcommand=txtV.set)
        txtV.grid(row=0, column=1, sticky="ns")
        
        if not nohsb:
            txtH = ttk.Scrollbar(self, orient="horizontal", command=self.txt.xview)
            self.txt.configure(xscrollcommand=txtH.set)
            txtH.grid(row=1, column=0, sticky="ew")

class ScrolledTreeview(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        widths = ()
        if "widths" in kwargs:
            widths = kwargs["widths"]
            del kwargs["widths"]
        #nohsb = False
        #if "nohsb" in kwargs:
        #    nohsb = kwargs["nohsb"]
        #    del kwargs["nohsb"]
        command = None
        if "command" in kwargs:
            command = kwargs["command"]
            del kwargs["command"]
        
        self.tree = ttk.Treeview(self, **kwargs)
        self.tree.grid(row=0, column=0, sticky="nsew")
        if "columns" in kwargs:
            if command:
                for i, text in enumerate(kwargs["columns"]):
                    self.tree.heading('#'+str(i+1), text=text, command=functools.partial(command, i+1))
            else:
                for i, text in enumerate(kwargs["columns"]):
                    self.tree.heading('#'+str(i+1), text=text)
            if widths:
                for i in range(len(kwargs["columns"])):
                    self.tree.column("#"+str(i+1), minwidth=10, width=widths[0])
        
        if command: self.tree.heading("#0", text="Name", command=lambda: command(0))
        else: self.tree.heading("#0", text="Name")
        
        if widths: self.tree.column("#0", minwidth=10, width=widths[0])
        
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        treeV = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=treeV.set)
        treeV.grid(row=0, column=1, sticky="ns")
        
        #if not nohsb:
        #    treeH = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        #    self.tree.configure(xscrollcommand=treeH.set)
        #    treeH.grid(row=1, column=0, sticky="ew")
        
    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "tree"), name)

class Tooltip:
    '''
    It creates a tooltip for a given widget as the mouse goes on it.

    http://stackoverflow.com/questions/3221956/what-is-the-simplest-way-to-make-tooltips-in-tkinter/36221216#36221216
    http://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter

    - Originally written by vegaseat on 2014.09.09.
    - Modified to include a delay time by Victor Zaccardo on 2016.03.25.
    - Modified
        - to correct extreme right and extreme bottom behavior,
        - to stay inside the screen whenever the tooltip might go out on
          the top but still the screen is higher than the tooltip,
        - to use the more flexible mouse positioning,
        - to add customizable background color, padding, waittime and
          wraplength on creation
      by Alberto Vassena on 2016.11.05.
    - Modified by mathgeniuszach to be smaller.
    '''

    def __init__(self, widget, *, bg='#FFFFFF', pad=(0, 0, 0, 0), text='widget info', waittime=400, wraplength=250):
        self.waittime = waittime  # in miliseconds, originally 500
        self.wraplength = wraplength  # in pixels, originally 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.onEnter)
        self.widget.bind("<Leave>", self.onLeave)
        self.widget.bind("<ButtonPress>", self.onLeave)
        self.bg = bg
        self.pad = pad
        self.id = None
        self.tw = None

    def onEnter(self, event=None):
        self.schedule()
    def onLeave(self, event=None):
        self.unschedule()
        self.hide()
    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show)
    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show(self):
        def tip_pos_calculator(widget, label, *, tip_delta=(10, 5), pad=(5, 3, 5, 3)):
            w = widget

            s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()
            width, height = (
                pad[0] + label.winfo_reqwidth() + pad[2],
                pad[1] + label.winfo_reqheight() + pad[3]
            )

            mouse_x, mouse_y = w.winfo_pointerxy()
            x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
            x2, y2 = x1 + width, y1 + height

            x_delta = x2 - s_width
            if x_delta < 0:
                x_delta = 0
            y_delta = y2 - s_height
            if y_delta < 0:
                y_delta = 0

            offscreen = (x_delta, y_delta) != (0, 0)
            if offscreen:
                if x_delta:
                    x1 = mouse_x - tip_delta[0] - width

                if y_delta:
                    y1 = mouse_y - tip_delta[1] - height

            offscreen_again = y1 < 0  # out on the top
            if offscreen_again:
                y1 = 0

            return x1, y1

        bg = self.bg
        pad = self.pad
        widget = self.widget

        # Creates a toplevel window
        self.tw = tk.Toplevel(widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)

        win = tk.Frame(self.tw, background=bg, borderwidth=0)
        label = tk.Label(win, text=self.text, justify=tk.LEFT, background=bg, relief=tk.SOLID, borderwidth=1, wraplength=self.wraplength)

        label.grid(padx=(pad[0], pad[2]), pady=(pad[1], pad[3]), sticky=tk.NSEW)
        win.grid()

        self.tw.wm_geometry("+%d+%d" % tip_pos_calculator(widget, label))

    def hide(self):
        if self.tw: self.tw.destroy()
        self.tw = None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        try:
            print("[INFO] Launching fpcurator GUI variant. Launch the program with the --help flag to see command line usage.")
            MAINFRAME = Mainframe()
            MAINFRAME.mainloop()
        except Exception as e:
            tkm.showerror(message=f"Fatal {e.__class__.__name__}: {str(e)}")
            traceback.print_exc()
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
        