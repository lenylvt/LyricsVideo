from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_audioclips
from moviepy import vfx, afx
import cv2
import os
import numpy as np
import json
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont
import textwrap

from images import LyricsFetcher, ImageMaker
from audio import AudioFetcher

@dataclass
class VideoConfig:
    """Configuration class for video generation settings"""
    fps: int = 30
    width: int = 1080  # 9:16 aspect ratio
    height: int = 1920  # 9:16 aspect ratio
    video_codec: str = 'libx264'
    audio_codec: str = 'aac'
    quality: str = 'medium'  # low, medium, high, ultra
    
@dataclass
class EffectConfig:
    """Configuration for visual effects"""
    sway_amplitude_x: float = 3.0  # Reduced for vertical format
    sway_amplitude_y: float = 5.0  # Increased for vertical format
    sway_speed: float = 4.0
    zoom_min: float = 1.0
    zoom_max: float = 1.02  # Slightly reduced for vertical format
    zoom_sharpness: float = 8.0
    zoom_decay_rate: float = 3.0
    fade_duration: float = 0.5
    enable_blur: bool = True
    blur_intensity: float = 0.5

class EffectsEngine:
    """Enhanced effects engine with more visual options"""
    
    def __init__(self, config: EffectConfig):
        self.config = config
    
    def get_sway_offsets(self, bpm: float, time: float) -> Tuple[float, float]:
        """Calculate sway offsets with improved smoothing"""
        frequency = bpm / 60.0 / self.config.sway_speed
        sway_x = self.config.sway_amplitude_x * np.sin(2 * np.pi * frequency * time)
        sway_y = self.config.sway_amplitude_y * np.cos(2 * np.pi * frequency * time)
        return float(sway_x), float(sway_y)
    
    def get_zoom_scale(self, bpm: float, time: float) -> float:
        """Calculate zoom scale with beat synchronization"""
        beats_per_second = bpm / 60.0
        beat_duration = 1.0 / beats_per_second
        time_within_beat = time % beat_duration
        
        if time_within_beat < beat_duration / 4:
            zoom_factor = self.config.zoom_min + (self.config.zoom_max - self.config.zoom_min) * \
                         (time_within_beat * self.config.zoom_sharpness)
        else:
            decay_time = time_within_beat - beat_duration / 4
            zoom_factor = self.config.zoom_max - (self.config.zoom_max - self.config.zoom_min) * \
                         (decay_time * self.config.zoom_decay_rate / beat_duration)
        
        return float(max(self.config.zoom_min, min(self.config.zoom_max, zoom_factor)))
    
    def get_fade_alpha(self, time: float, start_time: float, end_time: float) -> float:
        """Calculate fade alpha for smooth transitions"""
        if time < start_time + self.config.fade_duration:
            return (time - start_time) / self.config.fade_duration
        elif time > end_time - self.config.fade_duration:
            return (end_time - time) / self.config.fade_duration
        return 1.0
    
    def apply_blur_effect(self, img: np.ndarray, intensity: float) -> np.ndarray:
        """Apply blur effect based on intensity"""
        if not self.config.enable_blur or intensity <= 0:
            return img
        
        kernel_size = int(intensity * 10) + 1
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

