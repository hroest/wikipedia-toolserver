#!/usr/bin/python
# -*- coding: utf-8  -*-
import cgitb; cgitb.enable()
import MySQLdb
import datetime
import time 
import inequality
import sys
sys.path.append( '/data/project/hroest/' )
sys.path.append( '/data/project/hroest/meta' )
import optinHash
gnuplot_path = 'gnuplot'

today = datetime.date.today()
now = datetime.datetime.now()
this_year = today.year
this_month = today.month

print "Content-type: text/html; charset=utf-8"
print 

class CustomException(Exception):
   def __init__(self, value):
       self.parameter = value
   def __str__(self):
       return repr(self.parameter)

def collect_data_cat(year, month, cat):
    myfile = '../../flagged_data/all_month_users_%s%s%s' % (year, month, cat)
    # print "collect data cat, open file " , myfile
    all_time = -1
    try:
        f = open(myfile)
    except IOError:
        return -1,-1
    
    return f, all_time

def collect_data(year, month):
    file = '../../flagged_data/all_month_users_%s%s' % (year, month)
    #print "collect data"
    #print file, "<br/>"
    all_time = -1
    try: 
        if int(year) < -99 or int(month) < -99:
            file = '../../flagged_data/all_year_users_%s' % year
            all_time = int( year )
            if int(year) < -99:
                file = '../../flagged_data/all_time'
                all_time = 0
    except ValueError:
        return -1,-1

    try:
        f = open(file)
    except IOError:
        return -1,-1
    
    return f, all_time

def search_user_data(year, month, user_id):

    f, all_time = collect_data(year, month)
    if f == -1:
        print "wrong parameters, cannot find data for %s%s" % (year, month)
        exit()

    result = []
    f.readline()
    lines = f.readlines()
    lines.reverse()
    i = 1
    for line in lines:
        col =  line.split()
        #print col[1], " " , user_id, "<br/>"
        if int( col[1] ) == int(user_id): 
            return [i, int(col[0]) ]
        i += 1

    #we didnt find an entry
    return [ len(lines), 0]

