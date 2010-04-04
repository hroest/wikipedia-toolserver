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

myHist, timestamps, query_time = replag_lib.execute_unreviewed_changes_query(db)

median = timestamps[ len(timestamps) / 2 ]
P75 = timestamps[ len(timestamps) * 1 / 4 ]
P95 = timestamps[ len(timestamps) * 1 / 20 ]
mean = sum(timestamps) / len( timestamps )
print "Der Median P50 ist: %.2f d<br/>" % (median / (3600 * 24) )
print "Der P75 ist: %.2f d<br/>" % (P75 / (3600 * 24) )
print "Der P95 ist: %.2f d<br/>" % (P95 / (3600 * 24) )
print "Der Mittelwert ist: %.2f d<br/>" % (mean / (3600 * 24) )

print "<!--"
print myHist
print "-->"

print "Aelteste Aenderung: %s d <br/>" % len( myHist )
print "Anzahl ungesichtete Aenderungen: %s <br/>" % len( timestamps )


replag_lib.create_plot( myHist )

print """
 <hr>

 <p>
 This query took %s s
""" % query_time

