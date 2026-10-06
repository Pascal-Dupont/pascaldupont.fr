#!/usr/bin/env python3
"""
Construit à partir de maquette/index.html :
  - kadence-pascal/assets/pd.css   (styles des pages)
  - import/pages.xml               (pages à importer dans WordPress)
  - dist/kadence-pascal.zip        (thème enfant à envoyer sur WordPress)

La maquette reste la source : on la modifie, on relance ce script, on réimporte.
Usage : python3 outils/construire.py
"""
import datetime
import html as H
import json
import pathlib
import re
import subprocess
import zipfile

RACINE = pathlib.Path(__file__).resolve().parent.parent
MAQUETTE = (RACINE / 'maquette' / 'index.html').read_text(encoding='utf-8')
THEME = RACINE / 'kadence-pascal'
YT = 'https://www.youtube.com/watch?v='

# ---------------------------------------------------------------- CSS

def decouper(css):
    """Liste de (sélecteur, corps) au premier niveau."""
    blocs, i, n = [], 0, len(css)
    while i < n:
        j = css.find('{', i)
        if j < 0:
            break
        selecteur = css[i:j].strip()
        profondeur, k = 1, j + 1
        while k < n and profondeur:
            if css[k] == '{':
                profondeur += 1
            elif css[k] == '}':
                profondeur -= 1
            k += 1
        blocs.append((selecteur, css[j + 1:k - 1]))
        i = k
    return blocs


IGNORES = ('.note', '.entete', '.marque', '.menu', 'footer')


def portee(partie):
    partie = partie.strip()
    if partie == ':root':
        return partie
    if partie == 'html':
        return partie
    if partie == 'body':
        return 'body.pd-site'
    partie = re.sub(r'\.([a-zA-Z][\w-]*)', lambda m: '.pd-' + m.group(1), partie)
    return '.pd-page ' + partie


def transformer(css):
    sortie = []
    for selecteur, corps in decouper(css):
        if selecteur.startswith('@media'):
            interieur = transformer(corps)
            if interieur.strip():
                sortie.append('%s {\n%s}\n' % (selecteur, interieur))
            continue
        parties = [p.strip() for p in selecteur.split(',')]
        if any(p.startswith(IGNORES) for p in parties):
            continue
        sortie.append('%s {%s}\n' % (', '.join(portee(p) for p in parties), corps.rstrip() + ' ' if corps.strip() else ''))
    return ''.join(sortie)


def construire_css():
    css = re.search(r'<style>(.*?)</style>', MAQUETTE, re.S).group(1)
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    entete = '/* Généré depuis maquette/index.html par outils/construire.py : ne pas modifier à la main. */\n'
    (THEME / 'assets' / 'pd.css').write_text(entete + transformer(css), encoding='utf-8')

# ---------------------------------------------------------------- données

def donnees():
    js = re.search(r'<script>(.*)</script>', MAQUETTE, re.S).group(1)
    segment = js[js.index('var GROUPES'):js.index('/* ---- fabrique')]
    script = 'var YT=%s;%s;console.log(JSON.stringify({GROUPES:GROUPES,UNE:UNE,SERVAL:SERVAL,HOMMAGES:HOMMAGES}))' % (json.dumps(YT), segment)
    sortie = subprocess.run(['node', '-e', script], capture_output=True, text=True, check=True).stdout
    return json.loads(sortie)


D = donnees()
LIENS = {
    '#accueil': '/', '#films': '/films/', '#serval': '/serie-serval/', '#apropos': '/a-propos/',
    '#defense': '/defense-et-securite/', '#contact': '/contact/', '#prestations': '/#prestations',
    '#lakelab': '/lakelab/',
}


def degrade(identifiant):
    s = sum(ord(c) for c in identifiant)
    t = 190 + (s % 70)
    return 'linear-gradient(160deg,hsl(%d 22%% 34%%),hsl(%d 26%% 10%%))' % (t, t)


def e(texte):
    return H.escape(texte, quote=True)


