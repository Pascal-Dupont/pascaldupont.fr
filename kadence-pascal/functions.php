<?php
/**
 * Thème enfant de Kadence pour pascaldupont.fr
 *
 * - charge les styles et les polices du site (aucune requête vers Google) ;
 * - fournit le formulaire de contact [pd_formulaire], sans extension ;
 * - à la première visite de l'administration après l'import des pages, règle la
 *   page d'accueil, le titre du site et les menus.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'PD_VERSION', '1.0.0' );

/* ------------------------------------------------------------------ */
/* Styles, scripts et polices                                          */
/* ------------------------------------------------------------------ */

add_action(
	'wp_enqueue_scripts',
	function () {
		$dir = get_stylesheet_directory();
		$uri = get_stylesheet_directory_uri();
		foreach ( array( 'fonts', 'pd', 'pd-kadence' ) as $nom ) {
			$fichier = $dir . '/assets/' . $nom . '.css';
			wp_enqueue_style( 'pd-' . $nom, $uri . '/assets/' . $nom . '.css', array(), file_exists( $fichier ) ? filemtime( $fichier ) : PD_VERSION );
		}
		$js = $dir . '/assets/pd.js';
		wp_enqueue_script( 'pd-js', $uri . '/assets/pd.js', array(), file_exists( $js ) ? filemtime( $js ) : PD_VERSION, true );
	},
	30
);

add_filter(
	'body_class',
	function ( $classes ) {
		$classes[] = 'pd-site';
		return $classes;
	}
);

add_action(
	'wp_head',
	function () {
		$uri = get_stylesheet_directory_uri() . '/assets/fonts/';
		foreach ( array( 'Newsreader-normal-400-500.woff2', 'HankenGrotesk-normal-400-600.woff2' ) as $police ) {
			printf( '<link rel="preload" href="%s" as="font" type="font/woff2" crossorigin>' . "\n", esc_url( $uri . $police ) );
		}
	},
	1
);

/* ------------------------------------------------------------------ */
/* Formulaire de contact                                               */
/* ------------------------------------------------------------------ */

function pd_types_de_projet() {
	return array(
		'Documentaire ou film institutionnel',
		'Portrait filmé',
		'Captation d\'événement',
		'Stratégie et communication',
		'Montage et post-production',
		'Autre demande',
	);
}

function pd_jeton( $t ) {
	return hash_hmac( 'sha256', (string) $t, wp_salt( 'nonce' ) );
}

add_shortcode(
	'pd_formulaire',
	function () {
		$etat    = isset( $_GET['envoi'] ) ? sanitize_key( wp_unslash( $_GET['envoi'] ) ) : ''; // phpcs:ignore WordPress.Security.NonceVerification
		$messages = array(
			'ok'      => array( 'ok', 'Merci, votre message est bien parti. Je vous réponds personnellement.' ),
			'erreur'  => array( 'erreur', 'Le formulaire n\'a pas pu être envoyé. Vérifiez les champs et réessayez.' ),
			'attente' => array( 'erreur', 'Un message vient d\'être envoyé depuis votre connexion. Patientez une minute avant d\'en envoyer un autre.' ),
			'echec'   => array( 'erreur', 'Le message n\'a pas pu être remis. Écrivez-moi directement par e-mail.' ),
		);
		$t = time();

		ob_start();
		?>
		<form class="pd-formulaire" method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<input type="hidden" name="action" value="pd_contact">
			<input type="hidden" name="pd_t" value="<?php echo esc_attr( $t ); ?>">
			<input type="hidden" name="pd_s" value="<?php echo esc_attr( pd_jeton( $t ) ); ?>">
			<p class="pd-piege" aria-hidden="true"><label>Ne pas remplir<input type="text" name="pd_site" tabindex="-1" autocomplete="off"></label></p>
			<div class="pd-deux">
				<div class="pd-champ"><label for="pd-nom">Nom et prénom</label><input id="pd-nom" name="pd_nom" autocomplete="name" required maxlength="120"></div>
				<div class="pd-champ"><label for="pd-mail">Adresse e-mail</label><input id="pd-mail" name="pd_mail" type="email" autocomplete="email" required maxlength="160"></div>
			</div>
			<div class="pd-champ">
				<label for="pd-type">Type de projet</label>
				<select id="pd-type" name="pd_type">
					<?php foreach ( pd_types_de_projet() as $type ) : ?>
						<option><?php echo esc_html( $type ); ?></option>
					<?php endforeach; ?>
				</select>
			</div>
			<div class="pd-champ"><label for="pd-message">Votre message</label><textarea id="pd-message" name="pd_message" required minlength="10" maxlength="5000"></textarea></div>
			<p class="pd-consentement"><label><input type="checkbox" name="pd_consent" value="1" required> J'accepte que ces informations servent à répondre à ma demande (voir la <a href="<?php echo esc_url( home_url( '/confidentialite/' ) ); ?>">politique de confidentialité</a>).</label></p>
			<div class="pd-actions" style="margin:0"><button class="pd-bouton pd-plein" type="submit">Envoyer</button></div>
			<?php if ( isset( $messages[ $etat ] ) ) : ?>
				<p class="pd-retour pd-retour-<?php echo esc_attr( $messages[ $etat ][0] ); ?>" role="status"><?php echo esc_html( $messages[ $etat ][1] ); ?></p>
			<?php endif; ?>
		</form>
		<?php
		return ob_get_clean();
	}
);

