from PIL import Image, ImageDraw, ImageFont

PLAYFAIR = '/home/claude/fonts/PlayfairDisplay-VF.ttf'
SOURCE   = '/home/claude/fonts/SourceSans3-VF.ttf'

def fnt(path, size, weight=400):
    f = ImageFont.truetype(path, size)
    if weight != 400:
        f.set_variation_by_axes([weight])
    return f

# Brand colours
CREAM     = (244, 243, 238)
NAVY      = (0,   44,  79)
ORANGE    = (255, 106,  3)
GREEN     = (87,  164,  0)
GREY_CARD = (232, 231, 226)
WHITE     = (255, 255, 255)
YELLOW    = (253, 201,  3)
OLIVE     = (173, 192,  2)

# Extracted assets
LOGO      = Image.open('/home/claude/syc_logo_area.png').convert('RGBA')   # 478×210
BADGE     = Image.open('/home/claude/syc_tip_badge.png').convert('RGBA')   # 358×122

CARD_W = 1080
CARD_H = 1080
BORDER = 22

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    r = radius
    draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
    draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
    for cx, cy in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
        draw.ellipse([cx, cy, cx+2*r, cy+2*r], fill=fill)

def wrap_text(text, font_obj, max_width, draw):
    words = text.replace('\n', ' \n ').split(' ')
    lines, current = [], []
    for word in words:
        if word == '\n':
            if current: lines.append(' '.join(current))
            current = []
            continue
        test = ' '.join(current + [word])
        if draw.textlength(test, font=font_obj) > max_width and current:
            lines.append(' '.join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(' '.join(current))
    return [l for l in lines if l.strip()]

def auto_title_font(draw, title, max_w, max_h, hi=92, lo=46):
    for size in range(hi, lo-1, -2):
        f = fnt(PLAYFAIR, size)
        lines = wrap_text(title, f, max_w, draw)
        lh = draw.textbbox((0,0),'Ag',font=f)[3]
        if len(lines)*(lh+8) <= max_h:
            return f, lines, lh
    f = fnt(PLAYFAIR, lo)
    lines = wrap_text(title, f, max_w, draw)
    lh = draw.textbbox((0,0),'Ag',font=f)[3]
    return f, lines, lh

def draw_footer(draw, img):
    """Draw footer from scratch — no reference pixels."""
    FOOTER_Y = 880   # start of footer zone
    FT = fnt(SOURCE, 36, 700)   # Stack Your Cash — bold
    FL = fnt(SOURCE, 26, 400)   # Learn | Save | Invest
    FU = fnt(SOURCE, 24, 400)   # url

    # "Stack Your Cash"
    t1 = 'Stack Your Cash'
    w1 = draw.textlength(t1, font=FT)
    draw.text(((CARD_W-w1)//2, FOOTER_Y + 28), t1, font=FT, fill=NAVY)

    # "Learn | Save | Invest"
    t2 = 'Learn  |  Save  |  Invest'
    w2 = draw.textlength(t2, font=FL)
    draw.text(((CARD_W-w2)//2, FOOTER_Y + 80), t2, font=FL, fill=(130, 140, 150))

    # URL
    t3 = 'stackyourcash.co.uk'
    w3 = draw.textlength(t3, font=FU)
    draw.text(((CARD_W-w3)//2, FOOTER_Y + 118), t3, font=FU, fill=(130, 140, 150))

def make_card(title, topics, filename):
    # ── 1. Blank canvas ─────────────────────────────────────────────────
    img  = Image.new('RGB', (CARD_W, CARD_H), CREAM)
    draw = ImageDraw.Draw(img)

    # ── 2. Navy border all round ─────────────────────────────────────────
    draw.rectangle([0, 0, CARD_W, BORDER], fill=NAVY)
    draw.rectangle([0, CARD_H-BORDER, CARD_W, CARD_H], fill=NAVY)
    draw.rectangle([0, 0, BORDER, CARD_H], fill=NAVY)
    draw.rectangle([CARD_W-BORDER, 0, CARD_W, CARD_H], fill=NAVY)

    # ── 3. Colour bar ────────────────────────────────────────────────────
    BAR_Y0, BAR_Y1 = BORDER, BORDER+26
    inner_w = CARD_W - 2*BORDER
    seg = inner_w // 4
    x0 = BORDER
    for i, c in enumerate([ORANGE, YELLOW, OLIVE, GREEN]):
        draw.rectangle([x0+i*seg, BAR_Y0, x0+(i+1)*seg, BAR_Y1], fill=c)

    # ── 4. Header zone (cream) ───────────────────────────────────────────
    HEADER_Y0 = BAR_Y1
    HEADER_Y1 = 278
    draw.rectangle([BORDER, HEADER_Y0, CARD_W-BORDER, HEADER_Y1], fill=CREAM)

    # ── 5. Paste logo and badge FIRST (before second bar so bar sits on top) ─
    img.paste(LOGO, (BORDER+18, HEADER_Y0+12), LOGO)
    badge_x = CARD_W - BORDER - BADGE.width - 22
    badge_y = HEADER_Y0 + 20
    img.paste(BADGE, (badge_x, badge_y), BADGE)

    # ── 6. Second colour bar (drawn AFTER logo so it's never overwritten) ──
    draw = ImageDraw.Draw(img)
    BAR2_Y0 = HEADER_Y1 - 20
    BAR2_Y1 = HEADER_Y1
    segs2 = [(BORDER, x0+seg, ORANGE), (x0+seg, x0+2*seg, YELLOW),
             (x0+2*seg, x0+3*seg, OLIVE), (x0+3*seg, x0+4*seg, GREEN),
             (x0+4*seg, CARD_W-BORDER, NAVY)]
    for bx0, bx1, bc in segs2:
        draw.rectangle([bx0, BAR2_Y0, bx1, BAR2_Y1], fill=bc)

    # Redraw side borders (logo/badge paste may have overwritten edge)
    draw.rectangle([0, 0, BORDER, CARD_H], fill=NAVY)
    draw.rectangle([CARD_W-BORDER, 0, CARD_W, CARD_H], fill=NAVY)

    # ── 8. Content zone ──────────────────────────────────────────────────
    CONTENT_Y0 = 278
    FOOTER_Y   = 880
    MARGIN_X   = BORDER + 30   # 52

    # Title
    TITLE_Y   = CONTENT_Y0 + 36
    DIVIDER_Y = TITLE_Y + 175
    GRID_Y0   = DIVIDER_Y + 26
    GRID_Y1   = FOOTER_Y - 30

    title_max_w = CARD_W - MARGIN_X*2
    tf, tlines, tlh = auto_title_font(draw, title, title_max_w, 170)
    ty = TITLE_Y
    for line in tlines:
        lw = draw.textlength(line, font=tf)
        draw.text(((CARD_W-lw)//2, ty), line, font=tf, fill=NAVY)
        ty += tlh + 8

    # Orange divider — two segments to avoid column gap
    COL_MID  = CARD_W // 2
    GAP      = 20
    draw.rectangle([MARGIN_X+10, DIVIDER_Y, COL_MID-GAP//2-4, DIVIDER_Y+5], fill=ORANGE)
    draw.rectangle([COL_MID+GAP//2+4, DIVIDER_Y, CARD_W-MARGIN_X-10, DIVIDER_Y+5], fill=ORANGE)

    # ── 9. 2×2 grid cards ────────────────────────────────────────────────
    row_mid = (GRID_Y0 + GRID_Y1) // 2
    positions = [
        (MARGIN_X,          GRID_Y0,          COL_MID-GAP//2, row_mid-GAP//2),
        (COL_MID+GAP//2,    GRID_Y0,          CARD_W-MARGIN_X, row_mid-GAP//2),
        (MARGIN_X,          row_mid+GAP//2,   COL_MID-GAP//2, GRID_Y1),
        (COL_MID+GAP//2,    row_mid+GAP//2,   CARD_W-MARGIN_X, GRID_Y1),
    ]
    flat     = [topics[0][0], topics[0][1], topics[1][0], topics[1][1]]
    bold_fnt = fnt(SOURCE, 28, 700)

    for (cx0, cy0, cx1, cy1), topic in zip(positions, flat):
        draw_rounded_rect(draw, [cx0, cy0, cx1, cy1], 12, GREY_CARD)
        bar_x = cx0 + 16
        draw.rectangle([bar_x, cy0+20, bar_x+6, cy1-20], fill=ORANGE)
        tx0    = bar_x + 6 + 16
        tx1    = cx1 - 14
        lines  = wrap_text(topic, bold_fnt, tx1-tx0, draw)
        lh     = draw.textbbox((0,0),'Ag',font=bold_fnt)[3]
        sp     = 7
        total_h = len(lines)*lh + (len(lines)-1)*sp
        sy     = (cy0+cy1)//2 - total_h//2
        for line in lines:
            draw.text((tx0, sy), line, font=bold_fnt, fill=NAVY)
            sy += lh + sp

    # ── 10. Footer drawn from scratch ────────────────────────────────────
    draw_footer(draw, img)

    img.save(filename, 'PNG', dpi=(300,300))
    print(f'✓ {filename}')


make_card(
    title  = 'Currencies Explained',
    topics = [
        ['What exchange rates are & how they work',  'What drives the pound up or down'],
        ['How a weak pound hits your shopping bill', 'What it means for your portfolio'],
    ],
    filename = '/mnt/user-data/outputs/SYC_Card_Currencies_Explained.png'
)
make_card(
    title  = 'Oil & Energy Markets',
    topics = [
        ['How oil is priced & who controls supply', 'From the barrel to your petrol pump'],
        ['Why energy bills move with gas prices',   'What it means for your investments'],
    ],
    filename = '/mnt/user-data/outputs/SYC_Card_Oil_Energy_Markets.png'
)
make_card(
    title  = 'Market Corrections Explained',
    topics = [
        ['What a correction is & how to define one', 'What causes markets to fall'],
        ['How long corrections typically last',       'What to do — and what to avoid'],
    ],
    filename = '/mnt/user-data/outputs/SYC_Card_Market_Corrections.png'
)
make_card(
    title  = 'Thematic Investing',
    topics = [
        ['What thematic funds are & how they work',   'AI, clean energy & ageing population themes'],
        ['The risks: valuation, timing & cost',       'Thematic vs index: how they compare'],
    ],
    filename = '/mnt/user-data/outputs/SYC_Card_Thematic_Investing.png'
)
