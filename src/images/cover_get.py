import os
import requests
from urllib.parse import urlparse
from PIL import Image
import time

def download_cover(deezer_url, artwork_type='square', loops=1, audio=False, folder_name=None):
    """
    Download album cover from Deezer URL
    
    Args:
        deezer_url (str): Deezer URL of the album or track
        artwork_type (str): Type of artwork ('square', 'wide', etc.)
        loops (int): Number of loops for animated covers (ignored for static covers)
        audio (bool): Whether to include audio in animated covers (ignored)
        folder_name (str): Dossier de sauvegarde de la cover
    
    Returns:
        str: Path to the downloaded cover file, or None if failed
    """
    try:
        # Extract cover URL from Deezer
        cover_url = extract_deezer_artwork(deezer_url)
        
        if not cover_url:
            print("❌ Could not extract cover URL from Deezer")
            return None
        
        # Download the cover
        response = requests.get(cover_url, timeout=30)
        response.raise_for_status()
        
        # Determine file extension
        content_type = response.headers.get('content-type', '')
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'
        
        # Create filename (all covers are static from Deezer)
        filename = f"cover_{artwork_type}{ext}"
        
        # Déterminer le chemin de sauvegarde
        if folder_name and os.path.isdir(folder_name):
            save_path = os.path.join(folder_name, filename)
        else:
            save_path = filename
        
        # Save the file
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Cover downloaded: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"❌ Error downloading cover: {e}")
        return None

def extract_deezer_artwork(deezer_url):
    """
    Extract artwork URL from Deezer URL using Deezer API
    
    Args:
        deezer_url (str): Deezer URL (album, track, etc.)
    
    Returns:
        str: Direct URL to artwork, or None if failed
    """
    try:
        # Extract ID from Deezer URL
        if '/album/' in deezer_url:
            album_id = deezer_url.split('/album/')[-1].split('?')[0]
            api_url = f"https://api.deezer.com/album/{album_id}"
        elif '/track/' in deezer_url:
            track_id = deezer_url.split('/track/')[-1].split('?')[0]
            api_url = f"https://api.deezer.com/track/{track_id}"
        else:
            return None
        
        # Get data from Deezer API
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract cover URL
        if 'album' in data and 'cover_xl' in data['album']:
            return data['album']['cover_xl']
        elif 'cover_xl' in data:
            return data['cover_xl']
        elif 'album' in data and 'cover_big' in data['album']:
            return data['album']['cover_big']
        elif 'cover_big' in data:
            return data['cover_big']
        
        return None
        
    except Exception as e:
        print(f"❌ Error extracting Deezer artwork: {e}")
        return None



def get_deezer_cover_from_track_info(track_info):
    """
    Get cover URL from track info dictionary
    
    Args:
        track_info (dict): Track information dictionary
    
    Returns:
        str: Path to downloaded cover, or None if failed
    """
    try:
        # Try to get cover from deezer_link if available
        if 'deezer_link' in track_info:
            return download_cover(track_info['deezer_link'])
        
        # Try to search for the track and get cover
        artist = track_info.get('artist', '')
        title = track_info.get('title', '')
        
        if artist and title:
            # Search for the track on Deezer
            search_url = f"https://api.deezer.com/search"
            params = {
                'q': f'artist:"{artist}" track:"{title}"',
                'limit': 1
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data') and len(data['data']) > 0:
                track = data['data'][0]
                if 'album' in track and 'cover_xl' in track['album']:
                    return download_cover(track['album']['cover_xl'])
        
        return None
        
    except Exception as e:
        print(f"❌ Error getting Deezer cover: {e}")
        return None

def resize_cover(cover_path, size=(1000, 1000)):
    """
    Resize cover image to specified dimensions
    
    Args:
        cover_path (str): Path to the cover image
        size (tuple): Target size (width, height)
    
    Returns:
        str: Path to resized cover, or original path if failed
    """
    try:
        if not os.path.exists(cover_path):
            return cover_path
        
        with Image.open(cover_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize maintaining aspect ratio
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create new filename
            name, ext = os.path.splitext(cover_path)
            resized_path = f"{name}_resized{ext}"
            
            # Save resized image
            img.save(resized_path, quality=95)
            
            print(f"✅ Cover resized: {resized_path}")
            return resized_path
            
    except Exception as e:
        print(f"❌ Error resizing cover: {e}")
        return cover_path

def create_placeholder_cover(artist_name, song_title, size=(1000, 1000)):
    """
    Create a placeholder cover image when no cover is available
    
    Args:
        artist_name (str): Artist name
        song_title (str): Song title
        size (tuple): Image size (width, height)
    
    Returns:
        str: Path to placeholder cover
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a solid color background
        img = Image.new('RGB', size, color='#1a1a1a')
        draw = ImageDraw.Draw(img)
        
        # Try to use a nice font, fallback to default
        try:
            font_large = ImageFont.truetype("arial.ttf", 60)
            font_medium = ImageFont.truetype("arial.ttf", 40)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
        
        # Draw text
        text_color = '#ffffff'
        
        # Artist name
        draw.text((size[0]//2, size[1]//2-50), artist_name, 
                 fill=text_color, font=font_large, anchor='mm')
        
        # Song title
        draw.text((size[0]//2, size[1]//2+50), song_title, 
                 fill=text_color, font=font_medium, anchor='mm')
        
        # Save placeholder
        placeholder_path = "placeholder_cover.jpg"
        img.save(placeholder_path, quality=95)
        
        print(f"✅ Placeholder cover created: {placeholder_path}")
        return placeholder_path
        
    except Exception as e:
        print(f"❌ Error creating placeholder cover: {e}")
        return None