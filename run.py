import models.structure
import argparse
import os

parser = argparse.ArgumentParser(description='Synchronize workspace documents for a Projectplace Enterprise Account')
parser.add_argument('-c', '--clean', action='store_const', const=True,
                    help='Flag to start a clean sync (deletes local database)')
parser.add_argument('-s', '--sync', action='store_const', const=True, help='Flag to synchronize local database with active Projectplace content, and to download needed files')
parser.add_argument('-m', '--html', action='store_const', const=True, help='Flag to generate html-pages that can be used to navigate workspace content')

args = parser.parse_args()

if args.clean:
    os.remove('.data')

structure = models.structure.Structure()

if args.sync:
    structure.synchronize()

if args.html:
    structure.render_html()

if not args.sync and not args.html:
    print('Not doing anything, specify -s to sync and -m to render html, or both.')
