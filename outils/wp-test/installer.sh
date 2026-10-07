#!/usr/bin/env bash
# Installe un WordPress de test (SQLite) : installer.sh <source wordpress> <dossier cible> <port> [sans-theme]
set -euo pipefail
SRC="$1"; CIBLE="$2"; PORT="$3"; MODE="${4:-complet}"
ICI="$(cd "$(dirname "$0")" && pwd)"; DEPOT="$(cd "$ICI/../.." && pwd)"
rm -rf "$CIBLE"; cp -r "$SRC" "$CIBLE"
sed "s#{SQLITE_IMPLEMENTATION_FOLDER_PATH}#$CIBLE/wp-content/plugins/sqlite-database-integration#; s#{SQLITE_PLUGIN}#sqlite-database-integration/load.php#" \
  "$CIBLE/wp-content/plugins/sqlite-database-integration/db.copy" > "$CIBLE/wp-content/db.php"
cat > "$CIBLE/wp-config.php" <<PHP
<?php
define( 'DB_NAME', 'wp' ); define( 'DB_USER', 'wp' ); define( 'DB_PASSWORD', 'wp' ); define( 'DB_HOST', 'localhost' );
define( 'DB_CHARSET', 'utf8mb4' ); define( 'DB_COLLATE', '' );
define( 'WP_HOME', 'http://127.0.0.1:$PORT' ); define( 'WP_SITEURL', 'http://127.0.0.1:$PORT' );
define( 'AUTH_KEY', 'test1' ); define( 'SECURE_AUTH_KEY', 'test2' ); define( 'LOGGED_IN_KEY', 'test3' ); define( 'NONCE_KEY', 'test4' );
define( 'AUTH_SALT', 'test5' ); define( 'SECURE_AUTH_SALT', 'test6' ); define( 'LOGGED_IN_SALT', 'test7' ); define( 'NONCE_SALT', 'test8' );
define( 'WP_DEBUG', true ); define( 'WP_DEBUG_LOG', true ); define( 'WP_DEBUG_DISPLAY', false );
define( 'AUTOMATIC_UPDATER_DISABLED', true ); define( 'WP_AUTO_UPDATE_CORE', false ); define( 'DISALLOW_FILE_MODS', false );
\$table_prefix = 'wp_';
if ( ! defined( 'ABSPATH' ) ) { define( 'ABSPATH', __DIR__ . '/' ); }
require_once ABSPATH . 'wp-settings.php';
PHP
if [ "$MODE" = "complet" ]; then
  rm -rf "$CIBLE/wp-content/themes/kadence-pascal"; cp -r "$DEPOT/kadence-pascal" "$CIBLE/wp-content/themes/kadence-pascal"
fi
php "$ICI/preparer.php" "$CIBLE" "$PORT" "$MODE"
