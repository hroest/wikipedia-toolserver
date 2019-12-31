<?PHP
/*
 * tools_library.php
 * Common tools and functions.
 * (c) by Hannes Röst unless otherwise indicated.
 * Released under GPL.
 *
 */

//http://www.php.net/manual/en/function.array-multisort.php
//addition for numeric values by hroest
function array_sort_func($a,$b=NULL) {
   static $keys;
   if($b===NULL) return $keys=$a;
   foreach($keys as $k) {
      if(@$k[0]=='!') {
         $k=substr($k,1);
         if(@$a[$k]!==@$b[$k]) {
            if(is_numeric(@$a[$k])) {return (@$b[$k] > @$a[$k]); }
            return strcmp(@$b[$k],@$a[$k]);
         }
      }
      else if(@$a[$k]!==@$b[$k]) {
         if(is_numeric(@$a[$k])) {return (@$a[$k] > @$b[$k]); }
         return strcmp(@$a[$k],@$b[$k]); 
      }
   }
   return 0;
}

//http://www.php.net/manual/en/function.array-multisort.php
function array_sort(&$array) {
   if(!$array) return $keys;
   $keys=func_get_args();
   array_shift($keys);
   array_sort_func($keys);
   usort($array,"array_sort_func");       
} 


//magnus
//find user http request
function get_request ( $key , $default = "" ) {
    global $prefilled_requests ;
    if ( isset ( $prefilled_requests[$key] ) ) return $prefilled_requests[$key] ;
    if ( isset ( $_REQUEST[$key] ) ) return str_replace ( "\'" , "'" , $_REQUEST[$key] ) ;
    return $default ;
}


/**
 * Magnus
 * Returns the URL for a language/title combination
 * May be called with additional parameter $action
 */
function get_wikipedia_url ( $lang , $title , $action = "" , $project = "wikipedia" ) {
    $lang = trim ( strtolower ( $lang ) ) ;
    $url = "http://" ;
    if ( $lang != 'xxx' ) $url .= "{$lang}." ;
    if ( $lang == "commons" ) $url .= "wikimedia" ;
    else $url .= $project ;
    $url .= ".org/w/index.php?" ;
    if ( $action != "" ) $url .= "action={$action}&" ;
    $url .= "title=" . myurlencode ( $title ) ;
    return $url ;
}

//magnus
function myurlencode ( $t ) {
        $t = str_replace ( " " , "_" , $t ) ;
        $t = urlencode ( $t ) ;
        return $t ;
}

function mydecode ( $s ) {
    $s = utf8_decode ($s);
    $s = str_replace ( "_" , " " , $s ) ;
    return $s;
}

function myencode ( $s ) {
    $s = utf8_encode ($s);
    $s = str_replace ( " " , "_" , $s ) ;
    return $s;
}

function get_time_diff($timestamp, $return_as = 'D') {

    $year = date(Y) - substr( $timestamp, 0, 4)  ;
    $mon =  date(n) - substr( $timestamp, 4, 2)  ;
    $day =  date(j) - substr( $timestamp, 6, 2)  ;
    $hour = date(G) - substr( $timestamp, 8, 2)  ;
    $min =  date(i) - substr( $timestamp, 10, 2) ;

    if ($return_as == 'D') {
        $days = 360*$year + 30*$mon + $day;
        return $days;
    }
}


//magnus
function db_get_articles_in_category ( $language , $category , $depth = 0 , 
    $namespace = 0 , $exclude = array(), &$done_cats = array () , 
    $no_redirects = false , $limit = '' , $project = 'wikipedia' , 
    $only_redirects = false ) {

    // //print $done_cats[0] . $done_cats[1] . $category . "<br/>";
    // if (false) {
    // if ($category == 'Militärischer_Verband_(Schweiz)' ) {
    //     print 'dfd';
    // }
    // if ($category == 'Fernsehen_(Schweiz)' ) {
    //     print $category;
    //     print $exclude[2] . '<br/>';
    //     print $exclude[3] . '<br/>';
    // }
    // if ( in_array ( $category , $exclude ) ) print "excluding $category";
    // }

    if ( in_array ( $category , $done_cats ) )  return array () ;
    if ( in_array ( $category , $exclude ) )  return array () ;

    $mysql_con = db_get_con_new($language,$project) ;
    //$db = get_db_name ( $language , $project ) ;
    $db = $language . 'wiki_p' ;
    make_db_safe ( $category ) ;
    if ( $limit != '' ) $limit = "LIMIT $limit" ;
    $limit = str_replace ( 'LIMIT LIMIT' , 'LIMIT' , $limit ) ; // Some odd bug

    $ret = array () ;
    $subcats = array () ;
    $red = $no_redirects ? ' AND page_is_redirect=0' : '' ;
    if ( $only_redirects ) $red = ' AND page_is_redirect=1' ;

    $sql = "SELECT page_title,page_namespace FROM page,categorylinks 
        WHERE page_id=cl_from AND cl_to=\"{$category}\" $red $limit" ;
//  print "TESTING : $depth - $category : $sql<br/>" ;

    $res = mysql_db_query ( $db , $sql , $mysql_con ) ;
    while ( $o = mysql_fetch_object ( $res ) ) {

        if ( !isset ( $o->page_namespace ) ) continue ;
        if ( $o->page_namespace == 14 AND ($depth > 0 OR $depth < -99)  ) {
            $subcats[] = $o->page_title ;
        } else if ( $namespace >= 0 and $o->page_namespace != $namespace ) continue ;
        if ($namespace >= 0 and $o->page_namespace != $namespace ) continue;
        if (in_array( $o->page_title, $exclude ) ) continue;
        // if ( substr($o->page_title, 0, 11) == 'Grasshopper') print $category;
        $ret[$o->page_title] = $o->page_title ;
//      print "TESTING : $depth - $category / " . $o->page_title . "<br/>" ;
    }
    mysql_free_result ( $res ) ;

    $done_cats[] = $category ;
    foreach ( $subcats AS $sc ) {
//      print "Testing : $depth - $sc<br/>" ;
        $ret2 = db_get_articles_in_category ( $language , $sc , $depth - 1 , 
            $namespace , $exclude, $done_cats , $no_redirects , $limit , 
            $project ) ;
        foreach ( $ret2 AS $k => $v ) $ret[$k] = $v ;
    }

    return $ret ;
}


?>