function pd_redirige( $etat ) {
	wp_safe_redirect( add_query_arg( 'envoi', $etat, home_url( '/contact/' ) ) . '#formulaire' );
	exit;
}

function pd_traiter_contact() {
	if ( 'POST' !== ( $_SERVER['REQUEST_METHOD'] ?? '' ) ) { // phpcs:ignore WordPress.Security
		pd_redirige( 'erreur' );
	}

	// Piège à robots : un champ caché rempli, on fait comme si tout allait bien.
	if ( ! empty( $_POST['pd_site'] ) ) { // phpcs:ignore WordPress.Security.NonceVerification
		pd_redirige( 'ok' );
	}

	// Jeton signé avec l'heure d'affichage : ni trop rapide (robot), ni trop ancien.
	$t = isset( $_POST['pd_t'] ) ? (int) $_POST['pd_t'] : 0; // phpcs:ignore WordPress.Security.NonceVerification
	$s = isset( $_POST['pd_s'] ) ? (string) wp_unslash( $_POST['pd_s'] ) : ''; // phpcs:ignore WordPress.Security
	$age = time() - $t;
	if ( ! hash_equals( pd_jeton( $t ), $s ) || $age < 3 || $age > 7 * DAY_IN_SECONDS ) {
		pd_redirige( 'erreur' );
	}

	// Limite : un message par minute et par adresse IP.
	$ip  = isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : 'inconnue';
	$cle = 'pd_rl_' . md5( $ip );
	if ( get_transient( $cle ) ) {
		pd_redirige( 'attente' );
	}

	$nom     = isset( $_POST['pd_nom'] ) ? sanitize_text_field( wp_unslash( $_POST['pd_nom'] ) ) : ''; // phpcs:ignore WordPress.Security
	$mail    = isset( $_POST['pd_mail'] ) ? sanitize_email( wp_unslash( $_POST['pd_mail'] ) ) : ''; // phpcs:ignore WordPress.Security
	$type    = isset( $_POST['pd_type'] ) ? sanitize_text_field( wp_unslash( $_POST['pd_type'] ) ) : ''; // phpcs:ignore WordPress.Security
	$message = isset( $_POST['pd_message'] ) ? sanitize_textarea_field( wp_unslash( $_POST['pd_message'] ) ) : ''; // phpcs:ignore WordPress.Security
	$accord  = ! empty( $_POST['pd_consent'] ); // phpcs:ignore WordPress.Security.NonceVerification

	if ( strlen( $nom ) < 2 || ! is_email( $mail ) || strlen( $message ) < 10 || ! $accord || ! in_array( $type, pd_types_de_projet(), true ) ) {
		pd_redirige( 'erreur' );
	}

	set_transient( $cle, 1, MINUTE_IN_SECONDS );

	$destinataire = apply_filters( 'pd_destinataire', 'creationvideo@live.fr' );
	$nom_propre   = trim( str_replace( array( '<', '>', '"', ',', ';' ), '', $nom ) );
	$sujet        = '[pascaldupont.fr] ' . $type . ' : ' . $nom_propre;
	$corps        = "Nom : $nom_propre\nE-mail : $mail\nType de projet : $type\n\n$message\n";
	$entetes      = array( 'Content-Type: text/plain; charset=UTF-8', 'Reply-To: ' . $nom_propre . ' <' . $mail . '>' );

	pd_redirige( wp_mail( $destinataire, $sujet, $corps, $entetes ) ? 'ok' : 'echec' );
}
add_action( 'admin_post_nopriv_pd_contact', 'pd_traiter_contact' );
add_action( 'admin_post_pd_contact', 'pd_traiter_contact' );

