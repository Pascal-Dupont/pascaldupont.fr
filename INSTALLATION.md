# Installer le nouveau site sur WordPress (OVH)

Durée : environ 15 minutes. Vous n'avez rien à coder. Ce parcours a été rejoué de bout en bout, par l'interface d'administration, sur un WordPress neuf : les 9 pages s'affichent et s'ouvrent sans erreur dans l'éditeur.

## Fichiers à récupérer sur GitHub (dossier `dist/`)
- `kadence-pascal.zip` : le thème enfant de Kadence (couleurs, polices, en-tête, pied de page, formulaire de contact).
- `pages-pascaldupont.xml` : les 9 pages du site, en blocs Kadence éditables (Accueil, Films, Série Serval, À propos, Défense et sécurité, LAKELAB, Devis et contact, Mentions légales, Confidentialité).

Pour chacun : ouvrez le fichier sur GitHub, puis cliquez sur l'icône « Download raw file » (flèche vers le bas, en haut à droite du fichier).

## Avant de commencer
Il n'est pas nécessaire de sauvegarder l'ancien site si vous n'y tenez pas. À l'étape 1, ses pages seront mises à la corbeille.

## Étapes
1. **Vider les anciennes pages.** Administration WordPress, *Pages*, cochez tout, *Actions groupées : Mettre à la corbeille*, puis ouvrez *Corbeille* et cliquez sur *Vider la corbeille*. Cela évite les conflits d'adresses.
2. **Installer Kadence.** *Apparence, Thèmes, Ajouter*, tapez « Kadence », cliquez sur *Installer*. **N'activez pas encore.** Ignorez les propositions de modèles de démarrage.
3. **Installer Kadence Blocks.** *Extensions, Ajouter*, tapez « Kadence Blocks » (extension gratuite), *Installer maintenant*, puis *Activer*.
4. **Envoyer le thème enfant.** *Apparence, Thèmes, Ajouter, Téléverser un thème*, choisissez `kadence-pascal.zip`, *Installer*, puis *Activer*.
5. **Installer l'outil d'import.** *Outils, Importer*, ligne *WordPress*, *Installer maintenant*, puis *Lancer l'importeur*.
6. **Importer les pages.** Choisissez `pages-pascaldupont.xml`, *Téléverser le fichier et l'importer*. Dans la liste *Attribuer à un utilisateur existant*, choisissez votre compte. Laissez décoché « Télécharger et importer les fichiers joints ». Si une case propose de « changer les URL », vous pouvez la laisser telle quelle. Cliquez sur *Envoyer*.
7. **Ouvrir le Tableau de bord.** Un message vert annonce que la page d'accueil, le titre et les menus sont réglés (c'est automatique).
8. **Vérifier.** Ouvrez pascaldupont.fr sur ordinateur et sur téléphone, parcourez les pages et envoyez-vous un message par le formulaire de contact.

## Après l'installation
- **Les vignettes de films** viennent de YouTube et s'affichent automatiquement.
- **Icône du site (favicon)** : *Apparence, Personnaliser, Identité du site, Icône du site* (image carrée d'au moins 512 pixels).
- **Portrait** : sur la page À propos, remplacez le cadre « Portrait à ajouter » (bloc *Couverture*, bouton *Remplacer*).
- **Modifier un texte** : ouvrez la page dans *Pages*, cliquez sur le texte et tapez, comme dans un traitement de texte.
- **Mentions légales** : complétez le statut, le SIRET et l'adresse (repérés en pointillés).
- **Politique de confidentialité** : à faire relire.

## Si quelque chose ne va pas
- **L'ancien design s'affiche encore** : *Apparence, Thèmes* et vérifiez que « Pascal Dupont (Kadence, thème enfant) » est actif. Videz le cache du navigateur.
- **Le menu est vide ou l'accueil est une liste d'articles** : *Réglages, Lecture*, choisissez « Une page statique » avec « Accueil ». *Apparence, Menus*, assignez « Menu principal » à l'emplacement principal.
- **Le message du formulaire n'arrive pas** : regardez les courriers indésirables. Si besoin, installez l'extension gratuite « WP Mail SMTP » pour fiabiliser l'envoi.
- **Dans tous les cas** : envoyez-moi une capture d'écran, je corrige ici, vous renvoyez le zip.

## Pour les modifications futures (maintenance par Claude)
- Les textes validés sont dans `contenu/site.json`. Le générateur `outils/pages_kadence.py` en fait les pages. `outils/empaqueter.py` fabrique le zip et le fichier d'import.
- Les fiches `outils/kadence-reference/*.md` documentent, avec essais à l'appui, tous les réglages de Kadence et de Kadence Blocks utilisés.
