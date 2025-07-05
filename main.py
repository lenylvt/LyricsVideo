import os
import json
import time
from video import LyricsFetcher, AudioFetcher, ImageMaker, VideoMakerV2
from music_choose import choose_random_track
from cover_get import download_cover
from post import TikTokPoster

# Sélection aléatoire d'une musique
print("🎲 Sélection aléatoire d'une musique...")

# Nouvelle boucle pour s'assurer d'avoir des paroles
max_attempts = 25
attempt = 0
lyrics_found = False

while attempt < max_attempts and not lyrics_found:
    track_info = choose_random_track()

    if track_info is None:
        print("❌ Impossible de sélectionner une musique. Arrêt du programme.")
        exit()

    artist_name = track_info['artist']
    song_title = track_info['title']
    isrc = track_info['isrc']

    print(f"🎵 Musique sélectionnée : {artist_name} - {song_title}")
    print(f"🔗 Lien Deezer : {track_info['deezer_link']}")

    # Récupération et téléchargement de la cover Deezer
    print("🎨 Téléchargement de la cover depuis Deezer...")

    animated_cover_path = None
    static_cover_path = None

    try:
        static_cover_path = download_cover(track_info['deezer_link'], artwork_type='square', loops=1, audio=False)
        if static_cover_path:
            print(f"✅ Cover téléchargée : {static_cover_path}")
        else:
            print("⚠️ Pas de cover disponible pour ce morceau sur Deezer")
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement de la cover : {e}")

    folder_name = f"{artist_name} - {song_title}"

    # Création du dossier si nécessaire
    if not os.path.exists(folder_name):
        os.mkdir(folder_name)

    os.chdir(folder_name)

    print(f"📁 Dossier de travail : {folder_name}")
    print(f"🎬 Création de la vidéo pour {artist_name} - {song_title}...")

    try:
        print("📝 Récupération des paroles...")
        lyrics_fetcher = LyricsFetcher(artist_name, song_title)
        lyrics = lyrics_fetcher.fetch_lyrics()
        if lyrics is None:
            print("❌ Pas de paroles trouvées pour ce morceau. On change de musique...")
            os.chdir("..")
            # Nettoyer le dossier créé si vide
            if not os.listdir(folder_name):
                os.rmdir(folder_name)
            attempt += 1
            continue
        print("✅ Paroles récupérées!")
        lyrics_found = True
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des paroles : {e}")
        os.chdir("..")
        if not os.listdir(folder_name):
            os.rmdir(folder_name)
        attempt += 1
        continue

# Si aucune musique avec paroles n'a été trouvée
if not lyrics_found:
    print("❌ Impossible de trouver une musique avec des paroles après plusieurs tentatives. Arrêt du programme.")
    exit()

# Le reste du code ne s'exécute que si des paroles ont été trouvées
print("🎵 Récupération de l'audio...")
audio_fetcher = AudioFetcher()
audio_fetcher.fetch_audio(artist_name, song_title)
print("✅ Audio récupéré!")

bpm = audio_fetcher.get_bpm()
print(f"🥁 BPM de la chanson : {bpm}")

print("🖼️ Création des images...")
images_maker = ImageMaker(lyrics_fetcher.get_lyrics())
if static_cover_path:
    images_maker.animated_cover_path = static_cover_path  # On utilise la cover statique comme image principale
images_maker.make_images()
print("✅ Images créées!")

print("🎬 Création de la vidéo...")
# Passer les informations du morceau au VideoMaker
video_maker = VideoMakerV2(
    folder=images_maker.folder, 
    bpm=bpm,
    artist_name=artist_name,
    song_title=song_title,
    cover_path=static_cover_path  # Utiliser la cover statique pour le header
)

# Créer la vidéo complète
final_video = video_maker.create_complete_video()

print(f"🎉 Vidéo terminée pour : {artist_name} - {song_title}")
print(f"📹 Fichier vidéo : {final_video}")

client_key = "sbawtqg84z43tqt1cv"
client_secret = "HkavHcbJQBcJgobVIU998XODCOJyq5z3"
redirect_uri = "https://singer.lenylvt.cc/"
token_path = "../tiktok_tokens.txt" if not os.path.exists("tiktok_tokens.txt") else "tiktok_tokens.txt"

def save_tokens(token_data, path=token_path):
    token_data["saved_at"] = int(time.time())
    with open(path, "w") as f:
        json.dump(token_data, f)

def load_tokens(path=token_path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def is_token_expired(token_data):
    now = int(time.time())
    expires_in = int(token_data.get("expires_in", 0))
    saved_at = int(token_data.get("saved_at", 0))
    return now > saved_at + expires_in - 60  # marge de 1 min

# === Authentification TikTok (OAuth2) ===
token_data = load_tokens()
if not token_data:
    print("🔑 Aucun token TikTok trouvé. Veuillez coller le code d'autorisation TikTok (après connexion via Login Kit) :")
    code = input("Code : ").strip()
    try:
        print("⏳ Échange du code contre un access_token...")
        token_data = TikTokPoster.exchange_code_for_token(
            client_key=client_key,
            client_secret=client_secret,
            code=code,
            redirect_uri=redirect_uri
        )
        save_tokens(token_data)
        print("✅ Token TikTok sauvegardé dans tiktok_tokens.txt")
    except Exception as e:
        print(f"❌ Erreur lors de l'échange du code TikTok : {e}")
        exit(1)
else:
    # Vérifie si le token est expiré et rafraîchis-le si besoin
    if is_token_expired(token_data):
        print("🔄 Token TikTok expiré, rafraîchissement en cours...")
        try:
            refreshed = TikTokPoster.refresh_access_token(
                client_key=client_key,
                client_secret=client_secret,
                refresh_token=token_data["refresh_token"]
            )
            save_tokens(refreshed)
            token_data = refreshed
            print("✅ Token TikTok rafraîchi.")
        except Exception as e:
            print(f"❌ Erreur lors du rafraîchissement du token TikTok : {e}")
            exit(1)

access_token = token_data["access_token"]
tiktok = TikTokPoster(access_token)
try:
    print("🔍 Récupération des infos du créateur TikTok...")
    creator_info = tiktok.query_creator_info()
    print(f"👤 Utilisateur TikTok : {creator_info.get('data', {}).get('creator_username', 'inconnu')}")
    print("🚀 Initialisation de l'upload vidéo (direct post) sur TikTok...")
    init_resp = tiktok.init_video_upload_inbox(final_video)
    upload_url = init_resp["data"]["upload_url"]
    publish_id = init_resp["data"]["publish_id"]
    print("⬆️ Upload de la vidéo en cours...")
    tiktok.upload_video_file(upload_url, final_video)
    print("⏳ Vérification du statut de la publication...")
    status = tiktok.fetch_post_status(publish_id)
    print(f"📢 Statut de la publication : {status}")
except Exception as e:
    print(f"❌ Erreur lors de la publication TikTok : {e}")
    if hasattr(e, 'response') and e.response is not None:
        print("Réponse TikTok :", e.response.text)