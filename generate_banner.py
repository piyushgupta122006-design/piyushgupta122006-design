"""
generate_banner.py
Exact implementation of the Master Prompt specification for GitHub Profile Banner.

Features:
- 1180x610 Terminal Window titled 'profile.sh --live'
- Left ~38%: 'VISUAL.MAP' with Floyd-Steinberg dithered matrix, intro shimmering, drift bands, and morphing travellers
- Right: 'SYSTEM.INFO' with locked textLength + lengthAdjust="spacingAndGlyphs", computed dotted leaders
- Dual theme support: dark.svg and light.svg
- Accurate SMIL animation with intro fade (~3.2s) and logo morph loop (~14.2s)
"""

import math
import random
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw

def floyd_steinberg_dither(img_gray, serpentine=True):
    """
    1-bit Floyd-Steinberg dithering with serpentine scan order.
    """
    arr = np.array(img_gray, dtype=np.float32)
    h, w = arr.shape
    out = np.zeros((h, w), dtype=np.uint8)
    
    for y in range(h):
        xs = range(w) if (y % 2 == 0 or not serpentine) else range(w - 1, -1, -1)
        direction = 1 if (y % 2 == 0 or not serpentine) else -1
        
        for x in xs:
            old_val = arr[y, x]
            new_val = 255.0 if old_val >= 128.0 else 0.0
            out[y, x] = 1 if new_val == 0.0 else 0
            err = old_val - new_val
            
            xr = x + direction
            if 0 <= xr < w:
                arr[y, xr] += err * (7.0 / 16.0)
            
            y_down = y + 1
            if y_down < h:
                x_bl = x - direction
                if 0 <= x_bl < w:
                    arr[y_down, x_bl] += err * (3.0 / 16.0)
                arr[y_down, x] += err * (5.0 / 16.0)
                x_br = x + direction
                if 0 <= x_br < w:
                    arr[y_down, x_br] += err * (1.0 / 16.0)
                    
    return out

def build_portrait_matrix(w=200, h=250, image_path=None):
    """
    Builds head+shoulders portrait dither matrix.
    """
    if image_path:
        try:
            im = Image.open(image_path).convert("RGBA")
            bg = Image.new("RGBA", im.size, (10, 16, 31, 255))
            bg.paste(im, (0, 0), im)
            gray = bg.convert("L")
            gray = ImageOps.autocontrast(gray, cutoff=1)
            gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
            gray = gray.resize((w, h), Image.Resampling.LANCZOS)
            return floyd_steinberg_dither(gray, serpentine=True)
        except Exception:
            pass

    # High fidelity cyber developer portrait matrix
    im = Image.new("L", (w, h), 245)
    draw = ImageDraw.Draw(im)
    
    cx, cy = w // 2, int(h * 0.40)
    head_r = int(w * 0.23)
    
    # Head & face shading
    for r in range(head_r, 0, -1):
        shade = int(50 + 130 * (r / head_r))
        draw.ellipse([cx - r, cy - int(r*1.15), cx + r, cy + int(r*0.95)], fill=shade)
        
    # Cap / Hair
    draw.ellipse([cx - int(head_r * 1.08), cy - int(head_r * 1.3), cx + int(head_r * 1.08), cy - int(head_r * 0.2)], fill=25)
    
    # Visor / Glasses
    visor_y = cy - int(head_r * 0.15)
    draw.rounded_rectangle([cx - int(head_r * 0.82), visor_y - 13, cx - 6, visor_y + 13], radius=4, fill=15)
    draw.rounded_rectangle([cx + 6, visor_y - 13, cx + int(head_r * 0.82), visor_y + 13], radius=4, fill=15)
    draw.rectangle([cx - 8, visor_y - 4, cx + 8, visor_y + 2], fill=25)
    
    # Visor reflections
    draw.line([cx - int(head_r * 0.65), visor_y + 7, cx - 14, visor_y - 7], fill=210, width=2)
    draw.line([cx + 14, visor_y + 7, cx + int(head_r * 0.65), visor_y - 7], fill=210, width=2)
    
    # Features
    draw.polygon([(cx, cy + 4), (cx - 4, cy + 18), (cx + 4, cy + 18)], fill=55)
    draw.arc([cx - 24, cy + 28, cx + 24, cy + 38], start=10, end=170, fill=35, width=3)
    draw.arc([cx - int(head_r*0.7), cy - 10, cx + int(head_r*0.7), cy + int(head_r*0.85)], start=30, end=150, fill=35, width=6)
    
    # Headphones
    draw.ellipse([cx - head_r - 10, cy - 25, cx - head_r + 6, cy + 25], fill=35)
    draw.ellipse([cx + head_r - 6, cy - 25, cx + head_r + 10, cy + 25], fill=35)
    draw.arc([cx - head_r, cy - int(head_r*1.2), cx + head_r, cy], start=190, end=350, fill=35, width=6)
    
    # Shoulders & Hoodie
    draw.polygon([
        (cx - int(w * 0.48), h),
        (cx - int(head_r * 0.9), cy + int(head_r * 0.85)),
        (cx + int(head_r * 0.9), cy + int(head_r * 0.85)),
        (cx + int(w * 0.48), h)
    ], fill=40)
    draw.line([(cx, cy + int(head_r * 0.85)), (cx, h)], fill=15, width=3)
    
    gray = im.filter(ImageFilter.GaussianBlur(0.8))
    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=140))
    return floyd_steinberg_dither(gray, serpentine=True)

