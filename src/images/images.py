
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import threading
import random
import math

from src.lyrics.lyrics import LyricsFetcher

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONT_PATH = os.path.join(PROJECT_ROOT, "assets", "font.ttf")
BACKGROUND_PATH = os.path.join(PROJECT_ROOT, "assets", "background.jpg")

class ImageMaker:
    def __init__(self, lyrics: list[dict]):
        self.lyrics = lyrics
        self.folder = "lyrics_images"
        
        # 9:16 aspect ratio dimensions
        self.target_width = 1080
        self.target_height = 1920

        if not os.path.exists(self.folder):
            os.mkdir(self.folder)
        else:
            for file in os.listdir(self.folder):
                os.remove(os.path.join(self.folder, file))

    def resize_background_to_916(self, background):
        """Resize and crop background image to 9:16 aspect ratio"""
        original_width, original_height = background.size
        target_ratio = self.target_width / self.target_height
        original_ratio = original_width / original_height
        
        if original_ratio > target_ratio:
            # Image is wider than target, crop width
            new_width = int(original_height * target_ratio)
            new_height = original_height
            left = (original_width - new_width) // 2
            top = 0
            right = left + new_width
            bottom = new_height
        else:
            # Image is taller than target, crop height
            new_width = original_width
            new_height = int(original_width / target_ratio)
            left = 0
            top = (original_height - new_height) // 2
            right = new_width
            bottom = top + new_height
        
        # Crop to correct aspect ratio
        background = background.crop((left, top, right, bottom))
        
        # Resize to target dimensions
        background = background.resize((self.target_width, self.target_height), Image.Resampling.LANCZOS)
        
        return background

    def add_modern_effects(self, background):
        """Ajoute des effets modernes à l'arrière-plan"""
        # Légère saturation pour des couleurs plus vives
        enhancer = ImageEnhance.Color(background)
        background = enhancer.enhance(1.3)
        
        # Léger flou gaussien pour un effet doux
        background = background.filter(ImageFilter.GaussianBlur(radius=1.5))
        
        # Overlay sombre pour améliorer la lisibilité
        overlay = Image.new('RGBA', background.size, (0, 0, 0, 80))
        background = background.convert('RGBA')
        background = Image.alpha_composite(background, overlay)
        
        return background.convert('RGB')

    def create_gradient_overlay(self, width, height, color1=(0, 0, 0, 120), color2=(0, 0, 0, 40)):
        """Crée un overlay avec dégradé"""
        gradient = Image.new('RGBA', (width, height), color1)
        draw = ImageDraw.Draw(gradient)
        
        # Dégradé vertical
        for y in range(height):
            alpha = int(color1[3] - (color1[3] - color2[3]) * (y / height))
            color = (*color1[:3], alpha)
            draw.line([(0, y), (width, y)], fill=color)
        
        return gradient

    def get_smart_font_size(self, text, max_width, max_height):
        """Calcule intelligemment la taille de police optimale"""
        words = text.split()
        base_size = int(0.08 * self.target_width)  # Taille de base plus grande
        
        # Ajuste selon la longueur du texte
        if len(words) <= 3:
            return base_size + 20  # Texte court = plus grand
        elif len(words) <= 6:
            return base_size + 10
        elif len(words) <= 10:
            return base_size
        else:
            return base_size - 10  # Texte long = plus petit

    def wrap_text_intelligent(self, text, font, max_width):
        """Découpe le texte de manière intelligente"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            
            if bbox[2] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return lines

    def make_image(self, line):
        timestamp = line["timestamp"]
        # Vérifier si la ligne est vide ou ne contient que des espaces
        if not line["line"].strip():
            line_text = "..."
        else:
            line_text = line["line"].upper()

        if not os.path.exists(BACKGROUND_PATH):
            raise FileNotFoundError(f"Le fichier de fond '{BACKGROUND_PATH}' est introuvable. Place-le dans le dossier assets/.")
        background = Image.open(BACKGROUND_PATH)
        
        # Resize background to 9:16 aspect ratio
        background = self.resize_background_to_916(background)
        
        # Appliquer des effets modernes
        background = self.add_modern_effects(background)
        
        width, height = background.size

        # Taille de police intelligente
        font_size = self.get_smart_font_size(line_text, width, height)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Marges adaptatives
        margin = int(0.1 * width)
        max_text_width = width - margin * 2
        
        # Découpage intelligent du texte
        lines = self.wrap_text_intelligent(line_text, font, max_text_width)
        wrapped_text = "\n".join(lines)

        # Créer une image temporaire pour calculer les dimensions du texte
        temp_img = Image.new('RGB', (width, height))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), wrapped_text, font=font)
        
        # Position du texte (centré)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2
        
        draw = ImageDraw.Draw(background)
        
        # Effet de texte multicouche pour plus de profondeur
        # Ombre portée
        shadow_offset = 4
        draw.text((text_x + shadow_offset, text_y + shadow_offset), wrapped_text, 
                 font=font, fill=(0, 0, 0, 100))
        
        # Contour pour la lisibilité
        outline_width = 2
        for adj in range(-outline_width, outline_width + 1):
            for adj2 in range(-outline_width, outline_width + 1):
                if adj != 0 or adj2 != 0:
                    draw.text((text_x + adj, text_y + adj2), wrapped_text, 
                             font=font, fill=(0, 0, 0, 180))
        
        # Texte principal avec léger gradient
        draw.text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255))
        
        # Créer un dégradé overlay subtil
        gradient = self.create_gradient_overlay(width, height, (0, 0, 0, 30), (0, 0, 0, 10))
        background = background.convert('RGBA')
        background = Image.alpha_composite(background, gradient)
        
        # Sauvegarder l'image finale
        background = background.convert('RGB')
        background.save(f"{self.folder}/lyrics_{timestamp}.jpg", quality=95, optimize=True)

    def make_images(self):
        threads = []

        for line in self.lyrics:
            thread = threading.Thread(target=self.make_image, args=(line,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def create_title_card(self, artist, title, duration=3.0):
        """Crée une carte de titre moderne pour le début de la vidéo"""
        if not os.path.exists(BACKGROUND_PATH):
            raise FileNotFoundError(f"Le fichier de fond '{BACKGROUND_PATH}' est introuvable. Place-le dans le dossier assets/.")
        background = Image.open(BACKGROUND_PATH)
        background = self.resize_background_to_916(background)
        background = self.add_modern_effects(background)
        
        width, height = background.size
        
        # Fonts pour le titre et l'artiste
        title_font = ImageFont.truetype(FONT_PATH, int(0.12 * width))
        artist_font = ImageFont.truetype(FONT_PATH, int(0.08 * width))
        
        # Créer l'overlay
        background = background.convert('RGBA')
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 120))
        background = Image.alpha_composite(background, overlay)
        
        draw = ImageDraw.Draw(background)
        
        # Calculer positions
        title_bbox = draw.textbbox((0, 0), title.upper(), font=title_font)
        artist_bbox = draw.textbbox((0, 0), artist.upper(), font=artist_font)
        
        title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
        title_y = height // 2 - 100
        
        artist_x = (width - (artist_bbox[2] - artist_bbox[0])) // 2
        artist_y = title_y + 120
        
        # Dessiner le titre
        draw.text((title_x, title_y), title.upper(), font=title_font, fill=(255, 255, 255))
        draw.text((artist_x, artist_y), artist.upper(), font=artist_font, fill=(200, 200, 200))
        
        # Ligne décorative
        line_width = 200
        line_x = (width - line_width) // 2
        line_y = artist_y + 150
        draw.rectangle([line_x, line_y, line_x + line_width, line_y + 3], fill=(255, 255, 255))
        
        background = background.convert('RGB')
        background.save(f"{self.folder}/title_card.jpg", quality=95, optimize=True)