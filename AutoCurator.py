import fpclib
import sys, glob, os, logging

urls = []
links = []
priorities = {}

def qexit(code=0):
    input('\nPress enter to exit...')
    sys.exit(code)

def get_priority(obj):
    return priorities[obj[1].__name__]

def to_bool(s):
    l = s.lower()
    if l in ['true', 'yes', 'on', '1']:
        return True
    elif l in ['false', 'no', 'off', '0']:
        return False
    else:
        raise ValueError('options.ini file has invalid value "' + s + '"')

try:
    # Get options
    o = {}
    opl = fpclib.read_lines('options.ini')
    for line in opl:
        if line[0] not in ['[', '#']:
            il = line.index('=')
            o[line[:il]] = line[il+1:]
    
    fpclib.DEBUG_LEVEL = int(o['DEBUG_LEVEL'])
    
    SITES_FOLDER = o['SITES_FOLDER']
    OUTPUT_FOLDER = o['OUTPUT_FOLDER']
    ERROR_LOG = o['ERROR_LOG']
    
    SAVE = to_bool(o['SAVE'])
    TITLES = to_bool(o['TITLES'])
    IGNORE_ERRS = to_bool(o['IGNORE_ERRS'])
    
    # Get urls
    fpclib.debug('Parsing for urls', 1)
    fpclib.TABULATION += 1
    if (len(sys.argv) > 1):
        for arg in sys.argv[1:]:
            if arg.startswith('-'):
                fpclib.debug('Got url "{}"', 1, arg[1:])
                urls.append(arg[1:])
            else:
                try:
                    f_urls = fpclib.read_lines(arg)
                    fpclib.debug('Got {} urls from "{}"', 1, len(f_urls), arg)
                    urls.extend(f_urls)
                except:
                    fpclib.debug('"{}" file not found or is invalid! Skipping', 1, arg, pre='[ERR]  ')
    
    # Exit if no urls were found.
    if not urls:
        fpclib.debug('No urls were found to curate. Try dragging and dropping a txt file onto the script!', 1, pre='[ERR]  ')
        fpclib.TABULATION -= 1
        qexit(1)
    fpclib.TABULATION -= 1

    # Get links, which is everything from the sites folder. Append to the links variable for each found import.
    fpclib.debug('Parsing for links', 1)
    
    fpclib.TABULATION += 1
    sys.path.insert(0, SITES_FOLDER)
    for py_file in glob.glob(os.path.join(SITES_FOLDER, '*.py')):
        try:
            name = py_file[py_file.rfind('\\')+1:-3]
            m = __import__(name)
            
            priority = 0
            try:
                priority = m.priority
            except:
                pass
            priorities[name] = priority
            
            links.append((m.regex, getattr(m, name)))
            fpclib.debug('Found class "{}"', 1, name)
        except Exception as e:
            fpclib.debug('Skipping class "{}", error:', 1, name)
            print()
            logging.exception(' ', exc_info=True)
            print()
    
    sys.path.pop(0)
    fpclib.TABULATION -= 1
    links.sort(key=get_priority, reverse=True)

    if not links:
        fpclib.debug('No site-definitions were found', 1, pre='[ERR]  ')
        qexit(1)

    # Curate urls that were found.
    cwd = os.getcwd()
    fpclib.make_dir(OUTPUT_FOLDER, True)
    errs = fpclib.curate_regex(urls, links, use_title=TITLES, save=SAVE, ignore_errs=IGNORE_ERRS)
    os.chdir(cwd)

    # Write errors to file if there were any.
    if errs:
        fpclib.write(ERROR_LOG, [url for url, err, data in errs])
    
    qexit()
except Exception as e:
    print()
    logging.exception(' ', exc_info=True)
    qexit(1)