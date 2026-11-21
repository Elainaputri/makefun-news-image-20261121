#!/usr/bin/env python3
"""Render entry.png: a dense broadsheet front page summing up Saturday 21 November 2026.

36 dated stories across 7 colour-coded regions, a 3-card breaking lead strip, and a
market/science ticker footer, on warm newsprint at 1024x1024. Drawn at 2x and
downsampled with LANCZOS for crisp type. Every block is measured and fitted, so no
text is clipped. Run to (re)build the image:

    python3 render.py

The graded entry is main.py, which only copies entry.png to /output.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palette
PAPER = (244, 241, 234)      # #F4F1EA
INK = (26, 26, 26)           # #1A1A1A
GRAY = (74, 72, 68)          # body grey
LIGHT = (200, 194, 182)      # #C8C2B6
CRIMSON = (139, 30, 30)      # #8B1E1E
SLATE = (30, 58, 95)         # section navy            #1E3A5F

REGION_COLORS = {
    "MIDDLE EAST": (139, 30, 30),
    "EUROPE & SECURITY": (30, 58, 95),
    "GLOBAL & CLIMATE": (31, 100, 74),
    "AMERICAS": (200, 122, 30),
    "ASIA-PACIFIC": (107, 63, 160),
    "AFRICA": (168, 87, 27),
    "SCIENCE, TECH & MARKETS": (11, 19, 43),
}

SS = 2
W = H = 1024
CW, CH = W * SS, H * SS

FONT_ROOTS = (
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/data/data/com.termux/files/usr/share/fonts/TTF"),
)
FD = os.environ.get("DEJAVU_FONT_DIR") or str(next(
    (root for root in FONT_ROOTS if (root / "DejaVuSansCondensed.ttf").is_file()),
    FONT_ROOTS[0],
))
FD = FD.rstrip("/") + "/"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SERIF = FD + "DejaVuSerif.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SC_B = FD + "DejaVuSansCondensed-Bold.ttf"
SC = FD + "DejaVuSansCondensed.ttf"

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, int(size * SS))
    return _cache[key]


def tw(d, s, f):
    b = d.textbbox((0, 0), s, font=f)
    return (b[2] - b[0]) / SS


def line_h(f):
    a, desc = f.getmetrics()
    return (a + desc) / SS


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if tw(d, t, f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def ellipsize(d, s, f, maxw):
    if tw(d, s, f) <= maxw:
        return s
    while s and tw(d, s + "…", f) > maxw:
        s = s[:-1]
    return s.rstrip() + "…"


text_boxes = []


def draw_text(d, x, y, s, f, fill):
    left, top, right, bottom = d.textbbox((x * SS, y * SS), s, font=f)
    if not (0 <= left <= right <= CW and 0 <= top <= bottom <= CH):
        raise ValueError(f"Text outside canvas: {s!r}")
    for l, t, r, b, previous in text_boxes:
        if max(left, l) < min(right, r) and max(top, t) < min(bottom, b):
            raise ValueError(f"Text overlap: {s!r} and {previous!r}")
    text_boxes.append((left, top, right, bottom, s))
    d.text((x * SS, y * SS), s, font=f, fill=fill)


def hline(d, x1, y, x2, w=1, fill=LIGHT):
    d.rectangle([x1 * SS, y * SS, x2 * SS, (y + w) * SS - 1], fill=fill)


def vline(d, x, y1, y2, w=1, fill=LIGHT):
    d.rectangle([x * SS, y1 * SS, (x + w) * SS - 1, y2 * SS], fill=fill)


def rect(d, x1, y1, x2, y2, fill=None, outline=None, w=1):
    d.rectangle([x1 * SS, y1 * SS, x2 * SS - 1, y2 * SS - 1], fill=fill, outline=outline, width=w * SS)


# ------------------------------------------------------------------ content
# (coverage date and optional UTC publication time, headline, summary).
REGIONS = [
    ("MIDDLE EAST", [
        ("21 NOV • 05:15 UTC", "Saudi-led coalition says it intercepted three missiles targeting Riyadh",
         "Authorities issued overnight alerts in the capital and south. (Times of Bangladesh)"),
        ("20 NOV", "Saudi-led coalition reports strikes on Houthi-held sites",
         "Targets included locations in Yemen's capital, Sanaa. (Times of Bangladesh)"),
        ("21 NOV • 05:15 UTC", "IRGC claims it downed a US drone over Hormuz",
         "Iranian state media reported the claim. (Times of Bangladesh)"),
        ("20 NOV", "UN warns Yemen's Taiz food stocks meet only one-tenth of needs",
         "Road closures cut food, medicine and water supplies by 90%. (UN)"),
        ("20 NOV • 20:14 UTC", "Israeli drone strikes kill at least seven in central Gaza",
         "Medical sources reported deaths in Bureij and Nuseirat. (Al Jazeera)"),
    ]),
    ("EUROPE & SECURITY", [
        ("20 NOV", "Poland says three Russian objects violated its airspace overnight",
         "One missile came down near Nowy Lipowiec. (Reuters / AFP)"),
        ("20 NOV", "Russian barrage hits Kyiv bridges and Ukraine's power grid",
         "At least eight killed nationwide, officials say. (Reuters)"),
        ("21 NOV • 06:14 UTC", "Zelensky calls Putin a killer after Trump calls him a friend",
         "Ukraine's president made the remarks in a CNN interview. (Euronews)"),
        ("21 NOV", "NATO chief Rutte due in Warsaw after airspace breach",
         "Polish Prime Minister Donald Tusk announced the visit. (Reuters)"),
        ("21 NOV • 01:12 UTC", "Denmark orders Russia's defence attaché to leave",
         "Copenhagen alleges a plot to kill Ukrainian rapper Kyivstoner. (Al Jazeera)"),
        ("20 NOV • 17:37 UTC", "Youth-led protests spread across more than 25 European countries",
         "Italian unions called a 24-hour strike. (Euronews)"),
    ]),
    ("GLOBAL & CLIMATE", [
        ("21 NOV • 03:21 UTC", "COP31 negotiators in Antalya extend talks by one day",
         "Delegates continue to seek consensus on a final deal. (Times of Bangladesh)"),
        ("20 NOV • 22:00 UTC", "Draft climate text drops all references to fossil fuels",
         "Environmental groups criticised the omission. (Times of Bangladesh)"),
        ("20 NOV • 22:00 UTC", "Panama threatens a formal objection over the climate draft",
         "The country called for a cap on oil production. (Times of Bangladesh)"),
        ("20 NOV", "WFP plans to assist 91 million people in its 2027 global outlook",
         "The agency says it needs just over $12bn for the plan. (UN/WFP)"),
        ("20 NOV", "Education Cannot Wait commits $52m to 300,000 crisis-affected learners",
         "Funding targets children in Lebanon, Myanmar and South Sudan. (UN Geneva)"),
    ]),
    ("AMERICAS", [
        ("20 NOV", "Magnitude 6.8 earthquake in Junin sends Lima residents from homes",
         "GFZ reported the quake; Peru's institute placed its depth at 129km. (Reuters)"),
        ("20 NOV", "Former Brazilian president Jair Bolsonaro is hospitalised with intestinal obstruction",
         "He was taken to hospital after reporting abdominal pain. (Reuters)"),
        ("20 NOV", "Three Salvadoran soldiers die after explosives accident in Haiti",
         "A third soldier died after being taken to hospital. (The Haitian Times)"),
        ("21 NOV", "Trump praises ties with Xi and Putin amid domestic political pressure",
         "He praised his ties to both Putin and Xi after the Shenzhen meeting. (Euronews)"),
        ("20 NOV", "US judge rejects Trump administration's changes to homelessness programme",
         "The ruling blocks the proposed overhaul. (Reuters)"),
    ]),
    ("ASIA-PACIFIC", [
        ("20 NOV", "Japan's Nikkei falls 5.06% as tech stocks slide worldwide",
         "Technology shares led a wider global market rout. (Reuters)"),
        ("20 NOV", "Myanmar expresses disappointment over Rohingya genocide judgment",
         "The World Court issued its ruling on Thursday. (Reuters)"),
        ("20 NOV", "SK Hynix set to become top shareholder in Japan's Kioxia",
         "A December bond conversion would give it an indirect 14.1% stake. (Reuters)"),
        ("21 NOV", "South Korea's president urges speed in AI race on data-centre visit",
         "Lee highlighted the need to move quickly. (Reuters)"),
        ("20 NOV", "Mongolia's president resigns, setting up an early election",
         "President Ukhnaa Khurelsukh's departure opens a race to replace him. (Reuters)"),
    ]),
    ("AFRICA", [
        ("20 NOV • 00:10 UTC", "Four bodies recovered after a migrant boat capsizes off Senegal",
         "Search teams continued looking for survivors. (Al Jazeera)"),
        ("21 NOV", "Phumzile Mlambo-Ngcuka, South Africa's first female deputy president, dies at 71",
         "She later led UN Women as its executive director. (Reuters)"),
        ("20 NOV", "UN warns 76,000 displaced people in Congo site face rising threats",
         "Plaine Savo residents have only five litres of water per person daily. (UN)"),
        ("21 NOV • 03:14 UTC", "Passenger boat capsizes in southern Nigeria's Bayelsa state",
         "Local reports described an overcrowded boat. (Times of Bangladesh)"),
    ]),
    ("SCIENCE, TECH & MARKETS", [
        ("20 NOV", "S&P 500 falls 3.70% to 6,910.39 as AI shares lead Wall Street rout",
         "The index records a seventh consecutive decline. (Reuters/AP)"),
        ("20 NOV", "Nasdaq drops 5.28% to 22,617.73 in its worst week since 2020",
         "The tech-heavy index loses about 10% over five sessions. (Reuters/AP)"),
        ("20 NOV", "Anthropic shares stumble the day after their stock market debut",
         "The listing raised a record $81.3bn. (Reuters)"),
        ("20 NOV", "Bitcoin slips below $60,000 during a broader selloff",
         "The cryptocurrency fell through the closely watched threshold. (Reuters)"),
        ("20 NOV", "US markets regulator proposes taking control of Wall Street tracking system",
         "The SEC proposal has a 60-day public comment window. (Reuters)"),
        ("21 NOV", "BepiColombo is scheduled to enter orbit around Mercury",
         "The two ESA and JAXA orbiters are still attached for arrival. (ESA)"),
    ]),
]
if [len(items) for _, items in REGIONS] != [5, 6, 5, 5, 5, 4, 6]:
    raise ValueError("Unexpected story counts")

LEADS = [
    ("GLOBAL LEAD", "COP31 talks extend after fossil-fuel language disappears",
     "UN negotiators in Antalya add a day to seek consensus after a draft omits coal, oil and gas.", (31, 100, 74)),
]

# ------------------------------------------------------------------ canvas
img = Image.new("RGB", (CW, CH), PAPER)
d = ImageDraw.Draw(img)

M = 26
inner_l, inner_r = M, W - M

# frame
rect(d, M, 14, W - M, H - 14, outline=INK, w=1)

# ---- masthead -------------------------------------------------------------
f_mast = font(SERIF_B, 43)
mt = "THE WORLD DISPATCH"
mw = tw(d, mt, f_mast)
draw_text(d, (W - mw) / 2, 20, mt, f_mast, INK)

f_flank = font(SC_B, 9)
draw_text(d, inner_l + 6, 26, "WORLD FRONT PAGE", f_flank, SLATE)
fl = "UTC EDITION"
draw_text(d, inner_r - 6 - tw(d, fl, f_flank), 26, fl, f_flank, SLATE)

# subtitle band
band_y = 70
rect(d, M, band_y, W - M, band_y + 20, fill=SLATE)
f_sub = font(SC_B, 10)
sub = "SATURDAY, NOVEMBER 21, 2026 • WORLD EDITION • 36 VERIFIED REPORTS"
sw = tw(d, sub, f_sub)
draw_text(d, (W - sw) / 2, band_y + 5, sub, f_sub, PAPER)

# ---- breaking lead strip --------------------------------------------------
hy0 = band_y + 26          # 96
hero_h = 118
gap = 9
hw = (W - 2 * M - 2 * gap) / 3

for i, (tag, head, summ, col) in enumerate(LEADS):
    # The final page uses one dominant lead rather than three competing heroes.
    x = M if len(LEADS) == 1 else M + i * (hw + gap)
    card_w = W - 2 * M if len(LEADS) == 1 else hw
    rect(d, x, hy0, x + card_w, hy0 + hero_h, outline=LIGHT, w=1)
    # colour tab
    rect(d, x, hy0, x + card_w, hy0 + 3, fill=col)
    f_hl = font(SC_B, 9)
    draw_text(d, x + 7, hy0 + 8, tag, f_hl, col)
    f_hh = font(SERIF_B, 15)
    y = hy0 + 21
    for ln in wrap(d, head, f_hh, card_w - 14):
        draw_text(d, x + 7, y, ln, f_hh, INK)
        y += line_h(f_hh) * 0.98
    f_hs = font(SC, 8.5)
    for ln in wrap(d, summ, f_hs, card_w - 14):
        draw_text(d, x + 7, y + 1, ln, f_hs, GRAY)
        y += line_h(f_hs)
    if y > hy0 + hero_h - 4:
        raise ValueError(f"Lead card overflow: {tag}")

# ---- region grid ----------------------------------------------------------
GTOP = hy0 + hero_h + 10   # 224
colw = (W - 2 * M - 2 * gap) / 3
ROW_A_H = 258
ROW_B_H = 258
ROW_C_H = 222


def render_card(x, y, w, h, title, stories):
    col = REGION_COLORS[title]
    rect(d, x, y, x + w, y + h, outline=LIGHT, w=1)
    # header
    hh = 18
    rect(d, x, y, x + w, y + hh, fill=col)
    f_ct = font(SC_B, 10)
    draw_text(d, x + 7, y + 4, title, f_ct, PAPER)
    # count badge
    f_cb = font(SC_B, 8)
    bt = f"{len(stories)}"
    draw_text(d, x + w - 7 - tw(d, bt, f_cb), y + 5, bt, f_cb, PAPER)

    top = y + hh + 5
    avail = (y + h - 5) - top
    innerw = w - 14
    sx = x + 7

    # find the largest scale (grow or shrink) that still fits, summaries if they fit
    chosen = None
    for with_sum in (True,):
        best = None
        for step in range(26, 7, -1):          # scale 1.30 -> 0.80
            scale = step / 20.0
            f_time = font(SC_B, 7.5 * scale)
            f_head = font(SC_B, 10.5 * scale)
            f_sum = font(SC, 8.2 * scale)
            lh_t, lh_h, lh_s = line_h(f_time), line_h(f_head), line_h(f_sum)
            blocks, total = [], 0
            for (tm, hd, sm) in stories:
                hl = wrap(d, hd, f_head, innerw)
                lines = lh_t + len(hl) * lh_h
                sl = []
                if with_sum:
                    sl = wrap(d, sm, f_sum, innerw)
                    lines += len(sl) * lh_s
                blocks.append((hl, sl))
                total += lines
            need = total + (len(stories) - 1) * 3
            if need <= avail:
                best = (scale, with_sum, blocks, f_time, f_head, f_sum, lh_t, lh_h, lh_s)
                break
        if best:
            chosen = best
            break
    if chosen is None:
        raise ValueError(f"Regional card overflow: {title}")

    _s, with_sum, blocks, f_time, f_head, f_sum, lh_t, lh_h, lh_s = chosen
    cy = top
    for idx, ((tm, hd, sm), (hl, sl)) in enumerate(zip(stories, blocks)):
        draw_text(d, sx, cy, tm, f_time, CRIMSON)
        cy += lh_t
        for ln in hl:
            draw_text(d, sx, cy, ln, f_head, INK)
            cy += lh_h
        for ln in sl:
            draw_text(d, sx, cy, ln, f_sum, GRAY)
            cy += lh_s
        cy += 3
        if idx < len(stories) - 1:
            hline(d, sx, cy - 1.5, x + w - 7, 1, (224, 219, 208))


# Row A: first three regions
rowA = REGIONS[0:3]
for i, (title, stories) in enumerate(rowA):
    x = M + i * (colw + gap)
    render_card(x, GTOP, colw, ROW_A_H, title, stories)

# Row B: next three regions
rowB_y = GTOP + ROW_A_H + gap
rowB = REGIONS[3:6]
for i, (title, stories) in enumerate(rowB):
    x = M + i * (colw + gap)
    render_card(x, rowB_y, colw, ROW_B_H, title, stories)

# Row C: wide markets card, stories in 3 sub-columns
rowC_y = rowB_y + ROW_B_H + gap
title, stories = REGIONS[6]
col = REGION_COLORS[title]
rect(d, M, rowC_y, W - M, rowC_y + ROW_C_H, outline=LIGHT, w=1)
rect(d, M, rowC_y, W - M, rowC_y + 18, fill=col)
f_ct = font(SC_B, 10)
draw_text(d, M + 7, rowC_y + 4, title, f_ct, PAPER)
f_cb = font(SC_B, 8)
draw_text(d, W - M - 7 - tw(d, "6", f_cb), rowC_y + 5, "6", f_cb, PAPER)

# 3 columns x 2 rows, fonts grown to fill the card
sub_gap = 12
subw = (W - 2 * M - 2 * sub_gap) / 3
topC = rowC_y + 24
availC = (rowC_y + ROW_C_H - 6) - topC

# choose a common scale that fills the tallest column nicely
def col_plan(subset, cw, scale, with_sum):
    f_time = font(SC_B, 8.4 * scale)
    f_head = font(SC_B, 12 * scale)
    f_sum = font(SC, 9 * scale)
    lh_t, lh_h, lh_s = line_h(f_time), line_h(f_head), line_h(f_sum)
    blocks, total = [], 0
    for (tm, hd, sm) in subset:
        hl = wrap(d, hd, f_head, cw)
        lines = lh_t + len(hl) * lh_h
        sl = []
        if with_sum:
            sl = wrap(d, sm, f_sum, cw)
            lines += len(sl) * lh_s
        blocks.append((hl, sl))
        total += lines
    return total + (len(subset) - 1) * 8, (f_time, f_head, f_sum, lh_t, lh_h, lh_s, blocks)

bestC = None
for with_sum in (True,):
    for step in range(30, 11, -1):
        scale = step / 20.0
        ok = True
        info = None
        for ci in range(3):
            cw = subw - 12
            need, det = col_plan(stories[ci * 2:(ci + 1) * 2], cw, scale, with_sum)
            if need > availC:
                ok = False
                break
            info = det
        if ok:
            bestC = (scale, with_sum, info)
            break
    if bestC:
        break
if bestC is None:
    raise ValueError("Markets card overflow")

scaleC, with_sumC, _ = bestC
for ci in range(3):
    cx = M + ci * (subw + sub_gap) + 6
    cw = subw - 12
    subset = stories[ci * 2:(ci + 1) * 2]
    _need, (f_time, f_head, f_sum, lh_t, lh_h, lh_s, blocks) = col_plan(subset, cw, scaleC, with_sumC)
    cy = topC
    for j, ((tm, hd, sm), (hl, sl)) in enumerate(zip(subset, blocks)):
        draw_text(d, cx, cy, tm, f_time, CRIMSON)
        cy += lh_t
        for ln in hl:
            draw_text(d, cx, cy, ln, f_head, INK)
            cy += lh_h
        for ln in sl:
            draw_text(d, cx, cy, ln, f_sum, GRAY)
            cy += lh_s
        cy += 6
        if j < len(subset) - 1:
            hline(d, cx, cy - 4, cx + cw, 1, (224, 219, 208))
    if ci < 2:
        vline(d, M + (ci + 1) * (subw + sub_gap) - sub_gap / 2, topC, rowC_y + ROW_C_H - 8, 1, LIGHT)

# ---- footer ticker --------------------------------------------------------
ft_y = rowC_y + ROW_C_H + 8   # ~ 990
hline(d, M + 6, ft_y, W - M - 6, 2, INK)
f_tick = font(SC_B, 8.6)
tick = "MARKETS & DATA   ·   S&P 500 6,910.39 (−3.70%)   ·   BTC $56,813.68 (−3.57%)   ·   BRENT CFD $92.57   ·   GOLD $3,535"
# shrink to fit one line
fs = 8.6
while tw(d, tick, font(SC_B, fs)) > (W - 2 * M - 12) and fs > 5:
    fs -= 0.2
f_tick = font(SC_B, fs)
draw_text(d, (W - tw(d, tick, f_tick)) / 2, ft_y + 4, tick, f_tick, SLATE)

# ------------------------------------------------------------------ save
out = img.resize((W, H), Image.LANCZOS)
out.save("entry.png", format="PNG", optimize=True)
out.save("news_digest_20261121.png", format="PNG", optimize=True)
out.save("news-20261121.png", format="PNG", optimize=True)
out.save("news-20261121.webp", format="WEBP", quality=92, method=6)
print("wrote entry.png, news-20261121.png, news-20261121.webp", out.size, os.path.getsize("entry.png"), "bytes")
