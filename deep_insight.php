<?PHP

if ( $_REQUEST['mode'] == 'rss' ) {
	$hide_header = 1 ;
	$hide_doctype = 1 ;
}

include_once ( "db_library.php");
include_once ( "tools_library.php");
/*
include_once ( "common.php" ) ;
*/
$mb = 30;
ini_set ('memory_limit', 1024*1024*$mb);

function get_tool_name () {
    return '' ;
}

function bytes ( $nr ) {
		return "$nr bytes" ;
}

function db_get_in_sight ( $language , $category ) {
	global $last_revs , $last_ts , $page_len , $only_redirects , $page_is_redirect ;
	$mysql_con = set_up_db ( $language ) ;
	$db = $language . 'wiki_p' ;
	make_db_safe ( $category ) ;
	
	// Pages with sighted versions
	if ( $only_redirects ) {
		$sql = "SELECT ".get_tool_name()." pr.page_id AS page_id, pr.page_title AS page_title FROM page pa,page pr,pagelinks,categorylinks,flaggedrevs WHERE cl_to=\"$category\" AND cl_from=pa.page_id AND pr.page_id=fr_page_id AND pa.page_namespace=0 " ;
		$sql .= "AND pr.page_is_redirect=1 AND pl_from=pr.page_id AND pl_namespace=0 AND pl_title=pa.page_title" ;
	} else {
		$sql = "SELECT ".get_tool_name()." page_id,page_title FROM page,categorylinks,flaggedrevs WHERE cl_to=\"$category\" AND cl_from=page_id AND page_id=fr_page_id AND page_namespace=14" ;
	}
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	$reviewed_pages = array () ;
	while ( $o = mysql_fetch_object ( $res ) ) {
		$reviewed_pages[$o->page_id] = $o->page_title ;
	}


	if ( $only_redirects ) {
		$sql = "SELECT ".get_tool_name()." pr.page_id AS page_id, pr.page_title AS page_title, pr.page_len AS page_len, pr.page_is_redirect AS page_is_redirect " ;
		$sql .= "FROM page pa,page pr,pagelinks,categorylinks WHERE cl_to=\"$category\" AND cl_from=pa.page_id AND pa.page_namespace=0 " ;
		$sql .= "AND pr.page_is_redirect=1 AND pl_from=pr.page_id AND pl_namespace=0 AND pl_title=pa.page_title" ;
	} else {
		$sql = "SELECT ".get_tool_name()." page_id,page_title,page_len,page_is_redirect FROM page,categorylinks WHERE cl_to=\"$category\" AND cl_from=page_id AND page_namespace=14" ;
	}
	$res = mysql_db_query ( $db , $sql , $mysql_con ) ;
	$unreviewed_pages = array () ;
	while ( $o = mysql_fetch_object ( $res ) ) {
		if ( isset ( $reviewed_pages[$o->page_id] ) ) continue ; // Already reviewed
		$unreviewed_pages[$o->page_id] = $o->page_title ;
		$page_len[$o->page_id] = $o->page_len ;
		$page_is_redirect[$o->page_id] = $o->page_is_redirect ;
	}

	return $unreviewed_pages ;
}

function myenc ( $t ) {
	return  (  $t );
}

$language = get_request ( 'language' , 'de' ) ;
$category = get_request ( 'category' , '' ) ;
$depth = get_request ( 'depth' , 0 ) ;
$mode = get_request ( 'mode' , '' ) ;
$only_redirects = get_request ( 'redirects' , false ) ;
$testing = isset ( $_REQUEST['test'] ) ;

if ( $language == 'pl' ) $catname = 'Kategoria' ;
else $catname = 'Kategorie' ;


$category = str_replace ( '_' , ' ' , $category ) ;

$data = db_get_articles_in_category ( $language , $category , $depth-1 , 14 ) ;


if ( count ( $data ) == 0 ) {
	$category = urldecode ( $category ) ;
	$data = db_get_articles_in_category ( $language , $category , $depth-1 , 14 ) ;
}

//if ( $testing ) print_r ( $data ) ;

if ( !isset ( $data[$category] ) ) array_unshift ( $data , $category ) ;

