#!/usr/bin/python
# -*- coding: utf-8  -*-
# This displays 5 random wiktionary pages that either have {{el} or {{es} as
# template or have neither.
#
import cgitb; cgitb.enable()
import MySQLdb, sys
sys.path.append( '/home/hroest' )
import db_api
print "Content-type: text/html; charset=utf-8"
print ""

db3 = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf3")
select = """
select page_id, page_title from page 
inner join templatelinks on page_id = tl_from 
where page_namespace = 0 and (tl_title = 'es' or tl_title = 'el') 
group by page_id 
"""
create_drop = """
drop table u_hroest.alice_wk;
create table u_hroest.alice_wk as 
""" + select + " ; create index idx on u_hroest.alice_wk(page_id);"
select5 = select + "order by rand() limit 5"
selectNOT5 = """
select page_id, page_title from page 
where page_id not in (select page_id from u_hroest.alice_wk)
and page_namespace = 0
order by rand() limit 5; """

c  = db3.cursor()

c.execute( "use dewiktionary_p" )
c.execute( select5 )
lines = c.fetchall()

print "Haben entweder {{el}} oder {{es}} als template verlinkt: <br/>"
for l in lines:
    print '<a href="http://de.wiktionary.org/wiki/%s">%s</a><br/>' % (l[1],l[1])

print "<br/>" * 5

c.execute( "use dewiktionary_p" )
c.execute( selectNOT5 )
lines = c.fetchall()

print "Haben weder {{el}} noch {{es}} als template verlinkt: <br/>"
for l in lines:
    print '<a href="http://de.wiktionary.org/wiki/%s">%s</a><br/>' % (l[1],l[1])