def carte(identifiant, titre, sous='', duree='', type_='', liens=None, href=None, date=None, cat=''):
    inerte = liens is not None and len(liens) == 0
    if liens:
        url = liens[0][1]
    else:
        url = href or (YT + identifiant)
    url = LIENS.get(url, url)
    externe = not url.startswith('/')
    attrs = ' target="_blank" rel="noopener"' if externe else ''
    vignette = ''
    if re.fullmatch(r'[\w-]{11}', identifiant) and not liens and not href:
        vignette = '<img class="vignette" src="https://i.ytimg.com/vi/%s/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">' % identifiant
    interieur = vignette
    if type_:
        interieur += '<span class="type">%s</span>' % e(type_)
    if not inerte:
        interieur += '<span class="lecture"></span>'
    if duree:
        interieur += '<span class="duree">%s</span>' % e(duree)
    if inerte:
        cadre = '<div class="cadre" style="--g:%s">%s</div>' % (degrade(identifiant), interieur)
    else:
        cadre = '<a class="cadre" href="%s"%s style="--g:%s" aria-label="Lire : %s">%s</a>' % (url, attrs, degrade(identifiant), e(titre), interieur)
    voir = ''
    if liens:
        voir = '<p class="voir">Voir sur : %s</p>' % ' · '.join(
            '<a href="%s" target="_blank" rel="noopener">%s</a>' % (l[1], e(l[0])) for l in liens)
    return '<article class="film" data-cat="%s">%s%s<h3>%s</h3>%s%s</article>' % (
        cat, cadre, ('<span class="date">%s</span>' % e(date)) if date else '', e(titre),
        ('<p>%s</p>' % e(sous)) if sous else '', voir)


def trouver(identifiant):
    for g in D['GROUPES']:
        for f in g['films'] if isinstance(g, dict) else g[4]:
            if f[0] == identifiant:
                return f
    return None


def carte_depuis(f, cat=''):
    return carte(f[0], f[1], f[2], f[3], f[5] if len(f) > 5 else '', f[4] if len(f) > 4 else None, cat=cat)


def cartes_groupe(g):
    return ''.join(carte_depuis(f, g['cle']) for f in g['films'])


def groupes_films():
    sortie = []
    for g in D['GROUPES']:
        liens = list(g.get('liens', []))
        if g.get('pageServal'):
            liens.insert(0, ['Voir toute la série Serval', '#serval'])
        boutons = ''
        if liens:
            boutons = '<div class="liens-ext">%s</div>' % ''.join(
                '<a class="bouton contour" href="%s"%s>%s</a>' % (
                    LIENS.get(l[1], l[1]), '' if l[1].startswith('#') else ' target="_blank" rel="noopener"', e(l[0]))
                for l in liens)
        sortie.append('<div class="groupe" data-groupe="%s"><h2>%s</h2><p>%s</p><div class="films">%s</div>%s</div>' % (
            g['cle'], e(g['titre']), e(g['texte']), cartes_groupe(g), boutons))
    return ''.join(sortie)


def filtres():
    boutons = '<button class="filtre" type="button" data-cat="tous" aria-pressed="true">Tous</button>'
    for g in D['GROUPES']:
        boutons += '<button class="filtre" type="button" data-cat="%s" aria-pressed="false">%s</button>' % (g['cle'], e(g['titre']))
    return boutons


# ---------------------------------------------------------------- pages

def principal(vue):
    return re.search(r'<main id="vue-%s"[^>]*>(.*?)</main>' % vue, MAQUETTE, re.S).group(1)


def nettoyer(h):
    h = re.sub(r'<div class="dev">.*?</div>', '', h, flags=re.S)
    h = re.sub(r'<!--.*?-->', '', h, flags=re.S)
    for ancre, url in LIENS.items():
        h = h.replace('href="%s"' % ancre, 'href="%s"' % url)
    return h


def prefixer(h):
    def classes(m):
        return 'class="%s"' % ' '.join(t if t.startswith('pd-') else 'pd-' + t for t in m.group(1).split())
    return re.sub(r'class="([^"]*)"', classes, h)


def vers_bloc(h):
    h = re.sub(r'\n\s*\n+', '\n', h.strip())
    return '<!-- wp:html -->\n<div class="pd-page">\n%s\n</div>\n<!-- /wp:html -->' % h


def remplir(h, identifiant, contenu):
    motif = re.compile(r'(<div[^>]*id="%s"[^>]*>)(</div>)' % re.escape(identifiant))
    assert motif.search(h), identifiant
    return motif.sub(lambda m: m.group(1) + contenu + m.group(2), h)


def page_accueil():
    h = principal('accueil')
    h = re.sub(r'<section id="contact" class="contact">.*?</section>', '''<section>
    <div class="wrap">
      <div class="titre-section">
        <span class="etiquette">Contact</span>
        <h2>Parlons de votre projet</h2>
        <p>Un film, un portrait, une captation ? Décrivez-moi votre idée, je vous réponds personnellement.</p>
      </div>
      <div class="actions"><a class="bouton plein" href="#contact">Demander un devis</a></div>
    </div>
  </section>''', h, flags=re.S)
    une = ''
    for f in D['UNE']:
        une += carte(f[0], f[1], f[2], f[3], f[4], href=(f[5] if len(f) > 5 else ('#serval' if f[0] == 'SERVAL' else None)))
    h = remplir(h, 'grille-une', une)
    return vers_bloc(prefixer(nettoyer(h)))


def page_films():
    h = principal('films')
    h = remplir(h, 'filtres-films', filtres())
    h = remplir(h, 'groupes-films', groupes_films())
    return vers_bloc(prefixer(nettoyer(h)))


