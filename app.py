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

# Broadened Demographic Keyword Maps
# These ensure that even if the exact term isn't used, related services are found.
DEMOGRAPHIC_MAPS = {
    'gender': {
        'Men': [r'\bmen\b', r'\bmale\b', r'\bfather\b', r'\bboy\b'],
        'Women': [r'\bwomen\b', r'\bfemale\b', r'\bmother\b', r'\bpregnancy\b', r'\bmaternal\b', r'\bgirl\b',
                  r'\bywca\b']
    },
    'orientation': {
        'LGBTQ+': [r'\blgbt', r'\bgay\b', r'\blesbian\b', r'\bqueer\b', r'\btransgender\b', r'\bpride\b',
                   r'\bsexual orientation\b', r'\btriple point\b']
    },
    'race': {
        'Hispanic/Latino': [r'\bhispanic\b', r'\blatino\b', r'\blatina\b', r'\bspanish\b', r'\bbilingual\b',
                            r'\bmexican\b'],
        'Native American': [r'\bnative american\b', r'\bindigenous\b', r'\btribal\b', r'\btribe\b', r'\bumatilla\b',
                            r'\bconfederated\b'],
        'Black/African American': [r'\bblack\b', r'\bafrican american\b', r'\bcolor\b', r'\bminority\b', r'\bequity\b',
                                   r'\bdiversity\b', r'\bmulticultural\b'],
        'Asian': [r'\basian\b', r'\bpacific islander\b', r'\bchinese\b', r'\bkorean\b', r'\bmultilingual\b',
                  r'\blanguage\b', r'\bimmigrant\b', r'\brefugee\b']
    }
}

# --- Global Data Storage ---
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

        # Identify Header Row (Look for 'NAME')
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

            # Detect Category Header Row (The rows like "Community Services- FOOD")
            if (col_d.startswith('Community Services- ') or col_d.startswith('OTHER- ')) and col_a == '':
                current_cat = col_d.replace('Community Services- ', '').replace('OTHER- ', '').strip().upper()
                continue

            # If it's a valid resource row (not a header or empty)
            if col_a and col_a.upper() != 'NAME' and "closed" not in col_a.lower():
                ALL_RESOURCES.append({
                    'index': i,
                    'name': col_a,
                    'category': current_cat,
                    'full_row': row,
                    'search_blob': " ".join(row).lower()  # Lumped text for fast searching
                })

        CATEGORIES = sorted(list(set(r['category'] for r in ALL_RESOURCES)))

    except Exception as e:
        print(f"Load Error: {e}")


def get_filtered_results(query, cat_filter, gender, race, orientation):
    """The multi-gate filtering logic."""
    results = ALL_RESOURCES

    # Gate 1: Keyword Search
    if query:
        query = query.lower()
        results = [r for r in results if query in r['search_blob']]

    # Gate 2: Category Filter
    if cat_filter and cat_filter != 'All':
        results = [r for r in results if r['category'] == cat_filter]

    # Gate 3: Demographic Filters
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
    .resource-card { 
        background: white; padding: 20px; border-radius: 8px; border: 1px solid #ddd;
        text-decoration: none; color: #007bff; font-weight: 600; text-align: center;
        display: flex; align-items: center; justify-content: center; min-height: 80px;
    }
    .detail-card { max-width: 800px; margin: 40px auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .detail-item { display: flex; padding: 15px 0; border-bottom: 1px solid #eee; }
    .detail-label { width: 180px; font-weight: bold; color: #666; text-transform: uppercase; font-size: 0.8rem; }
</style>
"""

HOME_HTML = """
<!DOCTYPE html>
<html>
<head><title>Walla Walla Resources</title>{{ css|safe }}</head>
<body>
    <div class="navbar">Community Resource Finder</div>
    <div style="max-width: 800px; margin: 80px auto; text-align: center; background: white; padding: 60px; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
        <h1>How can we help you today?</h1>
        <p>Search for local services in the Walla Walla Valley.</p>
        <form action="/results" method="get" style="margin: 30px 0;">
            <input type="text" name="query" placeholder="Search by name, service, or keyword..." style="padding: 15px; width: 75%; font-size: 1.1rem;">
            <button class="apply-btn" style="width: auto; padding: 15px 40px;">Find Help</button>
        </form>
        <div>
            <strong>Quick Browse:</strong><br>
            {% for cat in categories[:10] %}
                <a href="/results?category={{ cat }}" style="display:inline-block; margin: 5px; padding: 8px 15px; background: #f0f7ff; color: #007bff; border-radius: 20px; text-decoration: none; font-size: 0.85rem;">{{ cat }}</a>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
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
                <div class="filter-group">
                    <label>Identity & Gender</label>
                    <select name="gender">
                        <option value="All">All</option>
                        <option value="Men" {% if sel_gen == 'Men' %}selected{% endif %}>Men's Services</option>
                        <option value="Women" {% if sel_gen == 'Women' %}selected{% endif %}>Women's Services</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Cultural/Race Focus</label>
                    <select name="race">
                        <option value="All">All</option>
                        <option value="Hispanic/Latino" {% if sel_race == 'Hispanic/Latino' %}selected{% endif %}>Hispanic/Latino</option>
                        <option value="Native American" {% if sel_race == 'Native American' %}selected{% endif %}>Native American</option>
                        <option value="Black/African American" {% if sel_race == 'Black/African American' %}selected{% endif %}>Black/African American</option>
                        <option value="Asian" {% if sel_race == 'Asian' %}selected{% endif %}>Asian/Pacific Islander</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Sexual Orientation</label>
                    <select name="orientation">
                        <option value="All">All</option>
                        <option value="LGBTQ+" {% if sel_ori == 'LGBTQ+' %}selected{% endif %}>LGBTQ+ Focused</option>
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
            {% if results|length == 0 %}
                <p>No services found matching those criteria. Try broadening your filters.</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""


# --- Routes ---

@app.route('/')
def home():
    load_data()
    return render_template_string(HOME_HTML, categories=CATEGORIES, css=LAYOUT_CSS)


@app.route('/results')
def results():
    query = request.args.get('query', '')
    category = request.args.get('category', 'All')
    gender = request.args.get('gender', 'All')
    race = request.args.get('race', 'All')
    orientation = request.args.get('orientation', 'All')

    filtered = get_filtered_results(query, category, gender, race, orientation)

    return render_template_string(
        RESULTS_HTML,
        results=filtered,
        query=query,
        categories=CATEGORIES,
        sel_cat=category, sel_gen=gender, sel_race=race, sel_ori=orientation,
        css=LAYOUT_CSS
    )


@app.route('/resource/<int:row_index>')
def resource_detail(row_index):
    res = next((r for r in ALL_RESOURCES if r['index'] == row_index), None)
    if not res: return "Resource not found", 404

    detail_items = []
    for i, header in enumerate(HEADERS):
        if i < len(res['full_row']):
            val = res['full_row'][i].strip()
            if val and val != "nan" and val != "":
                detail_items.append((header, val))

    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><title>{{ name }}</title>{{ css|safe }}</head>
        <body>
            <div class="navbar"><a href="javascript:history.back()">← Back to Results</a></div>
            <div class="detail-card">
                <h1 style="color:#007bff; margin-bottom:5px;">{{ name }}</h1>
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
    """, name=res['name'], category=res['category'], details=detail_items, css=LAYOUT_CSS)


if __name__ == '__main__':
    load_data()
    app.run(debug=True)