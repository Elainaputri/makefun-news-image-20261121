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
import math
from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------------ palette
PAPER = (247, 244, 235)      # warm archival newsprint  #F7F4EB
INK = (17, 19, 21)           # deep ink                #111315
GRAY = (74, 72, 68)          # body grey
LIGHT = (203, 197, 184)      # hairline rules          #CBC5B8
CRIMSON = (185, 28, 28)      # editorial accent        #B91C1C
SLATE = (30, 58, 95)         # section navy            #1E3A5F

REGION_COLORS = {
    "MIDDLE EAST & SECURITY": (179, 65, 44),
    "EUROPE & NATO": (30, 58, 95),
    "CLIMATE & COP31": (31, 122, 90),
    "AMERICAS": (200, 122, 30),
    "ASIA-PACIFIC": (107, 63, 160),
    "AFRICA": (168, 87, 27),
    "MARKETS, TECH & SPACE": (11, 19, 43),
}

SS = 2
W = H = 1024
CW, CH = W * SS, H * SS

FD = "/data/data/com.termux/files/usr/share/fonts/TTF/"
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


def draw_text(d, x, y, s, f, fill):
    d.text((x * SS, y * SS), s, font=f, fill=fill)


def hline(d, x1, y, x2, w=1, fill=LIGHT):
    d.rectangle([x1 * SS, y * SS, x2 * SS, (y + w) * SS - 1], fill=fill)


def vline(d, x, y1, y2, w=1, fill=LIGHT):
    d.rectangle([x * SS, y1 * SS, (x + w) * SS - 1, y2 * SS], fill=fill)


def rect(d, x1, y1, x2, y2, fill=None, outline=None, w=1):
    d.rectangle([x1 * SS, y1 * SS, x2 * SS - 1, y2 * SS - 1], fill=fill, outline=outline, width=w * SS)


