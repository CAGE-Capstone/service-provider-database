import os
import re
import pandas as pd
from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

# --- Configuration ---
CSV_FILE_NAME = 'CapstoneSpreadsheet - Sheet1.csv'
CATEGORY_COL_INDEX = 3
NAME_COL_INDEX = 0

# Common keywords for the homepage
COMMON_KEYWORDS = [
    'church', 'center', 'blue', 'mountain', 'services', 'children',
    'counseling', 'hotline', 'community', 'health', 'youth', 'care',
    'family', 'department', 'college'
]

# Demographic Keyword Maps (Used for filtering when specific columns don't exist)
DEMOGRAPHIC_MAPS = {
    'gender': {
        'Men': [r'\bmen\b', r'\bmale\b', r'\bfather\b'],
        'Women': [r'\bwomen\b', r'\bfemale\b', r'\bmother\b', r'\bpregnancy\b', r'\bmaternal\b']
    },
    'orientation': {
        'LGBTQ+': [r'\blgbt', r'\bgay\b', r'\blesbian\b', r'\bqueer\b', r'\btransgender\b', r'\bpride\b',
                   r'\bsexual orientation\b']
    },
    'race': {
        'Hispanic/Latino': [r'\bhispanic\b', r'\blatino\b', r'\blatina\b', r'\bspanish\b'],
        'Native American': [r'\bnative american\b', r'\bindigenous\b', r'\btribal\b', r'\btribe\b'],
        'Black/African American': [r'\bblack\b', r'\bafrican american\b'],
        'Asian': [r'\basian\b', r'\bpacific islander\b']
    }
}

# --- Global Data ---
ALL_RESOURCES = []
HEADERS = []
CATEGORIES = []


def load_data():
    """Loads CSV and pre-calculates categories and search text for every resource."""
    global ALL_RESOURCES, HEADERS, CATEGORIES
    if not os.path.exists(CSV_FILE_NAME):
        print(f"Error: {CSV_FILE_NAME} not found.")
        return

    try:
        df = pd.read_csv(CSV_FILE_NAME, header=None, keep_default_na=False)
        raw_rows = df.astype(str).values.tolist()

        # Identify Header Row
        header_idx = -1
        for i, row in enumerate(raw_rows):
            if len(row) > NAME_COL_INDEX and row[NAME_COL_INDEX].strip().upper() == 'NAME':
                header_idx = i
                break

        HEADERS = [h.strip().rstrip(':') for h in raw_rows[header_idx]] if header_idx != -1 else []

        # Parse Data with Category Context
        ALL_RESOURCES = []
        current_cat = "GENERAL"

        for i, row in enumerate(raw_rows):
            col_a = row[NAME_COL_INDEX].strip()
            col_d = row[CATEGORY_COL_INDEX].strip()

            # Detect Category Header Row
            if (col_d.startswith('Community Services- ') or col_d.startswith('OTHER- ')) and col_a == '':
                current_cat = col_d.replace('Community Services- ', '').replace('OTHER- ', '').strip().upper()
                continue

            # If it's a valid resource row
            if col_a and col_a.upper() != 'NAME' and "closed" not in col_a.lower():
                ALL_RESOURCES.append({
                    'index': i,
                    'name': col_a,
                    'category': current_cat,
                    'full_row': row,
                    'search_blob': " ".join(row).lower()  # For keyword searching
                })

        CATEGORIES = sorted(list(set(r['category'] for r in ALL_RESOURCES)))

    except Exception as e:
        print(f"Load Error: {e}")


def get_filtered_results(query, cat_filter, gender, race, orientation):
    """Main logic for filtering based on user input and demographics."""
    results = ALL_RESOURCES

    # 1. Search Query
    if query:
        query = query.lower()
        results = [r for r in results if query in r['search_blob']]

    # 2. Category Filter
    if cat_filter and cat_filter != 'All':
        results = [r for r in results if r['category'] == cat_filter]

    # 3. Demographic Filters (Regex Keyword Matching)
    def check_demographic(resource, group_key, selection):
        if not selection or selection == 'All': return True
        patterns = DEMOGRAPHIC_MAPS[group_key].get(selection, [])
        return any(re.search(p, resource['search_blob']) for p in patterns)

    if gender != 'All':
        results = [r for r in results if check_demographic(r, 'gender', gender)]
    if race != 'All':
        results = [r for r in results if check_demographic(r, 'race', race)]
    if orientation != 'All':
        results = [r for r in results if check_demographic(r, 'orientation', orientation)]

    return results


# --- HTML Templates ---

