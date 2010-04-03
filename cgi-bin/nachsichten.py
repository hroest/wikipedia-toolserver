#!/usr/bin/python
print "Content-type: text/html"
print 
print "<title>Nachsichten nach User</title>"
print "<h1>Nachsichten nach User</h1>"

year = '2010'
month = '01'
file = '../../flagged_data/all_month_users_%s%s' % (year, month)

f = open('../../all_month_users_march.out')
f = open('../../flagged_data/all_time')
f = open(file)

print "Jahr %s, Monat %s <br/>" % (year, month)

print "<table>"
print "<tr><th>Rang</th><th>Sichtungen</th><th>User</th></tr>"

f.readline()
lines = f.readlines()
lines.reverse()
i = 1
for line in lines:
    col =  line.split()
    print "<tr>"
    print "<td>", i,      "</td>"
    print "<td>", col[0], "</td>"
    print "<td>", col[1], "</td>"
    print "</tr>"
    i += 1

print "</table>"



exit()

import cgi 
form = cgi.FieldStorage()   # FieldStorage object to
if form.has_key('month') and form.has_key('year'):
    month = form.getvalue('month')
    year = form.getvalue('yeasr')
    #print peptides
    #peptides = input
    main( peptides, q1_w, q3_w, ssr_w, exp_key, db, high, low)
else:
    print """
<FORM action="nachsichten.py" method="post">
    <P>
    <label for="peptides">Peptides</label><br />
    <textarea cols="60" name="peptides" rows="20"></textarea>
    <br/>
    <br/>
    <INPUT type="submit" value="Send"> 
    </P>
 </FORM>
"""