# ------------------------------------------------------------------ content
# (time, headline, summary). 36 stories over 7 regions.
REGIONS = [
    ("MIDDLE EAST & SECURITY", [
        ("00:20", "Saudi air defences intercept three Houthi missiles over Riyadh",
         "The third straight night of sirens in the Saudi capital."),
        ("02:45", "Saudi-led coalition strikes Houthi drone workshops in Saada",
         "Northern Yemen sites hit; no casualty count released."),
        ("04:10", "IRGC says it downed a US MQ-9 Reaper over the Strait of Hormuz",
         "The Pentagon does not confirm the claim."),
        ("06:30", "Oil tanker damaged and ablaze off Khasab, Oman",
         "Vessel hit while transiting Hormuz; the crew is safe."),
        ("09:05", "Israeli drone strike kills seven in central Gaza",
         "The raid tests the fragile ceasefire; mediators urge restraint."),
    ]),
    ("EUROPE & NATO", [
        ("01:15", "Russian Kh-101 missile crashes in eastern Poland",
         "Debris found near Nowy Lipowiec; air-raid alerts issued."),
        ("02:40", "Overnight strikes hit Kyiv's energy grid and a kindergarten",
         "Among Russia's heaviest attacks of the year, officials say."),
        ("05:00", "Zelensky brands Putin \"a killer\" after Trump's warm words",
         "The rupture follows Trump calling Putin \"my friend\"."),
        ("07:20", "NATO's Rutte to make emergency visit to Warsaw",
         "Called over the Polish airspace breach, officials say."),
        ("08:45", "Denmark expels Russia's defence attaché over a plot",
         "Copenhagen links Moscow to a plan to kill rapper Kyivstoner."),
        ("11:30", "Gen Z protests sweep 25 European nations",
         "Rallies over living costs; a general strike paralyses Italy."),
    ]),
    ("CLIMATE & COP31", [
        ("00:50", "COP31 in Antalya runs past its deadline into overtime",
         "Some 200 nations remain deadlocked on the final text."),
        ("03:30", "\"Fossil fuels\" scrubbed from the draft Antalya Accord",
         "The EU warns the summit risks becoming a \"fossil summit\"."),
        ("06:10", "Panama vows to formally object to the weak draft",
         "Activists call it a possible \"worst COP ever\"."),
        ("08:00", "Draft aims to lift electricity to 35% of energy by 2035",
         "Up from about 21% today, in a push for electrification."),
        ("10:40", "Loss-and-damage finance pushed to triple",
         "An earlier draft cited $120bn a year for adaptation."),
    ]),
    ("AMERICAS", [
        ("00:09", "M6.7 earthquake strikes central Peru near Carhuamayo",
         "Depth 108 km, felt in Lima; no major damage reported."),
        ("05:12", "M5.0 aftershock hits the same Junín region",
         "About five hours after the mainshock; no new casualties."),
        ("07:55", "Three Salvadoran soldiers killed in Haiti blast",
         "The first deaths in El Salvador's Haiti deployment."),
        ("09:20", "Trump defends ties with Putin at a White House briefing",
         "Fresh from China, he takes questions on the war and markets."),
        ("13:00", "Mamdani plans to close New York's Rikers Island by 2032",
         "The mayor sets a deadline to shut the jail complex."),
    ]),
    ("ASIA-PACIFIC", [
        ("01:30", "Asia-Pacific stocks log their worst week since 2020",
         "Nikkei −4.5% and Kospi −5.0% as the tech rout deepens."),
        ("04:55", "ICJ finds Myanmar guilty of genocide against the Rohingya",
         "A first-ever ruling in The Gambia v. Myanmar case."),
        ("06:45", "South Korea catches 111 students cheating at the Suneung",
         "Banned smart devices found during the high-stakes exam."),
        ("09:10", "Nepal's PM Balendra Shah makes his first visit to India",
         "Trade and connectivity top the agenda with New Delhi."),
        ("11:50", "BepiColombo begins science operations at Mercury",
         "The ESA and JAXA orbiter starts its survey of the planet."),
    ]),
    ("AFRICA", [
        ("02:20", "UN: 2,230+ civilians killed in Sudan this year",
         "Some 1,630 died in drone strikes, many in Kordofan."),
        ("05:40", "Mali and Africa Corps strike a camp near Tinessako",
         "A Su-24 raid in the Kidal region, local sources say."),
        ("08:30", "Nearly 600 women killed in South Africa in three months",
         "Police data prompt calls for stronger protection."),
        ("12:15", "Phumzile Mlambo-Ngcuka, ex-UN Women chief, dies at 71",
         "South Africa's former deputy president led UN Women."),
    ]),
    ("MARKETS, TECH & SPACE", [
        ("13:30", "S&P 500 −3.70% to 6,910 as AI fears grip Wall Street",
         "The index closes in correction; Dow −1.93% to 48,147."),
        ("13:35", "Nasdaq plunges 5.28% to 22,617; VIX jumps 26%",
         "Nvidia falls 11% in a broad rout of technology shares."),
        ("14:00", "Anthropic shares slide a day after its record IPO",
         "The stock falls 8–12% after an $81.3bn listing near $1.41tn."),
        ("14:20", "Bitcoin falls below $59,000, down 23% in November",
         "Its worst month since June 2022 as investors flee risk."),
        ("15:00", "Gold drops 4% to about $3,539 as traders seek cash",
         "A safe-haven selloff alongside the equity slide."),
        ("15:30", "Claimed Claude-assisted proof of the Riemann Hypothesis",
         "Anthropic's Levent Alpöge releases it; verification pending."),
    ]),
]

