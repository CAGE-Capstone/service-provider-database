import os
import re
import pandas as pd
from flask import Flask, render_template_string, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# necessary for frontend to access backend
from flask_cors import CORS

app = Flask(__name__)

# allow access
CORS(app)

# --- Constants & Config ---
NAME_COL_INDEX = 0
CATEGORY_COL_INDEX = 3

# Typo & encoding corrections
CORRECTION_MAP = {
    "childrenâ€™s": "children's",
    "â€™": "'",
    "â€“": "-",
    "â€”": "-",
    "Helth": "Health",
    "Educaion": "Education",
    "Wall Walla": "Walla Walla",
    "Mental Helth": "Mental Health",
    "Servivces": "Services",
    "Cousel": "Counsel",
    "Deparment": "Department",
    "Communtiy": "Community"
}

# Homepage priority categories
HOME_PRIORITY = [
    'FOOD',
    'HEALTH',
    'MENTAL HEALTH',
    'EDUCATION AND RESEARCH',
    'ENVIRONMENT AND ANIMALS',
    'RELIGIOUS GROUPS',
    'ARTS'
]

# Demographic keyword patterns
DEMOGRAPHIC_MAPS = {
    'gender': {
        'Men': [r'\bmen\b', r'\bmale\b', r'\bfather\b', r'\bboy\b'],
        'Women': [r'\bwomen\b', r'\bfemale\b', r'\bmother\b', r'\bpregnancy\b', r'\bmaternal\b', r'\bgirl\b', r'\bywca\b']
    },
    'orientation': {
        'LGBTQ+': [r'\blgbt', r'\bgay\b', r'\blesbian\b', r'\bqueer\b', r'\btransgender\b', r'\bpride\b',
                   r'\bsexual orientation\b', r'\btriple point\b']
    },
    'race': {
        'Hispanic/Latino': [r'\bhispanic\b', r'\blatino\b', r'\blatina\b', r'\bspanish\b', r'\bbilingual\b', r'\bmexican\b'],
        'Native American': [r'\bnative american\b', r'\bindigenous\b', r'\btribal\b', r'\btribe\b', r'\bumatilla\b', r'\bconfederated\b'],
        'Black/African American': [r'\bblack\b', r'\bafrican american\b', r'\bcolor\b', r'\bminority\b', r'\bequity\b', r'\bdiversity\b', r'\bmulticultural\b'],
        'Asian': [r'\basian\b', r'\bpacific islander\b', r'\bchinese\b', r'\bkorean\b', r'\bmultilingual\b', r'\blanguage\b', r'\bimmigrant\b', r'\brefugee\b']
    }
}

# --- Global Data ---
ALL_RESOURCES = []
HEADERS = []
CATEGORIES = []
HOME_CATEGORIES = []

# --- Utility Functions ---
def clean_text(text):
    if not text: return ""
    for typo, correction in CORRECTION_MAP.items():
        if "â" in typo:
            text = text.replace(typo, correction)
        else:
            text = re.sub(re.escape(typo), correction, text, flags=re.IGNORECASE)
    return text

def load_data():
    global ALL_RESOURCES, HEADERS, CATEGORIES, HOME_CATEGORIES

    if not os.path.exists("credentials.json"):
        print("Error: credentials.json not found")
        return

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open("CapstoneSpreadsheet").sheet1
    raw_rows = sheet.get_all_values()

    # Find header row
    header_idx = -1
    for i, row in enumerate(raw_rows):
        if len(row) > NAME_COL_INDEX and row[NAME_COL_INDEX].strip().upper() == "NAME":
            header_idx = i
            break

    if header_idx != -1:
        HEADERS[:] = [clean_text(h.strip().rstrip(":")) for h in raw_rows[header_idx]]

    # Process rows
    temp_resources = []
    current_cat = "GENERAL"
    for i, row in enumerate(raw_rows):
        cleaned_row = [clean_text(cell) for cell in row]
        col_a = cleaned_row[NAME_COL_INDEX].strip()
        col_d = cleaned_row[CATEGORY_COL_INDEX].strip()

        if (col_d.startswith("Community Services- ") or col_d.startswith("OTHER- ")) and col_a == "":
            current_cat = col_d.replace("Community Services- ", "").replace("OTHER- ", "").strip().upper()
            current_cat = clean_text(current_cat)
            continue

        if col_a and col_a.upper() != "NAME" and "closed" not in col_a.lower():
            temp_resources.append({
                "index": i,
                "name": col_a,
                "category": current_cat,
                "full_row": cleaned_row,
                "search_blob": " ".join(cleaned_row).lower()
            })

    ALL_RESOURCES[:] = sorted(temp_resources, key=lambda x: x["name"].strip().lower())
    full_cat_list = sorted(list(set(r["category"] for r in ALL_RESOURCES)))
    CATEGORIES[:] = full_cat_list
    p_list = [c for c in HOME_PRIORITY if c in full_cat_list]
    o_list = [c for c in full_cat_list if c not in HOME_PRIORITY]
    HOME_CATEGORIES[:] = p_list + o_list

def get_filtered_results(query, cat_filter, gender, race, orientation):
    results = ALL_RESOURCES
    if query:
        query = query.lower()
        results = [r for r in results if query in r["search_blob"]]
    if cat_filter and cat_filter != "All":
        results = [r for r in results if r["category"] == cat_filter]

    def check_demographic(resource, group_key, selection):
        if not selection or selection == "All": return True
        patterns = DEMOGRAPHIC_MAPS[group_key].get(selection, [])
        return any(re.search(p, resource["search_blob"]) for p in patterns)

    if gender != "All": results = [r for r in results if check_demographic(r, "gender", gender)]
    if race != "All": results = [r for r in results if check_demographic(r, "race", race)]
    if orientation != "All": results = [r for r in results if check_demographic(r, "orientation", orientation)]

    return sorted(results, key=lambda x: x["name"].strip().lower())

