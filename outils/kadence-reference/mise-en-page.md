# Kadence : blocs de structure `kadence/rowlayout` et `kadence/column`

Fiche de référence pour générer des specs JSON (outil `outils/wp-test/editeur.js construire`).
Environnement vérifié : WordPress 7.1.3 (fr_FR), thème Kadence 1.5.2 + thème enfant `kadence-pascal`, Kadence Blocks **3.7.12.1** (gratuit).

Noms dans l'interface (en anglais, aucune traduction française de Kadence Blocks n'est installée) :
- `kadence/rowlayout` s'appelle « Row Layout ». C'est la rangée : fond pleine largeur et grille CSS des colonnes.
- `kadence/column` s'appelle « Section ». C'est une cellule de la grille, avec son propre fond, ses bordures et ses espacements.

Légende de la colonne « Vérif. » :
- **T** : testé en réel avec l'outil (page `ref-mise-en-page-*`, contenu enregistré relu avec `lire.php`, CSS public lu et mesuré avec `getComputedStyle` à 1280, 900 et 375 px).
- **C** : lu dans le code source seulement (`dist/blocks/*/block.json`, `includes/blocks/class-kadence-blocks-row-layout-block.php`, `class-kadence-blocks-column-block.php`, `includes/class-kadence-blocks-css.php`, `dist/blocks-rowlayout.js`, `dist/blocks-column.js`).

Points de rupture des feuilles CSS générées : **tablette ≤ 1024 px**, **mobile ≤ 767 px**, bureau ≥ 1025 px. Les règles mobiles s'ajoutent aux règles tablette (mobile ⊂ tablette).

---

## 0. Règles à respecter dans toute spec

1. **Mettre `uniqueID` et `"kbVersion": 2` sur chaque `kadence/rowlayout` ET sur chaque `kadence/column`.** [T]
   - Si la rangée n'a pas `uniqueID` **ou** pas `kbVersion: 2`, le rendu public **n'a ni conteneur ni CSS** : les colonnes sont sorties nues, sans grille ni fond. Constaté sur `ref-mise-en-page-01-minimal`, sur la page `essai` (uniqueID présent, kbVersion absent) et avec `do_blocks()` sur les trois combinaisons.
   - L'éditeur est censé ajouter ces deux attributs tout seul, mais avec l'outil ce n'est **pas fiable**. Dans `01-minimal`, rien n'a été ajouté avant l'enregistrement (cette rangée n'avait pas non plus de `colLayout`, voir règle 10).
   - Contre-vérification (`ref-mise-en-page-verif-collayout`, rangée sans `uniqueID` ni `kbVersion` mais avec `colLayout`) : l'éditeur a ajouté un `uniqueID` à la rangée et à ses colonnes, et `kbVersion: 2` aux colonnes, mais **pas** `kbVersion` à la rangée. Le code (`blocks-rowlayout.js`) fixe `kbVersion` en modifiant l'objet d'attributs sur place ; la valeur n'est donc pas enregistrée. Résultat : toujours aucun conteneur en rendu public. [T]
   - Le PHP ne produit le CSS d'un bloc que si son `uniqueID` est non vide (`render_css`, `output_head_data`).
2. **Format de `uniqueID`** : caractères `[A-Za-z0-9_-]`, unique dans la page. Utiliser des tirets, par exemple `pd-accueil-hero` ou `pd-accueil-hero-c1`. **Éviter la forme `a_b`** (exactement un `_`) : à l'ouverture dans l'éditeur, si la partie avant le `_` n'est pas l'ID de la page, l'ID est régénéré. Constaté : `x_y` est devenu `12_7fc3a9-48`. [T]
3. **Ne jamais cibler `uniqueID` dans du CSS ou du JS maison.** Quand l'outil reconstruit une page **existante**, les `uniqueID` **peuvent** être régénérés au format `<idPage>_<hash>` si les anciens blocs les ont déjà réservés dans l'éditeur. Constaté sur `ref-mise-en-page-modeles` : `mep-m1` est devenu `40_763096-ec`. Le rendu reste identique, mais les sélecteurs `.kb-row-layout-idmep-m1` ne correspondent plus. Pour styler, utiliser `className` ou `anchor`. [T]
   - Ce n'est **pas systématique**. En contre-vérification, `ref-mise-en-page-verif-m1` et `ref-mise-en-page-verif-m3`, reconstruites une seconde fois avec la même spec, ont gardé leurs `uniqueID` (`vrf-m1`, `vrf-m3-c1`…). Le code de Kadence ne libère jamais un ID réservé : tout dépend donc du moment où les anciens blocs ont été affichés avant leur remplacement par l'outil. Comme le résultat est imprévisible, la règle reste la même. [T]
4. **Sur chaque `kadence/column`, mettre `"borderWidth": ["","","",""]`.** [T]
   - La valeur par défaut est `[0,0,0,0]`. Quand l'éditeur monte la colonne, une migration recopie `borderWidth` dans `borderStyle` (`0||""`, donc `""`) et **efface les épaisseurs** de `borderStyle`.
   - Constaté : avec une épaisseur de 1 px, `"top":["palette6","solid",1]` a été enregistré `"top":["palette6","solid",""]` et la bordure a disparu (`04-colonnes`). Avec `borderWidth` vide, elle est conservée (`05-espacements`).
   - Contre-vérification : reproduit sur `ref-mise-en-page-verif-collayout` (bordure de 0 px sans `borderWidth`, 1 px avec). La migration ne s'exécute que si la colonne est **affichée** dans l'éditeur. Sous une rangée sans `colLayout` (règle 10), l'épaisseur a été enregistrée intacte (`verif-fragments`, rangée E), mais elle sera effacée dès que quelqu'un choisira une disposition et enregistrera. [T]
