import os
if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))
import models.structure
import argparse
import shutil
import logging


logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s %(name)s - %(levelname)s: %(message)s')

parser = argparse.ArgumentParser(description='Synchronize workspace documents for a Projectplace Enterprise Account')
parser.add_argument('-c', '--clean', action='store_const', const=True,
                    help='Flag to start a clean sync (deletes local database)')
parser.add_argument('-s', '--sync', action='store_const', const=True, help='Flag to synchronize local database with active Projectplace content')
parser.add_argument('-d', '--download', action='store_const', const=True, help='Flag to download files that are not marked as downloaded yet')
parser.add_argument('-m', '--html', action='store_const', const=True, help='Flag to generate html-pages that can be used to navigate workspace content')

args = parser.parse_args()

if args.clean:
    confirm_clean = input('Running with -c will delete all existing local information/documents. Are you sure? (type "yes")?')

    if confirm_clean.lower() == 'yes':
        try:
            os.remove('.data')
        except FileNotFoundError:
            pass
        shutil.rmtree('localdata')
    else:
        print('Cancelling operation')
        exit()

structure = models.structure.Structure()

if args.sync:
    structure.synchronize()

if args.download:
    structure.download_docs()

if args.html:
    structure.render_html()

if not args.sync and not args.html and not args.download:
    print('Not doing anything, specify -s to sync database, -d to download pending documents, and -m to render html, or all three at the same time.')
