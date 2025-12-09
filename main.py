import os
import math
import requests
import logging
from logging.handlers import RotatingFileHandler
from collections import Counter
from flask import Flask, send_file, request, make_response
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Correctly configure logging for Flask
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Language colors are shared across themes for consistency
LANG_COLORS = {
    "Python": "#3572A5",
    "JavaScript": "#f1e05a",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "TypeScript": "#2b7489",
    "Java": "#b07219",
    "Shell": "#89e051",
    "C++": "#f34b7d",
    "C": "#555555",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Go": "#00ADD8",
    "Other": "#ededed"
}

# Definição de múltiplos temas
THEMES = {
    "tokyonight": {
        "background": "#1a1b27",
        "title": "#70a5fd",
        "text": "#38bdae",
        "icon": "#bf91f3",
        "border": "#414868",
        "lang_colors": LANG_COLORS
    },
    "dracula": {
        "background": "#282a36",
        "title": "#ff79c6",
        "text": "#ffffff",
        "icon": "#bd93f9",
        "border": "#44475a",
        "lang_colors": LANG_COLORS
    },
    "gruvbox": {
        "background": "#282828",
        "title": "#fabd2f",
        "text": "#ebdbb2",
        "icon": "#d3869b",
        "border": "#504945",
        "lang_colors": LANG_COLORS
    },
    "onedark": {
        "background": "#282c34",
        "title": "#61afef",
        "text": "#ffffff",
        "icon": "#c678dd",
        "border": "#3f444f",
        "lang_colors": LANG_COLORS
    }
}

def fetch_github_stats(username):
    """
    Returns a dummy dictionary with sample GitHub stats to avoid hitting API rate limits.
    """
    app.logger.info(f"Returning dummy stats data for user: {username}")
    return {
        "name": username,
        "Total Stars": 123,
        "Total Forks": 45,
        "Public Repos": 67,
        "Followers": 890,
        "Total Commits": 2500, # Increased for a better rank
        "Total PRs": 512,      
        "Total Issues": 256,    
        "Contributions": 2048 
    }

def calculate_rank(stats):
    """Calculates a rank based on GitHub stats."""
    COMMITS_WEIGHT = 1.75
    PRS_WEIGHT = 1.5
    ISSUES_WEIGHT = 1
    STARS_WEIGHT = 1.25
    FOLLOWERS_WEIGHT = 1

    score = (
        stats.get("Total Commits", 0) * COMMITS_WEIGHT +
        stats.get("Total PRs", 0) * PRS_WEIGHT +
        stats.get("Total Issues", 0) * ISSUES_WEIGHT +
        stats.get("Total Stars", 0) * STARS_WEIGHT +
        stats.get("Followers", 0) * FOLLOWERS_WEIGHT
    )

    THRESHOLDS = {
        "S+": 10000, "S": 7500, "A+": 5000, "A": 2500,
        "B+": 1000, "B": 500, "C+": 250, "C": 100,
    }
    
    rank = "C"
    for r, threshold in THRESHOLDS.items():
        if score >= threshold:
            rank = r
            break
            
    RANK_COLORS = {
        "S": "#FFD700",
        "A": "#38bdae",
        "B": "#70a5fd",
        "C": "#c9cacc",
    }
    
    base_rank = rank[0]
    color = RANK_COLORS.get(base_rank, RANK_COLORS["C"])

    return {"level": rank, "color": color}

def create_stats_svg(stats, theme):
    '''Creates an SVG image for the GitHub stats.'''
    if not stats:
        return f'''<svg width="450" height="180" xmlns="http://www.w3.org/2000/svg">
                    <rect width="100%" height="100%" fill="{theme['background']}" rx="5" ry="5"/>
                    <text x="50%" y="50%" fill="#ff4a4a" text-anchor="middle" font-family="Arial, sans-serif">Failed to fetch GitHub stats</text>
                  </svg>'''

    rank = calculate_rank(stats)
    stat_items_svg = ""
    y_position = 70
    
    display_stats = {
        "Total Stars": stats.get("Total Stars"),
        "Total Forks": stats.get("Total Forks"),
        "Public Repos": stats.get("Public Repos"),
        "Followers": stats.get("Followers")
    }

    for key, value in display_stats.items():
        if value is not None:
            stat_items_svg += f'''
            <g transform="translate(25, {y_position})">
                <text x="25" y="15" font-family="Arial, sans-serif" font-size="14" fill="{theme['text']}">
                    <tspan font-weight="bold">{key}:</tspan> {value}
                </text>
            </g>
            '''
            y_position += 25

    rank_svg = f'''
    <g transform="translate(400, 45)">
        <text text-anchor="middle" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="{rank['color']}">
            {rank['level']}
        </text>
    </g>
    '''

    svg = f'''
    <svg width="450" height="180" xmlns="http://www.w3.org/2000/svg">
        <rect width="448" height="178" x="1" y="1" rx="5" ry="5" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
        <text x="25" y="35" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="{theme['title']}">
            GitHub Stats
        </text>
        {stat_items_svg}
        {rank_svg}
    </svg>
    '''
    return svg.strip()

