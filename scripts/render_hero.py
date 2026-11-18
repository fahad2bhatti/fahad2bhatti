import os, base64, urllib.request
from pathlib import Path
from PIL import Image, ImageOps
from fontTools import subset

USER = "fahad2bhatti"
FIRST = "Fahad"
SECOND = "Bhatti"          # apna surname/doosra lafz yahan badlo
LABEL = "FLUTTER DEVELOPER · NUML"
LINE1 = "I build Flutter apps with Firebase and AI,"
LINE2 = "and ship them solo."
LINK = "github.com/fahad2bhatti"

COLS = 80                  # portrait ki detail (zyada = zyada detail)
CHAR_W, LINE_H, FS = 4.2, 7.6, 7
RAMP = "@%#*+=-:. "        # dark -> light
INK, PAPER, MUTED, BLUE = "#1a1a1a", "#f4f3ef", "#6b665c", "#2563eb"
STATIC = os.environ.get("STATIC") == "1"

FONT_BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/instrumentserif/"
FONTS = {"InstrumentSerif-Regular": "serif-400", "InstrumentSerif-Italic": "serif-400i"}


def get_fonts():
    out = {}
    for src, name in FONTS.items():
        woff = Path(f"fonts/{name}.woff")
        if not woff.exists():
            ttf = Path(f"fonts/{src}.ttf")
            if not ttf.exists():
                urllib.request.urlretrieve(FONT_BASE + src + ".ttf", ttf)
            opts = subset.Options()
            opts.flavor = "woff"
            opts.layout_features = ["*"]
            f = subset.load_font(str(ttf), opts)
            s = subset.Subsetter(opts)
            s.populate(unicodes=list(range(0x20, 0x7F)) + [0xB7, 0x2192, 0x2197])
            s.subset(f)
            subset.save_font(f, str(woff), opts)
        out[name] = base64.b64encode(woff.read_bytes()).decode()
    return out


def get_avatar():
    p = Path("assets/avatar.png")
    if not p.exists():
        req = urllib.request.Request(f"https://github.com/{USER}.png?size=460",
                                     headers={"User-Agent": "Mozilla/5.0"})
        p.write_bytes(urllib.request.urlopen(req).read())
    return Image.open(p)


def ascii_rows(img):
    img = ImageOps.grayscale(img.convert("RGB"))
    w, h = img.size
    s = min(w, h)
    img = img.crop(((w - s) // 2, (h - s) // 2, (w + s) // 2, (h + s) // 2))
    img = ImageOps.autocontrast(img, cutoff=2)
    rows = int(COLS * (CHAR_W / LINE_H) * 1.0 * (h / h))  # square image
    rows = int(COLS * CHAR_W / LINE_H)
    img = img.resize((COLS, rows))
    px = img.load()
    out = []
    for y in range(rows):
        line = "".join(RAMP[int(px[x, y] / 256 * len(RAMP))] for x in range(COLS))
        out.append(line.rstrip())
    return out


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    fonts = get_fonts()
    rows = ascii_rows(get_avatar())
    W, H = 900, 430
    px0 = 530
    py0 = (H - len(rows) * LINE_H) / 2 + 6
    css = f"""
@font-face{{font-family:'ISerif';src:url(data:font/woff;base64,{fonts['serif-400']})}}
@font-face{{font-family:'ISerifI';src:url(data:font/woff;base64,{fonts['serif-400i']})}}
.serif{{font-family:'ISerif',Georgia,serif}}
.serifi{{font-family:'ISerifI',Georgia,serif;font-style:italic}}
.sans{{font-family:'Segoe UI',Helvetica,Arial,sans-serif}}
.mono{{font-family:'SFMono-Regular',Consolas,'Courier New',monospace}}
@keyframes rise{{from{{opacity:0;transform:translateY(20px)}}}}
@keyframes fade{{from{{opacity:0}}}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""
    if STATIC:
        css += "*{animation:none!important}"
    p = []
    p.append(f'<rect width="{W}" height="{H}" rx="18" fill="{PAPER}"/>')
    p.append(f'''<defs><linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="320" y2="0">
<stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
<stop offset=".5" stop-color="{BLUE}"/><stop offset=".58" stop-color="{INK}"/><stop offset="1" stop-color="{INK}"/>
<animateTransform attributeName="gradientTransform" type="translate" from="-320 0" to="640 0" dur="5s" repeatCount="indefinite"/>
</linearGradient></defs>''')
    p.append(f'<rect x="52" y="52" width="8" height="8" fill="{BLUE}" opacity=".5" style="animation:pulse 2s ease-in-out infinite"/>')
    p.append(f'<text class="mono" x="70" y="60" font-size="12" letter-spacing="1.5" fill="{MUTED}" style="animation:fade .8s backwards">{esc(LABEL)}</text>')
    p.append(f'<text class="serif" x="46" y="185" font-size="132" fill="{INK}" style="animation:rise .9s .2s ease-out backwards">{esc(FIRST)}</text>')
    p.append(f'<text class="serifi" x="46" y="298" font-size="132" fill="url(#sh)" style="animation:rise .9s .45s ease-out backwards">{esc(SECOND)}</text>')
    p.append(f'<text class="sans" x="52" y="342" font-size="18" fill="{INK}" style="animation:rise .8s .8s ease-out backwards">{esc(LINE1)}</text>')
    p.append(f'<text class="sans" x="52" y="367" font-size="18" fill="{INK}" style="animation:rise .8s .9s ease-out backwards">{esc(LINE2)}</text>')
    p.append(f'<text class="mono" x="52" y="400" font-size="13" fill="{INK}" style="animation:fade .8s 1.1s backwards">{esc(LINK)} <tspan fill="{BLUE}">↗</tspan></text>')
    for i, r in enumerate(rows):
        if not r.strip():
            continue
        y = py0 + (i + 1) * LINE_H
        d = 0.4 + i * 0.03
        p.append(f'<text class="mono" xml:space="preserve" x="{px0}" y="{y:.1f}" font-size="{FS}" fill="{INK}" '
                 f'textLength="{len(r) * CHAR_W:.1f}" lengthAdjust="spacing" style="white-space:pre;animation:fade .35s {d:.2f}s backwards">{esc(r)}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            f'<style>{css}</style>{"".join(p)}</svg>')


if __name__ == "__main__":
    Path("cards").mkdir(exist_ok=True)
    Path("cards/hero.svg").write_text(build(), encoding="utf-8")
    print("cards/hero.svg ready")
