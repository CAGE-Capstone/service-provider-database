import os
import re

import pandas as pd
from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

# data loading
ALL_DATA = []
HEADERS = []
CATEGORIES = []
CSV_FILE_NAME = 'CapstoneSpreadsheet - Sheet1.csv'

# Column indices
CATEGORY_COL_INDEX = 3  # Column D
NAME_COL_INDEX = 0  # Column A

# common keywords in column 1
COMMON_KEYWORDS = [
    'church', 'center', 'blue', 'mountain', 'services', 'umatilla', 'children',
    'club', 'society', 'child', 'ywca', 'counseling', 'hotline', 'catholic',
    'community', 'program', 'college', 'freewater', 'health', 'milton',
    'youth', 'care', 'charities', 'columbia', 'department', 'family',
    'home', 'national', 'wwcc', 'ymca'
]

# words to ignore
STOP_WORDS = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of', 'for',
              'with', 'by', 'as', 'from', 'it', 'its', 'that', 'this', 'we', 'i', 'you', 'he', 'she', 'they', 'our',
              'your', 'their', 'us', 'my', 'his', 'her', 'do', 'don', 'not', 'can', 'will', 'would', 'up', 'out',
              'down', 'be', 'been', 'have', 'has', 'had', 'all', 'any', 'some', 'no', 'so', 'get', 'just', 'more',
              'most', 'such', 'only', 'what', 'when', 'where', 'who', 'whom', 'which', 'how', 'one', 'two', 'three',
              'four', 'five', 'etc', 'name', 'details', 'number', 'director', 'address', 'website', 'function', 'email',
              'com', 'org', 'www', 'https', 'wa', 'st', 'ave', 'rd', 'dr', 'p', 's', 'n', 'w', 'e', 'rd', 'dr', 'blvd',
              "those", "through", "washington", "walla", "county", "oregon", "provides", "providing", "place",
              "provide", "main", "valley"}


def get_unique_categories(data):
    """Extracts unique category names for buttons."""
    categories = set()

    for row in data:
        if len(row) > CATEGORY_COL_INDEX and len(row) > NAME_COL_INDEX:
            col_d_value = row[CATEGORY_COL_INDEX].strip()
            col_a_value = row[NAME_COL_INDEX].strip()

            is_category_label_row = (col_d_value.startswith('Community Services- ') or col_d_value.startswith(
                'OTHER- ')) and \
                                    (col_a_value == '')

            if is_category_label_row:
                if col_d_value.startswith('Community Services- '):
                    category_name = col_d_value[len('Community Services- '):].strip()
                elif col_d_value.startswith('OTHER- '):
                    category_name = col_d_value[len('OTHER- '):].strip()
                else:
                    continue

                if category_name:
                    categories.add(category_name.upper())

    return sorted(list(categories))


def load_data():
    """Loads and preprocesses the CSV data, extracting headers and categories."""
    global ALL_DATA
    global HEADERS
    global CATEGORIES

    if not os.path.exists(CSV_FILE_NAME):
        print(f"Error: CSV file not found at {CSV_FILE_NAME}")
        return

    try:
        df = pd.read_csv(CSV_FILE_NAME, header=None, keep_default_na=False)
        ALL_DATA = df.astype(str).values.tolist()

        # Determine the header row by looking for the row starting with 'NAME'
        header_row_index = -1
        for i, row in enumerate(ALL_DATA):
            if len(row) > NAME_COL_INDEX and row[NAME_COL_INDEX].strip().upper() == 'NAME':
                header_row_index = i
                break

        if header_row_index != -1:
            HEADERS = [h.strip() for h in ALL_DATA[header_row_index]]
        else:
            print("Error: Could not find the header row starting with 'NAME'.")
            HEADERS = []

        CATEGORIES = get_unique_categories(ALL_DATA)

    except Exception as e:
        print(f"An error occurred while loading the CSV: {e}")
        ALL_DATA = []