if ( $mode == 'rss' ) {
	header('Content-type: text/xml; charset=utf-8');
	print '<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>' ;
	print '<title>' ;
	print "Neu zu sichtende Artikel in Kategorie:" . myenc ( $category ) . ", Tiefe $depth (" . count ( $data ) . " Kategorien insgesamt)" ;
	print '</title>' ;
	print '<ttl>5</ttl>' ;
	print '<link>' . htmlspecialchars ( "http://toolserver.org/~magnus/deep_insight.php?category=$category&depth=$depth&language=$language" ) . '</link>' ;
	print "<language>$language-$language</language>" ;
} else {
	print '<html>' ;
	print '<head>' ;
    print '<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">' ;
	print '<link href="'."http://toolserver.org/~magnus/deep_insight.php?category=".htmlspecialchars($category)."&depth=$depth&mode=rss&language=$language".'" rel="alternate" type="application/rss+xml" title="Diese Seite als RSS-Feed">' ;
	print '</head>' ;
	print '<body>' ;
	//print get_common_header ( "deep_insight.php" , "Deep InSight" ) ;
	$cd = count ( $data ) ;
	if ( $category == '' ) {
		$or = $only_redirects ? 'checked' : '' ;
		print "<form method='get'>" ;
		print "<table>" ;
		print "<tr><th>Language</th><td><input type='text' name='language' value='$language' /></td></tr>" ;
		print "<tr><th>Category</th><td><input type='text' name='category' value='$category' /></td></tr>" ;
		print "<tr><th>Depth</th><td><input type='text' name='depth' value='$depth' /></td></tr>" ;
		print "<tr><th>Mode</th><td>" ;
		print "<input type='radio' name='mode' value='web' id='mode_web' checked /><label for='mode_web'>Web page</label>" ;
		print "<input type='radio' name='mode' value='rss' id='mode_rss' /><label for='mode_rss'>RSS feed</label>" ;
		print "</td></tr>" ;
		//print "<tr><th>&nbsp;</th><td><input type='checkbox' name='redirects' id='redirects' value='1' $or /><label for='redirects'>Show only redirects</label></td></tr>" ;
		print "<tr><th>&nbsp;</th><td><input type='submit' name='doit' value='Do it' /></td></tr>" ;
		print "</table>" ;
		print "</form>" ;
		print "</body></html>" ;
		exit ;
	}
	print "<h1>$category</h1>" ;
	if ( $language == 'pl' ) {
		$f = array ( 'kategorię','kategorie','kategorii' ) ;
		print "Przeszukano $cd " . pluralPl ( $cd , $f ) . " w poszukiwaniu nieprzejrzanych artykułów..." ; myflush() ;
	} else {
		print "Durchsuche $cd Kategorien auf neu zu sichtende Artikel..." ; //myflush() ;
	}
	print '<ol>' ;
}

$had_that = array () ;
foreach ( $data AS $d ) {
	$url = "http://$language.wikipedia.org/w/index.php?title=Spezial%3ASeiten_mit_ungesichteten_Versionen&namespace=14&category=" . myurlencode ( $d ) ;
//	$pages = db_get_articles_in_category ( $language , $d , 0 , 0 ) ;
	$last_revs = array () ;
	$last_ts = array () ;
	$page_len = array () ;
	$page_is_redirect = array () ;
	$oos = db_get_in_sight ( $language , $d ) ;
	foreach ( $oos AS $k => $v ) { // Show each article only once
		if ( isset ( $had_that[$v] ) ) unset ( $oos[$k] ) ;
	}
	if ( count ( $oos ) == 0 ) continue ;

	if ( $mode == 'rss' ) {
		$nd = str_replace ( '_' , ' ' , $d ) ;
		print '<item>' ;
		print '<title>' . myenc ( "$catname:$nd" ) . '</title>' ;
		print '<link>' ;
		print htmlspecialchars ( $url ) ;
		print '</link>' ;
		$out = '<ol>' ;
		$last = '' ;
		foreach ( $oos AS $k2 => $t ) {
			$len = ' (' . bytes ( $page_len[$k2] ) . ')' ;
			$out .= '<li><a target="_blank" href="http://' . $language . '.wikipedia.org/w/index.php?redirect=no&title=' . urlencode ( $t ) . '">' ;
			$out .= myenc ( $t ) . "</a>$len</li>" ;
			$had_that[$t] = 1 ;
		}
		$out .= '</ol>' ;
		$guid = myenc ( "$language:$d:" . md5 ( $out ) ) ;
		print "<guid>$guid</guid>" ;
		print "<description>" . htmlspecialchars ( $out ) . "</description>" ;
		print '</item>' ;
	} else {
		$list = '<ol>';
		foreach ( $oos AS $k2 => $t ) {
			$len = ' (' . bytes ( $page_len[$k2] ) . ')' ;
			if ( $page_is_redirect[$k2] ) $len .= ' [REDIRECT]' ;
			$list .= '<li><a target="_blank" href="' . get_wikipedia_url ( $language , 'Kategorie:'.$t ) . '&redirect=no">' ;
			$list .= $t . "</a>$len</li>" ;
			$had_that[$t] = 1 ;
		}
		$list .= '</ol>' ;
		print "<li><a href=\"$url\" target='_blank'>$catname:$d</a>$list</li>" ;
	//	myflush () ;
	}
}


if ( $mode == 'rss' ) {
	print '</channel></rss>' ;
} else {
	print '</ol><hr/>' ;
	$cht = count ( $had_that ) ;
	if ( $language == 'pl' ) {
		print "Znaleziono $cht " . pluralPl ( $cht , array ( 'nieprzejrzany artykuł','nieprzejrzane artykuły','nieprzejrzanych artykułów' ) ) . '.' ;
	} else {
		print $cht . ' neu zu sichtende Artikel gefunden.</body></html>' ;
	}
}

?>