/* ------------------------------------------------------------------ */
/* Réglages automatiques après l'import des pages                      */
/* ------------------------------------------------------------------ */

function pd_page_par_cle( $cle ) {
	$ids = get_posts(
		array(
			'post_type'   => 'page',
			'post_status' => 'publish',
			'meta_key'    => '_pd_page', // phpcs:ignore WordPress.DB.SlowDBQuery
			'meta_value'  => $cle, // phpcs:ignore WordPress.DB.SlowDBQuery
			'numberposts' => 1,
			'fields'      => 'ids',
		)
	);
	return $ids ? (int) $ids[0] : 0;
}

function pd_creer_menu( $nom, $elements ) {
	$menu = wp_get_nav_menu_object( $nom );
	if ( $menu ) {
		wp_delete_nav_menu( $menu->term_id );
	}
	$menu_id = wp_create_nav_menu( $nom );
	if ( is_wp_error( $menu_id ) ) {
		return 0;
	}
	foreach ( $elements as $element ) {
		if ( ! empty( $element['page'] ) ) {
			wp_update_nav_menu_item(
				$menu_id,
				0,
				array(
					'menu-item-title'     => $element['titre'],
					'menu-item-object'    => 'page',
					'menu-item-object-id' => $element['page'],
					'menu-item-type'      => 'post_type',
					'menu-item-status'    => 'publish',
				)
			);
		} else {
			wp_update_nav_menu_item(
				$menu_id,
				0,
				array(
					'menu-item-title'  => $element['titre'],
					'menu-item-url'    => $element['url'],
					'menu-item-type'   => 'custom',
					'menu-item-status' => 'publish',
				)
			);
		}
	}
	return (int) $menu_id;
}

add_action(
	'admin_init',
	function () {
		if ( '1' === get_option( 'pd_installe' ) || ! current_user_can( 'manage_options' ) ) {
			return;
		}
		$cles = array( 'accueil', 'films', 'serie-serval', 'a-propos', 'defense-et-securite', 'lakelab', 'contact', 'mentions-legales', 'confidentialite' );
		$p    = array();
		foreach ( $cles as $cle ) {
			$p[ $cle ] = pd_page_par_cle( $cle );
		}
		if ( ! $p['accueil'] || ! $p['films'] ) {
			return; // les pages ne sont pas encore importées
		}

		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $p['accueil'] );
		update_option( 'page_for_posts', 0 );
		update_option( 'blogname', 'Pascal Dupont' );
		update_option( 'blogdescription', 'Auteur-réalisateur documentaire' );
		if ( ! get_option( 'permalink_structure' ) ) {
			update_option( 'permalink_structure', '/%postname%/' );
		}

		$principal = pd_creer_menu(
			'Menu principal',
			array(
				array( 'titre' => 'Films', 'page' => $p['films'] ),
				array( 'titre' => 'Série Serval', 'page' => $p['serie-serval'] ),
				array( 'titre' => 'À propos', 'page' => $p['a-propos'] ),
				array( 'titre' => 'LAKELAB', 'page' => $p['lakelab'] ),
				array( 'titre' => 'Devis et contact', 'page' => $p['contact'] ),
			)
		);
		$pied = pd_creer_menu(
			'Pied de page',
			array(
				array( 'titre' => 'Défense et sécurité', 'page' => $p['defense-et-securite'] ),
				array( 'titre' => 'Mentions légales', 'page' => $p['mentions-legales'] ),
				array( 'titre' => 'Confidentialité', 'page' => $p['confidentialite'] ),
			)
		);
		$lieux = get_theme_mod( 'nav_menu_locations', array() );
		if ( $principal ) {
			$lieux['primary'] = $principal;
			$lieux['mobile']  = $principal;
		}
		if ( $pied ) {
			$lieux['footer'] = $pied;
		}
		set_theme_mod( 'nav_menu_locations', $lieux );

		flush_rewrite_rules( false );
		update_option( 'pd_installe', '1' );
		set_transient( 'pd_avis', 1, 5 * MINUTE_IN_SECONDS );
	}
);

add_action(
	'admin_notices',
	function () {
		if ( get_transient( 'pd_avis' ) ) {
			delete_transient( 'pd_avis' );
			echo '<div class="notice notice-success is-dismissible"><p><strong>Pascal Dupont :</strong> la page d\'accueil, le titre du site et les menus sont réglés. Il reste à vérifier le site.</p></div>';
		}
	}
);
