import os
from pathlib import Path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
"""Script: make_hero_banner.py — compositing costume reale pe fundal curat."""
from PIL import Image
import numpy as np, os

BRAIN = r"C:\Users\ursac\.gemini\antigravity\brain\662a0445-9aa8-4814-8aa5-5b474c5f95d6"
COSTUMES_DIR = r"C:\Users\ursac\OneDrive\Desktop\Poze site superparty"
BG_PATH = os.path.join(BRAIN, "hero_bg_clean_1772752408143.png")
OUT_PATH = os.path.join(BRAIN, "hero_real_final.png")

W, H = 1280, 640

CHARS = [
    ("catalog_mickey_minnie_white_socks_1772227498889.png", "mickey"),
    ("catalog_unicorn_colorful_white_bg_1772228722896.png", "normal"),
    ("catalog_sonic_white_bg_1772227646947.png", "normal"),
    ("catalog_pikachu_white_bg_1772227634017.png", "normal"),
    ("catalog_princess_peach_white_bg_1772228877627.png", "normal"),
    ("catalog_tinkerbel_white_bg_1772228708465.png", "normal"),
    ("catalog_minion_white_bg_1772228616789.png", "normal"),
    ("catalog_minnie_pink_white_bg_1772228695778.png", "normal"),
]

def remove_white(img, mode="normal"):
    if mode == "mickey":
        w, h = img.size
        img = img.crop((0, 0, int(w * 0.46), h))
    d = np.array(img.convert("RGB"), dtype=np.uint8)
    mn = np.minimum(np.minimum(d[:,:,0], d[:,:,1]), d[:,:,2]).astype(np.int32)
    alpha = np.full(mn.shape, 255, dtype=np.uint8)
    alpha[mn >= 240] = 0
    fade = (mn >= 215) & (mn < 240)
    alpha[fade] = ((240 - mn[fade]) * 255 // 25).clip(0, 255).astype(np.uint8)
    return Image.fromarray(np.dstack([d, alpha]), "RGBA")

bg_sq = Image.open(BG_PATH).convert("RGB")
scale = max(W / bg_sq.width, H / bg_sq.height)
nw, nh = int(bg_sq.width * scale), int(bg_sq.height * scale)
bg = bg_sq.resize((nw, nh), Image.LANCZOS)
l, t = (nw - W) // 2, (nh - H) // 2
bg = bg.crop((l, t, l + W, t + H)).convert("RGBA")
print(f"BG: {W}x{H}")

n = len(CHARS)
target_h = int(H * 0.96)
slot_w = W // n

for i, (fname, mode) in enumerate(CHARS):
    img = Image.open(os.path.join(COSTUMES_DIR, fname))
    costume = remove_white(img, mode)
    ow, oh = costume.size
    max_w = slot_w - 2
    new_w = int(ow * target_h / oh)
    th = target_h
    if new_w > max_w:
        new_w = max_w
        th = int(oh * new_w / ow)
    costume = costume.resize((new_w, th), Image.LANCZOS)
    x = i * slot_w + (slot_w - new_w) // 2
    y = H - th
    bg.paste(costume, (x, y), costume)
    print(f"[{i+1}/{n}] {fname[:32]:34} x={x}")

bg.convert("RGB").save(OUT_PATH)
print("DONE:", OUT_PATH)
