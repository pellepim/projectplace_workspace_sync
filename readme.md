# Sync projectplace workspace documents

This is a tool intended for IT-personnel in an organisation using 
[Projectplace](https://www.projectplace.com).

It downloads all documents in the main document archive in all workspaces in a Projectplace Enterprise Account, 
and on subsequent runs downloads only new or modified files.

It then renders a HTML-page structure providing the opportunity to navigate the workspaces, folders and 
documents.

It is suitable to set up as a recurring task, for example nightly.

## Poor man's backup
When workspaces are archived or terminated in Projectplace - this script will retain data from 
those workspaces indefinitely (unless explicitly deleted). The same goes for documents that are deleted 
from workspaces in Projectplace. If they have been downloaded by this script once, the local database will 
retain those document.

Basically, the local version of the workspaces will behave as if nothing is ever deleted from document archives.

If documents are moved, or renamed - that will be reflected however. But as soon as they are deleted they will
remain as is.

## Set up

### 1. Config
First of all you need to request a "robot" from Projectplace. This is only applicable for Projectplace enterprise 
accounts. Then enter the information you received from projectplace in config.json as follows:

    {
        "consumer_key": "ENTER YOUR APPLICATION KEY",
        "consumer_secret": "ENTER YOUR APPLCIATION SECRET",
        "access_token": "ENTER YOUR TOKEN KEY",
        "access_token_secret": "ENTER YOUR TOKEN SECRET",
        "host": "https://api.projectplace.com"
    }

### 2. Limit to specific workspaces (optional)
If you want to limit the synchronisation to certain specific workspaces, specify an array of
workspace_ids such as:

    {
        ...
        "host": "https://api.projectplace.com",
        "workspace_ids": [3281238,3212309]
    }

### 3. Python environment
This script is written assuming python3 - make sure you have python3 available on your computer.

1. Start by cloning the repo
2. In the resulting directory type `virtualenv VIRTUAL -p python3`
3. Then type `source VIRTUAL/bin/activate` to enter the virtual environment
4. Run `pip install -r requirements.txt` to install necessary packages.


## Running
### 1. Run sync

`python run.py -s`

This will take a long time for the first run, as it populates a local sqlite database with all the
relevant information and also downloads each document in turn.

The sqlite database is saved in the local file `.data`.

### 2. Download pending files

Running the sync (see step 1) sets up a local datastructure, but it doesn't actually download any files. To
accomplish this run:

`python run.py -d`

All documents marked as in need of download during the synch-step are now downloaded in turn.

Each document is saved in directory
`localdata` sorted under workspace IDs. The file name from Projectplace will not be maintained. For example
"Resume.docx" will be visible as a unique ID, followed by the file ending - such as `27182376327.docx`.

### 3. Render html

`python run.py -m`

This should be relatively fast as it uses the local sqlite database to generate html-pages which can be used
to navigate Workspaces, Folders and to view documents.

Once run, simply double click `localdata/html/index.html` to navigate the workspace documents.

### 4. Do it all in one fell swoop
You can run all steps above by specifying

`python run.py -s -d -m`

This will synchronize the database, download files and render new HTML-pages.

## Danger Zone

### Delete data
 * If you want to rerun the synchronization from the beginning, supply the `-c` flag. Please note that you may
   permanently loose data if you do so. 
