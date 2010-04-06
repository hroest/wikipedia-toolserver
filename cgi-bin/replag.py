#!/usr/bin/python 
import datetime
import time 
import MySQLdb
import cgitb; cgitb.enable()
db = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf")
import sys
sys.path.append( '/home/hroest/' )
print "Content-type: text/html"
print 

import replag_lib
start = time.time()

#myHist, timestamps, query_time = replag_lib.execute_unreviewed_changes_query(db)

#median = timestamps[ len(timestamps) / 2 ]
#P75 = timestamps[ len(timestamps) * 1 / 4 ]
#P95 = timestamps[ len(timestamps) * 1 / 20 ]
#mean = sum(timestamps) / len( timestamps )

revlag_obj = replag_lib.execute_unreviewed_changes_query_fromCache(db)
myHist = revlag_obj.myHist
print "Der Median P50 ist: %.2f d<br/>" % ( revlag_obj.median / (3600 * 24) )
print "Der P75 ist: %.2f d<br/>" % (        revlag_obj.P75 / (3600 * 24) )
print "Der P95 ist: %.2f d<br/>" % (        revlag_obj.P95 / (3600 * 24) )
print "Der Mittelwert ist: %.2f d<br/>" % ( revlag_obj.mean / (3600 * 24) )

print "<!--"
print myHist
print "-->"

print "Aelteste Aenderung: %s d <br/>" % revlag_obj.longest_delay #len( myHist )
print "Anzahl ungesichtete Aenderungen: %s <br/>" % revlag_obj.unreviewed #len( timestamps )

replag_lib.create_plot( myHist )

replag_lib.revlag_color( db )

end = time.time()
query_time = end - start
print """
 <hr>

 <p>
 This query took %s s
""" % query_time

print """
<p>
Letzte Aktualisierung der Daten (GMT/UTC): %s
</p>
""" % revlag_obj.dtime