class VideoMakerV2:
    """Enhanced video maker with 9:16 aspect ratio and direct MP4 export"""
    
    def __init__(self, folder: str, bpm: float, config: VideoConfig = None, effects_config: EffectConfig = None, 
                 artist_name: str = None, song_title: str = None, cover_path: str = None):
        self.folder = folder
        self.bpm = bpm
        self.config = config or VideoConfig()
        self.effects = EffectsEngine(effects_config or EffectConfig())
        
        # Informations du morceau
        self.artist_name = artist_name or "Unknown Artist"
        self.song_title = song_title or "Unknown Song"
        self.cover_path = cover_path
        
        # File paths - Direct MP4 export
        self.video_name = "output_v2_temp.mp4"
        self.audio_file = "audio.m4a"
        self.final_video_name = "output_v2_final.mp4"
        self.background_image = "../background.jpg"
        
        # Video metadata
        self.metadata = {
            "version": "2.0",
            "created_at": None,
            "duration": 0,
            "fps": self.config.fps,
            "resolution": f"{self.config.width}x{self.config.height}",
            "aspect_ratio": "9:16",
            "effects_applied": ["sway", "zoom", "beat_sync"],
            "artist": self.artist_name,
            "song": self.song_title
        }
    
    def resize_background_to_916(self, background_path: str) -> np.ndarray:
        """Resize and crop background image to 9:16 aspect ratio"""
        background = cv2.imread(background_path)
        if background is None:
            raise ValueError(f"Could not load background image: {background_path}")
        
        original_height, original_width = background.shape[:2]
        target_ratio = self.config.width / self.config.height
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
        background = background[top:bottom, left:right]
        
        # Resize to target dimensions
        background = cv2.resize(background, (self.config.width, self.config.height))
        
        return background
    
    def validate_inputs(self) -> bool:
        """Validate all required inputs before processing"""
        if not os.path.exists(self.folder):
            raise FileNotFoundError(f"Images folder not found: {self.folder}")
        
        if not os.path.exists(self.audio_file):
            raise FileNotFoundError(f"Audio file not found: {self.audio_file}")
        
        if not os.path.exists(self.background_image):
            raise FileNotFoundError(f"Background image not found: {self.background_image}")
        
        images = [img for img in os.listdir(self.folder) if img.endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            raise ValueError("No images found in the specified folder")
        
        return True
    
    def load_and_prepare_images(self) -> List[Dict]:
        """Charge et trie les images, en mettant title_card.jpg en premier s'il existe"""
        images = [img for img in os.listdir(self.folder) if img.endswith(('.jpg', '.jpeg', '.png'))]
        image_data = []
        # Gestion spéciale pour title_card.jpg
        title_card_path = os.path.join(self.folder, 'title_card.jpg')
        if 'title_card.jpg' in images:
            image_data.append({
                'filename': 'title_card.jpg',
                'timestamp': 0,
                'path': title_card_path
            })
            images.remove('title_card.jpg')
        # Les autres images (lyrics_xx.xx.jpg)
        for img in images:
            try:
                timestamp = int(float(img.split("_")[1].split(".")[0]))
                image_data.append({
                    'filename': img,
                    'timestamp': timestamp,
                    'path': os.path.join(self.folder, img)
                })
            except (IndexError, ValueError):
                print(f"Warning: Skipping image with invalid filename format: {img}")
                continue
        # Trie par timestamp (title_card.jpg reste en premier car timestamp=0)
        image_data[1:] = sorted(image_data[1:], key=lambda x: x['timestamp'])
        return image_data
    
    def apply_frame_effects(self, img: np.ndarray, time: float, width: int, height: int) -> np.ndarray:
        """Apply all visual effects to a single frame"""
        # Get effect parameters
        sway_x, sway_y = self.effects.get_sway_offsets(self.bpm, time)
        zoom_scale = self.effects.get_zoom_scale(self.bpm, time)
        
        # Center coordinates
        center_x, center_y = width / 2, height / 2
        
        # Apply zoom transformation
        transformation_matrix = np.float32([
            [zoom_scale, 0, (1 - zoom_scale) * center_x],
            [0, zoom_scale, (1 - zoom_scale) * center_y]
        ])
        processed_img = cv2.warpAffine(img, transformation_matrix, (width, height))
        
        # Apply sway transformation
        sway_matrix = np.float32([[1, 0, sway_x], [0, 1, sway_y]])
        processed_img = cv2.warpAffine(processed_img, sway_matrix, (width, height))
        
        return processed_img
    
    def add_image_sequence(self, video_writer, img: np.ndarray, start_time: float, 
                          duration: float, width: int, height: int) -> None:
        """Add a sequence of frames for a single image with effects (sans header overlay)"""
        total_frames = int(duration * self.config.fps)
        for frame_idx in range(total_frames):
            current_time = start_time + frame_idx / self.config.fps
            # Apply effects
            processed_frame = self.apply_frame_effects(img, current_time, width, height)
            # Write frame (plus d'overlay)
            video_writer.write(processed_frame)
    
    def create_video_metadata(self, duration: float) -> None:
        import datetime
        import numpy as np
        def make_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (datetime.datetime, datetime.date)):
                return obj.isoformat()
            return obj
        self.metadata.update({
            "created_at": datetime.datetime.now().isoformat(),
            "duration": duration,
            "bpm": self.bpm,
            "effects_applied": ["sway", "zoom", "beat_sync"]
        })
        # Correction ici : conversion pour JSON
        with open("video_metadata_v2.json", "w") as f:
            import json
            json.dump(self.metadata, f, indent=2, default=make_serializable)
    
    def make_video(self) -> str:
        """Create the video with enhanced error handling and progress tracking (sans overlay)"""
        try:
            # Validate inputs
            self.validate_inputs()
            # Load and prepare images
            image_data = self.load_and_prepare_images()
            if not image_data:
                raise ValueError("No valid images found")
            # Load and resize background image to 9:16
            background_frame = self.resize_background_to_916(self.background_image)
            height, width = self.config.height, self.config.width
            # header_overlay supprimé
            # Initialize video writer with MP4 codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(self.video_name, fourcc, self.config.fps, (width, height))
            if not video_writer.isOpened():
                raise RuntimeError("Could not open video writer")
            print(f"Creating 9:16 video with {len(image_data)} images...")
            # Add initial background if first image doesn't start at 0
            max_duration = 60  # Limite stricte TikTok
            if image_data[0]['timestamp'] > 0:
                bg_duration = min(image_data[0]['timestamp'], max_duration)
                print(f"Adding background for {bg_duration} seconds")
                self.add_image_sequence(video_writer, background_frame, 0, bg_duration, width, height)
            # Process each image
            total_duration = 0
            for idx, img_info in enumerate(image_data):
                if img_info['timestamp'] >= max_duration:
                    break  # On ne traite pas les images qui commencent après 60s
                print(f"Processing image {idx + 1}/{len(image_data)}: {img_info['filename']}")
                # Load image
                img = cv2.imread(img_info['path'])
                if img is None:
                    print(f"Warning: Could not load image {img_info['path']}, using background")
                    img = background_frame
                else:
                    # Images are already in 9:16 format from ImageMaker
                    img = cv2.resize(img, (width, height))
                # Calculate duration
                if idx < len(image_data) - 1:
                    next_timestamp = image_data[idx + 1]['timestamp']
                    duration = next_timestamp - img_info['timestamp']
                else:
                    duration = 4  # Default duration for last image
                # Ajuster la durée pour ne pas dépasser 60s
                end_time = img_info['timestamp'] + duration
                if end_time > max_duration:
                    duration = max_duration - img_info['timestamp']
                if duration <= 0:
                    break
                self.add_image_sequence(video_writer, img, img_info['timestamp'], duration, width, height)
                total_duration = img_info['timestamp'] + duration
                if total_duration >= max_duration:
                    break
            # Clean up
            video_writer.release()
            print(f"9:16 Video created successfully: {self.video_name}")
            # Create metadata
            self.create_video_metadata(min(total_duration, max_duration))
            return self.video_name
        except Exception as e:
            print(f"Error creating video: {str(e)}")
            raise
    
    def add_audio(self) -> str:
        """Add audio to video with enhanced options and direct MP4 export"""
        try:
            print("Adding audio to video...")
            # Load video and audio clips
            video_clip = VideoFileClip(self.video_name)
            audio_clip = AudioFileClip(self.audio_file)
            
            # Limiter la durée à 60 secondes max
            max_duration = 60
            video_duration = min(video_clip.duration, max_duration)
            
            if audio_clip.duration > video_duration:
                audio_clip = audio_clip.subclipped(0, video_duration)
            elif audio_clip.duration < video_duration:
                # Loop audio if it's shorter than video
                loops_needed = int(video_duration / audio_clip.duration) + 1
                audio_clips = [audio_clip] * loops_needed
                audio_clip = concatenate_audioclips(audio_clips).subclipped(0, video_duration)
            
            # Tronquer la vidéo si jamais elle dépasse 60s
            if video_clip.duration > max_duration:
                video_clip = video_clip.subclip(0, max_duration)
            
            # CORRECTION : Appliquer les effets avec with_effects()
            final_video = video_clip.with_effects([
                vfx.FadeOut(2),      # Fondu vidéo de 5 secondes
                afx.AudioFadeOut(2)  # Fondu audio de 5 secondes
            ]).with_audio(audio_clip)
            
            # Alternative si vous voulez séparer les effets :
            # video_with_fade = video_clip.with_effects([vfx.FadeOut(5)])
            # audio_with_fade = audio_clip.with_effects([afx.AudioFadeOut(5)])
            # final_video = video_with_fade.with_audio(audio_with_fade)
            
            # Quality settings based on config
            quality_settings = {
                'low': {'bitrate': '1500k', 'preset': 'ultrafast'},
                'medium': {'bitrate': '3000k', 'preset': 'medium'},
                'high': {'bitrate': '6000k', 'preset': 'slow'},
                'ultra': {'bitrate': '10000k', 'preset': 'veryslow'}
            }
            settings = quality_settings.get(self.config.quality, quality_settings['high'])
            
            # Write final video directly to MP4
            final_video.write_videofile(
                self.final_video_name,
                codec=self.config.video_codec,
                audio_codec=self.config.audio_codec,
                bitrate=settings['bitrate'],
                preset=settings['preset'],
                logger=None,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Clean up
            video_clip.close()
            audio_clip.close()
            final_video.close()
            
            print(f"Final 9:16 MP4 video created: {self.final_video_name}")
            return self.final_video_name
            
        except Exception as e:
            print(f"Error adding audio: {str(e)}")
            raise
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        temp_files = [self.video_name]
        for file in temp_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Cleaned up temporary file: {file}")
                except Exception as e:
                    print(f"Warning: Could not remove {file}: {str(e)}")
    
    def create_complete_video(self) -> str:
        """Create complete video with audio in one method"""
        try:
            print("Starting 9:16 video creation process...")
            
            # Create video
            video_file = self.make_video()
            
            # Add audio
            final_video = self.add_audio()
            
            # Cleanup temporary files
            self.cleanup_temp_files()
            
            print(f"Complete 9:16 MP4 video created successfully: {final_video}")
            return final_video
            
        except Exception as e:
            print(f"Error in complete video creation: {str(e)}")
            raise