def main_table(year, month, reverseLorzen=False, specialcat = ''):

    plot_name = 'ttmp_plot%s%s' % (year, month)
    data_file = 'ttmp%s%s' % ( year, month)
    pic_file =  '../tmp/pics/ttmp%s%s.png' % ( year, month)

    if specialcat == '': f, all_time = collect_data(year, month)
    else: 
        f, all_time = collect_data_cat(year, month, specialcat)
        print "<p>Fuer Kategorie %s</p>" % specialcat
    if f == -1:
        print "wrong parameters, cannot find data for %s%s" % (year, month)
        exit()

    if all_time == 0: print "<p>Alle Sichtungsresultate seit Januar 2009</p>" 
    elif all_time == -1: print "<p>Jahr %s, Monat %s </p>" % (year, month)
    else: print "<p>Alle Sichtungsresultate für das Jahr %s</p>" % year

    f.readline()
    lines = f.readlines()
    if len(lines) == 0: 
        print "Leider keine Daten vorhanden fuer diese Anfrage"
        return
    numberFlagged = [ int(line.split()[0]) for line in lines ]
    totalFlagged = sum( numberFlagged )

    ################################
    #start graph 
    #write out data
    f = open( data_file, 'w')
    cumm_sum = 0
    if reverseLorzen: numberFlagged.reverse()
    for i, n in enumerate(numberFlagged):
        cumm_sum += n
        f.write( '%s %s\n' % (i * 100.0 / len( numberFlagged), 
                              cumm_sum * 100.0/totalFlagged ) )
    f.close()

    graph_title = 'Lorenz curve'
    myYrange = ''
    ylabel = "Prozent Sichtungen"
    with_lines = 'with lines'
    gnuplot =\
    """
    set terminal png enhanced #size 800,800
    set xlabel "Prozent Sichter"
    set ylabel "%(ylabel)s"
    %(yrange)s

    set grid

    set xtics nomirror
    set ytics nomirror 
    set border 3
    set nokey

    set output "%(pic_file)s"
    set title "%(graph_title)s"
    plot "%(data_file)s" using 1:2 %(with_lines)s
    """ % {'data_file' : data_file, 'graph_title' : graph_title,
           'with_lines' : with_lines, 'yrange' : myYrange, 
           'ylabel' : ylabel, 'pic_file' : pic_file}

    f = open(plot_name, 'w')
    f.write( gnuplot)
    f.close()

    import os 
    os.system( "%s %s" % (gnuplot_path, plot_name ) ) 

    mytext =  "<img src=\"%s\">" % pic_file
    #end graph
    #########################################

    #use inequality.py from 
    #GPL(c): Goetz Kluge, Munich 2004-09-17
    #
    #inequality.lua 1.4.0: inequality computations for welfare economics
    #GPL(c): Goetz Kluge, Munich 2007-07-07
    data = [ [1, n] for n in numberFlagged] 
    # print "Here I want to print my data"
    # print data
    myinequality,redundancy,equality,variation,mysum,absolute = inequality.ineq( data )

    print """<p>Total wurden %s Sichtungen von %s Sichtern getätigt. 
        Der <a href='http://de.wikipedia.org/wiki/Gini-Koeffizient'>
        Gini-Koeffizient</a> betraegt %s.</p>
        """ % (str( totalFlagged ), str(len(numberFlagged)),  str( myinequality.Gini ) )
    print "<table>"
    print "<tr><th>Rang</th><th>Sichtungen</th><th>WP-UserID</th><th>Prozent</th><th></th></tr>"
    print "<tr><td> </td><td> </td><td> </td><td> </td>" #dummy
    print "<td width=10></td>" #empty coloumn to make some space

    i = 1
    lines.reverse()
    top1pcnt = len(numberFlagged) / 100 
    top2pcnt = len(numberFlagged) / 50 
    addtop1 = 0
    addtop2 = 0
    mytable = ''
    for line in lines:
        col =  line.split()
        if i <= top1pcnt: addtop1 += int( col[0] )
        if i <= top2pcnt: addtop2 += int( col[0] )
        myuser = int( col[1] )
        if myuser in optinHash.optinhash: 
            myuser = '<b>' + optinHash.optinhash[ myuser ] + '</b>'
        mytable += "<tr>"
        mytable += "<td>%d</td>"   % i
        mytable += "<td>%s</td>" % col[0]
        mytable += "<td>%s</td>" % str(myuser)
        mytable += "<td>%.2f</td>" % ( int( col[0]) * 100.0 / totalFlagged )
        mytable += "<td></td>" * 2
        mytable += "</tr>"
        i += 1

    mytext += "<p>Die Top 1%% (x=99%%) der Sichter (%s Sichter) waren für %.2f%% der Sichtungen verantwortlich.</p>" % (
       top1pcnt, addtop1 * 100.0/totalFlagged  )
    mytext += "<p>Die Top 2%% (x=98%%) der Sichter (%s Sichter) waren für %.2f%% der Sichtungen verantwortlich.</p>" % (
       top2pcnt, addtop2 * 100.0/totalFlagged  )
    mytext += "<p>Die Top 5 Sichter waren für %.2f%% der Sichtungen verantwortlich.</p>" % (
      sum( [int(line.split()[0]) for line in lines[:5]] ) * 100.0/totalFlagged)
    print "<td rowspan='24'> %s </td> </tr>" % (
            mytext )
    print mytable
    print "</table>"

    os.system( 'rm %s ' % plot_name )
    os.system( 'rm %s ' % data_file )

class Userdata:
    def __init__(self, year=-1, month_str='-1',rank=-1,flagged=-1):
        self.year =         year
        self.month_str =    month_str
        self.rank =         rank
        self.flagged =      flagged
    @property
    def month(self):
        return int(self.month_str)
    @property
    def month_year_str(self):
        return '%s%s' % (self.year, self.month_str)
    @property
    def month_year_sep(self):
        return '%s-%s-01' % (self.year, self.month_str)

