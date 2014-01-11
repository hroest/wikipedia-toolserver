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
sys.path.append( '/home/hroest' )
import db_api
import time, datetime
print "Content-type: text/html; charset=utf-8"
print ""

try:
    db = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf")
except Exception:
    print  "Currently there is no data available. <br/>"
    print  "This is due to the toolserver being overloaded.<br/>"
    print  "The experts are working on it."
    exit()

subquery = """
create temporary table u_hroest.tmp123 as
select count(*) as occurence, rev_user, rev_user_text, updated_at from u_hroest.replag_users group by rev_user_text
having count(*) >= 5 order by count(*) desc
"""
c  = db.cursor()
c.execute( subquery )

# alter table u_hroest.replag_users add index(rev_user_text);

mainquery = """
select occurence, rev_user, rev_user_text, updated_at, group_concat( ug_group )
from u_hroest.tmp123
left join dewiki_p.user_groups ug on ug.ug_user = rev_user 
group by rev_user_text #rev_user
order by occurence DESC
# and ug.ug_group ='editor'
"""

c.execute( mainquery )
lines = c.fetchall()

l = lines[0]
now = datetime.datetime.now()
now_unix = time.mktime( now.timetuple()  )  
print """
<p>
Letzte Aktualisierung der Daten (GMT/UTC): %s (vor %2.1f min)
</p>
""" % ( datetime.datetime.fromtimestamp(l[3]), (now_unix - l[3])/60.0 )
        

print "<table>"
print "<tr><th>Benutzername</th><th>Rueckstand</th><th>Flags</th></tr>"
for l in lines:
    user = "<a href='http://de.wikipedia.org/wiki/Special:Contributions/%s'>%s</a>" %( l[2], l[2])
    editor = 'None'
    if l[4] is not None: editor = l[4]
    print "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (user, l[0], editor )
    if l[0] < 5: break

print "</table>"
print "Cut at Rueckstand = 5"


