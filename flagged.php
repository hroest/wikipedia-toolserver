<?PHP

/*
 * 
 * Deep out of Sight IMproved
 * (c) by Hannes Röst unless otherwise indicated.
 * this code is adapted from magnus' deep_out_of_sight.php 
 * Released under GPL.
 *
 */
include_once ( "db_library.php");
include_once ( "tools_library.php");
$mb = 30;
ini_set ('memory_limit', 1024*1024*$mb);

function get_fr( $language, $user ) {
    if ( !isset ( $mysql_con ) ) {$mysql_con = set_up_db($language);}
    $sql = "SELECT count(*) FROM flaggedrevs, user WHERE
            fr_user = user_id AND user_name = \"$user\"";

    $db = $language . 'wiki_p' ;
    $res = mysql_db_query ( $db , $sql , $mysql_con ) ;

}

//this will get all unreviewed pages that are in a given category
function db_get_unreviewed( $language, $category, $fast = 99, $namespace=0) {
    //global $mysql_con;
    if ( !isset ( $mysql_con ) ) {$mysql_con = set_up_db($language);}
    make_db_safe ( $category ) ;

    $sql = "SELECT page_id,page_title,page_latest,fp_stable, rev_len
    FROM page,categorylinks,flaggedpages, revision
    WHERE cl_to=\"$category\" AND cl_from=page_id AND fp_page_id=page_id 
    AND page_latest<>fp_stable AND page_namespace=$namespace
    AND rev_id=page_latest";

    $db = $language . 'wiki_p' ;
    $res = mysql_db_query ( $db , $sql , $mysql_con ) ;

    $reviewed_pages = array () ;
    while ( $o = mysql_fetch_object ( $res ) ) {
        $latest_size = $o ->rev_len;
        $current_rev = $o->page_latest;
        $stable_rev = $o->fp_stable;

        if($stable_rev >= $current_rev) 
        {
            // something is wrong here, lets leave
            print "<br/>Something is wrong here with ";
            print  $o->page_title;
            print " <br/>";
            continue;
        }

        if($fast == 1) {
            $reviewed_pages[ $o-> page_id ] = array( 'title' => $o->page_title,
                'stable_id' => $stable_rev);continue;}

        //now get the len of the last stable
        $sql = "SELECT rev_len FROM revision WHERE rev_id=$stable_rev";
        $res_inner = mysql_db_query ( $db , $sql , $mysql_con ) ;
        $o3 = mysql_fetch_object ( $res_inner ) ;
        $size_diff = $latest_size - $o3 -> rev_len;

        if($fast == 2) {
            $reviewed_pages[ $o-> page_id ] = array( 'title' => $o->page_title,
                 'diff' => $size_diff, 'stable_id' => $stable_rev);continue;}

        //now get the first unflagged revision
        while ( $current_rev != $stable_rev) {
            //$before_current_rev = $current_rev;
            $sql = "SELECT rev_parent_id, rev_timestamp FROM revision 
                    WHERE rev_id=$current_rev";
            $res_inner = mysql_db_query ( $db , $sql , $mysql_con ) ;
            $o2 = mysql_fetch_object ( $res_inner ) ;
            $current_rev = $o2->rev_parent_id;
            if($current_rev == 0) {break;}
            if(!$o2) {break;}
        }
        $first_unflagged_timestamp = $o2->rev_timestamp ;


        $reviewed_pages[ $o-> page_id ] = array( 'title' => $o->page_title, 
            'timestamp' => $first_unflagged_timestamp, 'diff' => $size_diff ,
            'stable_id' => $stable_rev);
     }
    return $reviewed_pages;
}

///////////////////////////////////////////////////////////////////////////
//   OPTIONS
///////////////////////////////////////////////////////////////////////////
$language = get_request ( 'language' , 'de' ) ;
$category = get_request ( 'category' , '' ) ;
$depth = get_request ( 'depth' , 1 ) ;
$namespace = get_request ( 'namespace' , 0 ) ;
$sortby = get_request ( 'sortby' , 'category' ) ;
$exclude_noncode = get_request ( 'exclude' , '' ) ;
$fast = get_request ( 'fast' , 1 ) ;
$show_color_at = get_request( 'show_color_at', 300);
$diff_only = get_request( 'diff_only', 0);

