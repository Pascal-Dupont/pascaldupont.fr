<?php
// php lire.php <dossier wp> <slug> : affiche le contenu brut d'une page
[$_, $cible, $slug] = $argv;
$_SERVER['HTTP_HOST'] = '127.0.0.1'; $_SERVER['REQUEST_URI'] = '/';
require $cible . '/wp-load.php';
$p = get_page_by_path( $slug );
echo $p ? $p->post_content : "introuvable\n";
