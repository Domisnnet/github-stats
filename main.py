import os
import math
from flask import Flask, send_file, request, make_response
from collections import Counter
import logging
from logging.handlers import RotatingFileHandler

# --- App and Logger Setup ---
app = Flask(__name__)
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# --- Theming and Colors (ALL THEMES NOW INCLUDED) ---
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "HTML": "#e34c26",
    "CSS": "#563d7c", "TypeScript": "#2b7489", "Java": "#b07219",
    "Shell": "#89e051", "C++": "#f34b7d", "C": "#555555",
    "PHP": "#4F5D95", "Ruby": "#701516", "Go": "#00ADD8", "Other": "#ededed"
}

THEMES = {
    "tokyonight": {
        "background": "#1a1b27", "title": "#70a5fd", "text": "#a9b1d6",
        "icon": "#70a5fd", "border": "#414868",
        "rank_circle_bg": "#414868", "rank_circle_fill": "#70a5fd"
    },
    "dracula": {
        "background": "#282a36", "title": "#ff79c6", "text": "#f8f8f2",
        "icon": "#ff79c6", "border": "#44475a",
        "rank_circle_bg": "#44475a", "rank_circle_fill": "#ff79c6"
    },
    "gruvbox": {
        "background": "#282828", "title": "#fabd2f", "text": "#ebdbb2",
        "icon": "#fabd2f", "border": "#504945",
        "rank_circle_bg": "#504945", "rank_circle_fill": "#fabd2f"
    },
    "onedark": {
        "background": "#282c34", "title": "#61afef", "text": "#abb2bf",
        "icon": "#61afef", "border": "#3f444f",
        "rank_circle_bg": "#3f444f", "rank_circle_fill": "#61afef"
    }
}

# --- SVG Icon Paths ---
ICONS = {
    "star": "M12 .5l3.09 6.26L22 7.77l-5 4.87 1.18 6.88L12 16.31l-6.18 3.22L7 12.64l-5-4.87 6.91-1.01L12 .5z",
    "commit": "M10.5 7.5a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0zm-2.5 3a.5.5 0 00-1 0v4.362l2.25 1.125a.5.5 0 00.5-.866L10 14.362V10.5zM15 4a1 1 0 10-2 0v1.51a3.52 3.52 0 00-1.5-.99V4a1 1 0 10-2 0v.51a3.52 3.52 0 00-1.5.99V4a1 1 0 10-2 0v.51C4.02 5.2 3 6.48 3 8v5.5a.5.5 0 001 0V8c0-1.04.5-2 1.5-2.5v2.24l-1.3.65a.5.5 0 00-.4.866l4 2a.5.5 0 00.4 0l4-2a.5.5 0 00-.4-.866l-1.3-.65V5.5C14.5 5 15 6.04 15 7v1a.5.5 0 001 0V7c0-1.52-1.02-2.8-2.5-3.49V4z",
    "pr": "M11.28 2.5a.75.75 0 00-1.06 0l-2.5 2.5a.75.75 0 000 1.06l2.5 2.5a.75.75 0 101.06-1.06L9.81 6l1.47-1.44a.75.75 0 000-1.06zm-6.56 0a.75.75 0 00-1.06 0L1.16 5.06a.75.75 0 000 1.06L3.66 8.5a.75.75 0 001.06-1.06L3.19 6l1.53-1.44a.75.75 0 000-1.06zM8 3a.75.75 0 000 1.5h.25V11a.75.75 0 001.5 0V4.5H10A.75.75 0 0010 3H8zM6 12a.75.75 0 00-1.5 0v1.25H2a.75.75 0 000 1.5h2.5a.75.75 0 00.75-.75V12z",
    "issue": "M8 1.5a6.5 6.5 0 100 13 6.5 6.5 0 000-13zM0 8a8 8 0 1116 0A8 8 0 010 8zm9-3a1 1 0 10-2 0v3a1 1 0 001 1h1a1 1 0 100-2H9V5z",
    "contrib": "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 010-1.5h2V1H4.5C3.12 1 2 2.12 2 3.5V13h1.5a.75.75 0 010 1.5H2a.75.75 0 01-.75-.75V3.5h.003A2.49 2.49 0 012 2.5zM3.5 1A1.5 1.5 0 002 2.5v1.41C2.58 3.57 3.47 3.5 4.5 3.5h5V1H3.5z",
}

