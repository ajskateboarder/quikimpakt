from flask import *
from .pubmed import pubmed
import zipfile
import base64
import os

# Web endpoint router thing
app = Flask('__main__')

@app.get('/')
def index():
  return open('./application/static/html/index.html',encoding='utf-8').read()

@app.get('/assets/<f>/')
def assetsf(f):
  if '/' not in f and os.path.isfile('./application/static/img/{}'.format(f)):
    return send_file('./application/static/img/{}'.format(f))
  else:
    abort(404)

@app.get('/build/')
def build():
  args = request.args
  if args.get('q'):
    pubmed.pubmed().constructdata(args.get('q'), 'results.txt')
    with zipfile.ZipFile('./application/pubmed/results.zip', 'w') as zipobj:
      for folder, subfolders, filenames in os.walk('./application/pubmed/results'):
        for filename in filenames:
          zipobj.write(os.path.join(folder, filename), os.path.basename(os.path.join(folder, filename)))
    send_file('./application/pubmed/results.zip')
    return open('./application/static/html/contentpre.html')\
      .read()\
      .replace('||base1||', 'data:image/png;base64,'+base64.b64encode(open('./application/pubmed/results/cloud.png', 'rb').read()).decode('utf-8'))\
      .replace('||base2||', 'data:image/png;base64,'+base64.b64encode(open('./application/pubmed/results/drugcloud.png', 'rb').read()).decode('utf-8'))\
      .replace('||base3||', 'data:image/png;base64,'+base64.b64encode(open('./application/pubmed/results/structure.png', 'rb').read()).decode('utf-8'))
  else:
    abort(404)

@app.url_value_preprocessor
def after(endpoint, r):
  try:
    os.remove('./application/pubmed/results.zip')
  except FileNotFoundError: pass

app.run(host='0.0.0.0')