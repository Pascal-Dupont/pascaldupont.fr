# Kadence : boutons, onglets, accordéon et ancres

Blocs couverts : `kadence/advancedbtn` + `kadence/singlebtn` (boutons), `kadence/tabs` + `kadence/tab` (onglets), `kadence/accordion` + `kadence/pane` (accordéon), ancres et liens internes.

Fiche de référence pour générer des specs JSON (outil `outils/wp-test/editeur.js construire`).
Environnement vérifié : WordPress 7.1.3 (fr_FR), thème Kadence 1.5.2 + thème enfant `kadence-pascal`, Kadence Blocks **3.7.12.1** (gratuit).
À lire avec `mise-en-page.md` (rangées `kadence/rowlayout` et colonnes `kadence/column`, utilisées ici pour les grilles de cartes).

Noms dans l'interface (en anglais, pas de traduction française de Kadence Blocks) :
- `kadence/advancedbtn` = « Buttons (Adv) » : le **groupe** (conteneur flex) ;
- `kadence/singlebtn` = « Single Button » : un bouton, uniquement à l'intérieur d'un groupe ;
- `kadence/tabs` = « Tabs », `kadence/tab` = « Tab » (un panneau) ;
- `kadence/accordion` = « Accordion », `kadence/pane` = « Pane » (un volet).

Légende de la colonne « Vérif. » :
- **T** : testé en réel avec l'outil (page `ref-boutons-onglets-navigation-*`, contenu enregistré relu avec `lire.php`, CSS généré lu dans `<style id="kadence_blocks_css-inline-css">`, styles calculés mesurés avec `getComputedStyle` à 1280, 900 et 375 px, survol simulé, clics et ancres simulés) ;
- **C** : lu dans le code seulement (`dist/blocks/*/block.json`, `includes/blocks/class-kadence-blocks-{advancedbtn,singlebtn,tabs,accordion}-block.php`, `includes/class-kadence-blocks-css.php`, `dist/blocks-*.js`, `dist/style-blocks-*.css`, `includes/assets/js/kt-tabs.min.js`).

Points de rupture du CSS généré : **tablette ≤ 1024 px**, **mobile ≤ 767 px** (les règles mobiles s'ajoutent aux règles tablette).
Le CSS propre à chaque bloc est écrit dans `<head>`, dans `<style id="kadence_blocks_css-inline-css">`, **après** les feuilles de base `style-blocks-*.css` : à spécificité égale, il l'emporte. [T]

---

## 0. Règles à respecter dans toute spec

1. **`uniqueID` sur chaque bloc** : `kadence/advancedbtn`, `kadence/singlebtn`, `kadence/tabs`, `kadence/tab`, `kadence/accordion`, `kadence/pane`. [T]
   - Un `kadence/singlebtn` sans `uniqueID` **ne produit rien du tout** en public : le bouton est rendu par PHP seulement si `uniqueID` est non vide (`render_css`). Constaté sur `00-ids` : `<div class="wp-block-kadence-advancedbtn kb-buttons-wrap"></div>`, vide.
   - Un `kadence/tabs` sans `uniqueID` s'affiche, mais avec la classe `kt-tabs-idnotset` et **sans aucun CSS** propre (couleurs, bordures, espacements ignorés).
   - L'outil n'ajoute pas les `uniqueID` : à l'enregistrement de `00-ids`, les blocs sans ID sont restés sans ID. L'éditeur ne les crée en général qu'à la réouverture suivante (`55_9a4fc5-6e`…), sans les enregistrer. **Ce n'est pas systématique** (contre-vérification) : sur `verif-pieges`, un `kadence/singlebtn` sans ID a reçu `163_6eed5b-60` dès le premier enregistrement et s'est affiché, alors que sur `verif-ids` les deux boutons sans ID sont restés sans ID et absents. Le comportement est aléatoire : il ne faut jamais compter dessus.
   - `kadence/tabs`, `kadence/tab`, `kadence/advancedbtn` et `kadence/singlebtn` **n'ont pas** d'attribut `kbVersion` (contrairement à `rowlayout` et `column`). [C]
2. **Format de `uniqueID`** : `[A-Za-z0-9_-]`, unique dans la page, avec des tirets (`pd-films-onglets`, `pd-hero-btn-films`). Éviter la forme `a_b` (voir `mise-en-page.md`, règle 2).
3. **Ne jamais cibler un `uniqueID` dans du CSS ou du JS maison.** Quand l'outil reconstruit une page **existante**, les `uniqueID` sont *parfois* tous régénérés au format `<idPage>_<hash>` : constaté une fois sur trois reconstructions (`06-modeles`, 2e construction : `mo-actions` → `79_e5beaa-a5`), pas sur `01-boutons` ni `04-ancres`. Une page **neuve** garde les ID de la spec (vérifié : 179 ID identiques sur `06-modeles`). Pour styler ou lier, utiliser `className`, `anchor` ou les ancres d'onglet. [T]
4. **Types stricts, conformes au block.json.** Une valeur du mauvais type est enregistrée telle quelle dans le commentaire du bloc, puis rejetée par l'éditeur à la relecture : le bloc devient **invalide**. Constaté sur `09-types` avec `"startTab":"2"` (chaîne au lieu d'un nombre) et `"id":"2"` sur un `kadence/tab`. Attention aux cas contre-intuitifs : sur `kadence/tabs`, `size`, `tabSize` et `mobileSize` sont des **chaînes** (`"0.85"`), alors que `lineHeight` est un **nombre**. [T]
5. **Les valeurs égales au défaut ne sont pas enregistrées** (`tabCount: 3`, `layout: "tabs"`, `target: "_self"`, `borderRadiusUnit: "px"`…). Le PHP génère le CSS à partir des attributs **enregistrés** : un attribut absent = aucune règle, c'est la feuille de base qui s'applique. [T]
6. **Un `kadence/singlebtn` doit toujours être dans un `kadence/advancedbtn`.** Hors groupe, il s'affiche, mais **ses styles principaux ne s'appliquent pas** : les sélecteurs des couleurs, fonds, bordures, rayons, typographie, espacements, largeur et survol commencent tous par `.wp-block-kadence-advancedbtn` (seuls les sélecteurs de l'icône et de `onlyIcon` font exception, en `.kb-btn{ID}.kb-button …`). [C pour l'exception] Constaté sur `05-pieges` : fond `#a3302f` demandé, fond bleu Kadence affiché. [T]
7. **Pas de groupe de boutons vide** : l'éditeur supprime un `kadence/advancedbtn` sans enfant à l'enregistrement. Constaté sur `06-modeles`, carte d'un film sans lien. [T]
8. **Onglets : `tabCount` = nombre d'éléments de `titles` = nombre de `kadence/tab` enfants, et chaque `kadence/tab` a son `id` (1, 2, 3…).** Voir le § 2.3 : en cas d'écart, il y a **perte de contenu** ou des onglets qui disparaissent. [T]
9. **Aucune police Google** : dans tout objet `typography`, mettre `"google": false` et `"loadGoogle": false`. Laisser `"family": ""` pour hériter de la police du site (Hanken Grotesk, définie par le thème enfant). [T]
10. **Couleurs acceptées** dans tous les champs couleur testés : `"#rrggbb"`, `"paletteN"` (donne `var(--global-paletteN, …)`), `"transparent"`, et `"var(--nom)"`. Les variables du thème enfant (`--beret`, `--ivoire`, `--nuit`…) sont définies dans `pd.css`, chargé sur toutes les pages : `"background":"var(--beret)"` donne bien `rgb(163,48,47)`. [T] Les specs de cette fiche utilisent les valeurs hexadécimales, comme demandé.
11. **Méta de page** : comme dans `mise-en-page.md`, garder `"meta":{"_kad_post_layout":"fullwidth","_kad_post_content_style":"unboxed","_kad_post_vertical_padding":"hide","_kad_post_title":"hide"}`. Toutes les pages d'essai les avaient.

---

## 1. Boutons : `kadence/advancedbtn` (groupe) + `kadence/singlebtn` (bouton)

### 1.1 HTML produit (rendu public) [T]

```html
<div class="wp-block-kadence-advancedbtn kb-buttons-wrap kb-btns{uniqueID groupe} {className}" id="{anchor}">
  <a class="kb-button kt-button button kb-btn{uniqueID bouton} kt-btn-size-{sizePreset} kt-btn-width-type-{widthType}
            kb-btn-global-{fill|outline|inherit} kt-btn-has-text-true kt-btn-has-svg-{true|false} {className} wp-block-kadence-singlebtn"
     id="{anchor}" aria-label="{label}" href="{link}" target="_blank" rel="noreferrer noopener">
    <span class="kb-svg-icon-wrap kb-svg-icon-fe_play kt-btn-icon-side-left"><svg …></svg></span>   <!-- si icon, côté gauche -->
    <span class="kt-btn-inner-text">{text}</span>
  </a>
</div>
```

- Le groupe est enregistré en HTML statique, avec les boutons sous forme de commentaires `<!-- wp:kadence/singlebtn {…} /-->`. Le **bouton est entièrement rendu par PHP** (`save` renvoie `null`).
- Sans `link`, le bouton est un `<span>` et non un `<a>`. [T]
- Feuille de base du groupe : `display:flex; flex-wrap:wrap; align-items:center; justify-content:center; gap:var(--global-kb-gap-xs, .5rem)`. **Les boutons passent donc à la ligne d'eux-mêmes** quand la place manque. [T]

### 1.2 `kadence/advancedbtn` (groupe)

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `uniqueID` | string | voir § 0 | `""` | classe `kb-btns{ID}`, CSS du groupe | T |
| `hAlign` | string | `left`, `center`, `right`, `space-between` | `"center"` | `justify-content` (`flex-start`, `center`, `flex-end`, `space-between`) | T (tous) |
| `thAlign` / `mhAlign` | string | mêmes valeurs ; `""` = hérite | `""` | tablette / mobile | T |
| `vAlign` | string | `top`, `center`, `bottom` | `"center"` | `align-items` (`flex-start`, `center`, `flex-end`) | T (`bottom`) |
| `tvAlign` / `mvAlign` | string | idem, tablette / mobile | `""` | | C |
| `gap` | array | `[bureau, tablette, mobile]` ; nombres ou jetons (voir ci-dessous) | `["xs","",""]` | `gap` horizontal **et** vertical (passage à la ligne) | T |
| `gapUnit` | string | `px`, `rem`, `em` | `"px"` | unité des nombres de `gap` | T (`px`, `rem`) |
| `orientation` | array | `[bureau, tablette, mobile]` : `row`, `column`, `row-reverse`, `column-reverse`, `""` | `["","",""]` | `flex-direction`. En `column`, `hAlign` pilote `align-items`, et **`space-between` devient `center`** (constaté à 375 px avec `"hAlign":"space-between","orientation":["","","column"]` : `align-items:center`) | T (`["","","column"]`) |
| `padding` / `tabletPadding` / `mobilePadding` | array | `[haut, droite, bas, gauche]` | `["","","",""]` | padding du groupe | T (`padding`) |
| `paddingUnit` | string | unité | `"px"` | | T |
| `margin` | array | **format particulier** : `[{"desk":[h,d,b,g],"tablet":[h,d,b,g],"mobile":[h,d,b,g]}]` | vide | marges du groupe | T |
| `marginUnit` | string | unité | `"px"` | | T |
| `className` | string | classes CSS | (aucun) | ajoutées au `<div>` | T |
| `anchor` | string | identifiant HTML sans `#` | (aucun) | `id` du `<div>` | T |
| `lockBtnCount` | boolean | verrouille le nombre de boutons dans l'éditeur | `false` | | C |