def generate_logo_points(num_points=450, center=(240, 335), scale=90):
    """
    Generates 3 sets of point swarms for logo morphing:
    Logo 1: Code glyph </>
    Logo 2: Vercel Delta ▲
    Logo 3: React Atom Orbit ⚛
    """
    cx, cy = center
    rng = random.Random(1337)
    
    # 1. Code Glyph </>
    pts_code = []
    # Left bracket <
    for t in np.linspace(0, 1, num_points // 3):
        if t < 0.5:
            u = t * 2
            x = cx - scale*0.8 + u * (scale*0.4)
            y = cy - scale*0.6 + u * (scale*0.6)
        else:
            u = (t - 0.5) * 2
            x = cx - scale*0.4 - u * (scale*0.4)
            y = cy + u * (scale*0.6)
        pts_code.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))
        
    # Slash /
    for t in np.linspace(0, 1, num_points // 3):
        x = cx - scale*0.2 + t * (scale*0.4)
        y = cy + scale*0.7 - t * (scale*1.4)
        pts_code.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))
        
    # Right bracket >
    for t in np.linspace(0, 1, num_points - len(pts_code)):
        if t < 0.5:
            u = t * 2
            x = cx + scale*0.4 + u * (scale*0.4)
            y = cy - scale*0.6 + u * (scale*0.6)
        else:
            u = (t - 0.5) * 2
            x = cx + scale*0.8 - u * (scale*0.4)
            y = cy + u * (scale*0.6)
        pts_code.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))

    # 2. Vercel Triangle ▲
    pts_vercel = []
    per_side = num_points // 3
    # Left edge
    for t in np.linspace(0, 1, per_side):
        x = cx + (t - 0.5) * scale * 1.5
        y = cy + scale * 0.7 - t * scale * 1.4
        pts_vercel.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))
    # Right edge
    for t in np.linspace(0, 1, per_side):
        x = cx + scale * 0.75 - t * scale * 0.75
        y = cy + scale * 0.7 - (1 - t) * scale * 1.4
        pts_vercel.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))
    # Bottom edge
    for t in np.linspace(0, 1, num_points - len(pts_vercel)):
        x = cx - scale * 0.75 + t * scale * 1.5
        y = cy + scale * 0.7
        pts_vercel.append((x + rng.gauss(0, 1.2), y + rng.gauss(0, 1.2)))

    # 3. React Atom ⚛
    pts_react = []
    # Nucleus
    nucleus_count = num_points // 4
    for _ in range(nucleus_count):
        r = rng.uniform(0, scale * 0.22)
        ang = rng.uniform(0, 2 * math.pi)
        pts_react.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    # 3 Elliptical orbits
    orbit_pts = (num_points - len(pts_react)) // 3
    for rot in [0, math.pi / 3, 2 * math.pi / 3]:
        for t in np.linspace(0, 2*math.pi, orbit_pts):
            ex = scale * 0.85 * math.cos(t)
            ey = scale * 0.35 * math.sin(t)
            rx = cx + ex * math.cos(rot) - ey * math.sin(rot)
            ry = cy + ex * math.sin(rot) + ey * math.cos(rot)
            pts_react.append((rx + rng.gauss(0, 1.0), ry + rng.gauss(0, 1.0)))

    # Balance length
    while len(pts_react) < num_points:
        pts_react.append((cx, cy))
        
    # Sort for minimal trajectory matching (Optimal Transport proxy)
    pts_code = sorted(pts_code, key=lambda p: (p[0], p[1]))
    pts_vercel = sorted(pts_vercel, key=lambda p: (p[0], p[1]))
    pts_react = sorted(pts_react, key=lambda p: (p[0], p[1]))
    
    return pts_code, pts_vercel, pts_react

