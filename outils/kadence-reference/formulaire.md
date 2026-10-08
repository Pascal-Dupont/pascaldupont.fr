# Kadence Blocks : formulaire de contact (`kadence/form`, `kadence/advanced-form`) comparé à `[pd_formulaire]`

Fiche de référence pour générer le formulaire de contact du site, soit en spec JSON pour `outils/wp-test/editeur.js`, soit dans le WXR produit par `outils/construire.py`.

- **Environnement d'essai** : WordPress 7.1.3 (fr_FR), thème Kadence 1.5.2 avec le thème enfant `kadence-pascal` (copie identique au dépôt, vérifié avec `diff -r`), Kadence Blocks **3.7.12.1** gratuit (pas de Kadence Blocks Pro), WordPress Importer 0.9.6, base SQLite. Essais du 7 octobre 2026 sur `http://127.0.0.1:8080`.
- **Pas de serveur de courrier** dans l'environnement : `/usr/sbin/sendmail` n'existe pas. Tous les envois réels échouent donc au niveau de `wp_mail()` (« Impossible d'instancier la fonction mail. »). Pour voir le courrier qui serait parti, j'ai exécuté le gestionnaire AJAX de Kadence en ligne de commande, dans WordPress, en interceptant le filtre `wp_mail` (script `mail-cli.php`, voir § 11). Je n'ai rien écrit dans le WordPress : ni extension, ni mu-plugin, ni réglage.
- **Sources lues** :
  - `dist/blocks/form/block.json`, `dist/blocks/advanced-form/block.json` et `dist/blocks/advanced-form/fields/*/block.json` ;
  - rendus PHP `includes/blocks/class-kadence-blocks-form-block.php`, `class-kadence-blocks-advanced-form-block.php` et `includes/blocks/form/*.php` ;
  - traitement des envois `includes/form-ajax.php`, `includes/advanced-form/advanced-form-ajax.php` et `advanced-form-submit-actions.php` ;
  - type de contenu et méta `includes/advanced-form/advanced-form-cpt.php`, captcha `advanced-form-captcha-settings.php` et `advanced-form-captcha-verify.php` ;
  - modèle d'e-mail `includes/templates/form-email.php`, scripts publics `includes/assets/js/kb-advanced-form-block.min.js` et `kb-form-block.min.js`, éditeur `dist/blocks-form.js` et `dist/blocks-advanced-form.js` ;
  - export/import `includes/class-kadence-blocks-cpt-import-export.php`, `wp-admin/includes/export.php`, `wordpress-importer/class-wp-import.php` ;
  - thème enfant `kadence-pascal/functions.php`.
- **Colonne « Vérif. »** :
  - **E** : essai réel. La spec a été construite dans le vrai éditeur, puis j'ai relu le contenu enregistré et contrôlé le rendu public et/ou une soumission réelle (Playwright ou requête HTTP) ;
  - **C** : lu dans le code seulement ;
  - **—** : non vérifié.

---

## 0. En bref

1. Les deux blocs existent dans la version gratuite. **E**
   - `kadence/form` s'appelle « Form » dans l'éditeur. C'est l'ancien bloc. Il est **retiré de l'inserteur** (`supports.inserter: false`) et l'éditeur propose de le transformer en « Form (Adv) ». Il reste rendu et fonctionnel sur les pages qui le contiennent déjà.
   - `kadence/advanced-form` s'appelle « Form (Adv) ». C'est le seul formulaire proposé dans l'inserteur. Son contenu est stocké dans un **type de contenu séparé, `kadence_form`** : les champs sont les blocs internes de ce contenu et les réglages (e-mail, messages…) sont ses **méta `_kad_form_*`**. La page ne contient qu'une référence : `<!-- wp:kadence/advanced-form {"id":64} /-->`.
2. Si l'on veut un bloc Kadence, il faut prendre **`kadence/advanced-form`**. Toutes les exigences du formulaire de contact se règlent avec lui (§ 2 à 4), mais la version gratuite a de vrais défauts :
   - **Aucune protection anti-spam par défaut** : ni pot de miel, ni délai minimal, ni limite d'envois. Une requête HTTP envoyée directement, sans afficher la page, est acceptée. **E**
   - **Un message de succès s'affiche même quand l'e-mail n'est pas parti** : le résultat de `wp_mail()` est ignoré. **E**
   - **Sans JavaScript, le message est perdu sans aucun avertissement.** **E**
   - Quelques messages restent en anglais (§ 4.3).
   - À l'import WXR, le formulaire **disparaît sans erreur** si l'ID du `kadence_form` change (§ 7). **E**
3. **Recommandation : garder `[pd_formulaire]`** (§ 8), avec deux corrections pour coller au cahier des charges :
   - supprimer le minimum de 10 caractères du message ;
   - ajouter une option vide « Choisissez… » à la liste déroulante.

   Notre shortcode est le seul des trois à cumuler pot de miel, délai minimal, limite d'envois, contrôle de la liste côté serveur et signalement d'échec d'envoi : ces cinq points ont été testés (E). Il voyage aussi en WXR sous forme de simple texte (C).

---

## 1. Comparatif

| Critère | `kadence/form` (ancien) | `kadence/advanced-form` | `[pd_formulaire]` (thème enfant) |
|---|---|---|---|
| Proposé dans l'inserteur | non (`inserter: false`) **E** | oui, « Form (Adv) » **E** | via le bloc « Code court » |
| Où vivent champs et réglages | attributs du bloc, dans la page | contenu + méta du post `kadence_form` | code PHP de `functions.php` |
| Génération par script (spec JSON, WXR) | difficile : bloc statique, il faut reproduire exactement le HTML de `save` ; `postID` figé | facile : champs dynamiques (`save` renvoie `null`), mais deux objets liés par un ID | trivial : `[pd_formulaire]` |
| Pot de miel | oui, actif par défaut (`honeyPot`) **E**, mais seulement si le robot envoie le champ **E** | **non** **E** | oui **E** |
| Délai minimal avant envoi | non **C** | non **E** | oui, au moins 3 s (jeton signé, valable 7 jours) **E** |
| Limite d'envois | non **C** | non **C** | 1 message par minute et par IP **E** |
| Captcha | reCAPTCHA v2/v3, clés globales **C** | bloc `kadence/advanced-form-captcha` : Turnstile, reCAPTCHA v2/v3, hCaptcha **E** (affichage et refus) | non |
| Valeur de la liste contrôlée côté serveur | non, une valeur hors liste est acceptée **E** | non, une valeur hors liste est acceptée **E** | oui (`in_array`) **E** |
| Échec de `wp_mail()` signalé au visiteur | **non** (succès affiché) **E** | **non** (succès affiché) **E** | oui (`?envoi=echec`) **E** |
| Fonctionne sans JavaScript | non (message `<noscript>`) **C** | non : la page se recharge, rien n'est envoyé ni signalé **E** | oui (formulaire POST classique) **C** |
| Message sans longueur minimale | oui **E** | oui **E** | **non** : 10 caractères minimum (`minlength` et contrôle serveur) **E** |
| Textes visibles 100 % français | non (§ 4.3) **E** | non (§ 4.3) **E** | oui **C** (libellés vus en page ; messages de retour lus dans le code) |
| En-tête Reply-To | `<e-mail du visiteur>` **E** | `<e-mail du visiteur>` **E** | `Nom <e-mail>` **E** |
| Format du courrier | HTML (modèle Kadence) ou texte **E** | HTML ou texte **E** | texte **E** |
| Transport par WXR | dans la page, mais `postID` figé dans le HTML **E** | page **et** `kadence_form`, ID à conserver **E** | dans la page, texte simple (déjà le cas dans `import/pages.xml`) **C** |
| Enregistrement des messages en base | non **C** | non : « Database Entry » est réservé à Pro **C** | non (transitoire de 60 s par IP) **C** |

---

## 2. `kadence/advanced-form` : fonctionnement

### 2.1 Les deux objets à créer

1. **Le formulaire**, de type `kadence_form`.
   - Type non public : `public: false`, `publicly_queryable: false`, `show_in_rest: true`, base REST `kadence_form`, `can_export: true`. Il apparaît dans le menu Kadence Blocks > Forms. **C**
   - Son `post_content` contient un unique bloc racine `kadence/advanced-form`, avec les champs en blocs internes. **E**

     ```
     <!-- wp:kadence/advanced-form {"uniqueID":"64_3028d6-7d"} -->
     <!-- wp:kadence/advanced-form-text {"uniqueID":"pd-nom","formID":"64","label":"Nom et prénom",...} /-->
     ...
     <!-- wp:kadence/advanced-form-submit {"uniqueID":"pd-envoyer","text":"Envoyer"} /-->
     <!-- /wp:kadence/advanced-form -->
     ```

   - Ses réglages sont dans les méta `_kad_form_*`. Liste au § 3.2.
2. **La page**, qui contient la référence `{"id": <ID du kadence_form>}`.

### 2.2 Bloc placé dans la page

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `id` | integer | ID du post `kadence_form` | `0` | **E** |
| `uniqueID` | string | inutile : le rendu utilise toujours `{id}-cpt-id` comme identifiant (classe `wp-block-kadence-advanced-form64-cpt-id`, `<form id="kb-adv-form-64-cpt-id">`). `"pd-contact"` a été enregistré mais ignoré ; sans `uniqueID`, l'éditeur n'en ajoute pas. | absent | **E** |
| `legacyMigration` | object | interne (transformation depuis `kadence/form`) | `null` | **C** |

Spec testée (page `ref-formulaire-03-captcha`, enregistrée telle quelle : `<!-- wp:kadence/advanced-form {"id":74} /-->`) :

```json
{"titre": "Réf formulaire – captcha", "slug": "ref-formulaire-03-captcha",
 "meta": {"_kad_post_layout": "fullwidth", "_kad_post_content_style": "unboxed", "_kad_post_vertical_padding": "hide", "_kad_post_title": "hide"},
 "blocs": [{"name": "kadence/advanced-form", "attributes": {"id": 74}}]}
```

Mise en page, constatée à la contre-vérification **E** : cette spec, seule dans une page `fullwidth` + `unboxed`, colle le formulaire **aux bords de l'écran**, sans marge latérale, à 1280 comme à 375 px. Pour le vrai site, envelopper le bloc dans une `kadence/rowlayout` avec `maxWidth` et `padding`, comme la page `ref-formulaire-02-avance`.

Le formulaire **n'est pas rendu** (sortie vide, sans message) dans les cas suivants :
- `id` absent ou à 0 ;
- le post n'est pas de type `kadence_form` ;
- son statut n'est pas `publish` (un statut `future` suffit, constaté au § 7.3) ;
- il est protégé par mot de passe. **E/C**

Pour styler le formulaire, **ne pas cibler `…64-cpt-id`**, car cet identifiant dépend de l'ID du post. Utiliser la méta `_kad_form_className` ou `_kad_form_anchor`. **C**

### 2.3 Créer le `kadence_form`

`editeur.js construire` ne sait créer que des **pages**. Trois façons de créer le formulaire :

1. **Dans le vrai éditeur**, par script. C'est ce que j'ai fait pour les essais (`creer-form.js`, § 9). Le principe :

   ```js
   // dans /wp-admin/post-new.php?post_type=kadence_form, une fois l'éditeur chargé :
   const racine = wp.data.select('core/block-editor').getBlocks().find(b => b.name === 'kadence/advanced-form');
   const fab = n => wp.blocks.createBlock(n.name, n.attributes || {}, (n.innerBlocks || []).map(fab));
   wp.data.dispatch('core/block-editor').replaceInnerBlocks(racine.clientId, spec.champs.map(fab), false);
   const meta = Object.assign({}, wp.data.select('core/editor').getEditedPostAttribute('meta'), spec.meta);
   wp.data.dispatch('core/editor').editPost({ title: spec.titre, slug: spec.slug, status: 'publish', meta });
   // attendre 4 s puis : wp.data.dispatch('core/editor').savePost()
   ```

   Ce que fait l'éditeur à l'enregistrement **E** :
   - il conserve les `uniqueID` fournis (`pd-nom`…) ;
   - il ajoute `formID: "<ID>"` (en chaîne) à chaque champ, sauf au bouton et au captcha ;
   - il donne à la racine un `uniqueID` de la forme `64_3028d6-7d` ;
   - il calcule la méta `_kad_form_fields` (`[{uniqueID, name, label, type}]`) ;
   - il écrit **toutes** les méta déclarées, avec leurs valeurs par défaut.

   Tous les blocs sont valides après rechargement.
2. **Dans le WXR**, en ajoutant un item `kadence_form` avec un ID fixe. C'est le chemin naturel pour `construire.py` (§ 7.3). **E**
3. **Par l'API REST** `POST /wp/v2/kadence_form` avec `content` et `meta`. L'éditeur passe par cette route, mais je ne l'ai pas appelée directement. **—**

---

## 3. Spec complète testée (`kadence_form` #64 `ref-formulaire-contact`, page `ref-formulaire-02-avance`)

### 3.1 Spec du formulaire (format de `creer-form.js`)

```json
{
 "titre": "Réf formulaire – contact", "slug": "ref-formulaire-contact",
 "meta": {
  "_kad_form_actions": ["email"],
  "_kad_form_email": {"emailTo": "contact@pascaldupont.fr", "subject": "[pascaldupont.fr] {type_projet} : {nom}", "fromEmail": "", "fromName": "", "replyTo": "email_field", "cc": "", "bcc": "", "html": true},
  "_kad_form_messages": {"success": "Merci, votre message est bien parti. Je vous réponds personnellement.", "error": "Le formulaire n'a pas pu être envoyé. Vérifiez les champs et réessayez.", "required": "", "invalid": "", "recaptchaerror": "Vérification anti-spam échouée, rechargez la page.", "preError": "Merci de corriger les erreurs ci-dessous."},
  "_kad_form_description": "Formulaire de contact (référence)",
  "_kad_form_browserValidation": true
 },
 "champs": [
  {"name": "kadence/rowlayout", "attributes": {"uniqueID": "pd-form-ligne1", "kbVersion": 2, "columns": 2, "colLayout": "equal", "padding": ["0", "0", "0", "0"], "columnGutter": "default", "mobileLayout": "row"}, "innerBlocks": [{"name": "kadence/column", "attributes": {"uniqueID": "pd-form-ligne1-c1", "kbVersion": 2, "borderWidth": ["", "", "", ""]}, "innerBlocks": [{"name": "kadence/advanced-form-text", "attributes": {"uniqueID": "pd-nom", "label": "Nom et prénom", "required": true, "inputName": "nom", "auto": "name", "requiredMessage": "Indiquez votre nom."}}]}, {"name": "kadence/column", "attributes": {"uniqueID": "pd-form-ligne1-c2", "kbVersion": 2, "borderWidth": ["", "", "", ""]}, "innerBlocks": [{"name": "kadence/advanced-form-email", "attributes": {"uniqueID": "pd-email", "label": "Adresse e-mail", "required": true, "inputName": "email", "auto": "email", "requiredMessage": "Indiquez votre adresse e-mail."}}]}]},
  {"name": "kadence/advanced-form-select", "attributes": {"uniqueID": "pd-type", "label": "Type de projet", "required": true, "inputName": "type_projet", "placeholder": "Choisissez…", "requiredMessage": "Choisissez un type de projet.", "options": [{"value": "Documentaire ou film institutionnel", "label": "Documentaire ou film institutionnel"}, {"value": "Portrait filmé", "label": "Portrait filmé"}, {"value": "Captation d'événement", "label": "Captation d'événement"}, {"value": "Stratégie et communication", "label": "Stratégie et communication"}, {"value": "Montage et post-production", "label": "Montage et post-production"}, {"value": "Autre demande", "label": "Autre demande"}]}},
  {"name": "kadence/advanced-form-textarea", "attributes": {"uniqueID": "pd-message", "label": "Votre message", "required": true, "inputName": "message", "rows": 8, "requiredMessage": "Écrivez votre message."}},
  {"name": "kadence/advanced-form-accept", "attributes": {"uniqueID": "pd-consentement", "label": "Consentement", "showLabel": false, "required": true, "inputName": "consentement", "description": "J'accepte que ces informations servent à répondre à ma demande (voir la <a href=\"/confidentialite/\">politique de confidentialité</a>).", "requiredMessage": "Cochez la case pour accepter."}},
  {"name": "kadence/advanced-form-submit", "attributes": {"uniqueID": "pd-envoyer", "text": "Envoyer"}}
 ]
}
```

Résultat **E** :
- blocs valides après rechargement ;
- au bureau (1280 px), nom et e-mail sont côte à côte (rangée Kadence à 2 colonnes) ; à 375 px, tout est empilé ; pas de débordement horizontal ;
- la soumission complète renvoie le message de succès en français ;
- le courrier capturé est décrit au § 5.

Rangées dans le formulaire **E** :
- `columns: 2` et `mobileLayout: "row"` sont des valeurs par défaut : elles ne sont pas enregistrées, mais le rendu est correct.
- Les règles de la fiche `mise-en-page.md` s'appliquent : `uniqueID` + `kbVersion: 2` + `borderWidth` vide sur les colonnes.
- Le serveur parcourt les blocs imbriqués : les champs placés dans des colonnes sont bien traités.
- **`select` et `accept` peuvent aller dans une colonne** (corrigé à la contre-vérification, § 12) :
  - L'éditeur (`wp.blocks.getBlockType(…).parent`) donne `["kadence/advanced-form"]` pour `select`, `accept`, `radio` et `file`. Pour `select` et `accept`, c'est l'enregistrement JS qui retire `kadence/column` de leur `block.json`. Pour `radio` et `file`, c'est déjà le cas dans le `block.json`. Les autres champs ont `["kadence/advanced-form", "kadence/column"]`. **C + E**
  - Cette déclaration n'empêche rien en pratique. Dans un formulaire, la `kadence/column` liste explicitement `select` et `accept` dans ses `allowedBlocks`. `canInsertBlockType` renvoie `true` et l'inserteur de la colonne les propose. **E**
  - Un `select` et un `accept` placés dans une colonne par spec restent valides après rechargement. Ils sont rendus, contrôlés par le serveur (champ obligatoire) et apparaissent dans l'e-mail. **E** (formulaire #140)

### 3.2 Méta du formulaire (`_kad_form_*`)

Les méta tableaux ou objets sont stockées **sérialisées en PHP** (voir § 7.3). Seules les trois premières lignes du tableau sont nécessaires pour un formulaire de contact. **E** : le formulaire 9100 du § 7.3 fonctionnait avec `_kad_form_actions`, `_kad_form_email` et `_kad_form_messages` seulement.

| Méta | Type | Format / valeurs | Défaut | Vérif. |
|---|---|---|---|---|
| `_kad_form_actions` | array de string | `["email"]` ; aussi `"redirect"`, `"mailerlite"`, `"fluentCRM"` en gratuit. `autoEmail`, `entry`, `webhook`, `mailchimp`, `sendinblue`, `convertkit`, `getresponse` et `activecampaign` sont marqués « (Pro addon) » | `["email"]` | **E** (email), **C** (reste) |
| `_kad_form_email.emailTo` | string | destinataire. Vide = e-mail d'administration du site. Les jetons `{inputName}` sont acceptés | `""` | **E** |
| `_kad_form_email.subject` | string | jetons `{inputName}` remplacés par la valeur saisie, `{page_title}` par le titre de la page d'envoi. Vide = `[Nom du site Submission]` | `""` | **E** (`{type_projet}`, `{nom}`), **C** (`{page_title}`, défaut) |
| `_kad_form_email.replyTo` | string | `"email_field"` = valeur du **dernier** champ de type e-mail ; `"from_email"` = `fromEmail` | `"email_field"` | **E** (`email_field`) |
| `_kad_form_email.fromEmail`, `.fromName` | string | en-tête `From`. Vide = expéditeur par défaut de WordPress | `""` | **C** |
| `_kad_form_email.cc`, `.bcc` | string | adresses séparées par des virgules | `""` | **C** |
| `_kad_form_email.html` | boolean | `true` = modèle HTML Kadence, `false` = texte `Libellé: valeur` | `true` | **E** (les deux, § 5) |
| `_kad_form_messages.success` | string | message affiché après envoi (HTML simple accepté) | `""` = « Submission Success, Thanks for getting in touch! » | **E** |
| `_kad_form_messages.preError` | string | titre de la liste d'erreurs **côté navigateur** (attribut `data-error-message`) | `""` = « Please fix the errors to proceed » | **E** |
| `_kad_form_messages.recaptchaerror` | string | message en cas d'échec du captcha | `""` = message anglais | **E** |
| `_kad_form_messages.error` | string | utilisé seulement si une action tierce échoue, **pas** pour les champs manquants | `""` | **C** |
| `_kad_form_messages.required`, `.invalid` | string | non utilisés par le traitement du formulaire avancé | `""` | **C** |
| `_kad_form_browserValidation` | boolean | `true` = validation native du navigateur **d'abord**, puis la validation JS Kadence, qui s'exécute à chaque envoi ; `false` ajoute `novalidate="true"` et laisse seulement le JS Kadence (§ 4.3) | `true` (stocké `"1"`, `false` stocké `""`) | **E** |
| `_kad_form_redirect` | string | URL de redirection, avec l'action `"redirect"` | `""` | **C** |
| `_kad_form_submitHide` | boolean | masque le formulaire après succès | `false` | **C** |
| `_kad_form_className`, `_kad_form_anchor` | string | classe et `id` sur l'enveloppe du formulaire (pour le CSS maison) | `""` | **C** |
| `_kad_form_description` | string | description dans la liste d'administration | `""` | **E** |
| `_kad_form_style`, `_kad_form_labelFont`, `_kad_form_inputFont`, `_kad_form_background`, `_kad_form_padding`… | objets | apparence (non étudiée ici). Sans eux, aucune règle CSS manquante : les classes `…-label-style-normal` et `…-input-size-standard` n'ont pas de style associé | voir `advanced-form-cpt.php` | **C** |
| `_kad_form_fields` | array | calculée par l'éditeur pour détecter les doublons de `inputName`. **Le serveur ne s'en sert pas** | `[]` | **E** (formulaire 9100 sans cette méta : fonctionne) |

---

## 4. Champs (blocs internes)

Tous les champs sont **dynamiques** : `save` renvoie `null` et seul le commentaire de bloc est enregistré. Le HTML est produit par PHP. **E/C**

### 4.1 Attributs communs (`text`, `email`, `select`, `textarea`, `accept`)

Exceptions relevées dans les `block.json` à la contre-vérification **C** :
- `accept` n'a ni `placeholder`, ni `auto`/`autoCustom`, ni `errorMessage` ;
- `select` n'a ni `auto` ni `autoCustom` ;
- `label` n'a pas de valeur par défaut dans `text` (`""` ailleurs) ;
- pour `accept`, un `defaultValue` non vide devient la valeur envoyée **et coche la case d'avance** (`get_accept_default`, `is_checked_from_param`). Ne pas en mettre sur la case de consentement.

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `uniqueID` | string | toujours le fournir, par exemple `pd-nom`. Il est conservé tel quel. Il sert à la classe `kb-field{formID}{uniqueID}`, à l'`id` `field{formID}{uniqueID}` et au nom par défaut `field{uniqueID}`. Sans lui, le PHP lit une clé absente | — | **E** |
| `formID` | string | ID du `kadence_form` **en chaîne** (`"64"`), ajouté par l'éditeur. Dans un WXR généré, mettre l'ID fixe | — | **E** |
| `inputName` | string | nom du champ envoyé en POST **et** jeton `{…}` du sujet. À fixer (`nom`, `email`, `type_projet`, `message`, `consentement`) | — (sinon `field{uniqueID}`) | **E** |
| `label` | string | libellé. **Non échappé** : HTML possible. C'est aussi le libellé de la ligne dans l'e-mail | `""` | **E** |
| `showLabel` | boolean | `false` : pas de `<label>` visible (`aria-label` sur le champ, `<legend class="screen-reader-text">` pour `accept`) | `true` | **E** (accept) |
| `required` | boolean | ajoute `required aria-required="true"`, l'astérisque et le contrôle serveur | `false` | **E** |
| `requiredMessage` | string | message d'erreur en français, rendu en `data-kb-required-message`. Il est affiché par le JS Kadence **dans les deux modes de `_kad_form_browserValidation`** : avec `true`, c'est quand le navigateur laisse passer, par exemple un champ rempli d'espaces. Il apparaît aussi quand le serveur refuse ce champ. Le serveur, lui, renvoie toujours « Missing a required field » : il lit une clé `required_message` qui n'existe pas. Sans `requiredMessage`, le JS affiche « <libellé> is required » (anglais) | — | **E** |
| `placeholder` | string | texte indicatif. Pour `select`, crée `<option value="" disabled selected>` | `""` | **E** (select) |
| `auto` | string | valeur de `autocomplete` (`"name"`, `"email"`) ; `"custom"` + `autoCustom` | — | **E** |
| `helpText` | string | aide sous le champ (échappée) | `""` | **C** |
| `defaultValue`, `defaultParameter` | string | valeur initiale ; ou nom d'un paramètre d'URL qui la fournit | — | **C** |
| `ariaDescription` | string | description pour lecteur d'écran | `""` | **C** |
| `maxWidth` | array [bureau, tablette, mobile] | nombres en chaîne, unité `maxWidthUnit` (`"%"` par défaut). `["50","","100"]` → `max-width:50%`, puis `100%` sous 767 px. Le formulaire est en `flex-direction: column` : un champ à 50 % **ne se met pas** à côté du suivant (utiliser une rangée, § 3.1) | `["","",""]` | **E** |
| `minWidth`, `minWidthUnit` | array, string | idem, unité `px` par défaut | `["","",""]`, `"px"` | **C** |
| `errorMessage` | string | présent dans `block.json` mais **non utilisé** par le rendu PHP 3.7.12 | — | **C** |

### 4.2 Particularités par champ

| Bloc | Attributs propres | Remarques | Vérif. |
|---|---|---|---|
| `kadence/advanced-form-text` | — | `<input type="text">` | **E** |
| `kadence/advanced-form-email` | — | `<input type="email">`. Valeur passée dans `sanitize_email` | **E** |
| `kadence/advanced-form-select` | `options` : array `[{value, label}]`, défaut `[{"value":"","label":""}]` ; `multiSelect` : boolean, défaut `false` | `value` vide = `label` (code). **Le JS Kadence ne valide pas le select** : pas de `data-required` dans le HTML. Le serveur contrôle seulement qu'il n'est pas vide, **pas que la valeur est dans la liste** | **E** |
| `kadence/advanced-form-textarea` | `rows` : number, défaut `3` | **Aucun attribut de longueur minimale ou maximale.** Un message « Ok » est accepté | **E** |
| `kadence/advanced-form-accept` | `description` : string, **HTML non échappé** (texte de la case, lien possible) ; `isChecked` : boolean, défaut `false` | Valeur envoyée `accept`, écrite « Accept » (en anglais) dans l'e-mail. Le lien `/confidentialite/` s'affiche dans le libellé de la case | **E** |
| `kadence/advanced-form-submit` | `text` : string (texte du bouton) ; `hAlign` (`"left"`) ; `widthType` ; styles du bouton… | `"text": "Envoyer"` donne `<button type="submit">…Envoyer…</button>` | **E** |
| `kadence/advanced-form-captcha` | `type` : `"googlev2"` (défaut), `"googlev3"`, `"turnstile"`, `"hcaptcha"` ; `useKbSettings` : boolean, défaut `true` ; `turnstileSiteKey`/`turnstileSecretKey`, `recaptchaSiteKey`/`recaptchaSecretKey`, `hCaptchaSiteKey`/`hCaptchaSecretKey` ; `theme` `"light"` ; `size` `"normal"` | Détails au § 6 | **E/C** |

Autres champs gratuits non étudiés : `checkbox`, `radio`, `number`, `telephone`, `date`, `time`, `file`, `hidden`. **C**

### 4.3 Validation et textes en français

Deux modes, réglés par la méta `_kad_form_browserValidation` :

- **`true` (défaut, recommandé)** : le navigateur valide d'abord.
  - Tous les champs obligatoires sont couverts, y compris la liste et la case.
  - Les messages sont ceux du navigateur, **dans la langue du visiteur**. En essai, Chromium en anglais a affiché « Please fill out this field. ».
  - **Si le navigateur laisse passer, la validation JS de Kadence s'exécute quand même** (`validateForm` est appelé à chaque envoi et compare les valeurs après `trim()`). Corrigé à la contre-vérification **E** :
    - nom et message remplis d'espaces : aucune requête envoyée, « Indiquez votre nom. » et « Écrivez votre message. » s'affichent (`requiredMessage`) ;
    - e-mail `jeanne@exemple`, accepté par le navigateur, refusé par l'expression régulière de Kadence (domaine sans point) : « Adresse e-mail is not valid », en anglais.
- **`false`** : la validation JS de Kadence affiche nos messages.
  - Exemple : « Merci de corriger les erreurs ci-dessous. » suivi de « Indiquez votre nom. », etc.
  - **La liste déroulante n'est pas contrôlée côté navigateur.** Si elle est vide, c'est le serveur qui refuse, avec un titre **en anglais** « Submission Failed » ; le message du champ, lui, est bien « Choisissez un type de projet. ». **E**

Textes anglais fixes, observés en essai sans traduction française de Kadence Blocks installée **E** :
- « Submission Failed » et « Missing a required field » (erreurs serveur) ;
- « <libellé> is required » : validation JS d'un champ **sans** `requiredMessage`, par exemple « Nom is required » ;
- « <libellé> is not valid » : e-mail au format refusé par le JS Kadence, par exemple « Adresse e-mail is not valid ». **Aucun attribut ne permet de le changer** : le JS lit `data-validation-message`, que le PHP n'écrit jamais. Ce message s'affiche dans les deux modes. Le suffixe vient de `kb_adv_form_params.validation`, une chaîne traduisible : un paquet de langue pourrait donc le traduire (**—**). On pourrait aussi ajouter `data-validation-message` avec le filtre PHP `kadence_advanced_form_input_attributes` (**C**, non essayé) ;
- « Accept » (valeur de la case dans l'e-mail) ;
- « Sent from Pascal Dupont » (pied du courrier HTML, modifiable par le filtre `kadence_blocks_form_email_footer_text`, **C**) ;
- « Submission rejected. » ;
- « Submission rejected, invalid security token… » ;
- les messages par défaut si `success`, `preError` ou `recaptchaerror` sont vides.

Sur le vrai site, le paquet de langue français de Kadence Blocks pourrait en traduire une partie (**—**, voir § 10).

---

## 5. Le courrier envoyé (capturé avec le filtre `wp_mail`)

Données envoyées : `nom=Jeanne Essai`, `email=jeanne.essai@exemple.test`, `type_projet=Captation d'événement`, `message=Ok`, `consentement=accept`. **E**

```
to:      contact@pascaldupont.fr
subject: [pascaldupont.fr] Captation d'événement : Jeanne Essai
headers: Content-Type: text/html; charset=UTF-8
         Reply-To: <jeanne.essai@exemple.test>
corps (HTML, 7,5 ko, texte extrait) : Nom et prénom Jeanne Essai | Adresse e-mail jeanne.essai@exemple.test |
         Type de projet Captation d'événement | Votre message Ok | Consentement Accept | Sent from Pascal Dupont
résultat de wp_mail : échec (« Impossible d'instancier la fonction mail. »)
réponse AJAX : {"submissionResults":{"success":true},"html":"<div class=\"kb-adv-form-message kb-adv-form-success\">Merci, votre message est bien parti…</div>","success":true,...}
```

- Avec `html: false` : `Content-Type: text/plain` et un corps de la forme `Nom et prénom: Jeanne Essai\n\nAdresse e-mail: …\n\nConsentement: Accept\n\n`. **E** (même chemin de code, valeur forcée par le filtre `kadence_blocks_advanced_form_form_args`.) Revérifié à la contre-vérification avec la méta réellement enregistrée (`"html": false`, formulaire #140) : corps `Nom: Jeanne\n\nType de projet: Choix B\n\nAdresse e-mail: …\n\n`, dans l'ordre des blocs.
- Pas d'en-tête `From` quand `fromEmail` est vide : WordPress met son expéditeur par défaut. **C**
- **Délivrabilité vers live.fr** (SPF/DKIM, extension SMTP) : **—**. Le guide `INSTALLATION.md` conseille déjà WP Mail SMTP.
- Le modèle HTML peut être remplacé en copiant `includes/templates/form-email.php` dans `kadence-pascal/kadence-blocks/form-email.php`. **C**

---

## 6. Anti-spam disponible gratuitement

| Protection | `kadence/advanced-form` | Vérif. |
|---|---|---|
| Pot de miel | **aucun** : rien dans le code (`advanced-form-ajax.php`) ni dans le HTML | **E** |
| Délai minimal / jeton horaire | **aucun** : une requête `curl` envoyée sans charger la page est acceptée et affiche « Merci… » | **E** |
| Limite d'envois | aucune | **C** |
| Nonce | désactivé par défaut. Le filtre `add_filter( 'kadence_blocks_form_verify_nonce', '__return_true' );` dans le thème enfant l'active : sans `_kb_form_verify`, l'envoi est refusé (« Submission rejected, invalid security token… », anglais). Attention au cache de page : le nonce expire | **E** (en ligne de commande) |
| Règle maison | filtre `kadence_blocks_advanced_form_submission_reject( $rejet, $form_args, $champs, $post_id )` : retourner `true` refuse l'envoi (« Submission rejected. »). Essayé avec « refuser si le message contient un lien » | **E** (en ligne de commande) |
| Captcha | bloc `kadence/advanced-form-captcha`, détails ci-dessous | **E** partiel |

Captcha (essai : formulaire #74 `ref-formulaire-captcha`, page `ref-formulaire-03-captcha`, clés de test publiques de Cloudflare Turnstile) :
- `useKbSettings: true` (défaut) : les clés viennent des **réglages** Kadence Blocks, options `kadence_blocks_turnstile_site_key` et `kadence_blocks_turnstile_secret_key` (`kadence_blocks_recaptcha_*`, `kadence_blocks_hcaptcha_*` pour les autres). Sans clé, le bloc ne rend **rien** et le serveur **ne vérifie rien**. **C** (les réglages du site n'ont pas été modifiés)
- `useKbSettings: false` : les clés sont des attributs du bloc. **La clé secrète est alors écrite dans le `post_content`** (constaté) : elle est donc exportée dans le WXR et lisible par les éditeurs. **À éviter.** **E**
- Rendu : `<div class="cf-turnstile" data-sitekey="…">` + script `https://challenges.cloudflare.com/turnstile/v0/api.js`. C'est un service tiers chargé sur la page (question RGPD/cookies à trancher). **E**
- Envoi sans jeton valide : refusé avec `_kad_form_messages.recaptchaerror` (« Vérification anti-robot échouée : rechargez la page et réessayez. », console « CAPTCHA Failed »). Le refus est donc bien sûr. **E**
- Envoi **avec** un jeton valide : **—**. L'accès réseau à Cloudflare est bloqué ici (le script ne se charge pas, la vérification serveur reçoit une erreur 403).
- reCAPTCHA v3 : seul `success` est contrôlé, **le score n'est pas comparé à un seuil**. **C**

---

## 7. Export et import WXR

### 7.1 Ce qu'exporte WordPress (Outils > Exporter)

- **« Pages » n'exporte pas les `kadence_form`** : l'export des pages contenait 35 pages et 0 formulaire. **E**
- **« Tout le contenu »** les inclut (2 `kadence_form`), car `can_export: true`. Il existe aussi un choix « Forms » propre au type. **E** pour l'export, **C** pour le bouton radio.
- Les méta `_kad_form_*` sont écrites **sérialisées en PHP**, par exemple `a:8:{s:7:"emailTo";s:21:"contact@pascaldupont.fr";…;s:4:"html";b:1;}`. **E**

Conclusion : avec `kadence/advanced-form`, il faut exporter et importer **la page et le `kadence_form`**.

### 7.2 Ce que fait l'import (WordPress Importer 0.9.6), essais sur des sites WordPress neufs séparés (ports 8091 à 8095)

- L'importeur demande l'ID d'origine (`import_id`). WordPress le garde **s'il est libre**, sinon il en attribue un nouveau. **L'importeur ne réécrit jamais les ID dans le contenu des blocs.** **C** + **E**

| Cas | Résultat | Vérif. |
|---|---|---|
| Site neuf, page 70 + formulaire 64 | IDs conservés (64→64, 70→70). Formulaire affiché, envoi accepté, destinataire, sujet et Reply-To intacts | **E** |
| Site où les ID 1 à 80 sont déjà pris | 64→81, 70→82. La page référence toujours `{"id":64}`, qui est maintenant un article : **le formulaire disparaît sans message** | **E** |
| Page importée sans son `kadence_form` | aucun formulaire, sans message | **E** |
| Ancien `kadence/form`, ID de page déjà pris (62→71) | l'attribut `postID` et le champ caché `_kb_form_post_id` valent toujours `62` : **envoi refusé** (« Submission Failed », console « Data not found ») | **E** |

- L'outil d'export/import propre à Kadence (boutons de la liste Kadence Blocks > Forms, fichier ZIP JSON) **crée toujours de nouveaux ID** et ne met à jour **que** les références entre posts Kadence, **pas les pages**. Les pages sont donc à corriger à la main. **C**
- `uniqueID` de la page, `formID` et racine du `kadence_form` : leur décalage après import ne casse rien. Le nom des champs vient de `inputName`, et les classes CSS ainsi que le CSS généré utilisent le même `formID` enregistré. **C**

### 7.3 Générer le formulaire dans le WXR (méthode pour `construire.py`)

Essai : WXR écrit à la main (`gen-wxr.py`), importé sur un site neuf, puis rendu et envoi vérifiés. **E**

1. Donner au `kadence_form` un **ID fixe libre**, par exemple `9100`, comme les pages 9001 à 9009 de `construire.py`. La page contact contient alors `<!-- wp:kadence/advanced-form {"id":9100} /-->`. L'ID est conservé si le site cible ne l'utilise pas.
2. **`post_content` doit commencer directement par `<!-- wp:kadence/advanced-form`.**
   - Avec un simple saut de ligne avant, le formulaire **s'affiche**, mais chaque envoi est refusé (« Submission Failed », console « Data not found »).
   - Cause : le serveur exige que le **premier** bloc analysé soit `kadence/advanced-form`. **E** (formulaire 9101)
3. **Méta en sérialisation PHP, pas en JSON.**
   - Avec du JSON, `_kad_form_actions` devient une chaîne : aucune action n'est exécutée, donc **aucun e-mail**. Le visiteur voit pourtant « Submission Success, Thanks for getting in touch! ». **E** (formulaire 9102)
4. **`post_date` et `post_date_gmt` dans le passé.** Sinon le statut devient `future` et le formulaire n'est pas rendu. **E** (premier essai, date fixée à 10 h UTC alors qu'il était 9 h 35). `construire.py` met l'heure courante : c'est correct.
5. Méta suffisantes : `_kad_form_actions`, `_kad_form_email`, `_kad_form_messages`. **E**
6. Champs : mettre `uniqueID`, `inputName` et `formID: "9100"` sur chaque champ. **E**

Extrait testé (Python) :

```python
def php_serialize(v):
    if v is None: return 'N;'
    if isinstance(v, bool): return 'b:%d;' % (1 if v else 0)
    if isinstance(v, int): return 'i:%d;' % v
    if isinstance(v, str): return 's:%d:"%s";' % (len(v.encode('utf-8')), v)   # longueur en OCTETS
    if isinstance(v, (list, tuple)): v = dict(enumerate(v))
    if isinstance(v, dict): return 'a:%d:{%s}' % (len(v), ''.join(php_serialize(k) + php_serialize(x) for k, x in v.items()))
    raise TypeError(type(v))

# item <wp:post_type>kadence_form</wp:post_type>, <wp:post_id>9100</wp:post_id>, <wp:status>publish</wp:status>, avec :
meta('_kad_form_actions', php_serialize(["email"]))
meta('_kad_form_email', php_serialize({"emailTo": "contact@pascaldupont.fr", "subject": "[pascaldupont.fr] {type_projet} : {nom}",
     "fromEmail": "", "fromName": "", "replyTo": "email_field", "cc": "", "bcc": "", "html": True}))
meta('_kad_form_messages', php_serialize({"success": "Merci, votre message est bien parti. Je vous réponds personnellement.", "error": "…",
     "required": "", "invalid": "", "recaptchaerror": "…", "preError": "Merci de corriger les erreurs ci-dessous."}))
# contenu : '<!-- wp:kadence/advanced-form {"uniqueID":"pd-form-contact"} -->\n' + champs + '\n<!-- /wp:kadence/advanced-form -->'
# un champ : '<!-- wp:kadence/advanced-form-text {"uniqueID":"pd-nom","formID":"9100","label":"Nom et prénom","required":true,"inputName":"nom","auto":"name"} /-->'
```

Réimport du même WXR : l'importeur ne reconnaît un post existant que par son titre **et** sa date. Comme `construire.py` met la date du moment, chaque réimport créerait des doublons : un nouveau formulaire avec un nouvel ID, et une nouvelle page qui pointerait encore vers l'ancien 9100. Ce point est déduit du code de l'importeur et n'a pas été essayé (**C**).

---

## 8. Recommandation : garder `[pd_formulaire]`

Essais du shortcode : page `ref-formulaire-04-maison` (spec `core/shortcode` `"text": "[pd_formulaire]"`), soumissions Playwright, et `pd_traiter_contact()` exécutée en ligne de commande. **E**

| Situation | Résultat |
|---|---|
| Envoi moins de 3 s après l'affichage | redirection `?envoi=erreur` |
| Envoi après 3,5 s, pas de serveur de courrier | `?envoi=echec` : l'échec est **signalé** |
| Second envoi dans la minute (même IP) | `?envoi=attente` |
| Pot de miel `pd_site` rempli | faux succès `?envoi=ok`, rien n'est envoyé |
| Type hors liste | `?envoi=erreur` |
| Message de 2 caractères | `?envoi=erreur` |

Courrier capturé : `to: contact@pascaldupont.fr`, `subject: [pascaldupont.fr] Captation d'événement : Jeanne Essai`, `Content-Type: text/plain`, `Reply-To: Jeanne Essai <jeanne.essai@exemple.test>`. Le corps contient le nom, l'e-mail, le type et le message.

Pourquoi le garder :
1. Seul à cumuler pot de miel, délai minimal signé, limite d'envois et contrôle de la liste côté serveur. Kadence gratuit n'a **rien de cela** sur le formulaire avancé.
2. **Seul à dire la vérité quand l'e-mail ne part pas.** Kadence affiche « Merci » même si `wp_mail()` échoue. Sur un hébergement mutualisé sans SMTP, des demandes de devis seraient perdues sans que personne ne le sache.
3. Fonctionne sans JavaScript.
4. Voyage dans le WXR comme du texte, sans ID à préserver (code).
5. Textes entièrement en français, y compris les erreurs (code).

Écarts avec le cahier des charges, à corriger dans `kadence-pascal/functions.php`. Ces corrections ne sont **pas** appliquées : le thème est en lecture seule pour cette tâche.
- **Supprimer la longueur minimale du message** : retirer `minlength="10"` (ligne 105) et `strlen( $message ) < 10 ||` (ligne 153). Le cahier des charges dit « sans limite basse ». `maxlength="5000"` peut rester.
- Ajouter une option vide `<option value="" disabled selected>Choisissez…</option>` et `required` au `<select>`. Aujourd'hui, la première option, « Documentaire ou film institutionnel », est présélectionnée et part par défaut. Le contrôle `in_array` du serveur refuse déjà la valeur vide.
- La redirection vise toujours `/contact/` (`pd_redirige`). Le formulaire n'est donc correct que sur cette page. Sur la page d'essai, la redirection a donné une 404 car la page `contact` n'existe pas sur le site de test.

**Si l'on choisit malgré tout Kadence**, prendre `kadence/advanced-form` (spec du § 3.1) et ajouter dans le thème enfant :
- le filtre de rejet (§ 6), pour un pot de miel ou un délai ;
- un journal sur `wp_mail_failed`, puisque Kadence ne signale pas l'échec ;
- les clés Turnstile dans les réglages Kadence, pas dans le bloc ;
- les règles d'export WXR du § 7.

**Ne pas utiliser `kadence/form`** :
- il est retiré de l'inserteur ;
- son HTML statique est difficile à générer par script ;
- son `postID` figé casse l'envoi dès que l'ID de la page change.

---

## 9. Ancien bloc `kadence/form` (pour mémoire)

Page `ref-formulaire-01-ancien` (#62), construite avec `editeur.js`, valide après rechargement. **E**

| Attribut | Type | Format | Défaut | Vérif. |
|---|---|---|---|---|
| `uniqueID` | string | clé de recherche côté serveur (`_kb_form_id`). Gardée telle quelle (`pd-form-ancien`) | `""` | **E** |
| `postID` | string | **rempli par l'éditeur** avec l'ID de la page (`"62"`) et figé dans le champ caché `_kb_form_post_id`. Vide = « Submission failed » | `""` | **E** (rempli), **C** (vide) |
| `fields` | array d'objets | **remplace entièrement** les 3 champs par défaut. Chaque objet doit avoir toutes les clés : `label, showLabel, placeholder, default, description, rows, options[{value,label}], multiSelect, inline, showLink, min, max, type, required, width[bureau,tablette,mobile], auto, errorMessage, requiredMessage, slug, ariaLabel`. Le PHP lit `required` et `multiSelect` sans `isset` | Name/Email/Message | **E** |
| `fields[].type` | string | `text`, `email`, `select`, `textarea`, `accept` (essayés) ; aussi `tel`, `checkbox`, `radio`, `hidden`… | `text` | **E** / **C** |
| `fields[].width` | array | `["50","",""]` met deux champs côte à côte au bureau | `["100","",""]` | **E** |
| `fields[]` de type `accept` | — | `showLink: true` + `placeholder` (texte du lien) + `default` (URL) affichent un lien au-dessus de la case (`target="_blank"`). `{privacy_policy}` dans `label` renvoie à la page de confidentialité **réglée dans WordPress** (ici `/politique-de-confidentialite/`, pas `/confidentialite/`) | — | **E** (showLink), **C** (`{privacy_policy}`) |
| `email` | array de 1 objet | `[{emailTo, subject, fromEmail, fromName, replyTo, cc, bcc, html}]`. Le sujet accepte `{field_N}` (N à partir de 1, dans l'ordre des champs) et `{page_title}`. Toujours fournir `html`, sinon avertissement PHP et texte brut | voir `block.json` | **E** (`{field_3} : {field_1}`) |
| `messages` | array de 1 objet | `[{success, error, required, invalid, recaptchaerror, preError}]` | vides | **E** (success, preError) |
| `submit` | array de 1 objet | objet complet de `block.json`, avec `"label": "Envoyer"` | `label: ""` = « Submit » | **E** |
| `honeyPot` | boolean | champ caché `_kb_verify_email` : s'il est rempli, « Submission Rejected » (anglais). S'il est **absent** de la requête, l'envoi passe | `true` | **E** |
| `recaptcha`, `recaptchaVersion` | boolean, string | Google seulement (`"v3"` ou `"v2"`), clés globales `kadence_blocks_recaptcha_site_key` et `kadence_blocks_recaptcha_secret_key` | `false`, `"v3"` | **C** |
| `actions`, `redirect` | array, string | `["email"]` ; `"redirect"` + URL | `["email"]`, `""` | **C** |

Essais d'envoi (Playwright et ligne de commande) **E** :
- **Champs vides** : messages en français par champ, sous le titre « Merci de corriger les erreurs ci-dessous. ».
- **Envoi valide** : « Merci… ». Le courrier part vers `contact@pascaldupont.fr`, avec pour sujet `[pascaldupont.fr] Captation d'événement : Jeanne Essai` et l'en-tête `Reply-To: <jeanne.essai@exemple.test>`. Le corps est en HTML ; le `<b>` saisi dans le message est retiré.
- **Pas de serveur de courrier** : succès affiché quand même.
- **Valeur hors liste et message « Ok »** : acceptés.

Spec générée par `gen-ancien.py`. Extrait de l'attribut principal. **Attention : c'est un extrait abrégé, pas une spec utilisable telle quelle.** Les chaînes `"… e-mail, select … textarea …"` et les clés `"…"` remplacent des objets complets. La spec complète est `scratchpad/ref/formulaire/spec-01-ancien.json` ; elle a été rejouée à la contre-vérification (§ 12).

```json
{"name": "kadence/form", "attributes": {
  "uniqueID": "pd-form-ancien",
  "fields": [ {"label": "Nom et prénom", "type": "text", "required": true, "auto": "name", "width": ["50","",""], "requiredMessage": "Indiquez votre nom.", "showLabel": true, "placeholder": "", "default": "", "description": "", "rows": 4, "options": [{"value": "", "label": ""}], "multiSelect": false, "inline": false, "showLink": false, "min": "", "max": "", "errorMessage": "", "slug": "", "ariaLabel": ""},
              "… e-mail, select (6 options + placeholder \"Choisissez…\"), textarea (rows 8) …",
              {"label": "J'accepte que ces informations servent à répondre à ma demande.", "type": "accept", "required": true, "showLink": true, "placeholder": "Voir la politique de confidentialité", "default": "/confidentialite/", "requiredMessage": "Cochez la case pour accepter.", "…": "autres clés comme ci-dessus"} ],
  "email": [{"emailTo": "contact@pascaldupont.fr", "subject": "[pascaldupont.fr] {field_3} : {field_1}", "fromEmail": "", "fromName": "", "replyTo": "email_field", "cc": "", "bcc": "", "html": true}],
  "messages": [{"success": "Merci, votre message est bien parti. Je vous réponds personnellement.", "error": "…", "required": "Ce champ est obligatoire.", "invalid": "Valeur non valide.", "recaptchaerror": "…", "preError": "Merci de corriger les erreurs ci-dessous."}],
  "submit": [{"label": "Envoyer", "…": "toutes les autres clés de submit[0] de block.json"}],
  "honeyPot": true }}
```

---

## 10. Ce qui n'a PAS pu être vérifié

- **Remise réelle d'un e-mail**, et sa réception par live.fr : pas de serveur de courrier. Seuls les arguments passés à `wp_mail()` et son échec ont été constatés.
- **Captcha avec jeton valide** (Turnstile, reCAPTCHA, hCaptcha) : réseau vers Cloudflare et Google bloqué. Les clés globales des réglages Kadence n'ont pas été essayées, pour ne pas modifier les réglages du site partagé.
- **Traduction française de Kadence Blocks** (paquet de langue de translate.wordpress.org) : non installée ici. On ne sait pas lesquels des textes anglais du § 4.3 seraient traduits en production.
- Création d'un `kadence_form` par appel direct à l'API REST.
- Actions `redirect`, `submitHide`, `fromEmail`/`fromName`, `cc`/`bcc`, `{page_title}`, `defaultParameter`, `helpText` : code lu seulement.
- Outil d'export/import ZIP propre à Kadence (Forms > Export/Import) : code lu seulement.
- Réimport du même WXR sur un site qui contient déjà le formulaire : déduit du code de l'importeur.
- ~~`select` ou `accept` placés dans une `kadence/column` à l'intérieur du formulaire.~~ Vérifié depuis (§ 12) : cela fonctionne.
- Chaîne « is not valid » remplacée par `data-validation-message` via le filtre `kadence_advanced_form_input_attributes` : code lu seulement.
- Rendu visuel du formulaire importé par WXR sans les méta de style : présence du formulaire et envoi vérifiés, pas de capture.
- `[pd_formulaire]` sans JavaScript : code lu, pas d'essai navigateur avec JavaScript désactivé (cet essai a été fait pour Kadence).

---

## 11. Traçabilité

**Sur le WordPress partagé** (`127.0.0.1:8080`) :

| Objet | Contenu |
|---|---|
| Page `ref-formulaire-01-ancien` (#62) | `kadence/form` |
| Page `ref-formulaire-02-avance` (#70) | rangée + `kadence/advanced-form {"id":64}` |
| Page `ref-formulaire-03-captcha` (#76) | `{"id":74}` |
| Page `ref-formulaire-04-maison` (#84) | `[pd_formulaire]` |
| Formulaire `kadence_form` #64 `ref-formulaire-contact` | spec du § 3.1 |
| Formulaire `kadence_form` #74 `ref-formulaire-captcha` | clés de test Turnstile |

Le brouillon automatique #61 (`kadence_form`), créé pendant l'exploration, a été supprimé. Aucun réglage, thème ni extension n'a été modifié.

**Sites d'essai séparés** (ports 8091 à 8095, installés avec `outils/wp-test/installer.sh`) : supprimés après les essais.

**Fichiers de travail** dans `scratchpad/ref/formulaire/` :

| Fichier | Rôle |
|---|---|
| `spec-01-ancien.json` (`gen-ancien.py`) | spec du bloc `kadence/form` |
| `spec-02-avance.json`, `spec-03-captcha.json`, `spec-04-maison.json` | specs des pages |
| `spec-form-avance-final.json`, `spec-form-captcha.json` | specs des formulaires |
| `creer-form.js` | crée un `kadence_form` dans l'éditeur |
| `soumettre.js`, `soumettre-captcha.js`, `soumettre-maison.js`, `sansjs.js` | soumissions Playwright |
| `mail-cli.php`, `maison-cli.php` | gestionnaires exécutés en ligne de commande, avec capture de `wp_mail` ; options `court-circuit`, `nonce`, `rejet`, `texte` |
| `lire-form.php`, `rendu.php`, `lire-ancien.php` | contenu, méta et rendu |
| `exporter.php`, `importer.php`, `gen-wxr.py` | essais WXR |
| `export-*.xml`, `wxr-*.xml` | fichiers WXR produits |
| `capture-*.png`, `envoi-*.png`, `editeur-form-*.png` | captures |

---

## 12. Contre-vérification (7 octobre 2026)

Relecture critique de la fiche, faite par un second agent sur le même WordPress de test (`127.0.0.1:8080`, WordPress 7.1.3, Kadence Blocks 3.7.12.1). Démarche : chaque affirmation importante a été recherchée dans le code source, puis les specs de la fiche ont été rejouées **telles qu'écrites dans la fiche** (JSON extrait du Markdown), avec seulement le slug, le titre et l'ID changés.

### 12.1 Specs rejouées

| Spec de la fiche | Objet créé | Contrôles | Résultat |
|---|---|---|---|
| § 3.1, formulaire complet (`creer-form.js`) | `kadence_form` #128 `ref-formulaire-verif-contact` | blocs après rechargement, `post_content`, méta brutes | **Conforme** : aucun bloc invalide ; `uniqueID` conservés ; `formID: "128"` (en chaîne) sur chaque champ, sauf le bouton ; racine `128_89e6e2-b7` ; `columns` et `mobileLayout` non enregistrés ; `_kad_form_fields` calculée ; 70 méta `_kad_form_*` écrites ; `_kad_form_actions` = `a:1:{i:0;s:5:"email";}`, `_kad_form_browserValidation` = `"1"` |
| § 2.2, page `{"id": …}` | page #130 `ref-formulaire-verif-avance` | contenu enregistré, rendu HTML, captures 1280 et 375 px, envois | **Conforme** : enregistré `<!-- wp:kadence/advanced-form {"id":128} /-->` sans `uniqueID` ; `<form id="kb-adv-form-128-cpt-id" … data-error-message="Merci de corriger…">` ; nom et e-mail côte à côte à 1280 px, empilés à 375 px, sans débordement ni erreur JS. Formulaire collé aux bords : remarque ajoutée au § 2.2 |
| § 9, ancien `kadence/form` (spec complète `spec-01-ancien.json`) | page #133 `ref-formulaire-verif-ancien` | contenu, rendu, envois Playwright | **Conforme** : bloc valide ; `uniqueID` conservé ; `postID` rempli par l'éditeur avec l'ID de la page (`"133"`), recopié dans `_kb_form_post_id` ; pot de miel `_kb_verify_email` rendu ; envoi valide → « Merci… » malgré l'échec de `wp_mail` ; pot de miel rempli → « Submission Rejected » |
| § 8, `[pd_formulaire]` | page #138 `ref-formulaire-verif-maison` | contenu, rendu 375 px | **Conforme** : `<!-- wp:shortcode -->[pd_formulaire]<!-- /wp:shortcode -->`, formulaire POST vers `admin-post.php`, `minlength="10"` présent, `<select>` sans option vide (écarts du § 8 confirmés, lignes 105 et 153 de `functions.php` exactes) |

### 12.2 Envois sur le formulaire #128

| Essai | Résultat |
|---|---|
| Ligne de commande (`mail-cli.php`), données du § 5 | Identique au § 5 : `to` `contact@pascaldupont.fr`, sujet `[pascaldupont.fr] Captation d'événement : Jeanne Essai`, `Reply-To: <jeanne.essai@exemple.test>`, HTML 7,5 ko avec « Accept » et « Sent from Pascal Dupont » ; `wp_mail` échoue mais la réponse dit succès |
| Valeur hors liste (`Valeur inventée`, message « x ») | Acceptée, e-mail préparé |
| Liste vide | « Submission Failed » / « Missing a required field », `fieldErrors` sur `type_projet` |
| Navigateur, formulaire complet | « Merci, votre message est bien parti… » |
| Navigateur, formulaire vide (`browserValidation: true`) | Validation native : « Please fill out this field. », « Please select an item in the list. », « Please check this box if you want to proceed. » |

### 12.3 Erreurs trouvées et corrigées dans la fiche

1. **§ 3.1, `select` et `accept` dans une colonne.** La fiche disait de ne pas les y mettre. L'essai montre le contraire : formulaire #140 `ref-formulaire-verif-colonne` et page #142 (`select` puis `accept` dans une `kadence/column`).
   - Dans l'éditeur, `canInsertBlockType` renvoie `true`. Les `allowedBlocks` de la colonne listent ces deux champs, et l'inserteur de la colonne les propose.
   - Les blocs restent valides après rechargement.
   - Le serveur refuse le formulaire quand ces champs obligatoires sont vides, et l'e-mail les contient (`Type de projet: Choix B`, `Consentement: Accept`).
   - Le § 3.1 a été réécrit et la ligne du § 10 barrée.
2. **§ 4.1 `requiredMessage` et § 4.3, mode `true`.** La fiche disait que les `requiredMessage` « ne s'affichent jamais » et qu'ils n'étaient affichés « qu'avec `browserValidation: false` ». C'est faux.
   - Le JS Kadence appelle `validateForm` à chaque envoi, sans regarder `novalidate`.
   - Essai sur #130 (`true`), nom et message remplis d'espaces : le navigateur accepte (`checkValidity()` = `true`). Kadence bloque ensuite sans requête AJAX et affiche « Indiquez votre nom. » et « Écrivez votre message. ».
3. **§ 4.3, textes anglais manquants.** Deux textes ont été ajoutés à la liste.
   - « <libellé> is required » : champ obligatoire sans `requiredMessage`. Constaté : « Nom is required ».
   - « <libellé> is not valid » : e-mail refusé par le JS Kadence. Constaté : « Adresse e-mail is not valid », en mode `false` avec `pas-un-email` et **en mode `true`** avec `jeanne@exemple`, une adresse que le navigateur accepte. Aucun attribut de bloc ne permet de le changer.
4. **§ 3.2, ligne `_kad_form_browserValidation`.** Le texte est corrigé dans le même sens que le point 2 : le navigateur valide d'abord, puis le JS Kadence. Le renvoi pointait vers « § 4.2 » au lieu de « § 4.3 ».
5. **§ 4.1, attributs « communs ».** Certains attributs manquent selon le champ :
   - `accept` n'a ni `placeholder`, ni `auto`, ni `errorMessage` ;
   - `select` n'a pas `auto` ;
   - pour `accept`, un `defaultValue` non vide **coche la case d'avance**.

   Ces précisions ont été ajoutées (code lu).
6. **§ 9, extrait JSON.** L'extrait n'est pas une spec valide en l'état : des chaînes `"…"` y remplacent des objets de `fields`. Un avertissement a été ajouté.

### 12.4 Affirmations vérifiées dans le code, sans écart

- `kadence/form` : `supports.inserter: false`. `kadence/advanced-form` s'appelle « Form (Adv) » dans l'éditeur, alors que son `block.json` dit « Advanced Form ».
- Défauts des attributs (`block.json`) :
  - `advanced-form` : `id` 0 ;
  - `select` : `options` `[{"value":"","label":""}]`, `multiSelect` `false` ;
  - `textarea` : `rows` 3 ;
  - `submit` : `hAlign` `"left"`, `widthType` `"auto"` ;
  - `captcha` : `type` `"googlev2"`, `useKbSettings` `true`, `theme` `"light"`, `size` `"normal"`. Il existe aussi `useKcSettings` (extension Kadence Captcha), non décrit ici ;
  - `form` : `honeyPot` `true`, `recaptchaVersion` `"v3"`.
- Méta enregistrées (`advanced-form-cpt.php`) :
  - `_kad_form_actions` vaut `["email"]` par défaut ;
  - `_kad_form_email` a 8 clés, avec `replyTo` `"email_field"` et `html` `true` par défaut ;
  - `_kad_form_messages` a 6 clés vides ;
  - défauts de `_kad_form_browserValidation` `true`, `_kad_form_submitHide` `false`, `_kad_form_redirect` `""`, `_kad_form_className` et `_kad_form_anchor` `""`.
  - Actions gratuites : `email`, `redirect`, `mailerlite`, `fluentCRM`. Les autres sont marquées « (Pro addon) » et désactivées.
- Traitement de l'envoi (`advanced-form-ajax.php`, `advanced-form-submit-actions.php`) :
  - premier bloc analysé obligatoirement `kadence/advanced-form` (ligne 773) ;
  - clé `required_message` lue, mais jamais écrite ;
  - `Reply-To` = dernier champ de type e-mail ;
  - sujet par défaut `[<nom du site> Submission]` ;
  - jetons `{inputName}` et `{page_title}` ;
  - résultat de `wp_mail()` ignoré ;
  - signature des filtres `kadence_blocks_form_verify_nonce`, `kadence_blocks_advanced_form_submission_reject`, `kadence_blocks_advanced_form_form_args`, `kadence_blocks_form_email_footer_text` ;
  - modèle remplaçable dans `<thème>/kadence-blocks/form-email.php`.
- Captcha :
  - options `kadence_blocks_{recaptcha|turnstile|hcaptcha}_{site|secret}_key` ;
  - bloc non rendu si une clé manque ;
  - reCAPTCHA v3 : seul `success` est lu (aucun seuil de score) ;
  - la clé secrète n'apparaît pas dans le HTML public (page `ref-formulaire-03-captcha`) ;
  - l'API REST `kadence_form` refuse la lecture aux visiteurs anonymes (`rest_cannot_view`).
- Rendu : `{id}-cpt-id` (`class-kadence-blocks-abstract-block.php` l. 211 et 271), rendu vide si statut ≠ `publish` ou mot de passe, `select` sans `data-required`.

### 12.5 Toujours non vérifié

Les points du § 10 restent valables, à l'exception de l'essai « select/accept en colonne », désormais fait.

### 12.6 Traçabilité de la contre-vérification

- **WordPress partagé** :
  - formulaires `kadence_form` #128 `ref-formulaire-verif-contact` et #140 `ref-formulaire-verif-colonne` ;
  - pages #130 `ref-formulaire-verif-avance`, #133 `ref-formulaire-verif-ancien`, #138 `ref-formulaire-verif-maison` et #142 `ref-formulaire-verif-colonne`.

  Aucun réglage, thème ni extension n'a été modifié.
- **Fichiers** dans `scratchpad/ref/formulaire-verif/` :
  - `fiche-json-*.json` : JSON extraits de la fiche ;
  - `spec-verif-*.json` : specs rejouées ;
  - `parents.js`, `parents2.js` : parents déclarés et insertion dans l'éditeur ;
  - `soumettre-colonne.js`, `soumettre-espaces.js`, `soumettre-email-sans-point.js` : essais de validation ;
  - `post-128-*.json`, `post-140-*.json` : envois en ligne de commande ;
  - `capture-verif-*.png`, `envoi-verif-*.png`, `editeur-verif-*.png` : captures.
