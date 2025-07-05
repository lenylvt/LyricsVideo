from PIL import Image, ImageDraw, ImageFont
import threading
import os

from lyrics import LyricsFetcher

class ImageMaker:
    def __init__(self, lyrics : list[dict]):
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

    def make_image(self, line):
        timestamp = line["timestamp"]
        # Vérifier si la ligne est vide ou ne contient que des espaces
        if not line["line"].strip():
            line_text = "..."
        else:
            line_text = line["line"].upper()

        background = Image.open("../background.jpg")
        
        # Resize background to 9:16 aspect ratio
        background = self.resize_background_to_916(background)
        
        width, height = background.size

        # Adjust font size for 9:16 aspect ratio (smaller relative to width)
        font = ImageFont.truetype("../font.ttf", int(0.07 * width))  # 7% of width

        draw = ImageDraw.Draw(background)

        # Adjust margins for vertical format
        margin = int(0.08 * width)  # 8% of width as margin
        wrapped_line = ""

        for word in line_text.split():
            if font.getbbox(wrapped_line.split("\n")[-1] + word)[2] > width - margin * 2:
                wrapped_line += "\n"
            wrapped_line += word + " "

        wrapped_line = wrapped_line.strip()
        rows = wrapped_line.split("\n")

        centered_rows = []

        for row in rows:
            row = row.center(max([len(r) for r in rows]))
            centered_rows.append(row)
        
        wrapped_line = "\n".join(centered_rows)

        _, _, w, h = draw.textbbox((0, 0), wrapped_line, font=font)
        
        # Position text in the center of the 9:16 frame
        text_x = (width - w) / 2
        text_y = (height - h) / 2
        
        # Add text outline for better visibility
        outline_width = 3
        for adj in range(-outline_width, outline_width + 1):
            for adj2 in range(-outline_width, outline_width + 1):
                draw.text((text_x + adj, text_y + adj2), wrapped_line, font=font, fill=(0, 0, 0))
        
        # Draw main text
        draw.text((text_x, text_y), wrapped_line, font=font, fill=(255, 255, 255))

        background.save(f"{self.folder}/lyrics_{timestamp}.jpg")

    def make_images(self):
        threads = []

        for line in self.lyrics:
            thread = threading.Thread(target=self.make_image, args=(line,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()