//we dont need these options
$extended = get_request ( 'extended' , 0 ) ;
$simple = get_request ( 'simple' , 0 ) ;

//rss?
$mode = get_request ( 'mode' , '' ) ;
$catname = 'Kategorie' ;


//print $exclude[0];
//print $exclude[1];
//$exclude = array( "Dendrologe", "Botaniker", "Forstwissenschaftler" );

print '<html><head><meta http-equiv="Content-Type" content="text/html;charset=UTF-8"></head>' ;
if ($category == '') {
        $t1 = 'Zeigt Artikel in (Unter)kategorien, die nachgesichtet werden müssen.' ; 
        $t2 = 'Sprache' ;
        $t3 = 'Tiefe' ;
        $t4 = 'Kategorie und direkte Unterkategorien' ;
        $t4B = 'Alle Unterkategorien' ;
        $t5= 'Sortiere nach' ;
        $t6= 'Namensraum' ;
        $t9 = 'Los!' ;

    print "<body>
    <h1>Flagged Revisions Tool</h1>
    <i>$t1</i><br/>
    <form method='get' action='flagged.php'>
    <table>
    <tr><th>$t2</th><td><input type='text' name='language' value='$language' size='30' /></td></tr>
    <tr><th>$catname</th><td><input type='text' name='category' value='' size='30' /></td></tr>
    <tr><th>exclude*</th><th>
        <textarea name='exclude' rows='3' cols='80'></textarea></th>
    </tr>
    <tr><th>$t3**</th><td><input type='text' name='depth' value='$depth' /> </td></tr>
    <tr><th>$t6</th><td><input type='text' name='namespace' value='$namespace' /> 0=articles, 14=categories</td></tr>
    <tr><th></th><td><input type='submit' name='doit' value='$t9' /></td></tr>
    <tr><th>$t5</th><th>
       <Input type = 'Radio' Name ='sortby' value= 'size' checked='checked' >Size
       <Input type = 'Radio' Name ='sortby' value= 'size_reverse'  >Size (reverse)
    </tr>
    <tr><th></th><th>
       <Input type = 'Radio' Name ='sortby' value= 'title'         >Title
       <Input type = 'Radio' Name ='sortby' value= 'title_reverse' >Title (reverse)
    </tr>
    <tr><th></th><th>
       <Input type = 'Radio' Name ='sortby' value= 'time'          >Time
       <Input type = 'Radio' Name ='sortby' value= 'time_reverse'  >Time (reverse)
    </tr>
    </table>
    <br/>
    *Format: \"cat1;cat2;cat3\".  <br/>
    This might not do what you expect it to do.<br/>
    If you list a category under \"exclude\", this category is not considered<br/>
    in the recursive search for articles. If the article you want to exclude is<br/>
    encountered in a different category during the search, it will still be <br/>
    included.
    <br/>
    <br/>
    ** 1=$t4, -99 = $t4B
    </form>
    <p> <a href='http://toolserver.org/~hroest/'>Zurueck zur Uebersicht</a> </p>
    </body>" ;
    print '</html>' ;
    exit  ;

}

// Process input
$exclude = str_replace( " ", "_", $exclude_noncode);
$exclude = split(";", $exclude);

//print $exclude;
print "Excluding: ";
foreach($exclude AS $ex) {
    print mydecode($ex) . ";";
}
print "<br/>";

//some options are mutually exclusive -- you cannot be fast and sort by time
if ($fast == 1) {
    if ($sortby =='title' or $sortby == 'title_reverse' or $sortby == 'category'){
        $myfast = 1;}  
    if ($sortby == 'size' or $sortby == 'size_reverse'){$myfast = 2;}
    if ($sortby == 'time' or $sortby == 'time_reverse'){$myfast = 99;}
} else $myfast = 99;


//Lets start!
//We get the categories we need
$starttime = microtime(true); 

//get all articles in category with ns == 14 (category ns)
$data = db_get_articles_in_category ( $language , $category , $depth-1 , 14 , 
    $exclude ) ;

if ( count ( $data ) == 0 ) {
    $category = utf8_encode ( $category ) ;
    $data = db_get_articles_in_category( $language , $category , $depth-1 , 14 ,
    $exclude ) ;
}
//now also add the root category itself
if ( !isset ( $data[$category] ) ) array_unshift ( $data , $category ) ;

