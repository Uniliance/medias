# Médias du Château Intérieur

Ce dépôt sert aux publications sur les **comptes communs du Château Intérieur** (Instagram, Facebook, YouTube).
Il a deux rôles, un par branche :

| Branche | Contenu | Rôle |
| --- | --- | --- |
| `main` (celle-ci) | ce README, `outils/`, `modeles/`, `polices/` | **la procédure** et les outils pour l'appliquer |
| `videos` | les fichiers prêts à publier, rangés par `AAAA/MM/`, et `reserve/` | **le quai de chargement** : Metricool vient y chercher les vidéos et images par leur adresse publique |

Adresse publique d'un fichier : `https://raw.githubusercontent.com/Uniliance/medias/videos/AAAA/MM/<fichier>`
(maximum 100 Mo par fichier).

**Pour l'utiliser, dites à votre IA :** « Lis le README du dépôt GitHub `Uniliance/medias` et applique-le à ma nouvelle vidéo. »

Chacun peut améliorer ce document : modifiez-le, et notez la modification dans le journal en bas.

---

## 1. Qui publie, et où

| Personne | Insta perso (Collab) | Page à mettre en avant |
| --- | --- | --- |
| Étienne | etienne_gigand | https://uniliance.life/praticiens/etienne-gigand/ |
| Martin | sapristouille_ | à préciser |
| Nathanaël | à compléter | https://uniliance.life/praticiens/nathanael-francisco/ |

- **Dépôt des vidéos brutes** : Drive `UNILIANCE / Média / Média Réseau / Dossier pour Claude`, partagé « Tous les utilisateurs disposant du lien » (lecteur). Un nom de fichier sans `~`.
- **Collab Insta** : la personne qui parle est toujours invitée ; les autres le sont quand le contenu les concerne (Ateliers Jaunes : Étienne + Martin).
- Le lien vers une page personnelle va dans la bio Insta de la personne, **jamais** dans la bio du compte collectif.

## 2. Les comptes communs

