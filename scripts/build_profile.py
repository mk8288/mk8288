#!/usr/bin/env python3
"""Build original README artwork from verified public GitHub data. Stdlib only."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = "mk8288"
SNAPSHOT = ROOT / "data" / "github-public.json"
MONO = "ui-monospace,SFMono-Regular,Consolas,monospace"
SANS = "system-ui,-apple-system,Segoe UI,sans-serif"


def fetch(url: str, *, api: bool = False) -> str:
    headers = {"User-Agent": "mk8288-profile-artwork", "Accept": "application/vnd.github+json" if api else "text/html"}
    token = os.environ.get("GITHUB_TOKEN")
    if api and token:
        headers["Authorization"] = "Bearer " + token
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as response:
                return response.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Unreachable request state")


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tooltips = {}
        self.target = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "td" and "data-date" in a:
            self.cells[a["id"]] = {"date": a["data-date"], "level": int(a["data-level"]), "x": int(a["data-ix"])}
        if tag == "tool-tip" and a.get("for") in self.cells:
            self.target, self.text = a["for"], []

    def handle_data(self, data):
        if self.target:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.target:
            self.tooltips[self.target] = "".join(self.text).strip()
            self.target = None

    def result(self):
        out = []
        for key, cell in self.cells.items():
            tip = self.tooltips[key]
            count = 0 if tip.startswith("No contributions") else int(re.match(r"([\d,]+) contributions? on", tip).group(1).replace(",", ""))
            out.append(dict(cell, y=(date.fromisoformat(cell["date"]).weekday() + 1) % 7, count=count))
        return sorted(out, key=lambda x: x["date"])


def get_snapshot():
    base = "https://api.github.com/users/" + USER
    profile = json.loads(fetch(base, api=True))
    repos = []
    page = 1
    while True:
        batch = json.loads(fetch(base + f"/repos?type=owner&per_page=100&page={page}", api=True))
        if not isinstance(batch, list):
            raise ValueError("Unexpected repository response")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    if len(repos) != profile["public_repos"]:
        raise ValueError("Repository total changed during collection; retry rather than publish mismatched counts")
    calendar_url = f"https://github.com/users/{USER}/contributions"
    html = fetch(calendar_url)
    parser = CalendarParser()
    parser.feed(html)
    cells = parser.result()
    declared = re.search(r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions?', html)
    if not declared or len(cells) < 350:
        raise ValueError("Contribution page markup changed or data is incomplete")
    declared_total = int(declared.group(1).replace(",", ""))
    if sum(x["count"] for x in cells) != declared_total:
        raise ValueError("Parsed calendar does not match GitHub's declared contribution total")
    return {
        "username": USER,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sources": [base, base + "/repos?type=owner&per_page=100", calendar_url],
        "public_repos": profile["public_repos"],
        "contributions": declared_total,
        "period": [cells[0]["date"], cells[-1]["date"]],
        "repositories": [{k: r[k] for k in ["name", "html_url", "fork", "language", "stargazers_count", "archived"]} for r in repos],
        "calendar": cells,
    }


def text(x, y, value, *, size=20, cls="fg", weight=400, mono=False, **attrs):
    extra = " ".join(f'{k.replace("_", "-")}="{escape(str(v), quote=True)}"' for k, v in attrs.items())
    return f'<text x="{x}" y="{y}" font-family="{MONO if mono else SANS}" font-size="{size}" font-weight="{weight}" class="{cls}" {extra}>{escape(str(value))}</text>'


def svg(width, height, content, title, description="", extra_css=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<style>
:root{{--bg:#F6F8FA;--surface:#FFFFFF;--border:#CBD5E1;--fg:#182434;--muted:#526171;--accent:#096B80;--mint:#16704B;--grid:#E2E8F0}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0D1117;--surface:#161D27;--border:#303B49;--fg:#F0F6FC;--muted:#AAB8C7;--accent:#64D8ED;--mint:#72E1B3;--grid:#233043}}}}
.bg{{fill:var(--bg)}}.surface{{fill:var(--surface)}}.fg{{fill:var(--fg)}}.muted{{fill:var(--muted)}}.accent{{fill:var(--accent)}}.mint{{fill:var(--mint)}}.border{{stroke:var(--border)}}
{extra_css}
@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
</style>
{content}</svg>'''


def panel(w, h, cls="surface"):
    return f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="16" class="{cls} border" fill="none"/>'


def hero(compact=False):
    w, h = (480, 348) if compact else (1000, 360)
    p = 28 if compact else 40
    content = panel(w, h, "bg")
    content += text(p, 40 if compact else 42, "MK8288 / SECURITY & SYSTEMS", size=13, mono=True, cls="muted", letter_spacing=1.5)
    if compact:
        content += text(p, 106, "Mohammad", size=49, weight=750)
        content += text(p, 164, "Kaif.", size=57, weight=750)
        content += text(p, 209, "Security engineer. CTF creator.", size=20, cls="muted")
        content += text(p, 239, "Imperial College London · MSc 2026–27", size=16, cls="muted")
        term_y = 275
    else:
        content += text(p, 133, "Mohammad Kaif.", size=68, weight=750, letter_spacing=-2)
        content += text(p, 182, "Security engineer. CTF creator.", size=27, cls="muted")
        content += text(p, 218, "Imperial College London · MSc Security & Resilience", size=18, cls="muted")
        content += '<g transform="translate(822 143)"><path d="M0 -62 L65 -38 L58 30 Q34 66 0 79 Q-34 66 -58 30 L-65 -38 Z" fill="none" stroke="var(--border)" stroke-width="2"/><path d="M-36 15 L-36 -18 L0 -18 L0 -39 M0 -18 L34 -18 L34 16 L0 16 L0 43" fill="none" stroke="var(--accent)" stroke-width="2"/>'
        for x, y in [(-36,15),(0,-39),(34,16),(0,43)]:
            content += f'<circle cx="{x}" cy="{y}" r="5" class="bg" stroke="var(--accent)" stroke-width="2"/>'
        content += '<circle r="4" class="mint"><animateMotion dur="8s" repeatCount="indefinite" path="M-36 15 L-36 -18 L0 -18 L0 -39 L0 -18 L34 -18 L34 16 L0 16 L0 43"/></circle></g>'
        # animateMotion is hidden for reduced-motion viewers by its parent class below.
        content = content.replace('<circle r="4" class="mint">', '<circle r="4" class="mint packet">')
        term_y = 264
    tw = w-2*p
    content += f'<rect x="{p}" y="{term_y}" width="{tw}" height="52" rx="8" class="surface border"/>'
    content += text(p+16, term_y+33, ">", size=21, mono=True, cls="accent")
    content += f'<defs><clipPath id="typing"><rect x="{p+40}" y="{term_y+10}" width="{tw-60}" height="34" class="reveal"/></clipPath></defs>'
    command = "build. test. understand." if compact else "ctf.build()  /  security.research()  /  systems.defend()"
    content += f'<g clip-path="url(#typing)">{text(p+40,term_y+33,command,size=16 if compact else 19,mono=True)}</g>'
    content += f'<rect x="{w-p-22}" y="{term_y+17}" width="7" height="20" class="accent cursor"/>'
    css = '@keyframes type{0%{width:0}16%,92%{width:100%}100%{width:0}}.reveal{animation:type 14s steps(50,end) infinite}@keyframes blink{0%,45%{opacity:1}50%,95%{opacity:0}}.cursor{animation:blink 1.6s step-end infinite}@media(prefers-reduced-motion:reduce){.packet{display:none}.reveal{width:100%}.cursor{opacity:1}}'
    return svg(w,h,content,"Mohammad Kaif | Security engineer and CTF creator","Animated console header. MSc Security and Resilience at Imperial College London, 2026–2027.",css)


def button(label, symbol):
    c = '<rect x=".5" y=".5" width="135" height="37" rx="7" class="surface border"/>'
    c += text(15,25,symbol,size=16,mono=True,cls="accent",weight=600)
    c += text(41,25,label,size=14,weight=600)
    return svg(136,38,c,label)


PROJECTS = [
    ("bastion", "01", "BastionAI", "AI-ASSISTED SECURITY TESTING", ["An experimental agent for authorised", "penetration-testing research."], "Python / Flask / LLM agents", "agent"),
    ("vision", "02", "Face & Object Detection", "COMPUTER VISION", ["Face recognition and YOLOv3 detection", "in the same real-time video stream."], "Python / OpenCV / YOLOv3", "vision"),
    ("lander", "03", "L.A.N.D.E.R", "LUNAR IMAGE SUPER-RESOLUTION", ["Exploring terrain assessment through", "super-resolution of lunar imagery."], "Python / PyTorch / SRGAN", "terrain"),
]


def project_card(item, compact=False):
    slug, number, title, category, lines, stack, icon = item
    w,h=(480,260) if compact else (1000,220)
    p=28 if compact else 36
    c=panel(w,h)
    c+=f'<path d="M{p} 1 H{p+64}" stroke="var(--accent)" stroke-width="3"/>'
    c+=text(p,36,number+" / "+category,size=12 if compact else 13,mono=True,cls="accent",letter_spacing=1)
    c+=text(p,83 if compact else 86,title,size=26 if compact else 33,weight=650,letter_spacing=-.5)
    for i,line in enumerate(lines):
        c+=text(p,124+i*27 if compact else 127+i*26,line,size=18 if compact else 20,cls="muted")
    c+=text(p,h-28,stack,size=14 if compact else 16,mono=True,cls="muted")
    c+=text(w-45,h-28,"↗",size=24,cls="accent")
    if not compact:
        c+='<g transform="translate(855 105)" stroke="var(--border)" stroke-width="2" fill="none">'
        if icon=="agent":
            c+='<rect x="-51" y="-31" width="102" height="73" rx="10"/><path d="M-28 -7 L-16 4 L-28 15 M-3 16 H27" stroke="var(--accent)"/><path d="M-24 -31 V-47 H25 V-31 M-24 42 V57 H25 V42"/>'
        elif icon=="vision":
            c+='<path d="M-60 -25 V-45 H-40 M40 -45 H60 V-25 M60 25 V45 H40 M-40 45 H-60 V25"/><circle r="25" stroke="var(--accent)"/><path d="M-45 0 H45 M0 -35 V35"/>'
        else:
            c+='<path d="M-75 40 L-40 -12 L-15 13 L12 -35 L45 17 L68 -8 L85 40 Z"/><path d="M-65 40 L-27 8 L4 40 L28 -10 L65 40" stroke="var(--accent)"/>'
        c+='</g>'
    return svg(w,h,c,title,"Open the "+title+" repository. "+" ".join(lines))


def activity(data, compact=False):
    w,h=(480,330) if compact else (1000,300)
    p=28 if compact else 36
    c=panel(w,h)
    c+=text(p,37,"PUBLIC GITHUB / "+USER,size=13,mono=True,cls="accent",letter_spacing=1)
    c+=text(p,88,str(data["public_repos"]),size=36,weight=650)
    c+=text(p+72,84,"public repositories",size=17,cls="muted")
    c+=text(p,128,str(data["contributions"]),size=30,weight=650)
    c+=text(p+72,123,"contributions in the displayed year",size=15 if compact else 17,cls="muted")
    grid_y=164
    cols=max(x["x"] for x in data["calendar"])+1
    spacing=(w-2*p)/cols
    size=max(2,spacing-3)
    colors=["var(--grid)","#2B8A6E","#269F7A","#36B995","#72E1B3"]
    for day in data["calendar"]:
        x=p+day["x"]*spacing
        y=grid_y+day["y"]*spacing
        c+=f'<rect x="{x:.2f}" y="{y:.2f}" width="{size:.2f}" height="{size:.2f}" rx="2" fill="{colors[day["level"]]}"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
    c+=f'<rect x="{p}" y="{grid_y-4}" width="2" height="{7*spacing+4:.2f}" class="accent scanner"/>'
    c+=text(p,h-20,"Snapshot "+data["fetched_at"][:10]+" UTC · public data only",size=12,mono=True,cls="muted")
    css=f'@keyframes scan{{0%,8%{{transform:translateX(0)}}88%,100%{{transform:translateX({w-2*p-2}px)}}}}.scanner{{animation:scan 14s linear infinite}}'
    return svg(w,h,c,"Public GitHub contribution trace",f'{data["public_repos"]} public repositories; {data["contributions"]} contributions. Calendar dates {data["period"][0]} through {data["period"][1]}. Scanner animation is decorative.',css)


def language_card(data, compact=False):
    counts=Counter(r["language"] for r in data["repositories"] if not r["fork"] and r["language"])
    w,h=(480,260) if compact else (1000,200)
    p=28 if compact else 36
    c=panel(w,h)
    c+=text(p,38,"PRIMARY LANGUAGES / PUBLIC REPOS" if compact else "PRIMARY LANGUAGES / NON-FORK PUBLIC REPOSITORIES",size=12 if compact else 13,mono=True,cls="accent",letter_spacing=1)
    colors=["#096B80","#25947E","#7175CB","#A17927","#B95D71"]
    x=p
    total=sum(counts.values())
    if not total:
        raise ValueError("No primary-language data available")
    for i,(lang,count) in enumerate(counts.most_common()):
        width=(w-2*p)*count/total
        c+=f'<rect x="{x:.3f}" y="69" width="{width:.3f}" height="14" rx="3" fill="{colors[i%len(colors)]}"/>'
        lx=p+(i%2)*220 if compact else p+i*184
        ly=124+(i//2)*36 if compact else 124
        c+=f'<circle cx="{lx+5}" cy="{ly-5}" r="5" fill="{colors[i%len(colors)]}"/>'
        c+=text(lx+19,ly,f"{lang} · {count}",size=18 if compact else 16)
        x+=width
    c+=text(p,h-29,"Repository counts, not skill ratings.",size=16 if compact else 15,cls="muted")
    return svg(w,h,c,"Primary repository languages",", ".join(f"{k}: {v} repositories" for k,v in counts.most_common()))


def build(data):
    ASSETS.mkdir(parents=True,exist_ok=True)
    files={"hero.svg":hero(),"hero-compact.svg":hero(True),"activity.svg":activity(data),"activity-compact.svg":activity(data,True),"languages.svg":language_card(data),"languages-compact.svg":language_card(data,True)}
    for label,symbol in [("Portfolio","↗"),("LinkedIn","in"),("Email","@")]:
        files["link-"+label.lower()+".svg"]=button(label,symbol)
    for item in PROJECTS:
        files["project-"+item[0]+".svg"]=project_card(item)
        files["project-"+item[0]+"-compact.svg"]=project_card(item,True)
    for label in ["Python","Rust","C / C++","Linux","Docker","Azure","Cloudflare","React","Flask","Burp Suite","Wireshark","Ghidra"]:
        slug=re.sub(r"[^a-z0-9]+","-",label.lower()).strip("-")
        width=max(72,len(label)*8+28)
        content=f'<rect x=".5" y=".5" width="{width-1}" height="31" rx="6" class="surface border"/>'+text(14,21,label,size=13,mono=True)
        files["tool-"+slug+".svg"]=svg(width,32,content,label)
    for name in ["hero.svg", "hero-compact.svg", "activity.svg", "activity-compact.svg"]:
        static = re.sub(r"<animateMotion\b[^>]*/>", "", files[name])
        static = static.replace("</style>", "*{animation:none!important}.packet{display:none}.reveal{width:100%}</style>")
        files[name.replace(".svg", "-static.svg")] = static
    for name,content in files.items():
        ET.fromstring(content)
        (ASSETS/name).write_text(content,encoding="utf-8")
    return files


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--offline",action="store_true",help="Rebuild from the checked-in, dated public snapshot")
    args=p.parse_args()
    if args.offline:
        data=json.loads(SNAPSHOT.read_text())
    else:
        data=get_snapshot()
    assert data["username"] == USER
    assert sum(x["count"] for x in data["calendar"]) == data["contributions"]
    files=build(data)
    if not args.offline:
        SNAPSHOT.parent.mkdir(parents=True,exist_ok=True)
        SNAPSHOT.write_text(json.dumps(data,indent=2)+"\n")
    print(json.dumps({"artwork_files":len(files),"artwork_bytes":sum(len(v.encode()) for v in files.values()),"data_fetched_at":data["fetched_at"],"public_repositories":data["public_repos"],"calendar_cells":len(data["calendar"]),"contributions":data["contributions"],"nonfork_primary_languages":dict(Counter(r["language"] for r in data["repositories"] if not r["fork"] and r["language"]))},indent=2))


if __name__ == "__main__":
    main()
