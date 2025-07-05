import requests
import random

def choose_random_track(playlist_id='13831509421'):
    url = f'https://api.deezer.com/playlist/{playlist_id}'
    response = requests.get(url)
    data = response.json()

    tracks = data['tracks']['data']
    if not tracks:
        print("Pas de musique dans la playlist... Ambiance Jean-Michel Silence.")
        return None

    track = random.choice(tracks)
    print("🎲 Musique choisie :", track['title'], "par", track['artist']['name'])

    # Récupérer le BPM via l'API track
    bpm = None
    try:
        track_id = track.get('id')
        if track_id:
            track_url = f'https://api.deezer.com/track/{track_id}'
            track_resp = requests.get(track_url)
            track_data = track_resp.json()
            bpm = track_data.get('bpm')
    except Exception as e:
        print(f"⚠️ Impossible de récupérer le BPM Deezer : {e}")
        bpm = None

    # Récupère les infos utiles
    return {
        'title': track['title'],
        'artist': track['artist']['name'],
        'isrc': track.get('isrc'),
        'deezer_link': track['link'],
        'bpm': bpm
    }