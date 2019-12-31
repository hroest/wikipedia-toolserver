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

print "Content-type: text/plain; charset=utf-8"
print ""

db = MySQLdb.connect(read_default_file=general_lib.mysql_config_file, host=general_lib.mysql_host)

#this query takes 30 seconds and selects all currently unflagged pages
all = """
SELECT page_id,page_title,page_latest,fp_stable, rev_len 
FROM page,flaggedpages, revision 
WHERE fp_page_id=page_id AND page_latest<>fp_stable
AND page_namespace=0 AND rev_id=page_latest;
"""
c  = db.cursor()

c.execute( "use dewiki_p" )
c.execute( all )
lines = c.fetchall()

#this may take between 2 minutes and 15 seconds, depending on the query cache
unflagged_list = []
for l in lines:
    unf = db_api.UnFlagged()
    unf.initialize_with_db( l )
    unf.get_unflagged(c )
    unflagged_list.append( unf )

unflagged_list.sort( lambda x,y: cmp(x.first_time, y.first_time ) )

for unfl in unflagged_list:
    if unfl.error: continue
    print unfl.page_title, "||;;;", unfl.page_nr, "||;;;",unfl.stable, "||;;;",unfl.latest, "||;;;",unfl.first_time 


