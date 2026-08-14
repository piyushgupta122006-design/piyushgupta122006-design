"""
generate_banner.py
Creates production-grade animated terminal banners (dark.svg and light.svg)
for GitHub profile according to the Master Prompt specification.
"""

import math
import random
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw

def floyd_steinberg_dither(img_gray, serpentine=True):
    """
    Perform 1-bit Floyd-Steinberg dithering with serpentine scan order.
    Returns 2D binary numpy array (1 for foreground dot, 0 for background).
    """
    arr = np.array(img_gray, dtype=np.float32)
    h, w = arr.shape
    
    out = np.zeros((h, w), dtype=np.uint8)
    
    for y in range(h):
        # Serpentine scanning
        xs = range(w) if (y % 2 == 0 or not serpentine) else range(w - 1, -1, -1)
        direction = 1 if (y % 2 == 0 or not serpentine) else -1
        
        for x in xs:
            old_val = arr[y, x]
            new_val = 255.0 if old_val >= 128.0 else 0.0
            out[y, x] = 1 if new_val == 0.0 else 0  # Invert so dark parts become dots
            err = old_val - new_val
            
            # Error diffusion
            # Right: 7/16
            xr = x + direction
            if 0 <= xr < w:
                arr[y, xr] += err * (7.0 / 16.0)
            
            # Bottom-left: 3/16
            y_down = y + 1
            if y_down < h:
                x_bl = x - direction
                if 0 <= x_bl < w:
                    arr[y_down, x_bl] += err * (3.0 / 16.0)
                
                # Bottom: 5/16
                arr[y_down, x] += err * (5.0 / 16.0)
                
                # Bottom-right: 1/16
                x_br = x + direction
                if 0 <= x_br < w:
                    arr[y_down, x_br] += err * (1.0 / 16.0)
                    
    return out

def generate_portrait_dither(target_w=190, target_h=230, image_path=None):
    """
    Generates the dithered dot matrix from an image or a procedural cyber developer avatar.
    """
    if image_path:
        try:
            im = Image.open(image_path).convert("RGBA")
            bg = Image.new("RGBA", im.size, (10, 16, 31, 255))
            bg.paste(im, (0, 0), im)
            gray = bg.convert("L")
            gray = ImageOps.autocontrast(gray, cutoff=1)
            gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
            gray = gray.resize((target_w, target_h), Image.Resampling.LANCZOS)
            return floyd_steinberg_dither(gray, serpentine=True)
        except Exception as e:
            print(f"Image load error: {e}, falling back to avatar synthesis")

    # Procedural high-tech stylized portrait / coder silhouette
    im = Image.new("L", (target_w, target_h), 245)
    draw = ImageDraw.Draw(im)
    
    cx, cy = target_w // 2, int(target_h * 0.40)
    head_r = int(target_w * 0.23)
    
    # Head & face gradient
    for r in range(head_r, 0, -1):
        shade = int(50 + 130 * (r / head_r))
        draw.ellipse([cx - r, cy - int(r*1.15), cx + r, cy + int(r*0.95)], fill=shade)
        
    # Hair / Tech Cap
    draw.ellipse([cx - int(head_r * 1.08), cy - int(head_r * 1.3), cx + int(head_r * 1.08), cy - int(head_r * 0.2)], fill=30)
    
    # Glasses / Cyber Visor
    visor_y = cy - int(head_r * 0.15)
    draw.rounded_rectangle([cx - int(head_r * 0.8), visor_y - 12, cx - 6, visor_y + 12], radius=4, fill=20)
    draw.rounded_rectangle([cx + 6, visor_y - 12, cx + int(head_r * 0.8), visor_y + 12], radius=4, fill=20)
    draw.rectangle([cx - 8, visor_y - 4, cx + 8, visor_y], fill=30)
    
    # Visor reflections
    draw.line([cx - int(head_r * 0.65), visor_y + 6, cx - 14, visor_y - 6], fill=200, width=2)
    draw.line([cx + 14, visor_y + 6, cx + int(head_r * 0.65), visor_y - 6], fill=200, width=2)
    
    # Nose & Beard/Chin
    draw.polygon([(cx, cy + 4), (cx - 4, cy + 18), (cx + 4, cy + 18)], fill=60)
    draw.arc([cx - 24, cy + 28, cx + 24, cy + 38], start=10, end=170, fill=40, width=3)
    draw.arc([cx - int(head_r*0.7), cy - 10, cx + int(head_r*0.7), cy + int(head_r*0.85)], start=30, end=150, fill=40, width=6)
    
    # Headphones
    draw.ellipse([cx - head_r - 10, cy - 25, cx - head_r + 6, cy + 25], fill=40)
    draw.ellipse([cx + head_r - 6, cy - 25, cx + head_r + 10, cy + 25], fill=40)
    draw.arc([cx - head_r, cy - int(head_r*1.2), cx + head_r, cy], start=190, end=350, fill=40, width=6)
    
    # Shoulders / Hoodie
    draw.polygon([
        (cx - int(target_w * 0.48), target_h),
        (cx - int(head_r * 0.9), cy + int(head_r * 0.85)),
        (cx + int(head_r * 0.9), cy + int(head_r * 0.85)),
        (cx + int(target_w * 0.48), target_h)
    ], fill=45)
    
    # Collar / Zipper line
    draw.line([(cx, cy + int(head_r * 0.85)), (cx, target_h)], fill=20, width=3)
    
    # Subtle dithering filter
    gray = im.filter(ImageFilter.GaussianBlur(1))
    gray = ImageOps.autocontrast(gray, cutoff=2)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=2, percent=130))
    return floyd_steinberg_dither(gray, serpentine=True)

