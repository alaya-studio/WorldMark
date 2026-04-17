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

# ── Slide 3: Our Approach (6.5s) ────────────────────────────────────────────
def gen_approach(n):
    cards = [
        ("01", "Unified Action Mapping",
         ["Translates WASD-style actions", "into each model's native format"]),
        ("02", "Hierarchical Test Suite",
         ["500 cases, 3 difficulty tiers", "First & third-person views"]),
        ("03", "Modular Evaluation Toolkit",
         ["Image Suite", "Action Suite", "Unified Action Mapping"]),
    ]
    ctimes = [0.3, 1.0, 1.7]
    CW, CH = 480, 350
    GAP = 60
    TW = 3*CW + 2*GAP
    SX = (W-TW)//2
    CY = 245
    frames = []
    for i in range(n):
        t = i/FPS
        f, d = make_base()
        ctext(d, "Our Approach", 75, f_title, TEXT_W)
        d.line([(W//2-200,158),(W//2+200,158)], fill=ACCENT, width=3)
        for ci, (num, title, items) in enumerate(cards):
            ct = ctimes[ci]
            if t < ct: continue
            a = min(1.0, (t-ct)/0.5)
            cx0 = SX + ci*(CW+GAP)
            cx1 = cx0+CW; cy1 = CY+CH
            d.rounded_rectangle([cx0,CY,cx1,cy1], radius=16,
                fill=fade_col(CARD_BG,a), outline=fade_col(ACCENT,a), width=2)
            d.text((cx0+24,CY+18), num, font=f_num, fill=fade_col(ACCENT,a))
            d.text((cx0+24,CY+115), title, font=f_card_h, fill=fade_col(TEXT_W,a))
            for ii,item in enumerate(items):
                d.text((cx0+36,CY+172+ii*48), "\u00b7 "+item, font=f_card_b, fill=fade_col(TEXT_G,a))
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
            # card height depends on content
            CH = 80 + len(metrics)*68 + 30
            cy1 = CY + CH

            # Card background
            d.rounded_rectangle([cx0, CY, cx1, cy1], radius=12,
                fill=fade_col(CARD_BG2, a))
            # Colored top border bar
            d.rounded_rectangle([cx0, CY, cx1, CY+TOP_BAR], radius=3,
                fill=fade_col(col, a))

            # Category title (colored)
            d.text((cx0+24, CY+TOP_BAR+18), dname, font=f_dim_title, fill=fade_col(col, a))

            # Metrics
            for mi, m in enumerate(metrics):
                my = CY + TOP_BAR + 18 + 58 + mi*62
                dot_cx = cx0 + 30
                dot_cy = my + 16
                d.ellipse([dot_cx-DOT_R, dot_cy-DOT_R, dot_cx+DOT_R, dot_cy+DOT_R],
                    fill=fade_col(col, a))
                d.text((cx0+52, my), m, font=f_metric, fill=fade_col(TEXT_W, a))

        frames.append(f)
    return frames

# ── Slide 9: Results (5.5s) ─────────────────────────────────────────────────
def gen_results(n):
    stats = [("6","Models Evaluated"),("500","Test Cases"),("8","Metrics"),("3","Difficulty Tiers")]
    stimes = [0.3,0.7,1.1,1.5]
    CW,CH=340,270; GAP=55
    TW=4*CW+3*GAP; SX=(W-TW)//2; CY=360
    frames = []
    for i in range(n):
        t=i/FPS
        f,d=make_base()
        ctext(d,"Benchmark at a Glance",75,f_title,TEXT_W)
        d.line([(W//2-265,158),(W//2+265,158)],fill=ACCENT,width=3)
        ctext(d,"WorldMark provides a standardized, reproducible evaluation framework",195,f_body_s,TEXT_G)
        for si,((num,label),st) in enumerate(zip(stats,stimes)):
            if t<st: continue
            a=min(1.0,(t-st)/0.4)
            cx0=SX+si*(CW+GAP); cx1=cx0+CW; cy1=CY+CH
            d.rounded_rectangle([cx0,CY,cx1,cy1],radius=16,
                fill=fade_col(CARD_BG,a),outline=fade_col(ACCENT,a),width=2)
            bb=d.textbbox((0,0),num,font=f_num)
            nx=cx0+(CW-(bb[2]-bb[0]))//2
            d.text((nx,CY+25),num,font=f_num,fill=fade_col(ACCENT,a))
            bb=d.textbbox((0,0),label,font=f_card_b)
            lx=cx0+(CW-(bb[2]-bb[0]))//2
            d.text((lx,CY+140),label,font=f_card_b,fill=fade_col(TEXT_G,a))
        frames.append(f)
    return frames

# ── Slide 10: Closing (4.0s) ────────────────────────────────────────────────
def gen_closing(n):
    url = "https://alaya-studio.github.io/WorldMark/"
    frames = []
    for i in range(n):
        t=i/FPS
        f,d=make_base()
        a=min(1.0,t/0.8)
        ctext(d,"WorldMark",300,f_hero,fade_col(TEXT_W,a),shadow=True)
        ctext(d,"A Unified Benchmark Suite for Interactive Video World Models",445,f_sub,fade_col(ACCENT,a))
        if t>0.5:
            ua=min(1.0,(t-0.5)/0.5)
            bb=d.textbbox((0,0),url,font=f_body)
            tw=bb[2]-bb[0]; ux=(W-tw)//2; uy=590; pad=20
            d.rounded_rectangle([ux-pad,uy-pad,ux+tw+pad,uy+42+pad],
                radius=12,fill=fade_col(CARD_BG,ua),outline=fade_col(ACCENT,ua),width=2)
            d.text((ux,uy),url,font=f_body,fill=fade_col(ACCENT,ua))
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
