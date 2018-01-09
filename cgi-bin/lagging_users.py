#!/usr/bin/python
# -*- coding: utf-8  -*-
#import cgitb; cgitb.enable()
#import MySQLdb
#import datetime
#import time 
#import inequality
#import sys
#
#
#today = datetime.date.today()
#now = datetime.datetime.now()
#this_year = today.year
#this_month = today.month
#
import cgitb; cgitb.enable()
import MySQLdb, sys
sys.path.append( '/data/project/hroest/meta' )
import db_api
import general_lib
from general_lib import database_name as myDB
import time, datetime
print "Content-type: text/html; charset=utf-8"
print ""

try:
    db_w = MySQLdb.connect(read_default_file=general_lib.mysql_config_file, host=general_lib.mysql_host)
    db_user = MySQLdb.connect(read_default_file=general_lib.mysql_config_file, host=general_lib.userdatabase_host)
except Exception:
    print  "Currently there is no data available. <br/>"
    print  "This is due to the toolserver being overloaded.<br/>"
    print  "The experts are working on it."
    exit()

# First query
subquery = """
# create temporary table %s.tmp123 as
select count(*) as occurence, rev_user, rev_user_text, updated_at from %s.replag_users group by rev_user_text
having count(*) >= 5 order by count(*) desc
""" % (myDB, myDB)
c  = db_user.cursor()
c.execute( subquery )

lines = c.fetchall()

# Mapping query
mapping = {}
if False:
  mainquery = """
  select occurence, rev_user, rev_user_text, updated_at, group_concat( ug_group )
  from %s.tmp123
  left join dewiki_p.user_groups ug on ug.ug_user = rev_user 
  group by rev_user_text #rev_user
  order by occurence DESC
  # and ug.ug_group ='editor'
  """ % (myDB)

  c.execute( mainquery )
  lines = c.fetchall()
else:
  c = db_w.cursor()
  seq = [str(l[1]) for l in lines]
  q = "select ug.ug_user, group_concat( ug_group )  from dewiki_p.user_groups ug where ug.ug_user in (%s) group by ug.ug_user; "  % (", ".join(seq) ) 
  c.execute( q )
  for m in c.fetchall():
    mapping[ m[0] ] = m[1]

l = lines[0]
now = datetime.datetime.now()
now_unix = time.mktime( now.timetuple()  )  
print """
<p>
Letzte Aktualisierung der Daten (GMT/UTC): %s (vor %2.1f min)
</p>
""" % ( datetime.datetime.fromtimestamp(l[3]), (now_unix - l[3])/60.0 )
print """
<p>
Dieses tool funktioniert besser mit dem <a
href="https://de.wikipedia.org/wiki/Benutzer:Hannes_R%C3%B6st/flagged_user.js">flagged_user.js</a>
snippet eingebunden in dein monobook.js (e.g. mit
<code>importScript('Benutzer:Hannes Röst/flagged_user.js');</code> eingebunden).
</p>
"""
        

print "<table>"
print "<tr><th>Benutzername</th><th>Rueckstand</th><th>Flags</th></tr>"
for l in lines:
    user = "<a href='http://de.wikipedia.org/wiki/Special:Contributions/%s'>%s</a>" %( l[2], l[2])
    editor = 'None'
    if l[1] in mapping: editor = mapping[l[1] ]
    # if l[4] is not None: editor = l[4]
    print "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (user, l[0], editor )
    if l[0] < 5: break

print "</table>"
print "Cut at Rueckstand = 5"


