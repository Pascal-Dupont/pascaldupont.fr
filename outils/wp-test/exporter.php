<?php
// php exporter.php <dossier wp> <port> <fichier.xml> : exporte les pages du site (format WXR, comme Outils > Exporter > Pages).
[$_, $cible, $port, $sortie] = $argv;
$_SERVER['HTTP_HOST'] = '127.0.0.1:' . $port; $_SERVER['REQUEST_URI'] = '/';
require $cible . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/export.php';
// Seules les pages du site (repérées par _pd_page) sont exportées : on retire les autres (page d'exemple, essais).
add_filter( 'export_query', function ( $sql ) {
	global $wpdb;
	return $sql . " AND {$wpdb->posts}.ID IN ( SELECT post_id FROM {$wpdb->postmeta} WHERE meta_key = '_pd_page' )";
} );
ob_start();
export_wp( array( 'content' => 'page', 'status' => 'publish' ) );
$xml = ob_get_clean();
foreach ( headers_list() as $h ) { /* en CLI, rien à faire */ }
$xml = str_replace( 'http://127.0.0.1:' . $port, 'https://pascaldupont.fr', $xml );
file_put_contents( $sortie, $xml );
echo 'pages exportées : ', substr_count( $xml, '<item>' ), ' -> ', $sortie, "\n";
