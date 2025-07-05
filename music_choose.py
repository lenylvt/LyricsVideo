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

    # Récupère les infos utiles
    return {
        'title': track['title'],
        'artist': track['artist']['name'],
        'isrc': track.get('isrc'),
        'deezer_link': track['link']
    }