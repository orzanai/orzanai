"""Builds the profile cards (dist/card.svg, dist/city.svg, dist/languages.svg).

Runs daily in GitHub Actions with GH_TOKEN set. Standard library only.
Local preview with made-up numbers:  DEMO=1 python3 scripts/build.py
"""
import json, math, os, random, urllib.request
from datetime import date, timedelta
from pathlib import Path

LOGIN = os.environ.get("PROFILE_LOGIN", "orzanai")
NAME = "Orzan"
TAGLINE = "I break AI so you don't have to"
SUBLINE = "AI agents · vibe coding · Claude Code"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"

BG, PANEL, LINE = "#070d14", "#0b1622", "#173244"
TEXT, DIM, MINT, MINT2 = "#d7e3ea", "#6f8796", "#5ef2c2", "#2bd4a0"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "-apple-system,Segoe UI,Helvetica,Arial,sans-serif"
W = 840


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- data
QUERY = """query($login:String!){user(login:$login){login followers{totalCount}
repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100){totalCount
nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name color}}}}}
contributionsCollection{contributionCalendar{totalContributions
weeks{contributionDays{contributionCount date weekday}}}}}}"""


def fetch():
    token = os.environ["GH_TOKEN"]
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    u = json.load(urllib.request.urlopen(req))["data"]["user"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or "#8b949e"])[0] += e["size"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    return {
        "login": u["login"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "total": cal["totalContributions"],
        "weeks": [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]],
        "days": [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]],
        "langs": langs,
    }


def demo():
    random.seed(7)
    days, weeks, start = [], [], date.today() - timedelta(days=364)
    for w in range(53):
        wk = []
        for d in range(7):
            c = 0 if random.random() < 0.45 else int(random.expovariate(0.25))
            wk.append(c)
            days.append(((start + timedelta(days=w * 7 + d)).isoformat(), c))
        weeks.append(wk)
    return {"login": LOGIN, "repos": 4, "stars": 12, "followers": 8, "total": sum(c for _, c in days),
            "weeks": weeks, "days": days,
            "langs": {"Python": [52000, "#3572A5"], "TypeScript": [41000, "#3178c6"],
                      "HTML": [18000, "#e34c26"], "Shell": [4000, "#89e051"], "CSS": [3000, "#563d7c"]}}


# ---------------------------------------------------------------- shared bits
def defs():
    return f"""<defs>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2.2" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{MINT}" stop-opacity=".55"/>
<stop offset=".5" stop-color="{LINE}"/><stop offset="1" stop-color="{MINT}" stop-opacity=".35"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#ffffff" opacity=".018"/></pattern>
</defs>"""


def frame(h, inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">{defs()}'
            f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="18" fill="{BG}" stroke="url(#edge)" stroke-width="1.5"/>'
            f'<rect x="1" y="1" width="{W-2}" height="{h-2}" rx="18" fill="url(#scan)"/>{inner}</svg>')


def write(name, svg):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(svg)


# ---------------------------------------------------------------- card
ICONS = {
    "repo": '<path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.71 1.71.75.75 0 0 1-1.06 1.06A2.49 2.49 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.71A2.49 2.49 0 0 1 4.5 9h8Z"/>',
    "star": '<path d="M8 .25a.75.75 0 0 1 .67.42l1.88 3.8 4.2.61a.75.75 0 0 1 .41 1.28l-3.04 2.96.72 4.18a.75.75 0 0 1-1.09.79L8 12.33l-3.75 1.97a.75.75 0 0 1-1.09-.79l.72-4.18L.84 6.37a.75.75 0 0 1 .42-1.28l4.2-.61L7.33.67A.75.75 0 0 1 8 .25Z"/>',
    "pulse": '<path d="M6 2c.31 0 .59.19.7.48L9 8.73l1.3-2.6A.75.75 0 0 1 11 5.75h4.25a.75.75 0 0 1 0 1.5h-3.79l-1.79 3.58a.75.75 0 0 1-1.37-.07L6 4.53 4.7 8.27a.75.75 0 0 1-.7.48H.75a.75.75 0 0 1 0-1.5h2.72l1.83-4.77A.75.75 0 0 1 6 2Z"/>',
    "people": '<path d="M2 5.5a3.5 3.5 0 1 1 5.9 2.55 5 5 0 0 1 2.98 4.54.75.75 0 0 1-1.5.06 3.5 3.5 0 0 0-6.99 0 .75.75 0 0 1-1.5-.06 5 5 0 0 1 2.99-4.54A3.49 3.49 0 0 1 2 5.5ZM11 4a3 3 0 0 1 1.84 5.37 4.5 4.5 0 0 1 2.66 4.1.75.75 0 0 1-1.5 0 3 3 0 0 0-2.13-2.87.75.75 0 0 1-.53-.72v-.36a.75.75 0 0 1 .4-.66A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0 0 4 2 2 0 0 0 0-4Z"/>',
}