def matrix_to_svg_paths(matrix, offset_x=55, offset_y=120, dot_size=1.45, pitch_x=1.9, pitch_y=1.9, num_groups=24):
    """
    Converts 2D dither matrix into interleaved SVG path groups for shimmering intro animation.
    Draws horizontal runs with shape-rendering="crispEdges".
    """
    h, w = matrix.shape
    groups = [[] for _ in range(num_groups)]
    
    rng = random.Random(42)
    
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
                p_height = dot_size
                
                path_chunk = f"M{px:.1f},{py:.1f}h{p_width:.1f}v{p_height:.1f}h-{p_width:.1f}Z "
                groups[grp_idx].append(path_chunk)
            else:
                x += 1
                
    return groups

def build_svg(theme="dark", image_path=None):
    """
    Builds the full 1180x610 SMIL-animated terminal SVG.
    """
    is_dark = (theme == "dark")
    
    # Design Tokens
    bg_color = "#0A101F" if is_dark else "#F8FAFC"
    panel_bg = "#0D1527" if is_dark else "#FFFFFF"
    frame_stroke = "#1E293B" if is_dark else "#CBD5E1"
    chrome_color = "#22D3EE" if is_dark else "#0891B2"
    portrait_color = "#A78BFA" if is_dark else "#7C3AED"
    accent_green = "#10B981" if is_dark else "#059669"
    text_muted = "#64748B" if is_dark else "#94A3B8"
    text_body = "#94A3B8" if is_dark else "#475569"
    text_val = "#F8FAFC" if is_dark else "#0F172A"
    leader_color = "#334155" if is_dark else "#CBD5E1"
    
    # 1. Generate Portrait Dither Matrix
    matrix = generate_portrait_dither(target_w=190, target_h=230, image_path=image_path)
    dot_groups = matrix_to_svg_paths(matrix, offset_x=55, offset_y=120, dot_size=1.45, pitch_x=1.9, pitch_y=1.9, num_groups=24)
    
    # 2. Prepare Info Rows
    rows = [
        ("Subject", "Piyush Gupta", text_val, True),
        ("Role", "CS Undergrad · Full-Stack Dev", chrome_color, True),
        ("Origin", "Maharashtra, India", text_val, False),
        ("Education", "SYCS (B.Sc. Computer Science)", text_val, False),
        ("Status", "Building S.A.G.E. · Shipping", accent_green, True),
        ("ToolChain", "VS Code · Git · Firebase · Vercel", text_val, False),
        ("Core.Lang", "Java · Python · JS · HTML5 · CSS", chrome_color, False),
        ("Core.Frontend", "React · Next.js · Tailwind CSS", portrait_color, False),
        ("Core.Backend", "Node.js · Firebase · Supabase", text_val, False),
        ("Core.Database", "Firestore · Supabase DB", text_val, False),
        ("Core.Infra", "Vercel · GitHub Actions", accent_green, False),
        ("Grid.Mail", "piyushgupta122006@gmail.com", text_body, False),
        ("Grid.Portfolio", "my-portfolio-eight-sigma.vercel.app", chrome_color, False),
        ("Grid.LinkedIn", "in/piyush-gupta-377694335", text_body, False),
        ("Grid.GitHub", "piyushgupta122006-design", portrait_color, False),
        ("Grid.X", "x.com/BirendraPiyush", text_body, False),
    ]
    
    # 3. Assemble SVG Components
    svg_parts = []
    
    # Header & Styles
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&amp;display=swap');
      .mono {{ font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
      .title {{ font-size: 13px; font-weight: 600; fill: {chrome_color}; }}
      .section-hdr {{ font-size: 11.5px; font-weight: 700; fill: {chrome_color}; letter-spacing: 1.5px; }}
      .sub-hdr {{ font-size: 10px; font-weight: 500; fill: {text_muted}; letter-spacing: 1px; }}
      .row-key {{ font-size: 13px; font-weight: 600; fill: {chrome_color}; }}
      .row-val {{ font-size: 13px; font-weight: 500; }}
      .leader {{ font-size: 11px; fill: {leader_color}; letter-spacing: 2px; }}
      .badge-text {{ font-size: 10.5px; font-weight: 700; letter-spacing: 1px; }}
      .handle-text {{ font-size: 11px; font-weight: 600; fill: {chrome_color}; }}
      .meta-num {{ font-size: 9.5px; fill: {text_muted}; font-weight: 500; }}
    </style>
    <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg_color}" />
      <stop offset="100%" stop-color="{panel_bg}" />
    </linearGradient>
    <linearGradient id="cyber-glow" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{chrome_color}" stop-opacity="0.8"/>
      <stop offset="50%" stop-color="{portrait_color}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{accent_green}" stop-opacity="0.8"/>
    </linearGradient>
  </defs>

  <!-- Background Panel -->
  <rect x="1" y="1" width="1178" height="608" rx="10" fill="url(#bg-grad)" stroke="{frame_stroke}" stroke-width="1.5" />

  <!-- Terminal Window Header -->
  <rect x="1" y="1" width="1178" height="42" rx="10" fill="{panel_bg}" stroke="{frame_stroke}" stroke-width="1.5"/>
  <line x1="1" y1="43" x2="1179" y2="43" stroke="{frame_stroke}" stroke-width="1.5" />
  
  <!-- Window Control Buttons -->
  <circle cx="28" cy="22" r="5.5" fill="#EF4444" opacity="0.9"/>
  <circle cx="46" cy="22" r="5.5" fill="#F59E0B" opacity="0.9"/>
  <circle cx="64" cy="22" r="5.5" fill="#10B981" opacity="0.9"/>

  <!-- Window Title -->
  <text x="92" y="27" class="mono title">profile.sh --live</text>

  <!-- Live Pulse Indicator -->
  <g transform="translate(940, 13)">
    <circle cx="9" cy="9" r="4.5" fill="#EF4444">
      <animate attributeName="opacity" values="1;0.2;1" dur="2s" repeatCount="indefinite"/>
    </circle>
    <circle cx="9" cy="9" r="7.5" fill="none" stroke="#EF4444" stroke-width="1" opacity="0.6">
      <animate attributeName="r" values="4.5;10;4.5" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.8;0;0.8" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="24" y="13" class="mono badge-text" fill="#EF4444">LIVE</text>
  </g>

  <!-- Profile Handle Pill -->
  <rect x="1005" y="10" width="158" height="24" rx="12" fill="{chrome_color}" fill-opacity="0.08" stroke="{chrome_color}" stroke-width="1"/>
  <text x="1084" y="26" class="mono handle-text" text-anchor="middle">@piyushgupta</text>

  <!-- Top Accent Neon Bar -->
  <rect x="1" y="42" width="1178" height="1.5" fill="url(#cyber-glow)" />

  <!-- ================= LEFT COLUMN: VISUAL.MAP ================= -->
  <g id="visual-map">
    <!-- Header -->
    <text x="40" y="76" class="mono section-hdr">VISUAL.MAP // 01</text>
    <text x="40" y="92" class="mono sub-hdr">FLOYD-STEINBERG DITHER · 1-BIT DENSITY</text>
    <text x="390" y="76" class="mono meta-num" text-anchor="end">LOC: 19.29°N 73.06°E</text>

    <!-- Outer Frame -->
    <rect x="40" y="104" width="385" height="476" rx="6" fill="{bg_color}" fill-opacity="0.6" stroke="{frame_stroke}" stroke-width="1.2"/>
    
    <!-- Corner Cyber Brackets -->
    <path d="M40,124 L40,104 L60,104" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M425,124 L425,104 L405,104" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M40,560 L40,580 L60,580" fill="none" stroke="{chrome_color}" stroke-width="2"/>
    <path d="M425,560 L425,580 L405,580" fill="none" stroke="{chrome_color}" stroke-width="2"/>

    <!-- Grid Crosshairs -->
    <line x1="40" y1="342" x2="52" y2="342" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="413" y1="342" x2="425" y2="342" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="232" y1="104" x2="232" y2="116" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>
    <line x1="232" y1="568" x2="232" y2="580" stroke="{chrome_color}" stroke-width="1" opacity="0.6"/>

    <!-- Dither Portrait Dots with Shimmer Intro Animation -->
    <g id="portrait-dots" fill="{portrait_color}" shape-rendering="crispEdges">
''')
    
    # Add interleaved animated path groups
    for i, grp in enumerate(dot_groups):
        if not grp:
            continue
        path_data = "".join(grp)
        delay = (i / len(dot_groups)) * 1.8
        svg_parts.append(f'''      <path d="{path_data}" opacity="0">
        <animate attributeName="opacity" from="0" to="1" dur="0.8s" begin="{delay:.2f}s" fill="freeze"/>
      </path>''')
        
    svg_parts.append(f'''    </g>

    <!-- Bottom Status Bar inside Visual Box -->
    <rect x="40" y="552" width="385" height="28" fill="{panel_bg}" fill-opacity="0.9" stroke="{frame_stroke}" stroke-width="1"/>
    <text x="54" y="570" class="mono meta-num" fill="{text_muted}">FPS: 60.0 // RES: 385x476</text>
    <text x="410" y="570" class="mono meta-num" fill="{accent_green}" text-anchor="end">STATUS: ACTIVE</text>
  </g>

  <!-- ================= VERTICAL DIVIDER ================= -->
  <line x1="455" y1="65" x2="455" y2="585" stroke="{frame_stroke}" stroke-width="1.2" stroke-dasharray="3,3" />

  <!-- ================= RIGHT COLUMN: SYSTEM.INFO ================= -->
  <g id="system-info" transform="translate(485, 0)">
    <!-- Header -->
    <text x="0" y="76" class="mono section-hdr">SYSTEM.INFO // SPECIFICATIONS</text>
    <text x="0" y="92" class="mono sub-hdr">CORE METRICS · TECH STACK · NETWORK GRID</text>
    <text x="650" y="76" class="mono meta-num" text-anchor="end">ENV: PRODUCTION</text>

    <!-- Specifications Table Rows -->
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
        
        svg_parts.append(f'''    <!-- Row {idx+1}: {label} -->
    <g transform="translate(0, {cur_y})">
      <text x="0" y="0" class="mono row-key">{label}</text>
      <text x="{dot_start_x:.1f}" y="-1" class="mono leader">{leader_dots}</text>
      <text x="{total_span_x}" y="0" class="mono row-val" font-weight="{weight}" fill="{val_col}" text-anchor="end" textLength="{val_w:.1f}" lengthAdjust="spacingAndGlyphs">{val}</text>
    </g>''')

    svg_parts.append(f'''  </g>
</svg>''')

    return "\n".join(svg_parts)

def main():
    print("Generating dark.svg...")
    dark_svg = build_svg(theme="dark", image_path=None)
    with open("dark.svg", "w", encoding="utf-8") as f:
        f.write(dark_svg)
    print(f"dark.svg created ({len(dark_svg)} bytes)")

    print("Generating light.svg...")
    light_svg = build_svg(theme="light", image_path=None)
    with open("light.svg", "w", encoding="utf-8") as f:
        f.write(light_svg)
    print(f"light.svg created ({len(light_svg)} bytes)")

if __name__ == "__main__":
    main()
