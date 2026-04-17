from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1920, 1080
FPS = 30
FADE_FRAMES = 15

IMG_DIR = "/Users/jessexu/Documents/WorldMark/.claude/worktrees/determined-mestorf/static/images"
OUT_DIR = "/tmp/video_frames"
os.makedirs(OUT_DIR, exist_ok=True)

BG_TOP    = (8,  14,  40)
BG_BOT    = (20, 28,  70)
ACCENT    = (100, 140, 255)
ACCENT2   = (80,  220, 200)
TEXT_W    = (240, 245, 255)
TEXT_G    = (160, 175, 210)
CARD_BG   = (25,  35,  80)

def gradient_bg():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0]*(1-t)+BG_BOT[0]*t)
        g = int(BG_TOP[1]*(1-t)+BG_BOT[1]*t)
        b = int(BG_TOP[2]*(1-t)+BG_BOT[2]*t)
        d.line([(0,y),(W,y)], fill=(r,g,b))
    return img

def add_dot_grid(draw, spacing=50, color=(20,28,55)):
    for x in range(0, W, spacing):
        for y in range(0, H, spacing):
            draw.ellipse([x-1,y-1,x+1,y+1], fill=color)

def load_font(size):
    for p in ["/System/Library/Fonts/Helvetica.ttc",
              "/System/Library/Fonts/Arial Unicode.ttf",
              "/Library/Fonts/Arial Unicode MS.ttf"]:
        try: return ImageFont.truetype(p, size)
        except: pass
    return ImageFont.load_default()

f_hero   = load_font(136)
f_title  = load_font(64)
f_sub    = load_font(60)
f_body   = load_font(34)
f_body_s = load_font(28)
f_author = load_font(44)
f_small  = load_font(31)
f_num    = load_font(80)
f_card_h = load_font(36)
f_card_b = load_font(28)

def ctext(draw, text, y, font, color, shadow=False):
    bb = draw.textbbox((0,0), text, font=font)
    x = (W - (bb[2]-bb[0])) // 2
    if shadow:
        draw.text((x+2,y+2), text, font=font, fill=(0,0,0))
    draw.text((x,y), text, font=font, fill=color)

def fade_col(color, alpha):
    return tuple(int(c * alpha) for c in color)

def make_base():
    f = gradient_bg()
    d = ImageDraw.Draw(f)
    add_dot_grid(d)
    return f, d

def paste_fit(frame, img_path, box, alpha=1.0):
    x0,y0,x1,y1 = box
    bw,bh = x1-x0, y1-y0
    img = Image.open(img_path).convert("RGB")
    iw,ih = img.size
    sc = min(bw/iw, bh/ih)
    nw,nh = int(iw*sc), int(ih*sc)
    img = img.resize((nw,nh), Image.LANCZOS)
    ox = x0 + (bw-nw)//2
    oy = y0 + (bh-nh)//2
    if alpha >= 1.0:
        frame.paste(img, (ox,oy))
    else:
        region = frame.crop((ox,oy,ox+nw,oy+nh))
        blended = Image.blend(region, img, alpha)
        frame.paste(blended, (ox,oy))

# ── Slide 1: Title (3.0s, no animation) ────────────────────────────────────
def gen_title(n):
    frames = []
    for _ in range(n):
        f, d = make_base()
        ctext(d, "WorldMark", 195, f_hero, TEXT_W, shadow=True)
        ctext(d, "A Unified Benchmark Suite for", 360, f_sub, ACCENT)
        ctext(d, "Interactive Video World Models", 432, f_sub, ACCENT)
        a1 = "Xiaojie Xu\u00b9  Zhengyuan Lin\u00b9\u00b2  Kang He\u00b9\u00b3  Yukang Feng\u00b9\u00b3"
        a2 = "Xiaofeng Mao\u00b9  Yuanyang Yin\u00b9\u00b3  Kaipeng Zhang\u00b9\u00b3  Yongtao Ge\u00b9"
        ctext(d, a1, 555, f_author, TEXT_G)
        ctext(d, a2, 612, f_author, TEXT_G)
        aff1 = "\u00b9Alaya Studio, Shanda AI Research Tokyo"
        aff2 = "\u00b2The University of Tokyo  \u00b3Shanghai Innovation Institute"
        ctext(d, aff1, 695, f_small, TEXT_G)
        ctext(d, aff2, 737, f_small, TEXT_G)
        frames.append(f)
    return frames