def category_block_search(query, data):
    """Filters by the category block structure (used by the category buttons)."""
    if not query or not data:
        return []

    user_query = query.upper().strip()
    filtered_rows = []
    in_matching_block = False

    for row in data:
        col_d_value = row[CATEGORY_COL_INDEX].upper().strip() if len(row) > CATEGORY_COL_INDEX else ''
        col_a_value = row[NAME_COL_INDEX].upper().strip() if len(row) > NAME_COL_INDEX else ''

        # Detect a Category Label Row
        is_category_label_row = (col_d_value.startswith('COMMUNITY SERVICES-') or col_d_value.startswith(
            'OTHER-')) and col_a_value == ''

        if is_category_label_row:
            # New category block found. Check if it matches the query.
            if user_query in col_d_value:
                in_matching_block = True
            else:
                in_matching_block = False

        elif in_matching_block:
            # We are inside the matching category block.
            if col_a_value != '' and col_a_value != 'NAME' and col_a_value != 'DETAILS:':
                filtered_rows.append(row)

    return filtered_rows


def keyword_search(query, data):
    """
    Performs a full-text search for the query string across all columns
    of the resource rows.
    """
    if not query or not data:
        return []

    # Get only the resource rows for search
    resource_rows = []
    for row in data:
        if len(row) > NAME_COL_INDEX:
            col_a_value = row[NAME_COL_INDEX].strip().upper()
            if col_a_value != '' and col_a_value != 'NAME':
                resource_rows.append(row)

    # Normalize search query
    search_term = query.upper().strip()

    matching_rows = []

    for row in resource_rows:
        row_text = " ".join(row).upper()

        # Check for the search term as a whole word (using word boundaries \b)
        if re.search(r'\b' + re.escape(search_term) + r'\b', row_text):
            matching_rows.append(row)

    return matching_rows


def build_table_html(values, headers):
    """Generates the HTML string for the results table."""

    if not values:
        return '<div class="loading-message">No matching resources found for this category.</div>'

    html = '<table><thead><tr>'

    trimmed_headers = [h for h in headers if h.strip()]  # Filter out empty columns
    for header in trimmed_headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead><tbody>'

    for row in values:
        html += '<tr>'
        for cell_value in row[:len(trimmed_headers)]:
            value = cell_value.strip() if cell_value else ''
            html += f'<td>{value}</td>'
        html += '</tr>'

    html += '</tbody></table>'
    return html


def generate_category_buttons_html(categories):
    """Generates the HTML string for the category buttons."""
    html = ""
    for category in categories:
        category_url = url_for('results', query=category, search_type='category')
        html += f'<a href="{category_url}" class="category-button">{category}</a>'
    return html


def generate_keyword_list_html(keywords):
    """Generates the HTML string for the keyword list."""
    html = "<ul>"
    for keyword in keywords:
        html += f'<li>{keyword.capitalize()}</li>'
    html += "</ul>"
    return html


# Load data on startup
load_data()

