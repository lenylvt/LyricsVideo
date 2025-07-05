import requests
import json
import os
from pytubefix import YouTube
import librosa
from urllib.parse import quote_plus

class Scraper:
    def __init__(self, api_key=None):
        """
        Initialise le scraper avec une clé API YouTube (optionnelle)
        Si pas de clé API, utilise une méthode alternative
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
    
    def get_link_with_api(self, artist, title):
        """Méthode utilisant l'API YouTube Data v3"""
        if not self.api_key:
            return None
            
        query = f"{artist} {title} audio officiel lyrics"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': 1,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'items' in data and len(data['items']) > 0:
                video_id = data['items'][0]['id']['videoId']
                return f"https://www.youtube.com/watch?v={video_id}"
        except requests.RequestException as e:
            print(f"Erreur API: {e}")
        
        return None
    
    def get_link_alternative(self, artist, title):
        """Méthode alternative sans API en scrapant la page de résultats"""
        query = quote_plus(f"{artist} {title} audio officiel lyrics")
        url = f"https://www.youtube.com/results?search_query={query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Recherche du premier lien vidéo dans le HTML
            content = response.text
            
            # Cherche les données JSON dans le script
            start_marker = 'var ytInitialData = '
            start_pos = content.find(start_marker)
            if start_pos != -1:
                start_pos += len(start_marker)
                end_pos = content.find('};', start_pos) + 1
                json_str = content[start_pos:end_pos]
                
                try:
                    data = json.loads(json_str)
                    # Navigation dans la structure JSON complexe de YouTube
                    contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                    
                    for section in contents:
                        if 'itemSectionRenderer' in section:
                            items = section['itemSectionRenderer'].get('contents', [])
                            for item in items:
                                if 'videoRenderer' in item:
                                    video_id = item['videoRenderer'].get('videoId')
                                    if video_id:
                                        return f"https://www.youtube.com/watch?v={video_id}"
                except json.JSONDecodeError:
                    pass
            
            # Méthode de fallback avec regex simple
            import re
            pattern = r'watch\?v=([a-zA-Z0-9_-]{11})'
            match = re.search(pattern, content)
            if match:
                video_id = match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
                
        except requests.RequestException as e:
            print(f"Erreur lors de la récupération: {e}")
        
        return None
    
    def get_link(self, artist, title):
        """Essaie d'abord l'API, puis la méthode alternative"""
        # Essaie d'abord avec l'API si disponible
        if self.api_key:
            link = self.get_link_with_api(artist, title)
            if link:
                return link
        
        # Sinon utilise la méthode alternative
        return self.get_link_alternative(artist, title)
    
    def close(self):
        """Méthode pour compatibilité avec l'ancienne version"""
        pass

class AudioFetcher:
    def __init__(self, youtube_api_key=None):
        """
        Initialise l'AudioFetcher
        
        Args:
            youtube_api_key (str, optional): Clé API YouTube Data v3
                Pour obtenir une clé : https://console.developers.google.com/
        """
        self.scraper = Scraper(youtube_api_key)
    
    def fetch_audio(self, artist, title):
        """Récupère l'audio depuis YouTube"""
        link = self.scraper.get_link(artist, title)
        print(f"Lien trouvé: {link}")
        
        if link:
            try:
                yt = YouTube(link)
                stream = yt.streams.filter(only_audio=True).first()
                
                if stream:
                    # Supprime l'ancien fichier s'il existe
                    if os.path.exists("audio.m4a"):
                        os.remove("audio.m4a")
                    
                    out_file = stream.download(filename="audio")
                    base, ext = os.path.splitext(out_file)
                    new_filename = "audio.m4a"
                    
                    # Renomme le fichier
                    if os.path.exists(out_file):
                        os.rename(out_file, new_filename)
                        print(f"Audio téléchargé: {new_filename}")
                    else:
                        print("Erreur: Le fichier téléchargé n'existe pas")
                else:
                    print("Aucun stream audio trouvé")
            except Exception as e:
                print(f"Erreur lors du téléchargement: {e}")
        else:
            print("Aucun lien trouvé")
    
    def close(self):
        """Ferme le scraper"""
        self.scraper.close()

    def get_bpm_from_audio(self, audio_path="audio.m4a"):
        """
        Calcule le BPM à partir du fichier audio (par défaut audio.m4a) avec librosa.
        Retourne le BPM (float) ou None en cas d'erreur.
        """
        try:
            import librosa
            y, sr = librosa.load(audio_path, sr=None, mono=True, duration=60)  # max 60s pour rapidité
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        except Exception as e:
            print(f"❌ Erreur lors du calcul du BPM avec librosa : {e}")
            return None

# Exemple d'utilisation
if __name__ == "__main__":
    # Option 1: Sans clé API (moins fiable)
    fetcher = AudioFetcher()
    
    # Option 2: Avec clé API YouTube (plus fiable)
    # fetcher = AudioFetcher(youtube_api_key="VOTRE_CLE_API_ICI")
    
    try:
        # Récupère l'audio
        fetcher.fetch_audio("Daft Punk", "Get Lucky")
        
        # Calcule le BPM
        # bpm = fetcher.get_bpm() # This line is removed as per the edit hint
        # if bpm:
        #     print(f"BPM: {bpm}")
        
    finally:
        fetcher.close()