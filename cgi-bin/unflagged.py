#!/usr/bin/python
# -*- coding: utf-8  -*-
import cgitb; cgitb.enable()
import MySQLdb, sys
sys.path.append( '/home/hroest' )
sys.path.append( '/data/project/hroest/meta' )
import db_api
import general_lib
import time, datetime
print "Content-type: text/html; charset=utf-8"
print ""

try:
    db = MySQLdb.connect(read_default_file=general_lib.mysql_config_file, host=general_lib.mysql_host)
except Exception:
    print  "Connection to DB failed..."
    exit()


all = """
select page_title, updated_at, rev_timestamp from %s.never_review 
order by rev_timestamp
""" %  general_lib.database_name
c  = db.cursor()

c.execute( all )
lines = c.fetchall()

l = lines[0]
now = datetime.datetime.now()
now_unix = time.mktime( now.timetuple()  )  
print """
<p>
Letzte Aktualisierung der Daten (GMT/UTC): %s (vor %2.1f min)
</p>
<p>
Es wurden %s Artikel gefunden, die noch nie gesichtet wurden.
</p>
""" % ( datetime.datetime.fromtimestamp(l[1]), (now_unix - l[1])/60.0, len(lines) )

        
print "<table>"
print "<tr><th>Titel</th><th>Erstellt am</th></tr>"
for l in lines:
    escaped_t = l[0].replace('"', '%22')
    title = '<a href="http://de.wikipedia.org/wiki/%s">%s</a>' %( escaped_t, escaped_t)
    print "<tr><td>%s</td><td>%s</td></tr>" % (title, l[2])

print "</table>"


