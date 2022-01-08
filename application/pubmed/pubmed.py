from bs4 import BeautifulSoup
from urllib.parse import quote
from . import stopwords
from PIL import ImageDraw 
from PIL import ImageFont
from PIL import Image
import collections
import summarizer4u
import requests
import shutil
import random
import json
import os

# Cool functions that are organized to look like a pip module file
config = 'nooo go get your ownnn'

class pubmed:
  def __init__(self) -> None:
    pass
  def search(self, q:str) -> list:
    '''
    Search for PubMed articles (ex: tobacco smoking)
    '''
    r = requests.get('https://pubmed.ncbi.nlm.nih.gov/?term={}'.format(quote(q)))
    ts = BeautifulSoup(r.text, 'html.parser')

    results = []

    for item in ts.findAll('a', { 'class': 'docsum-title' }, href=True):
      results.append([str(item.text).replace('  ','').replace('\n',''),int(item['href'].replace('/',''))])
    
    self.results = results

    return self
  def getdocumentbyid(self, pmid) -> str:
    '''
    Get a PubMed article by an unique document ID (ex: 15552776)
    '''
    r = requests.get('https://pubmed.ncbi.nlm.nih.gov/{}'.format(pmid))
    ts = BeautifulSoup(r.text, 'html.parser')

    try:
      self.title = ts.find('h1', { 'class': 'heading-title' }).text.replace('\n', '').replace('  ', '')
      self.abstract = ts.find('div', { 'class': ['abstract-content', 'selected'] }).find('p').text.replace('\n', '').replace('  ', '')
      self.published = ts.find('span', { 'class': 'cit' }).text.split(';')[0]
      self.doi = ts.find('a', { 'class': 'id-link' }, href=True)['href']
    except AttributeError:
      self.title = None
      self.abstract = None
      self.published = None
      self.doi = None

    return self

  def constructdata(self, q:str, f:str) -> None:
    try:
      shutil.rmtree('./application/pubmed/results/')
    except FileNotFoundError:
      pass
    os.mkdir('./application/pubmed/results/')
    results = pubmed().search(q).results

    fobj = open('./application/pubmed/results/results.txt', 'a', encoding='utf-8')
    alltexts = []

    # summarize text
    for i in range(len(results)):
      try:
        dept2 = pubmed().getdocumentbyid(results[i][1])
        alltexts.append(dept2.abstract+' ')
      except TypeError:
        break
    fobj.write('Summary\n-------\n'+summarizer4u.summary(''.join(alltexts))+'\n\nAbstracts\n--------\n')
    
    # make word mesh
    img = Image.open('./application/pubmed/canvas.jpg')
    w, h = img.size
    draw = ImageDraw.Draw(img)
    text = collections.Counter(''.join(alltexts).split()).most_common()

    off = -10
    i = 0

    for word in text:
      size = 85

      if i == 30: break

      if word[1] >= 10: size += 20
      if word[1] >= 15: size += 20
      if word[1] >= 20: size += 20

      if word[0] not in stopwords.words and word[0].lower() not in q:
        draw.text((w/2+off+random.choice([-100,-50,0,50,100,150,200,250,300,350,400,450,500,550,600]), h/1.5+off+40),word[0],(random.randint(0,256), random.randint(0,256), random.randint(0,256)),font=ImageFont.truetype('./application/pubmed/arial.ttf', size))

      i += 1
      off -= 30

    img.save('./application/pubmed/results/cloud.png')

    for i in range(len(results)):
      try:
        dept2 = pubmed().getdocumentbyid(results[i][1])
        fobj.write(dept2.abstract+'\n( Citation: '+dept2.doi+', Published on '+dept2.published+' )\n\n')
      except TypeError:
        break
    
    # make drug cloud
    r = requests.get('https://www.drugs.com/imprints.php?drugname='+q.upper())
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find_all('div', { 'class': ['pid-img', 'pid-img-fit', 'zoom'] })
    canvas = Image.open('./application/pubmed/canvas.jpg')
    offset = {'x':10, 'y':10}

    os.mkdir('./application/pubmed/results/images/')

    for i in range(len(content)):
        with requests.get(content[i].find('img')['src']) as request:
            with open('./application/pubmed/results/images/item'+str(i)+'.png', 'wb') as f:
                for chunk in request.iter_content(1024):
                    f.write(chunk)
        nobg = requests.post(
            'https://sdk.photoroom.com/v1/segment',
            files={'image_file': open('./application/pubmed/results/images/item'+str(i)+'.png', 'rb')},
            headers={
              'x-api-key': config
            }
        )
        if nobg.ok:
            with open('./application/pubmed/results/images/item'+str(i)+'.png', 'wb') as out:
                out.write(nobg.content)
        else:
          print(nobg.status_code, nobg.content)
        try:
          canvas.paste(Image.open('./application/pubmed/results/images/item'+str(i)+'.png'), (offset['x'], offset['y']), Image.open('./application/pubmed/results/images/item'+str(i)+'.png'))
        except ValueError:
          canvas.paste(Image.open('./application/pubmed/results/images/item'+str(i)+'.png'), (offset['x'], offset['y']))
        offset['x'] = offset['x'] + 200
        offset['y'] = offset['y'] + random.choice([0,50,100,150,200,250,300])

    canvas.save('./application/pubmed/results/drugcloud.png')
    shutil.rmtree('./application/pubmed/results/images')

    # get newest drug structure
    r = requests.get(
      "https://pubchem.ncbi.nlm.nih.gov/sdq/sdqagent.cgi?infmt=json&outfmt=json&query={%22download%22:%22*%22,%22collection%22:%22compound%22,%22where%22:{%22ands%22:[{%22*%22:%22_str_%22}]},%22order%22:[%22relevancescore,desc%22],%22start%22:1,%22limit%22:10000000,%22downloadfilename%22:%22PubChem_compound_text__str_%22}".replace('_str_', q.lower())
    ).text

    soup = BeautifulSoup(requests.get('https://pubchem.ncbi.nlm.nih.gov/compound/'+json.loads(r)[0]['cid'], headers={'referer': 'https://pubchem.ncbi.nlm.nih.gov/', 'user-agent': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.107 Safari/537.36'}).text, 'html.parser')
    url = soup.find('meta', property='og:image')['content']
    with open('./application/pubmed/results/structure.png', 'wb') as f:
      with requests.get(url) as resp:
        for chunk in resp.iter_content(1024):
          f.write(chunk)

