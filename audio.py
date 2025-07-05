import subprocess
import os
import librosa
from urllib.parse import quote_plus

class AudioFetcher:
    def __init__(self):
        """
        Initialise l'AudioFetcher avec yt-dlp uniquement
        """
        # Vérifie si yt-dlp est disponible
        if not self._check_ytdlp():
            raise Exception("yt-dlp n'est pas installé. Installez-le avec: pip install yt-dlp")
        
        print("✅ yt-dlp détecté")
    
    def _check_ytdlp(self):
        """Vérifie si yt-dlp est disponible"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _search_youtube(self, artist, title):
        """Recherche une vidéo sur YouTube avec yt-dlp"""
        query = f"{artist} {title} audio officiel lyrics"
        
        try:
            print(f"🔍 Recherche: {query}")
            
            # Utilise yt-dlp pour rechercher
            cmd = [
                'yt-dlp',
                '--get-id',
                '--default-search', 'ytsearch1:',
                query
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                video_id = result.stdout.strip()
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"✅ Lien trouvé: {youtube_url}")
                return youtube_url
            else:
                print(f"❌ Erreur de recherche: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return None
    
    def fetch_audio(self, artist, title, output_filename="audio.m4a"):
        """Récupère l'audio depuis YouTube avec yt-dlp"""
        
        # Recherche la vidéo
        youtube_url = self._search_youtube(artist, title)
        if not youtube_url:
            print("❌ Aucun lien trouvé")
            return False
        
        # Supprime l'ancien fichier s'il existe
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        try:
            print("🔄 Téléchargement avec yt-dlp...")
            
            # Commande yt-dlp pour télécharger uniquement l'audio
            cmd = [
                'yt-dlp',
                '--extract-audio',
                '--audio-format', 'm4a',
                '--output', output_filename,
                youtube_url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0 and os.path.exists(output_filename):
                print(f"✅ Audio téléchargé: {output_filename}")
                return True
            else:
                print(f"❌ Erreur yt-dlp: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return False
    
    def get_bpm_from_audio(self, audio_path="audio.m4a"):
        """
        Calcule le BPM à partir du fichier audio avec librosa.
        Retourne le BPM (float) ou None en cas d'erreur.
        """
        if not os.path.exists(audio_path):
            print(f"❌ Fichier audio non trouvé: {audio_path}")
            return None
            
        try:
            print("🎵 Calcul du BPM en cours...")
            y, sr = librosa.load(audio_path, sr=None, mono=True, duration=60)  # max 60s pour rapidité
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            print(f"✅ BPM calculé: {tempo:.1f}")
            return float(tempo)
        except Exception as e:
            print(f"❌ Erreur lors du calcul du BPM: {e}")
            return None