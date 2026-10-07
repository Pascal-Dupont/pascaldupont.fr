<?php
/**
 * Réglages Kadence 1.5.2 pour pascaldupont.fr, écrits en base à l'activation du thème enfant.
 *
 * - la palette globale va dans l'option `kadence_global_palette` (CHAÎNE JSON, partagée par tous les thèmes) ;
 * - les autres réglages vont dans les theme_mods du thème ACTIF (`theme_mods_kadence-pascal`).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/** Numéro de version des réglages : l'augmenter pour les réappliquer une fois sur un site déjà installé. */
define( 'PD_KADENCE_REGLAGES_VERSION', '1' );

/**
 * Palette sombre, dans l'ordre palette1 … palette9.
 */
function pd_kadence_couleurs() {
	return array(
		'#a3302f', // palette1 : accent (béret)
		'#c0403d', // palette2 : accent au survol (béret vif)
		'#e8e6e1', // palette3 : texte fort
		'#a9b6c0', // palette4 : texte doux
		'#c8b287', // palette5 : sable
		'#2c3a49', // palette6 : ligne
		'#223040', // palette7 : ardoise claire
		'#17202a', // palette8 : ardoise
		'#0d1217', // palette9 : fond (nuit)
	);
}

/**
 * Valeur de l'option `kadence_global_palette` : une chaîne JSON (jamais un tableau PHP).
 *
 * @return string
 */
function pd_kadence_palette_json() {
	$liste = array();
	foreach ( pd_kadence_couleurs() as $i => $couleur ) {
		$liste[] = array(
			'color' => $couleur,
			'slug'  => 'palette' . ( $i + 1 ),
			'name'  => 'Palette Color ' . ( $i + 1 ),
		);
	}
	// palette10 à palette15 : valeurs de Kadence 1.5.2. « #FfFfFf » (casse exacte) en palette10
	// veut dire « complémentaire calculée à partir de palette1 ».
	$extra = array(
		array( '#FfFfFf', 'Palette Color Complement' ),
		array( '#13612e', 'Palette Color Success' ),
		array( '#1159af', 'Palette Color Info' ),
		array( '#b82105', 'Palette Color Alert' ),
		array( '#f7630c', 'Palette Color Warning' ),
		array( '#f5a524', 'Palette Color Rating' ),
	);
	foreach ( $extra as $j => $e ) {
		$liste[] = array(
			'color' => $e[0],
			'slug'  => 'palette' . ( 10 + $j ),
			'name'  => $e[1],
		);
	}
	return wp_json_encode(
		array(
			'palette'        => $liste,
			'second-palette' => $liste, // les 3 jeux sont identiques : changer de jeu dans l'outil de personnalisation ne repasse pas en clair
			'third-palette'  => $liste,
			'active'         => 'palette',
		)
	);
}

/**
 * Theme mods Kadence. Chaque valeur est une structure COMPLÈTE : Kadence ne fusionne pas
 * une valeur enregistrée avec sa valeur par défaut (voir pd_kadence_theme_mods_complets()).
 *
 * @return array
 */
function pd_kadence_theme_mods() {
	$corps   = '"Hanken Grotesk", system-ui, -apple-system, "Segoe UI", sans-serif';
	$display = '"Newsreader", Georgia, "Times New Roman", serif';
	$titre   = function ( $desktop, $tablette, $mobile ) {
		return array(
			'size'       => array( 'desktop' => $desktop, 'tablet' => $tablette, 'mobile' => $mobile ),
			'sizeType'   => 'rem',
			'lineHeight' => array( 'desktop' => 1.1 ),
			'lineType'   => '-',
			'family'     => 'inherit',
			'google'     => false,
			'weight'     => '400',
			'variant'    => 'regular',
			'color'      => 'palette3',
		);
	};
	return array(
		// Fonds du site et du contenu.
		'site_background'       => array( 'desktop' => array( 'color' => 'palette9' ) ),
		'content_background'    => array( 'desktop' => array( 'color' => 'palette9' ) ),

		// Liens du contenu.
		'link_color'            => array(
			'highlight'      => 'palette5',
			'highlight-alt'  => 'palette3',
			'highlight-alt2' => 'palette9',
			'style'          => 'color-underline',
		),

		// Typographie : polices servies par le thème enfant (assets/fonts.css), donc google = false.
		'base_font'             => array(
			'size'       => array( 'desktop' => 17 ),
			'lineHeight' => array( 'desktop' => 1.6 ),
			'family'     => $corps,
			'google'     => false,
			'weight'     => '400',
			'variant'    => 'regular',
			'color'      => 'palette3',
		),
		'heading_font'          => array( 'family' => $display ),
		'h1_font'               => $titre( 3.2, 2.6, 2.2 ),
		'h2_font'               => $titre( 2.4, 2.1, 1.8 ),
		'h3_font'               => $titre( 1.6, 1.45, 1.3 ),
		'h4_font'               => $titre( 1.3, '', '' ),
		'h5_font'               => $titre( 1.1, '', '' ),
		'h6_font'               => $titre( 1, '', '' ),
		'load_fonts_local'      => false, // sans effet tant qu'aucune police n'a google = true

		// Boutons globaux (bouton principal).
		'buttons_color'         => array( 'color' => 'palette3', 'hover' => 'palette3' ),
		'buttons_background'    => array( 'color' => 'palette1', 'hover' => 'palette2' ),
		'buttons_border_radius' => array(
			'size' => array( 'mobile' => '', 'tablet' => '', 'desktop' => 2 ),
			'unit' => array( 'mobile' => 'px', 'tablet' => 'px', 'desktop' => 'px' ),
		),

		// Largeur du conteneur (72rem, comme .pd-wrap) et marge latérale.
		'content_width'         => array( 'size' => 72, 'unit' => 'rem' ),
		'content_edge_spacing'  => array(
			'size' => array( 'mobile' => '', 'tablet' => '', 'desktop' => 1.25 ),
			'unit' => array( 'mobile' => 'rem', 'tablet' => 'rem', 'desktop' => 'rem' ),
		),

		// Mise en page par défaut des pages : pleine largeur, sans boîte, sans marges ni titre.
		'page_layout'           => 'fullwidth',
		'page_content_style'    => 'unboxed',
		'page_vertical_padding' => 'hide',
		'page_title'            => false,

		// Bouton « remonter ».
		'scroll_up'             => true,
		'scroll_up_style'       => 'filled',
		'scroll_up_side'        => 'right',
		'scroll_up_icon'        => 'arrow-up',
		'scroll_up_color'       => array( 'color' => 'palette3', 'hover' => 'palette9' ),
		'scroll_up_background'  => array( 'color' => 'palette7', 'hover' => 'palette5' ),
		'scroll_up_radius'      => array( 'size' => array( 2, 2, 2, 2 ), 'unit' => 'px', 'locked' => true ),
	);
}

