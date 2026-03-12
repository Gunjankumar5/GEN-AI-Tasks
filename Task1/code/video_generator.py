"""
video_generator.py - Build a video from a script using MoviePy.
- Splits script into scenes (sentences)
- Fetches a relevant image via LoremFlickr (free, no API key needed)
- Overlays text on each scene using PIL (no ImageMagick required)
- Concatenates scenes and exports as MP4
"""

import os
import textwrap
import requests
from pathlib import Path

from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 24
SECONDS_PER_SCENE = 4


def create_video(script: str, title: str, output_path: str) -> bool:
    """
    Create a video from the script.

    Args:
        script: Narration text broken into sentences for scenes.
        title: Topic title used for image search.
        output_path: File path for the output MP4.

    Returns:
        True if video was created successfully, False otherwise.
    """
    sentences = _split_into_scenes(script)
    clips = []

    for i, sentence in enumerate(sentences):
        print(f"    Rendering scene {i + 1}/{len(sentences)}: {sentence[:50]}...")

        # Get background image as PIL Image
        bg_array = _get_background_image(title, i)
        bg_img = Image.fromarray(bg_array)

        # Draw text overlay using PIL
        composite_array = _draw_text_on_image(bg_img, sentence)

        # Create clip from composite image
        clip = (
            ImageClip(composite_array)
            .set_duration(SECONDS_PER_SCENE)
            .set_fps(FPS)
        )
        clips.append(clip)

    if not clips:
        print("  [Error] No scenes generated.")
        return False

    # Concatenate all scenes
    final_video = concatenate_videoclips(clips, method="compose")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(output_path, fps=FPS, codec="libx264", audio=False, logger=None)
    return True


def _draw_text_on_image(bg_img: Image.Image, text: str) -> np.ndarray:
    """
    Draw wrapped text with a semi-transparent bar at the bottom of the image
    using Pillow only (no ImageMagick dependency).
    """
    img = bg_img.copy().convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_size = 36
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=55)
    lines = wrapped.split("\n")

    # Measure text block height
    line_height = font_size + 8
    text_block_h = line_height * len(lines) + 20
    bar_top = VIDEO_HEIGHT - text_block_h - 60

    # Draw semi-transparent dark bar
    draw.rectangle([(0, bar_top), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=(0, 0, 0, 160))

    # Draw each line centered
    y = bar_top + 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - text_w) // 2
        # Shadow
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 200))
        # White text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height

    combined = Image.alpha_composite(img, overlay).convert("RGB")
    return np.array(combined)


def _split_into_scenes(script: str) -> list:
    """Split script into individual sentences for scenes."""
    import re
    sentences = re.split(r"(?<=[.!?])\s+", script.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def _get_background_image(query: str, index: int) -> np.ndarray:
    """
    Fetch a keyword-relevant image from LoremFlickr (free, no API key needed),
    or fall back to a coloured gradient placeholder.

    Args:
        query: Search keyword.
        index: Scene index (used for image variation).

    Returns:
        Numpy array (H, W, 3) representing the image.
    """
    img = _fetch_loremflickr_image(query, index)
    if img is not None:
        return img
    return _generate_placeholder(index)


def _fetch_loremflickr_image(query: str, index: int) -> np.ndarray | None:
    """
    Download a free, keyword-relevant image from loremflickr.com.
    Requires no API key. Uses scene index as a cache-busting lock parameter
    so each scene can get a different image for the same topic.
    """
    import io
    keyword = "_".join(query.split()[:4])  # keep query short and URL-safe
    url = f"https://loremflickr.com/{VIDEO_WIDTH}/{VIDEO_HEIGHT}/{keyword}?lock={index}"
    try:
        r = requests.get(url, timeout=12, allow_redirects=True)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB").resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        return np.array(img)
    except Exception:
        return None


def _generate_placeholder(index: int) -> np.ndarray:
    """Create a gradient coloured placeholder image."""
    colours = [
        ((30, 60, 114), (42, 82, 190)),
        ((11, 59, 108), (0, 160, 176)),
        ((83, 52, 131), (163, 37, 132)),
        ((30, 87, 153), (125, 185, 232)),
    ]
    c1, c2 = colours[index % len(colours)]

    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    for x in range(VIDEO_WIDTH):
        ratio = x / VIDEO_WIDTH
        r = int(c1[0] + (c2[0] - c1[0]) * ratio)
        g = int(c1[1] + (c2[1] - c1[1]) * ratio)
        b = int(c1[2] + (c2[2] - c1[2]) * ratio)
        draw.line([(x, 0), (x, VIDEO_HEIGHT)], fill=(r, g, b))

    return np.array(img)