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

import cgi 
form = cgi.FieldStorage()   # FieldStorage object to

#myHist, timestamps, query_time = replag_lib.execute_unreviewed_changes_query(db)

#median = timestamps[ len(timestamps) / 2 ]
#P75 = timestamps[ len(timestamps) * 1 / 4 ]
#P95 = timestamps[ len(timestamps) * 1 / 20 ]
#mean = sum(timestamps) / len( timestamps )

revlag_obj = replag_lib.execute_unreviewed_changes_query_fromCache(db)
myHist = revlag_obj.myHist
revlag_obj.get_extended(db)
timestamps = revlag_obj.timestamps
my3Hist = replag_lib.create_hist_from_timestamps( timestamps, 3)
my1Hist = replag_lib.create_hist_from_timestamps( timestamps, 1)

print "Der Median P50 ist: %.2f d<br/>" % ( revlag_obj.median / (3600 * 24) )
print "Der P75 ist: %.2f d<br/>" % (        revlag_obj.P75 / (3600 * 24) )
print "Der P95 ist: %.2f d<br/>" % (        revlag_obj.P95 / (3600 * 24) )
print "Der Mittelwert ist: %.2f d<br/>" % ( revlag_obj.mean / (3600 * 24) )

print "<!--"
print "Histogram 24 hour resolution"
print myHist
print "Histogram 3 hour resolution"
print my3Hist
print "-->"

print "Aelteste Aenderung: %s d <br/>" % revlag_obj.longest_delay #len( myHist )
print "Anzahl ungesichtete Aenderungen: %s <br/>" % revlag_obj.unreviewed #len( timestamps )

if form.has_key('hist'):
    try:
        hours = int( form.getvalue('hist') )
    except:
        print "<p><b><font color=red>Error: 'hist' parameter needs to be an integer</font></b></p>"
        hours = 24
    if form.has_key('h'):
        my1Hist = replag_lib.create_hist_from_timestamps( timestamps, 1)
        h = float( form.getvalue('h') )
        if h > 0:
            replag_lib.create_plot_kernel( my1Hist , 'hist' , 
                          "Rueckstand in Stunden", h = h )
        else:
            myXHist = replag_lib.create_hist_from_timestamps( timestamps, hours )
            replag_lib.create_plot( myXHist , 'hist' , "Rueckstand in Stunden / %s" % hours )
    else:
        myXHist = replag_lib.create_hist_from_timestamps( timestamps, hours )
        replag_lib.create_plot( myXHist , 'hist' , "Rueckstand in Stunden / %s" % hours )
else:
    replag_lib.create_plot( myHist )


if form.has_key('hist_day'):
    days = float( form.getvalue('hist_day') )
    cursor = replag_lib.revlag_color_cursor_lastseconds(db, days * 24 * 3600)
    replag_lib.revlag_color_plot(cursor, 'history')
else:
    cursor = replag_lib.revlag_color_cursor_all(db)
    replag_lib.revlag_color_plot(cursor, 'history')

if form.has_key('history_month') and form.has_key('history_year'):
    month = int( form.getvalue('history_month') )
    year = int( form.getvalue('history_year') )
    cursor = replag_lib.revlag_color_cursor_month(db, year, month )
    replag_lib.revlag_color_plot(cursor, 'one_month_only')

print "<br/>"* 5
print "Du magst die Graphiken nicht, willst selber was einstellen? Hier gehts zum <a href='../flagged_lag.html'>Formular</a>  "
print "<br/>"* 3
print '<p> <a href="http://toolserver.org/~hroest/">Zurueck zur Uebersicht</a> </p>'

end = time.time()
query_time = end - start
print """
 <hr>

 <p>
 This query took %s s
""" % query_time

now = datetime.datetime.now()
now_unix = time.mktime( now.timetuple()  )  

print """
<p>
Letzte Aktualisierung der Daten (GMT/UTC): %s (vor %2.1f min)
</p>
""" % ( revlag_obj.dtime, (now_unix - revlag_obj.timestamp)/60.0 )


