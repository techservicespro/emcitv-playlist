EMCI TV Afrique — Playlist IPTV
Source : https://geo.dailymotion.com/videos/x8azdkm
Playlist publique : https://raw.githubusercontent.com/techservicespro/emcitv-playlist/main/EMCI-TV.m3u
Installation
Décompresser l'archive et transférer les quatre fichiers dans le dépôt `techservicespro/emcitv-playlist`, en conservant le dossier caché `.github/workflows/`.
Remplacer les fichiers existants. Attention : `EMCI-TV.m3u` est fourni comme modèle non lisible ; la première exécution réussie doit le remplir.
Dans GitHub, ouvrir Actions → Update EMCI TV Afrique playlist → Run workflow.
Ouvrir le journal Update EMCI TV playlist et vérifier la présence de `HLS manifest reachable from runner`.
Ouvrir `EMCI-TV.m3u` pour vérifier que l'adresse HLS a été enregistrée.
Tester l'adresse de la playlist dans VLC. Un succès dans GitHub Actions ne garantit pas que VLC ou une Smart TV pourra lire le flux.
Ce qui a été corrigé
Actions `checkout@v5` et `setup-python@v6` (Node.js 24).
Concurrence limitée à une exécution à la fois.
Journal UTC et empreinte SHA-256 tronquée pour comparer les URL sans divulguer le jeton dans les logs.
Distinction explicite entre « manifeste accessible depuis GitHub » et « flux lisible ailleurs ».
Préservation du fichier précédent en cas d'échec, avec un message d'erreur explicite.
Limites importantes
Les URL `?sec=...` de Dailymotion sont temporaires et peuvent être soumises à des contrôles d'accès (403). La playlist GitHub est statique entre deux exécutions et ne génère pas un jeton adapté à chaque lecteur. La programmation GitHub Actions toutes les 30 minutes est approximative, pas garantie à la minute. Même un workflow vert ne prouve pas que la vidéo est lisible sur un autre réseau ou appareil. Ce projet ne contourne pas les restrictions Dailymotion ; un accès HLS officiel et autorisé reste préférable pour une IPTV multi-appareils.