- **Metricool** : marque `le_chateau_interieur` (blogId `7801329`), fuseau `Europe/Paris`. Réseaux : Page Facebook « Le Château Intérieur », Instagram @le_chateau_interieur, chaîne YouTube « Uniliance ». Les identifiants sont à demander à Étienne ; ils ne sont **jamais** écrits dans ce dépôt.
- **Quota** : l'offre gratuite permet 20 publications programmées par mois (une par réseau). Faire le compte avant de programmer, et prévenir Étienne à l'approche de la limite (il passera à l'offre payante).
- **Une publication par jour** sur le fil commun, à midi de préférence. Avant de programmer, regarder le calendrier Metricool (`getScheduledPosts`) pour ne pas publier deux fois le même jour qu'un autre membre.

## 3. Ligne éditoriale

- **Chaque publication offre une clé du Château** : une chambre, une carte, un éclairage. La promotion (accompagnement, appli, replay d'atelier) vient en second.
- **Ton** : tutoiement, chaleureux, profond et léger à la fois. L'humour est bienvenu.
- **Mots qui comptent pour le référencement** : Château Intérieur, Spirale Dynamique, Ennéagramme, chambre NN.
- **Pas de partage personnel de participants** d'atelier, ni d'image où ils apparaissent.
- **Valider** textes et visuels avec la personne concernée avant de programmer.

## 4. Vidéo courte (Reel / Short)

1. **Télécharger** la vidéo depuis le Drive (fichier partagé par lien) :
   `curl -sSL -o brute.mp4 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`
2. **Transcrire** : `ffmpeg -i brute.mp4 -ac 1 -ar 16000 audio.wav` puis `python3 outils/transcrire.py` (faster-whisper `medium`, français, horodatage par mot).
   Corriger dans `transcript.json` : majuscules, « Château Intérieur », lapsus signalés (« compte » et non « page », « soi-même » et non « moi-même »…).
3. **Sous-titres** : `python3 outils/sous_titres.py transcript.json "Accroche" "suite en or"` → `subs.ass`.
   Poppins Bold 140, texte blanc, contour brun foncé, le mot prononcé s'allume en or `#FFD700`, au niveau de la poitrine (marge basse 620 px).
   Les morceaux sont coupés **à la largeur réelle** du texte (≤ 900 px, 4 mots au plus) : jamais de ligne repliée sur deux.
   L'accroche facultative s'affiche en haut pendant les 4 premières secondes.
4. **Miniature** (1080×1920) : une image de la vidéo avec une expression **ouverte et souriante** (pas de grimace ni de sourire forcé). Dégradé sombre en bas, petite accroche blanche, titre en 2 lignes (la 2e en or), Poppins Bold, texte entre y ≈ 1000 et 1400 pour rester visible dans la grille Insta.
5. **Montage** : `bash outils/montage.sh brute.mp4 subs.ass miniature.jpg final.mp4`
   - la miniature s'affiche 0,4 s en ouverture (elle sert aussi de couverture sur YouTube) ;
   - puis la vidéo sous-titrée ;
   - puis le **plan de fin fixe de 3 s**, identique à chaque fois (`modeles/plan-de-fin-chateau.png` : logo, « Accompagnement • Appli • Ressources », uniliance.life), avec un fondu de 0,3 s.
   Qualité : H.264, CRF 21, son AAC 160k, **moins de 100 Mo**.
6. **Héberger** : copier `final.mp4` et la miniature dans la branche `videos`, dossier `AAAA/MM/`, puis commit et push. Vérifier que les adresses publiques répondent.
7. **Textes**, un par réseau :
   - Instagram : accroche (citation de la vidéo), 2 à 4 lignes de fond, un pont vers le Château, puis « 👉 … : lien dans ma bio, @<insta perso> » (ou « uniliance.life, rubrique … ») et une dizaine de hashtags.
   - Facebook : même texte, avec le lien cliquable.
   - YouTube Short : titre court (35 à 50 caractères), description avec les liens.
8. **Programmer** dans Metricool, bien avant l'heure, en trois publications :
   - Instagram : `REEL`, `collaborators`, `showReelOnFeed: true`, `videoThumbnailUrl` = miniature ;
   - Facebook : `REEL`, `videoThumbnailUrl` = miniature ;
   - YouTube : `short`, `public`, `madeForKids: false`, **sans** miniature (la chaîne n'y a pas encore droit : la requête serait refusée).
   La première programmation renvoie des adresses `static.metricool.com` : les réutiliser pour les deux autres réseaux.
9. Au moment de la publication, chaque personne invitée **accepte la Collab** sur son Insta perso (ça ne s'automatise pas).

## 5. Image + texte (visuel citation)

- **Format** 1080×1350 (4:5), style du site : dégradé bleu ciel → pêche, halo doré, carte crème arrondie.
  En haut « ATELIER JAUNE · CHAMBRE NN » (Jost, brun `#8B4513`), citation en Cormorant Garamond avec la fin en italique cuivre (`#C17854`),
  en bas le nom de l'atelier et « Replay disponible · uniliance.life ».
- **Outil** : `python3 outils/citation.py "Ligne 1|Ligne 2" "Fin en italique|ligne 2" sortie.jpg 76 "Le Labyrinthe des ombres"`
- **Photo perso** : recadrée en 4:5, sans texte ajouté si elle parle d'elle-même.
- Programmer sur Instagram (`POST`) et Facebook (`POST`). YouTube n'accepte pas d'image via Metricool.

## 6. Promotion des replays d'Ateliers Jaunes

- **Sources** : Drive `UNILIANCE / DoJaune 💛` (Replays Bruts, Replays Cut). Les notes Gemini de chaque atelier contiennent le résumé, parfois la transcription complète. Gemini attribue parfois mal les voix : vérifier qui a dit quoi.
- **Liens des replays** : `src/_data/ateliers.json` du dépôt `Uniliance/site-uniliance`.
- **Extraits vidéo** : 35 à 45 s, un seul animateur à l'écran, sans voix hors champ ni participant. Recadrage vertical sur la personne qui parle. Préciser « extrait de l'Atelier Jaune NN » et que l'atelier complet est en replay.
- **Article sur le site** : suivre le `CLAUDE.md` du site, signer « Étienne Gigand et Martin Desbordes », ajouter des encadrés « 💛 Dans l'atelier » vers le replay, et ne pas tout dévoiler.

## 7. Contenus en réserve

Publications prêtes et validées, pour un jour sans autre contenu. Elles sont dans la branche `videos`, dossier `reserve/`
(visuel + fichier `.md` avec les textes Insta et Facebook). Une fois publiée, déplacer la publication dans `AAAA/MM/`.

| Publication | Réseaux | Validée |
| --- | --- | --- |
| Citation Atelier 76 « Tu ne souffres pas de tes émotions, mais du refus de les ressentir » | Insta + FB | 13 nov. 2026 |

## 8. Prérequis pour l'IA de chacun

- Accès au **Drive** (dossiers Média et DoJaune 💛).
- Accès au **dépôt GitHub** `Uniliance/medias` en écriture (membres de l'organisation Uniliance).
- **Connecteur Metricool** connecté au compte commun.
- Domaines autorisés dans les réglages de l'IA : `huggingface.co`, `*.hf.co` (modèle de transcription), `drive.google.com`, `drive.usercontent.google.com` (téléchargement des vidéos).
- Outils : Python 3 avec `faster-whisper` et `Pillow`, et `ffmpeg` avec libass. Les polices sont dans `polices/` (licence libre OFL).

## 9. Journal des modifications

- 9 nov. 2026 : première version (Google Doc), à partir des publications des 2 au 7 novembre.
- 13 nov. 2026 : la procédure passe dans ce README, avec les outils (`outils/`), le plan de fin, les polices et la réserve. Étienne, avec Claude.
