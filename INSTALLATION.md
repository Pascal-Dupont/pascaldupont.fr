# Installer le nouveau site sur WordPress (OVH)

Durée : environ 10 minutes pour la première installation. **Pour une mise à jour de contenu, une seule étape** (voir plus bas) : le thème crée et met à jour ses pages lui-même, il n'y a plus besoin d'« Outils, Importer ».

## Fichier à récupérer sur GitHub (dossier `dist/`)
- `kadence-pascal.zip` : le thème enfant de Kadence, qui contient maintenant à la fois l'habillage (couleurs, polices, en-tête, pied de page, formulaire de contact) **et** le texte des 10 pages du site (Accueil, Documentaires, Films, Défense et sécurité, À propos, LAKELAB, Devis et contact, Mentions légales, Confidentialité, plus une page Thales protégée par mot de passe, à ne publier qu'après validation de Thales).

Ouvrez le fichier sur GitHub, puis cliquez sur l'icône « Download raw file » (flèche vers le bas, en haut à droite du fichier). S'il s'enregistre sous un autre nom, renommez-le en `kadence-pascal.zip`.

## Première installation
1. **Installer Kadence.** *Apparence, Thèmes, Ajouter*, tapez « Kadence », cliquez sur *Installer*. **N'activez pas encore.** Ignorez les propositions de modèles de démarrage.
2. **Installer Kadence Blocks.** *Extensions, Ajouter*, tapez « Kadence Blocks » (extension gratuite), *Installer maintenant*, puis *Activer*.
3. **Envoyer le thème enfant.** *Apparence, Thèmes, Ajouter, Téléverser un thème*, choisissez `kadence-pascal.zip`, *Installer*, puis *Activer*.
4. **Ouvrir le Tableau de bord.** Les 10 pages se créent automatiquement, avec la page d'accueil, le titre du site et les menus déjà réglés. Rien d'autre à faire : pas d'import, pas de corbeille à vider.
5. **Vérifier.** Ouvrez pascaldupont.fr sur ordinateur et sur téléphone, parcourez les pages et envoyez-vous un message par le formulaire de contact.

## Mettre à jour le contenu du site (une seule étape)
*Apparence, Thèmes, Ajouter, Téléverser un thème* : choisissez le nouveau `kadence-pascal.zip`, puis **Remplacer l'actif par la version téléversée**. Ouvrez ensuite n'importe quelle page de l'administration (le Tableau de bord, par exemple) : les pages se mettent à jour toutes seules, sans toucher à ce que vous avez modifié vous-même dans WordPress entre-temps sur d'autres réglages (widgets, extensions…).

Ce que cette étape ne touche jamais : un mot de passe que vous avez retiré vous-même (la page Thales, après validation), et tout réglage que vous faites ailleurs dans WordPress. Elle recrée une page si elle a été supprimée ou mise à la corbeille par erreur.

Pour une **toute petite correction de texte** (une faute, une date), vous pouvez aussi la faire vous-même, directement dans *Pages* : ouvrez la page, cliquez sur le texte, corrigez, *Mettre à jour*. Sachez seulement qu'elle sera remplacée à la prochaine fois où vous enverrez un nouveau thème : signalez-moi alors ce changement pour que je le reporte dans le fichier source.

## Après l'installation
- **Les vignettes de films** viennent de YouTube et s'affichent automatiquement.
- **Icône du site (favicon)** : la silhouette de montagnes est déjà incluse dans le thème. Rien à faire.
- **Modifier un texte** : ouvrez la page dans *Pages*, cliquez sur le texte et tapez, comme dans un traitement de texte (voir la remarque ci-dessus sur les mises à jour suivantes).

## Si quelque chose ne va pas
- **Le menu reste vide, ou l'accueil n'est pas la bonne page** : ouvrez n'importe quelle page de l'administration (cela suffit à déclencher le réglage), ou *Réglages, Lecture*, et choisissez « Une page statique » avec « Accueil ».
- **Une page a disparu** : rouvrez simplement le Tableau de bord, elle revient automatiquement (le thème la recrée depuis son propre contenu).
- **L'ancien design s'affiche encore** : *Apparence, Thèmes* et vérifiez que « Pascal Dupont (Kadence, thème enfant) » est actif. Videz le cache du navigateur.
- **Le message du formulaire n'arrive pas** : regardez les courriers indésirables. Les messages sont envoyés à contact@pascaldupont.fr. Si besoin, installez l'extension gratuite « WP Mail SMTP » (serveur ssl0.ovh.net, port 465, SSL, identifiant contact@pascaldupont.fr) pour fiabiliser l'envoi.
- **Dans tous les cas** : envoyez-moi une capture d'écran, je corrige ici, vous renvoyez le zip.

## Page Thales (à valider avant mise en ligne)
La page « Thales » est protégée par le mot de passe `Thales-visionnage-2026` et n'apparaît pas dans le menu. Envoyez son adresse (pascaldupont.fr/thales/) et ce mot de passe à Sarah Mathieu (Thales). Après son accord : dans *Pages*, ouvrez « Thales », retirez le mot de passe (Visibilité : Publique), puis ajoutez la page au menu. Les mises à jour suivantes du thème ne remettront jamais ce mot de passe.

## Pour les modifications futures (maintenance par Claude)
- Les textes validés sont dans `contenu/site.json`. Le générateur `outils/pages_kadence.py` en fait les pages, dans un WordPress de test. `outils/empaqueter.py` exporte ensuite leur contenu déjà vérifié vers `kadence-pascal/inc/contenu-pages.json` (embarqué dans le thème) et fabrique `dist/kadence-pascal.zip`.
- Les fiches `outils/kadence-reference/*.md` documentent, avec essais à l'appui, tous les réglages de Kadence et de Kadence Blocks utilisés.