Jetons de `gap` (CSS produit) : `none` 0, `xs` 0,5 rem, `sm` et `skinny` 1 rem, `md` et `default` 2 rem, `lg` et `wider` 4 rem, `narrow` 20 px, `wide` 40 px, `widest` 80 px. Mesuré : `"sm"` → 16 px ; attribut absent → 8 px (feuille de base). [T pour `sm` et l'absence, C pour les autres]

**Anciens attributs à ne pas utiliser** sur le groupe : `btns`, `btnCount`, `typography`, `fontWeight`, `fontStyle`, `textTransform`, `letterSpacing`, `googleFont`, `widthType`, `widthUnit`, `forceFullwidth`, `collapseFullwidth`. Ils datent de l'ancien format, où les boutons étaient décrits dans le groupe. Constaté sur `08-anciens-attributs` : `textTransform:"uppercase"`, `fontWeight:"700"` et `typography:"Georgia"` produisent une règle `.kt-btns{ID} .kt-button{…}` **sans effet**, car le groupe porte désormais la classe `kb-btns{ID}` et non `kt-btns{ID}`. La typographie se règle **sur chaque bouton**. [T]

Exemples testés :

```json
"hAlign":"right", "thAlign":"center", "mhAlign":"left"
"hAlign":"left", "orientation":["","","column"], "mhAlign":"center"
"hAlign":"left", "gap":[12,10,8], "gapUnit":"px"
"hAlign":"left", "padding":[16,0,16,0], "margin":[{"desk":[32,"",8,""],"tablet":["","","",""],"mobile":[8,"","",""]}], "marginUnit":"px"
```

Mesures : bouton à droite à 1280 px, au centre à 900, à gauche à 375 ; boutons empilés et centrés à 375 ; gouttières de 12, 10 et 8 px ; marge haute de 32 px (bureau et tablette) puis 8 px (mobile). [T]

### 1.3 `kadence/singlebtn` : contenu et lien

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `uniqueID` | string | voir § 0 | `""` | **obligatoire**, sinon aucun rendu | T |
| `text` | string | texte ; le HTML en ligne est conservé (`<em>`, `&amp;`) | `""` | `<span class="kt-btn-inner-text">` | T |
| `link` | string | `/chemin/`, `#ancre`, `https://…`, `tel:…`, `mailto:…` | `""` | `href` (passé par `esc_url`) ; sans lien → `<span>` | T |
| `target` | string | `_self`, `_blank` (`video` ouvre une visionneuse) | `"_self"` | `_blank` ajoute `target="_blank"` **et** `rel="noreferrer noopener"` | T (`_blank`), C (`video`) |
| `noFollow` | boolean | | `false` | ajoute `nofollow` à `rel` | T |
| `sponsored` | boolean | | `false` | ajoute `sponsored` à `rel` | T |
| `download` | boolean | | `false` | attribut `download=""` | T |
| `label` | string | texte | `""` | `aria-label` | T |
| `buttonRole` | boolean | | `false` | `role="button"` | T |
| `anchor` | string | identifiant | (aucun) | `id` du bouton | T |
| `className` | string | classes | (aucun) | ajoutées au bouton | T |

Constats :
- `"target":"_blank"` suffit : `rel="noreferrer noopener"` est **ajouté automatiquement**. Avec `noFollow` et `sponsored`, on obtient `rel="noreferrer noopener nofollow sponsored"`. Avec `noFollow` seul, `rel=" nofollow"` (espace initiale, sans conséquence). [T]
- `target:"_blank"` sans `link` : aucun attribut ajouté (`<span>`). [T]
- `"link":"#"` ajoute `role="button"`. [T]
- **Un lien relatif sans barre initiale est cassé** : `"films/"` devient `href="http://films/"`. Toujours écrire `"/films/"`. [T]
- Dans `text`, WordPress typographie l'affichage : `'` devient `’` et `--` devient `–`. [T]
- Les codes courts sont interprétés dans `link` (`do_shortcode`). [C]

```json
{"name":"kadence/singlebtn","attributes":{"uniqueID":"bt-ext","text":"YouTube (nouvel onglet)","link":"https://www.youtube.com/@pascaldupont","target":"_blank"}}
```

Rendu constaté : `<a class="kb-button … kb-btnbt-ext …" href="https://www.youtube.com/@pascaldupont" target="_blank" rel="noreferrer noopener">`.

### 1.4 `kadence/singlebtn` : style de base, couleurs, survol

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `inheritStyles` | string | `fill`, `outline`, `inherit` (style bouton du thème), `inherit-secondary` | `"fill"` | classe `kb-btn-global-…`, style de base | T (`fill`, `outline`) |
| `sizePreset` | string | `small`, `standard`, `large`, `xlarge` | `"standard"` | taille de police 0,9 / 1,125 / 1,35 / 1,65 rem | T |
| `color` | string | couleur (§ 0, règle 10) | `""` | couleur du texte | T |
| `background` | string | couleur, ou `"transparent"` | `""` | fond | T |
| `colorHover` / `backgroundHover` | string | couleur | `""` | survol **et** focus clavier (`:hover, :focus`) | T |
| `backgroundType` | string | `normal`, `gradient` | `"normal"` | | T (`gradient`) |
| `gradient` | string | dégradé CSS complet | `""` | `background: … !important` | T |
| `backgroundHoverType` / `gradientHover` | string | dégradé au survol | `"normal"` / `""` | | C |
| `textBackgroundType` / `textGradient` | string | texte en dégradé | `"normal"` / `""` | | C |

Constats :
- **Sans couleur, le bouton prend le bleu de Kadence**, qui ne correspond pas au site : fond `palette1` `rgb(43,108,176)`, texte blanc, survol `palette2` `rgb(33,83,135)`, rayon de 3 px, padding `.4em 1em`, police de 18 px et graisse 400. Toujours fixer les couleurs. [T]
- `outline` sans couleurs : bordure de 2 px `palette1`, fond transparent. [C]
- Si `colorHover` est absent, la couleur du texte reste celle de `color` au survol. Constaté avec `color:"palette3"`. [T]
- `"backgroundType":"gradient"` avec `backgroundHover` : le dégradé est mis en `!important` et le survol passe par un calque `::before` qui apparaît en fondu (0,3 s). [T pour le CSS]
- Transition de base : `transition: all .3s ease-in-out`. [C]

### 1.5 `kadence/singlebtn` : bordure, rayon, ombre

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `borderStyle` | array | `[{"top":[couleur, style, épaisseur], "right":[…], "bottom":[…], "left":[…], "unit":"px"}]` ; style `solid`, `dashed`… ; côté vide `["","",""]` | côtés vides | T |
| `borderHoverStyle` | array | même format, au survol et au focus | côtés vides | T |
| `tabletBorderStyle` / `mobileBorderStyle` (+ `…HoverStyle`) | array | même format, par palier | | C |
| `borderRadius` | array | `[haut-gauche, haut-droite, bas-droite, bas-gauche]` | `["","","",""]` (la feuille de base donne 3 px) | T |
| `tabletBorderRadius` / `mobileBorderRadius` | array | idem, par palier | | T (`mobileBorderRadius`) |
| `borderRadiusUnit` | string | `px`, `%`, `em`, `rem` | `"px"` | T (`px`) |
| `borderHoverRadius` | array | rayon au survol ; l'unité est **toujours px** (le code ne lit pas `borderHoverRadiusUnit`) | | T (contre-vérification : `[10,10,10,10]` avec `"borderHoverRadiusUnit":"%"` donne `10px`) |
| `displayShadow` + `shadow` | boolean + array | `[{"color":"#000000","opacity":0.5,"spread":0,"blur":12,"hOffset":0,"vOffset":4,"inset":false}]` (px ; opacité de 0 à 1) | `false` | T |
| `displayHoverShadow` + `shadowHover` | boolean + array | même format | `false` | C |

Le PHP répète les règles de bordure dans les media queries tablette et mobile ; c'est sans conséquence. [T]

```json
"borderStyle":[{"top":["#a3302f","solid",1],"right":["#a3302f","solid",1],"bottom":["#a3302f","solid",1],"left":["#a3302f","solid",1],"unit":"px"}],
"borderRadius":[999,999,999,999], "mobileBorderRadius":[0,0,0,0],
"displayShadow":true, "shadow":[{"color":"#000000","opacity":0.5,"spread":0,"blur":12,"hOffset":0,"vOffset":4,"inset":false}]
```

Mesuré : rayon de 999 px à 1280 et 900 px, 0 à 375 ; `box-shadow: rgba(0,0,0,0.5) 0px 4px 12px 0px`. [T]

### 1.6 `kadence/singlebtn` : espacements, largeur

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `padding` / `tabletPadding` / `mobilePadding` | array | `[h, d, b, g]` | `["","","",""]` (la feuille de base donne `.4em 1em`) | T |
| `paddingUnit` | string | `px`, `rem`, `em`… (une seule unité pour les trois paliers) | `"px"` | T (`px`, `rem`) |
| `margin` / `tabletMargin` / `mobileMargin` | array | `[h, d, b, g]` | `["","","",""]` | T (`margin`) |
| `marginUnit` | string | unité | `"px"` | T |
| `widthType` | string | `auto`, `fixed`, `full` | `"auto"` | T |
| `width` | array | `[bureau, tablette, mobile]` ; lu seulement si `widthType` vaut `fixed` | `["","",""]` | T |
| `widthUnit` | string | `px`, `%` | `"px"` | T |

Mesures [T] :
- `"widthType":"fixed","width":[240,200,160]` : 240, 200 puis 160 px ;
- `"widthType":"fixed","width":[50,"",100],"widthUnit":"%"` : 544 px sur 1088, puis 100 % au mobile ;
- `"widthType":"full"` (`flex:1 0 fit-content; width:100%`) : le bouton occupe toute la ligne. Deux boutons `full` dans un groupe se partagent la ligne : 2 × 540 px à 1280.

Avec `tabletPadding:[10,30,10,30]` et `mobilePadding:[6,12,6,12]`, on mesure `10px 30px` à 900 px et `6px 12px` à 375 px. [T]

### 1.7 `kadence/singlebtn` : typographie

`typography` est un tableau contenant **un** objet :

```json
"typography":[{"size":[0.95,"",""],"sizeType":"rem","lineHeight":[1.2,"",""],"lineType":"",
  "letterSpacing":[0.04,"",""],"letterType":"em","textTransform":"","family":"","google":false,
  "style":"","weight":"500","variant":"","subset":"","loadGoogle":false}]
```

| Clé | Type | Format | Vérif. |
|---|---|---|---|
| `size` | array | `[bureau, tablette, mobile]` ; nombres, ou jetons `sm`, `md`, `lg`, `xl`, `xxl`, `3xl` (`var(--global-kb-font-size-…)`, tailles fluides) | T (nombres, `md`) |
| `sizeType` | string | `px`, `rem`, `em` | T (`px`, `rem`) |
| `lineHeight` | array | `[bureau, tablette, mobile]` | T |
| `lineType` | string | `""` = sans unité (recommandé), `px`, `em` | T (`""`) |
| `letterSpacing` | array | `[bureau, tablette, mobile]` | T |
| `letterType` | string | `px`, `em` | T (`px`, `em`) |
| `textTransform` | string | `uppercase`, `lowercase`, `capitalize`, `""` | T (`uppercase`) |
| `family` | string | nom de police brut ; un nom avec espace est mis entre apostrophes ; `var(--display)` fonctionne ; `""` = hérite de la police du site | T |
| `weight` | string | `"400"`, `"500"`, `"700"`… | T |
| `style` | string | `italic`, `normal` | T |
| `google`, `loadGoogle` | boolean | **toujours `false`** | T |

Mesures [T] :
- `"size":[18,16,14]` donne 18, 16 puis 14 px ;
- `"letterSpacing":[2,"",1]` donne 2 px au bureau et en tablette, 1 px au mobile ;
- `"family":"var(--display)"` donne Newsreader ;
- `"family":""` donne `"Hanken Grotesk", system-ui, …`, la police du site.

**Piège** : `style` (`italic`) n'est écrit dans le CSS **que si `family` est renseigné** (le code le place dans le bloc `if family`). [C, confirmé : italique obtenu avec `family:"Georgia"`]

### 1.8 `kadence/singlebtn` : icône et divers

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `icon` | string | nom d'icône : `fe_arrowRight`, `fe_play`, `fe_externalLink`, `fe_download`, `fe_film`, `fe_mail`, `fe_chevronRight`… (`fe_*` = Feather, liste dans `includes/icons-ico-array.php` ; `fa_*` et `fas_*` dans `icons-array.php`) | `""` | T (`fe_arrowRight`, `fe_play`) |
| `iconSide` | string | `right`, `left` | `"right"` | T |
| `iconSize` | array | `[bureau, tablette, mobile]` | `["","",""]` (1em) | T |
| `iconSizeUnit` | string | unité | `"px"` | T |
| `iconColor` / `iconColorHover` | string | couleur | `""` (`currentColor`) | T |
| `onlyIcon` | array | `[bureau, tablette, mobile]` en booléens ; `true` masque le texte (`display:none`) | `[false,"",""]` | T (`[true,"",""]`) |
| `iconPadding`, `iconTitle`, `iconReveal`, `onlyText` | | | | C |
| `textUnderline` | string | `underline` | (aucun) | T |
| `tooltip`, `tooltipPlacement` | string | infobulle (script tippy) | `""` | C |

Icône seule : garder `text` (il reste dans le HTML) **et** renseigner `label`, qui devient l'`aria-label`. Mesuré : bouton de 36 × 36 px, texte en `display:none`. [T]

L'écart entre l'icône et le texte est de 0,5 em (`gap`, feuille de base). [T]

Variantes pour l'en-tête transparent ou collant (`colorTransparent…`, `…Sticky…`) : non pertinentes ici. [C]

### 1.9 Plusieurs boutons sur une ligne avec retour à la ligne [T]

Il n'y a rien à activer : le groupe est en `flex-wrap: wrap`. On règle seulement l'alignement et l'espacement :

```json
{"name":"kadence/advancedbtn","attributes":{"uniqueID":"bt-g6","hAlign":"left","gap":[12,10,8],"gapUnit":"px"},
 "innerBlocks":[ …8 boutons contour : « Documentaires », « Pour le 1er RCP », « Mémoire », « Série Serval », « Entreprises et institutions », « Salons et défense », « Entretiens », « Clips et créations »… ]}
```

| Largeur | Disposition mesurée |
|---|---|
| 1280 px | 6 boutons sur la 1re ligne, 2 sur la 2e ; écart de 12 px |
| 900 px | 4 + 4 ; écart de 10 px |
| 375 px | 7 lignes (1 ou 2 boutons par ligne) ; écart de 8 px ; aucun débordement horizontal |

Le `gap` s'applique aussi **entre les lignes**. Pour des boutons empilés au mobile et pleine largeur, ajouter `"orientation":["","","column"]` au groupe ; pour des boutons qui remplissent la ligne, `"widthType":"full"` sur chaque bouton.

---

## 2. Onglets : `kadence/tabs` + `kadence/tab`

### 2.1 HTML produit et comportement [T]

```html
<div class="wp-block-kadence-tabs alignnone" id="{anchor}">
 <div class="kt-tabs-wrap kt-tabs-id{uniqueID} kt-tabs-has-8-tabs kt-active-tab-{startTab||currentTab} kt-tabs-layout-tabs
             kt-tabs-tablet-layout-inherit kt-tabs-mobile-layout-inherit kt-tab-alignment-left [kt-create-accordion]">
  <ul class="kt-tabs-title-list [kb-tabs-list-columns kb-tab-title-columns-4]">
   <li id="films-documentaires" class="kt-title-item kt-title-item-1 … kt-tab-title-active">
     <a href="#films-documentaires" data-tab="1" class="kt-tab-title kt-tab-title-1"><span class="kt-title-text">Documentaires</span></a></li>
   <li id="films-1er-rcp" class="kt-title-item kt-title-item-2 … kt-tab-title-inactive">…</li>
  </ul>
  <div class="kt-tabs-content-wrap">
   <div class="wp-block-kadence-tab kt-tab-inner-content kt-inner-tab-1 kt-inner-tab{uniqueID tab}"><div class="kt-tab-inner-content-inner"> … blocs … </div></div>
   <div class="wp-block-kadence-tab kt-tab-inner-content kt-inner-tab-2 …">…</div>
  </div>
 </div>
</div>
```

- Le HTML est **statique** : titres et panneaux sont écrits dans le contenu enregistré.
- Au chargement, le script `kt-tabs.min.js` ajoute `role="tablist"`, `role="tab"` et `role="tabpanel"`, puis `aria-hidden` et `display:none` (en style en ligne) sur les panneaux inactifs. Il gère aussi les flèches gauche/droite du clavier. [T pour les rôles et l'affichage, C pour le clavier]
- **Sans JavaScript, tous les panneaux sont visibles**, les uns sous les autres. Mesuré sur `02-onglets` avec JS désactivé : les 8 panneaux en `display:block`. [T]
- Un clic sur un titre **ne modifie pas l'URL** (`preventDefault`). [T]
- **Ancre d'URL** : si l'adresse contient `#{id d'un titre}`, l'onglet correspondant s'ouvre au chargement **et** lors d'un changement d'ancre (`hashchange`). Mesuré : `…/#films-memoire` ouvre l'onglet 3 et fait défiler jusqu'à la barre de titres. [T]

### 2.2 Référencement : le contenu des onglets inactifs reste dans le HTML [T]

Vérifié sur `02-onglets` (8 onglets, 46 cartes de films) avec `curl` sur le HTML brut :
- les 46 titres `<h3>` des 8 onglets sont présents, ainsi que tous les liens YouTube ;
- dans le bloc d'onglets, le HTML brut ne contient ni `display:none`, ni `aria-hidden`, ni `role="tabpanel"` : ces attributs sont ajoutés par le script après le chargement ;
- les titres d'onglets sont de vrais liens `<a href="#films-…">`.

Le contenu est donc indexable. Pour un moteur qui exécute le JavaScript, les panneaux inactifs sont masqués visuellement (`display:none`). Le poids qu'un moteur leur donne n'est pas vérifiable ici.

L'accordéon (§ 3) se comporte de la même façon : le contenu des volets fermés est dans le HTML, avec la classe `kt-accordion-panel-hidden`.

### 2.3 `kadence/tabs` : structure et comportement

| Attribut | Type | Format / valeurs | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `uniqueID` | string | voir § 0 | `""` | classe `kt-tabs-id{ID}` ; sans lui, `kt-tabs-idnotset` et aucun CSS | T |
| `anchor` | string | identifiant | (aucun) | `id` du `<div>` extérieur | T |
| `tabCount` | number | **= nombre de titres = nombre de `kadence/tab`** | `3` | | T |
| `titles` | array | `[{"text":"…","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"…"}, …]`, un objet par onglet, dans l'ordre | 3 titres « Tab n » | texte des titres | T |
| `titles[i].anchor` | string | identifiant sans `#` | `""` | `id` du `<li>` et `href` du lien | T |
| `startTab` | number | numéro de l'onglet ouvert au chargement (à partir de 1) | `""` | classe `kt-active-tab-N` | T |
| `currentTab` | number | onglet sélectionné dans l'éditeur ; utilisé si `startTab` est vide | `1` | | T |
| `linkPaneCollapse` | boolean | en mode accordéon, un seul panneau ouvert à la fois | `false` | `data-no-allow-multiple-open` | T |
| `blockAlignment` | string | `none`, `wide`, `full`, `center` | `"none"` | classe `align{…}` sur l'enveloppe | T (`none`), C (autres) |

**Mettre toujours `startTab`.** `currentTab` change quand quelqu'un clique un onglet dans l'éditeur puis enregistre ; l'onglet ouvert en public changerait alors aussi. Constaté : `"currentTab":2` sans `startTab` ouvre l'onglet 2. [T]

**Identifiant d'un titre sans `anchor`** : `tab-` + le texte en minuscules, dont tout caractère hors `[0-9a-z-]` est **supprimé**. Les accents et les espaces disparaissent : « Mémoire » donne `tab-mmoire`, « Pour le 1er RCP » `tab-pourle1errcp`, « Clips & créations » `tab-clipscrations`. **Toujours renseigner `anchor`** pour obtenir des liens lisibles et stables (`/films/#films-memoire`). [T]

Cohérence des nombres (`05-pieges`) [T] :
- `tabCount:2` avec 3 `kadence/tab` : à l'enregistrement, l'éditeur **supprime le 3e panneau et son contenu**. Le gabarit des enfants est verrouillé (`templateLock:"all"`) sur `tabCount` ;
- `tabCount:3` avec 2 titres : le 3e titre s'affiche « Tab 3 » (identifiant `tab-tab3`) ;
- `kadence/tab` **sans `id`** : tous les panneaux deviennent `kt-inner-tab-1`. Le script supprime alors les titres 2 et 3, qui n'ont plus de panneau : **il ne reste qu'un onglet**.

### 2.4 `kadence/tabs` : disposition et responsive

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `layout` | string | bureau : `tabs` (titres en ligne) ou `vtabs` (titres en colonne à gauche) | `"tabs"` | T |
| `tabletLayout` | string | `inherit`, `tabs`, `vtabs`, `accordion` | `"inherit"` | T (`tabs`) |
| `mobileLayout` | string | `inherit`, `tabs`, `vtabs`, `accordion` | `"inherit"` | T (`accordion`) |
| `tabAlignment` | string | `left`, `center`, `right` (`justify-content` de la liste des titres) | `"left"` | T (tous) |
| `widthType` | string | `normal` (largeur du texte), `percent` (titres en colonnes égales) | `"normal"` | T |
| `tabWidth` | array | `[bureau, tablette, mobile]` = **nombre de titres par ligne** ; lu si `widthType` vaut `percent` | `[4,"",""]` | T |
| `gutter` | array | `[bureau, tablette, mobile]`, écart horizontal en px entre titres (mode `percent`) | `[10,"",""]` | T |
| `verticalTabWidth` | array | largeur de la colonne des titres en mode `vtabs`, **chaînes** : `["25","",""]` | `["30","",""]` | T |
| `verticalTabWidthUnit` | string | `%`, `px` | `"%"` | T (`%`) |
| `maxWidth` / `tabletMaxWidth` / `mobileMaxWidth` | number | px ; bloc centré | `""` | T (`maxWidth`) |

Le CSS tablette des dispositions est écrit `@media (min-width: 767px) and (max-width: 1024px)`. [C]

**Comportement mobile : trois options testées sur la barre de 8 catégories** (`02-onglets`, `06-modeles`) [T] :

| Option | Attributs | 1280 px | 900 px | 375 px |
|---|---|---|---|---|
| A. Pastilles qui passent à la ligne (**retenue pour les films**) | `mobileLayout:"inherit"` (défaut) | 8 titres sur 1 ligne | 6 + 2 | 5 lignes (2, 2, 1, 2, 1) |
| B. Grille de titres | `widthType:"percent"`, `tabWidth:[4,2,2]`, `gutter:[8,8,8]`, **`titleMargin:[0,0,8,0]`** (indispensable, voir ci-dessous) | 4 × 2 lignes, titres de 274 px | 2 par ligne (422 px) | 2 par ligne (160 px, texte sur 2 lignes si besoin) |
| C. Accordéon | `mobileLayout:"accordion"` | onglets | onglets | liste des titres masquée ; chaque titre est recopié par le script au-dessus de son panneau (`div.kt-tabs-accordion-title`), en pleine largeur |

**Option B : `titleMargin` est obligatoire** (contre-vérification). La feuille de base donne à chaque `<li>` une marge droite de 4 px (`margin:0 4px -1px 0`). Avec `flex:0 1 25 %` (ou 50 %), les titres ne tiennent alors plus sur la ligne. Le PHP ne force les marges gauche et droite des `<li>` à 0 en mode `percent` (disposition `tabs`) que si `titleMargin`, `tabletTitleMargin` ou `mobileTitleMargin` est enregistré, c'est-à-dire différent du défaut. Mesuré sur `verif-pieges` avec 8 titres : **sans** `titleMargin`, on obtient 3 lignes (3 + 3 + 2) à 1280 px et **1 titre par ligne** (8 lignes) à 900 et 375 px ; **avec** `titleMargin:[0,0,8,0]`, on obtient 4 + 4 à 1280 px, puis 2 par ligne à 900 et 375 px. [T]

Les mesures de largeur et de nombre de lignes du tableau dépendent du conteneur. Elles ont été prises dans une rangée à padding `md`, soit 311 px utiles à 375 px. En pleine largeur (375 px utiles), l'option A donne **4 lignes** au lieu de 5 (`verif-onglets`). [T]

Option C : sans `linkPaneCollapse`, plusieurs panneaux peuvent être ouverts en même temps, et un clic sur le titre ouvert le referme (tout peut être fermé). Avec `linkPaneCollapse:true`, un seul panneau est ouvert. Les styles de titre (`titleColor`, `titleBgActive`…) s'appliquent aussi aux titres d'accordéon. [T]

Aucun débordement horizontal dans les trois cas. [T]

### 2.5 `kadence/tabs` : style des titres

| Attribut | Type | Format | Défaut | Effet | Vérif. |
|---|---|---|---|---|---|
| `titleColor` / `titleColorHover` / `titleColorActive` | string | couleur | `null` | texte : normal, survol, onglet actif | T |
| `titleBg` / `titleBgHover` | string | couleur, `"transparent"` | `null` | fond | T |
| `titleBgActive` | string | couleur | `""` | **si vide, le fond actif est forcé à `#ffffff`** | T |
| `titleBorder` / `titleBorderHover` / `titleBorderActive` | string | couleur de bordure | `null` | | T |
| `titleBorderWidth` | array | `[h, d, b, g]` | `["","","",""]` (feuille de base : `1px 1px 0 1px`) | | T |
| `titleBorderWidthUnit` | string | unité | `"px"` | | T |
| `titleBorderRadius` | array | `[hg, hd, bd, bg]` | `null` (feuille de base : 4 px en haut) | | T |
| `titleBorderRadiusUnit` | string | unité | `"px"` | | T |
| `titlePadding` / `tabletTitlePadding` / `mobileTitlePadding` | array | `[h, d, b, g]` | vide (feuille de base : `8px 16px`) | | T |
| `titlePaddingUnit` | string | unité | `"px"` | | T (`px`, `rem`) |
| `titleMargin` / `tabletTitleMargin` / `mobileTitleMargin` | array | `[h, d, b, g]`, marge des `<li>` ; la marge droite du dernier est forcée à 0 (disposition `tabs`) ; en mode `widthType:"percent"`, les marges gauche et droite de **tous** les `<li>` sont forcées à 0 | vide (feuille de base : `0 4px -1px 0`) | à renseigner en mode `percent` (§ 2.4, option B) | T |
| `titleMarginUnit` | string | unité | `"px"` | | T |
| `enableSubtitle` + `titles[i].subText` | boolean + string | sous-titre sous le texte (`span.kt-title-sub-text`, 14 px) | `false` | | T |
| `subtitleColor` / `…Hover` / `…Active` | string | couleur | `null` | | T (`subtitleColor`) |
| `subtitleFont` | array | typographie du sous-titre | | | C |
| `titles[i].icon`, `iconSide`, `onlyIcon`, `iSize` | | icône dans le titre | | | C |

**Style par défaut inadapté au site sombre** (`02-onglets`, onglets T4) : titres en `palette5` `rgb(74,85,104)`, titre actif sur fond blanc avec bordure `#dee2e6`, panneau bordé de 1 px `#dee2e6` avec 20 px de padding. Toujours fixer les couleurs, dont `titleBgActive`. [T]

### 2.6 `kadence/tabs` : typographie des titres

Ces attributs sont des champs simples, et non un objet `typography` comme sur les boutons.

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `size` | **string** | `"0.85"`, `"18"` | `null` | T |
| `tabSize` / `mobileSize` | **string** | tablette / mobile | `null` | T |
| `sizeType` | string | `px`, `rem`, `em` (pour les trois tailles) | `"px"` | T (`px`, `rem`) |
| `lineHeight` | number | `1.4` | `null` | T |
| `lineType` | string | **`""` pour une valeur sans unité** | `"px"` | T |
| `tabLineHeight` / `mobileLineHeight` | number | | `null` | C |
| `letterSpacing` | number | en px | `null` | T |
| `typography` | string | nom de police (écrit tel quel, sans apostrophes) ; absent = police du site | `""` | T |
| `fontWeight` | string | `"500"` | `"regular"` | T |
| `textTransform` | string | `uppercase`… | `null` | T |
| `fontStyle` | string | `italic`, `normal` | `"normal"` | C |
| `googleFont` | boolean | **laisser `false`** | `false` | C |

**Piège `lineType`** : le défaut `"px"` n'est pas enregistré, et le PHP ajoute `px` quand `lineType` est absent. `"lineHeight":1.4` seul donne `line-height:1.4px`, et les titres s'écrasent : liste de 17 px de haut sur `05-pieges`. **Toujours écrire `"lineHeight":1.4,"lineType":""`.** [T]

Mesuré sur `07-complements` avec `size:"18"`, `tabSize:"16"`, `mobileSize:"13"`, `sizeType:"px"`, `textTransform:"uppercase"`, `letterSpacing:1.5` et `titlePadding` 12/24, 10/16, 6/10 : 18, 16 puis 13 px, avec le padding attendu à chaque palier. [T]

### 2.7 `kadence/tabs` : panneaux (contenu)

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `contentBorderStyles` | array | `[{"top":[couleur, style, épaisseur], "right":[…], "bottom":[…], "left":[…], "unit":"px"}]` ; pour **aucune bordure**, épaisseur `0` sur les 4 côtés | couleur `#dee2e6`, épaisseur 1 | T |
| `tabletContentBorderStyles` / `mobileContentBorderStyles` | array | même format | vide | C |
| `contentBorder` | array | **ancien attribut** : l'éditeur le convertit en `contentBorderStyles` (couleur `contentBorderColor` ou `#dee2e6`, style vide) et le vide | `["","","",""]` | T |
| `contentBorderRadius` | array | `[hg, hd, bd, bg]` ; toujours en **px** : le PHP lit `contentBorderRadiusType`, absent du block.json, et ignore `contentBorderRadiusUnit` | `[0,0,0,0]` | C |
| `contentBgColor` | string | couleur du panneau | `""` | T |
| `innerPadding` / `tabletInnerPadding` / `mobileInnerPadding` | array | `[h, d, b, g]` ; nombres (T) ou jetons d'espacement `sm`, `md`… (C) | `["sm","sm","sm","sm"]`, non enregistré : la feuille de base donne 20 px | T |
| `innerPaddingType` | string | unité | `"px"` | T |
| `minHeight` / `tabletMinHeight` / `mobileMinHeight` | number | px, hauteur minimale du panneau | `""` | T |

Mesuré sur `07-complements` : `minHeight` 200, 150 puis 100 px ; `innerPadding` 32, 24 puis 12 px ; fond `#17202a` ; bloc de 600 px centré avec `maxWidth:600`. [T]

### 2.8 `kadence/tab` (un panneau)

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `id` | number | **numéro du panneau, de 1 à `tabCount`, dans l'ordre** ; lie le panneau au titre (`kt-inner-tab-{id}` ↔ `data-tab`) | `1` (non enregistré pour le 1er) | T |
| `uniqueID` | string | voir § 0 | `""` | T |

Les enfants peuvent être n'importe quels blocs : rangée `kadence/rowlayout`, paragraphes, image, boutons… Testé avec un paragraphe, une rangée de 4 colonnes contenant chacune un groupe de boutons, et une image `core/image`. [T]

---

## 3. Accordéon : `kadence/accordion` + `kadence/pane`

Utile pour une FAQ, ou comme alternative aux onglets sur une page longue.

HTML [T] : `div.kt-accordion-wrap.kt-accordion-id{uniqueID}` > `div.kt-accordion-inner-wrap[data-allow-multiple-open][data-start-open]` > un `div.wp-block-kadence-pane.kt-accordion-pane-{id}` par volet, avec l'`id` = `anchor`. Chaque volet contient :
- `<{titleTag} class="kt-accordion-header-wrap"><button class="kt-blocks-accordion-header">…<span class="kt-blocks-accordion-title">{title}</span>…</button></{titleTag}>` ;
- `div.kt-accordion-panel.kt-accordion-panel-hidden` > `div.kt-accordion-panel-inner` > contenu.

### 3.1 `kadence/accordion`

| Attribut | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `uniqueID` | string | | `""` | T |
| `paneCount` | number | nombre de volets ; le garder égal au nombre d'enfants | `2` | T (non vérifié en cas d'écart ; le gabarit n'est pas verrouillé) |
| `openPane` | number | volet ouvert au départ, **à partir de 0** | `0` | T (`1` ouvre le 2e volet) |
| `startCollapsed` | boolean | tout fermé au départ (`data-start-open="none"`) | `false` | T |
| `linkPaneCollapse` | boolean | un seul volet ouvert à la fois | `true` | T |
| `faqSchema` | boolean | ajoute un JSON-LD `FAQPage` (questions = titres, réponses = contenus) dans `<head>` | `false` | T |
| `titleStyles` | array | `[{size:[…], sizeType, lineHeight:[…], lineType, letterSpacing, family, google, style, weight, variant, subset, loadGoogle, padding:[h,d,b,g], paddingTablet, paddingMobile, paddingType, marginTop, color, background, colorHover, backgroundHover, colorActive, backgroundActive, textTransform, border, borderRadius, borderWidth, borderHover, borderActive}]` | voir block.json | T (`size`, `family`, `weight`, `padding`, `marginTop`, couleurs) |
| `titleBorder` / `titleBorderHover` / `titleBorderActive` | array | même format que `borderStyle` | vide | T |
| `titleBorderRadius` (+ tablette, mobile, `…Unit`) | array | | | C |
| `contentBorderStyle` | array | **sans « s » final, contrairement aux onglets** | vide | T |
| `contentPadding` / `contentTabletPadding` / `contentMobilePadding` | array | `[h, d, b, g]` | `["sm","sm","sm","sm"]` | T (`contentPadding`) |
| `contentPaddingType` | string | unité | `"px"` | T |
| `contentBgColor` | string | couleur | `""` | C |
| `textColor` / `linkColor` / `linkHoverColor` | string | couleurs du contenu des volets | `""` | T (`textColor`) |
| `iconStyle` | string | `basic`, `basiccircle`, `xclose`, `xclosecircle`, `arrow`, `arrowcircle` | `"basic"` | T (`arrow`, `basic` : classes produites) |
| `iconColor` | object | `{"standard":"…","active":"…","hover":"…"}` | vides | C (CSS produit, rendu non mesuré) |
| `iconSide` | string | `right`, `left` | `"right"` | T (`right`) |
| `titleAlignment`, `maxWidth`, `columnLayout`, `columnGap` | | | | C |

**Style par défaut inadapté au site sombre** (`03-accordeon`, 2e accordéon) : titres sur fond `rgb(247,250,252)`, texte `rgb(74,85,104)` ; titre actif sur fond `rgb(74,85,104)`, texte blanc. [T]

### 3.2 `kadence/pane`

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `id` | number | 1, 2, 3… | `1` | T |
| `uniqueID` | string | | `""` | T |
| `title` | `rich-text` dans le block.json (`source: rich-text`) ; passer une chaîne dans la spec | texte du titre ; **non enregistré dans le commentaire du bloc**, il est relu dans le HTML (`.kt-blocks-accordion-title`) | `""` | T |
| `titleTag` | string | `div`, `h2`, `h3`… | `"div"` | T (`h3`, `div`) |
| `anchor` | string | `id` du volet | (aucun) | T |
| `icon`, `iconSide`, `hideLabel`, `ariaLabel` | | | | C |

Comportement mesuré sur `03-accordeon` (`startCollapsed:true`, `linkPaneCollapse:true`) : au départ, tout est fermé (`aria-expanded="false"`) ; un clic sur le volet 1 l'ouvre ; un clic sur le volet 2 ouvre le 2 et referme le 1. Titres `<h3>` présents dans le HTML ; JSON-LD `FAQPage` présent. [T]

---

## 4. Ancres et liens internes

| Bloc | Attribut | Élément qui reçoit l'`id` | Vérif. |
|---|---|---|---|
| `kadence/rowlayout` | `anchor` | `<section>` / `<div>` extérieur de la rangée | T |
| `kadence/column` | `anchor` | `div.wp-block-kadence-column` | T |
| `kadence/advancedbtn` | `anchor` | `div` du groupe | T |
| `kadence/singlebtn` | `anchor` | `<a>` du bouton | T |
| `kadence/tabs` | `anchor` | `div.wp-block-kadence-tabs` | T |
| titre d'onglet | `titles[i].anchor` | `<li>` du titre ; **ouvre l'onglet** quand il est dans l'URL | T |
| `kadence/pane` | `anchor` | `div` du volet | T |

Liens testés sur `04-ancres`, à 1280 et 375 px [T] :

| Lien | Résultat |
|---|---|
| bouton `"link":"#section-contact"` | défilement jusqu'à la rangée `anchor:"section-contact"` (haut de la cible à 0 px à 375) |
| lien dans un paragraphe `<a href="#section-contact">` | idem |
| bouton `"link":"#colonne-cible"` | défilement jusqu'à la colonne `anchor:"colonne-cible"` |
| bouton `"link":"#films-entretiens"` (onglet de la même page) | l'onglet 3 s'ouvre et la page défile jusqu'à la barre de titres |
| bouton `"link":"/ref-boutons-onglets-navigation-02-onglets/#films-serval"` (autre page) | chargement de la page, onglet « Série Serval » (4) ouvert |

- Le défilement est fluide grâce à `html { scroll-behavior: smooth; }` dans `pd.css`. L'en-tête Kadence n'est pas collant : la cible arrive en haut de l'écran sans être masquée. Avec un en-tête collant, il faudrait un `scroll-margin-top` (non testé).
- Pour pointer depuis l'accueil vers une catégorie de films : `"link":"/films/#films-serval"`, avec les `anchor` des titres du § 5.4.
- Rappel (`mise-en-page.md`) : `htmlTag:"nav"` n'est pas accepté sur une rangée.

---

## 5. Modèles testés

Ils ont été construits sur une page **neuve**, `ref-boutons-onglets-navigation-06-modeles` (méta du § 0, règle 11), sans bloc invalide, sans erreur JS et sans débordement horizontal à 1280, 900 et 375 px. La réouverture dans l'éditeur ne modifie aucun attribut, et les 179 `uniqueID` enregistrés sont identiques à la spec. Les specs sont produites par les fonctions Python du § 5.4, recopiées en JSON ci-dessous.

### 5.1 Bouton plein rouge, texte ivoire (`#a3302f`, survol `#c0403d`)

```json
{"name":"kadence/singlebtn","attributes":{
  "uniqueID":"mo-btn-films",
  "text":"Voir les films",
  "link":"/films/",
  "color":"#ece8df",
  "background":"#a3302f",
  "colorHover":"#ece8df",
  "backgroundHover":"#c0403d",
  "borderStyle":[{"top":["#a3302f","solid",1],"right":["#a3302f","solid",1],"bottom":["#a3302f","solid",1],"left":["#a3302f","solid",1],"unit":"px"}],
  "borderHoverStyle":[{"top":["#c0403d","solid",1],"right":["#c0403d","solid",1],"bottom":["#c0403d","solid",1],"left":["#c0403d","solid",1],"unit":"px"}],
  "borderRadius":[2,2,2,2],
  "borderRadiusUnit":"px",
  "padding":[0.9,1.5,0.9,1.5],
  "paddingUnit":"rem",
  "typography":[{"size":[0.95,"",""],"sizeType":"rem","lineHeight":[1.2,"",""],"lineType":"","letterSpacing":[0.04,"",""],"letterType":"em","textTransform":"","family":"","google":false,"style":"","weight":"500","variant":"","subset":"","loadGoogle":false}]
 }}
```

Mesuré à 1280 px :
- au repos : texte `rgb(236,232,223)`, fond `rgb(163,48,47)`, bordure `1px solid rgb(163,48,47)`, rayon de 2 px, padding `14.4px 24px`, police `"Hanken Grotesk", system-ui…` en 15,2 px et 500, espacement de 0,608 px, interligne de 18,24 px, bouton de 146 × 49 px ;
- au survol : fond et bordure `rgb(192,64,61)`, texte inchangé. [T]

La bordure de la couleur du fond reproduit le `border: 1px solid` de la maquette et donne au bouton plein la même hauteur que le bouton contour.

### 5.2 Bouton contour clair

```json
{"name":"kadence/singlebtn","attributes":{
  "uniqueID":"mo-btn-contact",
  "text":"Me contacter",
  "link":"/contact/",
  "inheritStyles":"outline",
  "color":"#e8e6e1",
  "background":"transparent",
  "colorHover":"#0d1217",
  "backgroundHover":"#e8e6e1",
  "borderStyle":[{"top":["#a9b6c0","solid",1],"right":["#a9b6c0","solid",1],"bottom":["#a9b6c0","solid",1],"left":["#a9b6c0","solid",1],"unit":"px"}],
  "borderHoverStyle":[{"top":["#e8e6e1","solid",1],"right":["#e8e6e1","solid",1],"bottom":["#e8e6e1","solid",1],"left":["#e8e6e1","solid",1],"unit":"px"}],
  "borderRadius":[2,2,2,2],
  "borderRadiusUnit":"px",
  "padding":[0.9,1.5,0.9,1.5],
  "paddingUnit":"rem",
  "typography":[{"size":[0.95,"",""],"sizeType":"rem","lineHeight":[1.2,"",""],"lineType":"","letterSpacing":[0.04,"",""],"letterType":"em","textTransform":"","family":"","google":false,"style":"","weight":"500","variant":"","subset":"","loadGoogle":false}]
 }}
```

Mesuré :
- au repos : texte `rgb(232,230,225)`, fond transparent, bordure `1px solid rgb(169,182,192)`, 148 × 49 px ;
- au survol : fond `rgb(232,230,225)`, texte `rgb(13,18,23)`, bordure `rgb(232,230,225)`. [T]

`"inheritStyles":"fill"` avec les mêmes couleurs donne exactement le même rendu (constaté : bouton `bt-contour-fill` de `01-boutons`).

Variante pour lien externe : ajouter `"target":"_blank"`. Testé avec `mo-btn-youtube`, rendu `target="_blank" rel="noreferrer noopener"`.

### 5.3 Groupe : plein + contour + externe, retour à la ligne au mobile

```json
{"name":"kadence/advancedbtn","attributes":{"uniqueID":"mo-actions","hAlign":"left","gap":[0.9,"",""],"gapUnit":"rem"},
 "innerBlocks":[ BOUTON_5.1, BOUTON_5.2,
   {"name":"kadence/singlebtn","attributes":{ …mêmes attributs que 5.2…, "uniqueID":"mo-btn-youtube","text":"Chaîne YouTube","link":"https://www.youtube.com/","target":"_blank"}} ]}
```

Les marqueurs `BOUTON_5.1`, `BOUTON_5.2` et `…mêmes attributs que 5.2…` sont à remplacer par les objets complets avant usage. La spec testée contenait les trois objets entiers.

Mesuré : écart de 14,4 px (0,9 rem) entre les boutons. À 375 px, « Voir les films » et « Me contacter » sur la 1re ligne, « Chaîne YouTube » sur la 2e. [T]

### 5.4 Barre de 8 onglets de catégories de films, chacun avec une grille de cartes

Choix : pastilles (option A du § 2.4) qui passent à la ligne au mobile, inspirées des `.pd-filtre` de la maquette. Chaque onglet contient le texte de la catégorie puis une rangée de 4 colonnes (2 en tablette, 1 au mobile) de cartes `article`. Chaque carte contient sa durée, son titre `h3`, sa description et un groupe de boutons contour, avec un bouton par lien du film.

**Bloc `kadence/tabs` (attributs exacts testés, les 8 titres compris) :**

```json
{"name":"kadence/tabs","attributes":{
  "uniqueID":"mo-onglets",
  "tabCount":8,
  "startTab":1,
  "layout":"tabs",
  "tabletLayout":"inherit",
  "mobileLayout":"inherit",
  "tabAlignment":"left",
  "titles":[
   {"text":"Documentaires","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-documentaires"},
   {"text":"Pour le 1er RCP","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-1er-rcp"},
   {"text":"Mémoire","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-memoire"},
   {"text":"Série Serval","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-serval"},
   {"text":"Entreprises et institutions","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-entreprises"},
   {"text":"Salons et défense","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-salons"},
   {"text":"Entretiens","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-entretiens"},
   {"text":"Clips et créations","icon":"","iconSide":"right","onlyIcon":false,"subText":"","anchor":"films-clips"}],
  "titleColor":"#a9b6c0",
  "titleColorHover":"#e8e6e1",
  "titleColorActive":"#0d1217",
  "titleBg":"transparent",
  "titleBgHover":"transparent",
  "titleBgActive":"#e8e6e1",
  "titleBorder":"#2c3a49",
  "titleBorderHover":"#a9b6c0",
  "titleBorderActive":"#e8e6e1",
  "titleBorderWidth":[1,1,1,1],
  "titleBorderWidthUnit":"px",
  "titleBorderRadius":[999,999,999,999],
  "titleBorderRadiusUnit":"px",
  "titlePadding":[0.5,1,0.5,1],
  "titlePaddingUnit":"rem",
  "titleMargin":[0,8,8,0],
  "titleMarginUnit":"px",
  "size":"0.85",
  "sizeType":"rem",
  "lineHeight":1.4,
  "lineType":"",
  "fontWeight":"500",
  "contentBorderStyles":[{"top":["","",0],"right":["","",0],"bottom":["","",0],"left":["","",0],"unit":"px"}],
  "innerPadding":[24,0,0,0],
  "innerPaddingType":"px"
 },"innerBlocks":[ ONGLET_1, ONGLET_2, …, ONGLET_8 ]}
```

**Un onglet (`ONGLET_1`), avec la première carte complète** (les autres cartes ont la même forme ; seuls `uniqueID`, le contenu et les liens changent) :

```json
{"name":"kadence/tab","attributes":{"id":1,"uniqueID":"mo-onglets-1"},"innerBlocks":[
  {"name":"core/paragraph","attributes":{"content":"Des films d'auteur diffusés ou prêts pour la télévision."}},
  {"name":"kadence/rowlayout","attributes":{
    "uniqueID":"mo-onglets-g1","kbVersion":2,"columns":4,"colLayout":"equal",
    "tabletLayout":"two-grid","mobileLayout":"row",
    "columnGutter":"custom","tabletGutter":"custom","mobileGutter":"custom","customGutter":[20,16,16],
    "collapseGutter":"custom","tabletRowGutter":"custom","mobileRowGutter":"custom","customRowGutter":[32,24,16],
    "columnsInnerHeight":true,"padding":["","","",""]
   },"innerBlocks":[
    {"name":"kadence/column","attributes":{
      "uniqueID":"mo-onglets-g1-c1","kbVersion":2,"htmlTag":"article","borderWidth":["","","",""],
      "background":"#17202a","padding":[20,20,20,20],
      "borderStyle":[{"top":["#2c3a49","solid",1],"right":["#2c3a49","solid",1],"bottom":["#2c3a49","solid",1],"left":["#2c3a49","solid",1],"unit":"px"}],
      "borderRadius":[2,2,2,2]
     },"innerBlocks":[
      {"name":"core/paragraph","attributes":{"content":"52:21"}},
      {"name":"core/heading","attributes":{"level":3,"content":"Chroniques du 93"}},
      {"name":"core/paragraph","attributes":{"content":"Pour France 4 · 2010 · immersion dans la CSI 93, en Seine-Saint-Denis"}},
      {"name":"kadence/advancedbtn","attributes":{"uniqueID":"mo-onglets-g1-c1-b","hAlign":"left","gap":[0.5,"",""],"gapUnit":"rem"},"innerBlocks":[
        {"name":"kadence/singlebtn","attributes":{
          "uniqueID":"mo-onglets-g1-c1-bt1","text":"Voir sur YouTube","link":"https://www.youtube.com/watch?v=c4xGjV6-sNg",
          "inheritStyles":"outline","color":"#e8e6e1","background":"transparent","colorHover":"#0d1217","backgroundHover":"#e8e6e1",
          "borderStyle":[{"top":["#a9b6c0","solid",1],"right":["#a9b6c0","solid",1],"bottom":["#a9b6c0","solid",1],"left":["#a9b6c0","solid",1],"unit":"px"}],
          "borderHoverStyle":[{"top":["#e8e6e1","solid",1],"right":["#e8e6e1","solid",1],"bottom":["#e8e6e1","solid",1],"left":["#e8e6e1","solid",1],"unit":"px"}],
          "borderRadius":[2,2,2,2],"borderRadiusUnit":"px","padding":[0.5,1,0.5,1],"paddingUnit":"rem",
          "typography":[{"size":[0.85,"",""],"sizeType":"rem","lineHeight":[1.2,"",""],"lineType":"","letterSpacing":[0.04,"",""],"letterType":"em","textTransform":"","family":"","google":false,"style":"","weight":"500","variant":"","subset":"","loadGoogle":false}],
          "target":"_blank"}}
      ]}
    ]},
    "… cartes 2 à 4 (et suivantes) …"
  ]}
]}
```

Les chaînes `"…"` ne sont pas des blocs : l'outil échouerait dessus. La spec testée était complète : 8 onglets, 46 cartes et 61 boutons de carte, générés par le code ci-dessous à partir de `contenu/site.json`.

**Colonne vide quand une catégorie a moins de 4 films.** Si une rangée a moins d'enfants que `columns`, l'éditeur **ajoute de lui-même** des colonnes vides (`{"id":4,…}`) à l'enregistrement. Constaté sur les catégories « Série Serval » et « Entretiens », qui ont 3 films. Le générateur les ajoute donc d'emblée, pour que la spec et le contenu enregistré restent identiques :

```json
{"name":"kadence/column","attributes":{"uniqueID":"mo-onglets-g4-v1","kbVersion":2,"borderWidth":["","","",""]}}
```

Au-delà de 4 films, la grille passe simplement à la ligne : 11 cartes donnent 4 + 4 + 3. Aucune colonne n'est ajoutée. [T]

**Générateur Python testé** (le code qui a produit `06-modeles`) :

```python
def bordure(couleur, epaisseur=1, style="solid"):
    cote = [couleur, style, epaisseur]
    return [{"top": cote, "right": cote, "bottom": cote, "left": cote, "unit": "px"}]

TYPO_BOUTON = [{"size": [0.95, "", ""], "sizeType": "rem", "lineHeight": [1.2, "", ""], "lineType": "",
                "letterSpacing": [0.04, "", ""], "letterType": "em", "textTransform": "", "family": "",
                "google": False, "style": "", "weight": "500", "variant": "", "subset": "", "loadGoogle": False}]

def bouton_plein(uid, texte, lien, **autres):
    a = {"uniqueID": uid, "text": texte, "link": lien,
         "color": "#ece8df", "background": "#a3302f", "colorHover": "#ece8df", "backgroundHover": "#c0403d",
         "borderStyle": bordure("#a3302f"), "borderHoverStyle": bordure("#c0403d"),
         "borderRadius": [2, 2, 2, 2], "borderRadiusUnit": "px",
         "padding": [0.9, 1.5, 0.9, 1.5], "paddingUnit": "rem", "typography": TYPO_BOUTON}
    a.update(autres)
    return {"name": "kadence/singlebtn", "attributes": a}

def bouton_contour(uid, texte, lien, **autres):
    a = {"uniqueID": uid, "text": texte, "link": lien, "inheritStyles": "outline",
         "color": "#e8e6e1", "background": "transparent", "colorHover": "#0d1217", "backgroundHover": "#e8e6e1",
         "borderStyle": bordure("#a9b6c0"), "borderHoverStyle": bordure("#e8e6e1"),
         "borderRadius": [2, 2, 2, 2], "borderRadiusUnit": "px",
         "padding": [0.9, 1.5, 0.9, 1.5], "paddingUnit": "rem", "typography": TYPO_BOUTON}
    a.update(autres)
    return {"name": "kadence/singlebtn", "attributes": a}

def groupe_boutons(uid, boutons, **autres):
    a = {"uniqueID": uid, "hAlign": "left", "gap": [0.9, "", ""], "gapUnit": "rem"}
    a.update(autres)
    return {"name": "kadence/advancedbtn", "attributes": a, "innerBlocks": boutons}

def carte_film(uid, film):
    """film : {"duree", "titre", "description", "liens": [{"texte", "url"}]}"""
    contenu = [
        {"name": "core/paragraph", "attributes": {"content": film["duree"]}},
        {"name": "core/heading", "attributes": {"level": 3, "content": film["titre"]}},
        {"name": "core/paragraph", "attributes": {"content": film["description"]}}]
    if film["liens"]:  # un groupe de boutons vide serait supprimé par l'éditeur
        contenu.append(groupe_boutons(uid + "-b", [
            bouton_contour("%s-bt%d" % (uid, k + 1), lien["texte"], lien["url"], target="_blank",
                           padding=[0.5, 1, 0.5, 1], typography=[dict(TYPO_BOUTON[0], size=[0.85, "", ""])])
            for k, lien in enumerate(film["liens"])], gap=[0.5, "", ""]))
    return {"name": "kadence/column", "attributes": {
                "uniqueID": uid, "kbVersion": 2, "htmlTag": "article", "borderWidth": ["", "", "", ""],
                "background": "#17202a", "padding": [20, 20, 20, 20],
                "borderStyle": bordure("#2c3a49"), "borderRadius": [2, 2, 2, 2]},
            "innerBlocks": contenu}

def grille_films(uid, films):
    return {"name": "kadence/rowlayout", "attributes": {
                "uniqueID": uid, "kbVersion": 2, "columns": 4, "colLayout": "equal",
                "tabletLayout": "two-grid", "mobileLayout": "row",
                "columnGutter": "custom", "tabletGutter": "custom", "mobileGutter": "custom", "customGutter": [20, 16, 16],
                "collapseGutter": "custom", "tabletRowGutter": "custom", "mobileRowGutter": "custom", "customRowGutter": [32, 24, 16],
                "columnsInnerHeight": True, "padding": ["", "", "", ""]},
            "innerBlocks": [carte_film("%s-c%d" % (uid, i + 1), f) for i, f in enumerate(films)]
                           # moins de 4 films : l'éditeur ajouterait une colonne vide ; on la met d'emblée
                           + [{"name": "kadence/column", "attributes": {"uniqueID": "%s-v%d" % (uid, j + 1), "kbVersion": 2,
                                                                         "borderWidth": ["", "", "", ""]}}
                              for j in range(4 - len(films))]}

def onglets_films(uid, categories):
    """categories : [{"titre", "ancre", "texte", "films": [...]}] ; tabCount, titres et panneaux restent cohérents."""
    return {"name": "kadence/tabs", "attributes": {
                "uniqueID": uid, "tabCount": len(categories), "startTab": 1,
                "layout": "tabs", "tabletLayout": "inherit", "mobileLayout": "inherit", "tabAlignment": "left",
                "titles": [{"text": c["titre"], "icon": "", "iconSide": "right", "onlyIcon": False,
                            "subText": "", "anchor": c["ancre"]} for c in categories],
                "titleColor": "#a9b6c0", "titleColorHover": "#e8e6e1", "titleColorActive": "#0d1217",
                "titleBg": "transparent", "titleBgHover": "transparent", "titleBgActive": "#e8e6e1",
                "titleBorder": "#2c3a49", "titleBorderHover": "#a9b6c0", "titleBorderActive": "#e8e6e1",
                "titleBorderWidth": [1, 1, 1, 1], "titleBorderWidthUnit": "px",
                "titleBorderRadius": [999, 999, 999, 999], "titleBorderRadiusUnit": "px",
                "titlePadding": [0.5, 1, 0.5, 1], "titlePaddingUnit": "rem",
                "titleMargin": [0, 8, 8, 0], "titleMarginUnit": "px",
                "size": "0.85", "sizeType": "rem", "lineHeight": 1.4, "lineType": "", "fontWeight": "500",
                "contentBorderStyles": [{"top": ["", "", 0], "right": ["", "", 0], "bottom": ["", "", 0], "left": ["", "", 0], "unit": "px"}],
                "innerPadding": [24, 0, 0, 0], "innerPaddingType": "px"},
            "innerBlocks": [{"name": "kadence/tab", "attributes": {"id": i + 1, "uniqueID": "%s-%d" % (uid, i + 1)},
                             "innerBlocks": [{"name": "core/paragraph", "attributes": {"content": c["texte"]}},
                                             grille_films("%s-g%d" % (uid, i + 1), c["films"])]}
                            for i, c in enumerate(categories)]}
```

Préparation des données utilisée pour le test, depuis `contenu/site.json` (`films.groupes`). Un film a soit `youtube`/`url`, soit une liste `liens` (Instagram, Facebook, X…), soit aucun lien :

```python
ancres = {"doc": "films-documentaires", "rcp": "films-1er-rcp", "memoire": "films-memoire", "serval": "films-serval",
          "entreprise": "films-entreprises", "salon": "films-salons", "entretien": "films-entretiens", "clip": "films-clips"}
for g in site["films"]["groupes"]:
    for f in g["films"]:
        if f.get("youtube") or f.get("url"):
            liens = [{"texte": "Voir sur YouTube", "url": f.get("youtube") or f.get("url")}]
        else:
            liens = [{"texte": "Voir sur " + l["reseau"], "url": l["url"]} for l in f.get("liens", [])]
```

Mesures sur `06-modeles` [T] :

| Largeur | Barre de titres | Grille de l'onglet actif |
|---|---|---|
| 1280 px | 8 pastilles sur 1 ligne (1088 × 45 px) | 4 × 257 px, gouttière de 20 px, cartes de même hauteur (355 px) |
| 900 px | 2 lignes (6 + 2) | 2 × 410 px, gouttière de 16 px, 24 px entre les lignes |
| 375 px | 5 lignes | 1 × 311 px, 16 px entre les cartes |

Autres constats :
- pastille active : fond `rgb(232,230,225)`, texte `rgb(13,18,23)` ; pastille inactive : texte `rgb(169,182,192)`, bordure `rgb(44,58,73)` ; au survol : texte `rgb(232,230,225)`, bordure `rgb(169,182,192)`. Police de 13,6 px, graisse 500, interligne de 19,04 px, padding `8px 16px`, rayon de 999 px ;
- panneaux : aucune bordure, 24 px au-dessus de la grille ;
- `…/ref-boutons-onglets-navigation-06-modeles/#films-serval` à 375 px ouvre l'onglet 4 ;
- carte avec deux liens (Instagram et Facebook) : boutons empilés à 1280 (carte étroite), côte à côte à 900, empilés à 375.

### 5.5 FAQ en accordéon (style sombre)

Spec testée sur `03-accordeon`. Les attributs `titleStyles` sont recopiés en entier, car le tableau contient un seul objet :

```json
{"name":"kadence/accordion","attributes":{
  "uniqueID":"pd-faq","paneCount":3,"openPane":0,"startCollapsed":true,"linkPaneCollapse":true,"faqSchema":true,
  "titleStyles":[{"size":[1.15,"",""],"sizeType":"rem","lineHeight":[1.3,"",""],"lineType":"","letterSpacing":"","family":"Newsreader","google":false,"style":"","weight":"400","variant":"","subset":"","loadGoogle":false,"padding":[16,0,16,0],"marginTop":0,"color":"#e8e6e1","background":"transparent","border":["","","",""],"borderRadius":["","","",""],"borderWidth":["","","",""],"colorHover":"#c8b287","backgroundHover":"transparent","borderHover":["","","",""],"colorActive":"#c8b287","backgroundActive":"transparent","borderActive":["","","",""],"textTransform":"","paddingTablet":["","","",""],"paddingMobile":["","","",""],"paddingType":"px"}],
  "titleBorder":[{"top":["","",""],"right":["","",""],"bottom":["#2c3a49","solid",1],"left":["","",""],"unit":"px"}],
  "titleBorderHover":[{"top":["","",""],"right":["","",""],"bottom":["#a9b6c0","solid",1],"left":["","",""],"unit":"px"}],
  "titleBorderActive":[{"top":["","",""],"right":["","",""],"bottom":["#c8b287","solid",1],"left":["","",""],"unit":"px"}],
  "contentBorderStyle":[{"top":["","",0],"right":["","",0],"bottom":["","",0],"left":["","",0],"unit":"px"}],
  "contentPadding":[16,0,24,0],"contentPaddingType":"px","contentBgColor":"","textColor":"#a9b6c0",
  "iconStyle":"arrow","iconSide":"right","iconColor":{"standard":"#a9b6c0","active":"#c8b287","hover":"#c8b287"}
 },"innerBlocks":[
  {"name":"kadence/pane","attributes":{"id":1,"uniqueID":"pd-faq-p1","title":"Quels formats réalisez-vous ?","titleTag":"h3","anchor":"faq-formats"},
   "innerBlocks":[{"name":"core/paragraph","attributes":{"content":"Documentaires de 52 minutes, films institutionnels, clips."}}]},
  {"name":"kadence/pane","attributes":{"id":2,"uniqueID":"pd-faq-p2","title":"Travaillez-vous pour les entreprises ?","titleTag":"h3","anchor":"faq-entreprises"},
   "innerBlocks":[{"name":"core/paragraph","attributes":{"content":"Oui, pour des entreprises et des institutions."}}]},
  {"name":"kadence/pane","attributes":{"id":3,"uniqueID":"pd-faq-p3","title":"Comment vous contacter ?","titleTag":"h3","anchor":"faq-contact"},
   "innerBlocks":[{"name":"core/paragraph","attributes":{"content":"Par le <a href=\"#section-contact\">formulaire de contact</a> en bas de page."}}]}
 ]}
```

Mesuré :
- titre au repos : `rgb(232,230,225)`, Newsreader 18,4 px, padding `16px 0`, filet bas `1px solid rgb(44,58,73)` ;
- titre ouvert : `rgb(200,178,135)`, filet de la même couleur ;
- un seul volet ouvert à la fois ;
- JSON-LD `FAQPage` présent dans `<head>`. [T]

`"family":"Newsreader"` fonctionne parce que le thème enfant charge la police localement (`fonts.css`) ; `google:false` évite tout appel à Google.

### 5.6 Barre de liens internes (ancres)

Testée sur `04-ancres` :

```json
{"name":"kadence/advancedbtn","attributes":{"uniqueID":"an-nav","hAlign":"left","anchor":"barre-liens"},"innerBlocks":[
  {"name":"kadence/singlebtn","attributes":{"uniqueID":"an-b1","text":"Section contact","link":"#section-contact","color":"#ece8df","background":"#a3302f","backgroundHover":"#c0403d","anchor":"bouton-contact"}},
  {"name":"kadence/singlebtn","attributes":{"uniqueID":"an-b2","text":"Onglet Entretiens (même page)","link":"#films-entretiens","color":"#ece8df","background":"#a3302f","backgroundHover":"#c0403d"}},
  {"name":"kadence/singlebtn","attributes":{"uniqueID":"an-b3","text":"Serval (autre page)","link":"/ref-boutons-onglets-navigation-02-onglets/#films-serval","color":"#ece8df","background":"#a3302f","backgroundHover":"#c0403d"}},
  {"name":"kadence/singlebtn","attributes":{"uniqueID":"an-b4","text":"Ancre colonne","link":"#colonne-cible","color":"#ece8df","background":"#a3302f","backgroundHover":"#c0403d"}}
]}
```

Cibles : une rangée `{"anchor":"section-contact"}`, une colonne `{"anchor":"colonne-cible"}`, et des titres d'onglets `{"anchor":"films-entretiens"}`. Les résultats sont au § 4.

---

## 6. Pièges constatés (résumé)

| # | Piège | Conséquence | Parade | Vérif. |
|---|---|---|---|---|
| 1 | `kadence/singlebtn` sans `uniqueID` | bouton absent de la page | `uniqueID` sur chaque bloc | T |
| 2 | Bouton hors `kadence/advancedbtn` | aucun style appliqué | toujours dans un groupe | T |
| 3 | Groupe de boutons sans enfant | supprimé par l'éditeur | ne pas l'émettre | T |
| 4 | `tabCount` inférieur au nombre de `kadence/tab` | **panneaux en trop supprimés avec leur contenu** | `tabCount = len(titles) = nb d'enfants` | T |
| 5 | `kadence/tab` sans `id` | un seul onglet reste visible | `id` de 1 à n | T |
| 6 | `lineHeight` des onglets sans `lineType:""` | `line-height:1.4px`, titres écrasés | `"lineType":""` | T |
| 7 | `titleBgActive` absent | fond blanc sur l'onglet actif | le renseigner | T |
| 8 | `contentBorder` (ancien) sur les onglets | converti par l'éditeur | `contentBorderStyles` directement | T |
| 9 | Onglets `contentBorderStyles` / accordéon `contentBorderStyle` | un « s » de différence | respecter chaque nom | T |
| 10 | Titre d'onglet sans `anchor` | id du type `tab-mmoire` (accents supprimés) | `anchor` explicite | T |
| 11 | Mauvais type (`"2"` au lieu de `2`, `size` en nombre…) | bloc invalide à la réouverture | types du block.json (§ 0, règle 4) | T |
| 12 | `link:"films/"` | `href="http://films/"` | `"/films/"` | T |
| 13 | Typographie sur le groupe (`textTransform`, `fontWeight`, `typography`) | sans effet | la mettre sur chaque bouton | T |
| 14 | `typography.style:"italic"` sans `family` | italique ignoré | renseigner `family` | T (contre-vérification : `font-style:normal` mesuré) |
| 15 | Couleurs Kadence par défaut (bleu, blanc) | boutons, onglets et accordéon non assortis au site sombre | toujours fixer les couleurs | T |
| 16 | Reconstruction d'une page existante | `uniqueID` parfois régénérés (`<idPage>_<hash>`) | ne pas cibler les ID ; page neuve pour garder les ID | T |
| 17 | Rangée avec moins de colonnes enfants que `columns` | l'éditeur ajoute des colonnes vides | les ajouter soi-même, ou ajuster `columns` | T |
| 18 | Clic sur un onglet | l'URL ne change pas | lier les catégories avec `#anchor` | T |
| 19 | `currentTab` seul | l'onglet ouvert dépend de la dernière édition | `startTab` | T |
| 20 | Onglets en accordéon sans `linkPaneCollapse` | plusieurs panneaux ouverts | `linkPaneCollapse:true` si un seul voulu | T |
| 21 | `borderHoverRadius` du bouton | toujours en px (`borderHoverRadiusUnit:"%"` donne `10px`) | utiliser `borderRadius` | T |
| 22 | Onglets `widthType:"percent"` sans `titleMargin` | la marge de 4 px de la feuille de base casse la grille : 3 titres par ligne au lieu de 4, et 1 au lieu de 2 au mobile | `titleMargin:[0,0,8,0]` (toute valeur différente du défaut) | T |
| 23 | `"hAlign":"space-between"` avec `orientation` en `column` | devient `align-items:center` | choisir `left`, `center` ou `right` en colonne | T |

---

## 7. Ce qui n'a PAS été vérifié par un essai

- **Boutons** :
  - `tooltip`, `tooltipPlacement`, `iconReveal`, `iconPadding`, `iconTitle`, `onlyText` ;
  - texte en dégradé (`textBackgroundType`), survol en dégradé (`backgroundHoverType:"gradient"`, `gradientHover`), ombre au survol (`displayHoverShadow`) ;
  - `target:"video"` (visionneuse), `isSubmit`, `inheritStyles:"inherit"` et `"inherit-secondary"` ;
  - bordures et rayons par palier hors `mobileBorderRadius` (`tabletBorderStyle`, `mobileBorderStyle`…) ; `borderHoverRadius` n'a été vérifié que dans le CSS produit (contre-vérification), pas au survol réel ;
  - unités `em` et `vw` pour la largeur ; variantes transparent et sticky ; codes courts dans `link` ;
  - un vrai fichier en téléchargement : l'attribut `download` est bien produit, mais `/wp-content/uploads/dossier.pdf` n'existe pas.
- **Groupe de boutons** : `tvAlign`, `mvAlign`, `orientation` en `row-reverse` ou `column-reverse`, marges tablette, jetons de `gap` autres que `sm` (CSS lu dans le code).
- **Onglets** :
  - icônes dans les titres (`titles[].icon`, `iSize`, `onlyIcon`), `subtitleFont`, `tabLineHeight`, `mobileLineHeight`, `fontStyle`, `contentBorderRadius` ;
  - bordures de panneau par palier, bordures, rayons et marges de titre par palier (seul le padding par palier est testé) ;
  - `blockAlignment` `wide`, `full` ou `center` ;
  - navigation au clavier (flèches), onglets imbriqués dans des onglets, décalage sous un en-tête collant ;
  - chargement des images (`core/image`) placées dans des onglets masqués : l'image de test n'apparaît pas sur la capture pleine page à 375 px. Le chargement différé n'a pas été étudié.
- **Accordéon** :
  - rendu des styles d'icône autres que `arrow` et `basic`, et couleur effective de `iconColor` (le CSS est produit, non mesuré) ;
  - `columnLayout`, `columnGap`, `titleAlignment`, `maxWidth`, `contentBgColor`, `linkColor`, `titleBorderRadius` ;
  - `paneCount` différent du nombre de volets ; `titleTag` autre que `h3` et `div` ; `icon`, `hideLabel` et `ariaLabel` des volets.
- **Éditeur** : affichage dans l'inspecteur des valeurs absentes de l'interface (`gapUnit:"rem"`, `titlePaddingUnit:"rem"`, couleurs `var(--…)`). Réouverts dans l'éditeur, les blocs ne montrent aucune modification d'attribut, et la sélection des 60 premiers blocs Kadence de `06-modeles` ne déclenche ni avertissement ni plantage. Le rendu visuel de l'éditeur n'a pas été contrôlé.
- **Référencement réel** : la présence du contenu dans le HTML est vérifiée (§ 2.2) ; la façon dont un moteur de recherche pondère un contenu masqué ne l'est pas.

---

## 8. Pages d'essai (WordPress de test, `http://127.0.0.1:8080/`)

| Page | Ce qu'elle montre |
|---|---|
| `ref-boutons-onglets-navigation-00-ids` | bouton et onglets **sans** `uniqueID` (bouton absent, onglets sans CSS) |
| `ref-boutons-onglets-navigation-01-boutons` | G1 plein et contour ; G2 attributs de lien ; G3 tailles et typographie ; G4 largeurs ; G5 alignements et orientation ; G6 huit boutons qui passent à la ligne ; G7 icônes, ombre, marges, rayon et padding par palier ; ancre `#ancre-bas` |
| `ref-boutons-onglets-navigation-02-onglets` | T1 : 8 onglets avec les 46 films ; T2 : titres en colonnes (`percent`, `startTab:3`) ; T3 : accordéon au mobile et ID automatiques ; T4 : onglets verticaux au style par défaut |
| `ref-boutons-onglets-navigation-03-accordeon` | FAQ sombre (`faqSchema`, `h3`, un seul volet ouvert) et accordéon au style par défaut |
| `ref-boutons-onglets-navigation-04-ancres` | ancres sur rangée, colonne, groupe, bouton, onglets ; liens vers un onglet de la même page et d'une autre page |
| `ref-boutons-onglets-navigation-05-pieges` | écarts `tabCount`, `tab` sans `id`, `currentTab`, `lineHeight` sans `lineType`, bouton hors groupe, couleurs `paletteN` et `var()`, `tel:`, `mailto:`, lien relatif cassé, dégradé |
| `ref-boutons-onglets-navigation-06-modeles` | les modèles du § 5 (boutons et 8 onglets avec toutes les cartes), page neuve |
| `ref-boutons-onglets-navigation-07-complements` | onglets centrés ou alignés à droite, `maxWidth`, `minHeight`, fond, typographie et padding par palier, sous-titres ; bouton icône seule, `className`, `buttonRole`, `anchor` |
| `ref-boutons-onglets-navigation-08-anciens-attributs` | typographie sur le groupe sans effet |
| `ref-boutons-onglets-navigation-09-types` | mauvais types → blocs invalides (contient **volontairement** des blocs invalides) |

Pour revérifier :
1. `node outils/wp-test/editeur.js construire spec.json`, puis lire `erreurs` (blocs invalides) ;
2. `php outils/wp-test/lire.php <wp> <slug>`, pour voir les attributs réellement enregistrés : comparer les `uniqueID`, et vérifier qu'aucun enfant n'a été ajouté ni supprimé ;
3. `curl -s http://127.0.0.1:8080/<slug>/`, pour lire le CSS dans `<style id="kadence_blocks_css-inline-css">` et le HTML des boutons et des onglets ;
4. `node outils/wp-test/editeur.js capture <slug> sortie.png 375`, pour contrôler le débordement horizontal et les erreurs JS.

Les scripts de mesure utilisés (survol, état des onglets, clics d'ancre, réouverture de l'éditeur sans enregistrement, générateur `modeles.py`) sont dans le dossier temporaire de la session, `scratchpad/ref/boutons-onglets-navigation/`. Ils ne sont pas conservés dans le dépôt.

---

## Contre-vérification (7 octobre 2026)

Relecture sceptique. Les affirmations clés ont été confrontées au code source (`dist/blocks/{advancedbtn,singlebtn,tabs,tabs/tab,accordion,accordion/pane}/block.json`, `includes/blocks/class-kadence-blocks-{advancedbtn,singlebtn,tabs,accordion,abstract}-block.php`, `includes/class-kadence-blocks-css.php`, `dist/style-blocks-{advancedbtn,tabs}.css`, `dist/blocks-tabs.js`, `includes/assets/js/kt-tabs.min.js`), puis rejouées avec l'outil sur des pages **neuves**. Les scripts et les specs sont dans `scratchpad/ref/boutons-onglets-navigation-verif/` (non conservés dans le dépôt).

### Specs rejouées

| Page `ref-boutons-onglets-navigation-…` | Contenu rejoué | Résultat |
|---|---|---|
| `verif-boutons` | § 5.1, 5.2 et 5.3 **recopiés tels quels** (groupe plein + contour + YouTube) ; bouton du § 1.3 ; extrait du § 1.5 ; les 4 exemples de groupe du § 1.2 ; barre d'ancres du § 5.6 et ses cibles ; sondes : `link:"#"`, `noFollow` seul, `link:"films/"`, italique sans `family`, `size:["md"…]`, `borderHoverRadius` en `%`, `widthType:"fixed"`, icône seule, `space-between` en colonne | 0 bloc invalide, ID conservés (34/34), aucune erreur JS, aucun débordement. **Toutes les mesures des § 1 et 5.1 à 5.3 se retrouvent à l'identique** : 146 × 49 et 148 × 49 px, `14.4px 24px`, 15,2 px, graisse 500, 0,608 px, 18,24 px, survols ; droite / centre / gauche ; empilement centré à 375 px ; gouttières de 12, 10 et 8 px ; marges de 32 puis 8 px ; rayon de 999 px puis 0 ; ombre ; largeurs de 240, 200 et 160 px ; `rel`, `role`, `aria-label` et `http://films/` conformes. Les ancres des § 4 et 5.6 défilent jusqu'à la cible à 1280 et 375 px, et ouvrent l'onglet Serval d'une autre page. |
| `verif-onglets` | Bloc `kadence/tabs` du § 5.4 **extrait du Markdown** ; `ONGLET_1` extrait tel quel ; onglets 2 à 8 produits par le **générateur Python du § 5.4 exécuté tel qu'il est écrit** (8 catégories, 18 cartes, catégories de 0 à 5 films, film sans lien) ; variantes : options B et C, `lineHeight` sans `lineType`, `currentTab` seul, typographie et panneaux par palier (§ 2.6 et 2.7), titres sans `anchor`, `vtabs` | Les attributs JSON du § 5.4 et ceux du générateur sont identiques. 0 bloc invalide, 120 ID sur 120 conservés, aucune colonne ajoutée par l'éditeur (le générateur complète bien les rangées) et aucun groupe vide. Confirmé : couleurs et tailles des pastilles (13,6 px, 19,04 px, `8px 16px`, 999 px) ; panneaux sans bordure, padding de 24 px ; `#films-serval` et `hashchange` ; le clic ne change pas l'URL ; sans JS, les 8 panneaux sont visibles ; rôles ARIA ; `lineHeight` seul donne `1.4px` (liste de 17 px) et fond actif `#ffffff` ; `currentTab:2` ouvre l'onglet 2 ; 18/16/13 px, padding, `minHeight` 200/150/100, `innerPadding` 32/24/12, `maxWidth` 600 centré ; `tab-mmoire`, `tab-pourle1errcp`, `tab-clipscrations` ; `verticalTabWidth:["25"…]` donne 25 % ; option C conforme, avec un seul panneau ouvert. **Écarts** : option B (voir corrections) ; option A, 4 lignes au lieu de 5 à 375 px en pleine largeur (écart dû au conteneur). |
| `verif-accordeon` | § 5.5 **extrait du Markdown tel quel** ; 2e accordéon `openPane:1`, `linkPaneCollapse:false`, `xclosecircle`, `titleTag:"h2"` | 0 bloc invalide. Confirmé à 1280 et 375 px : tout est fermé au départ (`data-start-open="none"`) ; un seul volet ouvert à la fois ; titre `rgb(232,230,225)` en Newsreader 18,4 px, padding `16px 0`, filet `1px solid rgb(44,58,73)` ; titre ouvert `rgb(200,178,135)` ; texte `rgb(169,182,192)` ; 3 `<h3>` ; JSON-LD `FAQPage` dans `<head>`. `openPane:1` ouvre bien le 2e volet (`data-start-open="1"`), et `linkPaneCollapse:false` permet deux volets ouverts. Style par défaut : `rgb(74,85,104)` sur `rgb(247,250,252)`. |
| `verif-pieges` | `tabCount:2` avec 3 `kadence/tab` ; `kadence/tab` sans `id` ; option B avec et sans `titleMargin` ; bouton sans `uniqueID` dans un groupe qui en a un | 3e panneau **supprimé** à l'enregistrement (confirmé) ; sans `id`, 3 × `kt-inner-tab-1` et un seul titre (confirmé) ; option B, voir corrections. Le bouton sans ID a reçu `163_6eed5b-60` et s'affiche (voir corrections). |
| `verif-types` | `"startTab":"2"` (chaîne) | bloc `kadence/tabs` **invalide** à la relecture (confirmé) |
| `verif-ids` | reprise du cas `00-ids` (groupe et bouton sans ID, groupe avec ID mais bouton sans ID, onglets sans ID) | les boutons restent sans ID ; groupes vides en public (`<div … kb-buttons-wrap"></div>`) ; onglets en `kt-tabs-idnotset` (confirmé) |
| `verif-boutons`, reconstruit 2 fois | règle 3 du § 0 | 1re reconstruction : **33 ID sur 34 régénérés** (`145_2e761f-88`…) ; 2e : 34 sur 34 conservés. L'avertissement est confirmé : la régénération est aléatoire. |

### Vérifié dans le code (sans écart)

Noms, types et défauts de tous les attributs des tableaux des § 1 à 3 (block.json) ; absence de `kbVersion` ; format non standard de `margin` sur le groupe (`desk`/`tablet`/`mobile`, unité via `marginUnit`) ; jetons de `gap` (valeurs exactes) et de taille de police ; correspondance `hAlign`/`vAlign` et `flex-*` ; `rel`, `role`, `download`, `do_shortcode`, `esc_url` ; `style` de la typographie écrit seulement si `family` est renseigné ; `borderHoverRadius` sans unité ; `titleBgActive` vide remplacé par `#ffffff` ; `lineType` absent remplacé par `px` ; `typography` des onglets écrit sans apostrophes ; règle de formation des identifiants de titre (`toLowerCase().replace(/[^0-9a-z-]/g,"")`) ; `contentPadding` / `contentTabletPadding` / `contentMobilePadding` (accordéon) ; classes `kt-accodion-icon-style-*` ; feuilles de base (bouton : 1,125 rem, `.4em 1em`, 3 px, `transition: all .3s` ; tailles 0,9 / 1,35 / 1,65 rem ; titres d'onglet : `8px 16px`, `1px 1px 0 1px`, 4 px ; panneau : 1 px `#dee2e6`, 20 px) ; media query tablette `(min-width: 767px) and (max-width: 1024px)` dans `style-blocks-tabs.css` ; flèches 37/39, `hashchange` et `display:none` en ligne dans `kt-tabs.min.js`.

### Corrections apportées à la fiche

1. **§ 0, règle 1** : l'éditeur peut générer et enregistrer un `uniqueID` dès le premier enregistrement (`verif-pieges`), mais pas toujours (`verif-ids`, `00-ids`). Ajout de la mention « non systématique ». La règle « toujours fournir `uniqueID` » est inchangée.
2. **§ 0, règle 6** : « tous les sélecteurs » était trop fort. Les sélecteurs de l'icône et de `onlyIcon` ne commencent pas par `.wp-block-kadence-advancedbtn`.
3. **§ 2.4, option B** : la spec indiquée (`widthType`, `tabWidth`, `gutter`) **ne donnait pas** la grille annoncée. La page d'origine (T2) avait aussi `titleMargin:[0,0,8,0]`. Sans lui : 3 titres par ligne à 1280 px et 1 par ligne à 900 et 375 px. Ajout de l'attribut dans le tableau, d'une explication (marge de 4 px de la feuille de base, forcée à 0 par le PHP seulement si `titleMargin` est enregistré), d'une ligne au § 2.5 et du piège n° 22.
4. **§ 1.2, `orientation`** : en colonne, `hAlign:"space-between"` devient `align-items:center` (code et mesure) ; piège n° 23.
5. **§ 3.2, `title` du volet** : son type est `rich-text`, et non `string`. Il n'est pas enregistré dans le commentaire du bloc, mais relu dans le HTML (constaté dans le contenu enregistré).
6. **§ 2.7, `contentBorderRadius`** : il est toujours en px, car `contentBorderRadiusUnit` n'est pas lu (code seulement).
7. Précisions : mesures du § 2.4 dépendantes du conteneur (4 lignes en pleine largeur à 375 px) ; écart de 14,4 px au § 5.3 ; pièges n° 14 et 21 passés de C à T.

### Toujours non vérifié

Tout ce que liste le § 7 reste non vérifié, sauf `borderHoverRadius`, contrôlé dans le CSS produit seulement (pas au survol réel). La suppression d'un groupe de boutons vide (règle 7 du § 0) n'a pas été rejouée. Le cas « bouton hors groupe » (règle 6) n'a pas été rejoué non plus.
