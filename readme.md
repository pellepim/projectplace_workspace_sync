# Sync projectplace workspace data

## 1. Set up config.json

First of all you need to request a "robot" from Projectplace. This is only applicable for Projectplace enterprise 
accounts. Then enter the information you received from projectplace in config.json as follows:

    {
        "consumer_key": "ENTER YOUR APPLICATION KEY",
        "consumer_secret": "ENTER YOUR APPLCIATION SECRET",
        "tokey_key": "ENTER YOUR TOKEN KEY",
        "token_secret": "ENTER YOUR TOKEN SECRET"
    }
    
## 2. Run sync

`python run.py -s`

This will take a long time for the first run, as it populates a local sqlite database with all the
relevant information and also downloads each document in turn.

The sqlite database is saved in the local file `.data`. Each document is saved in directory
`localdata` sorted under workspace IDs. The file name from Projectplace will not be maintained. For example
"Resume.docx" will be visible as a unique ID, followed by the file ending - such as `27182376327.docx`.

The real document names are stored in the sqlite database however, and this is used to render html-pages for
navigation.

## 3. Render html

`python run.py -m`

This should be relatively fast as it uses the local sqlite database to generate html-pages which can be used
to navigate Workspaces, Folders and to view documents.

Once run, simply double click `localdata/html/index.html` to navigate the workspace documents.