# Kadence Blocks : blocs de texte et de médias

Fiche de référence pour écrire les specs JSON de `outils/wp-test/editeur.js construire`.

- Environnement d'essai : WordPress 7.1.3 (fr_FR), thème Kadence 1.5.2 avec le thème enfant `kadence-pascal`, Kadence Blocks 3.7.12.1 (version gratuite). Essais du 7 octobre 2026 sur `http://127.0.0.1:8080`.
- Sources lues : `kadence-blocks/dist/blocks/<bloc>/block.json`, rendus PHP `includes/blocks/class-kadence-blocks-*-block.php`, aide CSS `includes/class-kadence-blocks-css.php`, fonctions `save` de `dist/blocks-*.js`, feuilles `dist/style-blocks-*.css`, CSS du thème Kadence (`content.min.css`, `global.min.css`).
- Colonne « Vérif. » des tableaux :
  - **E** : essai réel. La spec a été construite dans l'éditeur, le bloc est resté valide après rechargement, puis j'ai contrôlé le contenu enregistré (`lire.php`) et/ou le CSS généré et le rendu public (captures, styles calculés).
  - **C** : lu dans le code seulement.
  - **—** : non vérifié.
- Les extraits JSON ci-dessous sont copiés automatiquement depuis les fichiers de spec réellement construits. Le chapitre 13 (Traçabilité) indique d'où vient chaque extrait.

---

## 1. Quel bloc pour quel besoin

| Besoin | Bloc conseillé | Remarque |
|---|---|---|
| Titre h1 à h6 avec police, taille responsive, couleur, marges, fragment surligné | `kadence/advancedheading` | Toujours renseigner `color` et `fontWeight` (voir 2.7). |
| Sur-titre, étiquette, ligne courte stylée, ligne de liens colorés | `kadence/advancedheading` avec `htmlTag: "p"` | `linkColor`, `linkHoverColor` et `linkStyle` s'appliquent aussi aux liens placés dans le texte. |
| Paragraphe courant, description | `core/paragraph` | Styles écrits en ligne, pas de `uniqueID`, donc plus robuste. |
| Vignette 16/9 cliquable à partir d'une URL externe (YouTube) | `kadence/image` (`useRatio` + `ratio: "land169"`) | `core/image` fonctionne aussi (`aspectRatio: "16/9"`, `scale: "cover"`). |
| Boîte entièrement cliquable : icône ou image, titre, texte | `kadence/infobox` (`linkProperty: "box"`) | **Aucun lien dans le texte** : les liens imbriqués rendent le bloc invalide. |
| Carte avec plusieurs liens (vidéo + réseaux) | `kadence/column` composée : `kadence/image` + `kadence/advancedheading` + `core/paragraph` | Voir 10.3. |
| Espace vertical seul | `core/spacer`, ou `kadence/spacer` avec `dividerEnable: false` | Piège du `kadence/spacer` placé après un paragraphe (2.9). |
| Trait séparateur réglable (couleur, épaisseur, largeur, style) | `kadence/spacer` | `core/separator` pour un trait simple. |
| Liste à puces simple | `core/list` + `core/list-item` | |
| Liste avec icônes, en colonnes, liens par élément | `kadence/iconlist` + `kadence/listitem` | |
| Chiffres clés | `kadence/advancedheading` en version statique (recommandé) ou `kadence/countup` (animé) | Le nombre du compteur est **vide sans JavaScript** et vaut « 0 » tant qu'il n'est pas entièrement visible à l'écran. |

---

## 2. Règles communes à tous les blocs Kadence

### 2.1 `uniqueID` : ne pas le fournir pour les blocs de contenu
- Pour tous les blocs de cette fiche, l'éditeur l'attribue lui-même au montage du bloc, sous la forme `<id de la page>_<6 hexa>-<2 hexa>` (exemple `16_7cf592-bd`). **E** sur toutes les pages d'essai.
- Tout le CSS du bloc est généré côté serveur à partir de cet identifiant, dans `<style id="kadence_blocks_css-inline-css">`. Sans lui, le bloc n'a aucun style.
- Pour les **rangées et colonnes**, la fiche `mise-en-page.md` recommande au contraire un `uniqueID` explicite. Suivre cette fiche-là pour ces deux blocs.

**Contrôle à faire après chaque `construire`** : la sortie de `lire.php` ne doit contenir ni `undefined` (exemple observé : `data-kb-block="kb-adv-headingundefined"`) ni bloc Kadence sans `"uniqueID"`. **E**

