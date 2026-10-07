<?php
/**
 * En-tête et pied de page Kadence 1.5.2 pour pascaldupont.fr (theme_mods du thème actif).
 *
 * - En-tête bureau sur une ligne : titre du site à gauche, menu principal à droite.
 * - En-tête collant (bureau et mobile), fond #0d1217 à 92 %, bordure basse 1px #2c3a49.
 * - Mobile : titre à gauche, bouton menu à droite, tiroir latéral sombre.
 * - Pied de page sur une rangée : copyright à gauche, menu du pied à droite.
 *
 * Kadence ne fusionne PAS une valeur enregistrée avec sa valeur par défaut : chaque tableau
 * ci-dessous est donc complet (toutes les sous-clés), sinon les sous-clés absentes sont perdues.
 * Les menus (emplacements primary, mobile, footer) sont réglés ailleurs (functions.php du thème enfant).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Valeurs des theme_mods, clé => valeur, prêtes pour set_theme_mod().
 *
 * @return array
 */
function pd_kadence_entete_pied_mods() {
	$nuit      = '#0d1217';
	$ardoise   = '#17202a';
	$ligne     = '#2c3a49';
	$texte     = '#e8e6e1';
	$doux      = '#a9b6c0';
	$sable     = '#c8b287';
	$beret_vif = '#c0403d';

	$px3  = array( 'mobile' => 'px', 'tablet' => 'px', 'desktop' => 'px' );
	$fond = function ( $couleur ) {
		return array( 'desktop' => array( 'color' => $couleur ) );
	};
	$trait = function ( $couleur ) {
		return array( 'desktop' => array( 'width' => 1, 'unit' => 'px', 'style' => 'solid', 'color' => $couleur ) );
	};
	$police = function ( $taille, $unite, $graisse = '', $couleur = '' ) {
		$p = array(
			'size'       => array( 'desktop' => $taille ),
			'sizeType'   => $unite,
			'lineHeight' => array( 'desktop' => '' ),
			'family'     => 'inherit',
			'google'     => false,
			'weight'     => $graisse,
			'variant'    => '',
		);
		if ( '' !== $couleur ) {
			$p['color'] = $couleur;
		}
		return $p;
	};

	return array(
		/* ---------- En-tête : structure ---------- */
		'header_desktop_items'           => array(
			'top'    => array( 'top_left' => array(), 'top_left_center' => array(), 'top_center' => array(), 'top_right_center' => array(), 'top_right' => array() ),
			'main'   => array( 'main_left' => array( 'logo' ), 'main_left_center' => array(), 'main_center' => array(), 'main_right_center' => array(), 'main_right' => array( 'navigation' ) ),
			'bottom' => array( 'bottom_left' => array(), 'bottom_left_center' => array(), 'bottom_center' => array(), 'bottom_right_center' => array(), 'bottom_right' => array() ),
		),
		'header_mobile_items'            => array(
			'popup'  => array( 'popup_content' => array( 'mobile-navigation' ) ),
			'top'    => array( 'top_left' => array(), 'top_center' => array(), 'top_right' => array() ),
			'main'   => array( 'main_left' => array( 'mobile-logo' ), 'main_center' => array(), 'main_right' => array( 'popup-toggle' ) ),
			'bottom' => array( 'bottom_left' => array(), 'bottom_center' => array(), 'bottom_right' => array() ),
		),
		'header_main_layout'             => array( 'mobile' => '', 'tablet' => '', 'desktop' => 'standard' ),
		'header_main_height'             => array( 'size' => array( 'mobile' => 64, 'tablet' => '', 'desktop' => 76 ), 'unit' => $px3 ),

		/* ---------- En-tête : fond et bordure ---------- */
		// #masthead est BLANC par défaut (#ffffff) : sous la rangée à 92 % il donnerait un gris clair.
		// Sa règle s'applique aussi à la rangée une fois collée, d'où header_sticky_background plus bas.
		'header_wrap_background'         => $fond( $nuit ),
		'header_main_background'         => $fond( 'rgba(13,18,23,0.92)' ),
		'header_main_bottom_border'      => $trait( $ligne ),

		/* ---------- En-tête collant ---------- */
		'header_sticky'                  => 'main',
		'mobile_header_sticky'           => 'main',
		'header_sticky_shrink'           => false,
		'header_reveal_scroll_up'        => false,
		// Obligatoire avec un en-tête collant : sinon la rangée collée prend header_wrap_background (opaque).
		'header_sticky_background'       => $fond( 'rgba(13,18,23,0.92)' ),

		/* ---------- Titre du site (pas de logo image) ---------- */
		// Tablette et mobile explicites : avec 'tablet' => '', Kadence ajoute .vs-md-false au titre
		// de l'en-tête mobile, qui est alors MASQUÉ entre 720 et 1024 px.
		'logo_layout'                    => array(
			'include' => array( 'mobile' => 'logo_title', 'tablet' => 'logo_title', 'desktop' => 'logo_title' ),
			'layout'  => array( 'mobile' => '', 'tablet' => '', 'desktop' => 'standard' ),
		),
		'brand_typography'               => array(
			'size'          => array( 'desktop' => 1.35, 'tablet' => '', 'mobile' => 1.2 ),
			'sizeType'      => 'rem',
			'lineHeight'    => array( 'desktop' => 1.2 ),
			'letterSpacing' => array( 'desktop' => 0.01 ),
			'spacingType'   => 'em',
			'family'        => '"Newsreader", Georgia, "Times New Roman", serif',
			'google'        => false,
			'weight'        => '400',
			'variant'       => '',
			'color'         => $texte,
		),
		'brand_typography_color'         => array( 'hover' => $texte, 'active' => $texte ),

		/* ---------- Menu principal (bureau) ---------- */
		'primary_navigation_style'       => 'standard',
		'primary_navigation_spacing'     => array( 'size' => 1.4, 'unit' => 'em' ),
		'primary_navigation_vertical_spacing' => array( 'size' => 0.6, 'unit' => 'em' ),
		'primary_navigation_color'       => array( 'color' => $doux, 'hover' => $texte, 'active' => $texte ),
		'primary_navigation_background'  => array( 'color' => '', 'hover' => '', 'active' => '' ),
		'primary_navigation_typography'  => $police( 0.95, 'rem', '400' ),

		/* ---------- Mobile : bouton et tiroir ---------- */
		'mobile_trigger_icon'            => 'menu',
		'mobile_trigger_style'           => 'default',
		'mobile_trigger_label'           => '',
		'mobile_trigger_icon_size'       => array( 'size' => 24, 'unit' => 'px' ),
		'mobile_trigger_color'           => array( 'color' => $texte, 'hover' => $beret_vif ),
		'mobile_trigger_background'      => array( 'color' => '', 'hover' => '' ),
		'header_popup_layout'            => 'sidepanel',
		'header_popup_side'              => 'right',
		'header_popup_animation'         => 'fade',
		'header_popup_background'        => $fond( $ardoise ),
		'header_popup_close_color'       => array( 'color' => $texte, 'hover' => $beret_vif ),
		'mobile_navigation_color'        => array( 'color' => $texte, 'hover' => $sable, 'active' => $beret_vif ),
		'mobile_navigation_background'   => array( 'color' => '', 'hover' => '', 'active' => '' ),
		'mobile_navigation_divider'      => array( 'width' => 1, 'unit' => 'px', 'style' => 'solid', 'color' => $ligne ),
		'mobile_navigation_typography'   => $police( 17, 'px' ),
		'mobile_navigation_vertical_spacing' => array( 'size' => 0.9, 'unit' => 'em' ),

		/* ---------- Pied de page : une rangée (bas), deux colonnes ---------- */
		'footer_items'                   => array(
			'top'    => array( 'top_1' => array(), 'top_2' => array(), 'top_3' => array(), 'top_4' => array(), 'top_5' => array() ),
			'middle' => array( 'middle_1' => array(), 'middle_2' => array(), 'middle_3' => array(), 'middle_4' => array(), 'middle_5' => array() ),
			'bottom' => array( 'bottom_1' => array( 'footer-html' ), 'bottom_2' => array( 'footer-navigation' ), 'bottom_3' => array(), 'bottom_4' => array(), 'bottom_5' => array() ),
		),
		'footer_bottom_columns'          => '2',
		// Tablette : '' empilerait les deux colonnes entre 720 et 1024 px (classe …-tablet-column-layout-default).
		'footer_bottom_layout'           => array( 'mobile' => 'row', 'tablet' => 'equal', 'desktop' => 'equal' ),
		'footer_bottom_contain'          => array( 'mobile' => '', 'tablet' => '', 'desktop' => 'standard' ),
		'footer_bottom_top_spacing'      => array( 'size' => array( 'mobile' => '', 'tablet' => '', 'desktop' => 24 ), 'unit' => $px3 ),
		'footer_bottom_bottom_spacing'   => array( 'size' => array( 'mobile' => '', 'tablet' => '', 'desktop' => 24 ), 'unit' => $px3 ),
		'footer_bottom_column_spacing'   => array( 'size' => array( 'mobile' => 8, 'tablet' => '', 'desktop' => 30 ), 'unit' => $px3 ),
		'footer_wrap_background'         => $fond( $nuit ),
		'footer_bottom_background'       => $fond( $nuit ),
		'footer_bottom_top_border'       => $trait( $ligne ),
		'footer_bottom_widget_content'   => $police( 14, 'px', '', $doux ),
		'footer_bottom_link_colors'      => array( 'color' => $doux, 'hover' => $texte ),

		/* ---------- Copyright (élément « footer-html ») ---------- */
		'footer_html_content'            => '{copyright} {year} {site-title}',
		'footer_html_align'              => array( 'mobile' => 'center', 'tablet' => '', 'desktop' => 'left' ),
		'footer_html_vertical_align'     => array( 'mobile' => '', 'tablet' => '', 'desktop' => 'middle' ),
		'footer_html_typography'         => $police( 14, 'px', '', $doux ),
		'footer_html_link_style'         => 'plain',

		/* ---------- Menu du pied (élément « footer-navigation », emplacement « footer ») ---------- */
		'footer_navigation_align'        => array( 'mobile' => 'center', 'tablet' => '', 'desktop' => 'right' ),
		'footer_navigation_vertical_align' => array( 'mobile' => '', 'tablet' => '', 'desktop' => 'middle' ),
		'footer_navigation_spacing'      => array( 'size' => 1.2, 'unit' => 'em' ),
		'footer_navigation_vertical_spacing' => array( 'size' => 0.6, 'unit' => 'em' ),
		'footer_navigation_color'        => array( 'color' => $doux, 'hover' => $texte, 'active' => $texte ),
		'footer_navigation_background'   => array( 'color' => '', 'hover' => '', 'active' => '' ),
		'footer_navigation_typography'   => $police( 14, 'px' ),
	);
}

/**
 * Écrit les theme_mods de l'en-tête et du pied dans le thème actif.
 * Les autres theme_mods (menus, palette, typographie générale…) ne sont pas touchés.
 */
function pd_kadence_appliquer_entete_pied() {
	foreach ( pd_kadence_entete_pied_mods() as $cle => $valeur ) {
		set_theme_mod( $cle, $valeur );
	}
}

/*
 * Exemple d'appel unique (à mettre dans functions.php du thème enfant, une fois validé) :
 *
 * add_action( 'admin_init', function () {
 *     if ( '1' !== get_option( 'pd_entete_pied_version' ) && current_user_can( 'manage_options' ) ) {
 *         pd_kadence_appliquer_entete_pied();
 *         update_option( 'pd_entete_pied_version', '1' );
 *     }
 * } );
 */
