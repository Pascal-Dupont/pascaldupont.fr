#!/usr/bin/env python3
"""
Génère les pages du site en Kadence Blocks à partir de contenu/site.json.

Chaque page devient une spec JSON (outils/specs/<slug>.json) que l'outil
outils/wp-test/editeur.js construit dans le VRAI éditeur de blocs : c'est
Kadence qui écrit le code des blocs, les pages sont donc valides et éditables.

Règles suivies (voir outils/kadence-reference/*.md) :
  - uniqueID explicite (avec des tirets) sur chaque bloc Kadence structurel et bouton ;
  - kbVersion 2 et colLayout sur chaque rangée, borderWidth vide sur chaque colonne ;
  - couleurs explicites (palette Kadence du site ou hexadécimal), aucune police Google ;
  - méta de page Kadence : pleine largeur, sans boîte, sans marges, sans titre.

Usage :
  python3 outils/pages_kadence.py                       -> écrit les specs
  python3 outils/pages_kadence.py --construire [--base http://127.0.0.1:8081] [slug ...]
"""
import json
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SITE = json.loads((RACINE / 'contenu' / 'site.json').read_text(encoding='utf-8'))
SPECS = RACINE / 'outils' / 'specs'
YT = 'https://www.youtube.com/watch?v='

# Couleurs : palette Kadence du site (réglée par le thème enfant) ou hexadécimal.
NUIT, ARDOISE, ARDOISE2, LIGNE = 'palette9', 'palette8', 'palette7', 'palette6'
TEXTE, DOUX, SABLE, BERET, BERET_VIF = 'palette3', 'palette4', 'palette5', 'palette1', 'palette2'
HEX = {'palette9': '#0d1217', 'palette8': '#17202a', 'palette7': '#223040', 'palette6': '#2c3a49',
       'palette3': '#e8e6e1', 'palette4': '#a9b6c0', 'palette5': '#c8b287', 'palette1': '#a3302f', 'palette2': '#c0403d'}
IVOIRE, ENCRE, ENCRE_DOUX, LIGNE_CLAIRE = '#ece8df', '#10161c', '#4a5663', '#c9c4b8'

SERIF, MONO = 'Newsreader', 'IBM Plex Mono'
META_PAGE = {'_kad_post_layout': 'fullwidth', '_kad_post_content_style': 'unboxed',
             '_kad_post_vertical_padding': 'hide', '_kad_post_title': 'hide', '_kad_post_feature': 'hide'}


NBSP = '\u00a0'


def fr(t):
    """Typographie française : espaces insécables avant : ; ? ! », après «, entre un nombre et son unité, et dans « 1er RCP »."""
    if not isinstance(t, str):
        return t
    morceaux = re.split(r'(<[^>]*>)', t)
    sortie = []
    for m in morceaux:
        if m.startswith('<'):
            sortie.append(m)
            continue
        m = re.sub(r' ([:;?!»])', NBSP + r'\1', m)
        m = re.sub(r'« ', '«' + NBSP, m)
        m = re.sub(r'(\d) (?=(?:min|minutes|h|ans|jours|films|millions|vues)\b)', r'\1' + NBSP, m)
        m = re.sub(r'\b1er (?=RCP)', '1er' + NBSP, m)
        sortie.append(m)
    return ''.join(sortie)