def main_plot(user_id, start_y, stop_y, start_m, stop_m, 
             rank=False , lines = False, yrange = -1):

    print "<p>Nachsichtungsgraph fuer User %s</p>" % user_id
    print '<!--'
    print 'Rohdaten (Monat, Rang, Sichtungen):'

    ##this doesnt work for some reason
    #plot_name = '/tmp/hroest_tmp_plot%s' % user_id
    #data_file = '/tmp/hroest_tmp_plot%s' % user_id
    #pic_file =  '/tmp/hroest_tmp%s.png' % user_id
    #plot_name = '/home/hroest/public_html/tmp/tmp_plot%s' % user_id
    #data_file = '/home/hroest/public_html/tmp/tmp%s' % user_id
    #pic_file =  '/home/hroest/public_html/tmp/pics/tmp%s.png' % user_id
    #plot_name = '../tmp/tmp_plot%s' % user_id
    #data_file = '../tmp/tmp%s' % user_id
    #pic_file =  '../tmp/pics/tmp%s.png' % user_id

    plot_name = 'tmp_plot%s' % user_id
    data_file = 'tmp%s' % user_id
    pic_file =  '../tmp/pics/tmp%s.png' % user_id
    start_date = "2009-01"
    month_tics = 2

    #user_id = 352933
    #year = 2010
    data = []
    for year in range(start_y, stop_y+1 ):
        starting = 1
        stopping = 12
        if year == start_y: starting = start_m
        if year == stop_y: stopping = stop_m
        for i in range(starting,stopping+1):
            month = "%02d" % int( i )
            result =  search_user_data( year, month , user_id)
            print year, ' ', month, " ", result
            u =  Userdata(year, month, result[0], result[1])
            data.append( u  )

    print '-->'

    #print data
    import csv
    f = open(data_file, 'w')
    w = csv.writer( f, delimiter=' ')
    if rank:
        w.writerows( [ [u.month_year_sep, u.rank] for u in data] )
    else:
        w.writerows( [ [u.month_year_sep, u.flagged] for u in data] )
    f.close()

    graph_title = 'User %s' % user_id
    with_lines = ''
    myYrange = ''
    ylabel = "Anzahl Sichtungen"
    if lines: with_lines = 'with lines'
    if yrange > -1: myYrange = 'set yrange [0:%s]' % yrange
    if rank: ylabel = "Rang"
    gnuplot =\
    """
    set terminal png enhanced #size 800,800
    set xlabel "Monat"
    set ylabel "%(ylabel)s"
    %(yrange)s

    set xdata time
    set timefmt "%%Y-%%m-%%d"
    set format x "%%m.%%Y"

    #Rotation only for TT fonts...so no luck here
    #set xtics border scale 3,2 mirror rotate by 45  offset character 0, -5, 0 
    set xtics "%(start_date)s", 2678400*%(months)s rotate by 90 \
            offset character 0, -3, 0 # autofreq
    #set xtics "2009-01", 2678400*2 rotate by 45 offset character -4, -2, 0
    #set xtics "01/01/2009", 2678400*4
    set mxtics 2
    set xtics nomirror
    set ytics nomirror 
    set border 3
    set nokey

    set output "%(pic_file)s"
    set title "%(graph_title)s"
    plot "tmp%(user_id)s" using 1:2 %(with_lines)s
    """ % {'user_id' : user_id, 'graph_title' : graph_title,
           'with_lines' : with_lines, 'yrange' : myYrange, 
           'ylabel' : ylabel, 'pic_file' : pic_file, 'start_date' : start_date, 
           'months' : month_tics }

    f = open(plot_name, 'w')
    f.write( gnuplot)
    f.close()

    import os 
    os.system( "%s %s" % (gnuplot_path, plot_name ) ) 

    print '<br/>' * 2
    print "<img src=\"%s\">" % pic_file

    #cleanup
    os.system("rm %s" % plot_name)
    os.system("rm %s" % data_file)

def needs_update(year, month):
    raise CustomException('We do not update over the web. Let cron do that.')

    try: 
        year = int( year )
        month = int( month )
    except ValueError:
        return -1
    #is the user asking for data of this month?
    if not(year == this_year and month == this_month): return

    today = datetime.date.today()
    now = datetime.datetime.now()

    now = time.mktime(now.timetuple())
    latest_file = '../../flagged_data/latest_actualisation'
    f = open( latest_file ); back_then = float ( f.readline()  )
    f = open(latest_file , 'w'); f.write( str( now ) + '\n'  )
    f.close()

    seconds_since_last_load = now - back_then
    update_every = 60 * 60
    if seconds_since_last_load > 2:
        print "sorry for the wait, i had to generate new data"
        db = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf")
        print now - back_then
        start = time.time()
        create_data( db, this_year, this_month )
        end = time.time()
        print "uhhhh, this took me %s s" % (end - start)

###create all data for a given year
##db = MySQLdb.connect(read_default_file="/home/hroest/.my.cnf")
##for i in range(1,13):
##    create_data(db, 2008, i)

###########################################################################
###########################################################################
###########################################################################

import cgi 
form = cgi.FieldStorage()   # FieldStorage object to

print "<title>Nachsichten Statistik</title>"
print "<h1>Nachsichten nach User</h1>"


