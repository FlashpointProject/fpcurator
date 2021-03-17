import fpclib
import os, sys, traceback, sqlite3, re, difflib, codecs, glob, json, datetime
import bs4, zipfile
try:
    import Levenshtein
except: pass

import tkinterhtml as tkhtml
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkm

HEADINGS = ['TABLE OF CONTENTS', 'SUMMARY', 'DUPLICATE NAMES', 'DEFINITELY IN FLASHPOINT', 'PROBABLY IN FLASHPOINT', 'MAYBE IN FLASHPOINT', 'PROBABLY NOT IN FLASHPOINT', 'DEFINITELY NOT IN FLASHPOINT']
TEXTS = {
    'header': 'Search performed on %s\nDISCLAIMER: ALWAYS CHECK THE MASTER LIST AND DISCORD CHANNEL BEFORE CURATING, EVEN IF SOMETHING IS LISTED HERE AS NOT CURATED\n\n',
    'divider': '--------------- %s ---------------\n',
    'line': '-----------------------------------\n',
    'tbc.note': 'Note: use CTRL+F to find these sections quickly.\n\n',
    'info.numerics': ' (%d - %.3f%%)',
    'sum.totalgames': '%d Games Total',
    'sum.titlematch': '%d games match titles',
    'sum.sourcematch': '%d games match part of their source in the master list',
    'sum.either': '%d games match either query',
    'sum.lowmetric': '%d games have a very low similarity metric',
    'sum.priority': '%d games (%.3f%%) probably need curating',
    'sum.priority2': '%d games (%.3f%%) definitely need curating',
    'dup.note': 'These are a list of games that have been omitted from the search because they share the same name with another game in the list',
    'p5.exacturl': 'Exact url matches',
    'p5.partialurl': 'Exact url matches ignoring "http:// and any extra parentheses"',
    'p5.titleandsdp': 'Title matches with games that match part of their source/developer/publisher',
    'p4.titlestartsandssdp': 'Title starts another Title (>10 characters) that matches part of its source/developer/publisher',
    'p4.titleonly': 'Title matches',
    'p4.titlestartstitle': 'Title starts another Title (>10 characters)',
    'p4.titleintitle': 'Title is in another Title (>10 characters)',
    'p4.highmetric': 'Has a high similarity metric (>95%)',
    'p3.leftovers': 'Leftovers',
    'p3.leftovers2': 'These are the games that didn\'t match any query',
    'p2.lowmetric': 'Has a low similarity metric (<85%)',
    'p1.verylowmetric': 'Has a very low similarity metric (<75%)'
}

TITLE = "fpcurator v1.1.0"
ABOUT = "Created by Zach K - v1.1.0"

SITES_FOLDER = "sites"

fpclib.DEBUG_LEVEL = 4

AM_PATTERN = re.compile('[\W_]+')
AMS_PATTERN = re.compile('([^\w;]|_)+')

def set_entry(entry, data):
    entry.delete(0, "end")
    entry.insert(0, data)

def printfl(data):
    print(data, end="")
    sys.stdout.flush()

