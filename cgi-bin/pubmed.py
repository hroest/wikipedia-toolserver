#!/usr/bin/python 
# -*- coding: utf-8  -*-

import urllib2
import time, datetime

import httplib, socket, urlparse, urllib, urllib2  #Internet libs
from xml.dom import minidom   #XML Parsing for API

def send_request(webpage):
    request = urllib2.Request(webpage.encode('utf8'))
    # request.add_header('User-Agent', 
    #    u'de:HRoestBot by de-user Hannes Röst'.encode('utf8')) 
    opener = urllib2.build_opener()
    data = opener.open(request).read()   

    data = urllib.unquote(data)
    data = unicode(data, 'utf8')
    return data

def get_article_info(pmid):
  page = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=" + str(pmid)
  web_data = send_request(page)

  dom = minidom.parseString(web_data.encode('utf8'))
  summary = dom.getElementsByTagName('DocSum')[0]

  article = Article()
  pubmed_id = summary.getElementsByTagName('Id')[0]
  if pubmed_id.hasChildNodes():
    article.pmid = pubmed_id.childNodes[0].data

  for el in summary.getElementsByTagName('Item'):
    attrname = el.attributes["Name"].value
    attrtype = el.attributes["Type"].value
    if el.hasChildNodes():
      #print el.childNodes[0].data
      data = el.childNodes[0].data
    else:
      continue
    if attrname == "PubDate":
      article.set_publication_date_api(data)
    elif attrname == "Title":
      article.title = data
    elif attrname == "Volume":
      article.volume = data
    elif attrname == "Issue":
      article.issue = data
    elif attrname == "Pages":
      article.pages = data
    elif attrname == "FullJournalName":
      article.journal = data
    elif attrname == "ISSN":
      article.issn = data
    elif attrname == "DOI":
      article.doi = data
    elif attrname == "AuthorList":
      article.author_names = [sub_el.childNodes[0].data for sub_el in el.getElementsByTagName("Item")]
  return article
      


class Article():
  def __init__(self):
    self.title = None
    self.journal = None
    self.volume = None
    self.issue = None
    self.pages  = None
    self.location  = None
    self.publisher  = None
    self.doi  = None
    self.url = None
    self.issn = None
    self.pmid = None
    self.author_names = []
  def set_publication_date_api(self, data):
    self.pubdate = time.strptime(data, '%Y %b %d')
  def get_publication_date_wp(self):
    return time.strftime('%Y-%m-%d', self.pubdate)
  def get_wp_cite_journal(article):
      templ_text = u"{{cite journal\n"
      if len(article.author_names) > 0:
        templ_text += "| author = " + ", ".join(article.author_names) + "\n"

      if article.pubdate is not None:
        templ_text += "| year = " + str(article.pubdate.tm_year) + "\n"
        templ_text += "| month = " + str(article.pubdate.tm_mon) + "\n"

      for attr in ["title", "journal", "volume", "issue", "pages", "location", "publisher", "doi", "issn", "url", "pmid"]:
          if getattr(article, attr) is not None: 
            templ_text += "| " + attr + " = " + getattr(article, attr) + "\n"

      templ_text += u"| accessdate = " + str(datetime.datetime.now().date() ) + "\n}}"
      return templ_text 



# a = get_article_info(12540921)
# print a.get_wp_cite_journal()
