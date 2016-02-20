#!/usr/bin/python
# -*- coding: utf-8  -*-

def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')


import time
start = time.time()

# import cgitb; cgitb.enable()

import MySQLdb
import sys
import cgi
form = cgi.FieldStorage()  

helptext = """
<a onclick="helpdiv.style.display='block'" href="#">Help?</a>
<div id="helpdiv" style="display:none">
  <p>
  Q: How does the [replace] functionality work? 
  </p>
  <p>
  A: You need to add the following javascript snippet to your common.js: Go you the page [[User:Username/common.js]] and add the following line:
  <pre>
  importScript('User:Hannes Röst/autoSearchAndReplace.js'); //search and replace words
  </pre>
  This works on de and en Wikipedia. Then you can click on the [replace] links
  which will open a new tab, allow you to review your changes and then save
  them (e.g. using Alt-Shift-S). However, be careful: you can only do one
  replace per page at a time (otherwise you overwrite your previous change). If
  you have more than one change, use the "edit" link.
  </p>
</div>
<p>
  <a href="https://tools.wmflabs.org/hroest/">Go back</a>
</p>
"""

print "Content-type: text/html; charset=utf-8"
print ""

print """
<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="utf-8">
<title>Spellcheck</title>
</head>

<body>

<style>.snippet{ 
  width:600px;
  padding:10px;
  margin:10px;
  background-color:#f0f0f0;}
</style>



"""

import sys
# sys.path.append("/home/hroest_admin/pywiki/pywikibot-spellchecker/")
sys.path.append( '/data/project/hroest/bot/pywikibot-spell/' )
sys.path.append( '/data/project/hroest/bot/wikispell/' )
sys.path.append( '/data/project/hroest/pyhunspell/build/lib.linux-x86_64-2.7' )
sys.path.append( '/data/project/hroest/levenshtein/python-Levenshtein-0.12.0/build/lib.linux-x86_64-2.7' )

if not form.has_key('title') and not ( form.has_key('random') or form.has_key('start') ):
    print """ <h1>Spellcheck</h1>
    <form method='get' action='spell.py'>
        <p>
          Article <input type='text' name='title' size='30' /> <small>Please enter the name of a Wikipedia article in the language of choice</small>
        </p>
        <p>
          Language 
        <select name="language">
          <option value="de">German (de)</option>
          <option value="en">English (en)</option>
        </select>
        </p>
        <p>
          <input type="checkbox" name="keepSugg" value="yes"> Keep words where suggestions are dissimilar
        <a onclick="expl_sugg.style.display='block'; expl_sugg.style.marginBottom='50px'" style="display:inline" href="#"><small>show explanation</small></a>
        <div id="expl_sugg" style="display:none">This will tell the algorithm to keep words, even if the spellchecker did not find a close, matching word that is potentially correct. By default, words without a close correct match are excluded as they are possibly names of places and people while words that are very close to a suggested word are likely misspelled.  If you check this, expect to see more words in your results. 
        </div>
        </p>
        <p>
        Stringency
        <select name="stringent">
          <option value="Very">Low (Returns fewer words)</option>
          <option value="Medium">Medium (Returns many results, some false positives)</option>
          <option value="Loose">High (Returns many results, many false positives)</option>
        </select>
        <a onclick="expl_str.style.display='block'; expl_str.style.marginBottom='50px'" style="display:inline" href="#"><small>show explanation</small></a>
        <div id="expl_str" style="display:none">
        <p>
        This parameter changes how many words are identified as incorrect, using a larger vocabulary which consists of common words and titles of Wikipedia articles. It also adds several heuristics to filter out incorrect words. For most applications, "Medium" will provide a good balance between true positives and false positives while "Low" is appropriate in cases with too many words reported. On the other hand, "High" is mostly equivalent to using hunspell by itself without additional dictionaries or heuristics and thus is <b>highly discouraged</b> as it often reports hundreds of words that are not in the canonical dictionary ("High" generates similar results as using the OpenOffice spellchecker).
        </p>
        <p>
        Some of the heuristics employed are filtering out words that are common, filtering out words that appear as a title of any Wikipedia article (names and places mostly), filtering out words that appear multiple times in an article, filtering out words that are likely not in the target language and filtering out composite words (mostly for German).
        </p>
        </div>
        </p>
        <p>
        Check
        <select name="level">
          <option value="full">Regular text only (no italic, bold, tables, ref, lists)</option>
          <option value="wiki-skip">Skip Wiki Syntax</option>
          <option value="relaxed">Relaxed</option>
          <option value="none">All source</option>
        </select>
        <a onclick="expl_level.style.display='block'; expl_level.style.marginBottom='50px'" style="display:inline" href="#"><small>show explanation</small></a>
        <div id="expl_level" style="display:none">Which text to check. By default, the algorithm does not check within templates, weblinks, tables, lists, bold, italic text, quotation marks, at the end of the article etc. as these often contain names of places and people. If you choose to skip only Wiki Syntax, more text will be included (e.g. text in quotation marks, text at the end of the article). In relaxed mode
        </div>
        </p>
        <p>
          <input type='submit' name='doit' value='Go' />
        <p/>

        <p style="padding-top:45px">
          Alternatively, open 60 random pages instead for spellcheck:
        </p>
        <p>
          <input type='submit' name='random' value='Random page' />
        <p/>
    </form>
    """  % {"language" : "de" }
    print helptext
    print """

    </body>

    </html>
    """
    exit()

