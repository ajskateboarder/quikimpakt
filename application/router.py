from flask import *
from .pubmed import pubmed
import zipfile
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
    return send_file('./application/pubmed/results.zip')
  else:
    abort(404)

@app.url_value_preprocessor
def after(endpoint, r):
  try:
    os.remove('./application/pubmed/results.zip')
  except FileNotFoundError: pass

app.run(host='0.0.0.0')