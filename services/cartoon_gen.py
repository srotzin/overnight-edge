#!/usr/bin/env python3
"""Cartoon Scribble Generator for Overnight Edge Alerts"""

from PIL import Image, ImageDraw, ImageFont
import random
import os

CARTOON_DIR = "/mnt/user/overnight-edge/cartoons"
os.makedirs(CARTOON_DIR, exist_ok=True)

# Color palette (vibrant, sketchy)
COLORS = {
    "trump": {"skin": "#FFCCAA", "hair": "#FFD700", "suit": "#1a1a2e", "tie": "#e63946"},
    "pelosi": {"skin": "#FFCCAA", "hair": "#e0e0e0", "suit": "#457b9d", "tie": "#f1faee"},
    "graham": {"skin": "#FFCCAA", "hair": "#e0e0e0", "suit": "#264653", "tie": "#2a9d8f"},
    "gates": {"skin": "#FFCCAA", "hair": "#a8a8a8", "suit": "#1d3557", "tie": "#e63946"},
    "generic": {"skin": "#FFCCAA", "hair": "#4a4a4a", "suit": "#264653", "tie": "#e9c46a"},
}

def scribble_line(draw, x1, y1, x2, y2, color, width=2, jitter=3):
    """Draw a wobbly, hand-drawn style line"""
    points = []
    steps = max(abs(x2-x1), abs(y2-y1)) // 5 + 3
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t + random.randint(-jitter, jitter)
        y = y1 + (y2 - y1) * t + random.randint(-jitter, jitter)
        points.append((x, y))
    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=color, width=width)

