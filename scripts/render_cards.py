import os, json, math, random, urllib.request
import datetime as dt
from pathlib import Path

USER = "fahad2bhatti"
NAME = "Fahad"
TAGLINE = "Flutter developer · Firebase · AI/ML"
SUBLINE = "BSCS student at NUML, Pakistan · available on Fiverr"

INK, PAPER, MUTED = "#1a1a1a", "#f6f1e7", "#6b665c"
BLUE, RED, YELLOW = "#2563eb", "#e5484d", "#f5b301"
LEVELS = ["#e4dfd2", "#bfd3fb", "#7fa8f7", "#3b7af0", "#1d4ed8"]

TILES = [
    ("BUILD", BLUE, "#ffffff", "Flutter + Firebase", "Android apps, built solo"),
    ("FREELANCE", RED, "#ffffff", "Fiverr", "Apps for clients"),
    ("LEARN", YELLOW, INK, "BSCS · 4th year", "NUML, Pakistan"),
]

STATIC = os.environ.get("STATIC") == "1"
OUT = Path("cards")
OUT.mkdir(exist_ok=True)

BASE_CSS = """
text{font-family:Georgia,'Times New Roman',serif}
.sans{font-family:'Segoe UI',Helvetica,Arial,sans-serif}
@keyframes rise{from{opacity:0;transform:translateY(18px)}}
@keyframes pop{from{opacity:0;transform:scale(.2)}}
@keyframes grow{from{transform:scaleY(0)}}
@keyframes fade{from{opacity:0}}
@keyframes swing{from{opacity:0;transform:translateY(60px) rotate(-6deg)}60%{opacity:1;transform:translateY(-8px) rotate(1deg)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(7px)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.cell{transform-box:fill-box;transform-origin:center}
.bar{transform-box:fill-box;transform-origin:bottom}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""
if STATIC:
    BASE_CSS += "*{animation:none!important}"


def svg(w, h, body, bg=PAPER):
    bgrect = f'<rect width="{w}" height="{h}" rx="18" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}"><style>{BASE_CSS}</style>{bgrect}{body}</svg>')


# ---------- data ----------
QUERY = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def fetch_weeks():
    tok = os.environ.get("GH_TOKEN")
    if not tok:
        print("WARNING: GH_TOKEN nahi mila, demo data use ho raha hai (sirf preview ke liye)")
        today = dt.date.today()
        start = today - dt.timedelta(days=364)
        start -= dt.timedelta(days=(start.weekday() + 1) % 7)
        weeks, d = [], start
        while d <= today:
            week = []
            for _ in range(7):
                if d <= today:
                    week.append((d.isoformat(), random.choice([0, 0, 0, 1, 2, 3, 5, 8])))
                d += dt.timedelta(days=1)
            weeks.append(week)
        return weeks
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {tok}", "Content-Type": "application/json"},
    )
    data = json.load(urllib.request.urlopen(req))
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return [[(x["date"], x["contributionCount"]) for x in w["contributionDays"]]
            for w in cal["weeks"]]


def compute(weeks):
    days = sorted(x for w in weeks for x in w)
    today = dt.date.today()
    days = [x for x in days if dt.date.fromisoformat(x[0]) <= today]
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c > 0)
    best_day = max(days, key=lambda x: x[1])
    cur = 0
    seq = list(reversed(days))
    if seq and seq[0][1] == 0:
        seq = seq[1:]
    for _, c in seq:
        if c > 0:
            cur += 1
        else:
            break
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    keys, y, m = [], today.year, today.month
    for _ in range(12):
        keys.append((y, m))
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    keys.reverse()
    mt = {k: 0 for k in keys}
    for d, c in days:
        dd = dt.date.fromisoformat(d)
        if (dd.year, dd.month) in mt:
            mt[(dd.year, dd.month)] += c
    return dict(total=total, active=active, best_day=best_day, cur=cur,
                longest=longest, months=mt)


# ---------- cards ----------
def hero():
    body = f'''
<defs><linearGradient id="sh" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="300" y2="0">
<stop offset="0" stop-color="{INK}"/><stop offset=".42" stop-color="{INK}"/>
<stop offset=".5" stop-color="{BLUE}"/><stop offset=".58" stop-color="{INK}"/>
<stop offset="1" stop-color="{INK}"/>
<animateTransform attributeName="gradientTransform" type="translate" from="-300 0" to="600 0" dur="5s" repeatCount="indefinite"/>
</linearGradient></defs>
<text x="52" y="70" font-size="22" fill="{MUTED}" class="sans" style="animation:rise .8s ease-out backwards">Hi, I'm</text>
<text x="48" y="155" font-size="88" fill="url(#sh)" style="animation:rise .9s .2s ease-out backwards">{NAME}</text>
<text x="52" y="198" font-size="24" fill="{INK}" class="sans" style="animation:rise .9s .5s ease-out backwards">{TAGLINE}</text>
<circle cx="58" cy="228" r="5" fill="{BLUE}" style="animation:pulse 2s ease-in-out infinite"/>
<text x="72" y="233" font-size="15" fill="{MUTED}" class="sans" style="animation:rise .9s .7s ease-out backwards">{SUBLINE}</text>
<circle cx="800" cy="80" r="46" fill="{BLUE}" opacity=".12"/>
<circle cx="740" cy="170" r="26" fill="{YELLOW}" opacity=".25"/>
<circle cx="840" cy="190" r="18" fill="{RED}" opacity=".2"/>'''
    return svg(900, 260, body)


def graph(weeks, st):
    cell, gap = 13, 3
    n = len(weeks)
    width = n * (cell + gap) - gap
    x0 = (900 - width) // 2
    y0 = 62
    mx = max(c for w in weeks for _, c in w) or 1
    parts = [f'<text x="{x0}" y="38" font-size="20" fill="{INK}" '
             f'style="animation:fade .8s .9s backwards">{st["total"]} contributions in the last year</text>']
    for ci, w in enumerate(weeks):
        for d, c in w:
            row = (dt.date.fromisoformat(d).weekday() + 1) % 7
            lvl = 0 if c == 0 else max(1, min(4, math.ceil(4 * c / mx)))
            x = x0 + ci * (cell + gap)
            y = y0 + row * (cell + gap)
            delay = 1.0 + ci * 0.025
            parts.append(f'<rect class="cell" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                         f'fill="{LEVELS[lvl]}" style="animation:pop .4s {delay:.2f}s ease-out backwards"/>')
    return svg(900, y0 + 7 * (cell + gap) + 14, "".join(parts))


def months_card(st):
    mt = st["months"]
    vals = list(mt.values())
    mx = max(vals) or 1
    best_i = vals.index(max(vals))
    bd = dt.date.fromisoformat(st["best_day"][0]).strftime("%b %d")
    stats = [(str(st["total"]), "contributions"), (f'{st["cur"]} days', "current streak"),
             (str(st["active"]), "active days"), (f'{st["best_day"][1]}', f"busiest day · {bd}")]
    p = []
    for i, (big, lab) in enumerate(stats):
        x = 48 + i * 210
        p.append(f'<text x="{x}" y="72" font-size="40" fill="{INK}" style="animation:rise .7s {1.6 + i * .1:.1f}s backwards">{big}</text>')
        p.append(f'<text x="{x}" y="98" font-size="14" fill="{MUTED}" class="sans" style="animation:fade .7s {1.8 + i * .1:.1f}s backwards">{lab}</text>')
    base, maxh, slot = 290, 130, (900 - 96) / 12
    for i, ((y, m), c) in enumerate(mt.items()):
        h = max(4, c / mx * maxh)
        x = 48 + i * slot + 11
        col = BLUE if i == best_i else "#cfc8b8"
        d = 1.9 + i * 0.06
        p.append(f'<rect class="bar" x="{x:.1f}" y="{base - h:.1f}" width="45" height="{h:.1f}" rx="6" fill="{col}" style="animation:grow .7s {d:.2f}s ease-out backwards"/>')
        p.append(f'<text x="{x + 22.5:.1f}" y="{base + 22}" font-size="13" text-anchor="middle" fill="{MUTED}" class="sans">{dt.date(y, m, 1).strftime("%b")}</text>')
        if i == best_i:
            p.append(f'<text x="{x + 22.5:.1f}" y="{base - h - 8:.1f}" font-size="16" text-anchor="middle" fill="{BLUE}" style="animation:pop .5s 2.8s backwards">{c}</text>')
    return svg(900, 330, "".join(p))


def tile(i, label, bg, fg, big, small):
    d = 2.6 + i * 0.2
    body = f'''
<g class="bar" style="animation:swing 1s {d:.1f}s cubic-bezier(.2,.8,.2,1) backwards">
<rect x="6" y="6" width="278" height="168" rx="20" fill="{bg}"/>
<text x="28" y="44" font-size="14" letter-spacing="3" fill="{fg}" class="sans" opacity=".85">{label}</text>
<text x="28" y="108" font-size="32" fill="{fg}">{big}</text>
<text x="28" y="136" font-size="14" fill="{fg}" class="sans" opacity=".85">{small}</text>
<text x="246" y="152" font-size="26" fill="{fg}" class="sans" style="animation:nudge 2s ease-in-out infinite">→</text>
</g>'''
    return svg(290, 180, body, bg=None)


def main():
    weeks = fetch_weeks()
    st = compute(weeks)
    (OUT / "graph.svg").write_text(graph(weeks, st), encoding="utf-8")
    (OUT / "months.svg").write_text(months_card(st), encoding="utf-8")
    for i, (label, bg, fg, big, small) in enumerate(TILES):
        (OUT / f"tile{i + 1}.svg").write_text(tile(i, label, bg, fg, big, small), encoding="utf-8")
    print("cards/ updated:", st["total"], "contributions")


if __name__ == "__main__":
    main()