# --- Data Fetching and Processing ---
def k_formatter(num):
    return f"{num / 1000:.1f}k" if num >= 1000 else str(num)

def fetch_github_stats(username):
    return {
        "name": f"{username.capitalize()}",
        "total_stars": 2200,
        "total_commits": 1000,
        "total_prs": 202,
        "total_issues": 95,
        "contrib_to": 63,
    }

def calculate_rank(stats):
    score = ( stats["total_commits"] * 1.5 + stats["total_prs"] * 2.0 + stats["total_issues"] * 0.5 + stats["total_stars"] * 1.0 + stats["contrib_to"] * 2.5 )
    THRESHOLDS = {"S++": 6000, "S+": 5000, "S": 4500, "A++": 4000, "A+": 3000, "A": 2000, "B+": 1000, "B": 500}
    RANK_ORDER = ["C", "B", "B+", "A", "A+", "A++", "S", "S+", "S++"]
    level = "C"
    for r, threshold in sorted(THRESHOLDS.items(), key=lambda item: item[1]):
        if score >= threshold:
            level = r
    current_rank_index = RANK_ORDER.index(level)
    lower_bound = THRESHOLDS.get(level, 0)
    upper_bound_rank_key = RANK_ORDER[current_rank_index + 1] if current_rank_index + 1 < len(RANK_ORDER) else None
    upper_bound = THRESHOLDS.get(upper_bound_rank_key, lower_bound * 1.5) if upper_bound_rank_key else lower_bound * 1.5
    progress = ((score - lower_bound) / (upper_bound - lower_bound)) * 100 if (upper_bound - lower_bound) > 0 else 0
    return {"level": level, "progress": min(max(progress, 0), 100)}

# --- Main SVG Generation ---
def create_stats_svg(stats, theme_name="tokyonight"):
    theme = THEMES.get(theme_name.lower(), THEMES["tokyonight"])
    rank = calculate_rank(stats)
    width, height = 495, 195
    padding = 20
    stat_items_map = {
        "Total Stars": (ICONS["star"], stats["total_stars"]),
        "Total Commits": (ICONS["commit"], stats["total_commits"]),
        "Total PRs": (ICONS["pr"], stats["total_prs"]),
        "Total Issues": (ICONS["issue"], stats["total_issues"]),
        "Contributed to": (ICONS["contrib"], stats["contrib_to"]),
    }
    stats_svg = ""
    for i, (label, (icon_path, value)) in enumerate(stat_items_map.items()):
        icon_svg = f'<svg x="0" y="{i * 25}" width="16" height="16" viewBox="0 0 16 16" fill="{theme["icon"]}" xmlns="http://www.w3.org/2000/svg"><path d="{icon_path}"/></svg>'
        text_svg = f'<text x="25" y="{i * 25 + 12}" fill="{theme["text"]}" font-size="14" font-family="Segoe UI, Ubuntu, Sans-Serif"><tspan font-weight="bold">{label}:</tspan><tspan x="150" text-anchor="start">{k_formatter(value)}</tspan></text>'
        stats_svg += f'<g>{icon_svg}{text_svg}</g>\n'
    radius, cx, cy = 50, 50, 50
    circumference = 2 * math.pi * radius
    offset = circumference - (rank["progress"] / 100 * circumference)
    rank_circle_svg = f'''
        <g transform="translate(0, 0)">
            <circle r="{radius}" cx="{cx}" cy="{cy}" fill="none" stroke="{theme["rank_circle_bg"]}" stroke-width="10"/>
            <circle r="{radius}" cx="{cx}" cy="{cy}" fill="none" stroke="{theme["rank_circle_fill"]}" stroke-width="10" stroke-dasharray="{circumference}" stroke-dashoffset="{offset}" stroke-linecap="round" transform="rotate(-90 {cx} {cy})"/>
            <text x="{cx}" y="{cy + 10}" text-anchor="middle" fill="{theme["text"]}" font-size="28" font-weight="bold" font-family="Segoe UI, Ubuntu, Sans-Serif">{rank["level"]}</text>
        </g>'''
    return f'''
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none" xmlns="http://www.w3.org/2000/svg">
        <style>.header {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: {theme["title"]}; }}</style>
        <rect x="0.5" y="0.5" rx="4.5" height="99%" width="{width - 1}" fill="{theme["background"]}" stroke="{theme["border"]}"/>
        <g transform="translate({padding}, {padding})">
            <text x="0" y="18" class="header">{stats["name"]}\'s GitHub Stats</text>
            <g transform="translate(0, 40)">{stats_svg}</g>
            <g transform="translate(320, 30)">{rank_circle_svg}</g>
        </g>
    </svg>'''