myform = """
<FORM action="nachsichten.py" method="post">
    <P>
    <label for="year">Jahr</label>
        <input type="text" name="year" value="%s">
    <label for="month">Monat</label>
        <input type="text" name="month" value="%s">
    <br/>
    <br/>
 <small>
 Man kann sich 
 <a href="http://de.wikipedia.org/wiki/Benutzer:HRoestBot/Nachsichten">hier</a>
 im Opt-In eintragen und dann erscheint der Benutzername im Ranking. <br/>
 Weiterhin kriegt man taegliche Updates mit den neusten Sichterstatistiken.
 </small>
    <br/>
    <br/>
    <INPUT type="submit" value="Send"> 
    </P>
 </FORM>
 <br/>
 Um die Resultate seit Beginn der gesichteten Versionen anzuzeigen, <br/>
 gibt man -100 in eines der beiden Felder ein. 

<FORM action="nachsichten.py" method="post">
    <P>
    <label for="user_graph">Graphik für User
    (Achtung, hier User_ID* eintragen, nicht Benutzernamen):</label>
        <input type="text" name="user_graph">
        <br/>
    <label for="lines">Mit Linien darstellen:</label>
        <input type="text" name="lines" value="0">
        <br/>
    <label for="rank">Rang statt # Sichtungen</label>
        <input type="text" name="rank" value="0">
    <br/>
    <br/>
    <INPUT type="submit" value="Send"> 
    </P>
 </FORM>
 <br/>
 <small>
 * Die User_ID kann in der Wikipedia unter "Einstellungen" eingesehen werden. 
 Einfach kopieren was bei "Benutzer-ID" steht. <br/>
 <p>
 Dieses Tool benutzt die GMT/UTC und liefert daher leicht andere Antworten als <br/>
 Tools, die nach der deutschen Zeit rechnen.
 </p>
""" % (this_year, this_month)

#main if statement
if form.has_key('month') and form.has_key('year'):
    month = form.getvalue('month')
    month = "%02d" % int( month )
    year = form.getvalue('year')
    #needs_update( year, month)
    reverseLorenz = False
    specialCategory = ''
    if form.has_key('reverseLorenz'): reverseLorenz = True
    if form.has_key('specialCategory'): specialCategory = form.getvalue('specialCategory')
    if form.has_key('exp'):
        main_table_exp( year, month, reverseLorenz, specialCategory )
    else:
        main_table( year, month, reverseLorenz, specialCategory )
elif form.has_key('user_graph'):
    rank = False
    lines = False
    yrange = -1
    error = False
    try:
        user_id = form.getvalue( 'user_graph').strip()
        user_id = int( user_id )
    except:
        print '<font color="Red">Please user a number for the user_id</font>'
        error = True
    try:
        if form.has_key('rank'):
            rank = form.getvalue( 'rank')
            if int(rank) == 1: rank = True
            else: rank = False
        if form.has_key('lines'):
            lines = form.getvalue( 'lines')
            if int(lines) == 1: lines = True
            else: lines = False
        if form.has_key('yrange'): yrange = form.getvalue('yrange')
    except ValueError:
        print '<font color="Red">Please use numbers for rank / lines parameters </font>'
        error = True

    #print rank, lines, yrange, '<br/>'
    if error: print myform
    else: 
        main_plot( user_id, 2009, this_year, 1, this_month, rank, lines, yrange  )
else:
    print myform

my = \
"""
http://toolserver.org/~hroest/cgi-bin/nachsichten.py?user_graph=352933&rank=1&yrange=50
"""

latest_file = '../../flagged_data/latest_actualisation'
f = open( latest_file ); latest_act = ( f.readline()  )
print """

 <hr>

 <p> <a href="/hroest/">Zurück zur Übersicht</a> </p>
"""
print "Letzte Aktualisierung der Daten (GMT/UTC):", latest_act
f.close()

extra_stuff =  """
    <small>some undocumented stuff: <br/><br/>
    For all requests, you can also use GET requests.  <br/> <br/>
    For the graph, you can set the paramters:         <br/>
     --user_graph = your user_id <br/>
     --rank       = show ranks (0/1) <br/>
     --lines      = show lines instead of points (0/1) <br/>
     --yrange     = set the max of the y-range <br/>
    <br/>
     For the tabl, you can set the parameters:<br/>
     -- month<br/>
     -- year<br/>

    </small>"""
print "<br/>" * 4
print "<br/>" * 20
print extra_stuff

#Some nice extra <a href="/hroest/cgi-bin/nachsichten.py?&month=5&year=2010&specialCategory=schweiz">http://toolserver.org/~hroest/cgi-bin/nachsichten.py?&month=5&year=2010&specialCategory=schweiz</a>
#      <br> <a href="/hroest/cgi-bin/nachsichten.py?&month=-100&year=-100">All time</a>
#      <br> <a href="/hroest/cgi-bin/nachsichten.py?&month=-100&year=2009">All of 2009</a>
#      <br> <a href="/hroest/cgi-bin/nachsichten.py?&month=-100&year=2010">All of 2010</a>

# now = datetime.datetime.now()
# now_unix = time.mktime( now.timetuple()  )  
# f = open( '/home/hroest/nachsichten.log', 'a')
# f.write( "%s, %s\n" % (str(int(now_unix) ), str( now)  ) )
# f.close()

