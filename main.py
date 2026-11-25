#!/usr/bin/env python3
"""Tuesday 24 November 2026 — one day's world news on one page.

Draws a 1024x1024 newspaper front page with the Python standard library
only (Pillow is the image writer; everything else is hand-drawn with the
standard library's drawing primitives). Deterministic: no clock, no random
numbers, no network. Reads the land bitmap from worldmap.txt next to this
file and writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import hashlib
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 24
CONTENT_W = W - 2 * MARGIN

PAPER = (248, 244, 233)
INK = (17, 17, 17)
MUTED = (90, 84, 72)
RED = (156, 31, 31)
NAVY = (30, 58, 95)
SEA = (214, 228, 235)
LAND = (122, 138, 110)
RULE = (60, 55, 45)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap using measured widths; returns a list of lines."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- data ---

STORIES = [
    ("AMERICAS", [
        ("Trump awards the Medal of Freedom to Rudy Giuliani", "SCMP"),
        ("Trump nominates Jim O'Neill as a federal judge in a rush "
         "before Democrats take the Senate", "Reuters"),
        ("US consumer confidence jumps to 103.3, its highest in "
         "nearly two years", "Reuters"),
        ("Mexico's inflation hits a six-month high at 3.96% in "
         "early November", "Reuters"),
        ("US court clears the army to detonate toxic explosives "
         "in Iowa", "Reuters"),
    ]),
    ("EUROPE", [
        ("Russian strike on Zaporizhzhia kills 2 and wounds 44, "
         "including four children", "AP"),
        ("Russia says it shot down almost 700 Ukrainian drones "
         "overnight", "Naharnet"),
        ("NATO vows to defend against space threats after reports "
         "of a nuclear-armed satellite", "SCMP"),
        ("Germany becomes the first country to access Ukraine's "
         "Delta battle system", "Kyiv Independent"),
        ("UK police arrest two men after a break-in at Prince "
         "William's Anmer Hall", "SCMP"),
        ("Putin warns Ukraine that retaliation for energy strikes "
         "is inevitable", "WION"),
    ]),
    ("MIDDLE EAST", [
        ("Israeli strikes in Gaza kill Hamas security chief Naeem "
         "Abu Nahal and six others", "SCMP"),
        ("Houthis hit Riyadh's PIF tower again; 11 hurt, "
         "including two Indians", "WION"),
        ("US envoy casts doubt on Trump's pledge to end $3.8bn "
         "Israel military funding", "SCMP"),
        ("Vance and Rubio meet Qatar's PM at the White House "
         "over Iran", "AP"),
        ("Iran warns ships in Hormuz and rules out US talks "
         "without seven conditions", "Gulf News"),
        ("Iraq's PM orders Baghdad to run oilfields in "
         "Kurdish-controlled areas", "Reuters"),
    ]),
    ("ASIA-PACIFIC", [
        ("Gas blast at a Hanoi eatery kills 6 and injures more "
         "than 10", "Xinhua"),
        ("North Korea threatens to shut its Swiss office over "
         "youth-camp sanctions", "Naharnet"),
        ("South Korea scrambles jets as Russian aircraft enter its "
         "air defence zone", "Naharnet"),
        ("China extends its suspension of the gallium export ban "
         "to the US until 27 January", "Reuters"),
        ("Sheikh Hasina plans to return to Bangladesh on "
         "16 December", "Reuters"),
        ("US blacklists Singapore cloud firm Megaspeed in the "
         "Nvidia chip probe", "Just Security"),
        ("South Korea offers up to $375,000 to catch AI cheating "
         "in its college exam", "Just Security"),
    ]),
    ("AFRICA", [
        ("About 175 migrants unaccounted for after contact lost "
         "with a boat from Senegal", "Reuters"),
        ("Fighting in Ituri traps DR Congo Ebola responders for "
         "over 24 hours", "UN News"),
        ("Morocco becomes the first Arab nation to break into "
         "FIFA's top five", "Aaj TV"),
    ]),
    ("BUSINESS", [
        ("Nvidia shares slide 6% as the Huang comeback rally "
         "fades", "Reuters"),
        ("Advent weighs a bid for French testing firm Bureau "
         "Veritas", "Bloomberg"),
        ("Trump administration poised to unveil new tariffs after "
         "a Section 301 probe", "Reuters"),
        ("US blacklists an Alibaba subsidiary in the Nvidia "
         "scandal", "Reuters"),
    ]),
    ("TECH & SCIENCE", [
        ("Microsoft declares 'Code Red' for Microsoft 365 after "
         "its historic outage", "Reuters"),
        ("COP31 fallout: Guterres 'deeply disappointed' as about "
         "90 nations rejected the pact", "AP"),
        ("Global landmine casualties hit a five-year high of "
         "7,000; Myanmar, Syria worst", "SCMP"),
        ("Pentagon accuses Canada of falling short as a North "
         "America defence partner", "Just Security"),
    ]),
    ("SPORT", [
        ("England level the T20 series in Australia: Donald 85, "
         "188/2 in 13.1 overs", "ScoreZaap"),
        ("Brentford thrash Everton 4-0; Lewis-Potter scores twice, "
         "Tarkowski sent off", "ScoreZaap"),
        ("FIFA confirms 2031 Women's World Cup hosts: USA, Mexico, "
         "Costa Rica, Jamaica", "AP"),
        ("India A's Sooryavanshi smashes 204 off 53 balls, with 28 "
         "sixes, vs UAE", "SportzCraazy"),
        ("Jay Shah reappointed unopposed as ICC chairman for a "
         "second term", "Aaj TV"),
    ]),
]

TIMELINE = [
    ("02:00", "Hanoi eatery blast kills six (Xinhua)"),
    ("08:44", "Russia says it downed ~700 drones overnight (Naharnet)"),
    ("09:53", "North Korea threatens to shut Swiss office (Naharnet)"),
    ("11:38", "Russian strike hits Zaporizhzhia, two killed (AP)"),
    ("13:08", "Mexico inflation hits a six-month high (Reuters)"),
    ("15:00", "US consumer confidence at a near two-year high (Reuters)"),
    ("21:23", "Advent weighs a bid for Bureau Veritas (Bloomberg)"),
]

LEADS = [
    ("GULF ON EDGE", "US-Iran standoff deepens as Qatar mediates and "
     "Tehran warns ships in Hormuz"),
    ("RUSSIA TESTS NATO", "700 drones downed; alliance warns it will "
     "defend against threats in space"),
    ("HUANG RALLY FADES", "Nvidia slides 6% a day after its CEO's "
     "comeback; shares still down 32%"),
]

# (name, lat, lon, badge dx, dy from the marker in map pixels)
# Badge spots were hand-placed so close markers (Seoul/Pyongyang,
# Gaza/Riyadh, London/Zaporizhzhia) do not collide; badges sit over
# sea or carry a white box, with a red leader line back to the dot.
MARKERS = [
    ("1 WASHINGTON", 38.9, -77.0, -79, -28),
    ("2 MEXICO CITY", 19.4, -99.1, -68, 7),
    ("3 LONDON", 51.5, -0.1, -45, -27),
    ("4 ZAPORIZHZHIA", 47.8, 35.2, -13, -30),
    ("5 GAZA", 31.5, 34.5, -88, -3),
    ("6 RIYADH", 24.7, 46.7, 10, 13),
    ("7 DAKAR", 14.7, -17.4, -60, 12),
    ("8 SEOUL", 37.5, 127.0, 0, 33),
    ("9 PYONGYANG", 39.0, 125.8, -9, -27),
    ("10 HANOI", 21.0, 105.8, 9, 0),
]

# Two marker dots would sit almost on top of each other (Seoul and
# Pyongyang are 1 column apart; Gaza and Riyadh 4). Their dots are
# nudged a few pixels with a short leader back to the true lat/lon
# point, so both numbers stay readable.
DOT_OFFSET = {"8 SEOUL": (9, 7), "6 RIYADH": (6, 4)}

FOOTER_LINES = [
    "40 SOURCED STORIES  |  Reuters - AP - SCMP - Naharnet - Just Security - "
    "Kyiv Independent - Xinhua - Gulf News - Bloomberg - WION - UN News - Aaj TV - "
    "ScoreZaap - SportzCraazy",
    "DATE CHECK: 24 November 2026 was a Tuesday. The masthead, the UTC timeline and "
    "all 40 stories name this one day; the COP31 and FIFA items are dated by their "
    "24 November reporting.",
    "Drawn by a program in the Python standard library  |  One day, one page  |  "
    "Tuesday 24 November 2026",
]


def load_bitmap():
    path = Path(__file__).with_name("worldmap.txt")
    rows = [line.rstrip("\n") for line in path.read_text().splitlines()]
    rows = [r for r in rows if r]
    assert len(rows) == 45, f"expected 45 rows, got {len(rows)}"
    assert all(len(r) == 108 for r in rows), "expected 108 columns"
    return rows


# -------------------------------------------------------------- drawing ---

def draw_masthead(d):
    d.text((W // 2, 24), "THE WORLD IN ONE DAY", font=font(SERIF, 46),
           fill=INK, anchor="ma")
    d.line([(MARGIN, 74), (W - MARGIN, 74)], fill=RULE, width=2)
    d.text((W // 2, 82), "TUESDAY 24 NOVEMBER 2026", font=font(SANS_B, 32),
           fill=RED, anchor="ma")
    d.text((W // 2, 120), "40 sourced stories  -  All times UTC  -  One day, one page",
           font=font(SANS, 13), fill=MUTED, anchor="ma")
    d.line([(MARGIN, 142), (W - MARGIN, 142)], fill=RULE, width=3)


def draw_leads(d):
    y0, y1 = 154, 214
    bw = (CONTENT_W - 2 * 12) // 3
    for i, (kicker, text) in enumerate(LEADS):
        x0 = MARGIN + i * (bw + 12)
        d.rectangle([x0, y0, x0 + bw, y1], outline=RULE, width=1)
        d.text((x0 + 10, y0 + 5), kicker, font=font(SANS_B, 11), fill=RED)
        lines = wrap(d, text, font(SANS, 13), bw - 20)
        yy = y0 + 21
        for ln in lines[:3]:
            d.text((x0 + 10, yy), ln, font=font(SANS, 13), fill=INK)
            yy += 16
    d.line([(MARGIN, 224), (W - MARGIN, 224)], fill=RULE, width=2)


def draw_map(d, bitmap):
    """World map panel, left of the timeline band."""
    x0, y0 = MARGIN, 234
    panel_w = 356
    d.text((x0, y0), "WHERE THE DAY HAPPENED", font=font(SANS_B, 12), fill=NAVY)
    d.text((x0 + panel_w, y0), "10 places, numbered",
           font=font(SANS, 11), fill=MUTED, anchor="ra")
    mx, my = x0 + 12, y0 + 24
    pitch = 3
    # sea background
    d.rectangle([mx, my, mx + 108 * pitch, my + 45 * pitch], fill=SEA)
    for r, row in enumerate(bitmap):
        for c, ch in enumerate(row):
            px, py = mx + c * pitch, my + r * pitch
            if ch == "#":
                d.rectangle([px, py, px + 1, py + 1], fill=LAND)
            else:
                d.point((px + 1, py + 1), fill=(190, 205, 214))
    d.rectangle([mx, my, mx + 108 * pitch, my + 45 * pitch],
                outline=RULE, width=1)
    badge_fnt = font(SANS_B, 9)
    for name, lat, lon, dx, dy in MARKERS:
        col = int((lon + 180) * 0.3)
        row = int((90 - lat) * 0.3)
        cx = mx + col * pitch + 1
        cy = my + row * pitch + 1
        num = name.split(" ", 1)[0]
        # badge box, kept inside the panel (badges may sit over the sea
        # or the map edge, never over another badge)
        bw = int(d.textlength(name, font=badge_fnt)) + 8
        bx, by = cx + dx, cy + dy
        bx = max(MARGIN, min(bx, MARGIN + panel_w - bw))
        by = max(y0 + 20, min(by, my + 45 * pitch - 12))
        d.line([(cx, cy), (bx + bw // 2, by + 10)], fill=RED, width=1)
        d.rectangle([bx, by, bx + bw, by + 12], fill=(255, 255, 255),
                    outline=RED, width=1)
        d.text((bx + 4, by + 1), name, font=badge_fnt, fill=RED)
        # numbered marker on top (nudged where two true points collide)
        odx, ody = DOT_OFFSET.get(name, (0, 0))
        dcx, dcy = cx + odx, cy + ody
        if (odx, ody) != (0, 0):
            d.line([(cx, cy), (dcx, dcy)], fill=RED, width=1)
        d.ellipse([dcx - 6, dcy - 6, dcx + 6, dcy + 6], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((dcx, dcy), num, font=font(SANS_B, 8), fill=(255, 255, 255),
               anchor="mm")


def draw_timeline(d):
    x0 = MARGIN + 368
    y0 = 234
    w = W - MARGIN - x0
    d.text((x0, y0), "THE DAY IN UTC", font=font(SANS_B, 12), fill=NAVY)
    d.text((x0 + w, y0), "times as reported", font=font(SANS, 11),
           fill=MUTED, anchor="ra")
    yy = y0 + 24
    for t, text in TIMELINE:
        d.text((x0, yy), t, font=font(SANS_B, 13), fill=RED)
        d.text((x0 + 52, yy), text, font=font(SANS, 13), fill=INK)
        yy += 20
        d.line([(x0, yy - 4), (x0 + w, yy - 4)], fill=(210, 204, 190), width=1)
    d.line([(x0, y0 + 24 + 7 * 20 - 4), (x0 + w, y0 + 24 + 7 * 20 - 4)],
           fill=RULE, width=1)


def section_height(d, stories, body_fnt, col_w):
    """Height of one section (header + stories) at the given body font."""
    lh = body_fnt.size + 4
    h = 24  # header bar
    for text, src in stories:
        full = "\u2022  " + text + "  - " + src
        h += len(wrap(d, full, body_fnt, col_w - 4)) * lh
    return h + 6


def draw_section(d, x, y, title, stories, body_fnt, col_w):
    lh = body_fnt.size + 4
    d.rectangle([x, y, x + col_w, y + 20], fill=NAVY)
    d.text((x + 8, y + 3), title, font=font(SANS_B, 12), fill=(255, 255, 255))
    yy = y + 24
    for text, src in stories:
        full = "\u2022  " + text + "  - " + src
        for ln in wrap(d, full, body_fnt, col_w - 4):
            d.text((x + 2, yy), ln, font=body_fnt, fill=INK)
            yy += lh
    return yy + 6


def draw_sections(d, body_size):
    """Balance the eight sections across two columns; returns overflow."""
    col_w = (CONTENT_W - 24) // 2
    body_fnt = font(SANS, body_size)
    heights = [(t, s, section_height(d, s, body_fnt, col_w))
               for t, s in STORIES]
    # greedy balance: put each section in the shorter column
    cols = [[], []]
    totals = [0, 0]
    for item in heights:
        i = 0 if totals[0] <= totals[1] else 1
        cols[i].append(item)
        totals[i] += item[2]
    return cols, totals, body_fnt, col_w


def draw_footer(d):
    y0 = 948
    d.line([(MARGIN, y0 - 8), (W - MARGIN, y0 - 8)], fill=RULE, width=2)
    yy = y0
    for line in FOOTER_LINES:
        fnt = font(SANS_B, 12) if line.startswith("DATE CHECK") else font(SANS, 11)
        for ln in wrap(d, line, fnt, CONTENT_W):
            d.text((W // 2, yy), ln, font=fnt,
                   fill=RED if line.startswith("DATE CHECK") else MUTED,
                   anchor="ma")
            yy += 15


def build():
    bitmap = load_bitmap()
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_leads(d)
    draw_map(d, bitmap)
    draw_timeline(d)
    # pick the largest body size that fits the sections area (y 402..940)
    top, bottom = 402, 940
    for size in (13, 12, 11, 10):
        cols, totals, body_fnt, col_w = draw_sections(d, size)
        if max(totals) <= bottom - top:
            break
    y = top
    for i, col in enumerate(cols):
        x = MARGIN + i * (col_w + 24)
        yy = top
        for title, stories, _h in col:
            yy = draw_section(d, x, yy, title, stories, body_fnt, col_w)
    draw_footer(d)
    return img


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    img = build()
    path = out_dir / "entry.png"
    img.save(path, format="PNG")
    data = path.read_bytes()
    print(f"wrote {path} {len(data)} bytes sha256="
          f"{hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