import wikipedia as pywikibot
import marshal
from wikispell.HunspellSpellchecker import HunspellSpellchecker

level           =     form.getvalue( 'level')
language        =     form.getvalue( 'language')
sel_stringent   =     form.getvalue( 'stringent')


# Get the actual page (either random or supplied)
if form.has_key('random') or form.has_key('start'):
  site = pywikibot.getSite(language, "wikipedia")

  if form.has_key('random'):
      while True:
          page = site.randompage()
          if page.namespace() == 0:
              break
      start_title = page.title()
  else:
      start_title = form.getvalue('start').decode("utf8")

  import pagegenerators
  gen = pagegenerators.PreloadingGenerator(
              pagegenerators.AllpagesPageGenerator(start=start_title, namespace=0, includeredirects=False, site=site))

  pages = []
  for i, page in enumerate(gen):
      if i >= 60: break
      pages.append(page)


else:
  title = form.getvalue( 'title')
  title = title.decode("utf8")
  site = pywikibot.getSite(language, "wikipedia")
  page = pywikibot.Page(site, title)
  pages = [page]
  

remove_dissim   =    True
if form.has_key('keepSugg') and form.getvalue( 'keepSugg') == "yes":
    remove_dissim   =    False

if language == "de":
    
    hunspell_lang = "DE"

    dictionary = "/data/project/hroest/data/de_DE_frami_nhr"
    common_words_dict = set([])
    if sel_stringent == "Very":

        common_words_file = "/data/project/hroest/data/allgerman.msh"
        f = open(common_words_file); 
        common_words_dict = marshal.load(f); 

        ### Reading from text:
        ### common_words_file = "/home/hroest_admin/pywiki/spellcheck/lists/de/common_15.dic"
        ### f = open(common_words_file)
        ### for l in f:
        ###     common_words_dict.add(l.strip().decode("utf8").lower())
        ### f = open("/home/hroest_admin/pywiki/spellcheck/output_de.txt")
        ### for i,l in enumerate(f):
        ###     common_words_dict.add(l.strip().decode("utf8").lower())
        ### f = open("/home/hroest_admin/pywiki/spellcheck/output_en.txt")
        ### for i,l in enumerate(f):
        ###     common_words_dict.add(l.strip().decode("utf8").lower())
        ### # f = open("../spellcheck/lists/de/cbbnomcgdf-17166212131-e9u79o.txt")
        ### f = open("/home/hroest_admin/pywiki/spellcheck/lists/de/cbbnomcgdf-17166212131-e9u79o.txt")
        ### for i,l in enumerate(f):
        ###     german = l.split("\t")[0]
        ###     german = german.split("{")[0].strip()
        ###     german = german.split("[")[0].strip()
        ###     # comment
        ###     if german.startswith("#"): continue
        ###     # full phrases
        ###     if german.startswith('"'): continue
        ###     gwords = [g.replace("(", "").replace(")", "").decode("utf8").lower() for g in german.split()]
        ###     # update ...
        ###     common_words_dict.update(gwords)

    elif sel_stringent == "Medium":
        # marshal.dump ( common_words_dict, open( '/data/project/hroest/data/alltitles.msh' , 'w') )

        common_words_file = "/data/project/hroest/data/alltitles.msh"
        f = open(common_words_file); 
        common_words_dict = marshal.load(f); 

        ### common_words_file = "/data/project/hroest/data/output_de.txt.pickle"
        ### f = open(common_words_file); 
        ### import cPickle as pickle;
        ### common_words_dict = pickle.load(f); 
        ### common_words_file = "/data/project/hroest/data/output_en.txt.pickle"
        ### f = open(common_words_file); 
        ### import cPickle as pickle;
        ### common_words_dict_en = pickle.load(f); 
        ### common_words_dict.update(common_words_dict_en)

