#!/usr/bin/env python3
import argparse
import asyncio
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, VideoClip
import numpy as np
import os
import sys

async def capture(url, selector, img_out):
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--disable-dev-shm-usage'])
        # Vertical viewport 1080x1920 with high pixel density
        page = await browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1.5)
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(2000) # Let animations and fonts load
        except Exception as e:
            print(f"Warning during navigation: {e}")
        
        # Try to hide annoying cookie banners
        await page.evaluate("""
            document.querySelectorAll('[id*="cookie"], [class*="cookie"], [id*="banner"], [class*="banner"]').forEach(el => el.style.display = 'none');
        """)
        
        box = None
        if selector and selector.lower() != "none":
            try:
                elem = await page.wait_for_selector(selector, timeout=5000)
                await elem.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000) # Wait for Scroll
                box = await elem.bounding_box()
            except Exception as e:
                print(f"Failed to find or highlight selector '{selector}': {e}")
                
        await page.screenshot(path=img_out, full_page=False)
        await browser.close()
        return box

def process(url, selector, audio_in, output_mp4):
    img_tmp = "/tmp/capture_temp.png"
    box = asyncio.run(capture(url, selector, img_tmp))
    
    if not os.path.exists(img_tmp):
        print("Error: Failed to capture screenshot.")
        sys.exit(1)

    img = Image.open(img_tmp)
    scale = 1.5 # Same as device_scale_factor
    
    center_x = img.width / 2
    center_y = img.height / 2

    # Draw Red Box
    if box:
        draw = ImageDraw.Draw(img)
        x = box['x'] * scale
        y = box['y'] * scale
        w = box['width'] * scale
        h = box['height'] * scale
        
        thickness = 8
        draw.rectangle([x-thickness, y-thickness, x+w+thickness, y+h+thickness], outline="#FF2A2A", width=thickness)
        
        # New center for zoom target
        center_x = x + w/2
        center_y = y + h/2

    img_red_box_path = "/tmp/capture_boxed.png"
    img.save(img_red_box_path)
    print(f"Saved highlighted frame. Target center: ({center_x:.1f}, {center_y:.1f})")

    # Load Audio and calculate duration
    if not os.path.exists(audio_in):
        print(f"Error: Audio file {audio_in} not found.")
        sys.exit(1)

    audio = AudioFileClip(audio_in)
    dur = audio.duration
    
    # Setup Ken Burns Zoom in MoviePy
    img_np = np.array(img)
    img_h, img_w, _ = img_np.shape
    out_w, out_h = 1080, 1920
    
    def make_frame(t):
        p = min(1.0, t / dur)
        # Easing function for smoother stop
        ease_p = 1 - pow(1 - p, 3) 
        
        zoom_start = 1.0
        # Zoom tighter if a specific box was targeted, else subtle zoom
        zoom_end = 2.0 if box else 1.2
        current_zoom = zoom_start + (zoom_end - zoom_start) * ease_p
        
        cw = img_w / current_zoom
        ch = img_h / current_zoom
        
        # Pan from center of image to target box
        cx = (img_w / 2) * (1 - ease_p) + (center_x) * ease_p
        cy = (img_h / 2) * (1 - ease_p) + (center_y) * ease_p
        
        # Crop logic
        left = max(0, cx - cw/2)
        top = max(0, cy - ch/2)
        right = min(img_w, left + cw)
        bottom = min(img_h, top + ch)
        
        crop_box = (left, top, right, bottom)
        frame_img = img.crop(crop_box).resize((out_w, out_h), Image.Resampling.LANCZOS)
        return np.array(frame_img)

    clip = VideoClip(make_frame, duration=dur)
    clip = clip.set_audio(audio)
    
    print(f"Writing final video to {output_mp4} (Duration: {dur:.2f}s)")
    # Important: Use superfast preset and few threads to avoid docker container OOM and freeze
    clip.write_videofile(
        output_mp4,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        threads=2,
        logger=None # Disable TQDM progress bar for cleaner logs
    )
    print("Video generation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Director for Tech B-Rolls")
    parser.add_argument("--url", required=True, help="Website URL to capture")
    parser.add_argument("--selector", default="none", help="CSS selector to highlight with a red box")
    parser.add_argument("--audio", required=True, help="Path to the TTS audio file")
    parser.add_argument("--output", required=True, help="Path to save the output MP4")
    
    args = parser.parse_args()
    process(args.url, args.selector, args.audio, args.output)
