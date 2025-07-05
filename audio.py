import requests
import json
import os
from pytubefix import YouTube
import librosa
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

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
        # Récupère le PO token et visitor data depuis les variables d'environnement
        self.po_token = os.getenv('PO_TOKEN')
        self.visitor_data = os.getenv('VISITOR_DATA')
        if not self.po_token:
            print("⚠️  PO_TOKEN non trouvé dans le fichier .env")
        if not self.visitor_data:
            print("⚠️  VISITOR_DATA non trouvé dans le fichier .env")
    
    def fetch_audio(self, artist, title, output_filename="audio.m4a"):
        """Récupère l'audio depuis YouTube avec gestion améliorée des erreurs"""
        link = self.scraper.get_link(artist, title)
        print(f"Lien trouvé: {link}")
        
        if link:
            # Méthode 1 : Essayer sans PO token (le plus simple et souvent suffisant)
            try:
                print("🔄 Tentative sans PO token (méthode recommandée)...")
                yt = YouTube(link)
                
                stream = yt.streams.filter(only_audio=True).first()
                
                if stream:
                    # Supprime l'ancien fichier s'il existe
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                    
                    # Télécharge avec le nom de fichier spécifié
                    out_file = stream.download(filename=os.path.splitext(output_filename)[0])
                    
                    # Renomme le fichier si nécessaire
                    if out_file != output_filename and os.path.exists(out_file):
                        os.rename(out_file, output_filename)
                        print(f"✅ Audio téléchargé: {output_filename}")
                    elif os.path.exists(output_filename):
                        print(f"✅ Audio téléchargé: {output_filename}")
                    else:
                        print("❌ Erreur: Le fichier téléchargé n'existe pas")
                        return False
                    
                    return True
                else:
                    print("❌ Aucun stream audio trouvé")
                    
            except Exception as e:
                print(f"❌ Erreur avec méthode simple: {e}")
            
            # Méthode 2 : Essayer avec le client WEB
            try:
                print("🔄 Tentative avec le client WEB...")
                yt = YouTube(link, client='WEB')
                stream = yt.streams.filter(only_audio=True).first()
                
                if stream:
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                    
                    out_file = stream.download(filename=os.path.splitext(output_filename)[0])
                    
                    if out_file != output_filename and os.path.exists(out_file):
                        os.rename(out_file, output_filename)
                        print(f"✅ Audio téléchargé: {output_filename}")
                    elif os.path.exists(output_filename):
                        print(f"✅ Audio téléchargé: {output_filename}")
                    else:
                        print("❌ Erreur: Le fichier téléchargé n'existe pas")
                        return False
                    
                    return True
                else:
                    print("❌ Aucun stream audio trouvé avec le client WEB")
                    
            except Exception as e2:
                print(f"❌ Erreur avec client WEB: {e2}")
            
            # Méthode 3 : Essayer avec différents clients
            for client_name in ['ANDROID', 'IOS', 'MWEB']:
                try:
                    print(f"🔄 Tentative avec le client {client_name}...")
                    yt = YouTube(link, client=client_name)
                    stream = yt.streams.filter(only_audio=True).first()
                    
                    if stream:
                        if os.path.exists(output_filename):
                            os.remove(output_filename)
                        
                        out_file = stream.download(filename=os.path.splitext(output_filename)[0])
                        
                        if out_file != output_filename and os.path.exists(out_file):
                            os.rename(out_file, output_filename)
                            print(f"✅ Audio téléchargé avec {client_name}: {output_filename}")
                        elif os.path.exists(output_filename):
                            print(f"✅ Audio téléchargé avec {client_name}: {output_filename}")
                        else:
                            print("❌ Erreur: Le fichier téléchargé n'existe pas")
                            continue
                        
                        return True
                    else:
                        print(f"❌ Aucun stream audio trouvé avec {client_name}")
                        
                except Exception as e3:
                    print(f"❌ Erreur avec client {client_name}: {e3}")
                    continue
            
            # Méthode 4 : Utiliser le PO token seulement si TOUT est configuré ET les autres méthodes ont échoué
            if self.po_token and self.visitor_data:
                try:
                    print("🔑 Dernière tentative avec PO token depuis .env...")
                    # Définir les variables d'environnement pour pytubefix
                    os.environ['PO_TOKEN'] = self.po_token
                    os.environ['VISITOR_DATA'] = self.visitor_data
                    
                    # Utiliser une approche non-interactive pour le PO token
                    import subprocess
                    import sys
                    
                    # Créer un script temporaire pour éviter l'input interactif
                    temp_script = f"""
import os
from pytubefix import YouTube

os.environ['PO_TOKEN'] = '{self.po_token}'
os.environ['VISITOR_DATA'] = '{self.visitor_data}'

try:
    yt = YouTube('{link}', use_po_token=True)
    stream = yt.streams.filter(only_audio=True).first()
    if stream:
        stream.download(filename='{os.path.splitext(output_filename)[0]}')
        print("SUCCESS")
    else:
        print("NO_STREAM")
except Exception as e:
    print(f"ERROR: {{e}}")
"""
                    
                    # Sauvegarder et exécuter le script temporaire
                    with open('temp_download.py', 'w') as f:
                        f.write(temp_script)
                    
                    result = subprocess.run([sys.executable, 'temp_download.py'], 
                                          capture_output=True, text=True, timeout=60)
                    
                    # Nettoyer le script temporaire
                    if os.path.exists('temp_download.py'):
                        os.remove('temp_download.py')
                    
                    if "SUCCESS" in result.stdout:
                        # Renommer le fichier si nécessaire
                        downloaded_files = [f for f in os.listdir('.') if f.startswith(os.path.splitext(output_filename)[0])]
                        if downloaded_files:
                            downloaded_file = downloaded_files[0]
                            if downloaded_file != output_filename:
                                os.rename(downloaded_file, output_filename)
                            print(f"✅ Audio téléchargé avec PO token: {output_filename}")
                            return True
                    else:
                        print(f"❌ Erreur avec PO token: {result.stdout}")
                        
                except Exception as e_po:
                    print(f"❌ Erreur lors du téléchargement avec PO token: {e_po}")
            
            print("❌ Toutes les méthodes ont échoué")
            return False
        else:
            print("❌ Aucun lien trouvé")
            return False
    
    def close(self):
        """Ferme le scraper"""
        self.scraper.close()

    def get_bpm_from_audio(self, audio_path="audio.m4a"):
        """
        Calcule le BPM à partir du fichier audio (par défaut audio.m4a) avec librosa.
        Retourne le BPM (float) ou None en cas d'erreur.
        """
        if not os.path.exists(audio_path):
            print(f"❌ Fichier audio non trouvé: {audio_path}")
            return None
            
        try:
            import librosa
            print("🎵 Calcul du BPM en cours...")
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
    # Vous pouvez aussi mettre la clé API dans le .env avec YOUTUBE_API_KEY=votre_cle
    # youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    # fetcher = AudioFetcher(youtube_api_key=youtube_api_key)
    
    try:
        # Récupère l'audio
        success = fetcher.fetch_audio("Daft Punk", "Get Lucky")
        
        if success:
            # Calcule le BPM
            bpm = fetcher.get_bpm_from_audio()
            if bpm:
                print(f"🎵 BPM: {bpm}")
            else:
                print("❌ Impossible de calculer le BPM")
        else:
            print("❌ Échec du téléchargement audio")
        
    finally:
        fetcher.close()