# --- HTML Templates ---
LAYOUT_CSS = """<style>
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; }
.navbar { background: #007bff; color: white; padding: 1rem 2rem; }
.navbar a { color: white; text-decoration: none; font-weight: bold; }
.container { display: flex; min-height: 90vh; }
.sidebar { width: 300px; background: white; padding: 25px; border-right: 1px solid #ddd; }
.filter-group { margin-bottom: 20px; }
.filter-group label { display: block; font-weight: bold; margin-bottom: 5px; font-size: 0.9rem; color: #555; }
select, input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
.apply-btn { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
.main-content { flex-grow: 1; padding: 30px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
.resource-card { background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd; text-decoration: none; color: #007bff; font-weight: 600; text-align: center; display: flex; align-items: center; justify-content: center; min-height: 80px; }
.detail-card { max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.detail-item { display: flex; padding: 15px 0; border-bottom: 1px solid #eee; }
.detail-label { width: 180px; font-weight: bold; color: #666; text-transform: uppercase; font-size: 0.8rem; }
</style>"""

HOME_HTML = """<!DOCTYPE html>
<html>
<head><title>Walla Walla Resources</title>{{ css|safe }}</head>
<body>
<div class="navbar">Community Resource Finder</div>
<div style="max-width: 800px; margin: 80px auto; text-align: center; background: white; padding: 60px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
<h1>How can we help you today?</h1>
<form action="/results" method="get" style="margin: 30px 0;">
<input type="text" name="query" placeholder="Search for name, service, or keyword..." style="padding: 15px; width: 75%; font-size: 1.1rem;">
<button class="apply-btn" style="width: auto; padding: 15px 40px;">Find Help</button>
</form>
<div>
<strong>Quick Browse:</strong><br>
{% for cat in home_categories[:12] %}
<a href="/results?category={{ cat }}" style="display:inline-block; margin: 5px; padding: 8px 15px; background: #f0f7ff; color: #007bff; border-radius: 20px; text-decoration: none; font-size: 0.85rem;">{{ cat }}</a>
{% endfor %}
</div>
</div>
</body>
</html>"""

RESULTS_HTML = """<!DOCTYPE html>
<html>
<head><title>Search Results</title>{{ css|safe }}</head>
<body>
<div class="navbar"><a href="/">← Start Over</a></div>
<div class="container">
<div class="sidebar">
<form action="/results" method="get">
<h3>Filter Results</h3>
<div class="filter-group">
<label>Keyword</label>
<input type="text" name="query" value="{{ query }}">
</div>
<div class="filter-group">
<label>Service Category</label>
<select name="category">
<option value="All">All Categories</option>
{% for cat in categories %}
<option value="{{ cat }}" {% if sel_cat == cat %}selected{% endif %}>{{ cat }}</option>
{% endfor %}
</select>
</div>
<button type="submit" class="apply-btn">Update Results</button>
</form>
</div>
<div class="main-content">
<h2>{{ results|length }} Resources Match Your Filters</h2>
<div class="grid">
{% for item in results %}
<a href="/resource/{{ item.index }}" class="resource-card">{{ item.name }}</a>
{% endfor %}
</div>
</div>
</div>
</body>
</html>"""

# --- Flask Routes ---
@app.route('/')
def home():
    load_data()
    return render_template_string(HOME_HTML, home_categories=HOME_CATEGORIES, css=LAYOUT_CSS)

@app.route('/results')
def results():
    query = request.args.get('query', '')
    category = request.args.get('category', 'All')
    gender = request.args.get('gender', 'All')
    race = request.args.get('race', 'All')
    orientation = request.args.get('orientation', 'All')
    filtered = get_filtered_results(query, category, gender, race, orientation)
    return render_template_string(RESULTS_HTML, results=filtered, query=query, categories=CATEGORIES, sel_cat=category, css=LAYOUT_CSS)

@app.route('/resource/<int:row_index>')
def resource_detail(row_index):
    res = next((r for r in ALL_RESOURCES if r["index"] == row_index), None)
    if not res: return "Resource not found", 404
    detail_items = [(HEADERS[i], res["full_row"][i]) for i in range(len(HEADERS)) if i < len(res["full_row"]) and res["full_row"][i].strip()]
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head><title>{{ name }}</title>{{ css|safe }}</head>
    <body>
    <div class="navbar"><a href="javascript:history.back()">← Back</a></div>
    <div class="detail-card">
    <h1>{{ name }}</h1>
    <span style="background: #e7f3ff; color: #007bff; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">{{ category }}</span>
    <div style="margin-top: 30px;">
    {% for h, v in details %}
    <div class="detail-item">
    <div class="detail-label">{{ h }}</div>
    <div class="detail-value">{{ v }}</div>
    </div>
    {% endfor %}
    </div>
    </div>
    </body>
    </html>
    """, name=res["name"], category=res["category"], details=detail_items, css=LAYOUT_CSS)

# JSON API endpoints for organizations and categories

from flask import jsonify

@app.route('/api/organizations')
def api_organizations():
    return jsonify([
        {
            "id": r["index"],
            "name": r["name"],
            "category": r["category"],
            "data": r["full_row"]
        }
        for r in ALL_RESOURCES
    ])


@app.route('/api/categories')
def api_categories():
    return jsonify(CATEGORIES)


if __name__ == "__main__":
    load_data()
    app.run(debug=True)