def draw_face(draw, cx, cy, size, colors):
    """Draw a simple cartoon face with scribble style"""
    r = size
    
    # Face outline (scribble circle)
    for angle in range(0, 360, 15):
        import math
        x1 = cx + r * math.cos(math.radians(angle)) + random.randint(-2, 2)
        y1 = cy + r * math.sin(math.radians(angle)) + random.randint(-2, 2)
        x2 = cx + r * math.cos(math.radians(angle + 15)) + random.randint(-2, 2)
        y2 = cy + r * math.sin(math.radians(angle + 15)) + random.randint(-2, 2)
        draw.line([(x1, y1), (x2, y2)], fill=colors["skin"], width=2)
    
    # Fill face
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=colors["skin"], outline=colors["skin"], width=2)
    
    # Eyes
    eye_y = cy - r//4
    eye_offset = r//3
    eye_r = r//5
    draw.ellipse([cx-eye_offset-eye_r, eye_y-eye_r, cx-eye_offset+eye_r, eye_y+eye_r], fill="white", outline="black", width=2)
    draw.ellipse([cx+eye_offset-eye_r, eye_y-eye_r, cx+eye_offset+eye_r, eye_y+eye_r], fill="white", outline="black", width=2)
    # Pupils (looking in a direction)
    pupil_r = eye_r // 2
    draw.ellipse([cx-eye_offset-pupil_r, eye_y-pupil_r, cx-eye_offset+pupil_r, eye_y+pupil_r], fill="black")
    draw.ellipse([cx+eye_offset-pupil_r+2, eye_y-pupil_r, cx+eye_offset+pupil_r+2, eye_y+pupil_r], fill="black")
    
    # Mouth (expression based on alert type)
    mouth_y = cy + r//3
    mouth_w = r//2
    # Smirk or open mouth
    draw.arc([cx-mouth_w, mouth_y-r//4, cx+mouth_w, mouth_y+r//4], start=0, end=180, fill="black", width=2)
    
    # Hair (messy scribble)
    hair_color = colors["hair"]
    for _ in range(15):
        hx = cx + random.randint(-r-5, r+5)
        hy = cy - r + random.randint(-10, 5)
        draw.line([(hx, hy), (hx + random.randint(-15, 15), hy - random.randint(5, 20))], fill=hair_color, width=3)
    
    # Hair fill
    draw.ellipse([cx-r-5, cy-r-15, cx+r+5, cy-r+5], fill=hair_color, outline=hair_color)

def draw_body(draw, cx, cy, size, colors):
    """Draw simple body with suit"""
    r = size
    # Shoulders
    body_top = cy + r + 5
    body_w = r + 10
    body_h = int(r * 1.5)
    
    # Suit
    draw.rectangle([cx-body_w, body_top, cx+body_w, body_top+body_h], fill=colors["suit"], outline="black", width=2)
    
    # Tie
    tie_w = r // 3
    draw.polygon([(cx, body_top), (cx-tie_w, body_top+body_h//2), (cx+tie_w, body_top+body_h//2)], fill=colors["tie"])
    draw.line([(cx, body_top), (cx, body_top+body_h//2)], fill="black", width=1)
    
    # Scribble lines on suit for texture
    for _ in range(5):
        y = body_top + random.randint(5, body_h-5)
        draw.line([(cx-body_w+5, y), (cx+body_w-5, y)], fill="black", width=1)

def draw_speech_bubble(draw, x, y, w, h, text, font=None):
    """Draw a speech bubble with text"""
    # Bubble outline (scribble rectangle with rounded corners)
    r = 15
    
    # Draw bubble body
    draw.rounded_rectangle([x, y, x+w, y+h], radius=r, fill="white", outline="black", width=2)
    
    # Pointer to face
    points = [(x + w//2 - 10, y+h), (x + w//2, y+h+15), (x + w//2 + 10, y+h)]
    draw.polygon(points, fill="white", outline="black")
    draw.line([(x + w//2 - 10, y+h), (x + w//2, y+h+15)], fill="black", width=2)
    draw.line([(x + w//2, y+h+15), (x + w//2 + 10, y+h)], fill="black", width=2)
    
    # Text
    if font:
        # Wrap text
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            bbox = draw.textbbox((0,0), test, font=font)
            if bbox[2] - bbox[0] < w - 20:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        
        line_h = (draw.textbbox((0,0), "Ag", font=font)[3] - draw.textbbox((0,0), "Ag", font=font)[1]) + 4
        text_y = y + 15
        for line in lines:
            draw.text((x + 15, text_y), line, fill="black", font=font)
            text_y += line_h
    else:
        draw.text((x + 15, y + 15), text, fill="black")

def generate_cartoon(politician, alert_text, filename=None):
    """Generate a cartoon alert image"""
    
    # Map names to cartoon types
    name_map = {
        "trump": ["trump", "donald", "president"],
        "pelosi": ["pelosi", "nancy"],
        "graham": ["graham", "lindsey"],
        "gates": ["gates", "bill"],
    }
    
    ptype = "generic"
    p_lower = politician.lower()
    for key, names in name_map.items():
        if any(n in p_lower for n in names):
            ptype = key
            break
    
    colors = COLORS.get(ptype, COLORS["generic"])
    
    # Create image
    W, H = 600, 400
    img = Image.new("RGB", (W, H), "#f0f0f0")
    draw = ImageDraw.Draw(img)
    
    # Background scribbles
    for _ in range(20):
        x1, y1 = random.randint(0, W), random.randint(0, H)
        x2, y2 = x1 + random.randint(-50, 50), y1 + random.randint(-50, 50)
        draw.line([(x1, y1), (x2, y2)], fill="#e0e0e0", width=1)
    
    # Draw politician
    face_size = 50
    face_x = 120
    face_y = 180
    
    draw_body(draw, face_x, face_y, face_size, colors)
    draw_face(draw, face_x, face_y, face_size, colors)
    
    # Draw speech bubble
    bubble_x = 220
    bubble_y = 50
    bubble_w = 350
    bubble_h = 280
    
    # Try to load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = font
    
    draw_speech_bubble(draw, bubble_x, bubble_y, bubble_w, bubble_h, alert_text, font)
    
    # Add "Overnight Edge" branding
    draw.text((20, 370), "Overnight Edge — AI Market Intelligence", fill="#666666", font=small_font)
    
    # Save
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{CARTOON_DIR}/{ptype}_{timestamp}.png"
    
    img.save(filename)
    return filename

if __name__ == "__main__":
    # Test generation
    test = generate_cartoon(
        "Pelosi",
        "Just bought $1-5M of NVDA calls! Stock Act filing shows purchase on May 1. Confluence score: 4/5.",
        f"{CARTOON_DIR}/test_pelosi.png"
    )
    print(f"Generated: {test}")
    
    test2 = generate_cartoon(
        "Trump",
        "DJT 8-K filing: New media partnership announced. Stock up 12% pre-market.",
        f"{CARTOON_DIR}/test_trump.png"
    )
    print(f"Generated: {test2}")
