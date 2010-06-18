#!/usr/bin/python 
# -*- coding: utf-8  -*-

import time, sys
import MySQLdb
db = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf")
sys.path.append( '/home/hroest/' )
import replag_lib, db_api
import cgi 
form = cgi.FieldStorage()   # FieldStorage object to
start = time.time()
print "Content-type: text/html; charset=utf-8"
print ""

class Page:
    def __init__(self): pass

def get_time_diff(timestamp, return_as = 'D'):
    import datetime
    now = datetime.datetime.now()

    year = now.year     - int(timestamp[:4])
    mon =  now.month    - int(timestamp[4:6])
    day =  now.day      - int(timestamp[6:8])
    hour = now.hour     - int(timestamp[8:10])
    min =  now.minute   - int(timestamp[10:12])

    if return_as == 'D':
        days = 356*year + 30*mon + day
        return days

def db_get_unreviewed( language, category, c):

    category = db_api.make_db_safe( category )
    sql = """SELECT page_id,page_title,page_latest,fp_stable, rev_len
    FROM page,categorylinks,flaggedpages, revision
    WHERE cl_to="%s" AND cl_from=page_id AND fp_page_id=page_id 
    AND page_latest<>fp_stable AND page_namespace=0
    AND rev_id=page_latest""" % category;

    db = language + 'wiki_p' ;
    tmp = c.execute( sql )
    res = c.fetchall()

    reviewed_pages = []
    for o in res:
        page = Page()
        page.id          = o[0]
        page.title       = o[1]
        page.current_rev = o[2]
        page.stable_rev  = o[3]
        page.latest_size = o[4]

        #revision[0] is the latest flagged revision
        #revision[1] is the first unflagged revision 
        #we do not store the revisions for memory reasons
        sql = """select rev_id,  rev_comment, rev_user_text, 
        rev_timestamp, rev_len
        from revision where rev_page = %s
        and rev_id >= %s""" % (page.id, page.stable_rev)
        c.execute( sql ) 
        revisions = c.fetchall()

        stable_len = revisions[0][4]
        page.size_diff = page.latest_size - stable_len

        page.first_unflagged_timestamp = revisions[1][3]
        reviewed_pages.append(page)

    return reviewed_pages;


if not form.has_key('category'):
    print """ <h1>Flagged Revisions Tool</h1>
    <i>%(title)s</i><br/>
    <form method='get' action='flagged.py'>
    <table>
    <tr><th>%(language_title)s</th><td><input type='text' 
        name='language' value='%(language)s' size='30' /></td></tr>
    <tr><th>%(catname)s</th><td><input type='text' name='category' value='' 
        size='30' /></td></tr>
    <tr><th>exclude*</th><th>
        <textarea name='exclude' rows='3' cols='80'></textarea></th>
    </tr>
    <tr><th>%(depth_title)s**</th><td><input type='text' name='depth' 
        value='%(depth)s' /> </td></tr>
    <tr><th></th><td><input type='submit' name='doit' value='%(go)s' /></td></tr>
    <tr><th>%(sortby)s</th><th>
       <Input type = 'Radio' Name='sortby' value= 'size' checked='checked' >Size
       <Input type = 'Radio' Name='sortby' value= 'size_reverse'>Size (reverse)
    </tr>
    <tr><th></th><th>
       <Input type = 'Radio' Name='sortby' value= 'title'>Title
       <Input type = 'Radio' Name='sortby' value='title_reverse'>Title (reverse)
    </tr>
    <tr><th></th><th>
       <Input type = 'Radio' Name='sortby' value= 'time'>Time
       <Input type = 'Radio' Name='sortby' value= 'time_reverse'>Time (reverse)
    </tr>
    </table>
    <br/>
    *Format: \"cat1;cat2;cat3\".  <br/>
    This might not do what you expect it to do.<br/>
    If you list a category under \"exclude\", this category is not considered<br/>
    in the recursive search for articles. If the article you want to exclude is<br/>
    encountered in a different category during the search, it will still be <br/>
    included.
    <br/>
    <br/>
    ** 1=%(expl1)s, -99 = %(expl2)s
    </form>
    <p> <a href='http://toolserver.org/~hroest/'>Zurueck zur Uebersicht</a> </p>
    """ % { 'go' : 'Los!', 'catname' : 'Kategorie', 'depth' : 'Tiefe', 
        'depth_title' : 'Tiefe', 'language_title' : 'Sprache',
        'depth' : 1, 'sortby' : 'Sortiere nach', 'title' :  
        "Zeigt Artikel in (Unter)kategorien, die nachgesichtet werden müssen.", 
        'expl1' : 'Kategorie und direkte Unterkategorien', 'language' : 'de',
        'expl2' :'Alle Unterkategorien'  }
    exit()