/**
 * Theme mods complétés avec les valeurs par défaut de Kadence : une sous-clé absente
 * d'une valeur enregistrée n'est PAS reprise du défaut par Kadence.
 *
 * @return array
 */
function pd_kadence_theme_mods_complets() {
	$defauts = class_exists( '\Kadence\Options\Component' ) ? \Kadence\Options\Component::defaults() : array();
	$mods    = array();
	foreach ( pd_kadence_theme_mods() as $cle => $valeur ) {
		if ( is_array( $valeur ) && isset( $defauts[ $cle ] ) && is_array( $defauts[ $cle ] ) ) {
			$valeur = array_replace_recursive( $defauts[ $cle ], $valeur );
		}
		$mods[ $cle ] = $valeur;
	}
	return $mods;
}

/**
 * Écrit la palette et les theme mods. À appeler quand le thème enfant est actif
 * (les theme mods sont rangés sous le nom du thème actif).
 */
function pd_kadence_appliquer_reglages() {
	update_option( 'kadence_global_palette', pd_kadence_palette_json() );
	foreach ( pd_kadence_theme_mods_complets() as $cle => $valeur ) {
		set_theme_mod( $cle, $valeur );
	}
	// En-tête et pied de page (inc/entete-pied.php).
	if ( function_exists( 'pd_kadence_appliquer_entete_pied' ) ) {
		pd_kadence_appliquer_entete_pied();
	}
	update_option( 'pd_kadence_reglages', PD_KADENCE_REGLAGES_VERSION );
}

// À l'activation du thème enfant (s'exécute au chargement qui suit l'activation, sur « init », priorité 99).
add_action( 'after_switch_theme', 'pd_kadence_appliquer_reglages' );

// Site déjà installé avec le thème actif : appliquer une fois par version de réglages.
add_action(
	'admin_init',
	function () {
		if ( PD_KADENCE_REGLAGES_VERSION !== get_option( 'pd_kadence_reglages' ) && current_user_can( 'edit_theme_options' ) ) {
			pd_kadence_appliquer_reglages();
		}
	}
);

// Polices : ne jamais appeler Google (thème et Kadence Blocks).
add_filter( 'kadence_print_google_fonts', '__return_false' );
add_filter( 'kadence_blocks_print_google_fonts', '__return_false' );
add_filter( 'kadence_blocks_print_footer_google_fonts', '__return_false' );

// Polices du thème enfant proposées dans les listes de polices (outil de personnalisation et blocs Kadence).
function pd_kadence_polices_perso( $polices ) {
	$polices['Hanken Grotesk'] = array(
		'fallback' => 'system-ui, -apple-system, "Segoe UI", sans-serif',
		'weights'  => array( '400', '500', '600' ),
	);
	$polices['Newsreader']     = array(
		'fallback' => 'Georgia, "Times New Roman", serif',
		'weights'  => array( '400', '500' ),
	);
	$polices['IBM Plex Mono']  = array(
		'fallback' => 'ui-monospace, Menlo, Consolas, monospace',
		'weights'  => array( '400', '500' ),
	);
	return $polices;
}
add_filter( 'kadence_theme_add_custom_fonts', 'pd_kadence_polices_perso' );
add_filter( 'kadence_blocks_add_custom_fonts', 'pd_kadence_polices_perso' );
