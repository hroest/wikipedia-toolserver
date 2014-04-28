<?PHP
/*
 * db_library.php
 * Common db tools and functions.
 * (c) by Hannes Röst unless otherwise indicated.
 * Released under GPL.
 *
 */

function db_get_con_new( $language , $project) {
    return set_up_db ( $language );
}

function set_up_db( $language, $project = 'wiki' ) {
    //global $mysql_con;
    //TODO instead of wiki use $project
    //$mycnf = parse_ini_file("/home/".get_current_user()."/.my.cnf");
    $mycnf = parse_ini_file("/data/project/hroest2/replica.my.cnf");
    //$server = $language.'wiki-p.db.toolserver.org';
    $server = $language.'wiki.labsdb';
    if( !$mysql_con = mysql_connect($server, $mycnf['user'], $mycnf['password'])) {
        print mysql_error();
        echo 'Could not connect to the db. sorry.';
        exit;
    }
    //mysql_select_db($language'wiki_p', $mysql_con);
    unset($toolserver_mycnf);
    return $mysql_con;
}

//magnus
function make_db_safe ( &$title ) {
    $title = ucfirst ( trim ( $title ) ) ;
    $title = str_replace ( ' ' , '_' , $title ) ;
    $title = str_replace ( '"' , '\"' , $title ) ;
#   $title = str_replace ( "'" , "\\'" , $title ) ;
}

?>
