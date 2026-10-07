# Kadence 1.5.2 : réglages du thème en base (palette, typographie, couleurs, mise en page, méta de page)

Fiche de référence pour appliquer les réglages du thème Kadence **depuis le thème enfant `kadence-pascal`**, sans passer par l'outil de personnalisation. Elle sert aussi à écrire les méta de page (`"meta"`) dans les specs JSON de `outils/wp-test/editeur.js construire`.
Environnement vérifié : WordPress 7.1.3 (fr_FR), thème Kadence **1.5.2** + thème enfant `kadence-pascal`, Kadence Blocks 3.7.12.1 (gratuit).

Légende de la colonne « Vérif. » :
- **B** : vérifié en **écriture réelle** dans un bac à sable. C'est une copie privée du WordPress de test (fichiers et base SQLite copiés), servie sur `http://127.0.0.1:8091`. Les valeurs ont été écrites avec la fonction du § 10, relues en base, puis le rendu public a été mesuré avec `getComputedStyle` à 1280, 900 et 375 px. Pour les mesures, `?sans-pd` retirait `pd.css` et `pd-kadence.css` du thème enfant, qui écrasent Kadence avec `!important`. Ce paramètre n'existe que dans le bac à sable.
- **L** : vérifié **en lecture seule** sur le site partagé (`:8080`). Les valeurs étaient simulées en mémoire avec des filtres `pre_option_*`, puis Kadence les a lues et a produit son CSS avec `generate_base_css()`. Une lecture SQL directe avant et après a confirmé que la base n'avait pas changé.
- **T** : testé sur le site partagé avec l'outil (`editeur.js construire`, pages `ref-theme-reglages-*`), puis relu avec `get_post_meta` et dans le HTML public.
- **C** : lu dans le code source seulement (`inc/components/options/component.php`, `inc/components/styles/component.php`, `inc/class-kadence-css.php`, `inc/components/layout/component.php`, `inc/meta/class-theme-meta.php`, `inc/customizer/options/*.php`, `assets/css/global.min.css`).

Points de rupture du CSS du thème : **tablette ≤ 1024 px**, **mobile ≤ 767 px** (`@media all and (max-width: …)`).

---

## 0. Règles essentielles

1. **Deux lieux de stockage.** [B]
   - **Palette** : option WordPress `kadence_global_palette`. Sa valeur est une **chaîne JSON**. Elle est **commune à tous les thèmes** et chargée automatiquement (`autoload`).
   - **Tous les autres réglages** : *theme mods* du **thème actif**, soit l'option `theme_mods_kadence-pascal`. On les écrit avec `set_theme_mod()` pendant que le thème enfant est actif. Les theme mods du parent (`theme_mods_kadence`) ne sont **pas** lus quand l'enfant est actif.