elif language == "en":
    hunspell_lang = "EN"
    
    dictionary = "/usr/share/hunspell/en_US"
    # dictionary = "/usr/share/hunspell/de_DE_frami"
    dictionary = "/data/project/hroest/data/en_US"
    common_words_dict = set([])
    if sel_stringent == "Very":
        # marshal.dump ( common_words_dict, open( '/data/project/hroest/data/eng_strict.msh' , 'w') )

        common_words_file = "/data/project/hroest/data/eng_strict.msh"
        f = open(common_words_file); 
        common_words_dict = marshal.load(f); 

        ### common_words_file = "/home/hroest_admin/pywiki/spellcheck/lists/de/common_15.dic"
        ### f = open(common_words_file)
        ### for l in f:
        ###     common_words_dict.add(l.strip().decode("utf8").lower())
        ### f = open("/home/hroest_admin/pywiki/spellcheck/output_de.txt")
        ### for i,l in enumerate(f):
        ###     common_words_dict.add(l.strip().decode("utf8").lower())
        ### f = open("/home/hroest_admin/pywiki/spellcheck/output_en.txt")
        ### for i,l in enumerate(f):
        ###     common_words_dict.add(l.strip().decode("utf8").lower())

    elif sel_stringent == "Medium":
        # marshal.dump ( common_words_dict, open( '/data/project/hroest/data/eng_titles.msh' , 'w') )

        common_words_file = "/data/project/hroest/data/eng_titles.msh"
        f = open(common_words_file); 
        common_words_dict = marshal.load(f); 

        ## f = open("/home/hroest_admin/pywiki/spellcheck/output_en.txt")
        ## for i,l in enumerate(f):
        ##     common_words_dict.add(l.strip().decode("utf8").lower())


stringent = 0
composite_minlen = 0
if sel_stringent == "Very":
    composite_minlen = 0
elif sel_stringent == "Medium":
    # No composite words
    stringent = 90
elif sel_stringent == "Loose":
    # No composite words
    # No heuristics
    # No check for common words
    composite_minlen = 4
    stringent = 1999


sp = HunspellSpellchecker(hunspell_dict = dictionary, 
                       minimal_word_size=4, 
                       common_words=common_words_dict,  
                       stringent=stringent,  
                       composite_minlen = composite_minlen,
                       remove_dissimilar = remove_dissim,
                       language = hunspell_lang)

## end = time.time()
## timediff = end - start
## print "This query took %s seconds. <br/>" % timediff

if len(pages) > 0:
    print "I will spellcheck %s page(s), starting with: %s" % ( len(pages), pages[0].title().encode("utf8") )

