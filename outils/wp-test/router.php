<?php
// Routeur pour le serveur PHP intégré : sert les fichiers existants, sinon WordPress.
$racine = $_SERVER['DOCUMENT_ROOT'];
$chemin = parse_url( $_SERVER['REQUEST_URI'], PHP_URL_PATH );
if ( $chemin !== '/' && file_exists( $racine . $chemin ) && ! is_dir( $racine . $chemin ) ) {
	return false;
}
if ( is_dir( $racine . $chemin ) && file_exists( $racine . rtrim( $chemin, '/' ) . '/index.php' ) ) {
	$_SERVER['SCRIPT_NAME'] = rtrim( $chemin, '/' ) . '/index.php';
	require $racine . rtrim( $chemin, '/' ) . '/index.php';
	return;
}
$_SERVER['SCRIPT_NAME'] = '/index.php';
require $racine . '/index.php';