def fetch_top_languages(username):
    """
    Returns a dummy Counter object with sample language data to avoid hitting API rate limits.
    """
    app.logger.info(f"Returning dummy language data for user: {username}")
    return Counter({
        "Python": 58000,
        "JavaScript": 22000,
        "HTML": 15000,
        "Java": 3000,
        "Shell": 1500,
        "CSS": 500
    })

def create_language_donut_chart_svg(langs, theme):
    "Creates a donut chart SVG for top languages."
    if not langs or not isinstance(langs, Counter):
        return f'''<svg width="450" height="180" xmlns="http://www.w3.org/2000/svg">
                    <rect width="100%" height="100%" fill="{theme['background']}" rx="5" ry="5"/>
                    <text x="50%" y="50%" fill="#ff4a4a" text-anchor="middle" font-family="Arial, sans-serif">Failed to fetch language data</text>
                   </svg>'''

    total_size = sum(langs.values())
    top_langs = langs.most_common(6)

    cx, cy, r = 225, 90, 50
    inner_r = 30
    start_angle = -90
    
    paths = []
    legend_items = []

    for i, (lang, size) in enumerate(top_langs):
        percent = (size / total_size) * 100
        angle = (size / total_size) * 360
        end_angle = start_angle + angle

        large_arc_flag = 1 if angle > 180 else 0
        
        x1_outer = cx + r * math.cos(math.radians(start_angle))
        y1_outer = cy + r * math.sin(math.radians(start_angle))
        x2_outer = cx + r * math.cos(math.radians(end_angle))
        y2_outer = cy + r * math.sin(math.radians(end_angle))

        x1_inner = cx + inner_r * math.cos(math.radians(start_angle))
        y1_inner = cy + inner_r * math.sin(math.radians(start_angle))
        x2_inner = cx + inner_r * math.cos(math.radians(end_angle))
        y2_inner = cy + inner_r * math.sin(math.radians(end_angle))

        color = theme["lang_colors"].get(lang, theme["lang_colors"]['Other'])
        
        path_d = f"M {x1_outer} {y1_outer} A {r} {r} 0 {large_arc_flag} 1 {x2_outer} {y2_outer} L {x2_inner} {y2_inner} A {inner_r} {inner_r} 0 {large_arc_flag} 0 {x1_inner} {y1_inner} Z"
        paths.append(f'<path d="{path_d}" fill="{color}" />')
        
        legend_x = 20
        legend_y = 50 + i * 20
        legend_items.append(f'''
            <g transform="translate({legend_x}, {legend_y})">
                <rect width="10" height="10" fill="{color}" rx="2" ry="2"/>
                <text x="15" y="10" font-family="Arial, sans-serif" font-size="12" fill="{theme['text']}">
                    {lang} ({percent:.1f}%)
                </text>
            </g>
        ''')

        start_angle = end_angle

    svg = f'''
    <svg width="450" height="180" xmlns="http://www.w3.org/2000/svg">
        <rect width="448" height="178" x="1" y="1" rx="5" ry="5" fill="{theme['background']}" stroke="{theme['border']}" stroke-width="2"/>
        <text x="20" y="30" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="{theme['title']}">Top Languages</text>
        <g transform="translate(200, 0)">
           {" ".join(paths)}
        </g>
        <g>
            {" ".join(legend_items)}
        </g>
    </svg>'''
    return svg.strip()


@app.route('/')
def index():
    return send_file('src/index.html')

@app.route("/api/stats")
def api_stats():
    username = request.args.get('username')
    theme_name = request.args.get('theme', 'tokyonight')
    app.logger.info(f"Received request for stats for username: {username} with theme: {theme_name}")
    if not username:
        app.logger.warning("Username not provided.")
        return "Please provide a username, e.g., ?username=Domisnnet", 400

    theme = THEMES.get(theme_name.lower(), THEMES["tokyonight"])
    stats = fetch_github_stats(username)
    svg_content = create_stats_svg(stats, theme)
    
    response = make_response(svg_content)
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['cache-control'] = 's-maxage=3600, stale-while-revalidate'
    
    return response

@app.route("/api/top-langs")
def api_top_langs():
    username = request.args.get('username')
    theme_name = request.args.get('theme', 'tokyonight')
    app.logger.info(f"Received request for top-langs for username: {username} with theme: {theme_name}")
    if not username:
        app.logger.warning("Username not provided for top-langs.")
        return "Please provide a username, e.g., ?username=Domisnnet", 400
        
    theme = THEMES.get(theme_name.lower(), THEMES["tokyonight"])
    langs = fetch_top_languages(username)
    svg_content = create_language_donut_chart_svg(langs, theme)
    
    response = make_response(svg_content)
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['cache-control'] = 's-maxage=3600, stale-while-revalidate'
    
    return response

def main():
    app.run(port=int(os.environ.get('PORT', 8080)), host='0.0.0.0', debug=True)

if __name__ == "__main__":
    main()
