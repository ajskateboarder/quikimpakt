from bs4 import BeautifulSoup
from urllib.parse import quote
from . import stopwords
from PIL import ImageDraw 
from PIL import ImageFont
from PIL import Image
import collections
import requests
import shutil
import random
import os

# Cool functions that are organized to look like a pip module file
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

    for i in range(len(results)):
      try:
        dept2 = pubmed().getdocumentbyid(results[i][1])
        alltexts.append(dept2.abstract+' ')
      except TypeError:
        break

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

      if word[0] not in stopwords.words:
        draw.text((w/2+off+random.choice([-100,-50,0,50,100,150,200,250,300,350,400,450,500,550,600]), h/1.5+off+40),word[0],(random.randint(0,256), random.randint(0,256), random.randint(0,256)),font=ImageFont.truetype('./arial.ttf', size))

      i += 1
      off -= 30

    img.save('./application/pubmed/results/cloud.png')

    for i in range(len(results)):
      try:
        dept2 = pubmed().getdocumentbyid(results[i][1])
        fobj.write(dept2.abstract+'\n( Citation: '+dept2.doi+', Published on '+dept2.published+' )\n\n')
      except TypeError:
        break