def page_serval():
    h = principal('serval')
    h = remplir(h, 'grille-serval', ''.join(carte(f[0], f[2], '', f[3], '', date=f[1]) for f in D['SERVAL']))
    h = remplir(h, 'grille-hommages', ''.join(carte(f[0], f[2], '', f[3], '', date=f[1]) for f in D['HOMMAGES']))
    return vers_bloc(prefixer(nettoyer(h)))


def page_apropos():
    return vers_bloc(prefixer(nettoyer(principal('apropos'))))


def page_defense():
    h = principal('defense')
    cartes = ''.join(carte_depuis(trouver(i)) for i in ['RCP3', 'RCP1', 'RCP9', 'bhsuc7c241k', 'A1yfSvxryKg'])
    cartes += carte('SERVAL', 'Opération Serval', 'Mali 2013 · plus de 2 millions de vues', '', 'Série', href='#serval')
    h = remplir(h, 'grille-defense', cartes)
    return vers_bloc(prefixer(nettoyer(h)))


def section_contact():
    h = principal('accueil')
    return re.search(r'<section id="contact" class="contact">.*?</section>', h, re.S).group(0)


def page_contact():
    s = section_contact()
    s = re.sub(r'<form id="formulaire".*?</form>', '<div id="formulaire">[pd_formulaire]</div>', s, flags=re.S)
    return vers_bloc(prefixer(nettoyer(s)))


def page_lakelab():
    h = principal('accueil')
    s = re.search(r'<section id="lakelab" class="lakelab">.*?</section>', h, re.S).group(0)
    s = s.replace('<h2>LAKELAB</h2>', '<h2>Où nous suivre</h2>')
    titre = '''<div class="page-titre">
    <div class="wrap">
      <span class="etiquette">Recherches esthétiques</span>
      <h1>LAKELAB</h1>
      <p>LAKELAB est la contraction de « FabLab » et de « lac » : un laboratoire d'expérimentation au bord de l'eau. Lucile et moi y menons nos recherches en photographie, cinéma, musique et culture en général.</p>
    </div>
  </div>'''
    return vers_bloc(prefixer(nettoyer(titre + s)))


def page_legale(titre, etiquette, corps):
    h = '''<div class="page-titre"><div class="wrap"><span class="etiquette">%s</span><h1>%s</h1></div></div>
  <section><div class="wrap texte-legal">%s</div></section>''' % (etiquette, titre, corps)
    return vers_bloc(prefixer(h))


MENTIONS = '''
<h2>Éditeur du site</h2>
<p>Pascal Dupont, auteur-réalisateur.<br>Statut et numéro SIRET : <mark>à compléter</mark><br>Adresse : <mark>à compléter</mark><br>Téléphone : 06 86 31 15 96<br>E-mail : creationvideo@live.fr<br>Directeur de la publication : Pascal Dupont.</p>
<h2>Hébergeur</h2>
<p>OVH SAS, 2 rue Kellermann, 59100 Roubaix, France.</p>
<h2>Propriété intellectuelle</h2>
<p>Les textes, films et photographies de ce site sont la propriété de Pascal Dupont, sauf mention contraire. Les images de l'opération Serval proviennent de l'EMA et sont diffusées par l'ECPAD, sans utilisation commerciale. Toute reproduction sans accord est interdite.</p>
<h2>Liens et contenus tiers</h2>
<p>Les films sont hébergés sur YouTube, Instagram, Facebook et X. Ces services sont responsables de leurs propres contenus et de leurs conditions d'utilisation.</p>
<h2>Crédits</h2>
<p>Thème Kadence. Polices Newsreader, Hanken Grotesk et IBM Plex Mono, sous licence SIL OFL.</p>
'''

CONFIDENTIALITE = '''
<p><mark>Texte à faire relire avant la mise en ligne.</mark></p>
<h2>Responsable du traitement</h2>
<p>Pascal Dupont, joignable à l'adresse creationvideo@live.fr.</p>
<h2>Données collectées</h2>
<p>Le formulaire de contact recueille votre nom, votre adresse e-mail, le type de projet et votre message. Elles servent uniquement à répondre à votre demande. Elles ne sont ni vendues ni transmises à des tiers.</p>
<h2>Conservation</h2>
<p>Les messages sont conservés trois ans après le dernier échange, puis supprimés.</p>
<h2>Cookies et services tiers</h2>
<p>Ce site n'utilise ni statistiques ni publicité, et ne dépose pas de cookie de suivi. Les vignettes des films sont chargées depuis les serveurs de YouTube (Google) : votre adresse IP leur est alors transmise. Les liens vers YouTube, Instagram, Facebook et X ouvrent ces services, qui appliquent leurs propres règles.</p>
<h2>Vos droits</h2>
<p>Vous pouvez demander l'accès à vos données, leur rectification, leur effacement ou vous opposer à leur traitement, en écrivant à creationvideo@live.fr. En cas de difficulté, vous pouvez saisir la CNIL (cnil.fr).</p>
<h2>Hébergement</h2>
<p>Le site est hébergé par OVH SAS, 2 rue Kellermann, 59100 Roubaix, France.</p>
'''