### 2.2 Rangées : `kbVersion: 2` et `colLayout` obligatoires (détails dans la fiche mise en page)
- Une `kadence/rowlayout` sans `"kbVersion": 2` est enregistrée sans erreur, mais sur le site public les colonnes sortent sans le conteneur de la rangée, donc sans grille. **E**
- Une `kadence/rowlayout` sans `"colLayout"` (par exemple `"equal"`) affiche dans l'éditeur l'écran « Select Your Layout » (`!colLayout` dans le JS d'édition) et n'initialise pas ses blocs enfants. Résultat : aucun `uniqueID` dans toute la rangée, donc aucun CSS. **E + C** (page `surlignage`, première construction)
- La fiche mise en page indique que, **pour le rendu PHP**, un `colLayout` absent vaut `equal`. C'est exact, mais **dans l'éditeur** son absence bloque l'initialisation des blocs de contenu. Il faut donc toujours le renseigner.

### 2.3 Valeurs responsive
- Tableau `[ordinateur, tablette, mobile]`. `""` signifie « hérite de la taille au-dessus ».
- Requêtes média générées : tablette `@media (max-width: 1024px)`, mobile `@media (max-width: 767px)`. **E**
- Il n'y a qu'**une unité pour les trois tailles** (`sizeType`, `fontHeightType`, `marginType`, etc.). Les attributs `tabletMarginType` et `mobileMarginType` existent mais le PHP ne les lit pas. **C**

### 2.4 Mesures (marges, marges internes)
- Tableau `[haut, droite, bas, gauche]`.
- Un nombre reçoit l'unité de l'attribut `…Type` ou `…Unit` du bloc.
- `""` : aucune règle CSS, la valeur du thème s'applique.
- Préréglages acceptés à la place d'un nombre : `"xxs"` (0,5rem), `"xs"` (1rem), `"sm"` (1,5rem), `"md"` (2rem), `"lg"` (3rem), `"xl"` (4rem), `"xxl"` (5rem), `"3xl"` (6,5rem), `"4xl"` (8rem), `"5xl"` (10rem), `"ss-auto"`. Ils produisent `var(--global-kb-spacing-lg, 3rem)`. Ces variables ne sont pas définies sur le site, ce sont donc les valeurs de repli qui s'appliquent. **E** (`lg`, `md`) **/ C** (les autres)

### 2.5 Tailles de police prédéfinies
Les valeurs `"sm"`, `"md"`, `"lg"`, `"xl"`, `"xxl"` et `"3xl"` sont acceptées à la place d'un nombre dans `fontSize` (titre avancé) et dans `size` (objets typographie). Elles produisent `var(--global-kb-font-size-…)`, des tailles fluides définies sur le site :

| Préréglage | Valeur |
|---|---|
| `sm` | `clamp(0.8rem, …, 0.9rem)` |
| `md` | `clamp(1.1rem, …, 1.25rem)` |
| `lg` | `clamp(1.75rem, …, 2rem)` |
| `xl` | `clamp(2.25rem, …, 3rem)` |
| `xxl` | `clamp(2.5rem, …, 4rem)` |
| `3xl` | variable `--global-kb-font-size-xxxl`, `clamp(2.75rem, …, 6rem)` |

**E** (`xl`, `3xl`) **/ C** (les autres)

### 2.6 Couleurs
- Formats acceptés :
  - Hexadécimal (`"#c8b287"`). **E**
  - `"paletteN"`, qui produit `var(--global-paletteN, repli)`. **E**
  - Une variable CSS telle quelle (`"var(--sable)"`), transmise sans modification. **E** sur le site public.
- **La palette Kadence du site n'est pas réglée** : c'est celle d'origine de Kadence (palette1 `#2B6CB0` bleu, palette3 `#1A202C`, palette8 `#F7FAFC`, palette9 `#ffffff`). N'utilisez pas `paletteN` tant qu'elle n'est pas configurée ; préférez l'hexadécimal.
- Les variables du thème enfant (`--sable`, etc.) et ses polices ne sont **pas chargées dans l'éditeur** : `functions.php` ne déclare aucun style d'éditeur. L'aperçu dans l'éditeur est donc inexact (texte clair sur fond blanc, polices de repli). Sur le site public, le rendu est correct. **E** (capture de l'éditeur)
- Couleurs du site (`kadence-pascal/assets/pd.css`) :

| Variable | Valeur |
|---|---|
| `--nuit` | `#0d1217` |
| `--ardoise` | `#17202a` |
| `--ardoise-2` | `#223040` |
| `--ligne` | `#2c3a49` |
| `--texte` | `#e8e6e1` |
| `--texte-doux` | `#a9b6c0` |
| `--sable` | `#c8b287` |
| `--beret` | `#a3302f` |
| `--beret-vif` | `#c0403d` |
| `--ivoire` | `#ece8df` |
| `--encre` | `#10161c` |
| `--encre-doux` | `#4a5663` |

Le même fichier définit aussi les piles de polices `--display` (Newsreader, Georgia, serif), `--corps` (Hanken Grotesk, sans-serif) et `--mono` (IBM Plex Mono, chasse fixe), utilisables dans `typography` (3.1). (Ajout de la contre-vérification, lu dans `pd.css`.)

### 2.7 Polices et réglages par défaut du thème
- Polices embarquées par le thème enfant (aucune requête vers Google) :

| Police | Usage | Graisses disponibles |
|---|---|---|
| `Newsreader` | serif | 400 à 500 en romain, 400 en italique |
| `Hanken Grotesk` | police du corps de texte | 400 à 600 |
| `IBM Plex Mono` | chasse fixe | 400 et 500 |

- Indiquez le nom de famille avec `googleFont: false` (valeur par défaut).
- **`googleFont: true` ajoute `<link href="https://fonts.googleapis.com/css?family=Newsreader:regular…">`** dans la page (essai `ref-texte-et-medias-google`). C'est interdit sur ce site. **E**
- Le thème Kadence donne aux balises `h1` à `h6` une graisse `700`, un interlignage `1.5` et une couleur qui **dépend du niveau** (CSS du thème en ligne, relu à la contre-vérification) : `h1`–`h3` `var(--global-palette3)` (`#1A202C`), `h4`–`h5` `var(--global-palette4)` (`#2D3748`), `h6` `var(--global-palette5)` (`#4A5568`). Toutes sont presque invisibles sur le fond `#0d1217`. Tailles par défaut : 32, 28, 24, 22, 20 et 18px. Sur un titre (`htmlTag: "heading"`), **renseignez toujours `color` et `fontWeight`**. Sans `fontWeight`, Newsreader est affiché en faux gras. **E**
- En `htmlTag: "p"`, `"span"` ou `"div"`, la couleur est héritée du `body` (`#e8e6e1`). **E**

### 2.8 Valeurs par défaut non enregistrées
Un attribut égal à sa valeur par défaut n'est pas enregistré, et le PHP de ces blocs ne fusionne pas les valeurs par défaut. Ce qui s'affiche vient alors des feuilles de style de l'extension. **E** pour chacun des cas suivants :

| Cas | Conséquence |
|---|---|
| `<mark class="kt-highlight">` sans `markColor` | Texte orange `#f76a0c` (règle globale `.wp-block-kadence-advancedheading mark.kt-highlight{color:#f76a0c}`). |
| `kadence/infobox` sans `containerBackground` | Fond clair `var(--global-palette8, #f2f2f2)`. |
| `kadence/infobox` sans `containerPadding` | Marge interne de 1rem (préréglage `"xs"`). |
| `kadence/spacer` sans `dividerEnable: false` | Trait gris clair `#eee` sur 80 % de la largeur (défaut `dividerEnable: true`). |

### 2.9 Marges imposées par le thème Kadence (`content.min.css`) **E**
- `.single-content h1…h6 { margin: 1.5em 0 .5em }`, avec une marge haute nulle si le titre est le premier enfant.
- `.single-content p, figure, hr… { margin-bottom: var(--global-md-spacing) }`, soit 2rem, nulle si l'élément est le dernier enfant.
- `.single-content p:not(.wp-block-kadence-advancedheading) + .wp-block-kadence-spacer { margin-top: calc(0rem - var(--global-md-spacing)) }` : un `kadence/spacer` placé juste après un `core/paragraph` remonte de 2rem. Si la marge basse du paragraphe a été réduite (par exemple à 8px), l'espaceur chevauche le paragraphe. Utilisez alors `core/spacer`, qui n'est pas concerné par cette règle.
- Conséquence : dans les composants compacts (cartes, chiffres), fixez explicitement les marges haute et basse de chaque bloc.

### 2.10 Décalage de 16px sur mobile : mettre les méta de page
Sans méta de page, en dessous de 720px :
- la règle Kadence `.content-style-boxed .content-bg:not(.loop-entry){margin-left:-1rem}` décale tout le contenu de 16px vers la gauche ;
- un bloc placé hors d'une rangée a le début de son texte coupé ;
- dans une rangée avec 24px de marge interne, le texte se retrouve à 8px du bord.

Ce défaut a été observé sur toutes mes pages d'essai, construites sans méta. **E**

La correction est celle de la règle 8 de `mise-en-page.md` : ajouter dans la spec la clé `"meta"` suivante.

```json
{"titre": "…", "slug": "…", "meta": {"_kad_post_layout": "fullwidth", "_kad_post_content_style": "unboxed", "_kad_post_vertical_padding": "hide", "_kad_post_title": "hide"}, "blocs": []}
```

Avec ces méta, la page `ref-texte-et-medias-specs-meta` place l'article à x = 0 et le H1 à x = 24px. **E** Les règles de marge du thème décrites en 2.9 restent actives : la classe `single-content` est toujours présente.

**Attention (contre-vérification) :** avec ces méta, le contenu n'a plus aucune marge latérale. Le H1 est à 24px seulement parce qu'il est dans une rangée avec `padding: [32, 24, 32, 24]`. Un bloc placé **hors d'une rangée** touche le bord de l'écran (x = 0 à 1280 et à 390px, page `ref-texte-et-medias-verif-titres`). Placez donc tout bloc de contenu dans une `kadence/rowlayout` qui a une marge interne latérale. **E**

---

## 3. `kadence/advancedheading` (titre ou texte avancé)

**Rendu.** C'est un bloc statique.
- Code HTML enregistré : `<h1 class="kt-adv-heading<ID> wp-block-kadence-advancedheading" data-kb-block="kb-adv-heading<ID>">…</h1>`.
- Avec `link`, ce code est entouré de `<a class="kb-advanced-heading-link kt-adv-heading-link<ID>" …>`, ce qui rend tout le bloc cliquable.
- Les styles sont générés en PHP (`build_css`). **E**
- `content` est une chaîne HTML qui accepte `<mark>`, `<em>`, `<strong>`, `<a>` et `<br>`. **E**

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `content` | string (source html) | HTML en ligne | — | E |
| `level` | number | 1 à 6 (balise h1 à h6) | `2` | E (1, 2, 3, 4, 5) |
| `htmlTag` | string | `"heading"` (utilise `level`), `"p"`, `"span"` (le CSS ajoute `display:block`), `"div"` | `"heading"` | E (p, span, div) |
| `typography` | string | Nom de famille, recopié tel quel dans `font-family`. Mis entre apostrophes s'il contient une espace sans virgule (`'IBM Plex Mono'`). Une pile `"Newsreader, Georgia, serif"` ou `"var(--display)"` passe telle quelle. | `""` | E |
| `googleFont` | boolean | Garder `false` (voir 2.7) | `false` | E |
| `fontWeight` | string | `"400"`, `"500"`, `"600"`… | `""` | E |
| `fontStyle` | string | `"normal"`, `"italic"` | `"normal"` | E (italic) |
| `fontSize` | array | `[d, t, m]` : nombres, préréglages (2.5) ou chaîne CSS (voir l'astuce ci-dessous) | `["","",""]` | E |
| `sizeType` | string | Unité de `fontSize` : `"px"`, `"rem"`, `"em"`, `"vw"` | `"px"` | E (les quatre) |
| `fontHeight` | array | Interlignage `[d, t, m]` | `["","",""]` | E |
| `fontHeightType` | string | `""` (sans unité, recommandé), `"px"`, `"em"`, `"rem"` | `""` | E (`""`, px) |
| `letterSpacing` | number | Espacement des lettres sur ordinateur | — | E |
| `tabletLetterSpacing`, `mobileLetterSpacing` | number | Espacement sur tablette / mobile (attributs séparés, pas de tableau), avec l'unité de `letterSpacingType` | — | E (contre-vérification : 1 / 2 / 3px) |
| `letterSpacingType` | string | `"px"`, `"em"`, `"rem"` | `"px"` | E (em) |
| `textTransform` | string | `""`, `"none"`, `"uppercase"`, `"lowercase"`, `"capitalize"` | `""` | E (uppercase, capitalize) |
| `color` | string | Couleur (2.6) | — | E (hexa, palette1, palette9, var()) |
| `background` | string | Couleur de fond du bloc | — | E |
| `align` | string | `"left"`, `"center"`, `"right"` (produit `text-align`) | — | E |
| `tabletAlign`, `mobileAlign` | string | Idem, avec `!important` | — | E (mobileAlign) |
| `margin`, `tabletMargin`, `mobileMargin` | array | `[h, d, b, g]` (2.4) | `["","","",""]` | E (nombres et préréglages) |
| `marginType` | string | `"px"`. Le PHP accepte n'importe quelle unité CSS, qu'il colle derrière le nombre. Une seule unité pour les trois tailles (2.3). | `"px"` | E (px ; `rem` à la contre-vérification, appliqué aussi à `tabletMargin`) |
| `padding`, `tabletPadding`, `mobilePadding` + `paddingType` | array / string | Comme `margin` | `["","","",""]` / `"px"` | E (padding) |
| `maxWidth` | array | `[d, t, m]`. Avec `align: "center"`, ajoute des marges latérales `auto` (centrage du bloc). | `["","",""]` | E |
| `maxWidthType` | string | `"px"`, `"rem"`… | `"px"` | E (px, rem) |
| `anchor` | string | Attribut `id` de la balise | — | E |
| `link` | string | URL. **Tout le bloc** devient un lien. | — | E |
| `linkTarget` | boolean | `true` ajoute `target="_blank" rel="noopener noreferrer"` | `false` | E |
| `linkNoFollow`, `linkSponsored` | boolean | Ajoutent `nofollow` / `sponsored` au `rel` (avec `linkTarget` : `rel="noopener noreferrer nofollow sponsored"`) | `false` | E (les deux, contre-vérification) |
| `linkStyle` | string | `"none"`, `"underline"`, `"hover_underline"`. S'applique au lien du bloc **et aux `<a>` contenus dans le texte**. | — | E (les trois) |
| `linkColor`, `linkHoverColor` | string | Couleur des liens (bloc et liens du texte) | — | E |
| `borderStyle` | array | `[{"top":[couleur, style, épaisseur], "right":[…], "bottom":[…], "left":[…], "unit":"px"}]` | vide | E (bas seulement) |
| `borderRadius` + `borderRadiusUnit` | array / string | `[hg, hd, bd, bg]` (+ `tabletBorderRadius`, `mobileBorderRadius`) | `["","","",""]` / `"px"` | E (contre-vérification : `[8,8,8,8]` → `border-*-radius:8px`) |
| `markColor` | string | Couleur du `<mark class="kt-highlight">` | `"#f76a0c"` (orange, appliqué même si l'attribut est absent) | E |
| `markFontStyle`, `markFontWeight`, `markTypography`, `markTextTransform` | string | Comme pour le texte principal | `"normal"` / `""` | E |
| `markBG` | string | Fond du surlignage (la feuille de l'extension met `background:transparent` par défaut) | — | E |
| `markBGOpacity` | number | 0 à 1 (`0.5` avec `markBG: "#a3302f"` produit `background:rgba(163, 48, 47, 0.5)`) | `1` | E (contre-vérification) |
| `markSize` + `markSizeType` | array / string | `[d, t, m]` + unité | `["","",""]` / `"px"` | E (em) |
| `markLetterSpacing` + `markLetterSpacingType` | number / string | | — / `"px"` | E (em) |
| `markPadding` + `markPaddingType` | array / string | `[h, d, b, g]` | `[0,0,0,0]` / `"px"` | E |
| `markBorderRadius` | array | `[hg, hd, bd, bg]` | `["","","",""]` | E |
| `textShadow`, `enableTextGradient`/`textGradient`, `icon`…, `textOrientation`, `useRatio`/`ratio` (image en ligne) | | Non utilisés ici | | — |
| `size`, `lineHeight`, `tabSize`, `mobileSize`, `topMargin`… | | **Anciens attributs, à ne pas utiliser** : ils sont prioritaires sur `fontSize` et `fontHeight` (`if ( ! empty( $attributes['size'] ) )`). | | C |
| `colorClass`, `backgroundColorClass` | string | **Ne pas renseigner** : avec le thème Kadence, si `colorClass` est rempli, le CSS de `color` n'est plus produit. L'éditeur ajoute alors les classes `has-<colorClass>-color has-text-color` à la balise. | | E (contre-vérification : `color: "#ff0000"` + `colorClass` → titre à la couleur du thème) |

**Astuce non standard (E sur le site public).** `"fontSize": ["clamp(2.6rem, 7.2vw, 5.6rem)", "", ""]` avec `"sizeType": ""` produit `font-size:clamp(2.6rem, 7.2vw, 5.6rem)`. Le bloc reste valide. Le comportement du réglage de taille de l'éditeur si quelqu'un le modifie ensuite à la main n'a pas été vérifié. Les préréglages fluides `"xxl"` et `"3xl"` font la même chose sans astuce.

### 3.1 Fragment d'une autre couleur (surlignage `<mark>`)
- Écrire `<mark class="kt-highlight">mot</mark>` dans `content`, puis régler `markColor` et, si besoin, `markFontStyle: "italic"`. **E**
- `<mark class="kt-highlight"><em>mot</em></mark>` fonctionne aussi ; c'est l'`<em>` qui produit l'italique. **E**
- La couleur en ligne du cœur WordPress fonctionne aussi dans ce bloc : `<mark style="background-color:rgba(0, 0, 0, 0);color:#c0403d" class="has-inline-color">`. **E**
- En revanche, la classe de palette du cœur `has-palette-1-color` donne du **noir** : elle n'est pas définie par Kadence. **E** La classe qui existe est `has-theme-palette-1-color` (`.has-theme-palette-1-color{color:var(--global-palette1)}` dans le CSS du thème) : elle donne bien le bleu `#2B6CB0` (contre-vérification, page `ref-texte-et-medias-verif-cas`). **E**

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Je filme <mark class=\"kt-highlight\"><em>l'engagement</em></mark>",
    "level": 1,
    "typography": "var(--display)",
    "googleFont": false,
    "fontWeight": "400",
    "fontSize": ["clamp(2.6rem, 7.2vw, 5.6rem)", "", ""],
    "sizeType": "",
    "fontHeight": [1.05, "", ""],
    "color": "var(--texte)",
    "markColor": "var(--sable)",
    "margin": [0, "", 0, ""]
  }
}
```

Rendu public : `font-family:var(--display)`, `font-size:clamp(2.6rem, 7.2vw, 5.6rem)`, `mark.kt-highlight{color:var(--sable)}`, italique réelle de Newsreader. **E**

Surlignage complet (fond, police, taille, espacement, marges internes, coins arrondis) et alignement différent sur mobile :

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Un film <mark class=\"kt-highlight\">nouveau</mark> en tournage",
    "level": 2,
    "color": "#e8e6e1",
    "typography": "Newsreader",
    "fontWeight": "400",
    "fontSize": [40, "", ""],
    "align": "left",
    "mobileAlign": "center",
    "markColor": "#ece8df",
    "markBG": "#a3302f",
    "markBGOpacity": 1,
    "markPadding": [2, 8, 2, 8],
    "markPaddingType": "px",
    "markTypography": "IBM Plex Mono",
    "markFontWeight": "500",
    "markSize": [0.5, "", ""],
    "markSizeType": "em",
    "markTextTransform": "uppercase",
    "markLetterSpacing": 0.1,
    "markLetterSpacingType": "em",
    "markBorderRadius": [2, 2, 2, 2]
  }
}
```

CSS produit (**E**) : `mark.kt-highlight{letter-spacing:0.1em;font-size:0.5em;font-family:'IBM Plex Mono';font-weight:500;color:#ece8df;text-transform:uppercase;background:#a3302f;border-*-radius:2px;padding:2px 8px}` et, sous 767px, `text-align:center!important`.

### 3.2 Titre H2 : palette, préréglages de marge, marges responsive, fond, ancre

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Titre H2 couleur palette, marges responsive, aligné au centre",
    "level": 2,
    "align": "center",
    "color": "palette1",
    "fontSize": [2.5, 2, 1.6],
    "sizeType": "rem",
    "fontStyle": "italic",
    "margin": ["lg", "", "md", ""],
    "tabletMargin": [40, "", 20, ""],
    "mobileMargin": [24, "", 12, ""],
    "marginType": "px",
    "padding": [10, 20, 10, 20],
    "paddingType": "px",
    "background": "#223040",
    "anchor": "titre-ancre"
  }
}
```

CSS produit (**E**) :
- `margin-top:var(--global-kb-spacing-lg, 3rem); margin-bottom:var(--global-kb-spacing-md, 2rem); padding:10px 20px; font-size:2.5rem; font-style:italic; color:var(--global-palette1, #3182CE); background-color:#223040`
- tablette : `margin 40px / 20px`, `font-size 2rem` ; mobile : `24px / 12px`, `1.6rem`
- `id="titre-ancre"` sur la balise h2

### 3.3 Titre cliquable (lien externe, nouvel onglet)

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Titre lien externe (nouvel onglet)",
    "level": 3,
    "link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "linkTarget": true,
    "linkNoFollow": false,
    "linkStyle": "hover_underline",
    "linkColor": "#e8e6e1",
    "linkHoverColor": "#c0403d",
    "fontSize": [28, "", ""]
  }
}
```

HTML enregistré (**E**) : `<a href="https://www.youtube.com/watch?v=…" class="kb-advanced-heading-link kt-adv-heading-link<ID> hls-hover_underline" target="_blank" rel="noopener noreferrer"><h3 …>…</h3></a>`.
- Avec `linkNoFollow: true`, on obtient `rel="noopener noreferrer nofollow"`. **E**
- Sans `linkColor`, la couleur du lien est celle du titre. Le soulignement prend la couleur des liens du thème (palette1, bleu). **E**

### 3.4 Balises `span` et `div`, préréglage de taille, interlignage en px

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Un texte en balise span, poids 600, sans lettre majuscule forcée",
    "htmlTag": "span",
    "typography": "Hanken Grotesk",
    "fontWeight": "600",
    "fontSize": [1.1, "", ""],
    "sizeType": "em",
    "lineHeight": "",
    "fontHeight": [28, "", ""],
    "fontHeightType": "px",
    "color": "#a9b6c0"
  }
}
```

