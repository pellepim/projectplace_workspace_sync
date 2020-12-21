#!/usr/bin/env python3
import os
if os.path.dirname(__file__):
    os.chdir(os.path.dirname(__file__))
import models.structure
import argparse
import shutil
import logging
import config
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

parser = argparse.ArgumentParser(description='Synchronize workspace documents for a Projectplace Enterprise Account')
parser.add_argument('-c', '--clean', action='store_const', const=True,
                    help='Flag to start a clean sync (deletes local database)')
parser.add_argument('-s', '--sync', action='store_const', const=True, help='Flag to synchronize local database with active Projectplace content')
parser.add_argument('-d', '--download', action='store_const', const=True, help='Flag to download files that are not marked as downloaded yet')
parser.add_argument('-m', '--html', action='store_const', const=True, help='Flag to generate html-pages that can be used to navigate workspace content')
parser.add_argument('-st', '--silent', action='store_const', const=True, help='If specified, hides progress information from stdout')
args = parser.parse_args()

if args.clean:
    logging.info('Trying to clean')
    confirm_clean = input('Running with -c will delete all existing local information/documents. Are you sure? (type "yes")?')
    logging.info(confirm_clean)
    if confirm_clean.lower() == 'yes':
        if os.path.isfile('data.sqlite'):
            logging.info('Removing entire sqlitedatabase (data.sqlite file)')
            os.remove('data.sqlite')
        if os.path.isdir(config.conf.FILESTORAGE_PATH):
            logging.info('Removing entire file structure %s' % config.conf.FILESTORAGE_PATH)
            shutil.rmtree(config.conf.FILESTORAGE_PATH)
        exit()
    else:
        logging.info('Cancelling operation')
        exit()

structure = models.structure.Structure()

if args.sync:
    structure.synchronize()

if args.download:
    structure.download_docs()

if not args.sync and not args.html and not args.download:
    logging.info('Not doing anything, specify -s to sync database, -d to download pending documents, and -m to render html, or all three at the same time.')