# ── Slide 2: The Problem (7.0s) ─────────────────────────────────────────────
def gen_problem(n):
    # Each item: (text, dot_color, border_color)
    items = [
        ("Every model uses its own proprietary benchmark",
         (230,  90, 130), (220,  80, 120)),
        ("Different scenes, trajectories, and control interfaces",
         (230, 180,  60), (220, 170,  50)),
        ("Fair cross-model comparison is impossible",
         (230, 120,  70), (220, 100,  60)),
        ("No benchmark provides standardized test conditions",
         (150, 120, 240), (130, 100, 230)),
    ]
    item_sec = [0.5, 1.5, 2.5, 3.5]
    q_lines = [
        "How can we design a unified interface to enable fair comparisons",
        "across different interactive video world models?",
    ]
    q_sec = 4.5
    CARD_ROW_BG = (22, 32, 72)
    PAD_X = 160
    CARD_H = 100
    GAP    = 22
    BORDER_W = 6
    DOT_R  = 14
    block_y = 205   # fixed position below title

    f_bold = load_font(36)

    frames = []
    for i in range(n):
        t = i / FPS
        f, d = make_base()
        ctext(d, "The Problem", 75, f_title, TEXT_W)
        d.line([(W//2-200, 158),(W//2+200, 158)], fill=ACCENT, width=3)

        for idx, ((text, dot_col, border_col), ts) in enumerate(zip(items, item_sec)):
            if t < ts:
                continue
            a = min(1.0, (t - ts) / 0.4)
            cy = block_y + idx * (CARD_H + GAP)

            d.rounded_rectangle(
                [PAD_X, cy, W - PAD_X, cy + CARD_H],
                radius=10,
                fill=fade_col(CARD_ROW_BG, a),
            )
            d.rounded_rectangle(
                [PAD_X, cy, PAD_X + BORDER_W, cy + CARD_H],
                radius=4,
                fill=fade_col(border_col, a),
            )
            dot_x = PAD_X + BORDER_W + 30
            dot_cy = cy + CARD_H // 2
            d.ellipse(
                [dot_x - DOT_R, dot_cy - DOT_R, dot_x + DOT_R, dot_cy + DOT_R],
                fill=fade_col(dot_col, a),
            )
            text_x = dot_x + DOT_R + 22
            bb = d.textbbox((0, 0), text, font=f_body)
            text_y = cy + (CARD_H - (bb[3] - bb[1])) // 2
            d.text((text_x, text_y), text, font=f_body, fill=fade_col(TEXT_W, a))

        # Bold question at the bottom
        if t >= q_sec - 0.3:
            a = min(1.0, (t - (q_sec - 0.3)) / 0.5)
            col = fade_col(TEXT_W, a)
            y_q = 790
            for line in q_lines:
                bb = d.textbbox((0, 0), line, font=f_bold)
                x = (W - (bb[2] - bb[0])) // 2
                d.text((x, y_q), line, font=f_bold, fill=col)
                y_q += 52

        frames.append(f)
    return frames

# ── Slide 3: Three Pillars (6.5s) ───────────────────────────────────────────
def gen_approach(n):
    cards = [
        ("01", "Unified Action\nMapping",
         ["WASD + L/R vocabulary", "translated to each model's", "native control format"],
         (80, 160, 255)),
        ("02", "Hierarchical\nTest Suite",
         ["First & third-person views", "Real & Stylized scenes", "3 difficulty tiers"],
         (60, 210, 170)),
        ("03", "Modular Evaluation\nToolkit",
         ["Image Suite", "Action Suite", "Unified Action Mapping"],
         (160, 100, 255)),
    ]
    ctimes = [0.3, 1.0, 1.7]
    GAP  = 55
    CW   = (W - 2*GAP - 160*2) // 3
    SX   = 160
    CY   = 185
    TOP  = 6
    CARD_BG2 = (18, 28, 68)
    f_num_sm  = load_font(52)
    f_ctitle  = load_font(42)
    f_cbody   = load_font(30)

    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Three Pillars of WorldMark", 65, f_title, TEXT_W)
        d.line([(W//2-320,148),(W//2+320,148)], fill=ACCENT, width=3)
        for ci, (num, title, items, col) in enumerate(cards):
            ct = ctimes[ci]
            if t < ct: continue
            a  = min(1.0, (t-ct)/0.5)
            cx0 = SX + ci*(CW+GAP)
            cx1 = cx0 + CW
            CH  = 530
            cy1 = CY + CH
            # Card bg
            d.rounded_rectangle([cx0,CY,cx1,cy1], radius=14,
                fill=fade_col(CARD_BG2, a))
            # Top color bar
            d.rounded_rectangle([cx0,CY,cx1,CY+TOP], radius=3,
                fill=fade_col(col, a))
            # Number
            d.text((cx0+24, CY+TOP+14), num, font=f_num_sm, fill=fade_col(col, a))
            # Title (may be two lines)
            ty = CY + TOP + 14 + 62
            for line in title.split('\n'):
                d.text((cx0+24, ty), line, font=f_ctitle, fill=fade_col(TEXT_W, a))
                ty += 50
            # Divider
            ty += 10
            d.line([(cx0+24, ty),(cx1-24, ty)], fill=fade_col(col, a), width=1)
            ty += 20
            # Items (plain text, no bullets)
            for item in items:
                d.text((cx0+24, ty), item, font=f_cbody, fill=fade_col(TEXT_G, a))
                ty += 46
        frames.append(f)
    return frames

# ── Slide 4: Overview of WorldMark (6.0s) ───────────────────────────────────
def gen_teaser(n):
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Overview of WorldMark", 55, f_title, TEXT_W)
        d.line([(W//2-250,138),(W//2+250,138)], fill=ACCENT, width=3)
        a = max(0.0, min(1.0, (t-0.3)/0.8))
        if a > 0:
            paste_fit(f, f"{IMG_DIR}/teaser.png", (120,165,W-120,H-55), alpha=a)
        frames.append(f)
    return frames

# ── Slide 5: Image Suite (5.0s) ─────────────────────────────────────────────
def gen_image_suite(n):
    sub = "Overview of the Image Suite: diverse scenes and styles across Indoor, City, and Nature categories"
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Image Suite", 55, f_title, TEXT_W)
        d.line([(W//2-170,138),(W//2+170,138)], fill=ACCENT, width=3)
        ctext(d, sub, 160, f_body, TEXT_G)
        a = max(0.0, min(1.0, (t-0.3)/0.8))
        if a > 0:
            paste_fit(f, f"{IMG_DIR}/image_suite.png", (150,215,W-150,H-60), alpha=a)
        frames.append(f)
    return frames

# ── Slide 6: Action Suite (5.0s) ────────────────────────────────────────────
def gen_action_suite(n):
    sub = "15 standardized action sequences: elementary translations and rotations to combined trajectories"
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Action Suite", 55, f_title, TEXT_W)
        d.line([(W//2-170,138),(W//2+170,138)], fill=ACCENT, width=3)
        ctext(d, sub, 160, f_body, TEXT_G)
        a = max(0.0, min(1.0, (t-0.3)/0.8))
        if a > 0:
            paste_fit(f, f"{IMG_DIR}/trajectories_3d.png", (150,215,W-150,H-60), alpha=a)
        frames.append(f)
    return frames

# ── Slide 7: Action Sequence Reasoning (5.0s) ───────────────────────────────
def gen_action_reasoning(n):
    sub = "Context-aware action selection using VLM reasoning to identify physical constraints"
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Action Sequence Reasoning", 55, f_title, TEXT_W)
        d.line([(W//2-310,138),(W//2+310,138)], fill=ACCENT, width=3)
        ctext(d, sub, 160, f_body, TEXT_G)
        a = max(0.0, min(1.0, (t-0.3)/0.8))
        if a > 0:
            paste_fit(f, f"{IMG_DIR}/vlm_traj.png", (150,215,W-150,H-60), alpha=a)
        frames.append(f)
    return frames

# ── Slide 8: Eight Metrics (6.0s) ───────────────────────────────────────────
def gen_metrics(n):
    dims = [
        ("Visual Quality",
         ["Aesthetic Quality", "Imaging Quality"],
         (80, 160, 255)),
        ("Control Alignment",
         ["Translation Error", "Rotation Error"],
         (60, 210, 170)),
        ("World Consistency",
         ["Reprojection Error", "State Consistency", "Content Consistency", "Style Consistency"],
         (160, 100, 255)),
    ]
    dtimes = [0.5, 1.2, 1.9]
    GAP = 60
    CW = (W - 2*GAP - 160*2) // 3   # three equal columns
    SX = 160
    CY = 220
    TOP_BAR = 6
    DOT_R = 10
    CARD_BG2 = (18, 28, 68)

    f_dim_title = load_font(44)
    f_metric    = load_font(32)

    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Eight Metrics, Three Dimensions", 60, f_title, TEXT_W)
        d.line([(W//2-330, 143),(W//2+330, 143)], fill=ACCENT, width=3)

        for di, (dname, metrics, col) in enumerate(dims):
            dt = dtimes[di]
            if t < dt: continue
            a = min(1.0, (t - dt) / 0.5)
            cx0 = SX + di*(CW+GAP)
            cx1 = cx0 + CW
            CH = 80 + len(metrics)*68 + 30
            cy1 = CY + CH

            d.rounded_rectangle([cx0, CY, cx1, cy1], radius=12,
                fill=fade_col(CARD_BG2, a))
            d.rounded_rectangle([cx0, CY, cx1, CY+TOP_BAR], radius=3,
                fill=fade_col(col, a))
            d.text((cx0+24, CY+TOP_BAR+18), dname, font=f_dim_title, fill=fade_col(col, a))

            for mi, m in enumerate(metrics):
                my = CY + TOP_BAR + 18 + 58 + mi*62
                dot_cx = cx0 + 30
                dot_cy = my + 16
                d.ellipse([dot_cx-DOT_R, dot_cy-DOT_R, dot_cx+DOT_R, dot_cy+DOT_R],
                    fill=fade_col(col, a))
                d.text((cx0+52, my), m, font=f_metric, fill=fade_col(TEXT_W, a))

        # Key Finding card (appears after all dimension cards)
        kf_sec = 2.6
        if t >= kf_sec:
            a = min(1.0, (t - kf_sec) / 0.5)
            AMBER = (255, 170, 50)
            kf_x0, kf_y0 = SX, CY + max(80 + 4*68 + 30, 80 + 2*68 + 30) + 30
            kf_x1 = W - SX
            kf_h  = 110
            d.rounded_rectangle([kf_x0, kf_y0, kf_x1, kf_y0+kf_h], radius=10,
                fill=fade_col((18, 28, 68), a))
            d.rounded_rectangle([kf_x0, kf_y0, kf_x0+6, kf_y0+kf_h], radius=3,
                fill=fade_col(AMBER, a))
            d.text((kf_x0+22, kf_y0+14), "Key Finding", font=f_dim_title,
                fill=fade_col(AMBER, a))
            d.text((kf_x0+22, kf_y0+62),
                "Visual quality and world consistency are largely uncorrelated across models",
                font=f_metric, fill=fade_col(TEXT_W, a))

        frames.append(f)
    return frames

# ── Slide 9: WorldMark at a Glance (5.5s) ───────────────────────────────────
def gen_results(n):
    stats = [
        ("6",   "Models\nBenchmarked",  (80,  160, 255)),
        ("500", "Evaluation\nCases",    (60,  210, 170)),
        ("8",   "Standardized\nMetrics",(160, 100, 255)),
        ("3",   "Difficulty\nTiers",    (240,  80, 140)),
    ]
    models = ["YUME 1.5", "MatrixGame 2.0", "HY-World",
              "HY-GameCraft", "Genie 3", "Open-Oasis"]
    stimes = [0.3, 0.7, 1.1, 1.5]
    GAP = 45; TOP = 6
    CW = (W - 3*GAP - 160*2) // 4
    SX = 160; CY = 195; CH = 310
    CARD_BG2 = (18, 28, 68)
    f_stat_n  = load_font(90)
    f_stat_l  = load_font(30)
    f_model   = load_font(28)
    f_models_h= load_font(32)

    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "WorldMark at a Glance", 65, f_title, TEXT_W)
        d.line([(W//2-290,148),(W//2+290,148)], fill=ACCENT, width=3)

        for si, ((num, label, col), st) in enumerate(zip(stats, stimes)):
            if t < st: continue
            a   = min(1.0, (t-st)/0.4)
            cx0 = SX + si*(CW+GAP)
            cx1 = cx0 + CW
            cy1 = CY + CH
            d.rounded_rectangle([cx0,CY,cx1,cy1], radius=14,
                fill=fade_col(CARD_BG2, a))
            d.rounded_rectangle([cx0,CY,cx1,CY+TOP], radius=3,
                fill=fade_col(col, a))
            # Big number centered
            bb = d.textbbox((0,0), num, font=f_stat_n)
            nx = cx0 + (CW - (bb[2]-bb[0])) // 2
            d.text((nx, CY+TOP+20), num, font=f_stat_n, fill=fade_col(col, a))
            # Label (two lines)
            ly = CY + TOP + 20 + (bb[3]-bb[1]) + 18
            for line in label.split('\n'):
                bb2 = d.textbbox((0,0), line, font=f_stat_l)
                lx  = cx0 + (CW - (bb2[2]-bb2[0])) // 2
                d.text((lx, ly), line, font=f_stat_l, fill=fade_col(TEXT_G, a))
                ly += 38

        # Models Evaluated box
        models_sec = 2.1
        if t >= models_sec:
            a = min(1.0, (t - models_sec) / 0.5)
            bx0 = SX; bx1 = W - SX
            by0 = CY + CH + 35; by1 = by0 + 130
            d.rounded_rectangle([bx0,by0,bx1,by1], radius=12,
                fill=fade_col(CARD_BG2, a))
            # "Models Evaluated" label centered
            bb = d.textbbox((0,0), "Models Evaluated", font=f_models_h)
            mx = (W - (bb[2]-bb[0])) // 2
            d.text((mx, by0+14), "Models Evaluated", font=f_models_h,
                fill=fade_col(ACCENT, a))
            # Pill badges
            PILL_BG = (30, 42, 90)
            pill_pad_x, pill_pad_y = 18, 8
            pill_gap = 22
            total_w = sum(d.textbbox((0,0), m, font=f_model)[2] for m in models) \
                      + 2*pill_pad_x*len(models) + pill_gap*(len(models)-1)
            px = (W - total_w) // 2
            py = by0 + 14 + (bb[3]-bb[1]) + 16
            for m in models:
                bb = d.textbbox((0,0), m, font=f_model)
                pw = bb[2]-bb[0] + 2*pill_pad_x
                ph = bb[3]-bb[1] + 2*pill_pad_y
                d.rounded_rectangle([px, py, px+pw, py+ph], radius=ph//2,
                    fill=fade_col(PILL_BG, a), outline=fade_col(ACCENT, a), width=1)
                d.text((px+pill_pad_x, py+pill_pad_y), m, font=f_model,
                    fill=fade_col(TEXT_W, a))
                px += pw + pill_gap

        frames.append(f)
    return frames

# ── Slide 10: Closing (4.0s) ────────────────────────────────────────────────
def gen_closing(n):
    url   = "https://alaya-studio.github.io/WorldMark/"
    GLOW  = (60, 100, 220)
    f_url = load_font(36)
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()

        # Subtle horizontal glow line behind title
        if t > 0.1:
            ga = min(1.0, (t-0.1)/0.6)
            for gy in range(H//2-90, H//2-70):
                brightness = max(0, 1.0 - abs(gy - (H//2-80)) / 10.0)
                gc = tuple(int(c * brightness * ga * 0.4) for c in GLOW)
                d.line([(W//4, gy),(3*W//4, gy)], fill=gc)

        # Title slides up + fades in
        title_a   = min(1.0, max(0.0, (t-0.0)/0.7))
        title_y   = int(280 + (1-title_a)**2 * 60)
        ctext(d, "WorldMark", title_y, f_hero, fade_col(TEXT_W, title_a), shadow=True)

        # Subtitle fades in after title
        sub_a = min(1.0, max(0.0, (t-0.5)/0.6))
        sub_y = int(435 + (1-sub_a)**2 * 30)
        ctext(d, "A Unified Benchmark Suite for Interactive Video World Models",
              sub_y, f_sub, fade_col(ACCENT, sub_a))

        # URL box slides up + fades in
        url_a = min(1.0, max(0.0, (t-1.1)/0.6))
        if url_a > 0:
            bb  = d.textbbox((0,0), url, font=f_url)
            tw  = bb[2]-bb[0]
            ux  = (W-tw)//2
            uy  = int(590 + (1-url_a)**2 * 25)
            pad = 22
            d.rounded_rectangle([ux-pad, uy-pad, ux+tw+pad, uy+44+pad],
                radius=14, fill=fade_col(CARD_BG, url_a),
                outline=fade_col(ACCENT, url_a), width=2)
            d.text((ux, uy), url, font=f_url, fill=fade_col(ACCENT, url_a))

        frames.append(f)
    return frames

# ── Assemble ─────────────────────────────────────────────────────────────────
slide_defs = [
    (gen_title,           int(3.0*FPS)),
    (gen_problem,         int(7.0*FPS)),
    (gen_approach,        int(6.5*FPS)),
    (gen_teaser,          int(6.0*FPS)),
    (gen_image_suite,     int(5.0*FPS)),
    (gen_action_suite,    int(5.0*FPS)),
    (gen_action_reasoning,int(5.0*FPS)),
    (gen_metrics,         int(6.0*FPS)),
    (gen_results,         int(5.5*FPS)),
    (gen_closing,         int(4.0*FPS)),
]

blank = gradient_bg()
add_dot_grid(ImageDraw.Draw(blank))

# Clear old frames
import glob, os
for fp in glob.glob(f"{OUT_DIR}/frame_*.png"):
    os.remove(fp)

frame_idx = 0
all_slides = []
for si,(fn,nf) in enumerate(slide_defs):
    print(f"Rendering slide {si+1}/{len(slide_defs)}...")
    all_slides.append(fn(nf))

print("Writing frames...")
for si,slide_frames in enumerate(all_slides):
    for frm in slide_frames:
        frm.save(f"{OUT_DIR}/frame_{frame_idx:05d}.png")
        frame_idx += 1
    if si < len(all_slides)-1:
        src = slide_frames[-1]
        for f in range(FADE_FRAMES):
            a = f / FADE_FRAMES
            Image.blend(src, blank, a).save(f"{OUT_DIR}/frame_{frame_idx:05d}.png")
            frame_idx += 1

print(f"Total frames: {frame_idx}  ({frame_idx/FPS:.1f}s)")
print("Encoding video...")
os.system(
    f"ffmpeg -y -framerate {FPS} -i {OUT_DIR}/frame_%05d.png "
    f"-c:v libx264 -crf 18 -pix_fmt yuv420p "
    f"-vf scale=1920:1080 /tmp/intro.mp4"
)
print("Done -> /tmp/intro.mp4")
