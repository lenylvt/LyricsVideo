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

## Automatisation avec GitHub Actions

Le projet est entièrement automatisé grâce à GitHub Actions. À chaque push sur la branche `main` (ou lancement manuel), le workflow :

1. Installe Python, les dépendances du projet et ffmpeg.
2. Récupère les clés et tokens nécessaires via les **GitHub Secrets**.
3. Exécute automatiquement le script principal `main.py`.

### Secrets à configurer

Pour que l'automatisation fonctionne, il faut ajouter les secrets suivants dans les paramètres du dépôt GitHub (Settings > Secrets and variables > Actions) :

- `YOUTUBE_API_KEY` : Clé API YouTube Data v3
- `TIKTOK_CLIENT_KEY` : Clé client TikTok
- `TIKTOK_CLIENT_SECRET` : Secret client TikTok
- `TIKTOK_REDIRECT_URI` : URI de redirection TikTok (ex : https://singer.lenylvt.cc/)
- `TIKTOK_TOKEN_JSON` : (optionnel mais recommandé) Le contenu JSON du token TikTok déjà généré

Le script crée automatiquement le fichier `tiktok_tokens.txt` à partir de `TIKTOK_TOKEN_JSON` si ce secret est présent. Les autres secrets sont utilisés pour rafraîchir le token ou en générer un nouveau si besoin.

### Fichier de workflow

Le workflow se trouve dans `.github/workflows/python-app.yml` et ressemble à ceci :

```yaml
name: Génération vidéo paroles automatique

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout du code
        uses: actions/checkout@v4
      - name: Configuration de Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Installation des dépendances
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Installation de ffmpeg
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg
      - name: Exécution du script principal
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          TIKTOK_CLIENT_KEY: ${{ secrets.TIKTOK_CLIENT_KEY }}
          TIKTOK_CLIENT_SECRET: ${{ secrets.TIKTOK_CLIENT_SECRET }}
          TIKTOK_REDIRECT_URI: ${{ secrets.TIKTOK_REDIRECT_URI }}
          TIKTOK_TOKEN_JSON: ${{ secrets.TIKTOK_TOKEN_JSON }}
        run: |
          python main.py
```

**Résultat :**
À chaque push ou lancement manuel, la génération et la publication de la vidéo TikTok sont totalement automatisées et sécurisées.
