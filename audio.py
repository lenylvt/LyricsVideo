import subprocess
import os
import librosa
import os
from dotenv import load_dotenv

# Charge automatiquement les variables de .env
load_dotenv()  

# Si on trouve COOKIES_TXT, on recrée cookies.txt à la volée
cookie_blob = os.getenv("COOKIES_TXT")
if cookie_blob:
    with open("cookies.txt", "w") as f:
        f.write(cookie_blob)

class AudioFetcher:
    def __init__(self, browser=None, cookies_file="cookies.txt"):
        """
        Initialise AudioFetcher avec yt-dlp et gestion des cookies.
        
        :param browser: (str) nom du navigateur pour --cookies-from-browser (e.g., "chrome", "firefox").
        :param cookies_file: (str) chemin vers un fichier cookies Netscape pour --cookies.
        """
        self.browser = browser
        self.cookies_file = cookies_file
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
    
    def _build_cookie_args(self):
        """
        Retourne une liste d'arguments pour yt-dlp en fonction des cookies configurés.
        Préfère --cookies-from-browser si browser est défini, sinon --cookies si cookies_file est défini.
        """
        args = []
        if self.browser:
            args += ['--cookies-from-browser', self.browser]
        elif self.cookies_file:
            if not os.path.exists(self.cookies_file):
                raise FileNotFoundError(f"Fichier de cookies introuvable: {self.cookies_file}")
            args += ['--cookies', self.cookies_file]
        return args
    
    def _search_youtube(self, artist, title):
        """Recherche une vidéo sur YouTube avec yt-dlp en utilisant des cookies si fournis."""
        query = f"{artist} {title} audio officiel lyrics"
        print(f"🔍 Recherche: {query}")
        
        cmd = ['yt-dlp', '--get-id', '--default-search', 'ytsearch1:']
        cmd += self._build_cookie_args()
        cmd.append(query)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0 and result.stdout.strip():
                video_id = result.stdout.strip()
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"✅ Lien trouvé: {youtube_url}")
                return youtube_url
            else:
                print(f"❌ Erreur de recherche: {result.stderr.strip()}")
                return None
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return None
    
    def fetch_audio(self, artist, title, output_filename="audio.m4a"):
        """Télécharge l'audio depuis YouTube avec yt-dlp, en utilisant des cookies si disponibles."""
        youtube_url = self._search_youtube(artist, title)
        if not youtube_url:
            print("❌ Aucun lien trouvé pour la vidéo demandée.")
            return False
        
        if os.path.exists(output_filename):
            os.remove(output_filename)
        
        print("🔄 Téléchargement avec yt-dlp...")
        cmd = [
            'yt-dlp', '--extract-audio', '--audio-format', 'm4a',
            '--output', output_filename
        ]
        cmd += self._build_cookie_args()
        cmd.append(youtube_url)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and os.path.exists(output_filename):
                print(f"✅ Audio téléchargé: {output_filename}")
                return True
            else:
                print(f"❌ Erreur yt-dlp: {result.stderr.strip()}")
                return False
        except Exception as e:
            print(f"❌ Erreur lors du téléchargement: {e}")
            return False
    
    def get_bpm_from_audio(self, audio_path="audio.m4a"):
        """
        Calcule le BPM à partir d'un fichier audio avec librosa.
        Retourne le BPM (float) ou None en cas d'erreur.
        """
        if not os.path.exists(audio_path):
            print(f"❌ Fichier audio non trouvé: {audio_path}")
            return None
        
        try:
            print("🎵 Calcul du BPM en cours...")
            y, sr = librosa.load(audio_path, sr=None, mono=True, duration=60)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            print(f"✅ BPM calculé: {tempo:.1f}")
            return float(tempo)
        except Exception as e:
            print(f"❌ Erreur lors du calcul du BPM: {e}")
            return None