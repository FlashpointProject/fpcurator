# fpcurator
fpcurator is a Python and fpclib powered tool for auto-generating curations for Flashpoint.

If you don't want to install python to use fpcurator, check the releases page for a standalone executable.

## Basic Usage

To curate a list of urls, create a text file and put all the urls you want to curate into that file (one per line). After that, you should be able to drag and drop the file onto the AutoCurator script/executable and it will attempt to create partial curations for every file in the list. By default, the curations will be put in a folder named `output`, and any failed urls will be put into a file named `errors.txt`.

If you want to change _how_ the script works, change any of the settings in the `options.ini` file.