Dans cet essai, `"lineHeight": ""` est un reste sans effet (valeur vide). Ne pas le recopier.

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Texte en div, taille preset xl",
    "htmlTag": "div",
    "fontSize": ["xl", "", ""],
    "color": "palette9"
  }
}
```

**E** :
- en `span`, le CSS ajoute `display:block` ;
- `fontSize: ["xl"]` produit `var(--global-kb-font-size-xl, 3rem)` ;
- `palette9` produit `var(--global-palette9, #ffffff)`.

### 3.5 Bordure basse seule

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Bordure basse et rayon",
    "level": 5,
    "color": "#e8e6e1",
    "borderStyle": [
      {
        "top": ["", "", ""],
        "right": ["", "", ""],
        "bottom": ["#c8b287", "solid", 2],
        "left": ["", "", ""],
        "unit": "px"
      }
    ],
    "padding": ["", "", "8", ""]
  }
}
```

CSS produit : `border-bottom:2px solid #c8b287` (répété dans les requêtes tablette et mobile). **E**

### 3.6 Ligne de texte avec liens colorés (sans `link` sur le bloc)
Voir la ligne « Voir sur » de la carte film (10.3). On obtient `<p class="… hls-underline">` et le CSS `[data-kb-block] a{color:#e8e6e1;text-decoration:underline}` et `a:hover{color:#c0403d}`. **E**

---

## 4. `kadence/image` (image avancée)

**Image externe par URL : oui, c'est possible.**
- `url` accepte n'importe quelle URL : `https://i.ytimg.com/vi/<ID>/hqdefault.jpg` est enregistrée telle quelle dans `<img src>`.
- On ne fournit pas d'`id`. La classe de l'image est alors `kb-img`, sans `wp-image-N`, et il n'y a pas de `srcset`.
- Le bloc reste valide après rechargement et l'image externe s'affiche aussi dans l'éditeur (essai avec une URL locale). **E**
- L'affichage effectif de la vignette `i.ytimg.com` n'a pas pu être vu : ce domaine est bloqué par le proxy du bac à sable (erreur 403 sur CONNECT). Le recadrage a été validé avec une image locale qui imite `hqdefault` (480×360, bandes noires de 45px en haut et en bas, cadre rouge autour de la zone 16/9). Résultat : avec `ratio: "land169"`, le cadre rouge touche les quatre bords et aucune bande noire ne reste visible. **E**

**Rendu enregistré** (**E**) :
```html
<figure class="wp-block-kadence-image kb-image<ID> kb-image-is-ratio-size">
  <a href="…" class="kb-advanced-image-link" target="_blank" aria-label="…" rel="noopener noreferrer">
    <div class="kb-is-ratio-image kb-image-ratio-land169"><img src="…" alt="…" class="kb-img"/></div>
  </a>
  <figcaption>…</figcaption>
</figure>
```
- Le cadre est réservé par `padding-bottom:56.25%`, puis l'image est placée en `position:absolute` avec `object-fit:cover`. Il n'y a donc pas de saut de mise en page malgré l'absence de `width` et `height`. **E**
- Mesure dans une colonne de 389px : 389×219. **E**

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `url` | string (source `img@src`) | URL absolue, externe possible | — | E |
| `alt` | string (source `img@alt`) | | `""` | E |
| `id` | number | Identifiant de média de la bibliothèque. **À omettre pour une URL externe.** | — | C |
| `title` | string | Attribut `title` de l'image | — | C |
| `caption` | string (source html `figcaption`) | Légende en HTML | — | E |
| `showCaption` | boolean | `false` : la légende n'est **pas du tout enregistrée** | `true` | E |
| `captionStyles` | array | `[{"size":[d,t,m],"sizeType":"px","lineHeight":[…],"lineType":"px","letterSpacing":[d,t,m],"textTransform":"","family":"","google":false,"style":"","weight":"","color":"","background":""}]` | vide | E (size, style, color) |
| `link` | string | URL du lien posé sur l'image | — | E |
| `linkTarget` | boolean | `true` ajoute `target="_blank" rel="noopener noreferrer"` | `false` | E |
| `linkTitle` | string | Produit `aria-label` sur le `<a>` | — | E |
| `linkNoFollow`, `linkSponsored` | boolean | Ajoutent `nofollow` / `sponsored` au `rel`. Sans `linkTarget`, on obtient `rel="nofollow sponsored"` (sans `noopener`). | `false` | E (contre-vérification) |
| `useRatio` | boolean | Active le recadrage | `false` | E |
| `ratio` | string | `"land169"`, `"land43"` (utilisé si `ratio` est vide ou absent), `"land32"`, `"land21"`, `"land31"`, `"land41"`, `"square"`, `"port34"`, `"port23"` | aucun (absent du `block.json`) | E (land169, land21 ; absent → `kb-image-ratio-land43`) |
| `imagePosition` | string | Valeur de `object-position`, par exemple `"center top"` | `""` | E |
| `imgMaxWidth`, `imgMaxWidthTablet`, `imgMaxWidthMobile` | number | Largeur maximale en px | — | E (desktop) |
| `align` | string | `"center"`, `"left"`, `"right"` : enveloppe `<div class="wp-block-kadence-image …"><figure class="aligncenter">`. `"wide"`, `"full"` possibles. | — | E (center) |
| `marginDesktop`, `marginTablet`, `marginMobile` + `marginUnit` | array / string | `[h, d, b, g]` | `["","","",""]` / `"px"` | E |
| `paddingDesktop`… + `paddingUnit` | array / string | Idem | | C |
| `borderRadius` (+ `tabletBorderRadius`, `mobileBorderRadius`) + `borderRadiusUnit` | array / string | `[hg, hd, bd, bg]` | | E |
| `borderStyle` | array | Comme pour le titre avancé | | C |
| `imageFilter` | string | `"none"`, `"grayscale"`… | `"none"` | — |
| `overlay`, `overlayOpacity`, `overlayType`, `displayBoxShadow`, `maskSvg`… | | Non utilisés ici | | — |

Variantes testées (image locale avec légende stylée, puis image sans ratio de 240px centrée avec légende masquée) :

```json
{
  "name": "kadence/image",
  "attributes": {
    "url": "http://127.0.0.1:8095/hqdefault-test.png",
    "alt": "Image d'essai 480x360 à bandes noires",
    "useRatio": true,
    "ratio": "land169",
    "link": "https://www.youtube.com/watch?v=0ynsZ42MuU4",
    "linkTarget": true,
    "caption": "Image locale 4/3 recadrée en 16/9",
    "borderRadius": [4, 4, 4, 4],
    "borderRadiusUnit": "px",
    "captionStyles": [
      {
        "size": [13, "", ""],
        "sizeType": "px",
        "lineHeight": ["", "", ""],
        "lineType": "px",
        "letterSpacing": ["", "", ""],
        "textTransform": "",
        "family": "",
        "google": false,
        "style": "italic",
        "weight": "",
        "variant": "",
        "subset": "",
        "loadGoogle": true,
        "color": "#a9b6c0",
        "background": ""
      }
    ]
  }
}
```