# HTML for the main search page (searches by keyword in service name)
search_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resource Search</title>
    <style>
        body { font-family: 'Inter', sans-serif; padding: 20px; background-color: #f8f9fa; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 600px; 
            width: 100%;
        }
        h2 { color: #343a40; text-align: center; margin-bottom: 25px; }
        #search-form { display: flex; gap: 10px; margin-bottom: 20px; }
        #category-search { 
            padding: 12px; 
            border: 1px solid #ced4da; 
            border-radius: 8px; 
            flex-grow: 1;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        #filter-button {
            background-color: #007bff; 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: background-color 0.3s, transform 0.1s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            font-weight: 600;
        }
        #filter-button:hover { background-color: #0056b3; transform: translateY(-1px); }

        .section-title {
            text-align: center;
            color: #6c757d;
            margin: 20px 0 10px;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        .category-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            max-height: 200px; 
            overflow-y: auto; 
            padding: 5px;
        }
        .category-button {
            background-color: #f0f0f0;
            color: #343a40;
            padding: 8px 15px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
            font-weight: 500;
            text-decoration: none;
            display: inline-block;
            text-transform: uppercase;
            font-size: 0.85em;
        }
        .category-button:hover {
            background-color: #e2e6ea;
            border-color: #dae0e5;
        }
        .keyword-list-container {
            padding: 10px 0;
            text-align: center;
            font-size: 0.9em;
        }
        .keyword-list-container strong {
            display: block;
            margin-bottom: 5px;
        }
        .keyword-list-container ul {
            list-style: none;
            padding: 0;
            margin: 10px 0 0;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 8px;
            font-size: 0.9em;
        }
        .keyword-list-container li {
            background-color: #f8f9fa;
            color: #495057;
            padding: 4px 8px;
            border: 1px solid #e9ecef;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>Resource Search</h2>

        <form id="search-form" action="{{ url_for('results') }}" method="get">
            <input type="text" id="category-search" name="query" placeholder="Search by Keyword (e.g., CHURCH, COUNSELING, YWCA)" required>
            <input type="hidden" name="search_type" value="keyword">
            <button type="submit" id="filter-button">Search</button> 
        </form>

        <div class="keyword-list-container">
            <strong>Try searching for common terms like:</strong>
            {{ common_keywords_html | safe }}
        </div>

        <div class="section-title">-- OR BROWSE BY CATEGORY --</div>

        <div class="category-buttons">
            {{ category_buttons_html | safe }}
        </div>

    </div>
</body>
</html>
"""

# HTML for results page (/results)
results_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Results</title>
    <style>
        body { font-family: 'Inter', sans-serif; padding: 20px; background-color: #f8f9fa; }
        h2 { color: #343a40; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .back-link { display: block; margin-bottom: 20px; color: #007bff; text-decoration: none; font-weight: 500; }
        .back-link:hover { text-decoration: underline; }
        .loading-message {
            padding: 15px; 
            background-color: #fff3cd; 
            border: 1px solid #ffeeba; 
            color: #856404;
            border-radius: 8px;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 15px; 
            background-color: white; 
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.05);
        }
        th, td { 
            border: 1px solid #dee2e6; 
            padding: 12px; 
            text-align: left; 
            word-wrap: break-word;
        }
        th { 
            background-color: #e9ecef; 
            color: #495057; 
            text-transform: uppercase; 
            font-size: 0.85em; 
            font-weight: 600;
        }
        .error-message {
            background-color:#f8d7da; 
            color:#721c24; 
            border-color:#f5c6cb;
            padding: 15px;
            border: 1px solid;
            border-radius: 8px;
        }
    </style>
</head>
<body>

    <a href="/" class="back-link">&larr; Back to Search</a>
    <h2 id="results-title">{{ title }}</h2>

    <div id="data-container">
        {{ table_html | safe }} 
    </div>

</body>
</html>
"""


# Flask Routes (pages)
@app.route('/')
def home():
    """Renders the search form with dynamic category buttons and keyword list."""
    button_html = generate_category_buttons_html(CATEGORIES)
    keyword_html = generate_keyword_list_html(COMMON_KEYWORDS)

    return render_template_string(
        search_page_template,
        category_buttons_html=button_html,
        common_keywords_html=keyword_html
    )


@app.route('/results')
def results():
    """Handles both keyword and category searches."""
    query = request.args.get('query', '').upper().strip()
    search_type = request.args.get('search_type', '').lower()

    # In case csv was not cpnnected properly
    if not ALL_DATA or not HEADERS:
        title = "Data Error"
        table_html = f'<div class="error-message">Error: Could not load data from {CSV_FILE_NAME}. Please ensure the file is present.</div>'
        return render_template_string(results_page_template, title=title, table_html=table_html)

    # Handle empty query
    if not query:
        title = "Please Enter a Search Term"
        table_html = """<div class="loading-message">
                            Please use the search bar for a keyword or a button to select a category.
                        </div>"""
        return render_template_string(results_page_template, title=title, table_html=table_html)

    # Determine search method
    if search_type == 'category':
        # Using category buttons
        filtered_data = category_block_search(query, ALL_DATA)
        search_description = "Category Block Search"
    else:
        # Using main search bar
        filtered_data = keyword_search(query, ALL_DATA)
        search_description = "Keyword Search"

    # Generate results
    title = f'Results for {search_description}: "{query}"'

    if not filtered_data:
        table_html = f"""<div class="error-message">
                           No resources found matching "{query}".
                        </div>"""
    else:
        table_html = build_table_html(filtered_data, HEADERS)

    # Render the results page
    return render_template_string(results_page_template, title=title, table_html=table_html)


if __name__ == '__main__':
    app.run(debug=True)