2. **Lecture : `\Kadence\kadence()->option( $cle )`** (la fonction `kadence()` est dans l'espace de noms `Kadence`). Elle lit `get_theme_mod( $cle, null )`. Si le résultat est `null` ou `''`, elle prend la valeur par défaut de Kadence, puis le 2ᵉ argument. [L, B]
   - `false`, `0` et `[]` sont **conservés** : `scroll_up = false` reste `false`. [B pour `false`, C pour `0` et `[]`]
   - `''` revient au défaut : `page_layout = ''` donne `'normal'`. [B]
3. **Aucune fusion avec le défaut.** Une valeur enregistrée **remplace entièrement** la valeur par défaut, sans compléter les sous-clés manquantes. Avec `base_font = {"family":"Georgia, serif"}`, la règle `body` ne contient plus que `font-family` : la taille, l'interlignage, la graisse et la couleur disparaissent. [B] → **Toujours écrire la structure complète**, par exemple `array_replace_recursive( défaut, valeur )` comme au § 10.
4. **La palette est une chaîne JSON, jamais un tableau PHP.** `update_option( 'kadence_global_palette', $tableau )` provoque une **erreur fatale** (`TypeError: json_decode(): Argument #1 ($json) must be of type string, array given`). Le filtre `pre_update_option_kadence_global_palette` de Kadence fait en effet un `json_decode`. [B]
5. **Ne pas changer l'ordre des couleurs dans la palette.** L'entrée n° *n* doit avoir le slug `palette{n}`. Constaté : en inversant les deux premières entrées, `palette1` et `palette2` deviennent **vides**. [B]
6. **Couleurs** : `"paletteN"` (N = 1 à 15) devient `var(--global-paletteN)`. On peut aussi écrire `#hex`, `rgba(…)` ou, selon les clés, un dégradé `linear-gradient(…)`. [B pour `paletteN`, C pour le reste]
7. **Tailles responsive du thème** : ce sont des **objets** `{"desktop":…, "tablet":…, "mobile":…}`, **pas** les tableaux `[bureau, tablette, mobile]` de Kadence Blocks. Une valeur absente ou vide pour la tablette ou le mobile ne produit aucune règle : la valeur du palier plus large s'applique. [B]
8. **`after_switch_theme` ne s'exécute pas pendant `switch_theme()`**, mais **au chargement suivant**, sur `init` (priorité 99), quelle que soit la page chargée, administration ou site public. [B]
9. **Contraste** : avec la palette sombre, `palette1` (#a3302f) sur `palette9` (#0d1217) donne **2,71:1**, ce qui est insuffisant pour du texte. Or Kadence utilise `palette1` par défaut pour la couleur des liens et le texte des boutons « contour » (`outline`). Voir les § 4 et 5. Autres rapports sur `palette9` : p2 3,62 ; p3 15,09 ; p4 9,09 ; p5 9,12 ; p6 1,62. Texte p3 sur bouton p1 : 5,57.
10. **Le thème enfant actuel masque une partie des réglages.** `pd-kadence.css` force, avec `!important`, la pleine largeur, l'absence de titre, l'absence de marges et le fond `--nuit` sur **toutes** les pages. Sur le site partagé, l'effet des méta de page n'est donc visible que dans les classes de `<body>`. Les mesures réelles ont été faites dans le bac à sable avec `?sans-pd`.

---

## 1. Comment Kadence lit les valeurs (essai L, puis confirmé en B)

| Appel | Renvoie | Constaté |
|---|---|---|
| `get_option( 'kadence_global_palette' )` | chaîne JSON, ou `false` si absente | `string`, 15 couleurs dans `"palette"`, `active = palette` |
| `\Kadence\kadence()->palette_option( 'palette1' )` | couleur de l'entrée 1 du jeu actif ; `''` si slug décalé | `#a3302f` |
| `\Kadence\kadence()->palette_option( 'palette10' )` | si la valeur est `#FfFfFf` : `oklch(from var(--global-palette1) calc(l + 0.10 * (1 - l)) calc(c * 1.00) calc(h + 180) / 100%)` | idem |
| `\Kadence\kadence()->get_palette()` | chaîne JSON en base, sinon palette par défaut (filtre `kadence_global_palette_defaults`) | C |
| `get_theme_mod( 'page_layout' )` | valeur brute ; `false` si absente | `"fullwidth"` (simulé) |
| `\Kadence\kadence()->option( 'page_layout' )` | valeur brute, sinon défaut Kadence | `"fullwidth"` ; sans simulation : `"normal"` |
| `\Kadence\kadence()->option( 'cle_inconnue', 'secours' )` | 2ᵉ argument si aucun défaut n'existe | `'secours'` |
| `\Kadence\kadence()->sub_option( 'site_background', 'desktop', 'color' )` | sous-clé, ou `null` si vide (`0` est conservé) | `'palette9'` |
| `\Kadence\kadence()->default( 'page_layout' )` | défaut Kadence (filtre `kadence_theme_options_defaults`) | `normal` |
| `\Kadence\Options\Component::defaults()` | tableau des **969** valeurs par défaut | utilisé au § 10 |
| `\Kadence\Theme::instance()->component( 'styles' )->generate_base_css()` | CSS dynamique produit, inséré dans `<head>` | voir les extraits ci-dessous |

Mise en cache :
- `palette_option()` garde la palette en cache statique dès son premier appel, sur `after_setup_theme`, pour la palette de l'éditeur. Une palette modifiée plus tard dans la **même** requête n'apparaît donc qu'à la requête suivante.
- `option()` relit `get_theme_mod()` à chaque appel. [C]

`kadence_theme_option_type` vaut `'theme_mod'` par défaut. Avec le filtre à `'option'`, les réglages seraient lus dans l'option `kadence_settings` (filtre `kadence_theme_option_name`). On ne s'en sert pas. [C]

CSS produit par la fonction du § 10 (extraits relevés tels quels, L et B) :
```css
:root{--global-palette1:#a3302f;--global-palette2:#c0403d;--global-palette3:#e8e6e1;--global-palette4:#a9b6c0;--global-palette5:#c8b287;--global-palette6:#2c3a49;--global-palette7:#223040;--global-palette8:#17202a;--global-palette9:#0d1217;--global-palette10:oklch(from var(--global-palette1) …);--global-palette11:#13612e;…;--global-palette9rgb:13, 18, 23;--global-palette-highlight:var(--global-palette5);--global-palette-highlight-alt:var(--global-palette3);--global-palette-highlight-alt2:var(--global-palette9);--global-palette-btn-bg:var(--global-palette1);--global-palette-btn-bg-hover:var(--global-palette2);--global-palette-btn:var(--global-palette3);…;--global-body-font-family:"Hanken Grotesk", system-ui, -apple-system, "Segoe UI", sans-serif;--global-heading-font-family:"Newsreader", Georgia, "Times New Roman", serif;…;--global-content-width:72rem;--global-content-wide-width:calc(72rem + 10rem);--global-content-narrow-width:842px;--global-content-edge-padding:1.25rem;--global-content-boxed-padding:2rem;…}
body{background:var(--global-palette9);}
body, input, select, optgroup, textarea{font-weight:400;font-size:17px;line-height:1.6;font-family:var(--global-body-font-family);color:var(--global-palette3);}
.content-bg, body.content-style-unboxed .site{background:var(--global-palette9);}
h1,h2,h3,h4,h5,h6{font-family:var(--global-heading-font-family);}
h1{font-weight:400;font-size:3.2rem;line-height:1.1;color:var(--global-palette3);}
@media all and (max-width: 1024px){h1{font-size:2.6rem;}h2{font-size:2.1rem;}h3{font-size:1.45rem;}}
@media all and (max-width: 767px){h1{font-size:2.2rem;}h2{font-size:1.8rem;}h3{font-size:1.3rem;}}
button, .button, .wp-block-button__link, input[type="button"], … {border-radius:2px;box-shadow:0px 0px 0px -7px rgba(0,0,0,0);}
#kt-scroll-up-reader, #kt-scroll-up{border-radius:2px 2px 2px 2px;color:var(--global-palette3);background:var(--global-palette7);bottom:30px;font-size:1.2em;padding:0.4em 0.4em 0.4em 0.4em;}
```

---

## 2. Palette globale : option `kadence_global_palette`

| Élément | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| option `kadence_global_palette` | **string** (JSON) | `{"palette":[…],"second-palette":[…],"third-palette":[…],"active":"palette"}` | absente : Kadence prend sa palette par défaut, bleu-gris clair (`#2B6CB0`, `#215387`, `#1A202C`, `#2D3748`, `#4A5568`, `#718096`, `#EDF2F7`, `#F7FAFC`, `#ffffff`) | B |
| entrée de couleur | objet | `{"color":"#a3302f","slug":"palette1","name":"Palette Color 1"}` ; l'entrée n° *n* a obligatoirement le slug `palette{n}` | (Kadence) | B |
| `palette` / `second-palette` / `third-palette` | tableau | 15 entrées (`palette1` à `palette15`) | 3 jeux identiques | B (`palette`), C (les autres) |
| `active` | string | `"palette"`, `"second-palette"` ou `"third-palette"` ; vide : `"palette"` | `"palette"` | B (`second-palette` a bien changé `palette1`) |
| `palette10` | couleur | **`"#FfFfFf"`, casse exacte** : « complémentaire calculée à partir de palette1 » (valeur `oklch(...)`, filtre `kadence_palette_complement_color`) ; toute autre valeur est utilisée telle quelle | `#FfFfFf` | B |
| `palette11` à `palette15` | couleurs | succès `#13612e`, info `#1159af`, alerte `#b82105`, avertissement `#f7630c`, note `#f5a524` | idem | B |

Comportement :
- **Normalisation à 15 couleurs** : si un jeu contient **exactement 9** entrées, Kadence ajoute `palette10` à `palette15` **à l'écriture** (`pre_update_option_…`) et **à la lecture** (`option_…`). Constaté : un JSON à 9 couleurs a été enregistré avec 15. [B] Un jeu de 10 à 14 entrées n'est pas complété (le test du code porte sur `sizeof == 9`). [C]
- `get_palette_for_customizer()` exige `palette` **et** `active` non vide. Sinon, l'outil de personnalisation affiche la palette par défaut. [C]
- Filtres : `kadence_global_palette_defaults` (JSON par défaut), `kadence_active_palette` (jeu actif), `kadence_palette_option` (valeur finale d'un slug). [C ; le 1ᵉʳ est vérifié en L au § 11]

Utilisation, rendu CSS et éditeur :
- **CSS** : `--global-palette1` à `--global-palette15` et `--global-palette9rgb` (`13, 18, 23`) sur `:root`. [B]
- **Éditeur de blocs** : couleurs `theme-palette1` à `theme-palette15`, dont la valeur est `var(--global-paletteN)` (le `theme.json` du parent). Dans l'éditeur, `--global-palette1` vaut bien `#a3302f`. [B]
- **Classes** : `.has-theme-palette1-color`, `.has-theme-palette-1-color`, `…-background-color`. [C]

Rôle de chaque emplacement **par défaut** dans Kadence. Kadence est conçu pour un thème clair, donc ces rôles déterminent ce que deviennent les couleurs sombres. Sources : valeurs par défaut et `global.min.css`. [C, sauf mention]

| Slug | Rôle prévu par Kadence | Utilisations par défaut (non redéfinies au § 10) | Valeur sombre |
|---|---|---|---|
| palette1 | accent | liens (`link_color.highlight`), fond des boutons, texte et bordure des boutons « contour » | #a3302f |
| palette2 | accent au survol | survol des liens et des boutons, survol du bouton secondaire | #c0403d |
| palette3 | texte le plus fort | h1 à h3, texte d'un champ au focus, texte du bouton secondaire | #e8e6e1 |
| palette4 | texte | **texte courant** (`base_font.color`), h4, h5, bordure des citations, bouton « remonter » en style contour | #a9b6c0 |
| palette5 | texte moyen | h6, **texte des champs de formulaire**, auteur des citations | #c8b287 |
| palette6 | texte discret | **texte indicatif des champs** (placeholder), icône de recherche : 1,62:1, illisible | #2c3a49 |
| palette7 | fond discret | fond de `<pre>`, fond du bouton secondaire | #223040 |
| palette8 | fond clair | **fond du site** (`site_background`) | #17202a |
| palette9 | blanc | **fond du contenu**, **fond des champs**, texte des boutons | #0d1217 |

---

## 3. Typographie

### 3.1 Clés

| Clé (theme mod) | Rôle | Défaut Kadence 1.5.2 | Vérif. |
|---|---|---|---|
| `base_font` | texte courant (`body, input, select, optgroup, textarea`) et `--global-body-font-family` | `{"size":{"desktop":17},"lineHeight":{"desktop":1.6},"family":"-apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,…","google":false,"weight":"400","variant":"regular","color":"palette4"}` | B |
| `heading_font` | **famille seulement** : `--global-heading-font-family`, appliquée à `h1,h2,h3,h4,h5,h6` | `{"family":"inherit"}` | B |
| `h1_font` à `h6_font` | taille, graisse, interlignage, couleur… de chaque niveau | h1 `{"size":{"desktop":32},"lineHeight":{"desktop":1.5},"family":"inherit","google":false,"weight":"700","variant":"700","color":"palette3"}` ; h2 28, h3 24 (palette3) ; h4 22, h5 20 (palette4) ; h6 18 (palette5) | B (h1 à h3 mesurés), C (h4 à h6) |
| `title_above_font` | titre de page `.entry-hero h1` quand le titre est « au-dessus » | `{"size":{"desktop":""},"lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":"","color":""}` | C |
| `buttons_typography` | police des boutons | `{"size":{"desktop":""},"lineHeight":{"desktop":""},"family":"inherit","google":false,"weight":"","variant":""}` | C |
| `font_rendering` | `-webkit-font-smoothing: antialiased` sur `body` | `false` | C |

### 3.2 Format d'une valeur de typographie

| Sous-clé | Type | Format | Vérif. |
|---|---|---|---|
| `family` | string | pile CSS telle quelle (`"\"Hanken Grotesk\", system-ui, sans-serif"`), ou `"inherit"`. **Un nom seul contenant une espace, sans virgule ni guillemet, est entouré d'apostrophes** (`Hanken Grotesk` donne `'Hanken Grotesk'`). Dans `--global-body-font-family` et `--global-heading-font-family`, un point déclenche aussi les apostrophes. | B (pile avec guillemets), L (apostrophes) |
| `google` | bool | `true` : police Google à charger (§ 3.3) ; `false` : police système ou servie par le thème enfant | B |
| `weight` | string | `"400"`, `"700"`… (devient `font-weight`) | B |
| `variant` | string ; **tableau** pour `heading_font` en police Google | `"regular"`, `"italic"`, `"700"`… (sert à choisir les fichiers Google) | C |
| `style` | string | `"normal"`, `"italic"` | C |
| `size` | objet | `{"desktop":3.2,"tablet":2.6,"mobile":2.2}` | B |
| `sizeType` | string | `"px"` (par défaut si absent), `"rem"`, `"em"`, `"vw"`… | B (`px`, `rem`) |
| `lineHeight` | objet | `{"desktop":1.1,"tablet":…,"mobile":…}` | B (bureau), L (tablette et mobile : `line-height:1.2` et `1.3`, sans unité, avec `lineType: "-"`) |
| `lineType` | string | `"-"` ou absent : sans unité ; sinon `"px"`, `"em"`, `"rem"` | B (`-`) |
| `letterSpacing` / `spacingType` | objet / string | `{"desktop":0.02}` / `"em"` (par défaut) | C |
| `transform` | string | `"uppercase"`… | C |
| `color` | string | `"paletteN"` ou une couleur | B |
| `fallback` | string | **Lu seulement si `google` vaut `true`.** La valeur est ajoutée après la famille (`"serif"`…) ; si elle est absente ou vide, c'est `var(--global-fallback-font)` (`sans-serif`) ; `"handwriting"` donne `cursive`. **Si `google` vaut `false`, `fallback` est ignoré** et la famille est écrite seule : mettre la pile complète dans `family`. | C, L (`google: false` : `'Hanken Grotesk'` seul ; `google: true` : `'Hanken Grotesk', serif`) |
| `clamped`, `minFontSize`, `maxFontSize`, `minScreenSize`, `maxScreenSize`, `fontSizeUnit`, `screenSizeUnit` | bool / nombres / string | taille fluide `clamp()` au bureau (si `clamped` vaut `true`) | C |

Résultat mesuré (B, avec `?sans-pd`) :
- `body` : 17 px, interlignage 27,2 px, Hanken Grotesk, `rgb(232,230,225)`.
- `h1` : Newsreader 400, **51,2 px** (bureau), **41,6 px** (900 px), **35,2 px** (375 px), interlignage 1.1.
- `h2` : 38,4 / 33,6 / 28,8 px.
- `h3` : 25,6 / 23,2 / 20,8 px.

```php
set_theme_mod( 'h1_font', array(
	'size' => array( 'desktop' => 3.2, 'tablet' => 2.6, 'mobile' => 2.2 ), 'sizeType' => 'rem',
	'lineHeight' => array( 'desktop' => 1.1 ), 'lineType' => '-',
	'family' => 'inherit', 'google' => false, 'weight' => '400', 'variant' => 'regular', 'color' => 'palette3',
) );
set_theme_mod( 'heading_font', array( 'family' => '"Newsreader", Georgia, "Times New Roman", serif' ) );
```

### 3.3 Polices Google : désactiver ou charger localement

| Clé / filtre | Type | Effet | Défaut | Vérif. |
|---|---|---|---|---|
| sous-clé `google: true` d'une typographie | bool | ajoute la police à la feuille Google `kadence-fonts-gfonts` dans `<head>` | `false` partout | B |
| filtre `kadence_print_google_fonts` | bool | `false` : **aucune** feuille Google, ni distante ni locale, **y compris pour les polices des blocs Kadence**. Avec le thème Kadence, les polices Google des blocs sont fusionnées dans la feuille du thème, qui force `kadence_blocks_print_google_fonts` à `false`. | `true` | B |
| filtres `kadence_blocks_print_google_fonts`, `kadence_blocks_print_footer_google_fonts` | bool | n'ont d'effet que **sans** le thème Kadence. Avec lui, les retirer ne fait réapparaître aucun lien. | `true` | B (sans effet constaté), C |
| `load_fonts_local` | bool | `true` : Kadence **télécharge** les fichiers chez Google au premier affichage, les sert depuis `wp-content/fonts/` et ajoute des `<link rel="preload">` | `false` | B |
| `preload_fonts_local` | bool | préchargement des polices locales (seulement si `load_fonts_local` vaut `true`) | `true` | B |
| `google_subsets` | objet | `{"latin-ext":false,"cyrillic":false,…}` : sous-ensembles ajoutés à l'URL Google | tout à `false` | C |
| `load_base_italic` | bool | charge aussi l'italique de la police de base (Google) | `false` | C |

Constaté dans le bac à sable avec `base_font.family = "Roboto"` et `google: true` :
- avec `kadence_print_google_fonts` à `false` : aucun lien, mais `--global-body-font-family: Roboto, var(--global-fallback-font)` (la police n'est **pas** chargée, le navigateur prend la police de secours) ;
- sans le filtre : `<link id="kadence-fonts-gfonts-css" href="https://fonts.googleapis.com/css?family=Roboto:regular,700&display=swap">` ;
- avec `load_fonts_local: true` : `href="…/wp-content/fonts/<hash>.css?ver=1.5.2"` et `preload` de `…/wp-content/fonts/roboto/….woff2`.

Le même filtre bloque un `kadence/advancedheading` avec `"typography":"Roboto","googleFont":true`. Le titre est alors affiché en police de secours. **Dans les specs, ne pas utiliser `googleFont: true`.** [B]

**Pour ce site** : `google: false` partout. Les polices sont déclarées par `kadence-pascal/assets/fonts.css` (`@font-face`, fichiers woff2 locaux). Constaté : seules « Newsreader 400 500 » et « Hanken Grotesk 400 600 » sont chargées, et **aucune requête** vers `fonts.googleapis.com` ni `fonts.gstatic.com`. [B]

### 3.4 Déclarer des polices personnalisées dans les listes de choix

Il **n'existe pas** de filtre `kadence_custom_fonts` (aucune occurrence dans le thème ni dans l'extension). Les filtres réels sont les suivants : [B]

| Filtre | Où la liste apparaît | Format d'entrée | Format produit |
|---|---|---|---|
| `kadence_theme_add_custom_fonts` | outil de personnalisation du thème. Le filtre n'est lu que sur `customize_controls_enqueue_scripts` et alimente `kadence_theme_custom_fonts`, visible dans `kadenceCustomizerControlsData.cfontvars`. | `[ 'Hanken Grotesk' => [ 'fallback' => 'system-ui, sans-serif', 'weights' => ['400','500','600'] ] ]` | clé `"\"Hanken Grotesk\", system-ui, sans-serif"` → `{"v":["400","500","600"]}` |
| `kadence_theme_custom_fonts` | idem (forme finale) | `[ '<famille CSS>' => [ 'v' => [ variantes ] ] ]` | — |
| `kadence_blocks_add_custom_fonts` | éditeur de blocs Kadence. Le filtre n'est lu que dans l'administration (`init`, priorité 11) et alimente `kadence_blocks_custom_fonts`, visible dans `kadence_blocks_params.c_fonts`. | même format que `kadence_theme_add_custom_fonts` | `{"name":"\"Hanken Grotesk\", system-ui, …","weights":["400","500","600"],"styles":[]}` |
| `kadence_blocks_custom_fonts` | idem (forme finale) | `[ '<famille CSS>' => [ 'name' => …, 'weights' => […], 'styles' => […] ] ]` | — |

Ces filtres **ne chargent aucun fichier** : ils ne font qu'ajouter des noms aux listes. Le chargement (`@font-face`) reste à la charge du thème enfant. La famille enregistrée quand on choisit la police dans l'interface est **la clé complète** (`"Hanken Grotesk", system-ui, …`). En écrivant la même chaîne dans `base_font.family`, l'outil de personnalisation affiche la bonne police : constaté, `wp.customize('base_font').get().family` est identique. [B]

---

## 4. Fonds et couleurs des liens

| Clé | Type | Format | Défaut | CSS produit | Vérif. |
|---|---|---|---|---|---|
| `site_background` | objet | `{"desktop":{"color":"palette9"},"tablet":{…},"mobile":{…}}` ; chaque palier : `color`, `type` (`"color"` par défaut, `"image"` ou `"gradient"`), `gradient` (chaîne CSS), `image` : `{"url","repeat","size","attachment","position":{"x":0.5,"y":0.5}}` | `{"desktop":{"color":"palette8"}}` | `body{background:var(--global-palette9);}` | B (`color`), C (reste) |
| `content_background` | objet | même format | `{"desktop":{"color":"palette9"}}` | `.content-bg, body.content-style-unboxed .site{background:…}` | B |
| `link_color` | objet | `{"highlight":"palette5","highlight-alt":"palette3","highlight-alt2":"palette9","style":"color-underline"}` | `{"highlight":"palette1","highlight-alt":"palette2","highlight-alt2":"palette9","style":"standard"}` | `--global-palette-highlight`, `-alt`, `-alt2`, et classe `link-style-{style}` sur `<body>` | B |

Valeurs de `link_color.style`, avec leur effet dans `.entry-content` (`global.min.css`) :
- `standard` : soulignement, couleur `highlight`, puis `highlight-alt` au survol ;
- `color-underline` : texte de couleur `inherit`, **soulignement** de couleur `highlight`, puis `highlight-alt` au survol ;
- `no-underline` : couleur `highlight`, sans soulignement ;
- `hover-background` : couleur `highlight` et soulignement de 1 px ; au survol, fond `highlight` plein et texte `highlight-alt2` ;
- `offset-background` : bande de couleur décalée sous le texte.

Pour `color-underline`, mesuré (B) : texte `rgb(232,230,225)` (hérité), soulignement `rgb(200,178,135)` (palette5). Les autres styles n'ont pas été mesurés. [C]

En dehors du contenu, un `<a>` prend `color: var(--global-palette-highlight)`. **Ne pas laisser `highlight` sur palette1** dans un thème sombre (2,71:1). [C]

---

## 5. Boutons globaux

Ces réglages s'appliquent à `button, .button, .wp-block-button__link, input[type=submit|button|reset]` et à `kadence/singlebtn` réglé sur « hériter du thème ».

| Clé | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `buttons_color` | objet | `{"color":"palette3","hover":"palette3"}` (texte) | `{"color":"palette9","hover":"palette9"}` | B |
| `buttons_background` | objet | `{"color":"palette1","hover":"palette2"}` ; dégradé `linear-…`/`radial-…` accepté | `{"color":"palette1","hover":"palette2"}` | B |
| `buttons_border_radius` | objet | `{"size":{"desktop":2,"tablet":"","mobile":""},"unit":{"desktop":"px","tablet":"px","mobile":"px"}}` ; unités `px`, `em`, `rem`, `%` | tailles vides : 3 px de la feuille de base | B |
| `buttons_padding` | objet | `{"size":{"desktop":[haut,droite,bas,gauche]},"unit":{"desktop":"px"},"locked":{"desktop":false}}` | vides : `.4em 1em` | C |
| `buttons_border` / `buttons_border_colors` | objet | bordure responsive / `{"color":"","hover":""}` | `[]` / vides | C |
| `buttons_shadow`, `buttons_shadow_hover` | objet | `{"color":"rgba(0,0,0,0.1)","hOffset":0,"vOffset":15,"blur":25,"spread":-7,"inset":false,"disabled":false}` | voir à gauche (survol) | C |
| `buttons_typography` | objet | typographie (§ 3.2) | `family: inherit` | C |
| `buttons_secondary_*` | idem | mêmes sous-clés (`color`, `background`, `border_radius`…) | texte palette3 / palette9 au survol, fond palette7 / palette2 au survol | B (fond palette7 mesuré) |
| `buttons_outline_*` | idem | `buttons_outline_color`, `_border_colors`, `_border_radius`… | vides : couleur = `--global-palette-btn-bg`, donc palette1 | B (contour rouge mesuré) |

Mesures (B, page `ref-theme-reglages-bac-boutons`, `?sans-pd`) :

| Bouton | Fond | Texte | Rayon |
|---|---|---|---|
| `core/button` | `rgb(163,48,47)` | `rgb(232,230,225)` | **2 px** |
| `core/button` + `is-style-outline` | transparent | **`rgb(163,48,47)`, illisible** | 2 px ; bordure 2 px |
| `kadence/singlebtn` sans `inheritStyles` (= `"fill"`) | palette1 | palette3 | **3 px** : le rayon global n'est **pas** appliqué. Cause : la règle `.kb-button:not(.kb-btn-global-inherit){border-radius:3px}` de `kadence-blocks-advancedbtn-css`, chargée après le CSS du thème |
| `kadence/singlebtn` `"inheritStyles":"outline"` | transparent | palette1 | 3 px |
| `kadence/singlebtn` `"inheritStyles":"inherit"` | palette1 | palette3 | **2 px** : reprend tous les réglages globaux (classe `wp-block-button__link`) |
| `kadence/singlebtn` `"inheritStyles":"inherit-secondary"` | **palette7** `rgb(34,48,64)` | palette3 | 2 px (classe `button-style-secondary`) |

Spec testée (attributs relus avec `lire.php`, sérialisés tels quels) :
```json
{"name":"kadence/advancedbtn","attributes":{"uniqueID":"trb-btns"},"innerBlocks":[
 {"name":"kadence/singlebtn","attributes":{"uniqueID":"trb-btn-2","text":"Bouton inherit","link":"#b2","inheritStyles":"inherit"}},
 {"name":"kadence/singlebtn","attributes":{"uniqueID":"trb-btn-3","text":"Bouton inherit-secondary","link":"#b3","inheritStyles":"inherit-secondary"}}]}
```
→ **Pour que les boutons Kadence suivent les réglages globaux, mettre `"inheritStyles":"inherit"`** (ou `"inherit-secondary"`). La valeur par défaut `"fill"` ne reprend que les couleurs. [B]

---

## 6. Largeur du conteneur et espacements globaux

| Clé | Type | Format | Défaut | CSS / effet | Vérif. |
|---|---|---|---|---|---|
| `content_width` | objet | `{"size":72,"unit":"rem"}` ; unités **`px`, `em`, `rem` uniquement** (`vw` existe aussi dans le calcul de la largeur élargie). Bornes de l'interface : 400 à 2000 px, 30 à 140 em ou rem. | `{"size":1290,"unit":"px"}` | `--global-content-width` ; `max-width` de `.site-container`, du conteneur de l'en-tête et du pied | B : 1152 px |
| `content_narrow_width` | objet | idem | `{"size":842,"unit":"px"}` | largeur des pages « étroites » (`.content-width-narrow`) | B : 842 px |
| `content_edge_spacing` | objet | `{"size":{"desktop":1.25,"tablet":"","mobile":""},"unit":{"desktop":"rem",…}}` | 1.5 rem au bureau | `--global-content-edge-padding`, padding gauche et droit de `.site-container` (inclus dans `max-width`, `border-box`) | B : 20 px aux 3 largeurs |
| `content_spacing` | objet | même format | 5 / 3 / 2 rem | `margin-top`/`margin-bottom` de `.content-area` (marges verticales des pages) | B : 80 / 48 / 32 px |
| `boxed_spacing` | objet | même format | 2 / 2 / 1.5 rem | `--global-content-boxed-padding` (padding de l'article en mode « boîte ») | C |

`--global-content-wide-width` vaut `calc(72rem + 10rem)` en rem et `calc(1290px + 230px)` en px. [L]

```php
set_theme_mod( 'content_width', array( 'size' => 72, 'unit' => 'rem' ) );
```

---

## 7. Mise en page par défaut des pages (theme mods `page_*`)

Les mêmes clés existent pour les articles (`post_layout`, dont la valeur par défaut est `narrow`, `post_content_style`…) et pour chaque type de contenu (`{type}_layout`…). Kadence lit en effet `option( $post_type . '_layout' )`. [C]

| Clé | Type | Valeurs | Défaut | Classe sur `<body>` | Vérif. |
|---|---|---|---|---|---|
| `page_layout` | string | `normal`, `narrow`, `fullwidth`, `left`, `right` (barre latérale) | `normal` | `content-width-{…}` pour `normal`, `narrow` et `fullwidth`. **`left` et `right` donnent `content-width-normal has-sidebar`**, plus `has-left-sidebar` pour `left`, et non `content-width-left` comme la méta `_kad_post_layout` (§ 8) | B (`fullwidth`), L (`left`, `right`) |
| `page_content_style` | string | `boxed`, `unboxed` | `boxed` | `content-style-{…}` | B (`unboxed`) |
| `page_vertical_padding` | string | `show`, `hide`, `top`, `bottom` | `show` | `content-vertical-padding-{…}` | B (`hide`) |
| `page_title` | **bool** | `true`, `false` | `true` | `content-title-style-hide` si `false` | B |
| `page_title_layout` | string | `normal` (dans le contenu), `above` (bandeau au-dessus) | `above` | `content-title-style-{…}` | T (`above`) |
| `page_title_inner_layout` | string | `standard`, `fullwidth`, `contained` | `standard` | — | C |
| `page_title_height`, `page_title_align`, `page_title_background`, `page_title_font`, `page_title_elements` | objets | voir `\Kadence\Options\Component::defaults()` | — | — | C |
| `page_feature` | bool | image mise en avant affichée | `false` | — | C |
| `page_feature_position` | string | `above`, `behind`, `below` | `above` | — | C |
| `page_sidebar_id` | string | identifiant de zone de widgets | `sidebar-primary` | — | C |
| `page_background`, `page_content_background` | objet ou `""` | même format que `site_background` | `""` | — | C |
| `page_comments` | bool | | `false` | — | C |

Mesuré (B), page **sans aucune méta**, avec `page_layout=fullwidth`, `page_content_style=unboxed`, `page_vertical_padding=hide` et `page_title=false` :
- classes `content-title-style-hide content-width-fullwidth content-style-unboxed content-vertical-padding-hide` ;
- conteneur `max-width: none`, 1280 px ;
- `.content-area` marges 0 ;
- pas de titre, pas d'ombre sur l'article.

Ces 4 theme mods remplacent donc les 4 méta que `construire.py` pose sur chaque page.

---

## 8. Méta par page `_kad_post_*` (clé `"meta"` des specs)

Méta déclarées par `register_post_meta( '', …, show_in_rest => true )` pour tous les types de contenu. On les écrit avec la clé `"meta"` de la spec. **Une méta absente, vide ou invalide renvoie au réglage du thème (§ 7)**, puis au défaut de Kadence.

| Méta | Type | Valeurs acceptées par le rendu PHP | Vide, `default` ou invalide | Vérif. |
|---|---|---|---|---|
| `_kad_post_layout` | string | `normal`, `narrow`, `fullwidth`, `left`, `right` | `default` ou `""` : `page_layout`. **Une valeur invalide donne `normal`, pas `page_layout`** : constaté, `pleine` donne `content-width-normal` alors que `page_layout` vaut `fullwidth`. | T (toutes sauf `right`), B (`normal`, `narrow`, valeur invalide) |
| `_kad_post_content_style` | string | `boxed`, `unboxed` | vide, `default` ou invalide : `page_content_style` | T, B (invalide : `unboxed`, la valeur du theme mod) |
| `_kad_post_vertical_padding` | string | `show`, `hide`, `top`, `bottom` | vide, `default` ou invalide : `page_vertical_padding` | T (les 4), B (`top` : marge haute 80 px, basse 0 ; invalide : `hide`, la valeur du theme mod) |
| `_kad_post_title` | string | `hide`, `normal`, `above`, `show` (`show` : affiché selon `page_title_layout`, **même si `page_title` vaut `false`**) | vide, `default` ou invalide : `page_title` puis `page_title_layout` | T (les 4), B (`show` avec `page_title=false` : titre affiché ; invalide : masqué, comme `page_title=false`) |
| `_kad_post_feature` | string | `show`, `hide` | `page_feature` | T (`hide` enregistré), effet non vérifié |
| `_kad_post_feature_position` | string | `above`, `behind`, `below` | `page_feature_position` | C |
| `_kad_post_sidebar_id` | string | identifiant de zone de widgets (`default` ou vide : `page_sidebar_id`) | | C |
| `_kad_post_transparent` | string | `enable`, `disable` (en-tête transparent) | réglage `transparent_header_*` | T (`enable` : classes `transparent-header mobile-transparent-header`) |
| `_kad_post_header` | **boolean** | `true` : **pas d'en-tête** (classe `no-header`) | `false` | T (enregistré `"1"`, `#masthead` absent) |
| `_kad_post_footer` | **boolean** | `true` : **pas de pied de page** (classe `no-footer`) | `false` | T (`#colophon` absent) |
| `_kad_post_classname` | string | classe(s) ajoutée(s) telles quelles à `<body>`, séparées par des espaces | | T (`"pd-essai-classe pd-deuxieme"` : 2 classes) |

Spec testée (page `ref-theme-reglages-meta-plein`) :
```json
{"titre":"…","slug":"…","meta":{"_kad_post_layout":"fullwidth","_kad_post_content_style":"unboxed",
 "_kad_post_vertical_padding":"hide","_kad_post_title":"hide","_kad_post_feature":"hide"},"blocs":[…]}
```

Résultats (classes de `<body>` sur le site partagé, toutes les pages en `post_type = page`) :

| Page | Méta | Classes obtenues | En-tête du contenu |
|---|---|---|---|
| `meta-defaut` | aucune | `content-title-style-above content-width-normal content-style-boxed content-vertical-padding-show` | titre dans le bandeau |
| `meta-plein` | ci-dessus | `…-title-style-hide …-width-fullwidth …-style-unboxed …-vertical-padding-hide` | aucun titre |
| `meta-etroit` | `narrow`, `boxed`, `top`, `normal` | `…-title-style-normal …-width-narrow …-style-boxed …-vertical-padding-top` | titre dans le contenu |
| `meta-show` | `default`, `default`, `bottom`, `show` | `…-title-style-above …-width-normal …-style-boxed …-vertical-padding-bottom` | bandeau |
| `meta-invalide` | `pleine`, `aucun`, `rien`, `cache` | comme `meta-defaut` (avec les réglages par défaut de Kadence) | bandeau |
| `meta-sans-entete` | `left`, `_kad_post_header: true`, `_kad_post_footer: true`, `above` | `no-header no-footer has-sidebar has-left-sidebar …-width-left` | `#masthead` et `#colophon` absents, `#secondary` présent |

À noter :
- Quand la spec contient `"meta"`, l'éditeur enregistre **les 11 méta**, avec `""` pour celles qu'on n'a pas données. Sans `"meta"`, il n'en enregistre aucune. [T]
- La page d'accueil statique lit les méta de la page choisie dans `page_on_front`. [C]

---

## 9. Bouton « remonter »

| Clé | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `scroll_up` | bool | active le bouton (`<a id="kt-scroll-up">` et `<button id="kt-scroll-up-reader">` dans le pied de page) | `false` | B |
| `scroll_up_style` | string | `filled`, `outline`, `secondary` | `outline` | B (`filled`) |
| `scroll_up_side` | string | `left`, `right` | `right` | B |
| `scroll_up_icon` | string | `arrow-up`, `arrow-up2`, `chevron-up`, `chevron-up2` | `arrow-up` | B (`arrow-up`) |
| `scroll_up_icon_size` | objet | `{"size":{"desktop":1.2,…},"unit":{"desktop":"em",…}}` | 1.2 em | B (valeur par défaut) |
| `scroll_up_side_offset`, `scroll_up_bottom_offset` | objet | même format. Unités : `px`, `em`, `rem`, plus **`vw` pour `scroll_up_side_offset` seulement** et **`vh` pour `scroll_up_bottom_offset` seulement** | 30 px | B (valeur par défaut, 30 px), C (unités) |
| `scroll_up_visiblity` (*sic*, sans le second i) | objet | `{"desktop":true,"tablet":true,"mobile":false}` | idem | B : classes `vs-lg-true vs-md-true vs-sm-false` |
| `scroll_up_color`, `scroll_up_background`, `scroll_up_border_colors` | objet | `{"color":"palette3","hover":"palette9"}` | vides | B (`color`) |
| `scroll_up_radius` | objet | `{"size":[2,2,2,2],"unit":"px","locked":true}` (tableau de 4) | 0 | B |
| `scroll_up_padding` | objet | `{"size":{"desktop":[0.4,0.4,0.4,0.4]},"unit":{"desktop":"em"},"locked":{"desktop":true}}` | 0.4 em | B (valeur par défaut) |
| `scroll_up_border` | objet | bordure | `[]` | C |

Mesuré : fond `rgb(34,48,64)` (palette7), texte palette3, rayon 2 px, `right: 30px`, `bottom: 30px`, classes `scroll-up-side-right scroll-up-style-filled`. Le script du thème rend le bouton visible après défilement. [B]

---

## 10. Fonction PHP prête à l'emploi (testée en B)

À copier dans `kadence-pascal/inc/reglages-kadence.php`, puis à charger depuis `functions.php` :
```php
require get_stylesheet_directory() . '/inc/reglages-kadence.php';
```
Copie testée : `scratchpad/ref/theme-reglages/reglages-kadence.php`.

Quand les réglages s'appliquent :
- **à l'activation du thème enfant** (`after_switch_theme`, exécuté au chargement suivant) ;
- **une fois par version** sur un site où le thème est déjà actif, à la première visite de l'administration. Augmenter `PD_KADENCE_REGLAGES_VERSION` **écrase** les changements faits entre-temps dans l'outil de personnalisation.

```php
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
	return $polices;
}
add_filter( 'kadence_theme_add_custom_fonts', 'pd_kadence_polices_perso' );
add_filter( 'kadence_blocks_add_custom_fonts', 'pd_kadence_polices_perso' );
```

Constaté dans le bac à sable après `switch_theme( 'kadence' )` puis `switch_theme( 'kadence-pascal' )` : [B]
- au chargement suivant :
  - `kadence_global_palette` contient la chaîne JSON avec 3 × 15 couleurs (`autoload` à `auto`) ;
  - `pd_kadence_reglages` vaut `1` ;
  - `theme_mods_kadence-pascal` contient les **28** clés. Les valeurs du § 10 étant déjà complètes, la fusion avec les défauts n'a fait que réordonner les sous-clés de `h1_font` à `h6_font` : c'est un filet de sécurité pour les ajouts futurs. `scroll_up_radius` est bien enregistré comme un tableau de 4 nombres ;
- les clés existantes (`nav_menu_locations`, `initial_version`) sont conservées ;
- WordPress a ajouté `sidebars_widgets` au passage ;
- une ouverture de l'administration ensuite ne réapplique rien.

Rendu, avec `?sans-pd` :
- fond `rgb(13,18,23)` sur `body` et `.content-bg` ;
- texte `rgb(232,230,225)` ;
- conteneur de 1152 px ;
- polices locales seulement.

---

## 11. Variante sans écriture en base : filtrer les valeurs par défaut

Au lieu d'écrire en base, le thème enfant peut **changer les valeurs par défaut** de Kadence. Rien n'est stocké, et un réglage enregistré plus tard dans l'outil de personnalisation reste prioritaire. Le `functions.php` de l'enfant est chargé **avant** celui du parent, donc les filtres sont en place à temps. Vérifié en L : filtres pré-enregistrés, base sans palette ni theme mod.
- `palette1` vaut `#a3302f`, `palette9` vaut `#0d1217` ;
- `option('page_layout')` vaut `fullwidth` alors que `get_theme_mod('page_layout')` vaut `false` ;
- le CSS contient `body{background:var(--global-palette9);}`.

```php
add_filter( 'kadence_theme_options_defaults', function ( $d ) {
	$d['page_layout']        = 'fullwidth';
	$d['site_background']    = array( 'desktop' => array( 'color' => 'palette9' ) );
	$d['base_font']['color'] = 'palette3'; // ici, on peut ne modifier qu'une sous-clé
	return $d;
} );
add_filter( 'kadence_global_palette_defaults', function () {
	return pd_kadence_palette_json(); // fonction du § 10
} );
```
Avantage : on peut ne modifier qu'une sous-clé, puisqu'on part du défaut complet.
Inconvénients :
- `get_theme_mod()` ne voit rien : seul `\Kadence\kadence()->option()` en tient compte ;
- `get_option( 'kadence_global_palette' )` reste `false`.

---

## 12. Pièges constatés (résumé)

1. Une valeur partielle remplace tout le défaut : par exemple, `base_font` sans `size` supprime la taille du texte. [B]
2. Une palette passée en **tableau** à `update_option` provoque une erreur fatale `TypeError`. Il faut une chaîne `wp_json_encode(…)`. [B]
3. L'entrée n° *n* doit avoir le slug `palette{n}`, sinon la couleur est vide. [B]
4. `palette10 = "#FfFfFf"` (casse exacte) n'est pas une couleur mais le marqueur « complémentaire automatique ». [B]
5. Les theme mods dépendent du **thème actif**. Les écrire pendant que `kadence` est actif ne sert à rien pour `kadence-pascal`. [C, cohérent avec B]
6. `after_switch_theme` ne s'exécute qu'au chargement suivant. Un script qui fait `switch_theme()` puis lit les réglages dans le même processus ne voit rien. [B]
7. `page_title` est un **booléen** (theme mod), alors que `_kad_post_title` est une **chaîne** (`hide`, `show`…). [B, T]
8. `_kad_post_title: "show"` affiche le titre même si `page_title` vaut `false`. [B]
9. Une valeur de méta invalide n'est pas signalée. Pour `_kad_post_content_style`, `_kad_post_vertical_padding` et `_kad_post_title`, elle se comporte comme `default`. Pour `_kad_post_layout`, elle force `normal`, même si `page_layout` vaut `fullwidth`. [T, B]
10. `kadence/singlebtn` sans `inheritStyles` n'applique pas le rayon global (3 px au lieu de 2 px). Utiliser `"inheritStyles":"inherit"`. [B]
11. Les boutons « contour » et les liens prennent palette1 par défaut, illisible sur fond sombre : 2,71:1. [B, calcul]
12. `palette6` sert au texte indicatif des champs : en « ligne » #2c3a49, il est illisible (1,62:1). Le prévoir dans `pd.css` (`::placeholder`). [C]
13. Avec `kadence_print_google_fonts` à `false`, une police déclarée `google: true` (thème ou bloc) n'est **pas chargée**, mais son nom reste dans le CSS. [B]
14. `pd-kadence.css` (thème enfant actuel) écrase avec `!important` la largeur, les marges, le titre et les fonds de **toutes** les pages : sur le site partagé, les méta n'ont d'effet visible que dans les classes de `<body>`. [T]

---

## 13. Ce qui n'a PAS été vérifié par un essai

- Les écritures (`update_option`, `set_theme_mod`) n'ont été faites **que dans le bac à sable** (copie privée, port 8091), jamais sur le site partagé. Sur le site partagé, la lecture a été simulée en mémoire.
- `second-palette` et `third-palette` dans l'outil de personnalisation : bascule par l'interface et affichage des noms.
- Les filtres `kadence_active_palette`, `kadence_palette_option` et `kadence_palette_complement_color`.
- Typographie :
  - les sous-clés `letterSpacing`/`spacingType`, `transform`, `style`, `fallback` ;
  - la taille fluide (`clamped`, `minFontSize`…) ;
  - `lineHeight` par palier (tablette, mobile) : CSS produit vérifié depuis en lecture seule (voir « Contre-vérification »), rendu non mesuré ;
  - `title_above_font`, `buttons_typography`, `font_rendering`, `google_subsets`, `load_base_italic` ;
  - `variant` en tableau pour `heading_font` en police Google ;
  - les tailles h4 à h6 (lues dans le CSS produit, non mesurées dans la page).
- Fonds :
  - `site_background` et `content_background` de type `image` ou `gradient` ;
  - les fonds par palier (`tablet`, `mobile`) ;
  - `page_background`, `page_content_background`.
- `link_color.style` : `standard` (seule la classe a été vue, sans réglage), `no-underline`, `hover-background`, `offset-background`.
- Boutons :
  - `buttons_padding`, `buttons_border`, `buttons_border_colors`, ombres ;
  - les réglages `buttons_secondary_*` et `buttons_outline_*` modifiés (seules leurs valeurs par défaut ont été mesurées).
- Largeurs et espacements :
  - `boxed_spacing` ;
  - `content_width` en `px` ou `em` (seul `rem` a été testé ; `px` seulement en valeur par défaut) ;
  - `content_edge_spacing` par palier.
- Mise en page des pages :
  - `page_layout` `left`/`right` comme réglage global : seul le résultat de `check_conditionals()` a été vérifié en lecture seule (voir « Contre-vérification »), sans rendu. `_kad_post_layout: "right"` n'a pas été testé du tout ;
  - `page_title_layout: "normal"` comme réglage global ;
  - `page_title_inner_layout`, `page_title_*` (hauteur, fond, alignement, éléments) ;
  - `page_feature`, `page_feature_position`, `page_sidebar_id`.
- Méta :
  - effet de `_kad_post_feature` (aucune page d'essai n'avait d'image mise en avant) ;
  - `_kad_post_feature_position`, `_kad_post_sidebar_id` ;
  - `_kad_post_transparent: "disable"`.
- Bouton « remonter » :
  - styles `outline` et `secondary`, côté `left`, autres icônes, `scroll_up_border` ;
  - l'apparition au défilement (page trop courte : `opacity` 0 constatée).
- La lecture des réglages par l'éditeur au-delà de la palette : la police et la couleur du texte dans le canevas de l'éditeur n'ont pas été contrôlées.
- `kadence_theme_option_type = 'option'` (stockage dans `kadence_settings`).

---

## 14. Pages et fichiers d'essai

Site partagé (`http://127.0.0.1:8080/`), pages créées avec `editeur.js construire` :

| Page | Ce qu'elle montre |
|---|---|
| `ref-theme-reglages-meta-defaut` | aucune méta : réglages par défaut de Kadence |
| `ref-theme-reglages-meta-plein` | `fullwidth` + `unboxed` + `hide` + titre `hide` + image `hide` |
| `ref-theme-reglages-meta-etroit` | `narrow` + `boxed` + `top` + titre `normal` |
| `ref-theme-reglages-meta-show` | `default` + `default` + `bottom` + titre `show` |
| `ref-theme-reglages-meta-invalide` | valeurs invalides : retour au défaut |
| `ref-theme-reglages-meta-sans-entete` | `left` + `_kad_post_header`/`_kad_post_footer` à `true` + titre `above` |
| `ref-theme-reglages-meta-classe` | `_kad_post_classname` (2 classes) + `_kad_post_transparent: "enable"` |

Fichiers de travail dans `/tmp/claude-0/-home-user-pascaldupont-fr/9562e8de-1adf-51fb-b316-6cc9700228e2/scratchpad/ref/theme-reglages/`. Ce dossier est temporaire et propre à la session : les éléments essentiels sont recopiés dans cette fiche.
- `reglages-kadence.php` : la fonction du § 10 ;
- `lecture-seule.php` : essai L, sans écriture, contrôle SQL avant et après. Lancer `php lecture-seule.php` (simulation) ou `php lecture-seule.php sans-simulation` (état réel) ;
- `lecture-seule-defauts.php` : essai L de la variante du § 11 ;
- `defauts.php` : affiche les valeurs par défaut, par exemple `php defauts.php 'page_*' 'h?_font'` ;
- bac à sable :
  - `bac/` : copie du WordPress ; à servir avec `php -S 127.0.0.1:8091 -t bac outils/wp-test/router.php` ;
  - `bac-basculer.php`, `bac-etat.php`, `bac-pieges.php`, `bac-google.php` : scripts du bac à sable ;
  - `editeur-bac.js` : copie de l'outil, lancée avec `--base http://127.0.0.1:8091` ;
  - `mesurer.js`, `boutons.js`, `polices-admin.js` : mesures du rendu, des boutons et des listes de polices ;
  - pages du bac à sable : `ref-theme-reglages-bac-defaut`, `-bac-normal`, `-bac-etroit`, `-bac-invalide`, `-bac-boutons`, `-bac-police-blocs` ;
- `specs/` : specs JSON de toutes les pages.

Pour revérifier un réglage sans toucher au site partagé :
1. recréer le bac à sable : copier `wp/` sans la base, copier la base avec `SQLite3::backup()`, puis remplacer `8080` par `8091` dans `wp-config.php` et le chemin dans `wp-content/db.php` ;
2. y écrire la valeur (`set_theme_mod` dans un script `wp-load.php` dont `HTTP_HOST` vaut `127.0.0.1:8091`) ;
3. mesurer avec `node mesurer.js "http://127.0.0.1:8091/<slug>/?sans-pd" 1280`.

---

## Contre-vérification (7 octobre 2026)

Relecture sceptique : on a cherché à réfuter les affirmations les plus utiles à un développeur, dans le code source puis par des essais. Sur le site partagé, rien n'a été écrit en dehors des pages `ref-theme-reglages-verif-*` : ni option, ni theme mod, ni fichier. Les theme mods ont été simulés en mémoire avec les filtres `theme_mod_*` et `pre_option_*`, et une empreinte SQL prise avant et après a confirmé que la base n'avait pas changé.
Fichiers : `scratchpad/ref/theme-reglages-verif/` (`specs/`, `meta.php`, `simulation.php`, `simulation-par10.php`, `boutons-mesure.js`, `boutons-regles.js`, `defauts.php`).

### Specs rejouées avec `editeur.js construire`

Les specs de la fiche ont été rejouées sans changement, sauf le slug et les `uniqueID`. Résultat : 0 bloc invalide, 0 erreur JS. Les captures à 1280 et 375 px ne montrent aucun débordement.

| Page | Spec d'origine | Méta relues (`get_post_meta`) | Classes de `<body>` | Résultat |
|---|---|---|---|---|
| `ref-theme-reglages-verif-plein` | `meta-plein` | les 11 méta ; `""` pour celles qui ne sont pas données | `content-title-style-hide content-width-fullwidth content-style-unboxed content-vertical-padding-hide` | conforme |
| `ref-theme-reglages-verif-sans-entete` | `meta-sans-entete` | `_kad_post_header` et `_kad_post_footer` = `'1'` | `no-header no-footer has-sidebar has-left-sidebar content-width-left` ; `#masthead` et `#colophon` absents, `#secondary` présent | conforme |
| `ref-theme-reglages-verif-invalide` | `meta-invalide` | `pleine`, `aucun`, `rien`, `cache` enregistrés tels quels | `content-title-style-above content-width-normal content-style-boxed content-vertical-padding-show` | conforme |
| `ref-theme-reglages-verif-show` | `meta-show` | `default`, `default`, `bottom`, `show` | `content-title-style-above content-width-normal content-style-boxed content-vertical-padding-bottom` | conforme |
| `ref-theme-reglages-verif-classe` | `meta-classe` | `_kad_post_classname` = `'pd-essai-classe pd-deuxieme'` | `pd-essai-classe pd-deuxieme … transparent-header mobile-transparent-header` | conforme |
| `ref-theme-reglages-verif-boutons` | `bac-boutons` | — | sérialisation identique à la spec (`"inheritStyles":"inherit"` / `"inherit-secondary"`) ; classes `kb-btn-global-fill`, `kb-btn-global-outline`, `kb-btn-global-inherit` + `wp-block-button__link`, et `+ button-style-secondary` pour `inherit-secondary` | conforme |

Rayon des boutons, mesuré sur `verif-boutons` sans `pd.css` ni `pd-kadence.css`. Une règle `border-radius:2px` a été ajoutée **dans** `#kadence-global-inline-css` pour simuler `buttons_border_radius` à sa place dans la cascade. Résultat : `fill` et `outline` restent à **3 px** ; `inherit`, `inherit-secondary` et `core/button` passent à **2 px**. Cela confirme le § 5 et sa recommandation `"inheritStyles":"inherit"`.
Piège de mesure : les boutons ont `transition: all .2s`. Une mesure prise juste après un changement donne une valeur intermédiaire (2,93 px). Attendre au moins 300 ms avant `getComputedStyle`.

### Vérifié en lecture seule (theme mods simulés)

- `_kad_post_layout` invalide → `layout=normal`, même avec `page_layout=fullwidth`. Les autres méta invalides retombent sur le theme mod : `unboxed`, `hide`, et le titre `hide` si `page_title=false`. **Confirmé.**
- `_kad_post_title: "show"` avec `page_title=false` → titre `above`. **Confirmé.**
- `_kad_post_layout: "normal"` explicite avec `page_layout=fullwidth` → `normal`. **Confirmé.**
- **Corrigé (§ 7)** : `page_layout=left` ou `right` en theme mod → `layout=normal`, `sidebar=enable`, `side=left` ou `right`. La classe est donc `content-width-normal has-sidebar`, pas `content-width-left`. Cause dans le code : `inc/components/layout/component.php`, l. 619-638. Seule la méta place `left`/`right` dans `$layout`.
- `base_font = {"family":"Georgia, serif"}` → `body, input, select, optgroup, textarea{font-family:var(--global-body-font-family);}` seul : pas de fusion avec le défaut. **Confirmé.**
- **Précisé (§ 3.2)** : `fallback` est ignoré quand `google` vaut `false`. On obtient `--global-body-font-family:'Hanken Grotesk';`, alors qu'avec `google: true` on obtient `'Hanken Grotesk', serif`.
- `h1_font` en `rem` avec `lineHeight` par palier et `lineType: "-"` : `h1{…font-size:3.2rem;line-height:1.1;…}`, puis `font-size:2.6rem;line-height:1.2` (≤ 1024 px) et `2.2rem` / `1.3` (≤ 767 px). **Confirmé**, et cela complète le § 3.2.
- Palette passée en tableau à `pre_update_option_kadence_global_palette` → `TypeError: json_decode(): Argument #1 ($json) must be of type string, array given`. Un jeu de 9 couleurs passe à 15 ; un jeu de 10 reste à 10. Avec les entrées 1 et 2 inversées, `palette1` et `palette2` valent `''`. `palette10 = #FfFfFf` donne `oklch(from var(--global-palette1) …)`. **Tout confirmé.**
- `option()` : `''` → défaut (`normal`), et `false` est conservé. **Confirmé.**
- Fonction du § 10, prise telle qu'imprimée dans la fiche : `php -l` ne signale aucune erreur ; seul un commentaire diffère de `reglages-kadence.php`. Injectée en mémoire (sans `pd_kadence_appliquer_reglages()`), elle donne **28** theme mods. Le CSS produit contient les 15 fragments de l'extrait du § 1 : palette, `palette9rgb`, polices, `72rem`, `calc(72rem + 10rem)`, `1.25rem`, fonds, `body`, `h1`, bouton « remonter », et `border-radius:2px` des boutons. **Confirmé.**

### Vérifié dans le code source (sans écart)

- Les **969** valeurs par défaut, et toutes celles citées : typographies h1 à h6, `title_above_font`, `buttons_*`, fonds, `link_color`, `content_*`, `boxed_spacing`, `page_*`, `post_layout = narrow`, `scroll_up_*` (dont l'orthographe `scroll_up_visiblity`, `scroll_up_visibility` n'existant pas).
- `register_post_meta( '', … )` : 9 méta `string`, plus `_kad_post_header` et `_kad_post_footer` en `boolean`, toutes avec `show_in_rest`.
- Points de rupture : 1024 px et 767 px (filtres `kadence_tablet_media_query` et `kadence_mobile_media_query`). `check_theme_switched` est sur `init`, priorité 99 (WordPress 7.1.3).
- Filtres de polices : `kadence_theme_add_custom_fonts`, `kadence_blocks_add_custom_fonts` (administration seulement), `kadence_print_google_fonts`. Aucune occurrence de `kadence_custom_fonts` dans le thème ni dans l'extension.
- `link_color.style` : les 5 valeurs `standard`, `color-underline`, `no-underline`, `hover-background` et `offset-background`.
- Unités de `content_width` : `px`, `em`, `rem` ; ajout pour la largeur élargie : 230 px ou 10 em/rem/vw. Le thème comporte 15 couleurs `theme-palette1` à `theme-palette15` (`theme.json`). `kadence/singlebtn.inheritStyles` est une `string`, `"fill"` par défaut.
- **Précisé (§ 9)** : l'unité `vw` ne vaut que pour `scroll_up_side_offset`, et `vh` que pour `scroll_up_bottom_offset`.

### Non rejoué par la contre-vérification

- Les mesures du bac à sable (B) qui exigent des theme mods réellement écrits : rendu `getComputedStyle` des tailles de titres, fonds et conteneur, ainsi que le bouton « remonter » affiché.
- Le chargement réel des polices Google ou locales (`load_fonts_local`).
- Le moment d'exécution de `after_switch_theme` (seul le crochet `init`, priorité 99, a été lu dans le code) et l'`autoload` de la palette.
- `_kad_post_layout: "right"` et l'effet de `_kad_post_feature`.