def build_banner_svg(theme="dark", image_path=None):
    """
    Generates exact 1180x610 SMIL animated SVG banner.
    """
    is_dark = (theme == "dark")
    
    # Exact Curated Palette from Master Prompt
    bg_color = "#0A101F" if is_dark else "#F8FAFC"
    panel_bg = "#0B1324" if is_dark else "#FFFFFF"
    frame_stroke = "#1E293B" if is_dark else "#E2E8F0"
    chrome_color = "#22D3EE" if is_dark else "#0891B2"
    portrait_color = "#A78BFA" if is_dark else "#7C3AED"
    accent_green = "#10B981" if is_dark else "#059669"
    text_muted = "#64748B" if is_dark else "#94A3B8"
    text_body = "#94A3B8" if is_dark else "#475569"
    text_val = "#F8FAFC" if is_dark else "#0F172A"
    leader_color = "#334155" if is_dark else "#CBD5E1"
    
    # 1. Portrait Dither Runs
    matrix = build_portrait_matrix(w=195, h=235, image_path=image_path)
    h, w = matrix.shape
    num_groups = 60  # ~60 interleaved random groups for shimmering intro
    groups = [[] for _ in range(num_groups)]
    rng = random.Random(42)
    
    offset_x, offset_y = 52, 118
    pitch_x, pitch_y = 1.9, 1.9
    dot_size = 1.5
    
    for y in range(h):
        x = 0
        while x < w:
            if matrix[y, x] == 1:
                start_x = x
                while x < w and matrix[y, x] == 1:
                    x += 1
                run_len = x - start_x
                grp_idx = rng.randint(0, num_groups - 1)
                
                px = offset_x + start_x * pitch_x
                py = offset_y + y * pitch_y
                p_width = (run_len - 1) * pitch_x + dot_size
                
                path_chunk = f"M{px:.1f},{py:.1f}h{p_width:.1f}v{dot_size:.1f}h-{p_width:.1f}Z "
                groups[grp_idx].append(path_chunk)
            else:
                x += 1

    # 2. Travellers Layer (~450 morphing dots)
    pts_code, pts_vercel, pts_react = generate_logo_points(num_points=420, center=(240, 335), scale=85)
    
    # 3. Info Table Rows
    rows = [
        ("Subject", "Piyush Gupta", text_val, True),
        ("Role", "Full-Stack Developer", chrome_color, True),
        ("Origin", "Maharashtra, India", text_val, False),
        ("Education", "B.Sc. Computer Science (SYCS)", text_val, False),
        ("Status", "Building + Learning + Shipping", accent_green, True),
        ("ToolChain", "VS Code, Git, Firebase, Vercel", text_val, False),
        ("Core.Lang", "Java, Python, JS, HTML5, CSS", chrome_color, False),
        ("Core.Frontend", "React, Next.js, Tailwind CSS", portrait_color, False),
        ("Core.Backend", "Node.js, Firebase, Supabase", text_val, False),
        ("Core.Database", "Firestore, Supabase DB", text_val, False),
        ("Core.Infra", "Vercel, GitHub Actions", accent_green, False),
        ("Grid.Mail", "piyushgupta122006@gmail.com", text_body, False),
        ("Grid.Portfolio", "my-portfolio-eight-sigma.vercel.app", chrome_color, False),
        ("Grid.LinkedIn", "in/piyush-gupta-377694335", text_body, False),
        ("Grid.GitHub", "piyushgupta122006-design", portrait_color, False),
        ("Grid.Facebook", "profile.php?id=61563383442934", text_body, False),
    ]
    
    svg = []
    svg.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');
      .mono {{ font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, monospace; }}
      .title {{ font-size: 13px; font-weight: 600; fill: {chrome_color}; }}
      .hdr {{ font-size: 11.5px; font-weight: 700; fill: {chrome_color}; letter-spacing: 1.5px; }}
      .sub {{ font-size: 10px; font-weight: 500; fill: {text_muted}; letter-spacing: 1px; }}
      .r-key {{ font-size: 13.5px; font-weight: 600; fill: {chrome_color}; }}
      .r-val {{ font-size: 13px; font-weight: 500; }}
      .ldr {{ font-size: 11px; fill: {leader_color}; letter-spacing: 2px; }}
      .meta {{ font-size: 9.5px; fill: {text_muted}; font-weight: 500; }}
    </style>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}" />
      <stop offset="100%" stop-color="{panel_bg}" />
    </linearGradient>
    <linearGradient id="neon-glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{chrome_color}" />
      <stop offset="50%" stop-color="{portrait_color}" />
      <stop offset="100%" stop-color="{accent_green}" />
    </linearGradient>
  </defs>

  <!-- Background Canvas -->
  <rect x="1" y="1" width="1178" height="608" rx="10" fill="url(#bg-grad)" stroke="{frame_stroke}" stroke-width="1.5" />

  <!-- Terminal Window Bar -->
  <rect x="1" y="1" width="1178" height="42" rx="10" fill="{panel_bg}" stroke="{frame_stroke}" stroke-width="1.5"/>
  <line x1="1" y1="43" x2="1179" y2="43" stroke="{frame_stroke}" stroke-width="1.5" />
  
  <!-- Traffic Light Controls -->
  <circle cx="28" cy="22" r="5.5" fill="#EF4444"/>
  <circle cx="46" cy="22" r="5.5" fill="#F59E0B"/>
  <circle cx="64" cy="22" r="5.5" fill="#10B981"/>

  <!-- Title -->
  <text x="92" y="27" class="mono title">profile.sh --live</text>

  <!-- Pulsing Red LIVE Badge -->
  <g transform="translate(930, 13)">
    <circle cx="9" cy="9" r="4.5" fill="#EF4444">
      <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="9" cy="9" r="7.5" fill="none" stroke="#EF4444" stroke-width="1" opacity="0.6">
      <animate attributeName="r" values="4.5;10;4.5" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="24" y="13" class="mono" font-size="11" font-weight="700" fill="#EF4444" letter-spacing="1">LIVE</text>
  </g>

  <!-- Handle Pill -->
  <rect x="995" y="10" width="170" height="24" rx="12" fill="{chrome_color}" fill-opacity="0.08" stroke="{chrome_color}" stroke-width="1"/>
  <text x="1080" y="26" class="mono" font-size="11" font-weight="600" fill="{chrome_color}" text-anchor="middle">@piyushgupta</text>

  <!-- Top Accent Bar -->
  <rect x="1" y="42" width="1178" height="1.5" fill="url(#neon-glow)" />

  <!-- ================= LEFT COLUMN: VISUAL.MAP ================= -->
  <g id="visual-map">
    <text x="38" y="76" class="mono hdr">VISUAL.MAP // 01</text>
    <text x="38" y="92" class="mono sub">FLOYD-STEINBERG DITHER · 1-BIT DENSITY</text>
    <text x="430" y="76" class="mono meta" text-anchor="end">LOC: 19.29°N 73.06°E</text>

    <!-- Outer Frame -->
    <rect x="38" y="104" width="395" height="476" rx="6" fill="{bg_color}" fill-opacity="0.6" stroke="{frame_stroke}" stroke-width="1.2"/>
    
    <!-- Cyber Corner Brackets -->
    <path d="M38,124 L38,104 L58,104" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M433,124 L433,104 L413,104" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M38,560 L38,580 L58,580" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M433,560 L433,580 L413,580" fill="none" stroke="{chrome_color}" stroke-width="2"/>

    <!-- Crosshairs -->
    <line x1="38" y1="342" x2="50" y2="342" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="421" y1="342" x2="433" y2="342" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="235" y1="104" x2="235" y2="116" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="235" y1="568" x2="235" y2="580" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>

    <!-- Layer 1: Portrait Dither Dots (~60 interleaved groups for shimmer intro & drift loop) -->
    <g id="portrait-layer" fill="{portrait_color}" shape-rendering="crispEdges">
      <!-- Group loop drift animation -->
      <animateTransform attributeName="transform" type="translate"
        values="0 0; 0 0; 8 -6; 0 0; -6 6; 0 0"
        keyTimes="0; 0.25; 0.45; 0.65; 0.85; 1"
        dur="14.2s" repeatCount="indefinite" begin="3.2s" />