def portrait(x0, y0, size):
    rows = (ROOT / "scripts" / "portrait.txt").read_text().split()
    n = len(rows)
    p = size / n
    dim, mid, hot = [], [], []
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "0":
                continue
            cx, cy = x0 + x * p + p / 2, y0 + y * p + p / 2
            {"1": dim, "2": mid, "3": hot}[ch].append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{p*0.36:.2f}"/>')
    return (f'<g fill="#3fbf9c" opacity=".38">{"".join(dim)}</g>'
            f'<g fill="{MINT2}" opacity=".8">{"".join(mid)}</g>'
            f'<g fill="{MINT}" filter="url(#glow)">{"".join(hot)}</g>')


def card(d):
    h = 344
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1][0])[:4]
    chips_src = [(n, c) for n, (s, c) in top] or [("Claude Code", MINT), ("AI Agents", MINT2)]
    stats = [("repo", d["repos"], "Repositories"), ("star", d["stars"], "Stars"),
             ("pulse", d["total"], "Contributions"), ("people", d["followers"], "Followers")]
    s = []
    # window chrome
    s.append(f'<circle cx="28" cy="26" r="5.5" fill="#ff5f57"/><circle cx="46" cy="26" r="5.5" fill="#febc2e"/><circle cx="64" cy="26" r="5.5" fill="#28c840"/>')
    s.append(f'<text x="92" y="31" font-family="{MONO}" font-size="13" fill="{DIM}">README.md</text>')
    s.append(f'<line x1="1" y1="48" x2="{W-1}" y2="48" stroke="{LINE}"/>')
    # inner panel
    s.append(f'<rect x="20" y="64" width="{W-40}" height="{h-84}" rx="14" fill="{PANEL}" stroke="{LINE}"/>')
    tx = 46
    s.append(f'<text x="{tx}" y="100" font-family="{MONO}" font-size="14" fill="{MINT}">@{esc(d["login"])}</text>')
    s.append(f'<text x="{tx}" y="146" font-family="{SANS}" font-weight="800" font-size="44" fill="{MINT}" filter="url(#glow)" letter-spacing="-.5">{esc(NAME)}</text>')
    s.append(f'<text x="{tx}" y="174" font-family="{SANS}" font-size="15" fill="{TEXT}">{esc(TAGLINE)}</text>')
    s.append(f'<text x="{tx}" y="196" font-family="{MONO}" font-size="12.5" fill="{DIM}">{esc(SUBLINE)}</text>')
    for i, (ic, val, label) in enumerate(stats):
        cx, cy = tx + (i % 2) * 222, 232 + (i // 2) * 30
        s.append(f'<g transform="translate({cx},{cy-12}) scale(.95)" fill="{MINT2}">{ICONS[ic]}</g>')
        s.append(f'<text x="{cx+24}" y="{cy}" font-family="{MONO}" font-size="14"><tspan fill="{TEXT}" font-weight="700">{val:,}</tspan>'
                 f'<tspan fill="{DIM}" dx="8">{label}</tspan></text>')
    x = tx
    for name, color in chips_src:
        w = 26 + len(name) * 7.6
        s.append(f'<rect x="{x}" y="284" width="{w:.0f}" height="26" rx="13" fill="#0f2130" stroke="{LINE}"/>'
                 f'<circle cx="{x+13}" cy="297" r="4" fill="{color}"/>'
                 f'<text x="{x+22}" y="301.5" font-family="{MONO}" font-size="12" fill="{TEXT}">{esc(name)}</text>')
        x += w + 8
    # portrait
    px, ps = W - 20 - 30 - 206, 206
    s.append(f'<rect x="{px-14}" y="80" width="{ps+28}" height="{ps+28}" rx="12" fill="#06111a" stroke="{LINE}"/>')
    s.append(f'<circle cx="{px+ps/2}" cy="{94+ps/2}" r="{ps*0.42}" fill="{MINT}" opacity=".07" filter="url(#soft)"/>')
    s.append(portrait(px, 94, ps))
    write("card.svg", frame(h, "".join(s)))


# ---------------------------------------------------------------- city
def city(d):
    h = 360
    weeks = d["weeks"]
    counts = [c for _, c in d["days"]]
    mx = max(counts + [1])
    active = sum(1 for c in counts if c)
    busiest = max(counts + [0])
    s = []
    s.append(f'<text x="34" y="52" font-family="{SANS}" font-weight="700" font-size="22" fill="{TEXT}">The city I built this year</text>')
    s.append(f'<text x="34" y="96" font-family="{MONO}" font-size="12" letter-spacing="2" fill="{MINT2}">CONTRIBUTIONS</text>')
    s.append(f'<text x="34" y="146" font-family="{SANS}" font-weight="800" font-size="52" fill="{MINT}" filter="url(#glow)">{d["total"]:,}</text>')
    s.append(f'<text x="34" y="182" font-family="{MONO}" font-size="13" fill="{DIM}">{active} active days</text>')
    s.append(f'<text x="34" y="204" font-family="{MONO}" font-size="13" fill="{DIM}">Busiest day: {busiest}</text>')
    s.append(f'<text x="34" y="{h-34}" font-family="{MONO}" font-size="11.5" fill="{DIM}">one tower per day · height = commits, PRs, issues</text>')
    # isometric skyline
    u = 6.6
    cx0, cy0 = 505, 118
    cos, sin = math.cos(math.radians(30)), math.sin(math.radians(30))
    tops = ["#16302c", "#127a5e", "#1fb889", "#5ef2c2"]
    lefts = ["#0d1f1d", "#0b4d3c", "#147a5b", "#2fae8c"]
    rights = ["#0a1817", "#093b2f", "#0f5d46", "#238a6f"]

    def pt(wx, dy, z=0):
        return (cx0 + (wx - dy) * u * cos, cy0 + (wx + dy) * u * sin - z)

    cells = [(w, dd, c) for w, wk in enumerate(weeks) for dd, c in enumerate(wk)]
    cells.sort(key=lambda t: (t[0] + t[1], t[0]))
    for w, dd, c in cells:
        lvl = 0 if c == 0 else min(3, 1 + int(3 * c / (mx + 1)))
        z = 1.5 if c == 0 else 5 + 82 * (c / mx) ** 0.6
        g = 0.12
        a, b, cc, e = pt(w + g, dd + g, z), pt(w + 1 - g, dd + g, z), pt(w + 1 - g, dd + 1 - g, z), pt(w + g, dd + 1 - g, z)
        b0, cc0, e0 = pt(w + 1 - g, dd + g), pt(w + 1 - g, dd + 1 - g), pt(w + g, dd + 1 - g)
        P = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
        glow = ' filter="url(#glow)"' if lvl == 3 else ""
        s.append(f'<polygon points="{P(e, cc, cc0, e0)}" fill="{lefts[lvl]}"/>'
                 f'<polygon points="{P(cc, b, b0, cc0)}" fill="{rights[lvl]}"/>'
                 f'<polygon points="{P(a, b, cc, e)}" fill="{tops[lvl]}"{glow}/>')
    write("city.svg", frame(h, "".join(s)))


# ---------------------------------------------------------------- languages
def languages(d):
    top = sorted(d["langs"].items(), key=lambda kv: -kv[1][0])[:6]
    total = sum(v[0] for _, v in top) or 1
    h = 108 + 34 * max(1, len(top))
    s = [f'<text x="34" y="50" font-family="{SANS}" font-weight="700" font-size="22" fill="{TEXT}">Language Stack</text>',
         f'<text x="34" y="74" font-family="{MONO}" font-size="12.5" fill="{MINT2}">Repository-weighted technologies</text>',
         f'<text x="{W-34}" y="50" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">&gt; stack.scan_</text>']
    if not top:
        s.append(f'<text x="34" y="118" font-family="{MONO}" font-size="13" fill="{DIM}">No public code yet. Check back soon.</text>')
    bx, bw = 300, W - 34 - 300 - 70
    for i, (name, (size, color)) in enumerate(top):
        y = 112 + i * 34
        pct = 100 * size / total
        s.append(f'<circle cx="40" cy="{y-4}" r="5" fill="{color}"/>'
                 f'<text x="56" y="{y}" font-family="{MONO}" font-size="14" fill="{TEXT}">{esc(name)}</text>'
                 f'<rect x="{bx}" y="{y-11}" width="{bw}" height="10" rx="5" fill="#0f2130"/>'
                 f'<rect x="{bx}" y="{y-11}" width="{max(6, bw*pct/100):.1f}" height="10" rx="5" fill="{color}"/>'
                 f'<text x="{W-34}" y="{y}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{DIM}">{pct:.0f}%</text>')
    write("languages.svg", frame(h, "".join(s)))


if __name__ == "__main__":
    data = demo() if os.environ.get("DEMO") else fetch()
    card(data)
    city(data)
    languages(data)
    print("built", sorted(p.name for p in OUT.iterdir()))