LEADS = [
    ("CLIMATE", "COP31 runs into overtime deadlock over fossil fuels",
     "Some 200 nations miss the Antalya deadline as the draft drops any mention of coal, oil and gas.", (31, 122, 90)),
    ("EUROPE", "Riyadh intercepts missiles as Kyiv burns",
     "Houthi salvos target Saudi Arabia for a third night; Russian strikes pound Ukraine's grid.", (179, 65, 44)),
    ("WORLD", "Peru quake shakes Lima; BepiColombo reaches Mercury",
     "A M6.7 tremor hits central Peru at dawn; Europe's orbiter begins science at the planet.", (200, 122, 30)),
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
mt = "THE GLOBAL DISPATCH"
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
sub = "SATURDAY, 21 NOVEMBER 2026   ·   36 DATED STORIES   ·   7 REGIONS   ·   UTC EDITION"
sw = tw(d, sub, f_sub)
draw_text(d, (W - sw) / 2, band_y + 5, sub, f_sub, PAPER)

# ---- breaking lead strip --------------------------------------------------
hy0 = band_y + 26          # 96
hero_h = 118
gap = 9
hw = (W - 2 * M - 2 * gap) / 3

for i, (tag, head, summ, col) in enumerate(LEADS):
    x = M + i * (hw + gap)
    rect(d, x, hy0, x + hw, hy0 + hero_h, outline=LIGHT, w=1)
    # colour tab
    rect(d, x, hy0, x + hw, hy0 + 3, fill=col)
    f_hl = font(SC_B, 9)
    draw_text(d, x + 7, hy0 + 8, tag, f_hl, col)
    f_hh = font(SERIF_B, 15)
    y = hy0 + 21
    for ln in wrap(d, head, f_hh, hw - 14)[:3]:
        draw_text(d, x + 7, y, ln, f_hh, INK)
        y += line_h(f_hh) * 0.98
    f_hs = font(SC, 8.5)
    for ln in wrap(d, summ, f_hs, hw - 14)[:3]:
        draw_text(d, x + 7, y + 1, ln, f_hs, GRAY)
        y += line_h(f_hs)

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
    for with_sum in (True, False):
        best = None
        for step in range(26, 7, -1):          # scale 1.30 -> 0.80
            scale = step / 20.0
            f_time = font(SC_B, 7.5 * scale)
            f_head = font(SC_B, 10.5 * scale)
            f_sum = font(SC, 8.2 * scale)
            lh_t, lh_h, lh_s = line_h(f_time), line_h(f_head), line_h(f_sum)
            blocks, total = [], 0
            for (tm, hd, sm) in stories:
                hl = wrap(d, hd, f_head, innerw)[:2]
                lines = lh_t + len(hl) * lh_h
                sl = []
                if with_sum:
                    sl = wrap(d, sm, f_sum, innerw)[:2]
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
    if chosen is None:                          # extreme fallback: smallest, no summary
        scale = 0.8
        f_time = font(SC_B, 7.5 * scale); f_head = font(SC_B, 10.5 * scale)
        f_sum = font(SC, 8.2 * scale)
        lh_t, lh_h, lh_s = line_h(f_time), line_h(f_head), line_h(f_sum)
        blocks = [(wrap(d, hd, f_head, innerw)[:2], []) for (tm, hd, sm) in stories]
        chosen = (scale, False, blocks, f_time, f_head, f_sum, lh_t, lh_h, lh_s)

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
        hl = wrap(d, hd, f_head, cw)[:2]
        lines = lh_t + len(hl) * lh_h
        sl = []
        if with_sum:
            sl = wrap(d, sm, f_sum, cw)[:2]
            lines += len(sl) * lh_s
        blocks.append((hl, sl))
        total += lines
    return total + (len(subset) - 1) * 8, (f_time, f_head, f_sum, lh_t, lh_h, lh_s, blocks)

bestC = None
for with_sum in (True, False):
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
    bestC = (0.6, False, None)

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
tick = ("S&P 500 −3.70%   ·   NASDAQ −5.28%   ·   BTC $58,140   ·   BRENT $74.20   ·   "
        "COP31 +18H OVERTIME   ·   BEPICOLOMBO AT MERCURY   ·   COMPILED 21 NOV 2026")
# shrink to fit one line
fs = 8.6
while tw(d, tick, font(SC_B, fs)) > (W - 2 * M - 12) and fs > 5:
    fs -= 0.2
f_tick = font(SC_B, fs)
draw_text(d, (W - tw(d, tick, f_tick)) / 2, ft_y + 4, tick, f_tick, SLATE)

# ------------------------------------------------------------------ save
out = img.resize((W, H), Image.LANCZOS)
out.save("entry.png", format="PNG", optimize=True)
print("wrote entry.png", out.size, os.path.getsize("entry.png"), "bytes")