''')

    for i, grp in enumerate(groups):
        if not grp:
            continue
        path_data = "".join(grp)
        delay = (i / len(groups)) * 2.0
        svg.append(f'''      <path d="{path_data}" opacity="0">
        <animate attributeName="opacity" from="0" to="1" dur="1.0s" begin="{delay:.2f}s" fill="freeze"/>
      </path>''')

    svg.append(f'''    </g>

    <!-- Layer 2: Travellers Swarm (Morphs between Code </>, Vercel ▲, React ⚛) -->
    <g id="travellers-layer" fill="{chrome_color}" opacity="0">
      <!-- Hidden during portrait phase, visible during morph transitions -->
      <animate attributeName="opacity"
        values="0; 0; 0.9; 0.9; 0; 0.9; 0.9; 0"
        keyTimes="0; 0.25; 0.35; 0.55; 0.65; 0.75; 0.90; 1"
        dur="14.2s" repeatCount="indefinite" begin="3.2s"/>
''')

    # Morphing dots
    for p_idx in range(len(pts_code)):
        p1 = pts_code[p_idx]
        p2 = pts_vercel[p_idx]
        p3 = pts_react[p_idx]
        svg.append(f'''      <circle cx="{p1[0]:.1f}" cy="{p1[1]:.1f}" r="1.6">
        <animate attributeName="cx" values="{p1[0]:.1f}; {p1[0]:.1f}; {p2[0]:.1f}; {p2[0]:.1f}; {p3[0]:.1f}; {p3[0]:.1f}; {p1[0]:.1f}" keyTimes="0; 0.25; 0.45; 0.60; 0.75; 0.90; 1" dur="14.2s" repeatCount="indefinite" begin="3.2s"/>
        <animate attributeName="cy" values="{p1[1]:.1f}; {p1[1]:.1f}; {p2[1]:.1f}; {p2[1]:.1f}; {p3[1]:.1f}; {p3[1]:.1f}; {p1[1]:.1f}" keyTimes="0; 0.25; 0.45; 0.60; 0.75; 0.90; 1" dur="14.2s" repeatCount="indefinite" begin="3.2s"/>
      </circle>''')

    svg.append(f'''    </g>

    <!-- Status Bar inside Visual Box -->
    <rect x="38" y="552" width="395" height="28" fill="{panel_bg}" fill-opacity="0.9" stroke="{frame_stroke}" stroke-width="1"/>
    <text x="52" y="570" class="mono meta" fill="{text_muted}">FPS: 60.0 // DOTS: ~17K // DENSITY: 1-BIT</text>
    <text x="418" y="570" class="mono meta" fill="{accent_green}" text-anchor="end">STATUS: ACTIVE</text>
  </g>

  <!-- ================= VERTICAL DIVIDER ================= -->
  <line x1="460" y1="65" x2="460" y2="585" stroke="{frame_stroke}" stroke-width="1.2" stroke-dasharray="3,3" />

  <!-- ================= RIGHT COLUMN: SYSTEM.INFO ================= -->
  <g id="system-info" transform="translate(490, 0)">
    <text x="0" y="76" class="mono hdr">SYSTEM.INFO // SPECIFICATIONS</text>
    <text x="0" y="92" class="mono sub">CORE METRICS · TECH STACK · NETWORK GRID</text>
    <text x="650" y="76" class="mono meta" text-anchor="end">ENV: PRODUCTION</text>

    <!-- Locked monospace rows with calculated dotted leaders -->
