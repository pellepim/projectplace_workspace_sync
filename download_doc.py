import config
import logging
import argparse
import sdk.connection
import os

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s %(name)s - %(levelname)s: %(message)s')

parser = argparse.ArgumentParser(description='Download a single document from a Projectplace Enterprise Account')
parser.add_argument('-i', '--document_id', help='The ID of the document to download', required=True)
parser.add_argument('-w', '--workspace_id', help='The ID of the workspace we are downloading from', required=True)
parser.add_argument('-s', '--suffix', help='The suffix (file ending e.g xlsx, docx etc) of the file', required=True)

args = parser.parse_args()

document_id = int(args.document_id)

doc_response = sdk.connection.download_doc(document_id)

file_location = os.path.join(config.conf.FILESTORAGE_PATH, str(args.workspace_id))

if not os.path.exists(file_location):
    os.makedirs(file_location)

file_path = os.path.join(file_location, '%d.%s' % (document_id, args.suffix))

with open(file_path, 'wb') as fp:
    fp.write(doc_response.content)


