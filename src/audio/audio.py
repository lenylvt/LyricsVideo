import subprocess
import os
import librosa
import os
from dotenv import load_dotenv
import numpy as np
import time
import random

# Charge automatiquement les variables de .env
load_dotenv()  

# Si on trouve COOKIES_TXT, on recrée cookies.txt à la volée
cookie_blob = os.getenv("COOKIES_TXT")
cookies_path = os.path.join("assets", "cookies.txt")
if cookie_blob:
    os.makedirs(os.path.dirname(cookies_path), exist_ok=True)
    with open(cookies_path, "w") as f:
        f.write(cookie_blob)

class AudioFetcher:
    def __init__(self, browser=None, cookies_file=cookies_path):
        """
        Initialise AudioFetcher avec yt-dlp et gestion des cookies.
        
        :param browser: (str) nom du navigateur pour --cookies-from-browser (e.g., "chrome", "firefox", "edge", "safari").
        :param cookies_file: (str) chemin vers un fichier cookies Netscape pour --cookies (défaut "cookies.txt").
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
            # Utilise les cookies directement depuis le navigateur
            args += ['--cookies-from-browser', self.browser]
            print(f"🍪 Utilisation des cookies depuis {self.browser}")
        elif self.cookies_file:
            # Vérifie l'existence du fichier cookies
            if not os.path.exists(self.cookies_file):
                # Tente de recréer à partir de la variable d'environnement
                cookie_blob = os.getenv("COOKIES_TXT")
                if cookie_blob:
                    os.makedirs(os.path.dirname(self.cookies_file), exist_ok=True)
                    with open(self.cookies_file, "w") as f:
                        f.write(cookie_blob)
                    print(f"🍪 Fichier cookies recréé: {self.cookies_file}")
                else:
                    print("⚠️  Aucun cookie configuré - cela peut causer des problèmes avec YouTube")
                    return args
            args += ['--cookies', self.cookies_file]
            print(f"🍪 Utilisation du fichier cookies: {self.cookies_file}")
        else:
            print("⚠️  Aucun cookie configuré - cela peut causer des problèmes avec YouTube")
        
        return args
    
    def _add_anti_bot_measures(self, cmd):
        """Ajoute des mesures anti-détection de bot"""
        # User-Agent réaliste
        cmd += ['--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36']
        
        # Autres headers pour paraître plus humain
        cmd += ['--add-header', 'Accept-Language:fr-FR,fr;q=0.9,en;q=0.8']
        cmd += ['--add-header', 'Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8']
        
        # Limite la vitesse de téléchargement pour éviter d'être détecté
        cmd += ['--limit-rate', '1M']
        
        return cmd
    
    def _search_youtube(self, artist, title):
        """Recherche une vidéo sur YouTube avec yt-dlp en utilisant des cookies si fournis."""
        # Variations de requête pour améliorer les résultats
        queries = [
            f"{artist} {title}",
            f"{artist} {title} official",
            f"{artist} {title} audio",
            f"{artist} {title} lyrics",
            f'"{artist}" "{title}"'
        ]
        
        for i, query in enumerate(queries):
            print(f"🔍 Recherche (tentative {i+1}/5): {query}")
            
            cmd = ['yt-dlp', '--get-id', '--default-search', 'ytsearch1:']
            cmd = self._add_anti_bot_measures(cmd)
            cmd += self._build_cookie_args()
            cmd.append(query)
            
            try:
                # Délai aléatoire entre les requêtes pour éviter la détection
                if i > 0:
                    delay = random.uniform(1, 3)
                    print(f"⏳ Attente de {delay:.1f}s...")
                    time.sleep(delay)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    video_id = result.stdout.strip()
                    youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                    print(f"✅ Lien trouvé: {youtube_url}")
                    return youtube_url
                else:
                    print(f"❌ Erreur de recherche: {result.stderr.strip()}")
                    # Continue avec la prochaine requête
                    continue
                    
            except Exception as e:
                print(f"❌ Erreur lors de la recherche: {e}")
                continue
        
        print("❌ Aucun résultat trouvé après toutes les tentatives")
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
            'yt-dlp', 
            '--extract-audio', 
            '--audio-format', 'm4a',
            '--audio-quality', '0',  # Meilleure qualité audio
            '--output', output_filename,
            '--no-playlist',  # Évite de télécharger une playlist entière
            '--ignore-errors'  # Continue même en cas d'erreur mineure
        ]
        
        cmd = self._add_anti_bot_measures(cmd)
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
        """Calcule le BPM à partir d'un fichier audio avec librosa. Retourne le BPM (float) ou None en cas d'erreur."""
        if not os.path.exists(audio_path):
            print(f"❌ Fichier audio non trouvé: {audio_path}")
            return None
        try:
            print("🎵 Calcul du BPM en cours...")
            # Charge seulement les 2 premières minutes pour accélérer le calcul
            y, sr = librosa.load(audio_path, sr=None, mono=True, duration=120)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            if isinstance(tempo, (list, np.ndarray)):
                tempo = float(tempo.flatten()[0])
            else:
                tempo = float(tempo)
            print(f"✅ BPM calculé: {tempo:.1f}")
            return tempo
        except Exception as e:
            print(f"❌ Erreur lors du calcul du BPM: {e}")
            return None