```json
{
  "name": "kadence/image",
  "attributes": {
    "url": "http://127.0.0.1:8095/hqdefault-test.png",
    "alt": "Sans ratio, largeur max 240",
    "imgMaxWidth": 240,
    "align": "center",
    "showCaption": false,
    "caption": "légende masquée"
  }
}
```

Cadrage vers le haut (rapport 2/1) :

```json
{
  "name": "kadence/image",
  "attributes": {
    "url": "http://127.0.0.1:8095/hqdefault-test.png",
    "alt": "cadrage haut",
    "useRatio": true,
    "ratio": "land21",
    "imagePosition": "center top"
  }
}
```

**`core/image` avec une URL externe (E).** On obtient `<img src="…" style="aspect-ratio:16/9;object-fit:cover;width:100%;height:auto">` dans un `<a target="_blank" rel="noopener">` et une légende `figcaption.wp-element-caption`. Le bloc n'a pas d'attribut équivalent à `linkTitle` ; on n'obtient donc pas d'`aria-label`.

```json
{
  "name": "core/image",
  "attributes": {
    "url": "http://127.0.0.1:8095/hqdefault-test.png",
    "alt": "Même image en core/image",
    "aspectRatio": "16/9",
    "scale": "cover",
    "width": "100%",
    "href": "https://www.youtube.com/watch?v=0ynsZ42MuU4",
    "linkTarget": "_blank",
    "rel": "noopener",
    "linkDestination": "custom",
    "caption": "core/image : aspectRatio 16/9 + scale cover"
  }
}
```

---

## 5. `kadence/infobox` (boîte d'info)

**Rendu.**
- Avec `link` et `linkProperty: "box"` (défaut), toute la boîte est un `<a class="kt-blocks-info-box-link-wrap info-box-link …">`.
- Sans `link`, l'enveloppe est un `<span class="kt-blocks-info-box-link-wrap …">`.
- L'éditeur ajoute de lui-même `"kbVersion": 2`, et le CSS cible alors la classe `.kt-info-box<ID>`. **E**

**Pièges vérifiés** :
1. **Ne jamais mettre de `<a>` dans `contentText` ou `title` quand toute la boîte est un lien.** Ces liens sont imbriqués dans le lien de la boîte et le bloc est déclaré invalide au rechargement. Sur le site public, le navigateur casse la structure de la boîte. **E**
2. **Passer les objets complets** de `mediaIcon`, `mediaImage`, `mediaStyle`, `titleFont` et `textFont` (toutes les clés). Avec des objets partiels, le code HTML enregistré contient `kt-info-media-animate-undefined` (et `kt-info-icon-animate-undefined`) ; l'attribut `data-stroke` disparaît si la clé `width` manque dans `mediaIcon`. **E**
3. Sans `containerBackground`, le fond est clair (`var(--global-palette8, #f2f2f2)`). Mettre une couleur ou `"transparent"`. **E**
4. La marge interne par défaut est `["xs","xs","xs","xs"]` (1rem). Mettre `[0,0,0,0]` si aucune marge interne n'est voulue. **E**
5. Une image de média reçoit `width:<mediaImage[0].width>px; max-width:100%` : elle ne dépasse jamais la largeur déclarée. Avec 480, elle ne remplit pas une colonne de plus de 480px. **E** (CSS) / largeur plus grande non essayée
6. Les liens du texte (en mode `learnmore`) prennent la couleur des liens du thème (bleu palette1). **E** Le `block.json` de l'infobox ne contient aucun attribut de couleur de lien. **C**

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `link` | string (source `a.info-box-link@href`) | URL | — | E |
| `linkProperty` | string | `"box"` (toute la boîte), `"learnmore"` (seul le bouton est un lien, avec `displayLearnMore: true`), `"none"` | `"box"` | E (box, learnmore) |
| `target` | string (source `a.info-box-link@target`) | `"_self"`, `"_blank"` (ajoute `rel="noopener noreferrer"`) | `"_self"` | E |
| `linkNoFollow`, `linkSponsored`, `linkTitle` | | | | C |
| `hAlign` (+ `hAlignTablet`, `hAlignMobile`) | string | `"left"`, `"center"`, `"right"` | `"center"` | E (left) |
| `mediaType` | string | `"icon"`, `"image"`, `"number"`, `"none"` | `"icon"` | E (icon, image) |
| `mediaAlign` (+ `mediaAlignTablet`, `mediaAlignMobile`) | string | `"top"`, `"left"`, `"right"` | `"top"` | E (top) |
| `mediaIcon` | array | `[{"icon":"fe_film","size":32,"unit":"px","width":1.5,"title":"","color":"","hoverColor":"","hoverAnimation":"none","flipIcon":"","tabletSize":"","mobileSize":""}]`. `width` est l'épaisseur du trait des icônes `fe_`. | `fe_aperture`, 50 | E |
| `mediaImage` | array | `[{"url":"…","id":"","alt":"…","width":480,"height":360,"maxWidth":"","hoverAnimation":"none","flipUrl":"","flipId":"","flipAlt":"","flipWidth":"","flipHeight":"","subtype":"","flipSubtype":""}]` | | E |
| `imageRatio` | string | `"inherit"` ou les mêmes valeurs que `ratio` de l'image (recadrage `object-fit:cover`) | `"inherit"` | E (land169) |
| `mediaStyle` | array | `[{"background":"","hoverBackground":"","border":"","hoverBorder":"","borderRadius":0,"borderRadiusUnit":"px","borderWidth":[0,0,0,0],"borderWidthUnit":"px","padding":[h,d,b,g],"paddingUnit":"px","margin":[h,d,b,g],"marginUnit":"px"}]` | padding 10, margin `[0,15,0,15]` | E (padding, margin) |
| `displayTitle` | boolean | | `true` | C |
| `title` | rich-text | HTML en ligne | `"Title"` | E |
| `titleColor`, `titleHoverColor` | string | | `""` | E |
| `titleFont` | array | `[{"level":3,"size":[d,t,m],"sizeType":"px","lineHeight":[…],"lineType":"","letterSpacing":"","textTransform":"","family":"Newsreader","google":false,"style":"","weight":"400","variant":"","subset":"","loadGoogle":true,"padding":["","","",""],"paddingControl":"linked","margin":[h,d,b,g],"marginControl":"individual","paddingUnit":"px","marginUnit":"px"}]`. `level` donne la balise h. `letterSpacing`, `margin` et `padding` sont **toujours en px**. | `level` 2 | E (level, size, lineHeight, family, weight, margin) |
| `titleTagType` | string | `"heading"`, `"p"`, `"span"`, `"div"` | `"heading"` | C |
| `displayText`, `contentText` | boolean / rich-text | | `true` / texte latin | E |
| `textColor`, `textHoverColor` | string | | | E (textColor) |
| `textFont` | array | `[{"size":[…],"sizeType":"px","lineHeight":[…],"lineType":"","letterSpacing":"","family":"","google":"","style":"","weight":"","variant":"","subset":"","loadGoogle":true,"textTransform":""}]` | | E (size, lineHeight) |
| `displayLearnMore`, `learnMore` | boolean / rich-text | Bouton « en savoir plus ». Par défaut : **texte** gris `var(--global-palette5)` (`#4A5568`), fond transparent, marge interne 4px 8px | `false` / `"Learn More"` | E |
| `learnMoreStyles` | array | Styles du bouton | | — |
| `containerBackground`, `containerHoverBackground` (+ `…Opacity`) | string | | `""` | E |
| `containerPadding` (+ `containerTabletPadding`, `containerMobilePadding`) + `containerPaddingType` | array / string | `[h, d, b, g]` | `["xs","xs","xs","xs"]` | E |
| `containerMargin` + `containerMarginUnit` | array / string | | | C |
| `borderStyle`, `borderHoverStyle` | array | Comme pour le titre avancé | | E (borderStyle) |
| `borderRadius` + `borderRadiusUnit` | array / string | `[hg, hd, bd, bg]` | | E |
| `displayShadow`, `shadow`, `maxWidth`, `fullHeight`, `number`… | | Non utilisés ici | | — |
| `containerBorder`, `containerBorderWidth`, `containerBorderRadius` | | Anciens attributs, prioritaires s'ils sont remplis : ne pas utiliser | | C |

### 5.1 Boîte cliquable : icône, titre, texte (spec testée)

```json
{
  "name": "kadence/infobox",
  "attributes": {
    "link": "/films/",
    "linkProperty": "box",
    "target": "_self",
    "hAlign": "left",
    "mediaType": "icon",
    "mediaAlign": "top",
    "mediaIcon": [
      {
        "icon": "fe_film",
        "size": 32,
        "unit": "px",
        "width": 1.5,
        "title": "",
        "color": "#c8b287",
        "hoverColor": "#e8e6e1",
        "hoverAnimation": "none",
        "flipIcon": "",
        "tabletSize": "",
        "mobileSize": ""
      }
    ],
    "mediaStyle": [
      {
        "background": "",
        "hoverBackground": "",
        "border": "",
        "hoverBorder": "",
        "borderRadius": 0,
        "borderRadiusUnit": "px",
        "borderWidth": [0, 0, 0, 0],
        "borderWidthUnit": "px",
        "padding": [0, 0, 0, 0],
        "paddingUnit": "px",
        "margin": [0, 0, 16, 0],
        "marginUnit": "px"
      }
    ],
    "title": "Documentaires",
    "titleColor": "#e8e6e1",
    "titleHoverColor": "#c8b287",
    "titleFont": [
      {
        "level": 3,
        "size": [24, "", ""],
        "sizeType": "px",
        "lineHeight": [1.2, "", ""],
        "lineType": "",
        "letterSpacing": "",
        "textTransform": "",
        "family": "Newsreader",
        "google": false,
        "style": "",
        "weight": "400",
        "variant": "",
        "subset": "",
        "loadGoogle": true,
        "padding": ["", "", "", ""],
        "paddingControl": "linked",
        "margin": [0, "", 8, ""],
        "marginControl": "individual",
        "paddingUnit": "px",
        "marginUnit": "px"
      }
    ],
    "contentText": "Films institutionnels et récits au long cours.",
    "textColor": "#a9b6c0",
    "textFont": [
      {
        "size": [15, "", ""],
        "sizeType": "px",
        "lineHeight": [1.5, "", ""],
        "lineType": "",
        "letterSpacing": "",
        "family": "",
        "google": "",
        "style": "",
        "weight": "",
        "variant": "",
        "subset": "",
        "loadGoogle": true,
        "textTransform": ""
      }
    ],
    "containerBackground": "#17202a",
    "containerHoverBackground": "#223040",
    "containerPadding": [24, 24, 24, 24],
    "borderStyle": [
      {
        "top": ["#2c3a49", "solid", 1],
        "right": ["#2c3a49", "solid", 1],
        "bottom": ["#2c3a49", "solid", 1],
        "left": ["#2c3a49", "solid", 1],
        "unit": "px"
      }
    ],
    "borderRadius": [2, 2, 2, 2]
  }
}
```

Rendu (**E**) :
- boîte `#17202a` avec bordure de 1px `#2c3a49` et coins arrondis de 2px ;
- au survol : fond `#223040`, titre `#c8b287`, icône `#e8e6e1` ;
- icône Feather `fe_film` de 32px.

