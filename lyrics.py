import json
import re
import requests
from MusicMatch import MusixMatchAPI

class LyricsFetcher:
    def __init__(self, artist: str, title: str):
        self.artist = artist
        self.title = title
        self.lyrics = []
        self.api = MusixMatchAPI()

    def fetch_lyrics(self):
        """Récupère les paroles synchronisées depuis MusicXMatch (richsync > subtitle > LRCLib)"""
        try:
            # Recherche sur MusicXMatch
            print(f"🔍 Recherche sur MusicXMatch: '{self.title}' par '{self.artist}'")
            search = self.api.search_tracks(f"{self.title} {self.artist}")
            
            if search["message"]["body"]["track_list"]:
                track_info = search["message"]["body"]["track_list"][0]["track"]
                track_id = track_info["track_id"]
                track_isrc = track_info.get("track_isrc")
                commontrack_id = track_info.get("commontrack_id")
                
                # 1. Tentative avec richsync
                print("🎵 Tentative richsync...")
                richsync_lyrics = self._get_richsync_lyrics(track_id, track_isrc, commontrack_id)
                if richsync_lyrics:
                    print(f"✅ Paroles richsync trouvées sur MusicXMatch")
                    self.lyrics = richsync_lyrics
                    return richsync_lyrics
                
                # 2. Tentative avec subtitle
                print("📝 Tentative subtitle...")
                subtitle_lyrics = self._get_subtitle_lyrics(track_id, track_isrc, commontrack_id)
                if subtitle_lyrics:
                    print(f"✅ Paroles subtitle trouvées sur MusicXMatch")
                    self.lyrics = subtitle_lyrics
                    return subtitle_lyrics
            
            # 3. Fallback vers LRCLib
            print("🔄 Fallback vers LRCLib...")
            lrclib_lyrics = self._fetch_from_lrclib()
            if lrclib_lyrics:
                print(f"✅ Paroles synchronisées trouvées sur LRCLib")
                self.lyrics = lrclib_lyrics
                return lrclib_lyrics
            
            print("❌ Aucune parole synchronisée trouvée")
            self.lyrics = []
            return None
                
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des paroles: {e}")
            self.lyrics = []
            return None

    def _get_richsync_lyrics(self, track_id, track_isrc, commontrack_id):
        """Récupère les paroles richsync depuis MusicXMatch"""
        try:
            # Essaie avec les différents identifiants disponibles
            richsync_data = None
            
            if track_isrc:
                try:
                    richsync = self.api.get_track_richsync(track_isrc=track_isrc)
                    richsync_data = self._extract_richsync_body(richsync)
                except:
                    pass
            
            if not richsync_data and commontrack_id:
                try:
                    richsync = self.api.get_track_richsync(commontrack_id=commontrack_id)
                    richsync_data = self._extract_richsync_body(richsync)
                except:
                    pass
            
            if not richsync_data and track_id:
                try:
                    richsync = self.api.get_track_richsync(track_id=track_id)
                    richsync_data = self._extract_richsync_body(richsync)
                except:
                    pass
            
            if richsync_data:
                return self._parse_richsync_lyrics(richsync_data)
            
            return None
                
        except Exception as e:
            print(f"❌ Erreur richsync: {e}")
            return None

    def _get_subtitle_lyrics(self, track_id, track_isrc, commontrack_id):
        """Récupère les paroles subtitle depuis MusicXMatch"""
        try:
            # Essaie avec les différents identifiants disponibles
            subtitle_data = None
            
            if track_isrc:
                try:
                    subtitle = self.api.get_track_subtitle(track_isrc=track_isrc, subtitle_format="lrc")
                    subtitle_data = self._extract_subtitle_body(subtitle)
                except:
                    pass
            
            if not subtitle_data and commontrack_id:
                try:
                    subtitle = self.api.get_track_subtitle(commontrack_id=commontrack_id, subtitle_format="lrc")
                    subtitle_data = self._extract_subtitle_body(subtitle)
                except:
                    pass
            
            if not subtitle_data and track_id:
                try:
                    subtitle = self.api.get_track_subtitle(track_id=track_id, subtitle_format="lrc")
                    subtitle_data = self._extract_subtitle_body(subtitle)
                except:
                    pass
            
            if subtitle_data:
                return self._parse_lrc_format(subtitle_data)
            
            return None
                
        except Exception as e:
            print(f"❌ Erreur subtitle: {e}")
            return None

    def _extract_richsync_body(self, richsync_response):
        """Extrait le corps des richsync de la réponse API"""
        try:
            body = richsync_response["message"]["body"]
            
            # Vérifier la structure de la réponse
            richsync_data = body.get("richsync")
            if richsync_data:
                richsync_body = richsync_data.get("richsync_body")
            else:
                richsync_body = body.get("richsync_body")
            
            if richsync_body and richsync_body.strip() != "":
                return richsync_body
            
            return None
        except:
            return None

    def _extract_subtitle_body(self, subtitle_response):
        """Extrait le corps des subtitles de la réponse API"""
        try:
            body = subtitle_response["message"]["body"]
            
            # Vérifier la structure de la réponse
            subtitle_data = body.get("subtitle")
            if subtitle_data:
                subtitle_body = subtitle_data.get("subtitle_body")
            else:
                subtitle_body = body.get("subtitle_body")
            
            if subtitle_body and subtitle_body.strip() != "":
                return subtitle_body
            
            return None
        except:
            return None

    def _fetch_from_lrclib(self):
        """Récupère les paroles depuis LRCLib"""
        try:
            artist_encoded = "+".join(self.artist.split())
            title_encoded = "+".join(self.title.split())
            
            url = f"https://lrclib.net/api/get?artist_name={artist_encoded}&track_name={title_encoded}"
            response = requests.get(url)
            data = response.json()

            # Vérifier si 'syncedLyrics' existe et n'est pas vide
            if "syncedLyrics" not in data or not data["syncedLyrics"]:
                return None

            synced_lyrics = data["syncedLyrics"].split("\n")
            formatted_lyrics = []

            for line in synced_lyrics:
                split_line = line.strip()[1:].split("] ")
                if len(split_line) == 1:
                    split_line[0] = split_line[0][:-1]

                timestamp = split_line[0]
                line_text = split_line[1] if len(split_line) == 2 else ""

                mins, sec = map(float, timestamp.split(":"))
                formatted_lyrics.append({
                    "timestamp": mins * 60 + sec,
                    "line": line_text
                })

            return formatted_lyrics

        except Exception as e:
            print(f"❌ Erreur LRCLib: {e}")
            return None

    def _parse_richsync_lyrics(self, richsync_body):
        """Parse les données richsync JSON en format compatible"""
        try:
            # Les richsync sont généralement en format JSON
            richsync_data = json.loads(richsync_body)
            formatted_lyrics = []
            
            # MusicXMatch richsync format peut varier, on essaie plusieurs structures
            if isinstance(richsync_data, list):
                # Format liste directe
                for item in richsync_data:
                    if isinstance(item, dict) and 'ts' in item and 'l' in item:
                        # Gestion des caractères dans les paroles
                        line_text = ""
                        if item['l'] and isinstance(item['l'], list):
                            for char_info in item['l']:
                                if isinstance(char_info, dict) and 'c' in char_info:
                                    line_text += char_info['c']
                        
                        formatted_lyrics.append({
                            "timestamp": float(item['ts']),
                            "line": line_text.strip()
                        })
            elif isinstance(richsync_data, dict):
                # Format objet avec clés
                if 'lyrics' in richsync_data:
                    for item in richsync_data['lyrics']:
                        if isinstance(item, dict) and 'ts' in item and 'l' in item:
                            line_text = ""
                            if item['l'] and isinstance(item['l'], list):
                                for char_info in item['l']:
                                    if isinstance(char_info, dict) and 'c' in char_info:
                                        line_text += char_info['c']
                            
                            formatted_lyrics.append({
                                "timestamp": float(item['ts']),
                                "line": line_text.strip()
                            })
            
            return formatted_lyrics if formatted_lyrics else None
            
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON valide, on essaie de parser comme du texte LRC
            return self._parse_lrc_format(richsync_body)
        except Exception as e:
            print(f"❌ Erreur lors du parsing richsync: {e}")
            return None

    def _parse_lrc_format(self, lyrics_text):
        """Parse le format LRC standard"""
        try:
            lines = lyrics_text.strip().split('\n')
            formatted_lyrics = []
            
            for line in lines:
                # Pattern pour les timestamps LRC [mm:ss.xx] ou [mm:ss:xx]
                match = re.match(r'\[(\d{2}):(\d{2})[\.:](\d{2})\](.*)', line.strip())
                if match:
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    centiseconds = int(match.group(3))
                    text = match.group(4).strip()
                    
                    timestamp = minutes * 60 + seconds + centiseconds / 100
                    formatted_lyrics.append({
                        "timestamp": timestamp,
                        "line": text
                    })
            
            return formatted_lyrics if formatted_lyrics else None
            
        except Exception as e:
            print(f"❌ Erreur lors du parsing LRC: {e}")
            return None

    def get_lyrics(self):
        """Retourne les paroles formatées"""
        return self.lyrics