def create_language_donut_chart_svg(langs, theme_name="tokyonight"):
    theme = THEMES.get(theme_name.lower(), THEMES["tokyonight"])
    total_size = sum(langs.values())
    top_langs = langs.most_common(6)
    paths, legend_items = [], ""
    start_angle = -90
    for i, (lang, size) in enumerate(top_langs):
        percent = (size / total_size) * 100
        angle = (size / total_size) * 360
        end_angle = start_angle + angle
        large_arc_flag = 1 if angle > 180 else 0
        x1_outer, y1_outer = 225 + 50 * math.cos(math.radians(start_angle)), 90 + 50 * math.sin(math.radians(start_angle))
        x2_outer, y2_outer = 225 + 50 * math.cos(math.radians(end_angle)), 90 + 50 * math.sin(math.radians(end_angle))
        x1_inner, y1_inner = 225 + 30 * math.cos(math.radians(start_angle)), 90 + 30 * math.sin(math.radians(start_angle))
        x2_inner, y2_inner = 225 + 30 * math.cos(math.radians(end_angle)), 90 + 30 * math.sin(math.radians(end_angle))
        color = theme.get("lang_colors", {}).get(lang, "#ededed")
        path_d = f"M {x1_outer} {y1_outer} A 50 50 0 {large_arc_flag} 1 {x2_outer} {y2_outer} L {x2_inner} {y2_inner} A 30 30 0 {large_arc_flag} 0 {x1_inner} {y1_inner} Z"
        paths.append(f'<path d="{path_d}" fill="{color}" />')
        legend_items += f'<g transform="translate(20, {50 + i * 20})"><rect width="10" height="10" fill="{color}" rx="2" ry="2"/><text x="15" y="10" font-family="Arial, sans-serif" font-size="12" fill="{theme["text"]}">'{lang} ({percent:.1f}%)</text></g>'
        start_angle = end_angle
    return f'''
    <svg width="450" height="180" xmlns="http://www.w3.org/2000/svg">
        <rect width="448" height="178" x="1" y="1" rx="5" ry="5" fill="{theme["background"]}" stroke="{theme["border"]}"/>
        <text x="20" y="30" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="{theme["title"]}">Top Languages</text>
        <g transform="translate(200, 0)">{" ".join(paths)}</g>
        <g>{legend_items}</g>
    </svg>'''

# --- Flask Routes ---
@app.route('/')
def index():
    return send_file('src/index.html')

@app.route("/api/stats")
def api_stats():
    username = request.args.get('username', 'Domisnnet')
    theme = request.args.get('theme', 'tokyonight')
    stats = fetch_github_stats(username)
    svg_content = create_stats_svg(stats, theme)
    resp = make_response(svg_content)
    resp.headers["Content-Type"] = "image/svg+xml"
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route("/api/top-langs")
def api_top_langs():
    username = request.args.get('username', 'Domisnnet')
    theme = request.args.get('theme', 'tokyonight')
    langs = Counter({"Python": 58000, "JavaScript": 22000, "HTML": 15000, "Java": 3000, "Shell": 1500, "CSS": 500})
    svg_content = create_language_donut_chart_svg(langs, theme)
    resp = make_response(svg_content)
    resp.headers["Content-Type"] = "image/svg+xml"
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 8080), debug=True)