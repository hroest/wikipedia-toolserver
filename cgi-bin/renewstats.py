#!/usr/bin/python
# -*- coding: utf-8  -*-
import cgitb; cgitb.enable()
import datetime, time
import sys, os
sys.path.append( '/data/project/hroest/' )
sys.path.append( '/data/project/hroest/meta' )
# sys.path.append( '/data/project/hroest/bot/pywikibot-compat/' )
sys.path.append( '/data/project/hroest/bot/pywikibot/' )
import optinHash
import general_lib
import ReviewBotLib as h_lib_api
import ReviewBotLib
import wikipedia
site = wikipedia.getSite()
import cgi
form = cgi.FieldStorage()   # FieldStorage object to

import MySQLdb
db = MySQLdb.connect(read_default_file=general_lib.mysql_config_file, host=general_lib.mysql_host)
optinhashfile = '/data/project/hroest/optinHash.py'
optin_page = 'Benutzer:HRoestBot/Nachsichten/SichterOptIn'


today = datetime.date.today()
now = datetime.datetime.now()
this_year = today.year
this_month = today.month
start = time.time()

print "Content-type: text/html; charset=utf-8"
print 

myform = """
<p>
Wenn du deinen Wikipedia-Benutzernamen <a href="https://de.wikipedia.org/wiki/Benutzer:HRoestBot/Nachsichten/SichterOptIn">hier</a>
eingetragen hast, kannst du deinen Wikipedia-Benutzernamen in das untenstehende 
Formular eintragen und du erhaeltst sofort ein Update deiner Sichterbeitraege
und Sichtertabelle auf deiner Benutzerseite. Beachte, dass eine
Abfrage laenger dauern kann (ev. bis eine Minute und mehr), also sei geduldig.
Beachte auch, dass nur eine Abfrage pro Zeit laufen kann.
</p>
<FORM action="renewstats.py" method="post">
    <label for="user_name">Benutzername</label>
        <input type="text" name="user_name">
    <br/>
    <INPUT type="submit" value="Send"> 
    </P>
 </FORM>
""" 

print myform

if not form.has_key('user_name'): 
    print '<hr> <p> <a href="https://tools.wmflabs.org/hroest/">Zurück zur Übersicht</a> </p>'
    exit()
user = form.getvalue( 'user_name' )


#first check whether the user is in the optin-hash
if user not in optinHash.optinhash.values():
    ReviewBotLib.renew_optinhash(db, optin_page, optinhashfile)
    reload( optinHash )
    if user not in optinHash.optinhash.values():
        print "Not allowed for this user"
        exit()

# general_lib.release_pywiki_lock()

# general_lib.release_pywiki_lock_if_older_than()
if True: 
    # general_lib.acquire_pywiki_lock():
    #print "acquired lock<br/>"
    print "Konnte den Prozess starten.<br/>"
    ## #f = open('reviewed.dat', 'w' ) 
    ## #f.write( user )
    ## #f.close()
    h_lib_api.postReviewedPagesandTable( user.decode('utf-8'), site, async=False )
    #os.system('qsub -N reviewpages /home/hroest/postReviewedPagesandTables.sh')
    print "ERFOLG! Der Auftrag wurde gestartet<br/>"
    print "Die Aktualisierung kann aber zeitversetzt erfolgen!<br/>"
    print "Habe die Tabellen fuer den User %s erneuert." % user
    # general_lib.release_pywiki_lock()
else:
    print " <br/>Konnte den Prozess nicht starten.<br/>"
    print "Das heisst, dass gerade ein anderer Benutzer das Tool gerade benutzt.<br/>"
    print "Du musst deshalb warten. <br/> <br/>"
    print "Der andere Prozess %s Sekunden alt." % general_lib.get_lock_age()
    #print " <br/>could NOT acquire lock <br/>"
    #print "This means that another user is using the lock <br/>"
    #print "you will have to wait. <br/> <br/>"
    #print "The lock is from "
    #print general_lib.get_lock_value()
    #print " (das ist <a href='http://wwp.greenwichmeantime.com/time/scripts/clock-8/runner.php'>GMT</a>)  "
    print "<br/>Wenn diese Zeitangabe aelter "
    print "als ein paar Minuten ist, informiere Hannes."
    #print "Bitte ueberpruefe die Uhr zuerst, GMT ist NICHT die lokale Zeit."
    #print " (this is <a href='http://wwp.greenwichmeantime.com/time/scripts/clock-8/runner.php'>GMT</a>) <br/> if this is older than 2 hours"
    #print "and several minutes, please inform Hannes. Please do not write just because of summer time, check the clock first :-) "


end = time.time()
query_time = end - start
print """
 <hr>

 <p>
 This query took %s s
""" % query_time
