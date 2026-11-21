# EMCI TV Afrique — Playlist IPTV

Source Dailymotion : https://geo.dailymotion.com/videos/x8azdkm

## Installation GitHub

1. Ouvrir le dépôt public `techservicespro/emcitv-playlist` (ou le créer).
2. Envoyer **tous** les fichiers en conservant le chemin `.github/workflows/update.yml`.
3. Dans **Settings → Actions → General → Workflow permissions**, choisir **Read and write permissions** si nécessaire. Vérifier aussi que GitHub Actions est activé.
4. Ouvrir **Actions → Update EMCI TV Afrique playlist → Run workflow**.
5. Attendre la réussite, puis vérifier que `EMCI-TV.m3u` contient une ligne `#EXTINF` et une URL HLS. **Avant ce premier succès, le fichier est un modèle non lisible.**
6. Ajouter dans VLC ou IPTV Smarters :

   https://raw.githubusercontent.com/techservicespro/emcitv-playlist/main/EMCI-TV.m3u

Si votre compte, dépôt ou branche diffère, adapter l'URL.

## Fonctionnement et limites

Le script `update_emci.py` interroge les métadonnées Dailymotion, vérifie que l'URL renvoyée est bien un manifeste HLS, puis remplace la playlist. Le workflow tente une mise à jour environ toutes les 30 minutes ; les exécutions planifiées GitHub peuvent être retardées ou désactivées. Le lien de la playlist GitHub reste stable, mais les URL vidéo contiennent des jetons temporaires et peuvent expirer entre deux mises à jour ou pendant la lecture. Les lecteurs IPTV peuvent nécessiter un rechargement manuel.

L'accès automatisé et la redistribution des URL doivent respecter les conditions de Dailymotion et les droits du diffuseur. En cas de refus (403, etc.), le script conserve l'ancien fichier plutôt que de publier un lien invalide. Une lecture VLC réussie sur un poste ne garantit pas que les serveurs GitHub Actions auront accès au même flux.

## Dépannage

- **Actions échoue en 403** : l'accès peut être limité à certains clients/réseaux. Ne pas essayer de contourner ces restrictions ; demander un accès HLS officiel.
- **Push refusé** : vérifier les permissions d'écriture du workflow et les règles de protection de la branche.
- **Playlist inchangée** : vérifier les logs dans l'onglet Actions.
- **Flux ne joue plus** : relancer le workflow et recharger la playlist dans le lecteur ; cela peut ne pas suffire si la source a changé ses conditions d'accès.