LAYOUT_CSS = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #f0f2f5; color: #1c1e21; }
    .navbar { background: #007bff; color: white; padding: 1rem 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .navbar a { color: white; text-decoration: none; font-weight: bold; }
    .container { display: flex; min-height: 90vh; }

    /* Sidebar Filters */
    .sidebar { width: 280px; background: white; padding: 20px; border-right: 1px solid #ddd; }
    .filter-group { margin-bottom: 20px; }
    .filter-group label { display: block; font-weight: bold; margin-bottom: 8px; font-size: 0.9rem; color: #4b4f56; }
    select, input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ccd0d5; border-radius: 4px; box-sizing: border-box; }
    .apply-btn { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
    .apply-btn:hover { background: #0056b3; }

    /* Results Area */
    .main-content { flex-grow: 1; padding: 30px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
    .resource-card { 
        background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;
        text-decoration: none; color: #007bff; font-weight: 600; text-align: center;
        transition: transform 0.2s, box-shadow 0.2s; display: flex; align-items: center; justify-content: center; min-height: 80px;
    }
    .resource-card:hover { transform: translateY(-3px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); background: #f8f9fa; }

    /* Detail View */
    .detail-card { max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }
    .detail-item { padding: 12px 0; border-bottom: 1px solid #eee; display: flex; }
    .detail-label { width: 200px; font-weight: bold; color: #606770; text-transform: uppercase; font-size: 0.8rem; }
</style>
"""

HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>Walla Walla Resources</title>{{ css|safe }}</head>
<body>
    <div class="navbar">Resource Finder</div>
    <div style="max-width: 700px; margin: 100px auto; text-align: center; background: white; padding: 50px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
        <h1>Community Resource Search</h1>
        <p>Find food, health, shelter, and support services in Walla Walla.</p>
        <form action="/results" method="get" style="margin: 30px 0;">
            <input type="text" name="query" placeholder="Enter keyword (e.g. food, youth, church)..." style="padding: 15px; width: 70%; font-size: 1rem;">
            <button class="apply-btn" style="width: auto; padding: 15px 30px;">Search</button>
        </form>
        <div style="margin-top: 20px;">
            <strong>Quick Categories:</strong><br>
            {% for cat in categories[:8] %}
                <a href="/results?category={{ cat }}" style="display:inline-block; margin: 5px; padding: 5px 12px; background: #e7f3ff; color: #007bff; border-radius: 20px; text-decoration: none; font-size: 0.9rem;">{{ cat }}</a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
<html>
<head><title>Results</title>{{ css|safe }}</head>
<body>
    <div class="navbar"><a href="/">← Back to Home</a></div>
    <div class="container">
        <div class="sidebar">
            <form action="/results" method="get">
                <h3>Refine Search</h3>
                <div class="filter-group">
                    <label>Keyword Search</label>
                    <input type="text" name="query" value="{{ query }}">
                </div>
                <div class="filter-group">
                    <label>Category</label>
                    <select name="category">
                        <option value="All">All Categories</option>
                        {% for cat in categories %}
                        <option value="{{ cat }}" {% if sel_cat == cat %}selected{% endif %}>{{ cat }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="filter-group">
                    <label>Demographic: Gender</label>
                    <select name="gender">
                        <option value="All">All</option>
                        <option value="Men" {% if sel_gen == 'Men' %}selected{% endif %}>Men's Services</option>
                        <option value="Women" {% if sel_gen == 'Women' %}selected{% endif %}>Women's Services</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Demographic: Race</label>
                    <select name="race">
                        <option value="All">All</option>
                        <option value="Hispanic/Latino" {% if sel_race == 'Hispanic/Latino' %}selected{% endif %}>Hispanic/Latino</option>
                        <option value="Native American" {% if sel_race == 'Native American' %}selected{% endif %}>Native American</option>
                        <option value="Black/African American" {% if sel_race == 'Black/African American' %}selected{% endif %}>Black/African American</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Demographic: Orientation</label>
                    <select name="orientation">
                        <option value="All">All</option>
                        <option value="LGBTQ+" {% if sel_ori == 'LGBTQ+' %}selected{% endif %}>LGBTQ+ Focus</option>
                    </select>
                </div>
                <button type="submit" class="apply-btn">Apply Filters</button>
            </form>
        </div>
        <div class="main-content">
            <h2>{{ results|length }} Resources Found</h2>
            <div class="grid">
                {% for item in results %}
                <a href="/resource/{{ item.index }}" class="resource-card">{{ item.name }}</a>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""


# --- Flask Routes ---

@app.route('/')
def home():
    load_data()  # Refresh data
    return render_template_string(HOME_HTML, categories=CATEGORIES, css=LAYOUT_CSS)


@app.route('/results')
def results():
    query = request.args.get('query', '')
    category = request.args.get('category', 'All')
    gender = request.args.get('gender', 'All')
    race = request.args.get('race', 'All')
    orientation = request.args.get('orientation', 'All')

    filtered_data = get_filtered_results(query, category, gender, race, orientation)

    return render_template_string(
        RESULTS_HTML,
        results=filtered_data,
        query=query,
        categories=CATEGORIES,
        sel_cat=category, sel_gen=gender, sel_race=race, sel_ori=orientation,
        css=LAYOUT_CSS
    )


@app.route('/resource/<int:row_index>')
def resource_detail(row_index):
    # Find resource in global list
    res = next((r for r in ALL_RESOURCES if r['index'] == row_index), None)
    if not res: return "Resource not found", 404

    detail_items = []
    for i, header in enumerate(HEADERS):
        if i < len(res['full_row']):
            val = res['full_row'][i].strip()
            if val and val != "nan":
                detail_items.append((header, val))

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }}</title>{{ css|safe }}</head>
        <body>
            <div class="navbar"><a href="javascript:history.back()">← Back to Results</a></div>
            <div class="detail-card">
                <h1 style="color:#007bff; margin-top:0;">{{ name }}</h1>
                <p style="background: #e7f3ff; display: inline-block; padding: 5px 15px; border-radius: 20px; color: #007bff; font-weight: bold;">{{ category }}</p>
                <div style="margin-top: 20px;">
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
    """, name=res['name'], category=res['category'], details=detail_items, css=LAYOUT_CSS)


if __name__ == '__main__':
    load_data()
    app.run(debug=True)