#///////////////////////////////////////////////////////////////////////////
#//   OPTIONS
#///////////////////////////////////////////////////////////////////////////


language        =     form.getvalue( 'language')
category        =     form.getvalue( 'category')
depth           = int(form.getvalue( 'depth') )
sortby          =     form.getvalue( 'sortby')
exclude_noncode =     form.getvalue( 'exclude')
show_color_at   =     300
diff_only       =     0
exclude = exclude_noncode.replace( " ", "_")
exclude = exclude.split(";")

print "Excluding: ";
for ex in exclude: print ex + ";"
print "<br/>";

start = time.time()
c = db.cursor()
data = db_api.db_get_articles_in_category ( language, category, c, 
                                       depth-1, 14, exclude ) 
if not category in data: data.append( category )
print "Durchsuche " + str( len ( data ) ) + " Kategorien.";

output = []
for d in data:
    my_unreviewed = db_get_unreviewed ( language, d, c);
    for unrev in my_unreviewed:
        if not unrev.title in [o.title for o in output]: output.append( unrev)

print len( output )

#now we have all unreviewed pages, lets sort them
if (sortby == 'size')           :
    output.sort( lambda x, y: cmp(x.size_diff, y.size_diff)  )
elif (sortby == 'title')        :
    output.sort( lambda x, y: cmp(x.title, y.title)  )
elif (sortby == 'time')         :
    output.sort( lambda x, y: -cmp(x.first_unflagged_timestamp, 
                                  y.first_unflagged_timestamp)  )
elif (sortby == 'size_reverse') :
    output.sort( lambda x, y: -cmp(x.size_diff, y.size_diff)  )
elif (sortby == 'title_reverse'):
    output.sort( lambda x, y: -cmp(x.title, y.title)  )
elif (sortby == 'time_reverse') :
    output.sort( lambda x, y: cmp(x.first_unflagged_timestamp, 
                                  y.first_unflagged_timestamp)  )


printlist = '';
taburls = []
for page in output:
    t =  page.title.replace( "_" , " " )
    old_id = page.stable_rev
    url = "http://de.wikipedia.org/w/index.php?title=" + t 
    url += "&diffonly=0&oldid=%s&diff=cur" % old_id

    timediff = get_time_diff(page.first_unflagged_timestamp)
    diff = page.size_diff
    if abs ( diff ) > show_color_at:bg = '#AAAAAA';
    else: bg = '#FFFFFF';
    if diff > 0:
        diff_display="<span style='color:green;background:$bg'>+%s</span>"%diff
    elif diff < 0:
        diff_display = "<span style='color:red;background:$bg'>%s</span>"%diff
    else: diff_display = "<span style='background:$bg'>%s</span>"%diff

    note = "Diff = " + diff_display
    note += " Alter = "  + str(timediff) + " Tage" ;

    printlist += '<li><a target="_blank" href="%s">' % url
    printlist += t + "</a>%s</li>\n" % note;

    taburls.append(url)

print "<ol>" + printlist + "</ol>";
print "\n\n<br/>Today: " +  "\n<br/>";
end = time.time()
timediff = end - start
print "This query took %s seconds. <br/>" % timediff

print str(len( output ) ) + " nachzusichtende Artikel gefunden. "


#********************************************* 
#Javascript from Magnus
#********************************************* 
#
out = ''
print "<script type='text/javascript'>"

if len( taburls ) > 10:
    print "function open10 () {\n"
    for a in range(10):
        print "window.open ('"+taburls[a]+"', '_blank');" ;
    print "return false;};\n\n" ;
    out += "<a href='#' onclick='open10()'>Open first 10 in tabs</a> " ;

if len( taburls ) > 20:
    print "function open20 () {\n"
    for a in range(20):
        print "window.open ('"+taburls[a]+"', '_blank');" ;
    print "return false;};\n\n" ;
    out += "<a href='#' onclick='open20()'>Open first 20 in tabs</a> " ;

if len( taburls ) > 50:
    print "function open50 () {\n"
    for a in range(50):
        print "window.open ('"+taburls[a]+"', '_blank');" ;
    print "return false;};\n\n" ;
    out += "<a href='#' onclick='open50()'>Open first 50 in tabs</a> " ;

print "function open_all() {\n" ;
for tab in taburls:
    print "window.open ('"+tab+"', '_blank');\n" ;
print "return false;};\n\n" ;
out += "<a href='#' onclick='open_all()'>" ;
out += "Open all in tabs" ;
out += "</a> " ;

print "</script>" 
print out

print '<p> <a href="http://toolserver.org/~hroest/">Zurueck zur Uebersicht</a> </p>';
print '</html>' ;