### 5.2 Image + texte avec liens : lien sur le bouton uniquement (valide)

```json
{
  "name": "kadence/infobox",
  "attributes": {
    "link": "https://www.youtube.com/watch?v=0ynsZ42MuU4",
    "target": "_blank",
    "linkProperty": "learnmore",
    "hAlign": "left",
    "mediaType": "image",
    "mediaAlign": "top",
    "mediaImage": [
      {
        "url": "http://127.0.0.1:8095/hqdefault-test.png",
        "id": "",
        "alt": "Vignette",
        "width": 480,
        "height": 360,
        "maxWidth": "",
        "hoverAnimation": "none",
        "flipUrl": "",
        "flipId": "",
        "flipAlt": "",
        "flipWidth": "",
        "flipHeight": "",
        "subtype": "",
        "flipSubtype": ""
      }
    ],
    "imageRatio": "land169",
    "mediaStyle": [
      {
        "background": "",
        "hoverBackground": "",
        "border": "",
        "hoverBorder": "",
        "borderRadius": 0,
        "borderRadiusUnit": "px",
        "borderWidth": [0, 0, 0, 0],
        "borderWidthUnit": "px",
        "padding": [0, 0, 0, 0],
        "paddingUnit": "px",
        "margin": [0, 0, 12, 0],
        "marginUnit": "px"
      }
    ],
    "title": "Infobox, lien sur « Voir la vidéo » seulement",
    "titleColor": "#e8e6e1",
    "titleFont": [
      {
        "level": 3,
        "size": [20, "", ""],
        "sizeType": "px",
        "lineHeight": ["", "", ""],
        "lineType": "px",
        "letterSpacing": "",
        "textTransform": "",
        "family": "Newsreader",
        "google": false,
        "style": "",
        "weight": "400",
        "variant": "",
        "subset": "",
        "loadGoogle": true,
        "padding": ["", "", "", ""],
        "paddingControl": "linked",
        "margin": [0, "", 6, ""],
        "marginControl": "individual",
        "paddingUnit": "px",
        "marginUnit": "px"
      }
    ],
    "contentText": "Voir sur : <a href=\"https://www.instagram.com/\">Instagram</a> · <a href=\"https://www.facebook.com/\">Facebook</a>",
    "textColor": "#a9b6c0",
    "displayLearnMore": true,
    "learnMore": "Voir la vidéo",
    "containerBackground": "transparent",
    "containerPadding": [0, 0, 0, 0]
  }
}
```

**E** : le bloc reste valide. L'image, en revanche, n'est pas cliquable. Pour la carte film, on préfère donc la colonne composée (10.3).

### 5.3 Noms d'icônes (C : présence dans les tableaux d'icônes)
- **Feather** (`fe_…`, fichier `includes/icons-ico-array.php`) : `fe_film`, `fe_video`, `fe_youtube`, `fe_instagram`, `fe_facebook`, `fe_twitter`, `fe_playCircle`, `fe_play`, `fe_award`, `fe_users`, `fe_clock`, `fe_mapPin`, `fe_arrowRight`, `fe_chevronRight`, `fe_checkCircle`.
- **Font Awesome** (`fa_…`, fichier `includes/icons-array.php`) : `fa_instagram`, `fa_facebook`, `fa_facebook-f`, `fa_youtube`, `fa_twitter`, `fa_x-twitter-square`. Il n'existe pas de `fa_x-twitter` simple.
- Rendus à l'écran (**E**) : `fe_film`, `fe_award`, `fe_chevronRight`, `fe_youtube`.

---

## 6. `kadence/spacer` (espace et séparateur), `core/spacer`, `core/separator`