5. **`columns` = nombre de `kadence/column` enfants.** Un multiple est possible pour une grille sur plusieurs lignes : 6 colonnes enfants dans `columns: 4` donnent 4 + 2 au bureau, puis 2 × 3 et 1 × 6 (`06-divers`). [T] Si `columns` est absent, il vaut 2 : 3 enfants feraient alors 2 + 1. [C]
6. **Ne pas utiliser les anciens attributs** `topPadding`, `bottomPadding`, `leftPadding`, `rightPadding`, `topPaddingM`…, `topMargin`, `bottomMargin`, `topMarginT`, `topMarginM`…, ni `border`/`borderWidth` sur la rangée. L'éditeur les migre et **écrase** les tableaux modernes. Constaté : `margin:[40,"",40,""]` + `topMargin:10` a été enregistré `margin:[10,"","",""]`, la marge basse est perdue (`modeles`, rangée X2). [T]
7. **Les valeurs égales au défaut ne sont pas enregistrées** : `columns: 2`, `mobileLayout: "row"`, `tabletLayout: "inherit"`, `paddingUnit: "px"`, `padding: ["sm","","sm",""]`, etc. Le PHP calcule le CSS à partir des attributs **réellement enregistrés**, sans y appliquer les défauts du block.json. Un attribut absent signifie donc « aucune règle générée », et c'est la feuille de style de base qui s'applique. [T]
8. **Méta de page** : garder `_kad_post_layout: "fullwidth"`, `_kad_post_content_style: "unboxed"`, `_kad_post_vertical_padding: "hide"` et `_kad_post_title: "hide"`, comme `construire.py`. La clé `"meta"` de la spec les applique (vérifié : contenu collé sous l'en-tête, sans titre). Sans ces méta, au mobile, une rangée non alignée est décalée de −16 px (`entry-content` à x = −16 px, largeur 407 px pour un écran de 375 px ; page `07-sans-meta`). [T]
9. **Côtés gauche et droit sans padding** : une rangée sans `align: "full"` et sans fond n'a **aucun** padding latéral. Son contenu touche les bords de l'écran (mesuré : 0 px). Avec `align: "full"` ou un fond (classe `kt-row-has-bg`), la feuille de base ajoute `var(--global-content-edge-padding)`, soit 1,5 rem = 24 px, tant que `padding[1]`/`padding[3]` sont vides (`09-bords`). [T]
10. **Mettre `colLayout` sur chaque `kadence/rowlayout`, même avec `"columns":1`** (`"colLayout":"equal"` par défaut). [T, ajouté à la contre-vérification]
    - Sans `colLayout`, le rendu public est correct, puisque le PHP prend `equal`. Mais **l'éditeur affiche le sélecteur « Select Your Layout » à la place des colonnes** : elles restent dans le contenu, mais sont invisibles et impossibles à modifier dans l'éditeur.
    - Ces colonnes ne sont pas montées dans l'éditeur. Elles ne reçoivent donc ni `uniqueID` automatique, ni migration.
    - Constaté sur `ref-mise-en-page-verif-fragments` : les 11 rangées sans `colLayout` affichent le sélecteur et 0 colonne dans le canevas ; la seule rangée avec `colLayout` (`right-golden`) affiche ses 2 colonnes.
    - Dans le code (`blocks-rowlayout.js`), le conteneur des blocs enfants n'est rendu que si `colLayout` est non vide.

---

## 1. Structure HTML produite (rendu public, `kbVersion: 2`) [T]

```html
<section class="kb-row-layout-wrap kb-row-layout-id{uniqueID} alignfull kt-row-has-bg {className} wp-block-kadence-rowlayout" id="{anchor}">
  <div class="kt-row-layout-overlay kt-row-overlay-normal"></div>          <!-- seulement si superposition -->
  <div class="kt-row-column-wrap kt-has-2-columns kt-row-layout-equal kt-tab-layout-inherit kt-mobile-layout-row kt-row-valign-top">
    <div class="wp-block-kadence-column kadence-column{uniqueID} {className}" id="{anchor}">
      <div class="kt-inside-inner-col"> … blocs enfants … </div>
    </div>
  </div>
</section>
```

Où s'applique chaque réglage de la **rangée** :
- élément extérieur (`.kb-row-layout-id…`) : fond, image, dégradé, bordures, rayon, ombre, marges, couleur de texte. Le fond couvre donc toute la largeur ;
- conteneur interne (`> .kt-row-column-wrap`, en `display:grid`) : `maxWidth` avec `margin:auto`, **padding**, hauteur minimale, `grid-template-columns`, gouttières, alignement vertical.

Le padding est **à l'intérieur** du `maxWidth` (`box-sizing: border-box`). Avec `maxWidth: 72rem` et `padding[1]` = `padding[3]` = `md` (2 rem), le texte occupe 68 rem. Mesuré : conteneur de 1152 px, colonne de 1088 px. [T]

Pour une **colonne**, le fond, le padding, les bordures et l'ombre s'appliquent à `.kt-inside-inner-col`. Les marges, `maxWidth` et `text-align` s'appliquent à l'élément extérieur `.kadence-column{uniqueID}`. [T]

---

## 2. Valeurs prédéfinies (jetons)

### 2.1 Espacements (`padding`, `margin` des rangées et des colonnes) [T pour sm, md, lg, xl, 3xl, 4xl ; C pour le reste]

| Jeton | CSS produit |
|---|---|
| `"xxs"` | `var(--global-kb-spacing-xxs, 0.5rem)` |
| `"xs"` | `var(--global-kb-spacing-xs, 1rem)` |
| `"sm"` | `var(--global-kb-spacing-sm, 1.5rem)` |
| `"md"` | `var(--global-kb-spacing-md, 2rem)` |
| `"lg"` | `var(--global-kb-spacing-lg, 3rem)` |
| `"xl"` | `var(--global-kb-spacing-xl, 4rem)` |
| `"xxl"` | `var(--global-kb-spacing-xxl, 5rem)` |
| `"3xl"` | `var(--global-kb-spacing-3xl, 6.5rem)` |
| `"4xl"` | `var(--global-kb-spacing-4xl, 8rem)` |
| `"5xl"` | `var(--global-kb-spacing-5xl, 10rem)` |
| `"ss-auto"` | `var(--global-kb-spacing-auto, auto)` |
| nombre (`0`, `24`, `1.5`) | nombre + unité (`paddingUnit`/`marginUnit` pour la rangée, `paddingType`/`marginType` pour la colonne) |
| `""` | rien : le côté hérite du palier plus large ou du thème |

On peut mélanger jetons et nombres côté par côté, par exemple `["xl", 24, "xl", 24]`. [C] Un jeton ne dépend pas de l'unité.

### 2.2 Gouttières (`columnGutter`, `tabletGutter`, `mobileGutter`, `collapseGutter`, `tabletRowGutter`, `mobileRowGutter`)

| Valeur | CSS | Vérif. |
|---|---|---|
| `"none"` | `var(--global-kb-gap-none, 0rem)` | T |
| `"skinny"` | `var(--global-kb-gap-sm, 1rem)` | T |
| `"default"` | `var(--global-kb-gap-md, 2rem)` | C |
| `"wider"` | `var(--global-kb-gap-lg, 4rem)` | T |
| `"narrow"` / `"wide"` / `"widest"` | `20px` / `40px` / `80px` (absents de l'interface). Anciennes valeurs : sur `columnGutter`, l'éditeur les convertit à l'ouverture en `"custom"` avec `customGutter[0]` = 20, 40 ou 80 (`blocks-rowlayout.js`). Préférer directement `"custom"` | C |
| `"xs"` / `"sm"` / `"md"` / `"lg"` | 0,5 / 1 / 2 / 4 rem (absents de l'interface) | C |
| `"custom"` | valeur lue dans `customGutter[i]` (ou `customRowGutter[i]`) + `gutterType` (ou `rowGutterType`) | T |

Sans attribut, la feuille de base donne `gap: var(--global-row-gutter-md, 2rem)` dans les deux sens. Mesuré : 32 px. [T]

### 2.3 Couleurs [T]

Les champs couleur acceptent :
- `"palette1"` … `"palette9"`. Le PHP produit `var(--global-paletteN, <secours>)` ;
- `"#rrggbb"` ;
- `"rgba(…)"`, testé sur `bgColor`.

Palette actuelle du site (palette Kadence par défaut, lue dans la page) :

| Jeton | Valeur |
|---|---|
| `palette1` | `#2B6CB0` |
| `palette2` | `#215387` |
| `palette3` | `#1A202C` |
| `palette4` | `#2D3748` |
| `palette5` | `#4A5568` |
| `palette6` | `#718096` |
| `palette7` | `#EDF2F7` |
| `palette8` | `#F7FAFC` |
| `palette9` | `#ffffff` |

Le thème définit aussi `--global-palette10` à `--global-palette15`, mais `"palette10"` et au-delà n'ont pas été testés.

Attention : sur ce site au fond sombre, les titres Kadence prennent `palette3` (sombre). Donner `textColor` à la rangée : la règle produite vise la rangée **et** ses `h1`–`h6`. [T]

---

## 3. `kadence/rowlayout` : référence des attributs

### 3.1 Identité et rendu

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `uniqueID` | string | `[A-Za-z0-9_-]`, unique dans la page, sans forme `a_b` | `""` | classe `kb-row-layout-id{ID}` ; **obligatoire** | T |
| `kbVersion` | number | **`2`** | `""` | **obligatoire** : sans lui, pas de conteneur | T |
| `htmlTag` | string | `div`, `header`, `section`, `article`, `main`, `aside`, `footer` ; toute autre valeur donne `div` (constaté avec `nav`) | `"div"` | balise extérieure | T (`section`, `nav`) |
| `anchor` | string | identifiant HTML sans `#` | (aucun) | `id="…"` sur l'élément extérieur, cible des liens `#…` | T |
| `className` | string | classes séparées par des espaces (attribut des « supports » WordPress, absent du block.json) | (aucun) | ajoutées à l'élément extérieur | T |
| `align` | string | `"full"`, `"wide"`, `"center"`, absent | `"none"` | classe `alignfull`, `alignwide`… | T (`full`, `wide`, absent) |

Avec les méta `fullwidth` + `unboxed`, la rangée occupe 100 % de la largeur **quelle que soit** la valeur de `align`. Mesuré : `full`, `wide` et rien donnent 1280 px à 1280 px. `align: "full"` reste utile, car il ajoute le padding latéral du thème (règle 9). [T]

`blockAlignment` est un ancien attribut, inutilisé en version 2. [C]

```json
{"name":"kadence/rowlayout","attributes":{"uniqueID":"pd-films-intro","kbVersion":2,"columns":1,"colLayout":"equal",
 "align":"full","htmlTag":"section","anchor":"presentation","className":"pd-hero pd-test"}, "innerBlocks":[ … ]}
```

Rendu constaté : `<section class="kb-row-layout-wrap kb-row-layout-id… alignfull … pd-hero pd-test wp-block-kadence-rowlayout" id="presentation">`.

### 3.2 Nombre de colonnes et proportions

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `columns` | number | de 1 à 6 | `2` | T |
| `colLayout` | string | voir le tableau ci-dessous. **Obligatoire dans une spec** : absent, le rendu public utilise `equal`, mais l'éditeur affiche le sélecteur de disposition à la place des colonnes (§ 0, règle 10) | `""` | T |
| `firstColumnWidth` … `sixthColumnWidth` | number | **pourcentages** (40 = 40 %) | (aucun) | T |
| `firstColumnWidthTablet` …, `firstColumnWidthMobile` … | number | pourcentages, pour la tablette et le mobile | (aucun) | C |

Valeurs de `colLayout` proposées par l'éditeur (prises dans `blocks-rowlayout.js`), avec le CSS produit par le PHP :

| `columns` | Valeur | Grille |
|---|---|---|
| 1 | `equal` | `minmax(0,1fr)` |
| 2 | `equal` | `repeat(2, 1fr)` [T] |
| 2 | `left-golden` | 2fr 1fr, soit 2/3 – 1/3 [C] |
| 2 | `right-golden` | 1fr 2fr, soit **1/3 – 2/3**. Mesuré : 416 / 832 px [T] |
| 2 | `row` | empilé |
| 3 | `equal` | 3 parts égales |
| 3 | `left-half` | 2fr 1fr 1fr |
| 3 | `right-half` | 1fr 1fr 2fr |
| 3 | `center-half` | 1fr 2fr 1fr [T] |
| 3 | `center-wide` | 1fr 3fr 1fr |
| 3 | `center-exwide` | 1fr 6fr 1fr |
| 3 | `first-row` | 1re colonne sur toute la largeur, puis 2 |
| 3 | `last-row` | 2 colonnes, puis la 3e sur toute la largeur |
| 3 | `row` | empilé |
| 4 | `equal` | [T] |
| 4 | `left-forty` | 2fr 1fr 1fr 1fr |
| 4 | `right-forty` | 1fr 1fr 1fr 2fr |
| 4 | `two-grid` | grille 2 × 2 |
| 4 | `row` | empilé |
| 5 | `equal` | |
| 5 | `row` | empilé |
| 6 | `equal` | |
| 6 | `two-grid` | |
| 6 | `three-grid` | |
| 6 | `row` | empilé |

**Largeurs personnalisées** : si `firstColumnWidth` est renseigné, il remplace `colLayout`. Le CSS produit est :

`minmax(0, calc(40% - ((gouttière * (n-1))/n))) minmax(0, calc(60% - …))`

- La **dernière colonne vaut toujours 100 − la somme des autres** : pour 2 colonnes, `secondColumnWidth` est ignoré par le PHP, mais on le renseigne quand même pour l'éditeur.
- **« 1fr / 1.5fr » = `firstColumnWidth: 40`, `secondColumnWidth: 60`.** Comme la gouttière est retirée à parts égales, le rapport n'est pas exactement 1/1,5. Mesuré avec la gouttière `wider` (64 px) : 403 / 621 px, soit 0,649 au lieu de 0,667. [T]
- 3 colonnes : il faut `firstColumnWidth` **et** `secondColumnWidth`. 4 colonnes : il faut les trois premières, etc. [C]

```json
"columns":2, "colLayout":"equal", "firstColumnWidth":40, "secondColumnWidth":60
```

Mesuré : 496 / 752 px à 1280 px, **conservé en tablette** (344 / 524 px à 900 px), empilé à 375 px (`04-colonnes`, rangée A). [T]

### 3.3 Responsive : tablette, mobile, ordre

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `tabletLayout` | string | mêmes valeurs que `colLayout`, plus `two-grid` pour 3 colonnes et `two-grid`/`three-grid` pour 5 colonnes | `"inherit"` | T (`two-grid`, `row`) |
| `mobileLayout` | string | idem | `"row"` (empilé) | T (`row`, `equal`, `three-grid`) |
| `collapseOrder` | string | `"left-to-right"` ou `"right-to-left"` | `"left-to-right"` | T |
| `collapseOrderTablet` | string | (non lu par le PHP : ne pas l'utiliser) | `""` | C |

Comportement constaté :
- **Par défaut, toutes les rangées s'empilent au mobile** (`mobileLayout` vaut `"row"`). Pour garder les colonnes côte à côte au mobile, indiquer `"mobileLayout":"equal"`. Mesuré à 375 px : 2 × 139,5 px dans une rangée avec 32 px de padding latéral, et 2 × 171,5 px dans une rangée sans padding (`verif-fragments`, rangée I). [T]
- `tabletLayout` absent, ou `"inherit"` qui n'est pas enregistré : aucune règle tablette, la grille du bureau s'applique, **y compris les largeurs personnalisées**, jusqu'à 4 colonnes. [T] Avec 5 ou 6 colonnes sans `tabletLayout`, c'est la mise en page **mobile** qui s'applique en tablette. [C]
- `collapseOrder: "right-to-left"` inverse l'ordre **seulement** sur les paliers où la disposition est `row`, `two-grid`, `three-grid`, `first-row` ou `last-row`. Pour inverser en tablette, il faut donc aussi `tabletLayout: "row"`. Testé : 2 colonnes avec `tabletLayout` et `mobileLayout` à `row` ; la 2e colonne passe en premier à 900 et à 375 px. [T]
- Ordre au cas par cas : l'attribut `collapseOrder` (number) **de la colonne**. Voir la section 4.

Grille de 4 cartes, 4 puis 2 puis 1 :

```json
"columns":4, "colLayout":"equal", "tabletLayout":"two-grid", "mobileLayout":"row"
```

Mesuré : 4 × 248 px, puis 2 × 406 px, puis 1 × 311 px. [T]

### 3.4 Gouttières (espacement entre colonnes)

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `columnGutter` | string | jeton (§ 2.2) ou `"custom"` ; espace **horizontal** (`column-gap`) au bureau | `"default"` | T |
| `tabletGutter` / `mobileGutter` | string | jeton ou `"custom"` ; `""` = hérite | `""` | T |
| `customGutter` | array | `[bureau, tablette, mobile]`, nombres | `["","",""]` | T |
| `gutterType` | string | `px`, `em`, `rem` | `"px"` | T (`px`) |
| `collapseGutter` | string | même chose pour l'espace **vertical** (`row-gap`, entre lignes et colonnes empilées) | `"default"` | T |
| `tabletRowGutter` / `mobileRowGutter` | string | idem | `""` | T |
| `customRowGutter` | array | `[bureau, tablette, mobile]` | `["","",""]` | T |
| `rowGutterType` | string | `px`, `em`, `rem` | `"px"` | T |

**Piège** : `customGutter: [32,24,16]` avec seulement `columnGutter: "custom"` ne produit **que** la valeur du bureau (32 px partout). Mesuré : 32 px à 375 px. Il faut aussi `tabletGutter: "custom"` et `mobileGutter: "custom"`, et de même `tabletRowGutter` et `mobileRowGutter` pour `customRowGutter`. Testé : 32, 24 et 16 px obtenus. [T]

### 3.5 Largeur maximale du contenu

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `maxWidth` | number | nombre | `""` | T |
| `maxWidthUnit` | string | `px`, `%`, `vw`, `rem` (`rem` n'est proposé que par l'un des deux réglages de l'éditeur, voir plus bas) ; **`rem` fonctionne en rendu public** | `"px"` | T (`px`, `rem`) |
| `responsiveMaxWidth` | array | **`[tablette, mobile]`** (2 éléments) | `["",""]` | T |
| `inheritMaxWidth` | boolean | `true` = largeur du thème | `false` | T |

Effet : `.kb-row-layout-id… > .kt-row-column-wrap { max-width: 72rem; margin-left:auto; margin-right:auto }`. Le fond reste sur toute la largeur. Mesuré : conteneur de 1152 px centré à x = 64 px sur 1280 px. [T]

`inheritMaxWidth: true` produit `max-width: var(--global-content-width, 1290px)` et ajoute en plus `padding-left/right: var(--global-content-edge-padding)`. [T]

Le réglage « Content Max Width » de l'inspecteur propose `px`, `%` et `vw`. Un second réglage du même attribut, « Inner Content Width » (composant `JC` de `blocks-rowlayout.js`), propose en plus `rem` [C]. `rem` est donc une valeur prévue par l'éditeur. À l'ouverture dans l'éditeur, la valeur est conservée (aucune différence relevée), mais l'affichage des deux réglages n'a pas été contrôlé visuellement.

### 3.6 Espacements (padding et marge)

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `padding` | array | `[haut, droite, bas, gauche]` ; jetons ou nombres | `["sm","","sm",""]` | T |
| `tabletPadding` | array | idem, ≤ 1024 px | `["","","",""]` | T |
| `mobilePadding` | array | idem, ≤ 767 px | `["","","",""]` | T |
| `paddingUnit` | string | `px`, `em`, `rem`, `%`, `vh`, `vw` (une seule unité pour les 3 paliers) | `"px"` | T (`px`, `rem`) |
| `margin` | array | `[haut, droite, bas, gauche]` (l'interface ne gère que haut et bas) | `["","","",""]` | T |
| `tabletMargin` / `mobileMargin` | array | idem | `["","","",""]` | T |
| `marginUnit` | string | `px`, `em`, `rem`, `%`, `vh` | `"px"` | T (`px`) |

- Le padding va sur `.kt-row-column-wrap`, la marge sur l'élément extérieur. [T]
- Si `padding` est absent ou vaut le défaut `["sm","","sm",""]` (non enregistré), le haut et le bas valent `var(--global-kb-row-default-top, var(--global-kb-spacing-sm, 1.5rem))`, soit 24 px. [T]
- `"padding":["","","",""]` supprime vraiment le padding haut et bas (0 px). [T]
- Valeurs vides : le palier hérite du palier plus large, par cascade CSS. [T]

```json
"padding":[6,2,6,2], "tabletPadding":[4,1.5,4,1.5], "mobilePadding":[2.5,1,2.5,1], "paddingUnit":"rem",
"margin":[40,"",40,""], "tabletMargin":[24,"",24,""], "mobileMargin":[0,"",0,""], "marginUnit":"px"
```

Mesuré à 1280, 900 et 375 px : padding haut de 96, 64 et 40 px ; marge haute de 40, 24 et 0 px (`05-espacements`). [T]

### 3.7 Hauteur minimale

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `minHeight` | number | nombre ; `0` ou absent = aucune hauteur minimale | `0` | T |
| `minHeightTablet` / `minHeightMobile` | number | nombre | `""` | T |
| `minHeightUnit` | string | `px`, `vw`, `vh` dans l'interface (une seule unité pour tous les paliers) | `"px"` | T (`px`, `vh`) |

Mesuré : `"minHeight":60, "minHeightUnit":"vh"` donne 540 px dans une fenêtre de 900 px de haut. `400/300/200` px aux trois paliers sont respectés. [T]

### 3.8 Alignement vertical

| Attribut | Type | Valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `verticalAlignment` | string | `"top"`, `"middle"`, `"bottom"` | `"top"` | T (`middle`, `bottom`) |
| `columnsInnerHeight` | boolean | `true` = cartes de même hauteur (fond étiré) | `false` | T |

- `middle` produit `align-content:center` sur la grille et `justify-content:center` sur les colonnes. Le contenu est centré verticalement dans la `minHeight` et les colonnes sont centrées entre elles. [T]
- `bottom` aligne le bas des colonnes : mesuré, bas à 662 et 663 px pour des colonnes de 27 et 82 px de haut. [T]
- `columnsInnerHeight: true` : 4 cartes de 223 px malgré des textes de longueurs différentes. Ne s'applique pas quand les colonnes sont empilées (`row`). [T]

### 3.9 Fond : couleur, dégradé, image

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `bgColor` | string | couleur (§ 2.3) | `""` | T (`palette3`, `palette5`, `palette8`, hex, rgba) |
| `backgroundSettingTab` | string | `"normal"`, `"gradient"`, `"slider"`, `"video"` | `"normal"` | T (`normal`, `gradient`) |
| `gradient` | string | dégradé CSS complet ; `var(--global-paletteN)` est accepté | `""` | T |
| `bgImg` | string | URL de l'image | `""` | T (URL absolue) |
| `bgImgID` | number | ID dans la médiathèque (pour l'éditeur, inutile au CSS) | `""` | C |
| `bgImgSize` | string | `cover`, `contain`, `auto` | `"cover"` | T (`cover`) |
| `bgImgPosition` | string | position CSS, par exemple `"center top"` | `"center center"` | T |
| `bgImgAttachment` | string | `scroll`, `fixed`, `parallax` | `"scroll"` | T (`scroll`) |
| `bgImgRepeat` | string | `no-repeat`, `repeat`… | `"no-repeat"` | T |
| `tabletBackground` / `mobileBackground` | array | `[{"enable":true,"bgColor":"…","bgImg":"…","bgImgID":"","bgImgSize":"cover","bgImgPosition":"center center","bgImgAttachment":"scroll","bgImgRepeat":"no-repeat","forceOverDesk":false}]` | `enable:false` | T (`mobileBackground` + `bgColor`) |

- `backgroundSettingTab: "gradient"` : seul `gradient` est lu, **`bgColor` est ignoré** (le `switch` PHP). [C]
- `mobileBackground` activé produit, au mobile, `background: var(--global-palette1, …)` sur la rangée. Mesuré : `rgb(43,108,176)` à 375 px, palette3 au-delà. [T]

```json
"bgColor":"palette3"
"backgroundSettingTab":"gradient", "gradient":"linear-gradient(135deg, var(--global-palette3, #1A202C) 0%, #7a2e1d 100%)"
"bgImg":"https://…/image.jpg", "bgImgSize":"cover", "bgImgPosition":"center top", "bgImgAttachment":"scroll", "bgImgRepeat":"no-repeat"
```

Le `--` du dégradé est enregistré sous la forme `--`, ce qui est normal : le rendu est correct. [T]

### 3.10 Superposition (overlay)

La superposition est une `div.kt-row-layout-overlay` en position absolue, placée entre le fond et le contenu.

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `currentOverlayTab` | string | `"normal"` (couleur ou image), `"gradient"`, `"grad"` (ancien) | `"normal"` | T (`normal`, `gradient`) |
| `overlay` | string | couleur | `""` | T |
| `overlayOpacity` | number | **entier de 0 à 100** (70 donne `opacity:0.70`) | `30` | T |
| `overlayGradient` | string | dégradé CSS (si `currentOverlayTab` vaut `gradient`) | `""` | T |
| `overlayBlendMode` | string | `multiply`, `screen`… ou `none` | `"none"` | T (`multiply`) |
| `overlayBgImg` (+ `Size`, `Position`, `Attachment`, `Repeat`) | string | image de superposition | `""` | C |
| `overlayFirstOpacity` | number | opacité propre à la couleur, de 0 à 1 | `""` | C |
| `tabletOverlay` / `mobileOverlay` | array | `[{"enable":true,…}]` | | C |

- `overlayOpacity` doit être un **entier**. Le PHP (`render_opacity_from_100`) fabrique une chaîne de caractères : `"0.0" + valeur` sous 10 (5 donne `0.05`), `"0." + valeur` de 10 à 99, et `1` à partir de 100. Une valeur décimale comme `0.5` donnerait `0.00.5`, un CSS invalide. [C]
- Si `overlay` est renseigné sans `overlayOpacity`, la feuille de base applique 0,3. [C]

```json
"bgImg":"https://…/image.jpg", "overlay":"#000000", "overlayOpacity":70
"bgColor":"#2b6cb0", "currentOverlayTab":"gradient", "overlayGradient":"linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.9) 100%)", "overlayOpacity":100, "overlayBlendMode":"multiply"
```

Mesuré : `opacity 0.7`, fond noir ; puis `opacity 1`, dégradé, `mix-blend-mode multiply` (`03-fonds`). [T]

### 3.11 Bordures, rayon, ombre

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `borderStyle` | array | `[{"top":[couleur, style, épaisseur], "right":[…], "bottom":[…], "left":[…], "unit":"px"}]`. Style : `solid`, `dashed`, `dotted`… Un côté vide vaut `["","",""]` | côtés vides | T |
| `tabletBorderStyle` / `mobileBorderStyle` | array | même format | | C |
| `borderRadius` | array | `[haut-gauche, haut-droite, bas-droite, bas-gauche]` | `["","","",""]` | T |
| `tabletBorderRadius` / `mobileBorderRadius` | array | idem | | C |
| `borderRadiusUnit` | string | `px`, `%`… | `"px"` | T |
| `borderRadiusOverflow` | boolean | `true` ajoute `overflow:clip` quand un rayon est défini | `true` | T |
| `displayBoxShadow` | boolean | active l'ombre | `false` | T |
| `boxShadow` | array | `[{"color":"#000000","opacity":0.5,"spread":0,"blur":30,"hOffset":0,"vOffset":10,"inset":false}]`, en px, opacité de 0 à 1 | opacité 0.2, flou 14 | T |
| `border`, `borderWidth`, `tabletBorder`… | | **anciens attributs** : s'ils sont renseignés, ils remplacent `borderStyle` | | C |

```json
"borderStyle":[{"top":["#c9a227","solid",4],"right":["","",""],"bottom":["#c9a227","dashed",2],"left":["","",""],"unit":"px"}],
"borderRadius":[16,16,16,16], "borderRadiusUnit":"px",
"displayBoxShadow":true, "boxShadow":[{"color":"#000000","opacity":0.5,"spread":0,"blur":30,"hOffset":0,"vOffset":10,"inset":false}]
```

CSS constaté : `border-top:4px solid #c9a227; border-bottom:2px dashed #c9a227; border-*-radius:16px; overflow:clip; box-shadow:0px 10px 30px 0px rgba(0, 0, 0, 0.5)`. [T]

### 3.12 Couleurs du texte et des liens

| Attribut | Type | Effet | Vérif. |
|---|---|---|---|
| `textColor` | string | `color` sur la rangée et ses `h1`–`h6` | T |
| `linkColor` | string | `.kb-row-layout-id… a` | T |
| `linkHoverColor` | string | `… a:hover` | T |

### 3.13 Masquer selon l'appareil

| Attribut | Type | Effet | Vérif. |
|---|---|---|---|
| `vsdesk` | boolean | masque la rangée au-delà de 1025 px | C |
| `vstablet` | boolean | masque entre 768 et 1024 px (classe `kb-v-md-hidden`) | T |
| `vsmobile` | boolean | masque à 767 px et moins | C (testé sur une colonne) |

---

## 4. `kadence/column` : référence des attributs

Les unités ne portent **pas le même nom** que sur la rangée : `paddingType` et `marginType` (et non `paddingUnit`/`marginUnit`).

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `uniqueID` | string | voir § 0 | `""` | classe `kadence-column{ID}` ; **obligatoire** pour le CSS | T |
| `kbVersion` | number | `2` | `""` | ce que met l'éditeur | T |
| `borderWidth` | array | **`["","","",""]` obligatoire** (§ 0, règle 4) | `[0,0,0,0]` | | T |
| `htmlTag` | string | l'interface propose `div`, `header`, `section`, `article`, `main`, `aside`, `footer` | `"div"` | balise de la colonne | T (`article`) |
| `anchor` | string | identifiant HTML | | `id="…"` | T |
| `className` | string | classes | | ajoutées à la colonne | T |
| `padding` / `tabletPadding` / `mobilePadding` | array | `[h, d, b, g]`, jetons ou nombres | `["","","",""]` | sur `.kt-inside-inner-col` | T |
| `paddingType` | string | unité | `"px"` | | T |
| `margin` / `tabletMargin` / `mobileMargin` | array | `[h, d, b, g]` | `["","","",""]` | sur la colonne | T |
| `marginType` | string | unité | `"px"` | | T |
| `background` | string | couleur | `""` | `background-color` | T |
| `backgroundOpacity` | number | de 0 à 1, valable seulement pour une couleur hex (ignoré pour `paletteN`) | `1` | `#ffffff` à 0.5 donne `rgba(255,255,255,0.5)` | T (hex), C (palette) |
| `backgroundType` | string | `"normal"` ou `"gradient"` | `"normal"` | | T |
| `gradient` | string | dégradé CSS | `""` | `background-image` | T |
| `backgroundImg` | array | `[{"bgImg":"URL","bgImgID":"","bgImgSize":"cover","bgImgPosition":"center center","bgImgAttachment":"scroll","bgImgRepeat":"no-repeat"}]` | vide | | T |
| `overlay` | string | couleur de superposition (pseudo-élément `::before`) | `""` | | T |
| `overlayOpacity` | number | **de 0 à 1** (et non de 0 à 100 comme pour la rangée) | `0.3` | | T |
| `overlayType`, `overlayGradient`, `overlayImg`, `overlayBlendMode` | | variantes | | | C |
| `borderStyle` | array | même format que la rangée | | | T |
| `borderRadius` | array | `[hg, hd, bd, bg]` | `[0,0,0,0]` | | T |
| `borderRadiusUnit` | string | | `"px"` | | T |
| `displayShadow` | boolean | active l'ombre (le nom diffère de la rangée) | `false` | | T |
| `shadow` | array | même format que `boxShadow` | | | T |
| `textAlign` | array | `[bureau, tablette, mobile]` : `left`, `center`, `right` ; `""` = hérite | `["","",""]` | | T |
| `textColor` / `linkColor` / `linkHoverColor` | string | couleurs | `""` | | T |
| `verticalAlignment` | string | `top`, `middle`, `bottom` (alignement de la colonne dans la ligne et de son contenu) | (aucun) | | T (`middle`) |
| `verticalAlignmentTablet` / `verticalAlignmentMobile` | string | idem par palier | | | C |
| `maxWidth` | array | `[bureau, tablette, mobile]` ; colonne centrée par `margin:auto` | `["","",""]` | | T |
| `maxWidthUnit` | string | unité du bureau ; `maxWidthTabletUnit` et `maxWidthMobileUnit` héritent | `"px"` | | T |
| `height` | array | `[bureau, tablette, mobile]`, produit un `min-height` sur `.kt-inside-inner-col` | `["","",""]` | | T |
| `heightUnit` | string | | `"px"` | | T |
| `collapseOrder` | number | ordre CSS quand la rangée est `row`, `two-grid` ou `three-grid` au palier concerné ; en tablette, seulement si `tabletLayout` est explicite | (aucun) | | T (mobile) |
| `vsdesk` / `vstablet` / `vsmobile` | boolean | masque la colonne (classe `kvs-sm-false`…) | `false` | | T (`vsmobile`) |
| `id` | number | ancien index, inutile | `1` | | C |

La colonne propose aussi un mode flex interne : `direction`, `justifyContent`, `wrapContent`, `gutter`, `rowGap`, `flexBasis`. Il n'a pas été testé (hors sujet).

Exemple de colonne en carte (testé dans `05-espacements` et `modeles`) :

```json
{"name":"kadence/column","attributes":{
  "uniqueID":"pd-x-carte1","kbVersion":2,"htmlTag":"article",
  "background":"palette4","padding":["md","md","md","md"],
  "borderWidth":["","","",""],
  "borderStyle":[{"top":["palette6","solid",1],"right":["palette6","solid",1],"bottom":["palette6","solid",1],"left":["palette6","solid",1],"unit":"px"}],
  "borderRadius":[8,8,8,8],"borderRadiusUnit":"px",
  "displayShadow":true,"shadow":[{"color":"#000000","opacity":0.35,"spread":0,"blur":24,"hOffset":0,"vOffset":8,"inset":false}]},
 "innerBlocks":[ … ]}
```

Exemple de colonne avec image et superposition (testé dans `06-divers`) :

```json
"backgroundImg":[{"bgImg":"https://…/image.jpg","bgImgID":"","bgImgSize":"cover","bgImgPosition":"center center","bgImgAttachment":"scroll","bgImgRepeat":"no-repeat"}],
"overlay":"#000000","overlayOpacity":0.6
```

---

## 5. Modèles complets (testés tels quels)

Les trois modèles ci-dessous ont été construits dans la page `ref-mise-en-page-modeles` (méta pleine largeur, § 0 règle 8), sans bloc invalide ni erreur JS ni débordement horizontal à 1280, 900 et 375 px. Les mesures sont indiquées sous chaque modèle.

Ce sont des **éléments de `blocs`**. Une spec complète a la forme :

```json
{"titre":"…","slug":"…",
 "meta":{"_kad_post_layout":"fullwidth","_kad_post_content_style":"unboxed","_kad_post_vertical_padding":"hide","_kad_post_title":"hide"},
 "blocs":[ MODÈLE_1, MODÈLE_2, MODÈLE_3 ]}
```

Avant réutilisation, renommer les `uniqueID` (uniques dans la page, avec des tirets).

### 5.1 Section pleine largeur, fond sombre, contenu centré limité à 72rem

```json
{"name":"kadence/rowlayout","attributes":{
  "uniqueID":"mep-m1","kbVersion":2,
  "columns":1,"colLayout":"equal",
  "align":"full","htmlTag":"section","anchor":"presentation","className":"pd-section-sombre",
  "bgColor":"palette3","textColor":"palette9",
  "maxWidth":72,"maxWidthUnit":"rem",
  "padding":["xl","md","xl","md"],"mobilePadding":["lg","sm","lg","sm"]
 },
 "innerBlocks":[
  {"name":"kadence/column","attributes":{"uniqueID":"mep-m1-c1","kbVersion":2,"borderWidth":["","","",""],"textAlign":["center","",""]},
   "innerBlocks":[
    {"name":"core/heading","attributes":{"level":2,"content":"Section sombre pleine largeur"}},
    {"name":"core/paragraph","attributes":{"content":"Fond palette3 sur toute la largeur, contenu centré et limité à 72rem."}}
   ]}
 ]}
```

Mesures :
- `<section id="presentation">` de 1280 px de large, fond `rgb(26,32,44)` ;
- conteneur interne `max-width:1152px` centré (x = 64 px) ;
- padding de 64 px en haut et 32 px sur les côtés ; au mobile, 48 px et 24 px ;
- texte centré à tous les paliers ;
- le lien `#presentation` cible la section.

### 5.2 Deux colonnes 1fr / 1.5fr, empilées au mobile

```json
{"name":"kadence/rowlayout","attributes":{
  "uniqueID":"mep-m2","kbVersion":2,
  "columns":2,"colLayout":"equal",
  "firstColumnWidth":40,"secondColumnWidth":60,
  "mobileLayout":"row",
  "columnGutter":"wider","verticalAlignment":"middle",
  "align":"full","maxWidth":72,"maxWidthUnit":"rem",
  "padding":["xl","md","xl","md"],
  "textColor":"palette9"
 },
 "innerBlocks":[
  {"name":"kadence/column","attributes":{"uniqueID":"mep-m2-c1","kbVersion":2,"borderWidth":["","","",""]},
   "innerBlocks":[{"name":"core/heading","attributes":{"level":2,"content":"Colonne étroite (1fr)"}}]},
  {"name":"kadence/column","attributes":{"uniqueID":"mep-m2-c2","kbVersion":2,"borderWidth":["","","",""]},
   "innerBlocks":[{"name":"core/paragraph","attributes":{"content":"Colonne large (1.5fr). Sur mobile (≤ 767 px) les deux colonnes s'empilent, la colonne étroite au-dessus."}}]}
 ]}
```

Mesures :

| Largeur d'écran | Colonnes | Gouttière |
|---|---|---|
| 1280 px | 403 / 621 px | 64 px |
| 900 px (tablette, proportions conservées) | 302 / 470 px | 64 px |
| 375 px | 311 px, colonne étroite au-dessus | |

- `"mobileLayout":"row"` est la valeur par défaut, donc non enregistrée ; on la garde dans la spec pour la lisibilité.
- Pour mettre la colonne large au-dessus au mobile, ajouter `"collapseOrder":"right-to-left"`.

### 5.3 Grille de 4 cartes : 4 puis 2 puis 1 colonne

```json
{"name":"kadence/rowlayout","attributes":{
  "uniqueID":"mep-m3","kbVersion":2,
  "columns":4,"colLayout":"equal","tabletLayout":"two-grid","mobileLayout":"row",
  "columnGutter":"custom","tabletGutter":"custom","mobileGutter":"custom","customGutter":[32,24,16],"gutterType":"px",
  "collapseGutter":"custom","tabletRowGutter":"custom","mobileRowGutter":"custom","customRowGutter":[32,24,16],"rowGutterType":"px",
  "columnsInnerHeight":true,
  "align":"full","maxWidth":72,"maxWidthUnit":"rem",
  "padding":["xl","md","xl","md"],
  "textColor":"palette9"
 },
 "innerBlocks":[
  {"name":"kadence/column","attributes":{
    "uniqueID":"mep-m3-c1","kbVersion":2,"htmlTag":"article",
    "background":"palette4","padding":["md","md","md","md"],
    "borderWidth":["","","",""],
    "borderStyle":[{"top":["palette6","solid",1],"right":["palette6","solid",1],"bottom":["palette6","solid",1],"left":["palette6","solid",1],"unit":"px"}],
    "borderRadius":[8,8,8,8],"borderRadiusUnit":"px",
    "displayShadow":true,"shadow":[{"color":"#000000","opacity":0.35,"spread":0,"blur":24,"hOffset":0,"vOffset":8,"inset":false}]},
   "innerBlocks":[
    {"name":"core/heading","attributes":{"level":3,"content":"Carte 1"}},
    {"name":"core/paragraph","attributes":{"content":"Texte de la carte 1."}}
   ]},
  "… mep-m3-c2, mep-m3-c3, mep-m3-c4 : mêmes attributs, seul uniqueID change …"
 ]}
```

La chaîne `"… mep-m3-c2 …"` n'est pas un bloc : l'outil échouerait sur cet élément. Il faut la remplacer par trois copies de l'objet colonne, en changeant seulement `uniqueID` (`mep-m3-c2`, `-c3`, `-c4`) et le contenu. La spec testée telle quelle avait 4 objets colonne complets.

Mesures :

| Largeur d'écran | Grille | Gouttière |
|---|---|---|
| 1280 px | 4 × 248 px, cartes toutes de 223 px de haut | 32 px |
| 900 px | 2 × 406 px | 24 px dans les deux sens |
| 375 px | 1 × 311 px | 16 px |

Bordure de 1 px `palette6`, rayon de 8 px et ombre présents à tous les paliers.

---

## 6. Pièges constatés (résumé)

| # | Piège | Conséquence | Parade |
|---|---|---|---|
| 1 | Pas de `uniqueID` ou de `kbVersion:2` sur la rangée | aucun conteneur ni CSS en rendu public | toujours les deux (§ 0) |
| 2 | `borderWidth` absent sur une colonne | les épaisseurs de `borderStyle` sont effacées par l'éditeur | `"borderWidth":["","","",""]` |
| 3 | `uniqueID` de la forme `a_b` | régénéré à l'ouverture dans l'éditeur | des tirets seulement |
| 4 | Reconstruction d'une page existante | les `uniqueID` peuvent être régénérés (`<idPage>_<hash>`), de façon imprévisible | styler via `className` ou `anchor` |
| 5 | Anciens attributs (`topMargin`…) | migrés par l'éditeur, ils écrasent `margin`/`padding` | uniquement les tableaux |
| 6 | `customGutter` sans `tabletGutter`/`mobileGutter: "custom"` | la valeur du bureau s'applique partout | mettre `"custom"` à chaque palier |
| 7 | Rangée sans fond ni `align:"full"` | contenu collé aux bords de l'écran | `align:"full"` ou `padding[1]`/`[3]` |
| 8 | `overlayOpacity` de la rangée en 0–1, ou de la colonne en 0–100 | opacité fausse, voire CSS invalide | rangée : entier de 0 à 100 ; colonne : de 0 à 1 |
| 9 | `paddingUnit` sur une colonne | ignoré | la colonne utilise `paddingType` et `marginType` |
| 10 | `responsiveMaxWidth` à 3 valeurs | seules `[tablette, mobile]` sont lues | 2 éléments |
| 11 | Titres sombres sur fond sombre | `h1`–`h6` en palette3 | `textColor` sur la rangée |
| 12 | `htmlTag` hors liste (`nav`…) | rendu en `div` | utiliser la liste du § 3.1 ; éviter `main` (le thème a déjà un `<main>`) |
| 13 | Proportions 1fr / 1,5fr | ce sont des pourcentages moins la gouttière : rapport 0,649 au lieu de 0,667 avec 64 px | accepter l'écart ou ajouter du CSS via `className` |
| 14 | `colLayout` absent sur une rangée | rendu public correct, mais l'éditeur affiche « Select Your Layout » à la place des colonnes ; colonnes non montées (pas d'ID automatique, pas de migration) | toujours `"colLayout":"equal"` ou une autre disposition (§ 0, règle 10) |

---

## 7. Ce qui n'a PAS été vérifié par un essai

Les points suivants sont lus dans le code seulement, ou pas du tout :
- `bgImgAttachment: "fixed"` et `"parallax"` (script jarallax), images de superposition `overlayBgImg`, `overlayFirstOpacity`/`overlaySecondOpacity`, ancien mode `currentOverlayTab: "grad"` ;
- `tabletBackground` (seul `mobileBackground` + couleur a été testé), `forceOverDesk`, `tabletOverlay`/`mobileOverlay`, `backgroundSettingTab: "slider"` et `"video"` ;
- les dispositions `left-golden`, `left-half`, `right-half`, `center-wide`, `center-exwide`, `first-row`, `last-row`, `left-forty`, `right-forty` et les dispositions à 5 et 6 colonnes (seules `equal`, `right-golden`, `center-half`, `two-grid`, `three-grid` et `row` ont été mesurées) ;
- les largeurs personnalisées par palier (`firstColumnWidthTablet`, `…Mobile`) et les largeurs personnalisées à 3 colonnes ou plus ;
- `tabletBorderStyle`/`mobileBorderStyle`, les rayons par palier, l'état « survol » des colonnes (`borderHover*`, `shadowHover`, `backgroundHover`, `overlayHover`…) ;
- `vsdesk` et `vsmobile` sur la rangée (`vstablet` sur la rangée et `vsmobile` sur la colonne ont été testés), `zIndex`, `breakoutLeft`/`breakoutRight`, séparateurs `topSep`/`bottomSep`, `align: "center"` ;
- les jetons d'espacement `xxs`, `xs`, `xxl`, `5xl`, `ss-auto` et les jetons de gouttière `default`, `narrow`, `wide`, `widest`, `xs`/`sm`/`md`/`lg` (le CSS produit vient du code ; seuls `none`, `skinny`, `wider` et `custom` ont été mesurés) ;
- les couleurs `palette10` à `palette15` ;
- les unités `em`, `%`, `vh`, `vw` pour le padding et les marges (seuls `px` et `rem` ont été testés), `em`/`rem` pour les gouttières ;
- les URL d'image relatives (seule une URL absolue a été testée) ;
- `collapseOrder` d'une colonne en tablette ;
- le comportement de l'éditeur quand une rangée a moins de colonnes enfants que `columns` : le code laisse penser que l'éditeur en ajoute à l'ouverture ;
- l'affichage dans l'inspecteur de l'éditeur des valeurs hors interface (`maxWidthUnit: "rem"`, gouttières `custom`). Réouvertes dans l'éditeur, les pages `03`, `05`, `06` et `modeles` ne montrent **aucune modification d'attribut**, mais le rendu visuel de l'éditeur n'a pas été contrôlé.

---

## 8. Pages d'essai (WordPress de test, `http://127.0.0.1:8080/`)

| Page | Ce qu'elle montre |
|---|---|
| `ref-mise-en-page-01-minimal` | rangée sans `uniqueID` ni `kbVersion` : aucun conteneur en rendu public |
| `ref-mise-en-page-02-ids` | `uniqueID` personnalisés (`x_y` régénéré à l'ouverture dans l'éditeur) |
| `ref-mise-en-page-03-fonds` | 72 rem, palette, dégradé, image et superposition, superposition en dégradé, bordures et ombre, `anchor`, `className`, `section`, `minHeight` en vh |
| `ref-mise-en-page-04-colonnes` | 40/60, `right-golden` + ordre inversé, 4 cartes, alignement bas, gouttières ; bordure de carte perdue sans `borderWidth` |
| `ref-mise-en-page-05-espacements` | padding et marges responsive, `responsiveMaxWidth`, `minHeight` par palier, gouttières `custom` par palier, colonnes : `maxWidth`, `height`, `textAlign`, `vsmobile` |
| `ref-mise-en-page-06-divers` | 6 cartes dans 4 colonnes, `collapseOrder` de colonne, `htmlTag` invalide, `vstablet`, image et superposition de colonne, dégradé de colonne, `mobileBackground`, `align: "wide"` |
| `ref-mise-en-page-07-sans-meta` | page sans méta Kadence : décalage au mobile |
| `ref-mise-en-page-modeles` | les 3 modèles du § 5, plus `mobileLayout: "equal"` et la migration `topMargin` (IDs régénérés lors de la 2e construction) |
| `ref-mise-en-page-09-bords` | padding latéral automatique (`align: "full"`, fond) et fond en rgba |

Pour revérifier un attribut :
1. `node outils/wp-test/editeur.js construire spec.json`
2. `php outils/wp-test/lire.php <wp> <slug>`, pour lire les attributs réellement enregistrés ;
3. `curl -s http://127.0.0.1:8080/<slug>/ | sed 's/}/}\n/g' | grep kb-row-layout-id`, pour lire le CSS généré, qui est inséré dans `<head>`.

---

## 9. Contre-vérification (7 octobre 2026)

Relecture critique de la fiche : chaque affirmation importante a été recoupée avec le code source de Kadence Blocks 3.7.12.1, puis les specs d'exemple ont été rejouées avec l'outil dans des pages neuves. Fichiers de travail : `scratchpad/ref/mise-en-page-verif/` (`v1` à `v5` pour les specs, `mesurer.js` et `m-*.js` pour les mesures, `etat-editeur*.js` et `placeholder.js` pour lire l'état de l'éditeur sans enregistrer).

### 9.1 Specs rejouées

Les pages ont été construites avec `editeur.js construire`, relues avec `lire.php`, mesurées avec `getComputedStyle` à 1280, 900 et 375 px, puis capturées avec `editeur.js capture`. Résultat commun aux pages `verif-m1`, `verif-m2` et `verif-m3` : aucun bloc invalide, aucune erreur JS, aucun débordement horizontal.

| Page | Spec rejouée | Résultat |
|---|---|---|
| `ref-mise-en-page-verif-m1` | modèle § 5.1 (IDs renommés en `vrf-…`) | **Conforme.** `<section id="presentation">` de 1280 px, fond `rgb(26,32,44)`. Conteneur de 1152 px à x = 64. Padding 64 / 32 px, et 48 / 24 px à 375 px. Texte centré aux 3 paliers, titres blancs. Classes : `kb-row-layout-wrap kb-row-layout-idvrf-m1 alignfull kt-row-has-bg pd-section-sombre wp-block-kadence-rowlayout`. |
| `ref-mise-en-page-verif-m2` | modèle § 5.2 | **Conforme.** 403,2 / 620,8 px à 1280 px, 302,4 / 469,6 px à 900 px, gouttière de 64 px. Empilé à 375 px (311 px), colonne étroite au-dessus. `columns` et `mobileLayout` ne sont pas enregistrés (valeurs par défaut). |
| `ref-mise-en-page-verif-m3` | modèle § 5.3, avec 4 objets colonne complets (textes de longueurs différentes) | **Conforme.** 4 × 248 px, cartes toutes de 223 px de haut, gouttière de 32 px. Puis 2 × 406 px avec 24 / 24 px, et 1 × 311 px avec 16 px. Bordure 1 px `rgb(113,128,150)`, rayon de 8 px, ombre `rgba(0,0,0,0.35) 0 8px 24px` et balise `article` présents. |
| `ref-mise-en-page-verif-fragments` | extraits des § 3.6, 3.10, 3.11 et § 4, plus les pièges 2, 5, 6, 12 et la règle 1 | **Conforme pour le rendu public.** Bordures 4 px solid / 2 px dashed, rayon de 16 px, `overflow: clip`, ombre `rgba(0,0,0,0.5) 0 10px 30px`. Superposition à 0,7 et `center top`. Superposition en dégradé à opacité 1 en `multiply`. Padding 96 / 64 / 40 px et marges 40 / 24 / 0 px. `nav` rendu en `div`. `topMargin: 10` enregistré `margin:[10,"","",""]` (marge basse perdue). `right-golden` à 416 / 832 px, ordre inversé à 900 et 375 px. Superposition de colonne `::before` à 0,6 avec `min-height` de 200 px. `customGutter` sans `"custom"` aux autres paliers : 32 px à 375 px. Rangée sans ID : aucun conteneur. **Mais** les 11 rangées sans `colLayout` affichent « Select Your Layout » dans l'éditeur (nouvelle règle 10). |
| `ref-mise-en-page-verif-collayout` | piège 2 et règle 1, avec `colLayout` | Colonne sans `borderWidth` : épaisseur effacée à l'enregistrement (0 px) ; avec `["","","",""]` : 1 px conservé. Rangée sans `kbVersion` : l'éditeur ajoute les `uniqueID` mais pas `kbVersion` à la rangée, donc aucun conteneur. |
| `verif-m1` et `verif-m3` reconstruites | même spec, deuxième passage | `uniqueID` **conservés**, alors que la règle 3 annonçait une régénération systématique. |

### 9.2 Corrections apportées à la fiche

1. **Ajout de la règle 10 (§ 0) et du piège 14 (§ 6) : `colLayout` est obligatoire dans une spec.** Sans lui, l'éditeur remplace les colonnes par le sélecteur de disposition. Le tableau du § 3.2 disait « absent = `equal` », ce qui n'est vrai que pour le rendu PHP.
2. **Règle 3** : « tous les `uniqueID` sont régénérés » devient « **peuvent** être régénérés ». Le phénomène est réel (page `modeles`) mais pas systématique (non reproduit deux fois). La règle d'usage (styler par `className` ou `anchor`) est inchangée.
3. **Règles 1 et 4** : ajout de l'explication vérifiée. Les migrations et l'ajout automatique d'ID n'ont lieu que pour les blocs affichés dans l'éditeur. `kbVersion` de la rangée n'est jamais enregistré automatiquement. Les deux règles restent valables.
4. **§ 3.5** : `rem` est bien proposé par l'un des deux réglages de largeur maximale de l'éditeur (« Inner Content Width »). La fiche disait qu'aucun ne le proposait.
5. **§ 2.2** : `narrow`, `wide` et `widest` sur `columnGutter` sont convertis par l'éditeur en `"custom"` avec 20, 40 ou 80.
6. **§ 3.10** : formule exacte de `overlayOpacity` (`0.0`+v sous 10, `0.`+v jusqu'à 99, `1` au-delà).
7. **§ 3.3** : la mesure `mobileLayout: "equal"` est remise dans son contexte (139,5 px avec 32 px de padding latéral, 171,5 px sans).

### 9.3 Affirmations recoupées dans le code et confirmées

- Valeurs par défaut des deux `block.json` : `columns` 2, `mobileLayout` `row`, `tabletLayout` `inherit`, `collapseGutter`/`columnGutter` `default`, `padding` `["sm","","sm",""]`, `overlayOpacity` 30 (rangée) et 0.3 (colonne), `borderWidth` `[0,0,0,0]` (colonne), `borderRadiusOverflow` `true`, `responsiveMaxWidth` à 2 éléments, unités `paddingType`/`marginType` sur la colonne.
- Les jetons d'espacement et de gouttière du § 2 correspondent exactement à `class-kadence-blocks-css.php`.
- Seuils CSS : 767 px, 1024 px et 1025 px.
- Balises `htmlTag` autorisées pour la rangée : `div`, `header`, `section`, `article`, `main`, `aside`, `footer`.
- `get_custom_layout` : la dernière colonne vaut 100 − la somme des autres.
- `collapseOrder` de la rangée et de la colonne ; 5 et 6 colonnes sans `tabletLayout` prennent la disposition mobile en tablette.
- Le CSS est produit dans `<head>` à partir des attributs bruts enregistrés (`output_head_data`, sans fusion des valeurs par défaut pour `rowlayout` et `column`).
- Clés de méta `_kad_post_*` lues par le thème et posées par `outils/construire.py`.
- Palette et fond sombre du site (`--global-palette1` = `#2B6CB0`…, fond `rgb(13,18,23)`).

### 9.4 Toujours non vérifié

En plus de la liste du § 7 :
- l'emplacement exact du réglage « Inner Content Width » dans l'interface (lu dans le code seulement) ;
- ce que fait l'éditeur quand on choisit une disposition dans le sélecteur d'une rangée sans `colLayout`, alors qu'elle a déjà des colonnes.
