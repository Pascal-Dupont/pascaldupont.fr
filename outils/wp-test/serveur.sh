#!/usr/bin/env bash
# Démarre (ou redémarre) le serveur PHP d'un WordPress de test : serveur.sh <dossier wp> <port>
CIBLE="$1"; PORT="$2"; ICI="$(cd "$(dirname "$0")" && pwd)"
for pid in $(pgrep -f "^php .*-S 127.0.0.1:$PORT "); do kill "$pid"; done
sleep 1
cd "$CIBLE" && PHP_CLI_SERVER_WORKERS=8 nohup php -d memory_limit=512M -d upload_max_filesize=64M -d post_max_size=64M \
  -S 127.0.0.1:$PORT -t "$CIBLE" "$ICI/router.php" > "$CIBLE/../serveur-$PORT.log" 2>&1 &
sleep 2
curl -sS -o /dev/null -w "serveur $PORT : %{http_code}\n" "http://127.0.0.1:$PORT/wp-login.php"
