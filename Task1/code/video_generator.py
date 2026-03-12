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
    sentences = _split_into_scenes(script)
    clips = []

    for i, sentence in enumerate(sentences):
        print(f"    Rendering scene {i + 1}/{len(sentences)}: {sentence[:50]}...")

        bg_array = _get_background_image(title, i)
        bg_img = Image.fromarray(bg_array)

        composite_array = _draw_text_on_image(bg_img, sentence)

        clip = (
            ImageClip(composite_array)
            .set_duration(SECONDS_PER_SCENE)
            .set_fps(FPS)
        )
        clips.append(clip)

    if not clips:
        print("  [Error] No scenes generated.")
        return False

    final_video = concatenate_videoclips(clips, method="compose")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(output_path, fps=FPS, codec="libx264", audio=False, logger=None)
    return True


def _draw_text_on_image(bg_img: Image.Image, text: str) -> np.ndarray:
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

    line_height = font_size + 8
    text_block_h = line_height * len(lines) + 20
    bar_top = VIDEO_HEIGHT - text_block_h - 60

    draw.rectangle([(0, bar_top), (VIDEO_WIDTH, VIDEO_HEIGHT)], fill=(0, 0, 0, 160))

    y = bar_top + 10
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        x = (VIDEO_WIDTH - text_w) // 2
        draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 200))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_height

    combined = Image.alpha_composite(img, overlay).convert("RGB")
    return np.array(combined)


def _split_into_scenes(script: str) -> list:
    import re
    sentences = re.split(r"(?<=[.!?])\s+", script.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 5]


def _get_background_image(query: str, index: int) -> np.ndarray:
    img = _fetch_loremflickr_image(query, index)
    if img is not None:
        return img
    return _generate_placeholder(index)


def _fetch_loremflickr_image(query: str, index: int) -> np.ndarray | None:
    import io
    keyword = "_".join(query.split()[:4])
    url = f"https://loremflickr.com/{VIDEO_WIDTH}/{VIDEO_HEIGHT}/{keyword}?lock={index}"
    try:
        r = requests.get(url, timeout=12, allow_redirects=True)
        r.raise_for_status()
        img = Image.open(io.BytesIO(r.content)).convert("RGB").resize((VIDEO_WIDTH, VIDEO_HEIGHT))
        return np.array(img)
    except Exception:
        return None


def _generate_placeholder(index: int) -> np.ndarray:
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