class Mainframe(tk.Tk):
    def __init__(self):
        # Create window
        super().__init__()
        self.minsize(645, 600)
        self.title(TITLE)
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        
        # Add tabs
        tabs = ttk.Notebook(self)
        tabs.pack(expand=True, fill="both", padx=5, pady=5)
        
        self.downloader = Downloader()
        self.autocurator = AutoCurator()
        self.searcher = Searcher()
        self.lister = Lister()
        
        tabs.add(self.autocurator, text="Auto Curator")
        tabs.add(self.downloader, text="Download URLs")
        tabs.add(self.searcher, text="Search")
        tabs.add(self.lister, text="Wiki Data")
        
        # Add help and about label
        bframe = tk.Frame(self)
        bframe.pack(expand=False, padx=5, pady=(0, 5))
        
        label = ttk.Label(bframe, text=ABOUT)
        label.pack(side="left")
        help_button = ttk.Button(bframe, text="Help", command=self.show_help)
        help_button.pack(side="left", padx=5)
        
        # Add debug level entry
        self.debug_level = tk.StringVar()
        self.debug_level.set(str(fpclib.DEBUG_LEVEL))
        self.debug_level.trace("w", self.set_debug_level)
        dlabel = ttk.Label(bframe, text="Debug Level: ")
        dlabel.pack(side="left")
        debug_level = ttk.Entry(bframe, textvariable=self.debug_level)
        debug_level.pack(side="left")
        
        # Exists to prevent more than one help menu from opening at a time
        self.help = None
        
        # Load GUI state from last close
        self.load()
    
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
        self.save()
        self.destroy()
    
    def save(self):
        autocurator = {}
        downloader = {}
        searcher = {}
        
        data = {"autocurator": autocurator, "downloader": downloader, "searcher": searcher, "debug_level": self.debug_level.get()}
        
        # Save autocurator data
        autocurator["output"] = self.autocurator.output.get()
        
        autocurator["save"] = self.autocurator.save.get()
        autocurator["silent"] = self.autocurator.silent.get()
        autocurator["titles"] = self.autocurator.titles.get()
        autocurator["clear"] = self.autocurator.clear.get()
        autocurator["show_done"] = self.autocurator.show_done.get()
        
        autocurator["urls"] = self.autocurator.stxt.txt.get("1.0", "end")
        
        # Save downloader data
        downloader["output"] = self.downloader.output.get()
        
        downloader["original"] = self.downloader.original.get()
        downloader["keep_vars"] = self.downloader.keep_vars.get()
        downloader["clear"] = self.downloader.clear.get()
        downloader["show_done"] = self.downloader.show_done.get()
        
        downloader["urls"] = self.downloader.stxt.txt.get("1.0", "end")
        
        # Save searcher data
        searcher["database"] = self.searcher.database.get()
        searcher["sources"] = self.searcher.sources.get()
        searcher["devpubs"] = self.searcher.devpubs.get()
        
        searcher["priorities"] = self.searcher.priorities.get()
        searcher["log"] = self.searcher.log.get()
        searcher["strip"] = self.searcher.strip.get()
        searcher["exact_url"] = self.searcher.exact_url.get()
        searcher["difflib"] = self.searcher.difflib.get()
        
        searcher["titles"] = self.searcher.stxta.txt.get("1.0", "end")
        searcher["urls"] = self.searcher.stxtb.txt.get("1.0", "end")
        
        with open("data.json", "w") as file: json.dump(data, file)
    
    def load(self):
        try:
            with open("data.json", "r") as file: data = json.load(file)
            
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
            txt.delete("1.0", "end")
            txt.insert("1.0", autocurator["urls"])
            
            # Save downloader data
            set_entry(self.downloader.output, downloader["output"])
            
            self.downloader.original.set(downloader["original"])
            self.downloader.keep_vars.set(downloader["keep_vars"])
            self.downloader.clear.set(downloader["clear"])
            self.downloader.show_done.set(downloader["show_done"])
            
            txt = self.downloader.stxt.txt
            txt.delete("1.0", "end")
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
            txt.delete("1.0", "end")
            txt.insert("1.0", searcher["titles"])
            
            txt = self.searcher.stxtb.txt
            txt.delete("1.0", "end")
            txt.insert("1.0", searcher["urls"])
            
        except FileNotFoundError: pass