cnt = 0
for pagenr, page in enumerate(pages):

    title = page.title()
    text = page.get()
    text, wrongWords_unfiltered = sp.spellcheck(text, level=level)

    wrongWords = []
    for w in wrongWords_unfiltered:
        if len(w.suggestions) > 0:
            correct = w.suggestions[0].encode("utf8")
            if correct.find( " " ) != -1 and stringent < 100:
                continue

        if w.derive() in ["br", "name", "ref"]:
                continue

        wrongWords.append(w)

    if len(wrongWords) == 0: 
        continue

    print "<h2>%s. Spellcheck for <a href='https://%s.wikipedia.org/wiki/%s'>%s</a> </h2>" % (
            pagenr+1, language, title.encode("utf8"),  title.encode("utf8"))
    print "Wikipedia page <a href='https://%s.wikipedia.org/w/index.php?title=%s&action=edit'>%s (edit)</a>" % (
          language, title.encode("utf8"),  title.encode("utf8"))


    print "<p>"
    print "Found %s words" % len(wrongWords)
    print "</p>"
    print "<ul>"
    for w in wrongWords:
        i = cnt
        print "<li>"
        print w.derive().encode("utf8")
        if len(w.suggestions) > 0:
            print " &rarr;  " , w.suggestions[0].encode("utf8")
            print """<sup> <a target="_blank" href="http://%(lang)s.wikipedia.org/w/index.php?title=%(title)s&action=edit&summary=Fixed+Typo&minor=1&searchFor=%(wrong)s&replaceWith=%(correct)s&doSearchAndReplace=1">[replace] </a> </sup>  """ % {
              "lang" : language,
              "title" : title.encode("utf8"),
              "wrong" : w.derive().encode("utf8"),
              "correct" : w.suggestions[0].encode("utf8") 
              }
        print """<a id='snippet_%(i)s_show' 
        onclick="snippet_%(i)s.style.display='block'; 
        snippet_%(i)s_show.style.display='none';
        snippet_%(i)s_hide.style.display='inline'";
        style="display:inline" href="#nowhere">show snippet</a> """ % {'i': i}
        if len(w.suggestions) > 0:
          pass
        print """<a id='snippet_%(i)s_hide' 
        onclick="snippet_%(i)s.style.display='none'; 
        snippet_%(i)s_show.style.display='inline';
        snippet_%(i)s_hide.style.display='none'";
        style="display:none" href="#nowhere">hide snippet</a> """ % {'i': i}

        ## Print div
        print "<div id='snippet_%s' style='display:none;' class='snippet'>" % i
        snippet = text[ max(0, w.location-120) : min( len(text), w.location+120) ]
        snippet = snippet.encode("utf8")
        snippet = escape(snippet)
        snippet = snippet.replace( w.derive().encode("utf8"), "<span style='color:red;'>%s</span>" % w.derive().encode("utf8"))
        print snippet
        print "</div>"

        print "</li>"
        cnt += 1

    print "</ul>"



print "<script type='text/javascript'>"

print "function openAll () {\n"
for i in range(cnt):
    print "snippet_%s.style.display='block';" % i
    print "snippet_%s_show.style.display='none';" % i
    print "snippet_%s_hide.style.display='inline';" % i

print "return false;};\n\n" ;

print "function closeAll () {\n"
for i in range(cnt):
    print "snippet_%s.style.display='none';" % i
    print "snippet_%s_show.style.display='inline';" % i
    print "snippet_%s_hide.style.display='none';" % i

print "return false;};\n\n" ;

print "</script>"

print "<p>"
print """<a href='#' onclick='openAll()'>Open all</a> """
print """<a href='#' onclick='closeAll()'>Close all</a> """
print "</p>"


end = time.time()
timediff = end - start
print "Found a total of %s words in %s page(s). <br/>" % (cnt, len(pages) )
print "This query took %s seconds. <br/>" % timediff

print helptext
print """

</body>

</html>
"""

