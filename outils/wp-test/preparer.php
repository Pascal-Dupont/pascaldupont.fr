<?php
// Installation de WordPress et activation de Kadence, Kadence Blocks et du thème enfant.
[$_, $cible, $port, $mode] = $argv;
$_SERVER['HTTP_HOST'] = '127.0.0.1:' . $port; $_SERVER['REQUEST_URI'] = '/'; $_SERVER['SERVER_PROTOCOL'] = 'HTTP/1.1';
define( 'WP_INSTALLING', true );
require $cible . '/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/upgrade.php';
require_once ABSPATH . 'wp-admin/includes/plugin.php';
wp_install( 'Pascal Dupont', 'admin', 'admin@exemple.test', false, '', 'admin-test-2026', 'fr_FR' );
update_option( 'WPLANG', 'fr_FR' );
update_option( 'permalink_structure', '/%postname%/' );
update_option( 'timezone_string', 'Europe/Paris' );
foreach ( array( 'sqlite-database-integration/load.php', 'kadence-blocks/kadence-blocks.php', 'wordpress-importer/wordpress-importer.php' ) as $p ) {
	$r = activate_plugin( $p );
	echo $p, ' : ', is_wp_error( $r ) ? $r->get_error_message() : 'actif', "\n";
}
switch_theme( $mode === 'complet' ? 'kadence-pascal' : 'kadence' );
echo 'thème : ', get_stylesheet(), "\n";
flush_rewrite_rules();
echo "ok\n";
