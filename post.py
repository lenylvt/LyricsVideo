import requests
import os
from typing import Optional, Dict, Any
import math

# Chunk size limits based on TikTok API requirements
MIN_CHUNK_SIZE = 5 * 1024 * 1024       # 5 MB minimum for non-final chunks
MAX_CHUNK_SIZE = 64 * 1024 * 1024      # 64 MB maximum for all chunks

def _compute_chunk_params(file_size: int) -> tuple:
    """
    Calcule la taille de chunk et le nombre total de chunks selon la taille du fichier.
    Tous les chunks sauf le dernier font MAX_CHUNK_SIZE, le dernier peut être plus petit.
    """
    if file_size <= MAX_CHUNK_SIZE:
        return file_size, 1
    else:
        return MAX_CHUNK_SIZE, math.ceil(file_size / MAX_CHUNK_SIZE)

TIKTOK_API_BASE = "https://open.tiktokapis.com/v2/post/publish"
TIKTOK_VIDEO_INBOX_INIT = f"{TIKTOK_API_BASE}/inbox/video/init/"
TIKTOK_VIDEO_STATUS = f"{TIKTOK_API_BASE}/video/status/fetch/"

class TikTokPoster:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=UTF-8"
        }

    def query_creator_info(self) -> Dict[str, Any]:
        url = f"{TIKTOK_API_BASE}/creator_info/query/"
        resp = requests.post(url, headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def init_video_upload(self, title: str, privacy_level: str, video_path: str, disable_duet=False, disable_comment=True, disable_stitch=False, video_cover_timestamp_ms=1000) -> Dict[str, Any]:
        file_size = os.path.getsize(video_path)
        chunk_size, total_chunk_count = _compute_chunk_params(file_size)
        data = {
            "post_info": {
                "title": title,
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": video_cover_timestamp_ms
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunk_count
            }
        }
        url = f"{TIKTOK_API_BASE}/video/init/"
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def init_video_upload_inbox(self, video_path: str) -> dict:
        """
        Initialise l'upload vidéo en mode draft (inbox) sur TikTok.
        """
        file_size = os.path.getsize(video_path)
        chunk_size, total_chunk_count = _compute_chunk_params(file_size)
        data = {
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunk_count
            }
        }
        url = TIKTOK_VIDEO_INBOX_INIT
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def init_video_upload_direct_post(self, artist_name: str, song_title: str, video_path: str, privacy_level: str = "MUTUAL_FOLLOW_FRIENDS", disable_duet=False, disable_comment=True, disable_stitch=False, video_cover_timestamp_ms=1000) -> dict:
        """
        Initialise l'upload vidéo en mode direct post sur TikTok.
        """
        file_size = os.path.getsize(video_path)
        chunk_size, total_chunk_count = _compute_chunk_params(file_size)
        data = {
            "post_info": {
                "title": f"{artist_name} - {song_title}",
                "privacy_level": privacy_level,
                "disable_duet": disable_duet,
                "disable_comment": disable_comment,
                "disable_stitch": disable_stitch,
                "video_cover_timestamp_ms": video_cover_timestamp_ms
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": total_chunk_count
            }
        }
        url = f"{TIKTOK_API_BASE}/video/init/"
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def upload_video_file(self, upload_url: str, video_path: str) -> requests.Response:
        file_size = os.path.getsize(video_path)
        chunk_size, total_chunk_count = _compute_chunk_params(file_size)
        if total_chunk_count == 1:
            # Un seul chunk
            with open(video_path, "rb") as f:
                video_data = f.read()
            headers = {
                "Content-Range": f"bytes 0-{file_size-1}/{file_size}",
                "Content-Type": "video/mp4"
            }
            resp = requests.put(upload_url, headers=headers, data=video_data)
            resp.raise_for_status()
            return resp
        else:
            # Multi-chunk
            with open(video_path, "rb") as f:
                for chunk_index in range(total_chunk_count):
                    start = chunk_index * chunk_size
                    end = min(start + chunk_size, file_size) - 1
                    f.seek(start)
                    chunk_data = f.read(end - start + 1)
                    headers = {
                        "Content-Range": f"bytes {start}-{end}/{file_size}",
                        "Content-Type": "video/mp4"
                    }
                    resp = requests.put(upload_url, headers=headers, data=chunk_data)
                    resp.raise_for_status()
            return resp

    def fetch_post_status(self, publish_id: str) -> Dict[str, Any]:
        url = f"{TIKTOK_API_BASE}/status/fetch/"
        data = {"publish_id": publish_id}
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def post_photo(self, title: str, description: str, photo_urls: list, privacy_level: str = "PUBLIC_TO_EVERYONE", auto_add_music: bool = True, disable_comment: bool = True) -> Dict[str, Any]:
        url = f"{TIKTOK_API_BASE}/content/init/"
        data = {
            "post_info": {
                "title": title,
                "description": description,
                "disable_comment": disable_comment,
                "privacy_level": privacy_level,
                "auto_add_music": auto_add_music
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "photo_cover_index": 1,
                "photo_images": photo_urls
            },
            "post_mode": "DIRECT_POST",
            "media_type": "PHOTO"
        }
        resp = requests.post(url, headers=self.headers, json=data)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def exchange_code_for_token(client_key: str, client_secret: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Échange un code d'autorisation TikTok contre un access_token et un refresh_token (OAuth2)."""
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        data = {
            "client_key": client_key,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(url, data=data, headers=headers)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def refresh_access_token(client_key: str, client_secret: str, refresh_token: str) -> Dict[str, Any]:
        """Rafraîchit un access_token TikTok à partir d'un refresh_token."""
        url = "https://open.tiktokapis.com/v2/oauth/token/"
        data = {
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(url, data=data, headers=headers)
        resp.raise_for_status()
        return resp.json()