''')

    row_y_start = 126
    row_gap = 29.5
    total_span_x = 650
    
    for idx, (label, val, val_col, is_bold) in enumerate(rows):
        cur_y = row_y_start + idx * row_gap
        
        lbl_w = len(label) * 8.8 + 12
        val_w = len(val) * 7.8 + 8
        
        dot_start_x = lbl_w + 4
        dot_end_x = total_span_x - val_w - 4
        num_dots = max(4, int((dot_end_x - dot_start_x) / 7.5))
        leader_dots = ". " * num_dots
        
        weight = "700" if is_bold else "500"
        
        svg.append(f'''    <!-- Row {idx+1}: {label} -->
    <g transform="translate(0, {cur_y})">
      <text x="0" y="0" class="mono r-key">{label}</text>
      <text x="{dot_start_x:.1f}" y="-1" class="mono ldr">{leader_dots}</text>
      <text x="{total_span_x}" y="0" class="mono r-val" font-weight="{weight}" fill="{val_col}" text-anchor="end" textLength="{val_w:.1f}" lengthAdjust="spacingAndGlyphs">{val}</text>
    </g>''')

    svg.append(f'''  </g>
</svg>''')

    return "\n".join(svg)

def main():
    print("Generating exact Master Prompt dark.svg...")
    dark_svg = build_banner_svg(theme="dark", image_path=None)
    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"dark.svg created ({len(dark_svg)} bytes)")

    print("Generating exact Master Prompt light.svg...")
    light_svg = build_banner_svg(theme="light", image_path=None)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"light.svg created ({len(light_svg)} bytes)")

if __name__ == "__main__":
    main()
