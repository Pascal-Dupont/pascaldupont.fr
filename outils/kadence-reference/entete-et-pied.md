# Kadence 1.5.2 : en-tête et pied de page (Header Builder et Footer Builder) pilotés par theme_mods

Cette fiche sert à régler l'en-tête et le pied de page du thème Kadence **depuis le thème enfant `kadence-pascal`**, avec `set_theme_mod()`, sans passer par l'outil de personnalisation. Elle donne les clés exactes, leurs formats, les sélecteurs CSS réellement produits et une fonction PHP prête à l'emploi (§ 10).
Environnement vérifié : WordPress 7.1.3 (fr_FR), thème Kadence **1.5.2** + thème enfant `kadence-pascal`, Kadence Blocks 3.7.12.1 (gratuit).
À lire avec `theme-reglages.md` : palette, typographie générale, `site_background`, méta de page (`_kad_post_header`, `_kad_post_footer`, `_kad_post_transparent`).

Légende de la colonne « Vérif. » :
- **B** : vérifié par une **écriture réelle dans un bac à sable**. Le bac à sable est une copie privée du WordPress de test (fichiers, et base SQLite copiée avec `SQLite3::backup()`), servie sur `http://127.0.0.1:8097`. La valeur a été écrite avec `set_theme_mod()`, relue avec `get_theme_mod()` et `\Kadence\kadence()->option()`, puis le rendu public de la page `ref-entete-pied-test` a été mesuré avec `getComputedStyle` à 1280, 900 et 390 px (après défilement et menu mobile ouvert quand c'était utile). Pour isoler Kadence, `?sanspd=1` retirait `pd-kadence.css`. Ce paramètre est fourni par une extension `mu-plugins` présente **uniquement** dans le bac à sable.
- **T** : testé sur le **site partagé** (`http://127.0.0.1:8080`) avec l'outil (`editeur.js construire` puis `capture`), sans modifier aucun réglage : on y voit l'état par défaut de Kadence.
- **C** : lu dans le code source seulement (`inc/components/options/component.php` pour les valeurs par défaut, `inc/components/styles/component.php` pour le CSS, `inc/class-kadence-css.php`, `inc/template-functions/header-functions.php`, `inc/template-functions/footer-functions.php`, `inc/components/custom_header/component.php`, `inc/components/custom_footer/component.php`, `inc/components/nav_menus/component.php`, `template-parts/header/*.php`, `template-parts/footer/*.php`, `inc/customizer/options/*.php`, `assets/css/header.min.css`, `assets/css/footer.min.css`).

**Aucun réglage du site partagé n'a été modifié.** Sur `:8080`, les theme_mods sont restés `{"nav_menu_locations":[],"custom_css_post_id":-1,"initial_version":"1.5.2"}`, relus avant et après les essais. Seule la page `ref-entete-pied-test` y a été créée.

### Format des extraits « testés »

Ces réglages sont des **theme_mods**, pas des attributs de bloc : la spec JSON de `editeur.js construire` ne s'applique pas ici. Chaque extrait de cette fiche est un objet JSON `{ "clé": valeur }` qui a été écrit tel quel dans le bac à sable. Le script `clone.php variante <fichier.json>` (§ 13) fait un `set_theme_mod( $clé, $valeur )` par clé. Une valeur `null` y signifie `remove_theme_mod()`, c'est-à-dire le retour à la valeur par défaut. En PHP, on écrit la même chose avec des `array()`. La fonction complète est au § 10.

Points de rupture du CSS calculé par Kadence à partir des réglages : **tablette ≤ 1024 px**, **mobile ≤ 767 px**. La règle « bureau » (`desktop`) n'est dans aucune media query : elle s'applique à toutes les largeurs tant qu'une règle tablette ou mobile ne la remplace pas. Les classes des feuilles statiques (`vs-md-false`, `vs-sm-false`, colonnes du pied) utilisent d'autres seuils : **720–1024 px** et **≤ 719 px**.

---

## 0. Règles essentielles

1. **Stockage** : option `theme_mods_kadence-pascal`, c'est-à-dire les theme_mods du thème **actif**. On écrit avec `set_theme_mod( 'clé', valeur )` et on lit avec `\Kadence\kadence()->option( 'clé' )`. Celle-ci renvoie `get_theme_mod( 'clé', null )` et, si la valeur est `null` ou `''`, la valeur par défaut de Kadence. [B]
2. **Aucune fusion avec la valeur par défaut.** Une valeur enregistrée remplace **toute** la valeur par défaut. Essai : `{"brand_typography":{"size":{"desktop":30}}}` donne `.site-branding .site-title{font-size:30px;}` et rien d'autre. Le défaut, lui, donnait `font-weight:700;font-size:26px;line-height:1.2;color:var(--global-palette3)`. → **Toujours écrire l'objet complet**, avec toutes ses sous-clés. [B]
3. **Valeurs responsive = objets** `{"desktop":…,"tablet":…,"mobile":…}`, jamais des tableaux `[bureau, tablette, mobile]` comme dans Kadence Blocks. Une valeur vide (`""`) pour la tablette ou le mobile ne produit aucune règle : le palier plus large s'applique. Pour les tailles, l'unité est dans un objet parallèle `"unit":{"desktop":"px",…}`. [B]
4. **Deux en-têtes dans le HTML.** `#main-header` (bureau) est affiché à partir de 1025 px, `#mobile-header` en dessous. **Les tablettes ont donc l'en-tête mobile et le tiroir.** On change ce seuil avec `header_mobile_switch` (§ 6.4). [B]
5. **Couleurs** acceptées partout : `"#rrggbb"`, `"rgba(r,g,b,a)"`, `"transparent"` et `"paletteN"`, qui devient `var(--global-paletteN)`. [B] Les couleurs par défaut de Kadence sont des jetons de palette. Par exemple, le menu principal est en `palette5` par défaut, soit le sable `#c8b287` avec la palette du site (`theme-reglages.md`). → Indiquer **toutes** les couleurs explicitement.
6. **Zones de l'en-tête** : un élément n'est affiché que s'il est placé dans une zone. Une rangée n'est affichée que si sa zone `_left`, `_center` ou `_right` contient au moins un élément. **Les zones `_left_center` et `_right_center` ne sont rendues que si la zone `_center` de la même rangée est remplie.** Sinon, leurs éléments disparaissent sans message (§ 1.1). [B]
7. **Où trouver le CSS produit** : dans `<style id="kadence-global-inline-css">`, sous les commentaires `/* Kadence Header CSS */` et `/* Kadence Footer CSS */`. Il est recalculé à chaque chargement de page : une modification se voit au rechargement suivant, sans cache à vider. [B]
8. **`pd-kadence.css` écrase beaucoup de ces réglages avec `!important` et casse l'en-tête collant** (§ 9.3). À corriger en même temps que l'application des réglages.
9. **Menus** : les emplacements enregistrés sont `primary`, `secondary`, `mobile` et `footer`. [B, par `get_registered_nav_menus()`] Le menu mobile prend le menu `mobile` s'il existe, sinon `primary`. [C] Un emplacement sans menu affiche **à la place les 5 premières pages** (tri `menu_order` puis titre). Constaté sur le site partagé, sans menu : l'en-tête liste « Essai, Page d'exemple, REF accordeon 03, REF ancien 08, REF ancres 04 ». [T] Dans ce cas, le `<ul>` porte toujours `id="primary-menu"`, même dans le tiroir mobile ou le pied : on obtient des `id` en double. [B] Le `functions.php` du thème enfant attribue les emplacements `primary`, `mobile` et `footer` au premier passage dans l'administration, **une seule fois** (option `pd_installe`) et **seulement si** les pages portant la méta `_pd_page` = `accueil` et `films` existent déjà. Sur le site partagé, ces pages n'existent pas : `pd_installe` vaut `false` et `nav_menu_locations` reste vide, d'où le menu de secours. [Lecture du code + état relu, contre-vérification]
10. **Titre masqué sur tablette avec les valeurs par défaut.** Si `logo_layout.include.tablet` vaut `""` (défaut), Kadence ajoute la classe `vs-md-false` au titre de l'en-tête mobile. Cette classe donne `display:none !important` entre **720 et 1024 px** : sur tablette, l'en-tête n'a plus que le bouton menu. Constaté à 900 px sur le site partagé [T] et dans le bac à sable [B]. → Renseigner `include.tablet` (et `include.mobile`) explicitement (§ 2).

---

## 1. Éléments de l'en-tête

### 1.1 `header_desktop_items` (en-tête bureau)

| | |
|---|---|
| Type | objet à 3 niveaux : rangée → zone → liste ordonnée d'identifiants d'éléments |
| Rangées | `top`, `main`, `bottom` |
| Zones | `{rangée}_left`, `{rangée}_left_center`, `{rangée}_center`, `{rangée}_right_center`, `{rangée}_right` (ex. `main_left`) |
| Éléments | `logo`, `navigation` (menu `primary`), `navigation-2` (menu `secondary`), `search`, `button`, `social`, `html` (et `cart` avec WooCommerce). Chaque identifiant charge `template-parts/header/{identifiant}.php`. |
| Défaut | `{"top":{toutes zones []},"main":{"main_left":["logo"],"main_left_center":[],"main_center":[],"main_right_center":[],"main_right":["navigation"]},"bottom":{toutes zones []}}` |
| Vérif. | B |

Extrait testé (titre à gauche, menu à droite, rangée principale seule) :

```json
{"header_desktop_items": {
  "top":    {"top_left":[],"top_left_center":[],"top_center":[],"top_right_center":[],"top_right":[]},
  "main":   {"main_left":["logo"],"main_left_center":[],"main_center":[],"main_right_center":[],"main_right":["navigation"]},
  "bottom": {"bottom_left":[],"bottom_left_center":[],"bottom_center":[],"bottom_right_center":[],"bottom_right":[]}
}}
```

Constats [B] :
- La forme minimale `{"main":{"main_left":["logo"],"main_right":["navigation"]}}` fonctionne aussi en public. La structure complète reste préférable : c'est celle qu'enregistre l'outil de personnalisation.
- `top` avec un élément **seulement** dans `top_left_center` : la rangée `.site-top-header-wrap` est **absente** du HTML.
- `bottom` avec `["html"]` dans `bottom_center` : rangée affichée (`.site-bottom-header-wrap`).
- `main_left_center: ["html"]` et `main_right_center: ["button"]` avec `main_center` vide : **ni le HTML ni le bouton ne sont rendus**. Avec `main_center: ["social"]`, les deux apparaissent, dans `.site-header-main-section-left-center` et `.site-header-main-section-right-center`.
- Classes de la rangée : `.site-header-row-has-sides` ou `.site-header-row-only-center-column`, et `.site-header-row-center-column` ou `.site-header-row-no-center`.

### 1.2 `header_mobile_items` (en-tête mobile et tablette, tiroir)

| | |
|---|---|
| Type | objet : rangée → zone → liste d'identifiants |
| Rangées | `popup` (contenu du tiroir), `top`, `main`, `bottom` |
| Zones | `popup_content` ; `{rangée}_left`, `{rangée}_center`, `{rangée}_right`. L'interface ne propose pas `_left_center` ni `_right_center` en mobile, **mais le gabarit `mobile-header-row.php` les rend quand ils sont écrits par code**, à la même condition qu'au bureau : la zone `_center` de la rangée doit être remplie. Contre-vérification [B] : `main_left_center: ["mobile-html"]` est rendu avec `main_center: ["mobile-social"]`, et absent avec `main_center` vide. Préférer les trois zones de l'interface. |
| Éléments | `mobile-logo`, `mobile-navigation`, `search`, `mobile-button`, `mobile-social`, `mobile-html`, `popup-toggle` (le bouton qui ouvre le tiroir) et `mobile-cart` avec WooCommerce |
| Défaut | `{"popup":{"popup_content":["mobile-navigation"]},"top":{…[]},"main":{"main_left":["mobile-logo"],"main_center":[],"main_right":["popup-toggle"]},"bottom":{…[]}}` |
| Vérif. | B |

```json
{"header_mobile_items": {
  "popup":  {"popup_content":["mobile-navigation"]},
  "top":    {"top_left":[],"top_center":[],"top_right":[]},
  "main":   {"main_left":["mobile-logo"],"main_center":[],"main_right":["popup-toggle"]},
  "bottom": {"bottom_left":[],"bottom_center":[],"bottom_right":[]}
}}
```

- Le tiroir `#mobile-drawer` n'est produit **que si `popup-toggle` est placé** dans une rangée. Sans lui, ni `#mobile-toggle` ni `#mobile-drawer` ne figurent dans le HTML, même si `popup_content` est rempli. [B]
- Le tiroir est imprimé en fin de page (`wp_footer`), en dehors de `#masthead`. [B]

---

## 2. Titre du site (logo texte)

Le titre affiché est `get_bloginfo('name')`, c'est-à-dire l'option `blogname`, ici « Pascal Dupont ». HTML [B] :
- bureau : `div.site-branding.branding-layout-standard > a.brand[rel=home] > div.site-title-wrap > p.site-title` ;
- mobile : `div.site-branding.mobile-site-branding… > a.brand > div.site-title-wrap > div.site-title`, avec en plus `.vs-md-false` quand `logo_layout.include.tablet` est vide (valeur par défaut, voir le piège ci-dessous).

Le lien `a.brand` **entoure** le titre : le sélecteur `.site-title a` ne trouve donc rien.

| Clé | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `logo_layout` | objet | `{"include":{"desktop":…,"tablet":…,"mobile":…},"layout":{…}}`. Valeurs de `include` dans l'interface : `logo_only`, `logo_title`, `logo_title_tagline`. Le code cherche seulement les mots `logo`, `title` et `tagline` : `"title"` seul fonctionne aussi. `layout` : `standard`, `title_logo`, `top_logo_title`, `top_title_logo` ; avec slogan : `title_tag_logo`, `top_logo_title_tag`, `top_title_tag_logo`, `top_title_logo_tag`. **Piège** : `include.tablet = ""` masque le titre de l'en-tête mobile entre 720 et 1024 px (classe `vs-md-false`, § 0 point 10). Un `include.mobile` non vide **sans** `title` ajoute `vs-sm-false`, qui masque le titre jusqu'à 719 px. Un `logo_layout` **partiel**, sans la clé `include.tablet`, produit en plus à chaque page un `PHP Warning: Undefined array key "tablet"` et un `Deprecated: strpos()` (`header-functions.php`, ligne 482) [B, contre-vérification]. | `{"include":{"mobile":"","tablet":"","desktop":"logo_title"},"layout":{"mobile":"","tablet":"","desktop":"standard"}}` | sans image de logo (`custom_logo` vide), `logo_title` et `title` donnent le même HTML : le titre seul | B (`logo_title`, `title`, piège de la tablette et sa correction : titre visible à 1280, 900, 800, 720 et 390 px) ; C (autres mises en page, `vs-sm-false`) |
| `brand_typography` | objet typo | `{"size":{"desktop":n,"tablet":n,"mobile":n},"sizeType":"px\|rem\|em","lineHeight":{"desktop":n,…},"lineType":"" ,"letterSpacing":{"desktop":n},"spacingType":"em","family":"…","google":false,"weight":"400","variant":"","color":"…"}` | `{"size":{"desktop":26},"lineHeight":{"desktop":1.2},"family":"inherit","google":false,"weight":"700","variant":"700","color":"palette3"}` | `.site-branding .site-title{…}` ; tailles tablette et mobile en media query | B |
| `brand_typography_color` | objet | `{"hover":"…","active":"…"}`. `active` ne s'applique que sur la page d'accueil (`body.home .site-branding .site-title`). | `{"hover":"","active":""}` | `.site-branding .site-title:hover` | B (règles écrites) ; C (`body.home`, la page d'essai n'est pas l'accueil) |
| `brand_tag_typography` | objet typo | même format ; slogan `.site-description`, affiché seulement si `include` contient `tagline` | `{"size":{"desktop":16},…,"weight":"700","color":"palette5"}` | `.site-branding .site-description` | C |
| `header_logo_padding` | objet | `{"size":{"desktop":[h,d,b,g]},"unit":{"desktop":"px"},"locked":{"desktop":false}}` | vides | `.site-branding{padding:…}` | B (rendu `0px 0px 0px 0px` par défaut) |
| `custom_logo`, `use_logo_icon`, `logo_width` | id d'image, bool, objet | non utilisés ici (titre texte) | `custom_logo` vide, `use_logo_icon:false` | — | C |

Détails de `brand_typography` [B] :
- `family` : une valeur sans espace ni virgule est écrite telle quelle. `"var(--display)"` donne `font-family:var(--display)`, soit Newsreader, la police embarquée du thème enfant. D'après le code [C], une valeur avec espace et sans virgule, comme `Hanken Grotesk`, est mise entre apostrophes. `"inherit"` n'écrit aucune `font-family`. Garder **`"google": false`** pour ne charger aucune police Google.
- `sizeType` vaut pour **tous** les paliers : `"rem"` avec `size.mobile = 1.2` donne `@media (max-width:767px){.site-branding .site-title{font-size:1.2rem;}}`.
- `lineHeight` est **sans unité** si `lineType` est vide ou vaut `"-"`, sur les trois paliers. Essai : `lineHeight.mobile = 1.1` donne `line-height:1.1`, mesuré 21,12 px pour 19,2 px.
- `letterSpacing` avec `spacingType:"em"` : `0.01` donne `letter-spacing:0.01em`.
- `weight` est une **chaîne** (`"400"`).

Extrait testé (mesuré : Newsreader, 21,6 px, graisse 400, interligne 25,92 px, approche 0,216 px, couleur rgb(232,230,225) ; 19,2 px à 390 px) :

```json
{"logo_layout": {"include":{"mobile":"logo_title","tablet":"logo_title","desktop":"logo_title"},"layout":{"mobile":"","tablet":"","desktop":"standard"}},
 "brand_typography": {"size":{"desktop":1.35,"tablet":"","mobile":1.2},"sizeType":"rem","lineHeight":{"desktop":1.2},
   "letterSpacing":{"desktop":0.01},"spacingType":"em","family":"var(--display)","google":false,"weight":"400","variant":"","color":"#e8e6e1"},
 "brand_typography_color": {"hover":"#e8e6e1","active":"#e8e6e1"}}
```

---

## 3. Rangée principale : hauteur, largeur, fond, bordures

| Clé | Type | Format | Défaut | CSS produit | Vérif. |
|---|---|---|---|---|---|
| `header_main_height` | objet | `{"size":{"mobile":n,"tablet":n,"desktop":n},"unit":{"mobile":"px","tablet":"px","desktop":"px"}}` ; unités `px`, `em`, `rem`, `vh` | `size.desktop = 80`, les autres vides | `.site-main-header-inner-wrap{min-height:…}` (+ media query) | B : 76 px au bureau, 64 px à 390 px |
| `header_main_layout` | objet | `{"desktop":"standard\|fullwidth\|contained","tablet":"","mobile":""}` | `desktop: "standard"` | classe `site-header-row-layout-{valeur}` | B : à 1700 px, `standard` donne un contenu de 1242 px (largeur de contenu du site) et `fullwidth` 1652 px |
| `header_main_padding` | objet | `{"size":{"desktop":[h,d,b,g]},"unit":{"desktop":"px"},"locked":{"desktop":false}}` | vides | `.site-main-header-wrap .site-header-row-container-inner>.site-container{padding:…}` | C |
| `header_wrap_background` | objet fond | `{"desktop":{"color":"…"}}` (+ `tablet`, `mobile`) | **`{"desktop":{"color":"#ffffff"}}`** | `#masthead`, **et aussi la rangée une fois collée** : `#masthead .kadence-sticky-header.item-is-fixed:not(.item-at-start) > .site-header-row-container-inner` | B |
| `header_main_background` | objet fond | `{"desktop":{"color":"rgba(13,18,23,0.92)"}}` ; avec `"type":"image"` ou `"gradient"`, voir `site_background` dans `theme-reglages.md` | `{"desktop":{"color":""}}` | `.site-main-header-wrap .site-header-row-container-inner{background:…}`. Cette règle vise **aussi la rangée de l'en-tête mobile**. | B (couleur) ; C (image, dégradé) |
| `header_main_bottom_border` | objet bordure | `{"desktop":{"width":1,"unit":"px","style":"solid","color":"#2c3a49"},"tablet":{…},"mobile":{…}}` ; `style` : `none`, `solid`, `dashed`, `dotted`, `double` | `[]` | `.site-main-header-wrap .site-header-row-container-inner{border-bottom:1px solid #2c3a49;}` | B (bureau ; mobile `3px solid #c0403d` constaté à 390 px) |
| `header_main_top_border` | objet bordure | idem | `[]` | `border-top` | C |
| `header_main_trans_background` | objet fond | fond de la rangée quand l'en-tête est transparent | vide | `.transparent-header #masthead .site-main-header-wrap …` | C |
| `header_top_*`, `header_bottom_*` | idem | mêmes clés pour les rangées haute et basse (`_height`, `_layout`, `_background`, `_top_border`, `_bottom_border`, `_padding`) | `height.desktop = 0` | `.site-top-header-wrap …`, `.site-bottom-header-wrap …` | C (B : affichage de la rangée basse) |

- **Fond et bordure** : toujours les mettre sur la rangée (`header_main_*`). `#masthead` est **blanc par défaut** : sous une rangée à 92 %, cela donne un gris clair, et une fois l'en-tête collé la rangée devient blanche (§ 4). Mettre `header_wrap_background` à `#0d1217`. [B]
- Pour la bordure, le contrôle « Border » de l'interface (`header_main_border`) écrit en réalité **deux** theme_mods : `header_main_top_border` et `header_main_bottom_border`. [C]

Extrait testé (mesuré : fond `rgba(13, 18, 23, 0.92)`, bordure `1px solid rgb(44, 58, 73)`, hauteur minimale 76 px puis 64 px) :

```json
{"header_wrap_background": {"desktop":{"color":"#0d1217"}},
 "header_main_background": {"desktop":{"color":"rgba(13,18,23,0.92)"}},
 "header_main_bottom_border": {"desktop":{"width":1,"unit":"px","style":"solid","color":"#2c3a49"}},
 "header_main_height": {"size":{"mobile":64,"tablet":"","desktop":76},"unit":{"mobile":"px","tablet":"px","desktop":"px"}},
 "header_main_layout": {"mobile":"","tablet":"","desktop":"standard"}}
```

---

## 4. En-tête collant

| Clé | Type | Valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `header_sticky` | string | `no`, `main`, `top_main`, `top_main_bottom`, `top`, `bottom` | `"no"` | classe `kadence-sticky-header` sur la rangée choisie. Avec `main`, c'est `.site-main-header-wrap`. Avec `top_main`, c'est `.site-header-upper-inner-wrap`. Avec `top_main_bottom`, c'est `.site-header-inner-wrap`. | B (`main`, `top_main`, `no`) |
| `mobile_header_sticky` | string | mêmes valeurs, en-tête mobile | `"no"` | idem dans `#mobile-header` | B (`main`, `no`) |
| `header_sticky_background` | objet fond | `{"desktop":{"color":"…"}}` | vide | rangée collée : `#masthead .kadence-sticky-header.item-is-fixed:not(.item-at-start):not(.item-hidden-above) > .site-header-row-container-inner` | B |
| `header_sticky_shrink` + `header_sticky_main_shrink` | bool + objet | `{"size":56,"unit":"px"}`. **`unit` est ignoré** : seul `size` est transmis au script (`data-shrink-height="56"`) et il est toujours lu en px. | `false`, `{"size":60,"unit":"px"}` | la rangée collée descend à cette hauteur | B : 76 → 56 px après défilement ; contre-vérification : 56 px aussi avec `"unit":"em"` |
| `mobile_header_sticky_shrink`, `mobile_header_sticky_main_shrink` | idem | mobile | `false`, 60 px | | C |
| `header_reveal_scroll_up`, `mobile_header_reveal_scroll_up` | bool | l'en-tête ne réapparaît qu'en remontant | `false` | attribut `data-reveal-scroll-up` | C |
| `header_sticky_bottom_border` | objet bordure | `{"desktop":{…}}` | `[]` | `border-bottom` de la rangée collée | C |
| `header_sticky_box_shadow` | objet ombre | `{"color":"…","hOffset":0,"vOffset":0,"blur":0,"spread":0,"inset":false}` | ombre transparente | | C |
| `header_sticky_site_title_color`, `header_sticky_navigation_color` (`color`/`hover`/`active`), `header_sticky_navigation_background`, `header_sticky_logo`, `header_sticky_custom_logo` | | couleurs et logo propres à l'état collé | vides | | C |

Fonctionnement [B] :
- PHP pose `kadence-sticky-header`. Le script `navigation.min.js` ajoute `item-is-fixed` puis `item-at-start` en haut de page, et `item-is-stuck` après défilement. Il ajoute aussi `child-is-fixed` au parent. La rangée est en `position: fixed; top: 0` **dès le haut de page**. Kadence ne charge la version allégée `navigation-lite.min.js` que si `header_sticky` et `mobile_header_sticky` valent `no` et que `enable_scroll_to_id` et `scroll_up` sont faux [C]. Or `enable_scroll_to_id` vaut `true` par défaut : `navigation.min.js` était chargé dans tous les essais [B].
- **Piège du fond** : la règle de `header_wrap_background` (blanc par défaut) vise aussi la rangée collée, avec une spécificité (1,4,0) plus forte que celle de `header_main_background` (0,2,0). Mesures après un défilement de 400 px :
  - `header_wrap_background` par défaut : rangée **blanche** `rgb(255,255,255)` ;
  - `header_wrap_background` à `transparent`, sans `header_sticky_background` : rangée **transparente** ;
  - `header_sticky_background` à `rgba(13,18,23,0.92)` : rangée `rgba(13, 18, 23, 0.92)`. Sa règle (1,5,0) l'emporte.
  → **Avec un en-tête collant, toujours remplir `header_sticky_background`.**
- **Piège CSS** : un `backdrop-filter`, un `filter` ou un `transform` sur un **ancêtre** de la rangée (`#masthead`, `.site-header-upper-wrap`…) la fait défiler avec la page. C'est le cas avec `pd-kadence.css` actuel (§ 9.3).

```json
{"header_sticky":"main","mobile_header_sticky":"main","header_sticky_shrink":false,"header_reveal_scroll_up":false,
 "header_sticky_background":{"desktop":{"color":"rgba(13,18,23,0.92)"}}}
```

---

## 5. Menu principal (bureau)

HTML [B] : `div.site-header-item.site-header-item-main-navigation > nav#site-navigation.main-navigation.header-navigation.hover-to-open.nav--toggle-sub.header-navigation-style-{style}.header-navigation-dropdown-animation-{…} > div.primary-menu-container.header-menu-container > ul#primary-menu.menu > li.menu-item(.current-menu-item) > a`.

| Clé | Type | Format / valeurs | Défaut | CSS produit | Vérif. |
|---|---|---|---|---|---|
| `primary_navigation_color` | objet | `{"color":…,"hover":…,"active":…}` | `{"color":"palette5","hover":"palette-highlight","active":"palette3"}` | `.main-navigation .primary-menu-container > ul > li.menu-item > a{color}` ; `…> a:hover` ; `…> li.menu-item.current-menu-item > a` | B : `#a9b6c0`, survol `#e8e6e1`, actif `#e8e6e1` ; `palette5` donne `var(--global-palette5)` |
| `primary_navigation_background` | objet | même format | vides | `background` sur les mêmes sélecteurs | C (vides écrits, pas de règle) |
| `primary_navigation_typography` | objet typo | `{"size":{"desktop":n},"sizeType":"rem","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"400","variant":""}` | `{"size":{"desktop":""},…,"family":"inherit"}` | `.main-navigation .primary-menu-container > ul li.menu-item > a{font-weight;font-size}`. Une `family` non `inherit` devient `font-family:var(--global-primary-nav-font-family)`, variable définie dans `:root` (elle vaut `inherit` avec `"family":"inherit"`). | B : 0,95 rem = 15,2 px, graisse 400, `--global-primary-nav-font-family:inherit` ; C (autre `family`) |
| `primary_navigation_spacing` | objet | `{"size":1.4,"unit":"em"}` ; unités `px`, `em`, `rem`, `vw` | `{"size":1.2,"unit":"em"}` | **marge intérieure gauche et droite = la moitié** : `padding-left:calc(1.4em / 2)` | B : 10,64 px pour 15,2 px |
| `primary_navigation_vertical_spacing` | objet | `{"size":0.6,"unit":"em"}` | `{"size":0.6,"unit":"em"}` | `padding-top` et `padding-bottom` entiers, **seulement** avec les styles `standard` et `underline` | B : 9,12 px |
| `primary_navigation_style` | string | `standard`, `fullheight`, `underline`, `underline-fullheight` | `"standard"` | classe `header-navigation-style-{valeur}`. `underline` : trait `::after` de 2 px, couleur `currentColor`, déployé au survol et sur la page courante | B (`standard`, `underline` : `::after` de 2 px en `rgb(192,64,61)` sur l'élément actif) |
| `primary_navigation_stretch`, `primary_navigation_fill_stretch` | bool | menu étiré sur la largeur disponible | `false` | classes `header-navigation-layout-stretch-…` | C (classes `-false` vues en B) |
| `primary_navigation_open_type` | string | `hover`, `click` (sous-menus) ; lu directement par `get_theme_mod` | `"hover"` | classe `hover-to-open` ou `click-to-open` | C (`hover-to-open` vu en B) |
| `primary_navigation_parent_active` | bool | le parent d'une page active est aussi marqué actif | `false` | sinon, seul `li.current-menu-item` est coloré | C |
| `dropdown_navigation_*` | | sous-menus : `_color`, `_background`, `_typography`, `_width`, `_vertical_spacing`, `_divider`, `_shadow`, `_border_radius`, `_reveal`. Défauts clairs (`background` en `palette3`). | | `.header-navigation .header-menu-container ul ul …` | C (le menu du site n'a pas de sous-menu) |
| `secondary_navigation_*` | | mêmes clés pour l'élément `navigation-2` (emplacement `secondary`) | | | C |

```json
{"primary_navigation_style":"standard",
 "primary_navigation_spacing":{"size":1.4,"unit":"em"},
 "primary_navigation_vertical_spacing":{"size":0.6,"unit":"em"},
 "primary_navigation_color":{"color":"#a9b6c0","hover":"#e8e6e1","active":"#e8e6e1"},
 "primary_navigation_background":{"color":"","hover":"","active":""},
 "primary_navigation_typography":{"size":{"desktop":0.95},"sizeType":"rem","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"400","variant":""}}
```

---

## 6. Mobile : bouton, tiroir, menu mobile

HTML [B] :

```
#mobile-header … div.site-header-item-navgation-popup-toggle > div.mobile-toggle-open-container
  > button#mobile-toggle.menu-toggle-open.drawer-toggle.menu-toggle-style-{default|bordered}[aria-expanded]
    > (span.menu-toggle-label) span.menu-toggle-icon > span.kadence-svg-iconset > svg
div#mobile-drawer.popup-drawer.popup-drawer-layout-{sidepanel|fullwidth}.popup-drawer-animation-{fade|scale|slice}.popup-drawer-side-{right|left}
  > div.drawer-overlay + div.drawer-inner
    > div.drawer-header > button.menu-toggle-close.drawer-toggle > span.toggle-close-bar ×2
    > div.drawer-content.mobile-drawer-content.content-align-{…}.content-valign-{…}
      > div.site-header-item-mobile-navigation > nav#mobile-site-navigation.mobile-navigation.drawer-navigation
        > div.mobile-menu-container.drawer-menu-container > ul#mobile-menu.menu.has-collapse-sub-nav > li > a
```

(`navgation` est bien la faute de frappe du thème, à recopier telle quelle.) À l'ouverture, `#mobile-drawer` reçoit `show-drawer active pop-animated`, et `body` la classe `showing-popup-drawer-from-right`. [B]

### 6.1 Bouton (`popup-toggle`)

| Clé | Type | Valeurs | Défaut | CSS / effet | Vérif. |
|---|---|---|---|---|---|
| `mobile_trigger_color` | objet | `{"color":…,"hover":…}` | `{"color":"palette5","hover":"palette-highlight"}` | `.mobile-toggle-open-container .menu-toggle-open{color}` ; `:hover, :focus-visible` | B : `#e8e6e1`, survol `#c0403d` |
| `mobile_trigger_background` | objet | idem | vides | `background` | C |
| `mobile_trigger_icon` | string | `menu`, `menu2`, `menu3` | `"menu"` | icône SVG | B (`menu`) |
| `mobile_trigger_icon_size` | objet | `{"size":24,"unit":"px"}` | `{"size":20,"unit":"px"}` | `.menu-toggle-open .menu-toggle-icon{font-size}` | B : 24 px |
| `mobile_trigger_style` | string | `default`, `bordered` | `"default"` | classe `menu-toggle-style-…` ; `bordered` utilise `mobile_trigger_border` | B (`bordered` : `1px solid` constaté) |
| `mobile_trigger_border` | objet | `{"width":1,"unit":"px","style":"solid","color":"currentColor"}` (non responsive) | celui-ci | | B |
| `mobile_trigger_label` | string | texte à côté de l'icône (`span.menu-toggle-label`) | `""` | | B (« Menu ») |
| `mobile_trigger_typography`, `mobile_trigger_padding` | typo, mesure | `{"size":[0.4,0.6,0.4,0.6],"unit":"em","locked":false}` | 14 px ; 0,4 em × 0,6 em | | B (valeurs par défaut rendues) |

### 6.2 Tiroir (`header_popup_*`)

| Clé | Type | Valeurs | Défaut | CSS / effet | Vérif. |
|---|---|---|---|---|---|
| `header_popup_layout` | string | `sidepanel` (panneau latéral), `fullwidth` (plein écran) | `"sidepanel"` | classe `popup-drawer-layout-…` | B : `sidepanel` = 351 px à 390 px (largeur max 90 %) ; `fullwidth` = 390 px |
| `header_popup_side` | string | `right`, `left` | `"right"` | `popup-drawer-side-…` | B (`right`) |
| `header_popup_animation` | string | `fade`, `scale`, `slice` | `"fade"` | `popup-drawer-animation-…` | B (`fade`) |
| `header_popup_background` | objet fond | `{"desktop":{"color":"#17202a"}}` (+ `tablet`, `mobile`) | `{"desktop":{"color":""}}`, alors fond du thème `#090c10` | `#mobile-drawer .drawer-inner{background}` | B : rgb(23,32,42) |
| `header_popup_width` | objet | `{"size":{"mobile":…,"tablet":…,"desktop":…},"unit":{…}}`, seulement en `sidepanel` | vides (100 %, max 90 %) | `width` de `.drawer-inner` | C |
| `header_popup_content_align` | string | `left`, `center`, `right` | `"left"` | `.drawer-content.content-align-…` | B (`center` : `text-align:center`) |
| `header_popup_vertical_align` | string | `top`, `middle`, `bottom` | `"top"` | `content-valign-…` | B (`top`) |
| `header_popup_close_color` | objet | `{"color":…,"hover":…}` | vides | `#mobile-drawer .drawer-header .drawer-toggle{color}` | B : `#e8e6e1` |
| `header_popup_close_background`, `header_popup_close_icon_size` (`{"size":"24","unit":"px"}`), `header_popup_close_padding` | | | | | B (taille 24 px et marge 0,6 em × 0,15 em par défaut rendues) ; C (fond) |

### 6.3 Menu dans le tiroir (`mobile-navigation`)

| Clé | Type | Format | Défaut | CSS | Vérif. |
|---|---|---|---|---|---|
| `mobile_navigation_color` | objet | `{"color","hover","active"}` | `{"color":"palette8","hover":"","active":"palette-highlight"}` | `.mobile-navigation ul li > a{color}` ; `li.current-menu-item > a` | B : `#e8e6e1`, actif `#c0403d` |
| `mobile_navigation_background` | objet | idem | vides | | C |
| `mobile_navigation_divider` | objet bordure | `{"width":1,"unit":"px","style":"solid","color":"#2c3a49"}` | `rgba(255,255,255,0.1)` | `border-bottom` de chaque lien | B |
| `mobile_navigation_typography` | objet typo | `{"size":{"desktop":17},"sizeType":"px",…}` | 14 px | `.mobile-navigation ul li{font-size}` | B : 17 px |
| `mobile_navigation_vertical_spacing` | objet | `{"size":0.9,"unit":"em"}` | `{"size":1,"unit":"em"}` | `padding-top` et `padding-bottom` des liens | B : 15,3 px |
| `mobile_navigation_collapse`, `mobile_navigation_parent_toggle` | bool | sous-menus repliables, parent cliquable | `true`, `false` | classe `has-collapse-sub-nav`, `drawer-navigation-parent-toggle-…` | B (classes) ; C (comportement) |

### 6.4 Seuil bureau / mobile

| Clé | Type | Format | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `header_mobile_switch` | objet | `{"size":900,"unit":"px"}` (`unit` non utilisé : valeur en px) | `{"size":"","unit":"px"}` = 1024/1025 | en dessous de `size`, l'en-tête mobile est affiché : bureau à partir de `size` px, mobile jusqu'à `size − 1` px. Effet de bord [C] : la media query « tablette » de **tout** le CSS d'en-tête devient `(max-width: size−1px)` (hauteurs, fonds, bordures `tablet` de l'en-tête). | B : avec 900, bureau à 1000 px et mobile à 880 px ; contre-vérification : bureau à 900 px, mobile à 899 px, CSS `@media all and (max-width: 899px)` et `(min-width: 900px)` |

```json
{"mobile_trigger_icon":"menu","mobile_trigger_style":"default","mobile_trigger_label":"",
 "mobile_trigger_icon_size":{"size":24,"unit":"px"},
 "mobile_trigger_color":{"color":"#e8e6e1","hover":"#c0403d"},"mobile_trigger_background":{"color":"","hover":""},
 "header_popup_layout":"sidepanel","header_popup_side":"right","header_popup_animation":"fade",
 "header_popup_background":{"desktop":{"color":"#17202a"}},
 "header_popup_close_color":{"color":"#e8e6e1","hover":"#c0403d"},
 "mobile_navigation_color":{"color":"#e8e6e1","hover":"#c8b287","active":"#c0403d"},
 "mobile_navigation_background":{"color":"","hover":"","active":""},
 "mobile_navigation_divider":{"width":1,"unit":"px","style":"solid","color":"#2c3a49"},
 "mobile_navigation_typography":{"size":{"desktop":17},"sizeType":"px","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":""},
 "mobile_navigation_vertical_spacing":{"size":0.9,"unit":"em"}}
```

---

## 7. Pied de page : structure et rangées

### 7.1 `footer_items`

| | |
|---|---|
| Type | objet : rangée → colonne → liste d'identifiants |
| Rangées | `top`, `middle`, `bottom` |
| Colonnes | `{rangée}_1` à `{rangée}_5` |
| Éléments | `footer-html` (copyright), `footer-navigation` (menu `footer`), `footer-social`, `footer-widget1` à `footer-widget6`. Fichier chargé : `template-parts/footer/{identifiant}.php`. |
| Défaut | `{"top":{…[]},"middle":{…[]},"bottom":{"bottom_1":["footer-html"],"bottom_2":[],…}}` |
| Vérif. | B |

- Une rangée est affichée dès qu'une de ses 5 colonnes contient un élément. [B]
- **Seules les `footer_{rangée}_columns` premières colonnes sont rendues.** Essai avec `footer_bottom_columns: "1"` et `bottom_2: ["footer-navigation"]` : le menu du pied **n'apparaît pas**. [B] → Mettre `footer_bottom_columns` au nombre de colonnes utilisées.

```json
{"footer_items": {
  "top":    {"top_1":[],"top_2":[],"top_3":[],"top_4":[],"top_5":[]},
  "middle": {"middle_1":[],"middle_2":[],"middle_3":[],"middle_4":[],"middle_5":[]},
  "bottom": {"bottom_1":["footer-html"],"bottom_2":["footer-navigation"],"bottom_3":[],"bottom_4":[],"bottom_5":[]}
},
 "footer_bottom_columns": "2"}
```

### 7.2 Réglages d'une rangée (`footer_bottom_*` ; mêmes clés en `footer_top_*` et `footer_middle_*`)

| Clé | Type | Format / valeurs | Défaut (bas) | CSS / effet | Vérif. |
|---|---|---|---|---|---|
| `footer_bottom_columns` | **string** | `"1"` à `"5"` (un entier `2` fonctionne aussi : le gabarit applique `absint()`) | `"1"` (haut et milieu : `"3"`) | classe `site-footer-row-columns-N` | B (contre-vérification : entier `2` → 2 colonnes, menu rendu) |
| `footer_bottom_layout` | objet | `{"desktop":…,"tablet":…,"mobile":…}`. Avec 2 colonnes : `equal`, `left-golden` (2/3, 1/3), `right-golden`, et `row` (empilé) en tablette ou mobile. Avec 3 colonnes : `equal`, `left-half`, `right-half`, `center-half`, `center-wide`, et en tablette ou mobile aussi `first-row`, `last-row`. Avec 4 colonnes : `equal`, `left-forty`, `right-forty`, et `two-grid` en tablette ou mobile [C, `footer.min.css`]. Avec 1 colonne : `row`. | `{"mobile":"row","tablet":"","desktop":"row"}` | classes `site-footer-row-column-layout-…`, `-tablet-column-layout-…`, `-mobile-column-layout-…` | B |
| `footer_bottom_contain` | objet | `standard`, `fullwidth`, `contained` par palier | `desktop: "standard"` | `site-footer-row-layout-…` | B : 1242 px (`standard`) ou 1652 px (`fullwidth`) à 1700 px |
| `footer_bottom_top_spacing`, `footer_bottom_bottom_spacing` | objet | `{"size":{"mobile":"","tablet":"","desktop":24},"unit":{…"px"}}` | `"30"` | `.site-bottom-footer-inner-wrap{padding-top;padding-bottom}` | B (24 px écrits) |
| `footer_bottom_column_spacing` | objet | idem | `"30"` | `grid-column-gap` **seulement** pour la rangée basse (les rangées `top` et `middle` écrivent aussi `grid-row-gap`). Conséquence : une fois les colonnes empilées (mobile `row`, ou tablette `""`), la valeur `mobile`/`tablet` n'a **aucun effet visible**. Les deux blocs empilés se touchent (écart mesuré 0 px, avec 8 comme avec 40). Pour espacer des colonnes empilées, passer par du CSS. | B (30 px ; `column-gap: 8px` en mobile, sans effet visible) |
| `footer_bottom_widget_spacing`, `footer_bottom_height` | objet | idem | 30 ; vide | `.widget{margin-bottom}` ; `min-height` | B (30 écrit) ; C |
| `footer_bottom_background` | objet fond | `{"desktop":{"color":"#0d1217"}}` | vide | `.site-bottom-footer-wrap .site-footer-row-container-inner{background}` | B |
| `footer_bottom_top_border`, `footer_bottom_bottom_border` | objet bordure | `{"desktop":{"width":1,"unit":"px","style":"solid","color":"#2c3a49"}}` | `[]` | `border-top`, `border-bottom` sur la même règle | B (haut) ; C (bas) |
| `footer_bottom_column_border` | objet bordure | séparateur vertical entre colonnes | `[]` | `.site-footer-section:not(:last-child):after` | C |
| `footer_bottom_widget_content` | objet typo **avec `color`** | `{"size":{"desktop":14},"sizeType":"px",…,"color":"#a9b6c0"}` | vide | `font-size` et `color` de la rangée | B : 14 px, rgb(169,182,192) |
| `footer_bottom_widget_title` | objet typo | titres de widgets | vide | | C |
| `footer_bottom_link_colors` | objet | `{"color":…,"hover":…}` (**absent des valeurs par défaut** de Kadence) | — | `.site-footer .site-bottom-footer-wrap a:where(:not(.button)…){color}` | B (règle écrite) |
| `footer_bottom_link_style` | string | `plain` (soulignement au survol), `normal` (toujours souligné), `noline` (jamais souligné) | `"plain"` | classe `ft-ro-lstyle-…` sur la grille ; vise **tous** les liens de la rangée, menu du pied compris | B (classe). Contre-vérification : `normal` souligne aussi les liens de `footer-navigation` ; `noline` retire le soulignement du copyright même avec `footer_html_link_style: "normal"` |
| `footer_bottom_direction`, `footer_bottom_collapse` | objet, string | `row` ou `column` ; `normal` ou `rtl` (ordre une fois empilé) | `row`, `normal` | `ft-ro-dir-…`, `ft-ro-collapse-…` | C (classes par défaut vues) |
| `footer_wrap_background` | objet fond | `{"desktop":{"color":"#0d1217"}}` | `{"desktop":{"color":""}}` | `#colophon{background}` | B |

- **Tablette** : avec `tablet: ""` (défaut), la classe `site-footer-row-tablet-column-layout-default` **empile les colonnes**. Mesuré à 900 px : `grid-template-columns: 852px`. Avec `"tablet":"equal"` : `411px 411px`. [B]
- **Mobile** `row` : colonnes empilées. Mesuré à 390 px : `342px`. [B]
- Ces classes de colonnes viennent de la feuille statique `footer.min.css`, dont les seuils sont **720–1024 px** (tablette) et **≤ 719 px** (mobile). Ce ne sont pas les seuils du CSS calculé (≤ 767 px). [C]

```json
{"footer_bottom_layout":{"mobile":"row","tablet":"equal","desktop":"equal"},
 "footer_bottom_contain":{"mobile":"","tablet":"","desktop":"standard"},
 "footer_bottom_top_spacing":{"size":{"mobile":"","tablet":"","desktop":24},"unit":{"mobile":"px","tablet":"px","desktop":"px"}},
 "footer_bottom_bottom_spacing":{"size":{"mobile":"","tablet":"","desktop":24},"unit":{"mobile":"px","tablet":"px","desktop":"px"}},
 "footer_bottom_column_spacing":{"size":{"mobile":8,"tablet":"","desktop":30},"unit":{"mobile":"px","tablet":"px","desktop":"px"}},
 "footer_wrap_background":{"desktop":{"color":"#0d1217"}},
 "footer_bottom_background":{"desktop":{"color":"#0d1217"}},
 "footer_bottom_top_border":{"desktop":{"width":1,"unit":"px","style":"solid","color":"#2c3a49"}},
 "footer_bottom_widget_content":{"size":{"desktop":14},"sizeType":"px","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":"","color":"#a9b6c0"},
 "footer_bottom_link_colors":{"color":"#a9b6c0","hover":"#e8e6e1"}}
```

---

## 8. Copyright et menu du pied

### 8.1 Copyright : élément `footer-html`

| Clé | Type | Format | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `footer_html_content` | string (HTML) | balises `{copyright}` → `&copy;`, `{year}` → année (`date_i18n('Y')`), `{site-title}` → `blogname`, `{theme-credit}` → « - Theme WordPress par <a>Kadence WP</a> » (lien `rel="nofollow noopener"`). Puis `wpautop()` et `do_shortcode()`. | `"{copyright} {year} {site-title} {theme-credit}"` | `div.footer-html > div.footer-html-inner > <p>…</p>` | B |
| `footer_html_align` | objet | `{"desktop":"left\|center\|right","tablet":"","mobile":"center"}` (**absent des valeurs par défaut** : `default`) | — | classes `content-align-…`, `content-tablet-align-…`, `content-mobile-align-…` sur `.site-info` | B : `text-align:left` à 1280 et 900 px, `center` à 390 px |
| `footer_html_vertical_align` | objet | `top`, `middle`, `bottom` par palier (absent des défauts) | — | `content-valign-…` | B (classe) |
| `footer_html_typography` | objet typo + `color` | `{"size":{"desktop":14},"sizeType":"px",…,"color":"#a9b6c0"}` | vide | `#colophon .footer-html{font-size;color}` | B |
| `footer_html_link_color` | objet | `{"color","hover"}` | vides | `#colophon … .footer-html a` | C |
| `footer_html_link_style` | string | `normal` (liens soulignés), `plain` | `"normal"` | classe `inner-link-style-…` | B (classe) ; C (soulignement : `assets/css/footer.min.css`) |
| `footer_html_margin` | objet mesure | `{"size":[h,d,b,g],"unit":"px","locked":false}` | vide (le thème donne `margin:1em 0`) | | B (marge du thème : 14 px) |

Essais [B] :
- `"{copyright} {year} {site-title}"` donne `<p>© 2026 Pascal Dupont</p>`.
- `"{copyright} {year} {site-title} {theme-credit} · <a href=\"/mentions-legales/\">Mentions</a> [ep_test]\nLigne 2"` donne `<p>© 2026 Pascal Dupont - Theme WordPress par <a href="https://www.kadencewp.com/" rel="nofollow noopener">Kadence WP</a> · <a href="/mentions-legales/">Mentions</a> [ep_test]<br>\nLigne 2</p>`. Le HTML est conservé, un code court inconnu reste en clair et un saut de ligne devient `<br>`.
- Valeur par défaut (site partagé) : « © 2026 Pascal Dupont - Theme WordPress par Kadence WP ». [T]
- **Piège (contre-vérification [B])** : `"footer_html_content": ""` ne vide **pas** le copyright. `kadence()->option()` traite `''` comme absent et renvoie la valeur par défaut, crédit Kadence compris. Pour supprimer le bloc, retirer `footer-html` de `footer_items`.

### 8.2 Menu du pied : élément `footer-navigation`, emplacement `footer`

HTML [B] : `div.footer-widget-area.widget-area.footer-navigation-wrap.content-align-…  > div.footer-navigation-inner > nav#footer-navigation.footer-navigation > div.footer-menu-container > ul#footer-menu.menu > li.menu-item > a`. La profondeur est limitée à 1 (`depth = 1`, pas de sous-menu). [C]

| Clé | Type | Format | Défaut | CSS | Vérif. |
|---|---|---|---|---|---|
| `footer_navigation_color` | objet | `{"color","hover","active"}` | `{"color":"palette5","hover":"palette-highlight","active":"palette3"}` | `#colophon .footer-navigation .footer-menu-container > ul > li > a{color}` ; `ul li a:hover` ; `ul li.current-menu-item > a` | B : `#a9b6c0`, survol `#e8e6e1` |
| `footer_navigation_background` | objet | idem | vides | | C |
| `footer_navigation_spacing` | objet | `{"size":1.2,"unit":"em"}` | 1,2 em | `padding-left` et `padding-right` = **moitié** (`calc(1.2em / 2)`) | B : 8,4 px |
| `footer_navigation_vertical_spacing` | objet | `{"size":0.6,"unit":"em"}` | 0,6 em | `padding-top` et `padding-bottom` = **moitié** aussi (contrairement au menu principal) | B : 4,2 px |
| `footer_navigation_typography` | objet typo | `{"size":{"desktop":14},"sizeType":"px",…}` | vide | `#colophon .footer-navigation .footer-menu-container > ul li a{font-size}` | B : 14 px |
| `footer_navigation_align` | objet | `left`, `center`, `right` par palier (absent des défauts) | — | `content-align-…` ; `.footer-navigation .menu{justify-content}` | B : `flex-end` au bureau, `center` à 390 px |
| `footer_navigation_vertical_align` | objet | `top`, `middle`, `bottom` | — | `content-valign-…` | B (classe) |
| `footer_navigation_stretch` | bool | liens répartis sur la largeur | `false` | `footer-navigation-layout-stretch-…` | B (classe `-false`) |

```json
{"footer_html_content":"{copyright} {year} {site-title}",
 "footer_html_align":{"mobile":"center","tablet":"","desktop":"left"},
 "footer_html_vertical_align":{"mobile":"","tablet":"","desktop":"middle"},
 "footer_html_typography":{"size":{"desktop":14},"sizeType":"px","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":"","color":"#a9b6c0"},
 "footer_html_link_style":"plain",
 "footer_navigation_align":{"mobile":"center","tablet":"","desktop":"right"},
 "footer_navigation_vertical_align":{"mobile":"","tablet":"","desktop":"middle"},
 "footer_navigation_spacing":{"size":1.2,"unit":"em"},
 "footer_navigation_vertical_spacing":{"size":0.6,"unit":"em"},
 "footer_navigation_color":{"color":"#a9b6c0","hover":"#e8e6e1","active":"#e8e6e1"},
 "footer_navigation_background":{"color":"","hover":"","active":""},
 "footer_navigation_typography":{"size":{"desktop":14},"sizeType":"px","lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":""}}
```

---

## 9. Sélecteurs CSS réels et comparaison avec `pd-kadence.css`

### 9.1 Arbre HTML rendu (page `ref-entete-pied-test`, réglages du § 10, 1280 px) [B]

```
header#masthead.site-header
  div#main-header.site-header-wrap                                  ← en-tête bureau (≥ 1025 px)
    div.site-header-inner-wrap
      div.site-header-upper-wrap
        div.site-header-upper-inner-wrap(.child-is-fixed)
          div.site-main-header-wrap.site-header-row-container.site-header-focus-item.site-header-row-layout-standard
              .kadence-sticky-header(.item-is-fixed.item-at-start | .item-is-stuck)
            div.site-header-row-container-inner                     ← FOND et BORDURE de la rangée
              div.site-container
                div.site-main-header-inner-wrap.site-header-row.site-header-row-has-sides.site-header-row-no-center   ← min-height
                  div.site-header-main-section-left.site-header-section.site-header-section-left
                    div.site-header-item.site-header-focus-item
                      div.site-branding.branding-layout-standard
                        a.brand > div.site-title-wrap > p.site-title
                  div.site-header-main-section-right.site-header-section.site-header-section-right
                    div.site-header-item.site-header-item-main-navigation.header-navigation-layout-stretch-false…
                      nav#site-navigation.main-navigation.header-navigation.hover-to-open.nav--toggle-sub.header-navigation-style-standard…
                        div.primary-menu-container.header-menu-container
                          ul#primary-menu.menu > li.menu-item(.current-menu-item) > a
  div#mobile-header.site-mobile-header-wrap                         ← en-tête mobile (≤ 1024 px)
    div.site-header-inner-wrap > div.site-header-upper-wrap > div.site-header-upper-inner-wrap
      div.site-main-header-wrap.site-header-focus-item.site-header-row-layout-standard.site-header-row-tablet-layout-default
          .site-header-row-mobile-layout-default.kadence-sticky-header   (pas de .site-header-row-container ici)
        div.site-header-row-container-inner > div.site-container > div.site-main-header-inner-wrap.site-header-row…
          div.site-header-main-section-left … div.site-branding.mobile-site-branding… > a.brand > div.site-title-wrap > div.site-title
              (+ .vs-md-false si logo_layout.include.tablet est vide : titre masqué de 720 à 1024 px)
          div.site-header-main-section-right … div.mobile-toggle-open-container > button#mobile-toggle.menu-toggle-open.drawer-toggle
div#mobile-drawer.popup-drawer…  (voir § 6, hors de #masthead)
footer#colophon.site-footer
  div.site-footer-wrap
    div.site-bottom-footer-wrap.site-footer-row-container.site-footer-focus-item.site-footer-row-layout-standard…
      div.site-footer-row-container-inner                           ← FOND, BORDURE, taille et couleur du texte de la rangée
        div.site-container
          div.site-bottom-footer-inner-wrap.site-footer-row.site-footer-row-columns-2.site-footer-row-column-layout-equal…   ← grille
            div.site-footer-bottom-section-1.site-footer-section
              div.footer-widget-area.site-info.content-align-left.content-mobile-align-center.content-valign-middle…
                div.footer-widget-area-inner.site-info-inner > div.footer-html.inner-link-style-plain > div.footer-html-inner > p
            div.site-footer-bottom-section-2.site-footer-section
              div.footer-widget-area.widget-area.footer-navigation-wrap.content-align-right…
                div.footer-navigation-inner > nav#footer-navigation.footer-navigation > div.footer-menu-container > ul#footer-menu.menu > li > a
```

Sélecteurs à utiliser dans un CSS maison :

| Cible | Sélecteur fiable |
|---|---|
| tout l'en-tête | `#masthead` (ne pas y mettre de `backdrop-filter`, `filter` ni `transform`) |
| rangée principale, bureau **et** mobile | `.site-main-header-wrap .site-header-row-container-inner` |
| rangée bureau seule ou mobile seule | `#main-header .site-main-header-wrap …`, `#mobile-header .site-main-header-wrap …` |
| rangée collée | `.kadence-sticky-header.item-is-stuck` |
| titre | `.site-branding .site-title` (lien : `.site-branding a.brand`) |
| liens du menu principal | `.main-navigation .primary-menu-container > ul > li.menu-item > a` ; page courante `li.current-menu-item > a` |
| bouton du menu mobile | `#mobile-toggle` ou `.mobile-toggle-open-container .menu-toggle-open` |
| tiroir | `#mobile-drawer .drawer-inner` ; liens `#mobile-drawer .mobile-navigation ul li > a` ; fermer `#mobile-drawer .drawer-header .drawer-toggle` |
| pied | `#colophon` ; rangée `.site-bottom-footer-wrap .site-footer-row-container-inner` ; grille `.site-bottom-footer-inner-wrap` |
| copyright | `#colophon .footer-html` |
| menu du pied | `#colophon .footer-navigation .footer-menu-container > ul > li > a` |

### 9.2 Sélecteurs de `pd-kadence.css` (blocs « En-tête » et « Pied de page »)

Nombre d'éléments trouvés par `document.querySelectorAll` (pseudo-classes `:hover` retirées) sur la page d'essai. « Partagé » = site partagé, réglages par défaut, aucun menu. « Réglé » = bac à sable avec la fonction du § 10 et de vrais menus. Mesuré à 1280 et 390 px, résultats identiques. [T, B]

| Sélecteur | Partagé | Réglé | Verdict |
|---|---|---|---|
| `body.pd-site #masthead` | 1 | 1 | existe. Son `backdrop-filter` **casse l'en-tête collant** (§ 9.3). |
| `body.pd-site .site-header .site-header-row-container-inner` | 2 | 2 | existe (rangées bureau et mobile) |
| `body.pd-site .site-header-upper-wrap` | 2 | 2 | existe, mais c'est un **ancêtre** de la rangée : son `backdrop-filter` casse aussi le collant, et il ajoute un 2ᵉ fond et une 2ᵉ bordure |
| `body.pd-site .site-main-header-wrap .site-header-row-container-inner` | 2 | 2 | existe : **le bon** sélecteur pour la rangée |
| `body.pd-site .site-branding a.brand` | 2 | 2 | existe |
| `body.pd-site .site-branding .site-title` | 2 | 2 | existe |
| `body.pd-site .site-title a` | **0** | **0** | **ne correspond à rien** : le lien entoure le titre (`a.brand > … > .site-title`), il n'est pas dedans |
| `body.pd-site .site-description` | 0 | 0 | **rien** tant que `logo_layout` ne contient pas `tagline`. Le slogan n'est jamais affiché avec les réglages par défaut ni ceux du § 10. |
| `body.pd-site .header-navigation .header-menu-container > ul > li > a` | 5 | 5 | existe |
| `body.pd-site .header-navigation ul.menu > li.menu-item > a` | 5 | 5 | existe (doublon du précédent) |
| `….header-menu-container > ul > li.current-menu-item > a`, `…ul.menu > li.current-menu-item > a` | 0 | 1 | existent quand la page courante est dans le menu. Sur le site partagé, la page d'essai ne fait pas partie des 5 pages de la liste de secours. |
| `body.pd-site .menu-toggle-open`, `… .menu-toggle-open .menu-toggle-icon` | 1 | 1 | existent |
| `body.pd-site #mobile-drawer .drawer-inner`, `… .drawer-content` | 1 | 1 | existent |
| `body.pd-site #mobile-drawer a` | 5 | 5 | existe. Son `color … !important` **efface la couleur « actif »** du menu mobile. |
| `body.pd-site #mobile-drawer .menu-toggle-close` | 1 | 1 | existe |
| `body.pd-site #colophon` | 1 | 1 | existe |
| `body.pd-site .site-footer .site-footer-row-container-inner`, `… .site-footer-wrap .site-footer-row-container-inner` | 1 | 1 | existent ; ils visent le même élément (doublon) |
| `body.pd-site #colophon a`, `… .site-footer a` (+ `:hover`) | 1 | 3 | existent (1 lien, « Kadence WP », sur le partagé ; 3 liens du menu une fois réglé) |
| `body.pd-site .footer-navigation ul.menu` | **0** | 1 | **rien** sur le site actuel : le pied par défaut ne contient pas d'élément `footer-navigation`. Existe une fois l'élément placé (§ 7). |
| `body.pd-site #kt-scroll-up`, `#kt-scroll-up-reader` | 0 | 0 | **rien** tant que `scroll_up` vaut `false` (défaut). Avec `scroll_up: true` : `<a id="kt-scroll-up">` et `<button id="kt-scroll-up-reader">` présents. [B] |

Hors sujet de cette fiche, mais à zéro sur cette page : `.entry-hero`, `.entry-header` et `.page-hero-section` existent seulement quand le titre de page est affiché. Ils sont présents sur `page-d-exemple` du site partagé, et absents ici à cause de la méta `_kad_post_title: hide`. `.entry-content > .wp-block-html` et les sélecteurs `.pd-page …` dépendent du contenu de la page.

### 9.3 Conflits mesurés entre `pd-kadence.css` et les réglages Kadence [B]

Même bac à sable, mêmes réglages (§ 10), trois feuilles différentes. « Kadence seul » : sans `pd-kadence.css`. « pd actuel » : le fichier tel qu'il est dans le dépôt. « CSS proposé » : blocs En-tête et Pied remplacés par le § 9.4.

| Mesure | Kadence seul | pd actuel | CSS proposé |
|---|---|---|---|
| Rangée bureau après défilement (y, 1280 px) | 0 (collée) | **−450 (partie avec la page)** | 0 |
| Rangée mobile après défilement (y, 390 px) | 0 | **−900** | 0 |
| Hauteur de `#masthead` (1280 px) | 77 px | 79 px (3 fonds et 3 bordures empilés : `#masthead`, `.site-header-upper-wrap`, rangée) | 77 px |
| Titre à 390 px | 19,2 px (réglage mobile) | 21,6 px (`!important` 1,35 rem partout) | 19,2 px |
| Lien actif dans le tiroir | rgb(192, 64, 61) | rgb(232, 230, 225) (`#mobile-drawer a … !important`) | rgb(192, 64, 61) |
| Survol du bouton menu (390 px) | rgb(192, 64, 61) | rgb(232, 230, 225) (`.menu-toggle-open … !important`) | — |
| Espace entre liens du pied | padding seul | padding + `gap: 1.2rem` | padding seul |
| Lien actif du menu bureau | couleur seule | souligné béret | souligné béret |
| `#colophon` `border-top` | aucune | 1px (doublon de la bordure de la rangée) | aucune |

Cause du collant cassé, vérifiée : avec `pd-kadence.css` chargé, retirer seulement le `backdrop-filter` de `#masthead` **ne suffit pas**. Il faut aussi le retirer de `.site-header-upper-wrap`. La rangée reste alors collée (y = 0, à 1280 et à 390 px). Un `backdrop-filter` sur un ancêtre fait de celui-ci le bloc conteneur des éléments en `position: fixed`.

### 9.4 Remplacement proposé (testé en bac à sable [B], non appliqué au dépôt)

Une fois la fonction du § 10 appliquée, les blocs `/* En-tête */` et `/* Pied de page */` de `pd-kadence.css`, de `/* En-tête */` jusqu'à `/* Bouton « remonter » de Kadence */` exclu, peuvent se réduire à ceci :

```css
/* En-tête et pied : fonds, bordures, couleurs, tailles et alignements viennent des réglages
   Kadence (theme_mods, voir outils/kadence-reference/entete-et-pied.md). Ici, seulement ce que Kadence ne sait pas faire. */

/* Flou derrière la rangée de l'en-tête. JAMAIS sur #masthead ni .site-header-upper-wrap :
   un backdrop-filter sur un ancêtre de la rangée collée (position: fixed) la fait défiler avec la page. */
body.pd-site .site-main-header-wrap .site-header-row-container-inner {
	-webkit-backdrop-filter: blur(8px);
	backdrop-filter: blur(8px);
}

/* Soulignement béret au survol et sur la page courante (menu principal, bureau) */
body.pd-site .main-navigation .primary-menu-container > ul > li.menu-item > a:hover,
body.pd-site .main-navigation .primary-menu-container > ul > li.current-menu-item > a {
	text-decoration: underline;
	text-decoration-color: var(--beret-vif);
	text-underline-offset: .45em;
}
```

Mesures avec ce CSS : `backdrop-filter: blur(8px)` sur la rangée, rangée collée à y = 0 sur bureau et mobile, lien actif souligné en rgb(192, 64, 61) avec un décalage de 6,84 px, titre à 19,2 px sur mobile, lien actif du tiroir en béret. [B] Le bloc « Bouton remonter » (`#kt-scroll-up`) peut rester tel quel : il ne concerne pas ces réglages.

---

## 10. Fonction PHP prête à l'emploi

Elle produit : un en-tête sur une ligne (titre à gauche, menu principal à droite), collant, avec un fond `#0d1217` à 92 % et une bordure basse `1px #2c3a49` ; un pied d'une rangée (copyright à gauche, menu du pied à droite) ; un tiroir mobile sombre.
Elle a été **appliquée uniquement dans le bac à sable** (61 clés écrites et relues, rendu mesuré, § 10.2), **pas** sur le site partagé.
À placer par exemple dans `kadence-pascal/inc/entete-pied.php` et à charger depuis `functions.php` avec `require get_stylesheet_directory() . '/inc/entete-pied.php';`.

```php
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
			'family'        => 'var(--display)',
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
```

### 10.1 À savoir avant de l'appliquer

- Elle **suppose** que le `functions.php` du thème enfant a placé les menus dans `primary`, `mobile` et `footer`. Sinon, l'en-tête et le pied affichent les 5 premières pages (§ 0, point 9).
- Elle ne touche ni la palette ni `site_background` (voir `theme-reglages.md`). Les couleurs sont en hexadécimal : le résultat ne dépend donc pas de la palette. Équivalents avec la palette prévue dans `theme-reglages.md` : `#0d1217` = `palette9`, `#17202a` = `palette8`, `#2c3a49` = `palette6`, `#e8e6e1` = `palette3`, `#a9b6c0` = `palette4`, `#c8b287` = `palette5`, `#c0403d` = `palette2`.
- Avec `pd-kadence.css` tel qu'il est aujourd'hui, l'en-tête collant **ne fonctionne pas** (§ 9.3). Remplacer en même temps ses blocs En-tête et Pied par le § 9.4.
- Pour revenir aux valeurs par défaut de Kadence : `foreach ( array_keys( pd_kadence_entete_pied_mods() ) as $k ) { remove_theme_mod( $k ); }`.

### 10.2 Résultat mesuré dans le bac à sable (sans `pd-kadence.css`) [B]

| Point | 1280 px | 390 px |
|---|---|---|
| Rangée | fond `rgba(13, 18, 23, 0.92)`, bordure basse `1px solid rgb(44, 58, 73)`, hauteur minimale 76 px | idem, 64 px |
| Fond de `#masthead` | rgb(13, 18, 23) | idem |
| Collant | `item-is-stuck`, y = 0 après défilement ; fond toujours `rgba(…, 0.92)` | idem |
| Titre | Newsreader, 21,6 px, 400, rgb(232, 230, 225) | 19,2 px |
| Menu | rgb(169, 182, 192), 15,2 px, padding 9,12 px × 10,64 px ; survol et actif rgb(232, 230, 225) | — |
| Bouton | — | icône 24 px, rgb(232, 230, 225), survol rgb(192, 64, 61) |
| Tiroir | — | `sidepanel` à droite, 351 px, fond rgb(23, 32, 42), liens 17 px séparés par `1px solid rgb(44, 58, 73)`, actif rgb(192, 64, 61) |
| Pied | `#colophon` et rangée rgb(13, 18, 23), bordure haute 1px rgb(44, 58, 73), grille `601px 601px`, « © 2026 Pascal Dupont » à gauche, menu à droite (`flex-end`), 14 px, rgb(169, 182, 192), survol rgb(232, 230, 225) | grille `342px` (empilée), copyright et menu centrés |
| À 900 px | en-tête mobile avec le titre visible (aussi à 800 et 720 px) ; pied sur deux colonnes `411px 411px` | |
| Erreurs JS, débordement horizontal | aucun | aucun |

---

## 11. Captures

Dossier : `/tmp/claude-0/-home-user-pascaldupont-fr/9562e8de-1adf-51fb-b316-6cc9700228e2/scratchpad/ref/entete-pied/captures/` (temporaire, propre à la session).

| Fichier | Contenu |
|---|---|
| `partage-etat-actuel-1280-haut.png`, `-1280-defile.png`, `-1280-bas.png`, `-390-haut.png`, `-390-defile.png`, `-390-bas.png`, `-390-menu-ouvert.png` | site **partagé**, page `ref-entete-pied-test`, réglages par défaut + `pd-kadence.css` : menu de secours (5 pages), en-tête non collant, pied d'une colonne avec le crédit Kadence |
| `prive-kadence-seul-*` (mêmes suffixes) | bac à sable, fonction du § 10, **sans** `pd-kadence.css` : le rendu exact des réglages |
| `prive-avec-pd-kadence-css-*` | bac à sable, fonction du § 10, `pd-kadence.css` actuel : l'en-tête disparaît au défilement (`-defile`, `-bas`) |
| `prive-css-propose-*` | bac à sable, fonction du § 10 + CSS du § 9.4 : rendu cible |
| `prive-outil-1280.png`, `prive-outil-390.png` | pleine page avec l'outil (`editeur.js capture … --base http://127.0.0.1:8097`) : `statut 200`, pas de débordement horizontal, aucune erreur JS |

Les captures du site partagé ont aussi été faites avec l'outil (`editeur.js capture ref-entete-pied-test … 1280` et `… 390`) : statut 200, aucun débordement, aucune erreur JS. Note : le défilement de la page est animé (`scroll-behavior`). Une capture prise moins d'une seconde après un `scrollTo` montre la rangée collée décalée vers le bas. C'est un artefact de capture : mesurée après 1,8 s, la rangée est bien à y = 0.

---

## 12. Ce qui n'a PAS été vérifié

- **Rien n'a été appliqué au site partagé** : ni la fonction du § 10, ni la correction de `pd-kadence.css`. Tous les essais d'écriture ont eu lieu dans le bac à sable.
- **Outil de personnalisation** (`customize.php`) jamais ouvert : rien ne garantit qu'il affiche correctement des valeurs écrites par code. Exemple : `logo_layout.include = "title"` fonctionne en public, mais l'interface ne propose pas cette valeur.
- Clés lues dans le code seulement (C dans les tableaux) : `header_main_padding`, `header_main_top_border`, `header_top_*`, `header_bottom_*` (sauf l'affichage de la rangée), `header_*_trans_background` et tout l'en-tête transparent `transparent_header_*`, `header_reveal_scroll_up`, `header_sticky_bottom_border`, `header_sticky_box_shadow`, couleurs et logo propres à l'état collé, `mobile_header_sticky_shrink`, `brand_tag_typography` (slogan), `custom_logo`, `logo_width`, `use_logo_icon`, `primary_navigation_parent_active`, `primary_navigation_open_type: click`, `primary_navigation_stretch`, tous les `dropdown_navigation_*` (aucun sous-menu dans les essais), `secondary_navigation_*`, `header_popup_width`, `header_popup_close_background`, les animations `scale` et `slice`, `mobile_navigation_background`, `footer_bottom_bottom_border`, `footer_bottom_column_border`, `footer_bottom_widget_title`, `footer_bottom_direction`, `footer_bottom_collapse: rtl`, `footer_html_link_color`, `footer_html_margin`, `footer_navigation_background`, `footer_navigation_stretch: true`, `footer_social_*`, `footer-widget1`…`6`, `header_search_*`, `header_button_*` (sauf son affichage), `header_social_*`, `header_html_*` (sauf son contenu), panier WooCommerce (`cart`, `mobile-cart`).
- `brand_typography_color.active`, appliqué seulement sur la page d'accueil (`body.home`) : règle CSS vue, effet non mesuré, car la page d'essai n'est pas l'accueil.
- Fonds de type `image` ou `gradient` sur l'en-tête et le pied : seule la couleur a été testée.
- Comportements de `navigation.min.js` autres que la fixation : réapparition au retour vers le haut, rétrécissement en mobile, navigation au clavier dans le tiroir (seule la fermeture par Échap a été utilisée, sans contrôle).
- Tailles intermédiaires hors 390, 880, 900, 1000, 1280 et 1700 px.
- Effet sur les vraies pages du site (accueil, films…) : seule `ref-entete-pied-test` a été rendue.

---

## 13. Reproduction et fichiers de travail

Page créée sur le site partagé : `ref-entete-pied-test` (id 108), spec `spec-test.json`. Elle contient 4 rangées `kadence/rowlayout` avec un titre et un paragraphe, et les méta `_kad_post_layout: fullwidth`, `_kad_post_content_style: unboxed`, `_kad_post_vertical_padding: hide`, `_kad_post_title: hide`. L'outil n'a signalé aucun bloc invalide, et le contenu enregistré a été relu avec `lire.php`.

Dossier de travail : `/tmp/claude-0/-home-user-pascaldupont-fr/9562e8de-1adf-51fb-b316-6cc9700228e2/scratchpad/ref/entete-pied/` (temporaire) :
- `pd-entete-pied.php` : la fonction du § 10 (identique) ;
- `pd-kadence-entete-pied-propose.css` : le CSS du § 9.4 ;
- `wp-clone/` : le bac à sable. Pour le relancer : `php -S 127.0.0.1:8097 -t wp-clone /home/user/pascaldupont.fr/outils/wp-test/router.php`. Sa base contient les menus d'essai « Menu principal » et « Pied de page » et la fonction appliquée. `wp-clone/wp-content/mu-plugins/ep-essais.php` fournit `?sanspd=1` ;
- `clone.php` : `etat`, `menus`, `reinit`, `appliquer`, `variante <json>`, `lire <clés>`. Il refuse de s'exécuter si `ABSPATH` n'est pas le bac à sable ou si l'adresse n'est pas `:8097` ;
- `var/*.json` : les variantes essayées : fond par défaut et collant (`va`, `vb`, `vi`), typographie (`vc`, `vd`), zones et soulignement (`ve`, `vn`), colonnes du pied et menu absent (`vf`), mobile, seuil et rétrécissement (`vg`), modes collants (`vh`), défilement vers le haut (`vj`), largeurs (`vk`), structure minimale (`vl`), pied en tablette (`vm`), tiroir sans bouton (`vo`), titre sur tablette (`vp`) ;
- `inspecter.js` (styles calculés, sélecteurs de `pd-kadence.css`, CSS Kadence, captures), `mesurer.js` (sondes ciblées), `captures.js`, `arbre.js` (squelette HTML), `test-flou.js` (cause du collant cassé), `survol-bouton.js`, `bas.js` (artefact de capture) ;
- `defauts.php` : valeurs par défaut de Kadence, par exemple `php defauts.php 'header_*' 'footer_*'` (lecture seule sur le site partagé) ;
- `out/` : mesures JSON, HTML rendus, `arbre-c1.txt`, `arbre-partage.txt` et `css-kadence-final.css`, le CSS que Kadence produit avec la fonction du § 10.

Pour revérifier un réglage sans toucher au site partagé : relancer le bac à sable, écrire la valeur dans un fichier JSON, puis `php clone.php variante fichier.json` et `node mesurer.js "http://127.0.0.1:8097/ref-entete-pied-test/?sanspd=1" 1280 sondes.json [défilement]`. Pour revenir à l'état du § 10 : `php clone.php reinit && php clone.php appliquer`.

---

## Contre-vérification (relecture sceptique du 7 octobre 2026)

Objectif : essayer de réfuter les affirmations les plus utiles à un développeur (clés, formats, valeurs par défaut, sélecteurs, extraits JSON, fonction du § 10). Les corrections ont été reportées directement dans les sections concernées. Elles sont repérables par la mention « contre-vérification ».

### Méthode

- **Bac à sable distinct** de celui de l'auteur : copie du WordPress de test dans `scratchpad/ref/entete-pied-verif/wp-verif/`, base SQLite copiée avec `SQLite3::backup()` et servie sur `http://127.0.0.1:8098`. Seule cette copie contient un `mu-plugins/epv-sanspd.php` (`?sanspd=1` retire `pd-kadence.css`) et deux menus d'essai, « Verif principal » (`primary` et `mobile`, avec la page d'essai comme élément actif) et « Verif pied » (`footer`). Le pilote `clone.php` (`etat`, `reinit`, `variante`, `lire`) refuse de s'exécuter hors de cette copie.
- **Page construite avec l'outil** : `editeur.js construire spec-verif-page.json`, avec 4 `kadence/rowlayout` et les méta `_kad_post_*` du § 13, sous le slug `ref-entete-pied-verif-page`. Elle a été créée dans le bac à sable (`--base http://127.0.0.1:8098`) et sur le site partagé (id 171 dans les deux cas). Résultat : 0 bloc invalide, 0 erreur JS. Le contenu enregistré a été relu avec `lire.php`.
- **Mesures** : script Playwright `sonde.js` (`getComputedStyle`, boîtes, classes), à 1280, 1025, 1024, 1000, 900, 899, 880, 768, 767, 740, 720, 719 et 390 px. Selon les cas, après un défilement de 400 ou 600 px, ou avec le tiroir ouvert. Captures avec `editeur.js capture` : `captures/verif-specs-{1280,900,390}.png` (statut 200, pas de débordement, aucune erreur JS) et `captures/partage-defaut-900.png`.
- **Code** : relecture de `Options\Component::option()` et `sub_option()`, de `Component::defaults()` (≈ 110 clés relues une par une), de `styles/component.php` (CSS de l'en-tête et du pied), de `class-kadence-css.php` (`render_font`, `render_color`, `render_background`, `render_border`), de `custom_header` et `custom_footer`, des gabarits `header-row.php`, `mobile-header-row.php`, `base.php`, `mobile.php` et `footer-row.php`, de `footer-html.php`, de `header-functions.php`, de `footer-functions.php`, de `nav_menus/component.php` et des feuilles `footer.min.css`, `header.min.css` et `global.min.css`.
- **Site partagé** : aucun réglage modifié. Les theme_mods ont été relus avant et après : `{"nav_menu_locations":[],"custom_css_post_id":-1,"initial_version":"1.5.2"}`. Seule la page `ref-entete-pied-verif-page` y a été ajoutée.

### Specs d'exemple rejouées

Les **10 extraits JSON** de la fiche (§ 1.1, § 1.2, § 2, § 3, § 4, § 5, § 6, § 7.1, § 7.2 et § 8) ont été extraits automatiquement du Markdown, puis écrits **tels quels** dans le bac à sable avec `set_theme_mod()`, à partir de theme_mods remis à zéro. Résultat : 61 clés, toutes au format JSON valide. Comparées clé par clé au tableau que renvoie `pd_kadence_entete_pied_mods()` (§ 10, `php -l` sans erreur), elles ne présentent **aucune différence**.

| Spec rejouée | Mesure de contre-vérification | Verdict |
|---|---|---|
| § 0, règle 2 (`{"brand_typography":{"size":{"desktop":30}}}`) | CSS produit : `.site-branding .site-title{font-size:30px;}` et rien d'autre. Après `remove_theme_mod` : `font-weight:700;font-size:26px;line-height:1.2;color:var(--global-palette3)` | confirmé |
| § 2 (titre) | 1280 px : Newsreader, 21,6 px, 400, interligne 25,92 px, approche 0,216 px, rgb(232, 230, 225). 390 px : 19,2 px. 900 px : titre de l'en-tête mobile **visible**. Sur le site partagé (défaut) à 900 px : `div.site-title.vs-md-false` en `display:none` | confirmé |
| § 3 + § 4 (rangée, collant) | Rangée bureau et mobile : `rgba(13, 18, 23, 0.92)`, `1px solid rgb(44, 58, 73)`, hauteur minimale 76 px (1280 et 900 px) puis 64 px (≤ 767 px), `#masthead` rgb(13, 18, 23). Après défilement : `item-is-fixed item-is-stuck`, y = 0, fond toujours à 0,92. Sans `header_sticky_background` : rangée collée rgb(13, 18, 23) (opaque) avec `#0d1217`, **blanche** avec la valeur par défaut. Commutation : bureau à 1025 px, mobile à 1024 px | confirmé |
| § 5 (menu principal) | rgb(169, 182, 192), 15,2 px, 400, padding 9,12 px × 10,64 px ; actif rgb(232, 230, 225) ; `--global-primary-nav-font-family:inherit` | confirmé |
| § 6 (bouton, tiroir) | Icône 24 px, rgb(232, 230, 225). Tiroir ouvert : `show-drawer active pop-animated`, `.drawer-inner` de 351 px, fond rgb(23, 32, 42), liens 17 px séparés par `1px solid rgb(44, 58, 73)`, actif rgb(192, 64, 61), fermeture rgb(232, 230, 225). Sans `header_popup_background` : rgb(9, 12, 16) | confirmé |
| § 7.1 + § 7.2 + § 8 (pied) | 1280 px : grille `601px 601px`, `column-gap` 30 px, padding 24 px, rangée rgb(13, 18, 23) avec bordure haute `1px solid rgb(44, 58, 73)`, texte 14 px rgb(169, 182, 192), « © 2026 Pascal Dupont » aligné à gauche, menu `flex-end`, liens 8,4 px × 4,2 px, actif et survol rgb(232, 230, 225). 900 px : `411px 411px`. 390 px : `342px`, copyright et menu centrés. `footer_bottom_columns: "1"` : menu du pied absent du HTML. `.footer-html` : marge 14 px | confirmé, avec une réserve sur `column_spacing` (voir ci-dessous) |
| § 9.4 (CSS proposé, injecté par Playwright) | Rangée collée à y = 0 à 1280 et 390 px, `backdrop-filter: blur(8px)` sur la rangée, lien actif souligné rgb(192, 64, 61) avec un décalage de 6,84 px. Avec le `pd-kadence.css` actuel : rangée à y = −400 après un défilement de 400 px | confirmé |

Autres affirmations confirmées par essai :
- zones `_left_center` et `_right_center` du bureau ignorées sans `_center` ;
- rangée `top` absente si seul `top_left_center` est rempli ;
- tiroir absent sans `popup-toggle` : `#mobile-drawer` et `#mobile-toggle` absents du HTML ;
- deux `ul#primary-menu` sur le site partagé, sans menu ;
- seuils statiques 720–1024 et ≤ 719 px pour les colonnes du pied ;
- seuil du CSS calculé à ≤ 767 px (hauteur mobile appliquée à 767 px, pas à 768 px).

### Erreurs et manques corrigés dans la fiche

1. **§ 1.2, zones mobiles** : « pas de `_left_center` en mobile » était inexact. L'interface ne les propose pas, mais `mobile-header-row.php` rend `{rangée}_left_center` et `{rangée}_right_center` quand `_center` est rempli. Vérifié par essai.
2. **§ 10, commentaire PHP** : « empilerait les deux colonnes entre 768 et 1024 px » a été remplacé par **720** et 1024 px. Mesure avec `tablet: ""` : une colonne à 1024, 768, 740 et 720 px, deux colonnes à 1025 px. Le commentaire a aussi été corrigé dans la copie `ref/entete-pied/pd-entete-pied.php`, pour que le § 13 (« identique ») reste vrai.
3. **§ 7.2, `footer_bottom_column_spacing`** : pour la rangée **basse**, Kadence n'écrit que `grid-column-gap`, sans `grid-row-gap` (contrairement à `top` et `middle`). La valeur `mobile: 8` de l'extrait ne sépare donc pas les blocs empilés : écart mesuré de 0 px, avec 8 comme avec 40.
4. **§ 7.2, `footer_bottom_link_style`** : il manquait la valeur `noline`. Sens des trois valeurs : `plain` souligne au survol, `normal` souligne toujours (menu du pied compris), `noline` ne souligne jamais et l'emporte sur `footer_html_link_style`.
5. **§ 8.1, piège ajouté** : `footer_html_content: ""` revient au texte par défaut, crédit Kadence compris. Pour supprimer le copyright, il faut retirer `footer-html` de `footer_items`.
6. **§ 4, `header_sticky_main_shrink`** : `unit` est ignoré. La valeur est toujours lue en px (essai avec `"unit":"em"` : 56 px).
7. **§ 6.4, `header_mobile_switch`** : seuil exact, bureau à `size` px et mobile à `size − 1` px. Effet de bord ajouté : la media query « tablette » du CSS d'en-tête est déplacée à `(max-width: size−1px)`. Cet effet est lu dans le code ; la règle `@media all and (max-width: 899px)` a été vue dans la page, mais son effet sur une valeur `tablet` n'a pas été mesuré.
8. **§ 2, `logo_layout` partiel** : un objet sans `include.tablet` produit un `PHP Warning` et un `Deprecated` à chaque page (`header-functions.php:482`).
9. **§ 0, point 9** : l'attribution automatique des menus par `functions.php` n'a lieu qu'une fois, et seulement quand les pages `_pd_page` = `accueil` et `films` existent. Ce n'est pas encore le cas sur le site partagé (`pd_installe` = `false`).
10. **§ 7.2, compléments** : `footer_bottom_columns` accepte aussi un entier (`absint()`). Valeurs de `footer_bottom_layout` ajoutées pour 3 colonnes (`first-row`, `last-row`) et 4 colonnes (`left-forty`, `right-forty`, `two-grid`), lues dans `footer.min.css` [C].

### Non revérifié lors de cette relecture

- Le tableau de comptage des sélecteurs de `pd-kadence.css` (§ 9.2) et les chiffres exacts −450 / −900 du § 9.3. Les mesures de cette relecture donnent y = −400 pour un défilement de 400 px, ce qui mène à la même conclusion.
- Les valeurs `layout` de `logo_layout` autres que `standard`, le slogan, le logo image, `primary_navigation_style: underline` (seule la feuille `header.min.css` a été relue), `mobile_trigger_style: bordered`, `header_popup_layout: fullwidth` et `brand_typography_color.active`.
- Les mêmes réserves que le § 12 : outil de personnalisation jamais ouvert, fonds `image` et `gradient`, en-tête transparent, sous-menus.

Fichiers de cette relecture : `scratchpad/ref/entete-pied-verif/` (`clone.php`, `sonde.js`, `css-propose.js`, `comparer.php`, `var/*.json` pour les variantes et les 10 extraits de la fiche, `out/*.json` pour les mesures, `captures/`). Le bac à sable `wp-verif/` se relance avec `php -S 127.0.0.1:8098 -t wp-verif /home/user/pascaldupont.fr/outils/wp-test/router.php`. Il contient les 61 clés de la fiche.
