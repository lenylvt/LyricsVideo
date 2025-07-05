# 🎬 Lyrics Video Maker

Lyrics Video Maker est un outil automatisé en Python qui génère des vidéos de paroles synchronisées à partir d'une musique choisie aléatoirement sur Deezer, puis les publie automatiquement sur TikTok.

## Fonctionnalités

- Sélection aléatoire d'un morceau depuis une playlist Deezer.
- Téléchargement automatique de la cover de l'album.
- Récupération des paroles synchronisées (MusicXMatch, LRCLib).
- Génération d'images modernes pour chaque ligne de paroles (format vertical 9:16).
- Création d'une vidéo dynamique avec effets visuels synchronisés au rythme (BPM).
- Ajout automatique de l'audio extrait de YouTube.
- Publication automatisée sur TikTok (brouillon ou direct).

## Prérequis

- Python 3.8 ou supérieur
- ffmpeg installé sur votre système (requis par moviepy)
- Un compte TikTok avec accès à l'API (pour la publication automatique)
- Clé API YouTube Data v3 (optionnelle mais recommandée pour une meilleure fiabilité audio)

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/lyrics-video-maker.git
   cd lyrics-video-maker
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Placez une image de fond nommée `background.jpg` et une police `font.ttf` à la racine du projet.

## Utilisation

Lancez simplement le script principal :

```bash
python main.py
```

Le script :
- choisira une musique aléatoire,
- téléchargera la cover,
- récupérera les paroles synchronisées,
- générera les images et la vidéo,
- publiera la vidéo sur TikTok.

### Authentification TikTok

Lors de la première utilisation, le script vous demandera un code d'autorisation TikTok (OAuth2). Suivez les instructions affichées pour obtenir ce code via Login Kit.

Les tokens sont sauvegardés dans `tiktok_tokens.txt` pour les prochaines utilisations.

## Configuration

- Pour changer la playlist Deezer utilisée, modifiez l'ID dans `music_choose.py`.
- Pour utiliser votre propre clé API YouTube, renseignez-la dans `main.py` (variable `youtube_api_key`).

## Dépendances principales

- `requests`, `moviepy`, `opencv-python`, `numpy`, `Pillow`, `selenium`, `pytubefix`, `librosa`, `scipy`, `matplotlib`
- Voir `requirements.txt` pour la liste complète.

## Auteurs

- Par moi
- Basé sur des APIs publiques Deezer, YouTube, LRCLib, TikTok
- Crée grâce au Reverse de MusicMatch de Strvm : https://github.com/Strvm/musicxmatch-api et crée de base par Pranavgnn : https://github.com/pranavgnn/lyrics-video-maker.