class Page:
    """Fabrique de blocs pour une page : numérote les uniqueID."""

    def __init__(self, cle):
        self.cle = cle
        self.n = 0

    def uid(self, suffixe=''):
        self.n += 1
        return 'pd-%s-%d%s' % (self.cle, self.n, ('-' + suffixe) if suffixe else '')

    # ------------------------------------------------------------ structure

    def colonne(self, enfants, **attr):
        a = {'uniqueID': self.uid('c'), 'kbVersion': 2, 'borderWidth': ['', '', '', '']}
        a.update(attr)
        return {'name': 'kadence/column', 'attributes': a, 'innerBlocks': enfants}

    def rangee(self, colonnes, layout='equal', tablette=None, mobile='row', gouttiere=None, gouttiere_v=None, **attr):
        """Rangée imbriquée (sans fond ni padding latéral)."""
        a = {'uniqueID': self.uid('r'), 'kbVersion': 2, 'columns': len(colonnes) if attr.get('columns') is None else attr.pop('columns'),
             'colLayout': layout, 'mobileLayout': mobile, 'padding': [0, 0, 0, 0], 'paddingUnit': 'px'}
        if tablette:
            a['tabletLayout'] = tablette
        if gouttiere:
            a.update({'columnGutter': 'custom', 'tabletGutter': 'custom', 'mobileGutter': 'custom', 'customGutter': gouttiere, 'gutterType': 'px'})
        if gouttiere_v:
            a.update({'collapseGutter': 'custom', 'tabletRowGutter': 'custom', 'mobileRowGutter': 'custom', 'customRowGutter': gouttiere_v, 'rowGutterType': 'px'})
        a.update(attr)
        return {'name': 'kadence/rowlayout', 'attributes': a, 'innerBlocks': colonnes}

    def section(self, enfants, fond=NUIT, texte=TEXTE, padding=(96, 72, 56), padding_bas=None, classe=None, ancre=None, bordures=None, fond_attr=None):
        """Section pleine largeur, contenu centré limité à 72rem, une colonne."""
        bas = padding_bas or padding
        a = {'uniqueID': self.uid('s'), 'kbVersion': 2, 'columns': 1, 'colLayout': 'equal', 'align': 'full', 'htmlTag': 'section',
             'bgColor': fond, 'textColor': texte,
             'padding': [padding[0], '', bas[0], ''], 'tabletPadding': [padding[1], '', bas[1], ''], 'mobilePadding': [padding[2], '', bas[2], ''],
             'paddingUnit': 'px', 'maxWidth': 72, 'maxWidthUnit': 'rem'}
        if classe:
            a['className'] = classe
        if ancre:
            a['anchor'] = ancre
        if bordures:
            a['borderStyle'] = bordures
        if fond_attr:
            a.update(fond_attr)
        return {'name': 'kadence/rowlayout', 'attributes': a, 'innerBlocks': [self.colonne(enfants)]}

    # ------------------------------------------------------------ texte

    def surtitre(self, texte, couleur=SABLE, marge_bas=16):
        return {'name': 'kadence/advancedheading', 'attributes': {
            'content': fr(texte), 'htmlTag': 'p', 'typography': MONO, 'googleFont': False, 'fontWeight': '500',
            'fontSize': [0.75, '', ''], 'sizeType': 'rem', 'fontHeight': [1.5, '', ''], 'fontHeightType': '',
            'letterSpacing': 0.14, 'letterSpacingType': 'em', 'textTransform': 'uppercase',
            'color': couleur, 'margin': [0, '', marge_bas, ''], 'marginType': 'px'}}

    def titre(self, texte, niveau=2, taille=(3.2, 2.6, 2.1), couleur=TEXTE, marge_bas=20, accent=None, largeur=None, interligne=1.1, lien=None):
        a = {'content': fr(texte), 'level': niveau, 'typography': SERIF, 'googleFont': False, 'fontWeight': '400',
             'fontSize': list(taille), 'sizeType': 'rem', 'fontHeight': [interligne, '', ''], 'fontHeightType': '',
             'color': couleur, 'margin': [0, '', marge_bas, ''], 'marginType': 'px'}
        if accent:
            a.update({'markColor': accent, 'markFontStyle': 'italic'})
        if largeur:
            a.update({'maxWidth': [largeur, '', ''], 'maxWidthType': 'px'})
        if lien:
            a.update({'link': lien, 'linkTarget': lien.startswith('http'), 'linkStyle': 'hover_underline', 'linkColor': couleur, 'linkHoverColor': BERET_VIF})
        return {'name': 'kadence/advancedheading', 'attributes': a}

    def ligne(self, texte, taille=1.1, couleur=DOUX, marge_bas=16, largeur=None, police=None, italique=False, interligne=1.6,
              liens=None, graisse=None, classe=None):
        """Texte court stylé (advancedheading en <p>) : accroches, lignes de liens."""
        a = {'content': fr(texte), 'htmlTag': 'p', 'fontSize': list(taille) if isinstance(taille, tuple) else [taille, '', ''], 'sizeType': 'rem',
             'fontHeight': [interligne, '', ''], 'fontHeightType': '', 'color': couleur, 'margin': [0, '', marge_bas, ''], 'marginType': 'px'}
        if police:
            a.update({'typography': police, 'googleFont': False, 'fontWeight': graisse or '400'})
        elif graisse:
            a['fontWeight'] = graisse
        if italique:
            a['fontStyle'] = 'italic'
        if largeur:
            a.update({'maxWidth': [largeur, '', ''], 'maxWidthType': 'px'})
        if liens:
            a.update({'linkColor': liens[0], 'linkHoverColor': liens[1], 'linkStyle': 'underline'})
        if classe:
            a['className'] = classe
        return {'name': 'kadence/advancedheading', 'attributes': a}

    def paragraphe(self, texte, couleur=None, taille='1.0625rem', marge_bas='1.1rem', classe=None):
        style = {'typography': {'fontSize': taille, 'lineHeight': '1.65'}, 'spacing': {'margin': {'top': '0', 'bottom': marge_bas}}}
        if couleur:
            style['color'] = {'text': HEX.get(couleur, couleur)}
        a = {'content': fr(texte), 'style': style}
        if classe:
            a['className'] = classe
        return {'name': 'core/paragraph', 'attributes': a}

    # ------------------------------------------------------------ boutons

    @staticmethod
    def _bord(c):
        cote = [c, 'solid', 1]
        return [{'top': cote, 'right': cote, 'bottom': cote, 'left': cote, 'unit': 'px'}]

    def bouton(self, texte, url, style='plein', petit=False):
        externe = url.startswith('http')
        typo = [{'size': [0.85 if petit else 0.95, '', ''], 'sizeType': 'rem', 'lineHeight': [1.2, '', ''], 'lineType': '',
                 'letterSpacing': [0.04, '', ''], 'letterType': 'em', 'textTransform': '', 'family': '', 'google': False,
                 'style': '', 'weight': '500', 'variant': '', 'subset': '', 'loadGoogle': False}]
        a = {'uniqueID': self.uid('b'), 'text': fr(texte), 'link': url, 'borderRadius': [2, 2, 2, 2], 'borderRadiusUnit': 'px',
             'padding': [0.5, 1, 0.5, 1] if petit else [0.9, 1.5, 0.9, 1.5], 'paddingUnit': 'rem', 'typography': typo}
        if style == 'plein':
            a.update({'color': IVOIRE, 'background': BERET, 'colorHover': IVOIRE, 'backgroundHover': BERET_VIF,
                      'borderStyle': self._bord(HEX[BERET]), 'borderHoverStyle': self._bord(HEX[BERET_VIF])})
        elif style == 'contour-sombre':  # sur fond clair
            a.update({'inheritStyles': 'outline', 'color': ENCRE, 'background': 'transparent', 'colorHover': IVOIRE, 'backgroundHover': ENCRE,
                      'borderStyle': self._bord(ENCRE), 'borderHoverStyle': self._bord(ENCRE)})
        else:  # contour clair sur fond sombre
            a.update({'inheritStyles': 'outline', 'color': TEXTE, 'background': 'transparent', 'colorHover': NUIT, 'backgroundHover': TEXTE,
                      'borderStyle': self._bord(HEX[DOUX]), 'borderHoverStyle': self._bord(HEX[TEXTE])})
        if externe:
            a['target'] = '_blank'
        return {'name': 'kadence/singlebtn', 'attributes': a}

    def boutons(self, liste, marge_haut=8, petit=False, **extra):
        return {'name': 'kadence/advancedbtn', 'attributes': {
            'uniqueID': self.uid('g'), 'hAlign': 'left', 'gap': [0.9 if not petit else 0.5, '', ''], 'gapUnit': 'rem',
            'margin': [{'desk': [marge_haut, '', 0, ''], 'tablet': ['', '', '', ''], 'mobile': ['', '', '', '']}], 'marginUnit': 'px', **extra},
            'innerBlocks': [self.bouton(b['texte'], b['url'], b.get('style', 'plein'), petit) for b in liste]}

    # ------------------------------------------------------------ éléments composés

    def entete_section(self, surtitre, titre, texte=None, couleur_titre=TEXTE, couleur_sur=SABLE, couleur_texte=DOUX, marge_bas=40):
        blocs = []
        if surtitre:
            blocs.append(self.surtitre(surtitre, couleur_sur))
        blocs.append(self.titre(titre, 2, couleur=couleur_titre, marge_bas=16 if texte else marge_bas))
        if texte:
            blocs.append(self.ligne(texte, 1.0625, couleur_texte, marge_bas=marge_bas, largeur=672))
        return blocs

    def entete_page(self, e, enfants_apres=None):
        blocs = []
        if e.get('retour'):
            blocs.append(self.ligne('<a href="%s">%s</a>' % (e['retour']['url'], e['retour']['texte']), 0.9, DOUX, 20, liens=(DOUX, TEXTE)))
        blocs.append(self.surtitre(e['surtitre']))
        blocs.append(self.titre(e['titre'], 1, taille=(4.4, 3.4, 2.6), marge_bas=20, largeur=880))
        if e.get('texte'):
            blocs.append(self.ligne(e['texte'], 1.15, DOUX, 0, largeur=720))
        blocs += enfants_apres or []
        return self.section(blocs, padding=(88, 72, 48), padding_bas=(56, 48, 32))

    def duree(self, d):
        if not d:
            return ''
        p = [int(x) for x in d.split(':')]
        if len(p) == 3:
            h, m, s = p
            m += 1 if s >= 30 else 0
            return '%d h %02d' % (h, m)
        m, s = p
        m += 1 if s >= 30 else 0
        return '%d min' % max(m, 1)

    def carte(self, f, date=None, etiquette=None):
        """Carte film : vignette 16/9 (YouTube) ou aplat, titre, description, liens."""
        liens = f.get('liens')
        yt = f.get('youtube')
        if not yt and liens:
            yt = next((x['url'] for x in liens if 'youtube.com/watch' in x['url']), None)
        if not yt and liens is None and re.fullmatch(r'[\w-]{11}', f['id']):
            yt = YT + f['id']
        if yt and liens:
            liens = [x for x in liens if x['url'] != yt] or None
        enfants = []
        if yt:
            enfants.append({'name': 'kadence/image', 'attributes': {
                'url': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % f['id'], 'alt': 'Vignette du film « %s »' % f['titre'],
                'useRatio': True, 'ratio': 'land169', 'link': yt, 'linkTarget': True,
                'linkTitle': 'Voir « %s » sur YouTube (nouvel onglet)' % f['titre'],
                'borderRadius': [2, 2, 2, 2], 'borderRadiusUnit': 'px', 'marginDesktop': [0, 0, 14, 0], 'marginUnit': 'px'}})
        elif f['id'].startswith('RCP') and RCP_VIGNETTE and f.get('liens'):
            enfants.append({'name': 'kadence/image', 'attributes': {
                'url': RCP_VIGNETTE, 'alt': 'Vignette du film « %s »' % f['titre'], 'useRatio': True, 'ratio': 'land169',
                'link': f['liens'][0]['url'], 'linkTarget': True, 'linkTitle': 'Voir « %s » sur %s (nouvel onglet)' % (f['titre'], f['liens'][0]['reseau']),
                'borderRadius': [2, 2, 2, 2], 'borderRadiusUnit': 'px', 'marginDesktop': [0, 0, 14, 0], 'marginUnit': 'px'}})
        else:
            s = sum(ord(c) for c in f['id'])
            t = 190 + (s % 70)
            enfants.append({'name': 'core/cover', 'attributes': {
                'customGradient': 'linear-gradient(160deg,hsl(%d 22%% 34%%),hsl(%d 26%% 10%%))' % (t, t), 'dimRatio': 100, 'isDark': True,
                'contentPosition': 'bottom left', 'minHeight': 120, 'minHeightUnit': 'px',
                'style': {'dimensions': {'aspectRatio': '16/9'}, 'border': {'radius': '2px'}, 'spacing': {'margin': {'bottom': '14px'}, 'padding': {'top': '12px', 'right': '14px', 'bottom': '12px', 'left': '14px'}}},
                'className': 'pd-vignette-vide'},
                'innerBlocks': []})
        if date:
            enfants.append(self.surtitre(date, marge_bas=6))
        elif etiquette or f.get('etiquette'):
            enfants.append(self.surtitre(etiquette or f.get('etiquette'), marge_bas=6))
        lien_titre = liens[0]['url'] if (liens and not yt) else None
        enfants.append(self.titre(f['titre'], 3, taille=(1.35, 1.3, 1.25), marge_bas=6, interligne=1.2, lien=lien_titre))
        desc = ' · '.join(x for x in [f.get('description', ''), self.duree(f.get('duree', ''))] if x)
        if desc:
            enfants.append(self.ligne(desc, 0.92, DOUX, 6, interligne=1.5))
        if liens:
            l = ' · '.join('<a href="%s" target="_blank" rel="noreferrer noopener">%s</a>' % (x['url'], x['reseau']) for x in liens)
            enfants.append(self.ligne('Voir sur : ' + l, 0.85, DOUX, 0, interligne=1.5, liens=(TEXTE, BERET_VIF)))
        return self.colonne(enfants, htmlTag='article', className='pd-carte')

    def grille(self, cartes, colonnes=4):
        while len(cartes) < colonnes:
            cartes.append(self.colonne([]))
        return self.rangee(cartes, layout='equal', tablette='two-grid', mobile='row', gouttiere=[24, 20, 16], gouttiere_v=[40, 32, 28],
                           columns=colonnes, margin=[0, '', 0, ''], marginUnit='px')

    def chiffres(self, liste, fond_clair=False):
        cols = []
        for c in liste:
            cols.append(self.colonne([
                self.ligne(c['valeur'], (2.8, 2.6, 2.4), TEXTE, 10, police=SERIF, interligne=1),
                self.ligne(c['texte'], 0.92, DOUX, 0, interligne=1.5),
            ], borderStyle=[{'top': [HEX[SABLE], 'solid', 1], 'right': ['', '', ''], 'bottom': ['', '', ''], 'left': ['', '', ''], 'unit': 'px'}],
                padding=[16, 0, 0, 0], paddingType='px'))
        return self.rangee(cols, layout='equal', tablette='two-grid', mobile='two-grid', gouttiere=[24, 20, 16], gouttiere_v=[36, 28, 24],
                           columns=4)

    def lignes_titre_texte(self, lignes, clair=False):
        """Liste à deux colonnes (titre | texte) séparées par un filet : prestations, formats."""
        filet = LIGNE_CLAIRE if clair else HEX[LIGNE]
        rangs = []
        for i, l in enumerate(lignes):
            bord = {'top': ['', '', ''], 'right': ['', '', ''], 'bottom': [filet, 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}
            if i == 0:
                bord['top'] = [ENCRE if clair else HEX[LIGNE], 'solid', 1]
            rangs.append(self.rangee([
                self.colonne([self.titre(l['titre'], 3, taille=(1.6, 1.45, 1.3), couleur=ENCRE if clair else TEXTE, marge_bas=0, interligne=1.2)]),
                self.colonne([self.ligne(l['texte'], 1.0625, ENCRE_DOUX if clair else DOUX, 0, interligne=1.6)]),
            ], layout='equal', firstColumnWidth=40, secondColumnWidth=60, mobile='row', gouttiere=[48, 32, 8], gouttiere_v=[8, 8, 8], borderStyle=[bord],
                padding=[24, 0, 24, 0], paddingUnit='px'))
        return rangs

    def liste_dates(self, lignes, classe='pd-liste'):
        corps = [{'cells': [{'content': a, 'tag': 'td'}, {'content': b, 'tag': 'td'}]} for a, b in lignes]
        return {'name': 'core/table', 'attributes': {'body': corps, 'hasFixedLayout': False, 'className': classe}}

    def coordonnee(self, etiquette, valeur):
        return [self.surtitre(etiquette, marge_bas=4), self.ligne(valeur, 1.25, TEXTE, 18)]


# ================================================================ pages

_RCP = next((x for x in ('rcp-vignette.jpg', 'rcp-vignette.png') if (DEPOT / 'kadence-pascal' / 'assets' / x).exists()), None)
RCP_VIGNETTE = '/wp-content/themes/kadence-pascal/assets/' + _RCP if _RCP else None


def films_par_id():
    d = {}
    for g in SITE['films']['groupes']:
        for f in g['films']:
            d[f['id']] = f
    return d


def page_accueil():
    P = Page('accueil')
    c = SITE['pages']['accueil']
    h = c['hero']
    hero = P.section([
        P.surtitre(h['surtitre'], marge_bas=20),
        P.titre(h['titre'] + '<mark class="kt-highlight">' + h['titre_accent'] + '</mark>' + h['titre_fin'], 1, taille=(5.4, 4, 2.7),
                accent=SABLE, largeur=880, interligne=1.05, marge_bas=28),
        P.ligne(h['texte'], 1.15, DOUX, 0, largeur=608),
        P.boutons(h['boutons'], marge_haut=36, orientation=['', '', 'column']),
    ], padding=(120, 96, 72), padding_bas=(200, 168, 136), classe='pd-hero',
        fond_attr={'backgroundSettingTab': 'gradient', 'gradient': 'linear-gradient(180deg,#131c25 0%,#1b2733 55%,#2a3846 100%)'})

    une = c['a_la_une']
    fid = films_par_id()
    cartes = []
    for u in SITE['films']['une']:
        if u['id'] == 'SERVAL':
            f = {'id': 'SERVAL', 'titre': u['titre'], 'description': u['description'], 'liens': [{'reseau': 'la série complète', 'url': '/serie-serval/'}]}
            col = P.carte(f, etiquette='Série')
            # lien interne : pas de nouvel onglet
            for b in col['innerBlocks']:
                if b['name'] == 'kadence/advancedheading' and 'Voir sur' in b['attributes']['content']:
                    b['attributes']['content'] = '<a href="/serie-serval/">Voir la série</a>'
            cartes.append(col)
        elif u['id'] == 'JEB':
            f = dict(fid['RCP4'])
            f['description'] = u['description']
            cartes.append(P.carte(f, etiquette=u['etiquette']))
        else:
            f = dict(fid.get(u['id'], {}))
            f.update({'id': u['id'], 'titre': u['titre'], 'description': u['description'], 'duree': u['duree']})
            if u['id'] == 'uF7zqXfUsjc':  # Everrard : vignette YouTube à la une
                f.pop('liens', None)
            cartes.append(P.carte(f, etiquette=u['etiquette']))
    a_la_une = P.section(P.entete_section(une['surtitre'], une['titre'], une['texte']) + [P.grille(cartes, 3), P.boutons([une['bouton']], marge_haut=40)],
                         ancre='a-la-une', padding=(40, 32, 24), padding_bas=(96, 72, 56))

    r = c['revivre']
    moitie = len(r['paragraphes']) // 2
    revivre = P.section([
        P.surtitre(r['surtitre']),
        P.titre(r['titre'], 2, taille=(3.2, 2.6, 2.1), marge_bas=16),
        P.ligne(r['question'], (1.9, 1.7, 1.45), TEXTE, 32, police=SERIF, italique=True, largeur=640, interligne=1.25, classe='pd-equilibre'),
        P.rangee([P.colonne([P.paragraphe(t, DOUX) for t in r['paragraphes'][:moitie]]),
                  P.colonne([P.paragraphe(t, DOUX) for t in r['paragraphes'][moitie:]])], gouttiere=[40, 32, 0], gouttiere_v=[0, 0, 0]),
    ], fond=ARDOISE, ancre='revivre',
        bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': [HEX[LIGNE], 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}])

    ref = c['references']
    noms = {'name': 'core/list', 'attributes': {'className': 'pd-noms'},
            'innerBlocks': [{'name': 'core/list-item', 'attributes': {'content': n}} for n in ref['noms']]}
    references = P.section(P.entete_section(ref['surtitre'], ref['titre'], marge_bas=32) + [noms], padding=(80, 64, 48))

    pr = c['prestations']
    prestations = P.section(P.entete_section(pr['surtitre'], pr['titre'], pr['texte'], couleur_titre=ENCRE, couleur_sur=BERET, couleur_texte=ENCRE_DOUX)
                            + P.lignes_titre_texte(pr['lignes'], clair=True) + [P.boutons(pr['boutons'], marge_haut=40)],
                            fond=IVOIRE, texte=ENCRE, ancre='prestations')

    lk = c['lakelab']
    reseaux_lk = [{'texte': r['reseau'], 'url': r['url'], 'style': 'contour'} for r in SITE['identite']['reseaux_lakelab']]
    lakelab = P.section([P.rangee([
        P.colonne([P.surtitre(lk['surtitre']), P.titre(lk['titre'], 2, marge_bas=16), P.ligne(lk['texte'], 1.0625, DOUX, 0, largeur=544),
                   P.boutons([lk['bouton']] + reseaux_lk, marge_haut=28, petit=True)]),
        P.colonne([P.carte(fid['6FrZTiHyWsk'], etiquette='LAKELAB')]),
    ], layout='equal', tabletLayout='row', gouttiere=[48, 40, 0], gouttiere_v=[0, 24, 40], verticalAlignment='middle')], fond=ARDOISE, ancre='lakelab',
        bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': [HEX[LIGNE], 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}])

    ct = c['contact']
    ident = SITE['identite']
    contact = P.section([P.rangee([
        P.colonne(P.entete_section(ct['surtitre'], ct['titre'], ct['texte'], marge_bas=8) + [P.boutons([ct['bouton']], marge_haut=32)]),
        P.colonne(P.coordonnee('Téléphone', ident['telephone']) + P.coordonnee('E-mail', ident['email'])),
    ], layout='equal', gouttiere=[56, 40, 0], gouttiere_v=[0, 0, 32])])
    return c['titre'], [hero, a_la_une, revivre, references, prestations, lakelab, contact]


def page_films():
    P = Page('films')
    c = SITE['pages']['films']
    entete = P.entete_page(c['entete'])
    ongl = SITE['films']['onglets']
    fid = films_par_id()
    titres = [{'text': o['titre'], 'icon': '', 'iconSide': 'right', 'onlyIcon': False, 'subText': '', 'anchor': 'films-' + o['ancre']} for o in ongl]
    onglets = []
    for i, o in enumerate(ongl, start=1):
        enfants = [P.ligne(o['texte'], 1.0625, DOUX, 8, largeur=720)]
        for k, bl in enumerate(o['blocs']):
            haut = 40 if (k or True) else 0
            if bl.get('docs'):
                cols = []
                for x in bl['docs']:
                    f = dict(fid[x['id']])
                    f.update({'titre': x['titre'], 'description': '', 'duree': ''})
                    col = P.carte(f, etiquette=x['etiquette'])
                    col['innerBlocks'].append(P.paragraphe(x['texte'], DOUX))
                    col['innerBlocks'].append(P.boutons(x['boutons'], marge_haut=8, petit=True))
                    cols.append(col)
                enfants.append(P.grille(cols, 3))
                continue
            if bl.get('titre'):
                h = P.titre(bl['titre'], 3, taille=(1.6, 1.5, 1.4), marge_bas=10)
                h['attributes']['margin'] = [haut + 8, '', 10, '']
                enfants.append(h)
            if bl.get('texte'):
                enfants.append(P.ligne(bl['texte'], 1.0, DOUX, 24, largeur=720))
            if bl.get('films'):
                enfants.append(P.grille([P.carte(fid[x]) for x in bl['films']], 4))
            if bl.get('boutons'):
                enfants.append(P.boutons([{'texte': l['texte'], 'url': l['url'], 'style': l.get('style', 'contour')} for l in bl['boutons']], marge_haut=28))
        onglets.append({'name': 'kadence/tab', 'attributes': {'id': i, 'uniqueID': P.uid('o')}, 'innerBlocks': enfants})
    tabs = {'name': 'kadence/tabs', 'attributes': {
        'uniqueID': P.uid('onglets'), 'tabCount': len(ongl), 'startTab': 1, 'layout': 'tabs', 'tabletLayout': 'inherit', 'mobileLayout': 'inherit',
        'tabAlignment': 'left', 'titles': titres,
        'titleColor': HEX[DOUX], 'titleColorHover': HEX[TEXTE], 'titleColorActive': HEX[NUIT],
        'titleBg': 'transparent', 'titleBgHover': 'transparent', 'titleBgActive': HEX[TEXTE],
        'titleBorder': HEX[LIGNE], 'titleBorderHover': HEX[DOUX], 'titleBorderActive': HEX[TEXTE],
        'titleBorderWidth': [1, 1, 1, 1], 'titleBorderWidthUnit': 'px', 'titleBorderRadius': [999, 999, 999, 999], 'titleBorderRadiusUnit': 'px',
        'titlePadding': [0.5, 1, 0.5, 1], 'titlePaddingUnit': 'rem', 'titleMargin': [0, 8, 8, 0], 'titleMarginUnit': 'px',
        'size': '0.85', 'sizeType': 'rem', 'lineHeight': 1.4, 'lineType': '', 'fontWeight': '500',
        'contentBorderStyles': [{'top': ['', '', 0], 'right': ['', '', 0], 'bottom': ['', '', 0], 'left': ['', '', 0], 'unit': 'px'}],
        'innerPadding': [32, 0, 0, 0], 'innerPaddingType': 'px'}, 'innerBlocks': onglets}
    corps = P.section([tabs], padding=(24, 24, 16), padding_bas=(96, 72, 56))
    return c['titre'], [entete, corps]


def page_apropos():
    P = Page('apropos')
    c = SITE['pages']['a-propos']
    entete = P.entete_page(c['entete'])
    portrait = {'name': 'core/cover', 'attributes': {
        'customGradient': 'linear-gradient(160deg,#46606f,#10181e)', 'dimRatio': 100, 'isDark': True, 'contentPosition': 'bottom left',
        'minHeight': 320, 'minHeightUnit': 'px', 'className': 'pd-portrait',
        'style': {'dimensions': {'aspectRatio': '4/5'}, 'spacing': {'padding': {'top': '16px', 'right': '16px', 'bottom': '16px', 'left': '16px'}}}},
        'innerBlocks': [P.ligne(c['portrait']['texte_provisoire'], 0.72, TEXTE, 0, police=MONO, graisse='500')]}
    texte = [P.paragraphe(t, TEXTE, taille='1.2rem', marge_bas='1.3rem') for t in c['paragraphes']]
    citation = P.ligne(c['citation'], 2, TEXTE, 0, police=SERIF, italique=True, interligne=1.2)
    citation['attributes'].update({'borderStyle': [{'top': ['', '', ''], 'right': ['', '', ''], 'bottom': ['', '', ''], 'left': [HEX[BERET_VIF], 'solid', 2], 'unit': 'px'}],
                                   'padding': [0, 0, 0, 20], 'paddingType': 'px', 'margin': [16, '', 32, ''], 'marginType': 'px'})
    bloc = P.section([P.rangee([P.colonne([portrait]), P.colonne(texte + [citation, P.boutons(c['boutons'])])],
                               layout='equal', firstColumnWidth=36, secondColumnWidth=64, gouttiere=[56, 40, 0], gouttiere_v=[0, 0, 32])], padding=(24, 16, 8))
    rep, lu = c['reperes'], c['lucile']
    lucile_p = [P.paragraphe(lu['paragraphes'][0], DOUX),
                P.paragraphe(lu['paragraphes'][1].replace('LAKELAB', '<a href="%s">%s</a>' % (lu['lien']['url'], lu['lien']['texte']), 1), DOUX)]
    bas = P.section([P.rangee([
        P.colonne([P.titre(rep['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16), P.liste_dates(rep['lignes'])]),
        P.colonne([P.titre(lu['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16)] + lucile_p),
    ], layout='equal', gouttiere=[48, 40, 0], gouttiere_v=[0, 0, 40])], fond=ARDOISE,
        bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': [HEX[LIGNE], 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}])
    return c['titre'], [entete, bloc, bas]


def page_defense():
    P = Page('defense')
    c = SITE['pages']['defense-et-securite']
    entete = P.entete_page(c['entete'])
    chiffres = P.section([P.chiffres(c['chiffres'])], padding=(40, 32, 24), padding_bas=(72, 56, 40))
    fo = c['formats']
    formats = P.section(P.entete_section(fo['surtitre'], fo['titre'], marge_bas=32) + P.lignes_titre_texte(fo['lignes']), padding=(0, 0, 0))
    ind = c['industrie']
    fid0 = films_par_id()
    industrie = P.section(P.entete_section(ind['surtitre'], ind['titre'], ind['texte'], marge_bas=32)
                          + [P.grille([P.carte(fid0[i]) for i in ind['films']], 4), P.boutons(ind['boutons'], marge_haut=36)],
                          padding=(0, 0, 0), padding_bas=(96, 72, 56))
    me, rf = c['methode'], c['references']
    etapes = {'name': 'core/list', 'attributes': {'ordered': True, 'className': 'pd-etapes'},
              'innerBlocks': [{'name': 'core/list-item', 'attributes': {'content': '<strong>%s</strong> %s' % (a, b)}} for a, b in me['etapes']]}
    milieu = P.section([P.rangee([
        P.colonne([P.titre(me['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16), etapes]),
        P.colonne([P.titre(rf['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16), P.liste_dates(rf['lignes'])]),
    ], layout='equal', gouttiere=[48, 40, 0], gouttiere_v=[0, 0, 40])], fond=ARDOISE,
        bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': [HEX[LIGNE], 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}])
    se = c['selection']
    fid = films_par_id()
    cartes = []
    for i in se['films']:
        cartes.append(P.carte(fid[i]))
    selection = P.section(P.entete_section(se['surtitre'], se['titre']) + [P.grille(cartes, 3), P.boutons(se['boutons'], marge_haut=40)])
    sv = c['serval']
    fab, presse = sv['fabrication'], sv['presse']
    credits = P.ligne('<br>'.join(fab['credits']), 0.8, DOUX, 0, police=MONO, interligne=1.8)
    credits['attributes']['borderStyle'] = [{'top': ['', '', ''], 'right': ['', '', ''], 'bottom': ['', '', ''], 'left': [HEX[BERET], 'solid', 2], 'unit': 'px'}]
    credits['attributes']['padding'] = [0, 0, 0, 16]
    credits['attributes']['paddingType'] = 'px'
    serval = P.section(P.entete_section(sv['surtitre'], sv['titre'], sv['texte'], marge_bas=32) + [P.chiffres(sv['chiffres']), P.rangee([
        P.colonne([P.titre(fab['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16)] + [P.paragraphe(t, DOUX) for t in fab['paragraphes']] + [credits]),
        P.colonne([P.titre(presse['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=16), P.liste_dates(presse['lignes'])]),
    ], layout='equal', gouttiere=[48, 40, 0], gouttiere_v=[0, 0, 40], margin=[56, '', 0, ''], marginUnit='px')],
        fond=ARDOISE, ancre='serval', bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': ['', '', ''], 'left': ['', '', ''], 'unit': 'px'}])
    return c['titre'], [entete, chiffres, industrie, formats, milieu, selection, serval]


def page_lakelab():
    P = Page('lakelab')
    c = SITE['pages']['lakelab']
    entete = P.entete_page(c['entete'])
    reseaux = [{'texte': r['reseau'], 'url': r['url'], 'style': 'contour'} for r in SITE['identite']['reseaux_lakelab']]
    suivre = P.section([P.titre(c['suivre']['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=12), P.ligne(c['suivre']['texte'], 1.0625, DOUX, 0),
                        P.boutons(reseaux, marge_haut=24)], padding=(16, 16, 8), padding_bas=(64, 48, 40))
    fid = films_par_id()
    films = P.section([P.titre(c['films']['titre'], 2, taille=(1.9, 1.75, 1.6), marge_bas=28), P.grille([P.carte(fid[i]) for i in c['films']['ids']], 3)],
                      fond=ARDOISE, bordures=[{'top': [HEX[LIGNE], 'solid', 1], 'right': ['', '', ''], 'bottom': [HEX[LIGNE], 'solid', 1], 'left': ['', '', ''], 'unit': 'px'}])
    return c['titre'], [entete, suivre, films]


def page_contact():
    P = Page('contact')
    c = SITE['pages']['contact']
    ident = SITE['identite']
    e = c['entete']
    liens = ' · '.join('<a href="%s" target="_blank" rel="noreferrer noopener">%s</a>' % (r['url'], r['reseau']) for r in ident['reseaux_personnels'])
    gauche = [P.surtitre(e['surtitre']), P.titre(e['titre'], 1, taille=(3.6, 3, 2.4), marge_bas=16), P.ligne(e['texte'], 1.1, DOUX, 32, largeur=480)]
    gauche += P.coordonnee('Téléphone', ident['telephone']) + P.coordonnee('E-mail', ident['email'])
    gauche += [P.surtitre('Me suivre', marge_bas=6), P.ligne(liens, 1.0, TEXTE, 0, interligne=1.8, liens=(TEXTE, BERET_VIF))]
    droite = [{'name': 'core/shortcode', 'attributes': {'text': '[pd_formulaire]'}}]
    bloc = P.section([P.rangee([P.colonne(gauche), P.colonne(droite, anchor='formulaire')], layout='equal', gouttiere=[56, 40, 0], gouttiere_v=[0, 0, 40])],
                     padding=(88, 72, 48))
    return c['titre'], [bloc]


def page_legale(cle):
    P = Page(cle.split('-')[0])
    c = SITE['pages'][cle]
    blocs = [P.surtitre('Informations légales' if cle == 'mentions-legales' else 'Vos données'),
             P.titre(c['titre'], 1, taille=(3.6, 3, 2.4), marge_bas=32)]
    if c.get('a_relire'):
        blocs.append(P.ligne('Texte à faire relire avant la mise en ligne.', 0.95, SABLE, 24))
    for s in c['sections']:
        blocs.append(P.titre(s['titre'], 2, taille=(1.6, 1.5, 1.35), marge_bas=10))
        blocs.append(P.paragraphe('<br>'.join(s['lignes']).replace('[à compléter]', '<mark>[à compléter]</mark>'), DOUX, marge_bas='1.6rem'))
    return c['titre'], [P.section([P.rangee([P.colonne(blocs)], layout='equal', maxWidth=46, maxWidthUnit='rem')], padding=(88, 72, 48))]


PAGES = {
    'accueil': page_accueil, 'films': page_films, 'a-propos': page_apropos,
    'defense-et-securite': page_defense, 'lakelab': page_lakelab, 'contact': page_contact,
    'mentions-legales': lambda: page_legale('mentions-legales'), 'confidentialite': lambda: page_legale('confidentialite'),
}


def ecrire_specs():
    SPECS.mkdir(parents=True, exist_ok=True)
    for slug, fabrique in PAGES.items():
        titre, blocs = fabrique()
        meta = dict(META_PAGE)
        meta['_pd_page'] = slug
        spec = {'titre': titre, 'slug': slug, 'meta': meta, 'blocs': blocs}
        if slug in SITE.get('descriptions', {}):
            spec['excerpt'] = SITE['descriptions'][slug]
        (SPECS / (slug + '.json')).write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding='utf-8')
    return list(PAGES)


def construire(base, slugs):
    rapport = {}
    for slug in slugs:
        r = subprocess.run(['node', str(RACINE / 'outils' / 'wp-test' / 'editeur.js'), 'construire', str(SPECS / (slug + '.json')), '--base', base],
                           capture_output=True, text=True, timeout=600)
        try:
            rapport[slug] = json.loads(r.stdout[r.stdout.index('{'):])
        except ValueError:
            rapport[slug] = {'erreur': (r.stdout + r.stderr)[-2000:]}
        res = rapport[slug]
        print(slug, '->', res.get('id'), 'invalides:', len(res.get('erreurs', [])), 'inconnus:', res.get('blocsInconnus'), 'JS:', res.get('erreursJS'), res.get('erreur', '')[:300])
    return rapport


if __name__ == '__main__':
    args = sys.argv[1:]
    toutes = ecrire_specs()
    print('specs écrites :', ', '.join(toutes))
    if args and args[0] == '--construire':
        base = 'http://127.0.0.1:8081'
        if '--base' in args:
            base = args[args.index('--base') + 1]
        choix = [a for a in args[1:] if a in PAGES] or toutes
        rapport = construire(base, choix)
        (SPECS / 'rapport.json').write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding='utf-8')
