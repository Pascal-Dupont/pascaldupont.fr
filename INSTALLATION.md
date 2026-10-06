# Installer le nouveau site sur WordPress (OVH)

Durée : environ 15 minutes. Vous n'avez rien à coder.

## Fichiers à récupérer sur GitHub
- `dist/kadence-pascal.zip` : le thème.
- `import/pages.xml` : les 9 pages du site (accueil, films, série Serval, à propos, défense et sécurité, LAKELAB, contact, mentions légales, confidentialité).

Pour chacun : ouvrez le fichier sur GitHub, puis cliquez sur l'icône « Download raw file » (flèche vers le bas, en haut à droite du fichier).

## Étapes
1. **Vider les anciennes pages.** Administration WordPress, *Pages*, cochez tout, *Actions groupées : Mettre à la corbeille*, puis ouvrez *Corbeille* et cliquez sur *Vider la corbeille*. Cela évite les conflits d'adresses.
2. **Installer Kadence.** *Apparence, Thèmes, Ajouter*, tapez « Kadence », cliquez sur *Installer*. **N'activez pas encore.** Ignorez les propositions de modèles de démarrage.
3. **Envoyer le thème enfant.** *Apparence, Thèmes, Ajouter, Téléverser un thème*, choisissez `kadence-pascal.zip`, *Installer*, puis *Activer*.
4. **Importer les pages.** *Outils, Importer*, ligne *WordPress*, *Installer maintenant*, puis *Lancer l'importeur*. Choisissez `pages.xml`, *Téléverser le fichier et l'importer*. Dans la liste *Attribuer à un utilisateur existant*, choisissez votre compte. Laissez décoché « Télécharger et importer les fichiers joints ». Cliquez sur *Envoyer*.
5. **Régler le site automatiquement.** Ouvrez le *Tableau de bord* : un message vert indique que la page d'accueil, le titre et les menus sont réglés.
6. **Vérifier.** Ouvrez pascaldupont.fr sur ordinateur et sur téléphone, parcourez toutes les pages et envoyez-vous un message par le formulaire de contact.

## Si quelque chose ne va pas
- **L'ancien design s'affiche encore** : *Apparence, Thèmes* et vérifiez que « Pascal Dupont (Kadence, thème enfant) » est actif. Videz le cache du navigateur.
- **Le menu est vide ou l'accueil est une liste d'articles** : *Réglages, Lecture*, choisissez « Une page statique » avec « Accueil ». *Apparence, Menus*, assignez « Menu principal » à l'emplacement principal.
- **Le message du formulaire n'arrive pas** : regardez les courriers indésirables. Si besoin, installez l'extension gratuite « WP Mail SMTP » pour fiabiliser l'envoi.
- **Dans tous les cas** : envoyez-moi une capture d'écran, je corrige le thème ici, vous renvoyez le zip.

## À compléter ensuite
- *Mentions légales* : statut, SIRET et adresse (repérés en pointillés).
- *Politique de confidentialité* : à faire relire.
- Portrait, logos, audiences du 1er RCP : voir `contenu/a-completer.md`.

## Pour les modifications futures
La maquette `maquette/index.html` est la source. Après modification, `python3 outils/construire.py` régénère le thème, le zip et les pages.