PAGES = [
    # clé, titre, fonction, ordre
    ('accueil', 'Accueil', page_accueil),
    ('films', 'Films', page_films),
    ('serie-serval', 'Série Serval', page_serval),
    ('a-propos', 'À propos', page_apropos),
    ('defense-et-securite', 'Défense et sécurité', page_defense),
    ('lakelab', 'LAKELAB', page_lakelab),
    ('contact', 'Devis et contact', page_contact),
    ('mentions-legales', 'Mentions légales', lambda: page_legale('Mentions légales', 'Informations légales', MENTIONS)),
    ('confidentialite', 'Politique de confidentialité', lambda: page_legale('Politique de confidentialité', 'Vos données', CONFIDENTIALITE)),
]


def cdata(texte):
    return '<![CDATA[%s]]>' % texte.replace(']]>', ']]]]><![CDATA[>')


def meta(cle, valeur):
    return '<wp:postmeta><wp:meta_key>%s</wp:meta_key><wp:meta_value>%s</wp:meta_value></wp:postmeta>' % (cle, cdata(valeur))


def construire_wxr():
    maintenant = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    items = []
    for ordre, (cle, titre, fabrique) in enumerate(PAGES, start=1):
        identifiant = 9000 + ordre
        contenu = fabrique()
        items.append('''<item>
<title>%s</title>
<link>https://pascaldupont.fr/%s/</link>
<dc:creator>%s</dc:creator>
<guid isPermaLink="false">https://pascaldupont.fr/?page_id=%d</guid>
<description></description>
<content:encoded>%s</content:encoded>
<excerpt:encoded>%s</excerpt:encoded>
<wp:post_id>%d</wp:post_id>
<wp:post_date>%s</wp:post_date>
<wp:post_date_gmt>%s</wp:post_date_gmt>
<wp:post_modified>%s</wp:post_modified>
<wp:post_modified_gmt>%s</wp:post_modified_gmt>
<wp:comment_status>closed</wp:comment_status>
<wp:ping_status>closed</wp:ping_status>
<wp:post_name>%s</wp:post_name>
<wp:status>publish</wp:status>
<wp:post_parent>0</wp:post_parent>
<wp:menu_order>%d</wp:menu_order>
<wp:post_type>page</wp:post_type>
<wp:post_password></wp:post_password>
<wp:is_sticky>0</wp:is_sticky>
%s
</item>''' % (
            e(titre), cle, cdata('admin'), identifiant, cdata(contenu), cdata(''), identifiant,
            maintenant, maintenant, maintenant, maintenant, cle, ordre,
            '\n'.join([
                meta('_pd_page', cle),
                meta('_kad_post_layout', 'fullwidth'),
                meta('_kad_post_content_style', 'unboxed'),
                meta('_kad_post_vertical_padding', 'hide'),
                meta('_kad_post_title', 'hide'),
                meta('_kad_post_feature', 'hide'),
            ])))
    xml = '''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0"
 xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
 xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:wfw="http://wellformedweb.org/CommentAPI/"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
<title>Pascal Dupont</title>
<link>https://pascaldupont.fr</link>
<description>Auteur-réalisateur documentaire</description>
<language>fr-FR</language>
<wp:wxr_version>1.2</wp:wxr_version>
<wp:base_site_url>https://pascaldupont.fr</wp:base_site_url>
<wp:base_blog_url>https://pascaldupont.fr</wp:base_blog_url>
<wp:author><wp:author_id>1</wp:author_id><wp:author_login>admin</wp:author_login><wp:author_email></wp:author_email><wp:author_display_name>admin</wp:author_display_name><wp:author_first_name></wp:author_first_name><wp:author_last_name></wp:author_last_name></wp:author>
%s
</channel>
</rss>
''' % '\n'.join(items)
    (RACINE / 'import' / 'pages.xml').write_text(xml, encoding='utf-8')


def construire_zip():
    destination = RACINE / 'dist' / 'kadence-pascal.zip'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as z:
        for chemin in sorted(THEME.rglob('*')):
            if chemin.is_file():
                info = zipfile.ZipInfo('kadence-pascal/' + chemin.relative_to(THEME).as_posix(), date_time=(2026, 10, 6, 12, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, chemin.read_bytes())


if __name__ == '__main__':
    construire_css()
    construire_wxr()
    construire_zip()
    print('ok : assets/pd.css, import/pages.xml, dist/kadence-pascal.zip')
