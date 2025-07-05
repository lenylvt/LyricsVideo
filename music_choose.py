import requests
import random
import os
import time

def choose_random_track(playlist_id="6955605564"):
    """
    Choose a random track from a Deezer playlist with improved error handling
    """
    if playlist_id is None:
        playlist_id = os.getenv("PLAYLIST_ID")
    
    if not playlist_id:
        print("❌ Erreur : PLAYLIST_ID non défini dans les variables d'environnement")
        return None
    
    print(f"🔍 Tentative d'accès à la playlist Deezer ID: {playlist_id}")
    
    url = f'https://api.deezer.com/playlist/{playlist_id}'
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        # Check for API errors
        if 'error' in data:
            error_info = data['error']
            error_type = error_info.get('type', 'Unknown')
            error_message = error_info.get('message', 'Unknown error')
            error_code = error_info.get('code', 'Unknown')
            
            print(f"❌ Erreur API Deezer: {error_type} - {error_message} (Code: {error_code})")
            
            if error_code == 800:
                print("💡 Suggestions pour résoudre l'erreur 800:")
                print("   - Vérifiez que l'ID de playlist est correct")
                print("   - Assurez-vous que la playlist est publique")
                print("   - Testez avec une playlist publique connue (ex: 1362987571)")
            
            return None
        
        # Check response structure
        if not isinstance(data, dict) or 'tracks' not in data:
            print("❌ Erreur : structure de réponse Deezer inattendue")
            print(f"Réponse reçue: {data}")
            return None
        
        tracks_data = data['tracks']
        if not isinstance(tracks_data, dict) or 'data' not in tracks_data:
            print("❌ Erreur : pas de données de tracks dans la réponse")
            return None
        
        tracks = tracks_data['data']
        if not tracks:
            print("❌ Erreur : playlist vide")
            return None
        
        # Select random track
        track = random.choice(tracks)
        print(f"🎲 Musique choisie : {track['title']} par {track['artist']['name']}")
        
        # Get BPM from track details
        bpm = None
        try:
            track_id = track.get('id')
            if track_id:
                track_url = f'https://api.deezer.com/track/{track_id}'
                track_resp = requests.get(track_url, timeout=10)
                if track_resp.status_code == 200:
                    track_data = track_resp.json()
                    if 'error' not in track_data:
                        bpm = track_data.get('bpm')
        except Exception as e:
            print(f"⚠️ Impossible de récupérer le BPM Deezer : {e}")
            bpm = None
        
        return {
            'title': track['title'],
            'artist': track['artist']['name'],
            'isrc': track.get('isrc'),
            'deezer_link': track['link'],
            'bpm': bpm
        }
        
    except requests.exceptions.Timeout:
        print("❌ Erreur : timeout lors de l'accès à l'API Deezer")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur réseau : {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
        return None