print "Durchsuche " .  count ( $data ) . " Kategorien.";

$output = array () ;
foreach ( $data AS $d ) {
    $my_unreviewed = db_get_unreviewed ( $language, $d, $myfast, $namespace);
    foreach ( $my_unreviewed AS $k => $v ) { // Show each article only once
        if ( isset ( $output[$k] ) ) {unset ( $my_unreviewed[$k] );}
    }

    //print mydecode($d) . "\n <br/>";
    //dont need this
    //if ( count ( $my_unreviewed ) == 0 ) continue ;

    //do NOT use array_merge, this will rename keys!
    $output =  $output + $my_unreviewed;
}

if ($sortby == 'size')              array_sort($output,'diff'); 
else if ($sortby == 'title')        array_sort($output,'title'); 
else if ($sortby == 'time')         array_sort($output,'!timestamp'); 
else if ($sortby == 'size_reverse') array_sort($output,'!diff'); 
else if ($sortby == 'title_reverse')array_sort($output,'title'); 
else if ($sortby == 'time_reverse') array_sort($output,'timestamp'); 
else if ($sortby == 'category') {;}

$printlist = '';
$taburls = array () ;
foreach ($output AS $page) {
    $t =  str_replace ( "_" , " " , $page['title'] );
    $old_id = $page['stable_id'];
    $url = get_wikipedia_url ( $language , $t ) . 
        "&diffonly=$diff_only&oldid=$old_id&diff=cur" ;

    $timediff = get_time_diff( $page['timestamp'], 'D' );
   
    //size
    $diff = $page['diff'];
    if ( abs ( $diff ) > $show_color_at) $bg = '#AAAAAA';
    else $bg = '#FFFFFF';
    if ( $diff > 0 ) 
        $diff_display = "<span style='color:green;background:$bg'>+$diff</span>" ;
    else if ( $diff < 0 ) 
        $diff_display = "<span style='color:red;background:$bg'>$diff</span>" ;
    else $diff_display = "<span style='background:$bg'>$diff</span>" ;

    $note = " ";
    if($myfast > 1)  $note .= "Diff = " . $diff_display;
    if($myfast > 2)  $note .= " Alter = "  . $timediff . " Tage" ;

    $printlist .= '<li><a target="$target" href="' . $url . '">' ;
    $printlist .= $t . "</a>$note</li>\n" ;

    $taburls[] = $url ;
}

///////////////////////////////////////////////////////////////////////////
// Print out starts here
///////////////////////////////////////////////////////////////////////////

flush();

print "<ol>" . $printlist . "</ol>";
print "\n\n<br/>Today: " . date(DATE_RSS) . "\n<br/>";
$endtime = microtime(true); 
$timediff = $endtime - $starttime;
print "This query took $timediff seconds. <br/>";

print count( $output ) . " nachzusichtende Artikel gefunden. ";


//
//********************************************* 
//Javascript from Magnus
//********************************************* 
//
$out = '' ;
print "<script type='text/javascript'>" ;

if ( count ( $taburls ) > 20 ) {
    print "function open20 () {\n" ;
    for ( $a = 0 ; $a < 20 ; $a++ ) {
        print "window.open ('".$taburls[$a]."', '_blank');\n" ;

    }
    print "return false;};\n\n" ;
    $out .= "<a href='#' onclick='open20()'>Open first 20 in tabs</a> " ;
}

if ( count ( $taburls ) > 50 ) {
    print "function open50 () {\n" ;
    for ( $a = 0 ; $a < 50 ; $a++ ) {
        print "window.open ('".$taburls[$a]."', '_blank');\n" ;

    }
    print "return false;};\n\n" ;
    $out .= "<a href='#' onclick='open50()'>Open first 50 in tabs</a> " ;
}

print "function open_all() {\n" ;
for ( $a = 0 ; $a < count($taburls) ; $a++ ) {
    print "window.open ('".$taburls[$a]."', '_blank');\n" ;
}
print "return false;};\n\n" ;
$out .= "<a href='#' onclick='open_all()'>" ;
$out .= "Open all in tabs" ;
$out .= "</a> " ;

print "</script>$out" ;

print '<p> <a href="http://toolserver.org/~hroest/">Zurueck zur Uebersicht</a> </p>';
print '</html>' ;

?>
