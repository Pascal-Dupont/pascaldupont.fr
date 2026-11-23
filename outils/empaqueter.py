#!/usr/bin/env python3
"""
Prépare les deux fichiers à installer sur le vrai site :
  - dist/kadence-pascal.zip : le thème enfant ;
  - dist/pages-pascaldupont.xml : les pages, exportées du WordPress de test où elles ont été construites et vérifiées.
Usage : python3 outils/empaqueter.py <dossier du wordpress de test> <port>
"""
import json
import pathlib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

RACINE = pathlib.Path(__file__).resolve().parent.parent
THEME = RACINE / 'kadence-pascal'
DIST = RACINE / 'dist'
NS = {'wp': 'http://wordpress.org/export/1.2/', 'content': 'http://purl.org/rss/1.0/modules/content/',
      'excerpt': 'http://wordpress.org/export/1.2/excerpt/'}


def zipper():
    DIST.mkdir(exist_ok=True)
    destination = DIST / 'kadence-pascal.zip'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as z:
        for chemin in sorted(THEME.rglob('*')):
            if chemin.is_file():
                info = zipfile.ZipInfo('kadence-pascal/' + chemin.relative_to(THEME).as_posix(), date_time=(2026, 10, 7, 12, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, chemin.read_bytes())
    print('thème :', destination)


def exporter(wp, port):
    sortie = DIST / 'pages-pascaldupont.xml'
    subprocess.run(['php', str(RACINE / 'outils' / 'wp-test' / 'exporter.php'), wp, port, str(sortie)], check=True)
    # ne garder que les pages du site (repère _pd_page) : retire la page d'exemple et les essais
    xml = sortie.read_text(encoding='utf-8')
    morceaux = re.split(r'(?=\t<item>)', xml)
    garde = [m for m in morceaux if not m.startswith('\t<item>') or '_pd_page' in m]
    if garde[-1].startswith('\t<item>') and '</channel>' not in garde[-1]:
        garde.append('\n</channel>\n</rss>\n')
    # le dernier élément contient la fin du document : la recoller si on l'a retiré
    if '</channel>' not in ''.join(garde):
        fin = xml[xml.rindex('</item>') + len('</item>'):]
        garde.append(fin)
    xml2 = ''.join(garde)
    # Adresse d'origine vide : l'importeur WordPress ne tente alors aucune « réécriture des URL »
    # (case cochée par défaut), qui transformerait les liens d'onglets #films-… en /#films-… et
    # rendrait le bloc d'onglets invalide dans l'éditeur. Nos liens internes sont tous relatifs (/films/).
    xml2 = re.sub(r'<wp:base_site_url>.*?</wp:base_site_url>', '<wp:base_site_url></wp:base_site_url>', xml2)
    xml2 = re.sub(r'<wp:base_blog_url>.*?</wp:base_blog_url>', '<wp:base_blog_url></wp:base_blog_url>', xml2)
    sortie.write_text(xml2, encoding='utf-8')
    print('pages gardées :', xml2.count('<item>'))


def generer_contenu_pages():
    """Extrait de l'export WXR, déjà construit et vérifié dans le vrai éditeur, le contenu de
    chaque page (titre, extrait, contenu, méta) et l'écrit en JSON dans le thème. Le thème s'en
    sert pour créer ou mettre à jour ses pages lui-même, à chaque activation : plus besoin de
    passer par Outils > Importer pour une mise à jour de contenu."""
    source = DIST / 'pages-pascaldupont.xml'
    racine = ET.fromstring(source.read_text(encoding='utf-8'))
    pages = []
    for item in racine.find('channel').findall('item'):
        metas = {m.find('wp:meta_key', NS).text: (m.find('wp:meta_value', NS).text or '')
                 for m in item.findall('wp:postmeta', NS)}
        cle = metas.get('_pd_page')
        if not cle:
            continue
        titre = (item.findtext('title') or '').strip()
        slug = (item.findtext('wp:post_name', namespaces=NS) or cle).strip()
        contenu = item.findtext('content:encoded', namespaces=NS) or ''
        extrait = item.findtext('excerpt:encoded', namespaces=NS) or ''
        pages.append({'cle': cle, 'slug': slug, 'titre': titre, 'excerpt': extrait, 'content': contenu, 'meta': metas})
    pages.sort(key=lambda p: p['cle'])
    destination = THEME / 'inc' / 'contenu-pages.json'
    destination.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding='utf-8')
    print('contenu des pages :', destination, '(%d pages)' % len(pages))


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        exporter(sys.argv[1], sys.argv[2])
        generer_contenu_pages()
    zipper()