Code HTML enregistré (**E**) : `<div class="wp-block-kadence-spacer aligncenter kt-block-spacer-<ID>"><div class="kt-block-spacer kt-block-spacer-halign-left"><hr class="kt-divider"/></div></div>`. Le `<hr>` est absent si `dividerEnable` vaut `false`.

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `spacerHeight` | number | Hauteur. Si l'attribut est absent, la feuille de style impose 60px. | `60` | E (24, 40) / C (60px par défaut) |
| `spacerHeightUnits` | string | `"px"`, `"vh"` (proposées par l'éditeur). `"rem"` est aussi rendu correctement. | `"px"` | E (px, rem) |
| `tabletSpacerHeight`, `mobileSpacerHeight` | number | Même unité, avec `!important` | `""` | E |
| `dividerEnable` | boolean | **`false` pour un espace sans trait** | `true` | E |
| `dividerStyle` | string | `"solid"`, `"dashed"`, `"dotted"`, `"stripe"` | `"solid"` | E (solid, dashed) |
| `dividerColor` | string | Couleur | `"#eee"` | E |
| `dividerOpacity` | number | 0 à 100 (60 produit `rgba(…, 0.60)`) | `100` | E |
| `dividerWidth` + `dividerWidthUnits` | number / string | `"%"` ou `"px"` | `80` / `"%"` | E (100 %, 120px) |
| `tabletDividerWidth`, `mobileDividerWidth` | number | | | C |
| `dividerHeight` | number | Épaisseur du trait en px | `1` | E (1, 2) |
| `hAlign` (+ `tabletHAlign`, `mobileHAlign`) | string | `"left"`, `"center"`, `"right"` : position du trait | `"center"` | E (left) |
| `vsdesk`, `vstablet`, `vsmobile` | boolean | Masquer selon l'appareil | `false` | C |

```json
{"name": "kadence/spacer", "attributes": {"spacerHeight": 24, "dividerEnable": false}}
```

```json
{
  "name": "kadence/spacer",
  "attributes": {
    "spacerHeight": 40,
    "tabletSpacerHeight": 30,
    "mobileSpacerHeight": 20,
    "dividerColor": "#c8b287",
    "dividerWidth": 100,
    "dividerHeight": 1,
    "dividerOpacity": 60,
    "hAlign": "left"
  }
}
```

```json
{
  "name": "kadence/spacer",
  "attributes": {
    "spacerHeight": 3,
    "spacerHeightUnits": "rem",
    "dividerStyle": "dashed",
    "dividerColor": "#2c3a49",
    "dividerWidth": 120,
    "dividerWidthUnits": "px",
    "dividerHeight": 2
  }
}
```

Équivalents du cœur WordPress (**E**) :
- `core/spacer` produit `<div style="height:32px" aria-hidden="true" class="wp-block-spacer">` ;
- `core/separator` avec `className: "is-style-wide"` et `style.color.background` produit `<hr class="wp-block-separator … is-style-wide" style="background-color:#2c3a49;color:#2c3a49"/>`, un trait d'environ 3px dans ce thème.

```json
{"name": "core/spacer", "attributes": {"height": "32px"}}
```

```json
{
  "name": "core/separator",
  "attributes": {"style": {"color": {"background": "#2c3a49"}}, "className": "is-style-wide"}
}
```

---

## 7. `kadence/iconlist` + `kadence/listitem` (liste à icônes), `core/list`

- `kadence/listitem` n'existe que comme enfant d'une `kadence/iconlist`.
- L'icône par défaut vient du parent : le code HTML contient `data-name="USE_PARENT_DEFAULT_ICON"`, remplacé lors du rendu PHP. **E**
- Code HTML d'un élément avec lien : `<li class="wp-block-kadence-listitem …"><a href="…" class="kt-svg-icon-link" target="_blank" rel="noopener noreferrer"><span …icône…></span><span class="kt-svg-icon-list-text">…</span></a></li>`. **E**

| Attribut (iconlist) | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `icon` | string | Icône par défaut des éléments | `"fe_checkCircle"` | E |
| `iconSize` | array | `[d, t, m]` en px | `["","",""]` | E |
| `color` | string | Couleur des icônes | `""` | E |
| `width` | number | Épaisseur du trait des icônes `fe_` | `2` | C |
| `listStyles` | array | `[{"size":[d,t,m],"sizeType":"px","lineHeight":[…],"lineType":"","letterSpacing":"","family":"","google":false,"style":"","weight":"","variant":"","subset":"","loadGoogle":true,"color":"#…","textTransform":""}]` | | E (size, lineHeight, color) |
| `listGap` (+ `tabletListGap`, `mobileListGap`) | number | Espace vertical entre éléments en px (`grid-row-gap`) | `5` | E |
| `listLabelGap` | number | Espace entre l'icône et le texte, en px | `10` | E |
| `columns`, `tabletColumns`, `mobileColumns` | number | Nombre de colonnes | `1` / `""` / `""` | E (2 / mobile 1) |
| `columnGap` (+ tablette et mobile) | number | px | `0` | C |
| `linkUnderline` | string | `"inherit"`, `"always"`, `"hover"`, `"none"` | `"inherit"` | E (hover) |
| `linkColor`, `linkHoverColor` | string | | `""` | E |
| `listMargin` + `listMarginType` | array / string | `[h, d, b, g]`. Si l'attribut n'est pas enregistré, la liste reçoit `margin-bottom: var(--global-kb-spacing-sm, 1.5rem)`. | `["0","0","sm","0"]` | E |
| `style` | string | `"default"`, `"stacked"` (icône dans une pastille : `background`, `border`, `borderRadius` en %, `padding`) | `"default"` | C |
| `items` | array | Ancien format, inutile avec les blocs enfants | | C |

| Attribut (listitem) | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `text` | string (source html) | HTML en ligne, `<mark class="kt-highlight">` accepté | — | E |
| `link` | string | | `""` | E |
| `target` | string | `"_self"`, `"_blank"` | `"_self"` | E |
| `linkNoFollow`, `linkSponsored` | boolean | | `false` | C |
| `icon` | string | Remplace l'icône du parent pour cet élément | `""` | E (fe_youtube) |
| `showIcon` | boolean | `false` laisse **un SVG vide à la place de l'icône** (le décalage du texte reste) | `true` | E |
| `markColor` et les autres `mark…` | | Comme pour le titre avancé (défaut orange) | `"#f76a0c"` | E (markColor) |
| `size`, `width`, `color`, `style`… | | Réglages propres à l'élément | | C |

```json
{
  "name": "kadence/iconlist",
  "attributes": {
    "icon": "fe_chevronRight",
    "iconSize": [14, "", ""],
    "color": "#c8b287",
    "listGap": 6,
    "listLabelGap": 8,
    "listStyles": [
      {
        "size": [15, "", ""],
        "sizeType": "px",
        "lineHeight": [1.5, "", ""],
        "lineType": "",
        "letterSpacing": "",
        "family": "",
        "google": false,
        "style": "",
        "weight": "",
        "variant": "",
        "subset": "",
        "loadGoogle": true,
        "color": "#e8e6e1",
        "textTransform": ""
      }
    ],
    "linkUnderline": "hover",
    "linkColor": "#e8e6e1",
    "linkHoverColor": "#c0403d",
    "columns": 2,
    "mobileColumns": 1
  },
  "innerBlocks": [
    {"name": "kadence/listitem", "attributes": {"text": "Documentaires", "link": "/films/"}},
    {
      "name": "kadence/listitem",
      "attributes": {"text": "Portraits filmés <mark class=\"kt-highlight\">nouveau</mark>", "markColor": "#c0403d"}
    },
    {
      "name": "kadence/listitem",
      "attributes": {
        "text": "YouTube (nouvel onglet)",
        "link": "https://www.youtube.com/",
        "target": "_blank",
        "icon": "fe_youtube"
      }
    },
    {"name": "kadence/listitem", "attributes": {"text": "Sans icône", "showIcon": false}}
  ]
}
```

`core/list` (**E**) produit `<ul style="color:#a9b6c0" class="wp-block-list has-text-color"><li>…</li></ul>` :

```json
{
  "name": "core/list",
  "attributes": {"style": {"color": {"text": "#a9b6c0"}}},
  "innerBlocks": [
    {"name": "core/list-item", "attributes": {"content": "Liste native, puce standard"}},
    {
      "name": "core/list-item",
      "attributes": {"content": "Deuxième élément avec <a href=\"https://example.org\">lien</a>"}
    }
  ]
}
```

---

## 8. `kadence/countup` (compteur)

**Rendu enregistré** (**E**) : `<div class="wp-block-kadence-countup kb-count-up-<ID> kb-count-up" data-start="0" data-end="120" data-prefix="" data-suffix="+" data-duration="2" data-separator=""><div class="kb-count-up-process kb-count-up-number"></div><div class="kb-count-up-title">films réalisés</div></div>`.

Le nombre est **vide dans le HTML**. C'est le script `kb-countup.min.js` qui le remplit :
- sans JavaScript, il reste vide ;
- avec JavaScript, il vaut « 0 » tant que **tout** le bloc n'est pas visible à l'écran (`isInViewport` exige top ≥ 0 et bottom ≤ hauteur de la fenêtre), puis il s'anime au défilement ;
- le script ajoute un texte pour lecteur d'écran (`.screen-reader-text`) contenant la valeur finale.

**E** : capture sans JavaScript, nombre vide ; capture mobile sur toute la page, « 0 » sous la ligne de flottaison ; « 25 », « 120+ », « 1 500 000 », « 14 » après défilement.

Conséquences :
- les captures pleine page montrent « 0 » pour les compteurs situés sous la ligne de flottaison. Un compteur visible dès le chargement est capturé **en cours d'animation**, avec une valeur intermédiaire. Exemple à la contre-vérification, capture 1280×900 : « 118+ » et « 1 499 882 » au lieu de « 120+ » et « 1 500 000 ». La capture ne montre donc pas forcément la valeur finale ;
- les moteurs de recherche et les visiteurs sans JavaScript ne voient pas les chiffres.

Pour des chiffres clés fiables, préférer la **version statique** (10.4), visuellement identique (**E**).

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `start`, `end` | number | Valeurs de départ et d'arrivée | `0`, `100` | E |
| `duration` | number | Durée en secondes | `2.5` | E (2) |
| `prefix`, `suffix` | string | Texte avant / après le nombre | `""` | E (`"+"`) |
| `separator` | string | Séparateur des milliers. `" "` produit « 1 500 000 ». | `""` | E |
| `decimal`, `decimalSpaces` | string / number | Séparateur décimal (par exemple `","`) et nombre de décimales. Enregistrés en `data-decimal=","` et `data-decimal-spaces="1"`. `end: 3.5` s'affiche « 3,5 », mais le texte pour lecteur d'écran reste « 3.5 ». | `""`, `2` | E (contre-vérification) |
| `title`, `displayTitle` | string / boolean | Libellé sous le nombre | `""`, `true` | E |
| `titleFont` | array | `[{"level":4,"htmlTag":"div","size":[…],"sizeType":"px","lineHeight":[…],"lineType":"","letterSpacing":0.14,"letterType":"em","textTransform":"uppercase","family":"…","google":false,"style":"","weight":"500","variant":"","subset":"","loadGoogle":true}]` | `htmlTag "div"`, `level 4` | E |
| `titleColor`, `titleAlign` (`[d,t,m]`), `titleMargin`/`titlePadding` (`[h,d,b,g]`, + tablette et mobile) | | | | E (couleur, alignement, marge) |
| `numberFont` | array | Même format que `titleFont`, sans `level` ni `htmlTag` | taille `["50","",""]`, `lineType "px"` | E |
| `numberColor`, `numberAlign`, `numberMargin`, `numberPadding`, `numberMinHeight` | | | | E (couleur, alignement) |

**Particularités des objets typographiques** (méthode `render_typography`, utilisée par countup et iconlist ; **E**) :
- L'unité de `letterSpacing` est lue dans **`letterType`** : `"letterType": "em"` produit `letter-spacing:0.14em`.
- Avec `letterSpacingType` seul, on obtient `letter-spacing:0.14` (sans unité, donc ignoré par le navigateur) et l'avertissement PHP `Undefined array key "letterType"`.
- `style` (italique) n'est appliqué **que si `family` est renseigné**.
- Unité de l'interlignage : `lineType: ""` donne une valeur sans unité. Attention, la valeur par défaut de `numberFont` est `"px"`.

Le filtre PHP `kadence-blocks-countup-static` permettrait de produire le nombre final côté serveur ; il faudrait l'ajouter dans le thème. **C**, non essayé.

---

## 9. Blocs natifs : formats testés et quand les préférer

| Bloc | Attributs testés (E) | À préférer quand |
|---|---|---|
| `core/paragraph` | `content` (HTML) ; `style.color.text` ; `style.typography.fontSize` / `lineHeight` (chaînes CSS) ; `style.spacing.margin.top` / `bottom` ; `style.elements.link.color.text` et `style.elements.link[":hover"].color.text` | Texte courant, descriptions, lignes de liens. Le style est écrit en ligne (`style="color:…;margin-top:0;…"`) : pas de `uniqueID`, pas de dépendance à l'initialisation Kadence. Les couleurs de liens passent par une classe `wp-elements-N` générée au rendu. |
| `core/list` + `core/list-item` | `style.color.text` ; `content` | Liste simple sans icônes. |
| `core/image` | `url` externe, `alt`, `caption`, `aspectRatio: "16/9"`, `scale: "cover"`, `width: "100%"`, `href`, `linkTarget: "_blank"`, `rel`, `linkDestination: "custom"` | Image simple ; recadrage CSS natif. Pas d'`aria-label` pour le lien. |
| `core/spacer` | `height: "32px"` | Espace vertical après un paragraphe (pas de marge négative, voir 2.9). |
| `core/separator` | `className: "is-style-wide"`, `style.color.background` | Trait simple pleine largeur. |

Paragraphe avec liens colorés (`core/paragraph`, **E** : liens `#e8e6e1`, survol `#c0403d`) :

```json
{
  "name": "core/paragraph",
  "attributes": {
    "content": "Voir sur : <a href=\"https://www.instagram.com/\" target=\"_blank\" rel=\"noreferrer noopener\">Instagram</a> · <a href=\"https://www.facebook.com/\" target=\"_blank\" rel=\"noreferrer noopener\">Facebook</a> · <a href=\"https://x.com/\" target=\"_blank\" rel=\"noreferrer noopener\">X</a>",
    "style": {
      "color": {"text": "#a9b6c0"},
      "elements": {"link": {"color": {"text": "#e8e6e1"}, ":hover": {"color": {"text": "#c0403d"}}}},
      "typography": {"fontSize": "0.85rem"},
      "spacing": {"margin": {"top": "0", "bottom": "0"}}
    }
  }
}
```

Les familles de police du cœur WordPress (`fontFamily`, qui n'accepte que les identifiants de préréglage) n'ont pas été testées. Pour une police précise, utilisez `kadence/advancedheading`.

---

## 10. Les quatre specs demandées (testées ensemble sur `ref-texte-et-medias-specs`)

Elles ont été construites deux fois :
- avec les vraies URL `i.ytimg.com` (page `ref-texte-et-medias-specs`) ;
- avec une image locale à la place, pour contrôler le rendu (page `ref-texte-et-medias-specs-visuel`).

Résultat : 0 bloc invalide, aucune erreur JavaScript, aucun débordement horizontal. Captures à 1280, 900 et 390px. **E**

Dans une page réelle, ajoutez la clé `"meta"` de 2.10. Le même contenu a été construit avec ces méta sur `ref-texte-et-medias-specs-meta`. **E**

**Rangées et colonnes de ce chapitre (contre-vérification).** Les extraits `kadence/rowlayout` et `kadence/column` ci-dessous n'ont ni `uniqueID` ni `"borderWidth": ["","","",""]` (colonnes `"attributes": {}`). Ils contredisent donc les règles 1 et 4 de `mise-en-page.md`. Ils fonctionnent tels quels : rejoués sur `ref-texte-et-medias-verif-cartes`, l'éditeur a ajouté `uniqueID` aux rangées, et `uniqueID`, `kbVersion: 2` et `borderWidth` vide aux colonnes. Le rendu est conforme. Dans une spec de production, suivez quand même `mise-en-page.md` : `uniqueID` explicite, `kbVersion: 2`, `colLayout` sur la rangée, `borderWidth` vide sur chaque colonne.

### 10.1 Titre H1 serif de grande taille avec un fragment en italique d'une autre couleur

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Je filme <mark class=\"kt-highlight\">l'engagement</mark> et ceux qui le portent",
    "level": 1,
    "typography": "Newsreader",
    "googleFont": false,
    "fontWeight": "400",
    "fontSize": [88, 60, 40],
    "sizeType": "px",
    "fontHeight": [1.05, 1.1, 1.15],
    "fontHeightType": "",
    "color": "#e8e6e1",
    "markColor": "#c8b287",
    "markFontStyle": "italic",
    "margin": [0, "", 24, ""],
    "marginType": "px",
    "maxWidth": [900, "", ""],
    "maxWidthType": "px"
  }
}
```

Rendu (**E**) :
- Newsreader 88px (60 sur tablette, 40 sur mobile), interlignage 1.05, couleur `#e8e6e1` ;
- « l'engagement » en Newsreader italique (vraie italique, fichier `Newsreader-italic-400.woff2`), couleur `#c8b287` ;
- pas de fond sur le `<mark>` (la feuille de l'extension impose `background:transparent`).

Variante fluide (sans palier) : voir l'extrait de 3.1.

### 10.2 Sur-titre en petites capitales à chasse fixe, espacé
Il n'existe **pas d'attribut `font-variant: small-caps`**. `fontVariant` sert à choisir une variante Google (comme `"500italic"`), pas les petites capitales. L'effet « petites capitales » s'obtient donc avec `textTransform: "uppercase"`, une petite taille et un espacement en `em`, comme `.pd-etiquette` dans la maquette.

```json
{
  "name": "kadence/advancedheading",
  "attributes": {
    "content": "Auteur-réalisateur · documentaire",
    "htmlTag": "p",
    "typography": "IBM Plex Mono",
    "googleFont": false,
    "fontWeight": "500",
    "fontSize": [0.75, "", ""],
    "sizeType": "rem",
    "letterSpacing": 0.14,
    "letterSpacingType": "em",
    "textTransform": "uppercase",
    "color": "#c8b287",
    "margin": [0, "", 16, ""],
    "marginType": "px"
  }
}
```

CSS produit (**E**) : `font-size:0.75rem;font-weight:500;font-family:'IBM Plex Mono';text-transform:uppercase;letter-spacing:0.14em;color:#c8b287;margin-top:0px;margin-bottom:16px`. Espacement mesuré : 1.68px à 12px.

La rangée « héros » qui contient les deux blocs :

```json
{
  "name": "kadence/rowlayout",
  "attributes": {
    "kbVersion": 2,
    "columns": 1,
    "colLayout": "equal",
    "tabletLayout": "inherit",
    "mobileLayout": "row",
    "padding": [32, 24, 32, 24],
    "paddingUnit": "px"
  },
  "innerBlocks": ["…"]
}
```

(Ses `innerBlocks` : une `kadence/column` vide d'attributs contenant le sur-titre puis le H1.)

### 10.3 Carte film
Contenu de la carte :
- vignette YouTube 16/9 cliquable vers la vidéo (nouvel onglet) ;
- titre ;
- ligne de description ;
- ligne « Voir sur : Instagram · Facebook · X » avec trois liens.

C'est une **colonne composée**. L'infobox est écartée : liens imbriqués, voir 5.

```json
{
  "name": "kadence/column",
  "attributes": {},
  "innerBlocks": [
    {
      "name": "kadence/image",
      "attributes": {
        "url": "http://127.0.0.1:8095/hqdefault-test.png",
        "alt": "Vignette : Forces spéciales et 1er RCP à Tessalit",
        "useRatio": true,
        "ratio": "land169",
        "link": "https://www.youtube.com/watch?v=0ynsZ42MuU4",
        "linkTarget": true,
        "linkTitle": "Lire « Forces spéciales et 1er RCP à Tessalit » sur YouTube (nouvel onglet)",
        "borderRadius": [2, 2, 2, 2],
        "borderRadiusUnit": "px",
        "marginDesktop": [0, 0, 12, 0],
        "marginUnit": "px"
      }
    },
    {
      "name": "kadence/advancedheading",
      "attributes": {
        "content": "Forces spéciales et 1er RCP à Tessalit",
        "level": 3,
        "typography": "Newsreader",
        "googleFont": false,
        "fontWeight": "400",
        "fontSize": [1.4, "", ""],
        "sizeType": "rem",
        "fontHeight": [1.2, "", ""],
        "fontHeightType": "",
        "color": "#e8e6e1",
        "margin": [0, "", 6, ""],
        "marginType": "px"
      }
    },
    {
      "name": "core/paragraph",
      "attributes": {
        "content": "8 février 2013 · 2 min 32",
        "style": {
          "color": {"text": "#a9b6c0"},
          "typography": {"fontSize": "0.92rem", "lineHeight": "1.5"},
          "spacing": {"margin": {"top": "0", "bottom": "6px"}}
        }
      }
    },
    {
      "name": "kadence/advancedheading",
      "attributes": {
        "content": "Voir sur : <a href=\"https://www.instagram.com/\" target=\"_blank\" rel=\"noreferrer noopener\">Instagram</a> · <a href=\"https://www.facebook.com/\" target=\"_blank\" rel=\"noreferrer noopener\">Facebook</a> · <a href=\"https://x.com/\" target=\"_blank\" rel=\"noreferrer noopener\">X</a>",
        "htmlTag": "p",
        "fontSize": [0.85, "", ""],
        "sizeType": "rem",
        "color": "#a9b6c0",
        "linkColor": "#e8e6e1",
        "linkHoverColor": "#c0403d",
        "linkStyle": "underline",
        "margin": [0, "", 0, ""],
        "marginType": "px"
      }
    }
  ]
}
```

La rangée de trois cartes : 3 colonnes, 2 par ligne sur tablette, 1 par ligne sur mobile.

```json
{
  "name": "kadence/rowlayout",
  "attributes": {
    "kbVersion": 2,
    "columns": 3,
    "colLayout": "equal",
    "tabletLayout": "two-grid",
    "mobileLayout": "row",
    "padding": [32, 24, 32, 24],
    "paddingUnit": "px"
  },
  "innerBlocks": ["…"]
}
```

(`innerBlocks` = trois colonnes comme ci-dessus, avec les vidéos `0ynsZ42MuU4`, `2S8XpTEGSH0`, `p5W9PKR6FdU`.)

Rendu mesuré dans une colonne de 389px (**E**) :

| Élément | Mesure |
|---|---|
| Vignette | 389×219, `margin-bottom:12px`, coins de 2px |
| Titre | Newsreader 22.4px, `margin:0 0 6px` |
| Description | 14.72px, `#a9b6c0`, `margin:0 0 6px` |
| Ligne « Voir sur » | 13.6px, liens `#e8e6e1` soulignés, `#c0403d` au survol |

Code HTML du lien de la vignette : `<a href="https://www.youtube.com/watch?v=0ynsZ42MuU4" class="kb-advanced-image-link" target="_blank" aria-label="Lire « Forces spéciales et 1er RCP à Tessalit » sur YouTube (nouvel onglet)" rel="noopener noreferrer">`.

Variante possible : mettre aussi le lien sur le titre (`link`, `linkTarget`, `linkStyle: "none"`). On obtient alors deux liens vers la même vidéo ; ce n'est pas fait dans la spec, comme dans la maquette.

### 10.4 Rangée de 4 chiffres clés

**Version animée (`kadence/countup`).** Rangée de 4 colonnes, 2×2 sur tablette et mobile :

```json
{
  "name": "kadence/rowlayout",
  "attributes": {
    "kbVersion": 2,
    "columns": 4,
    "colLayout": "equal",
    "tabletLayout": "two-grid",
    "mobileLayout": "two-grid",
    "padding": [32, 24, 32, 24],
    "paddingUnit": "px"
  },
  "innerBlocks": ["…"]
}
```

Chaque colonne contient un compteur. Exemple de la deuxième colonne :

```json
{
  "name": "kadence/countup",
  "attributes": {
    "start": 0,
    "end": 120,
    "duration": 2,
    "prefix": "",
    "suffix": "+",
    "separator": "",
    "title": "films réalisés",
    "numberColor": "#e8e6e1",
    "numberFont": [
      {
        "size": [56, 44, 36],
        "sizeType": "px",
        "lineHeight": [1, "", ""],
        "lineType": "",
        "letterSpacing": "",
        "textTransform": "",
        "family": "Newsreader",
        "google": false,
        "style": "",
        "weight": "400",
        "variant": "",
        "subset": "",
        "loadGoogle": true
      }
    ],
    "numberAlign": ["left", "", ""],
    "titleColor": "#c8b287",
    "titleFont": [
      {
        "level": 4,
        "htmlTag": "div",
        "size": [12, "", ""],
        "sizeType": "px",
        "lineHeight": [1.4, "", ""],
        "lineType": "",
        "letterSpacing": 0.14,
        "letterType": "em",
        "textTransform": "uppercase",
        "family": "IBM Plex Mono",
        "google": false,
        "style": "",
        "weight": "500",
        "variant": "",
        "subset": "",
        "loadGoogle": true
      }
    ],
    "titleAlign": ["left", "", ""],
    "titleMargin": [8, 0, 0, 0]
  }
}
```

Les autres colonnes sont identiques, à l'exception de `end`, `title`, `suffix` et `separator` :

| Colonne | `end` | `title` | `suffix` | `separator` |
|---|---|---|---|---|
| 1 | `25` | « ans de tournages » | `""` | `""` |
| 2 | `120` | « films réalisés » | `"+"` | `""` |
| 3 | `1500000` | « vues cumulées » | `""` | `" "` |
| 4 | `14` | « pays traversés » | `""` | `""` |

Ces chiffres sont des exemples de mise en page, pas des données réelles.

**Version statique (recommandée).** Même rangée ; chaque colonne contient deux titres avancés en `p`. Le rendu est identique, sans JavaScript, et le nombre est présent dans le HTML. **E**

```json
{
  "name": "kadence/column",
  "attributes": {},
  "innerBlocks": [
    {
      "name": "kadence/advancedheading",
      "attributes": {
        "content": "120+",
        "htmlTag": "p",
        "typography": "Newsreader",
        "googleFont": false,
        "fontWeight": "400",
        "fontSize": [56, 44, 36],
        "sizeType": "px",
        "fontHeight": [1, "", ""],
        "fontHeightType": "",
        "color": "#e8e6e1",
        "margin": [0, "", 8, ""]
      }
    },
    {
      "name": "kadence/advancedheading",
      "attributes": {
        "content": "films réalisés",
        "htmlTag": "p",
        "typography": "IBM Plex Mono",
        "googleFont": false,
        "fontWeight": "500",
        "fontSize": [12, "", ""],
        "sizeType": "px",
        "letterSpacing": 0.14,
        "letterSpacingType": "em",
        "textTransform": "uppercase",
        "color": "#c8b287",
        "margin": [0, "", 0, ""]
      }
    }
  ]
}
```

---

## 11. Récapitulatif des pièges

1. Rangée sans `colLayout` : aucun `uniqueID`, aucun style. Rangée sans `kbVersion: 2` : pas de grille. (2.2)
2. Vérifier l'absence de `undefined` et la présence de `uniqueID` dans `lire.php`. (2.1)
3. Titres sans `color` : couleur du thème selon le niveau (`#1A202C` pour h1–h3, `#2D3748` pour h4–h5, `#4A5568` pour h6), invisible sur fond sombre. Sans `fontWeight` : gras 700. (2.7)
4. `<mark class="kt-highlight">` sans `markColor` : orange `#f76a0c`. (2.8)
5. `googleFont: true` : chargement depuis fonts.googleapis.com, interdit. (2.7)
6. `paletteN` : palette Kadence d'origine (bleue), car la palette du site n'est pas réglée. (2.6)
7. Infobox entièrement cliquable + liens dans le texte : bloc invalide. Objets partiels : classes `undefined`. Fond clair par défaut. (5)
8. `kadence/spacer` juste après un paragraphe : remonte de 2rem. `dividerEnable` vaut `true` par défaut. (2.9, 6)
9. Compteur : nombre vide sans JavaScript, « 0 » hors de l'écran. Unité d'espacement à mettre dans `letterType`. Italique seulement si `family` est renseigné. (8)
10. Une seule unité pour les trois tailles d'écran. Les anciens attributs (`size`, `lineHeight`, `topMargin`…) sont prioritaires et ne doivent pas être utilisés. (2.3, 3)
11. `showCaption: false` supprime la légende du code HTML enregistré. (4)
12. L'aperçu de l'éditeur ne charge ni les polices ni les variables du thème enfant. (2.6)
13. Décalage de 16px vers la gauche sous 720px si la spec n'a pas de `"meta"` de page. (2.10)

## 12. Ce qui n'a PAS pu être vérifié

- **Affichage réel des vignettes `https://i.ytimg.com/…/hqdefault.jpg`** : le domaine est bloqué par le proxy du bac à sable (CONNECT 403). Le code HTML, le CSS et le recadrage ont été vérifiés avec une image locale qui imite `hqdefault` (480×360 avec bandes noires).
- Formats des vignettes YouTube : `hqdefault` 480×360 avec bandes noires, `mqdefault` 320×180 en 16/9, `maxresdefault` 1280×720 pas toujours disponible. C'est une connaissance générale, non vérifiée ici.
- Comportement des réglages de l'éditeur Kadence si un humain modifie à la main un attribut rempli par une valeur non standard (`fontSize` en `clamp()`, `typography: "var(--display)"` ou une pile de polices, couleurs `var(--…)`). Seuls la validité du bloc et le rendu public ont été vérifiés.
- Attributs marqués **C** ou **—** dans les tableaux, notamment :
  - `textShadow`, dégradés et icônes du titre avancé ;
  - ~~`borderRadius` du titre avancé~~ et ~~`decimal` du compteur~~ : vérifiés depuis (voir Contre-vérification) ;
  - `learnMoreStyles`, ombres, `maxWidth` et `mediaAlign` gauche/droite de l'infobox ;
  - style `stacked` de la liste à icônes ;
  - `imageFilter`, superpositions et masques de l'image ;
  - ~~`colorClass`~~ : vérifié depuis (voir Contre-vérification).
- Le filtre `kadence-blocks-countup-static` (il faut du code PHP dans le thème).
- Les familles de police natives de WordPress (`core/paragraph` `fontFamily`).

## 13. Traçabilité

Pages d'essai (préfixe `ref-texte-et-medias-`), toutes publiées sur le WordPress de test :

| Fichier de spec | Page | Contenu |
|---|---|---|
| `t1-titres.json` | `titres` | Sur-titre, H1 avec mark, H2 palette/marges, H3 lien, span, div |
| `t2-titres-variantes.json` | `titres-variantes` | `clamp`, `var()`, pile de polices, mark sans couleur, couleurs du cœur, bordure |
| `t3-images.json` | `images` | Image i.ytimg, image locale avec légende, `core/image`, largeur max |
| `t4-listes-espaces.json` | `listes` | Paragraphe, espaceurs, liste à icônes, `core/list`, séparateur, `core/spacer` |
| `t5-infobox.json` | `infobox` | Boîte cliquable à icône, liens imbriqués (invalide), objets partiels |
| `t6-compteurs.json` | `compteurs` | Compteurs |
| `t7-specs.json` / `t7-specs-visuel.json` | `specs` / `specs-visuel` | Les quatre specs du chapitre 10 |
| `t8-cas-limites.json` | `cas-limites` | `letterSpacingType` seul, `<br>` et nofollow, `imagePosition`, infobox en mode learnmore |
| `t9-google.json` | `google` | Contre-exemple `googleFont: true` |
| `t10-mark.json` | `surlignage` | Surlignage complet |
| `t11-paragraphe-liens.json` | `paragraphe-liens` | Couleurs de liens de `core/paragraph` |
| `t12-specs-meta.json` | `specs-meta` | Chapitre 10 avec les méta de page (correction du décalage mobile) |

Les fichiers de spec, captures et scripts d'inspection se trouvent dans `scratchpad/ref/texte-et-medias/` (dossier temporaire de la session) :
- `inspect.js` : styles calculés ;
- `rules.js` : règles CSS appliquées ;
- `attente.js` : capture après animation ;
- `gen/specs.py` : générateur des specs du chapitre 10 ;
- `gen/remplir.py` : insertion des extraits dans cette fiche.

L'image locale de contrôle était servie sur `http://127.0.0.1:8095/` pendant les essais. Elle n'est plus disponible : la page `…-specs-visuel` n'affichera plus ses vignettes.

## 14. Contre-vérification (7 octobre 2026)

Relecture sceptique. Le but était de réfuter les affirmations les plus utiles à un développeur : noms d'attributs, formats, valeurs par défaut et specs d'exemple.

### 14.1 Méthode
- **Extraits rejoués tels quels.** Les 30 blocs JSON de la fiche ont été extraits automatiquement (script `extraire.py`) ; tous sont du JSON valide. Une seule modification : l'URL de l'image locale (`127.0.0.1:8095`, qui ne répond plus) a été remplacée par la même image servie sur `127.0.0.1:8096`. Ce serveur a été arrêté après les essais : les pages `…-verif-*` n'affichent plus leurs vignettes.
- **Contrôles après chaque `construire`** :
  - validité des blocs après rechargement ;
  - sortie de `lire.php` : `uniqueID` présents, aucun `undefined` ;
  - CSS public de `kadence_blocks_css-inline-css` ;
  - styles calculés avec Playwright ;
  - captures à 1280 et 390px.
- **Code source relu** :
  - les `block.json` d'`advancedheading`, `image`, `infobox`, `spacer`, `iconlist`, `listitem` et `countup` ;
  - les fonctions `build_css` de ces blocs ;
  - dans `class-kadence-blocks-css.php` : les préréglages d'espacement et de taille de police, `render_measure_output`, `render_typography`, `render_color` et `sanitize_color` ;
  - dans `class-kadence-blocks-abstract-block.php` : le CSS du `<head>` est construit à partir des attributs bruts, sans fusion des valeurs par défaut, ce qui confirme 2.8 ;
  - `kb-countup.min.js` : `isInViewport` et le texte pour lecteur d'écran ;
  - le CSS du thème (`content.min.css`, CSS en ligne des titres) ;
  - dans le thème enfant : `pd.css`, `fonts.css` et `functions.php`.
- Fichiers de travail : `scratchpad/ref/texte-et-medias-verif/` (`spec-A.json` à `spec-E.json`, `specs.py`, `inspect.js`, captures).

### 14.2 Pages rejouées

| Page (`ref-texte-et-medias-verif-…`) | Ce qui a été rejoué | Résultat |
|---|---|---|
| `titres` (page 122) | Les 7 extraits du chapitre 3 (3.1 ×2, 3.2, 3.3, 3.4 ×2, 3.5), plus 10.2 et 10.1, avec la clé `meta` de 2.10 | **Conforme.** 0 bloc invalide, 9 `uniqueID` au format `122_xxxxxx-xx`, aucun `undefined`. CSS identique à celui annoncé : surlignage complet avec `text-align:center!important` sous 767px, `var(--global-kb-spacing-lg, 3rem)`, `var(--global-palette1, #3182CE)`, `display:block` du span, `var(--global-kb-font-size-xl, 3rem)`, bordure basse répétée en tablette et mobile, sur-titre à `letter-spacing:0.14em` (1.68px mesuré), H1 88 / 60 / 40px. H2 et H3 sans `fontWeight` : 700 mesuré. Aucun lien `fonts.googleapis.com`. |
| `medias` (page 124) | Chapitre 4 (3 `kadence/image` et `core/image`), 5.1, 5.2, les 3 `kadence/spacer`, `core/spacer`, `core/separator`, chapitre 7 (liste à icônes et 4 éléments), `core/list`, `core/paragraph` du chapitre 9 | **Conforme.** 0 bloc invalide. HTML enregistré identique aux modèles des chapitres 4, 6 et 7. `kbVersion: 2` ajouté automatiquement aux infobox. Bordure, survol et `padding:24px` de 5.1. Image de 5.2 : `width:480px;max-width:100%`, `padding-bottom:56.25%`. Espaceurs : `rgba(200, 178, 135, 0.60)`, `height:3rem`, trait de 120px en `dashed` de 2px. Liste : `margin-bottom:var(--global-kb-spacing-sm, 1.5rem)` sans `listMargin`, et SVG vide avec `showIcon: false`. Liens du paragraphe en `#e8e6e1` (classe `wp-elements-1`). Séparateur de 3px. |
| `cartes` (page 126) | Rangée héros de 10.2, rangée de trois cartes de 10.3, 4 compteurs de 10.4 (tableau des colonnes appliqué) et version statique | **Conforme.** 0 bloc invalide. Mesures identiques au tableau de 10.3 : vignette 389×219, titre 22.4px, description 14.72px, ligne « Voir sur » 13.6px avec liens soulignés. `aria-label` présent sur le lien de la vignette. Compteurs : nombre vide dans le HTML, `letter-spacing:0.14em`, 56 / 44 / 36px. Aucun débordement horizontal à 1280 ni à 390px. |
| `cas` (page 132) | Cas complémentaires pour les attributs marqués **C** | Lien du titre `nofollow` + `sponsored` : `rel="noopener noreferrer nofollow sponsored"`. `markBGOpacity: 0.5` : `rgba(163, 48, 47, 0.5)`. `borderRadius` du titre : 8px. `tabletLetterSpacing` / `mobileLetterSpacing` : 2 / 3px. `colorClass` rempli : aucune couleur produite. `marginType: "rem"` appliqué aussi à `tabletMargin`. `kadence/spacer` après un paragraphe : `margin-top:-32px`, ce qui le fait chevaucher le paragraphe (2.9). Image `useRatio` sans `ratio` : `kb-image-ratio-land43`. Lien d'image `rel="nofollow sponsored"`. Compteur avec `letterSpacingType` seul : `letter-spacing:0.14` sans unité et avertissement `Undefined array key "letterType"` dans `debug.log`. Italique ignorée sans `family`. `decimal: ","` : « 3,5 » affiché. Infobox à objets partiels : `kt-info-media-animate-undefined`. `has-palette-1-color` : noir ; `has-theme-palette-1-color` : bleu. |
| `invalide` (page 136, sans méta) | Infobox `linkProperty: "box"` avec un `<a>` dans `contentText` | **Conforme au piège 1 du chapitre 5** : bloc invalide au rechargement (« Expected token … StartTag a »). Sans méta, l'article est à x = −16px à 390px (2.10 confirmé). |

### 14.3 Erreurs trouvées et corrigées dans la fiche
1. **2.7 et piège 3 du chapitre 11** : la couleur par défaut des titres n'est pas `palette3` pour tous. Le CSS du thème donne `palette3` à h1–h3, `palette4` (`#2D3748`) à h4–h5 et `palette5` (`#4A5568`) à h6. Mesuré : un h4 sans `color` sort en `rgb(45, 55, 72)`.
2. **Chapitre 8** : « les captures pleine page montrent « 0 » » n'est vrai que sous la ligne de flottaison. Un compteur visible au chargement est capturé en cours d'animation (« 118+ » et « 1 499 882 » observés à 1280px).
3. **Tableau du chapitre 4** : `ratio` n'a pas de valeur par défaut dans le `block.json` (la fiche indiquait `""`). Un `ratio` absent produit `land43`.
4. **Tableau du chapitre 5** : `#4A5568` est la couleur du **texte** du bouton « en savoir plus », pas un fond gris. Le fond est transparent.
5. **Chapitre 5, piège 2** : `data-stroke` ne disparaît que si `width` manque dans `mediaIcon`.

### 14.4 Compléments ajoutés
- **2.6** : variables `--encre` et `--encre-doux`, et piles de polices `--display`, `--corps` et `--mono` de `pd.css`.
- **2.10** : avec les méta, un bloc placé hors d'une rangée touche le bord de l'écran (x = 0).
- **3.1** : la classe de palette valide est `has-theme-palette-1-color`.
- **Chapitre 10** : les extraits de rangées et de colonnes n'appliquent pas les règles 1 et 4 de `mise-en-page.md`. Ils fonctionnent (l'éditeur complète les attributs), mais ces règles restent à suivre en production.
- **Passés de C à E** dans les tableaux : `linkSponsored`, `borderRadius`, `markBGOpacity`, `tabletLetterSpacing` / `mobileLetterSpacing`, `colorClass`, `marginType` en `rem` (titre avancé) ; `linkNoFollow` / `linkSponsored` (image) ; `decimal` / `decimalSpaces` (compteur).

### 14.5 Toujours non vérifié après la contre-vérification
- L'affichage réel des vignettes `i.ytimg.com` : le domaine est toujours inaccessible depuis le bac à sable.
- Le comportement de l'éditeur Kadence si un humain modifie à la main les valeurs non standard (`clamp()`, `var(--…)`, piles de polices).
- **2.2** (rangée sans `kbVersion` ou sans `colLayout`) : non rejoué ici. Le code (`!colLayout` dans `blocks-rowlayout.js`) et la contre-vérification de `mise-en-page.md` (règle 10) concordent.
- `googleFont: true` : non reconstruit. Seule la page d'essai de l'auteur (`ref-texte-et-medias-google`) a été relue ; elle contient bien `<link … fonts.googleapis.com/css?family=Newsreader:regular…>`.
- Les attributs encore marqués **C** ou **—** au chapitre 12.