class Help(tk.Toplevel):
    def __init__(self, parent):
        # Create window
        super().__init__(bg="white")
        self.minsize(445, 400)
        self.geometry("745x700")
        self.protocol("WM_DELETE_WINDOW", self.exit_window)
        self.parent = parent
        
        # Create htmlframe for displaying help information
        txt = tkhtml.HtmlFrame(self, vertical_scrollbar="auto", horizontal_scrollbar="auto")
        txt.set_content(fpclib.read("help.html"))
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
        curate = ttk.Button(tframe, text="Curate", command=self.curate)
        curate.pack(side="left", padx=5)
        
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
        clear = tk.Checkbutton(cframe, bg="white", text="Clear URLs", var=self.clear)
        clear.pack(side="left", padx=5)
        show_done = tk.Checkbutton(cframe, bg="white", text='Show Done', var=self.show_done)
        show_done.pack(side="left")
        
        # Create site definition display
        dframe = tk.Frame(self, bg="white")
        dframe.pack()
        
        self.defcount = tk.StringVar()
        self.defcount.set("0 site definitions found")
        defcount = tk.Label(dframe, bg="white", textvariable=self.defcount)
        defcount.pack(side="left")
        
        reload = ttk.Button(dframe, text="Reload", command=self.reload)
        reload.pack(side="left", padx=5)
        self.reload()
        
        # Create panel for inputting urls
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=5)
    
    def folder(self):
        # For changing the output folder
        folder = tkfd.askdirectory()
        if folder:
            self.output.delete(0, "end")
            self.output.insert(0, folder)
    
    def get_defs(silent=False):
        defs = []
        priorities = {}
    
        # Parse for site definitions
        fpclib.debug('Parsing for site definitions', 1)
        fpclib.TABULATION += 1
        sys.path.insert(0, SITES_FOLDER)
        for py_file in glob.glob(os.path.join(SITES_FOLDER, '*.py')):
            try:
                name = py_file[py_file.rfind('\\')+1:-3]
                m = __import__(name)
                
                priority = 0
                try: priority = m.priority or 0
                except: pass
                priorities[name] = priority
                
                defs.append((m.regex, getattr(m, name)))
                fpclib.debug('Found class "{}"', 1, name)
            except Exception as e:
                fpclib.debug('Skipping class "{}", error:', 1, name)
                print()
                traceback.print_exc()
                print()
        
        fpclib.TABULATION -= 1
        
        # Print count of site definitions
        if defs: defs.sort(key=lambda x: priorities[x[1].__name__], reverse=True)
        else: 
            if not silent: fpclib.debug('No valid site-definitions were found', 1)
        
        return defs
    
    def reload(self):
        # Initialize defs and priorities
        self.defs = AutoCurator.get_defs()
        self.defcount.set(f"{len(self.defs)} site defintitions found")
    
    def curate(self):
        txt = self.stxt.txt
        # Get urls and curate them with all site definitions
        urls = [i.strip() for i in txt.get("1.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
        
        cwd = os.getcwd()
        fpclib.make_dir(self.output.get(), True)
        errs = fpclib.curate_regex(urls, self.defs, use_title=self.titles.get(), save=self.save.get(), ignore_errs=self.silent.get())
        os.chdir(cwd)
        
        if self.show_done.get():
            if errs:
                if len(errs) == len(urls):
                    tkm.showerror(message=f"All {len(errs)} urls could not be curated.")
                else:
                    tkm.showinfo(message=f"Successfully curated {len(urls)-len(errs)}/{len(urls)} urls.\n\n{len(errs)} urls could not be downloaded.")
            else:
                tkm.showinfo(message=f"Successfully curated {len(urls)} urls.")
            
        if self.clear.get():
            txt.delete("1.0", "end")
            print(errs)
            if errs: txt.insert("1.0", "\n".join([i for i, e, s in errs]))

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
        download = ttk.Button(tframe, text="Download", command=self.download)
        download.pack(side="left", padx=5)
        
        # Create checkboxes
        cframe = tk.Frame(self, bg="white")
        cframe.pack(padx=5)
        
        self.original = tk.BooleanVar()
        self.original.set(True)
        self.keep_vars = tk.BooleanVar()
        self.clear = tk.BooleanVar()
        self.clear.set(True)
        self.show_done = tk.BooleanVar()
        self.show_done.set(True)
        
        original = tk.Checkbutton(cframe, bg="white", text='Remove "web.archive.org"', var=self.original)
        original.pack(side="left")
        keep_vars = tk.Checkbutton(cframe, bg="white", text="Keep URLVars", var=self.keep_vars)
        keep_vars.pack(side="left", padx=5)
        clear = tk.Checkbutton(cframe, bg="white", text="Clear URLs", var=self.clear)
        clear.pack(side="left")
        show_done = tk.Checkbutton(cframe, bg="white", text='Show Done', var=self.show_done)
        show_done.pack(side="left", padx=5)
        
        # Create panel for inputting urls to download
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=5)
    
    def folder(self):
        # For changing the output directory
        folder = tkfd.askdirectory()
        if folder:
            self.output.delete(0, "end")
            self.output.insert(0, folder)
    
    def download(self):
        txt = self.stxt.txt;
        try:
            links = [i.strip() for i in txt.get("1.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
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
                    txt.delete("1.0", "end")
                    if errs:
                        txt.insert("1.0", "\n".join([i for i, e in errs]))
            else:
                tkm.showinfo(message="You must specify at least one url to download.")
        except Exception as e:
            print("[ERR]  Failed to download urls, err ", end="")
            traceback.print_exc()
            tkm.showerror(message=f"Failed to download urls.\n{e.__class__.__name__}: {str(e)}")

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
        load = ttk.Button(tframe, text="Load", command=self.load)
        load.pack(side="left")
        search = ttk.Button(tframe, text="Search", command=self.search)
        search.pack(side="left", padx=5)
        
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
        
        # Panels
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
    
    def load(self):
        try:
            # Acquire the database!
            dbloc = self.database.get()
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
        except:
            print("[ERR]  Failed to load database, err ", end="")
            traceback.print_exc()
            tkm.showerror(message=f"Failed to load database. Ensure the the database provided is valid.\n{e.__class__.__name__}: {str(e)}")
    
    def search(self):
        print('[INFO] Initiating search')
        try:
            # Get input data
            period = time.time()
            printfl('[INFO] Parsing input data...')
            
            txta = self.stxta.txt
            txtb = self.stxtb.txt
            
            titles = [i.strip() for i in txta.get("1.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
            urls = [i.strip() for i in txtb.get("1.0", "end").replace("\r\n", "\n").replace("\r", "\n").split("\n") if i.strip()]
            #if urls and len(titles) != len(urls):
            if len(titles) != len(urls):
                print('Failed (input count mismatch)')
                tkm.showerror(message=f"Input data count mismatch: # of titles is {len(titles)}, while # of urls is {len(urls)}.")
                return
            input_count = len(titles)
            if input_count == 0:
                print('Failed (no data)')
                tkm.showerror(message=f"No input data to search with; you must provide at least one title and url to search with.")
                return
            
            # Get source regex
            try: src_regex = re.compile(self.sources.get())
            except:
                print('Failed (incorrect source regex)')
                tkm.showerror(message=f"Your source regex is formatted incorrectly.")
                return
            # Get devpubs regex
            try: dp_regex = re.compile(self.devpubs.get())
            except:
                print('Failed (incorrect dev/pub regex)')
                tkm.showerror(message=f"Your developer/publisher regex is formatted incorrectly.")
                return
            
            # Get options
            PRIORITIES = self.priorities.get()
            LOG = self.log.get()
            STRIP_SUBTITLES = self.strip.get()
            EXACT_URL_CHECK = self.exact_url.get()
            DIFFLIB = self.difflib.get()
            
            # Format input
            for i in range(input_count):
                title = titles[i]
                if STRIP_SUBTITLES:
                    colon = title.find(':')
                    title = title[0, colon]
                titles[i] = AM_PATTERN.sub('', title)
            
            print('Done (%.3f secs)' % (time.time() - period))
            
            
            
            # Check for duplicates
            period = time.time()
            print('[INFO] Checking for duplicates')
            duplicates = set()
            for i, title in enumerate(titles):
                print('       %d/%d - %d%% Complete' % (i, input_count, int(100 * i / input_count)), end='\r')
                if titles.count(title) > 1: duplicates.add(i)
            
            print('       %d/%d - %d%% Complete (%.3f secs)' % (input_count, input_count, 100, time.time() - period))
            print('       %d duplicates found.' % (len(duplicates)))
            
            
            
            # Load the database
            period = time.time()
            printfl('[INFO] Loading database...')
            try:
                raw_data = fpclib.read("search/database.tsv")
            except:
                try:
                    print('Failed')
                    print('[INFO] Attempting to load external database')
                    self.load()
                    data = fpclib.read("search/database.tsv")
                except:
                    return
            
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
                print('       %d/%d - %d%% Complete' % (i, data_count, int(100 * i / data_count)), end='\r')
                
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
            
            print('       %d/%d - %d%% Complete (%.3f secs)' % (data_count, data_count, 100, time.time() - period))
            print('       %d games match title' % (title_match_count))
            print('       %d games match source/dev/pub' % (sdp_match_count))
            print('       %d games match either' % (title_or_sdp_match_count))
            
            
            
            # Now comes the time to roll up our sleeves and search through the data
            period = time.time()
            period_item = time.time()
            print('[INFO] Performing main search')
            
            data_sources_str = "\n"+"\n".join(data_sources)
            sdp_matches_str = "\n"+"\n".join(sdp_matches)
            
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
            
            for i in range(input_count):
                print('       %d/%d - %d%% Complete (last took %.3f secs)' % (i, input_count, int(100 * i / input_count), time.time() - period_item), end='\r')
                period_item = time.time()
                
                # Duplicates get thrown out
                if i in duplicates:
                    duplicate.append(title + "\t" + url)
                    priorities.append('-1.0')
                    continue
                
                # Get title and url
                title = titles[i]
                url = urls[i]
                line = title + "\t" + url
                title_is_long = len(title) > 10
                
                if url and EXACT_URL_CHECK:
                    # Exact url matches
                    if url in data_sources:
                        url_matches.append(line)
                        priorities.append('5.0')
                        continue
                    
                    # Exact url matches ignoring protocol and other small data
                    colon = url.find(':')
                    if colon != -1 and colon+3 < len(url):
                        if url[colon+3] in data_sources_str:
                            partial_url_matches.append(line)
                            priorities.append('4.9')
                            continue
                
                # Title matches with games that match part of their source/developer/publisher
                if title in sdp_matches:
                    title_and_sdp_matches.append(line)
                    priorities.append('4.8')
                    continue
                
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
            print('       %d/%d - %d%% Complete (%.3f secs) (avg %.3f secs)' % (input_count, input_count, 100, time_took, time_took / input_count))
            # SUMMARY information
            probables = len(leftovers) + len(low_metric) + len(very_low_metric)
            print('  ' + TEXTS['sum.priority'] % (probables, probables * 100 / input_count))
            print('  ' + TEXTS['sum.priority2'] % (len(very_low_metric), len(very_low_metric) * 100 / input_count))
            print()
            
            # Save information!
            if PRIORITIES:
                printfl("Writing priorities to output file...")
                fpclib.write("search/priorities.tsv", '\n'.join(priorities))
                print("Done")
            if LOG:
                printfl("Writing to log file...")
                fpclib.make_dir("search")
                with codecs.open("log.txt", 'w', 'utf-8') as log_file:
                    # Sorter
                    sorter = lambda e: e[1]
                    
                    # Header
                    log_file.write(HEADER % (datetime.now().strftime('%Y-%m-%d')))
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
                    if (not OPTIONS['-r']):
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
        except:
            print("[ERR]  Failed to load database, err ", end="")
            traceback.print_exc()
            tkm.showerror(message=f"Search failed.\n{e.__class__.__name__}: {str(e)}")

class Lister(tk.Frame):
    def __init__(self):
        # Create panel
        super().__init__(bg="white")
        tframe = tk.Frame(self, bg="white")
        tframe.pack(padx=5, pady=5)
        
        self.choice = tk.StringVar()
        self.choice.set("Tags")
        c = ttk.Combobox(tframe, textvariable=self.choice, values=["Tags", "Platforms", "Game_Master_List", "Animation_Master_List"])
        c.pack(side="left")
        
        find = ttk.Button(tframe, text="Find", command=self.find)
        find.pack(side="left", padx=5)
        
        clear = ttk.Button(tframe, text="Clear", command=self.clear)
        clear.pack(side="left")
        
        self.stxt = ScrolledText(self, width=10, height=10, wrap="none")
        self.stxt.pack(expand=True, fill="both", padx=5, pady=(0, 5))
    
    def find(self):
        fpclib.debug("Getting all data from the {} page on the wiki", 1, self.choice.get())
        txt = self.stxt.txt
        txt.delete("1.0", "end")
        txt.insert("end", "\n".join(fpclib.get_fpdata(self.choice.get())))
    
    def clear(self):
        self.stxt.txt.delete("1.0", "end")

class ScrolledText(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.txt = tk.Text(self, **kwargs)
        txtV = ttk.Scrollbar(self, orient="vertical", command=self.txt.yview)
        txtH = ttk.Scrollbar(self, orient="horizontal", command=self.txt.xview)
        self.txt.configure(yscrollcommand=txtV.set, xscrollcommand=txtH.set)
        
        self.txt.grid(row=0, column=0, sticky="nsew")
        txtV.grid(row=0, column=1, sticky="ns")
        txtH.grid(row=1, column=0, sticky="ew")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

if __name__ == "__main__":
    Mainframe().mainloop()