import os
import re

import pandas as pd
from flask import Flask, render_template_string, request, url_for

app = Flask(__name__)

# data loading
ALL_DATA = []
HEADERS = []
CATEGORIES = []
# NOTE: The actual data file must be in the same directory as this script.
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


# --- Helper function for filtering out "closed" resources ---
def is_valid_resource(row):
    """Checks if the row is a valid resource and does not contain 'closed' in the name."""
    if len(row) > NAME_COL_INDEX:
        col_a_value = row[NAME_COL_INDEX].strip()
        if col_a_value != '' and col_a_value.upper() != 'NAME':
            # Check for "closed" (case-insensitive) in the name column
            if "closed" not in col_a_value.lower():
                return True
    return False


# --- Map Resource Rows to their Original Index ---
def get_resource_rows_with_index(data):
    """
    Returns a list of tuples: (original_row_index, row_data)
    Includes only rows that are actual resources, excluding those marked 'closed'.
    """
    resource_map = []
    for i, row in enumerate(data):
        if is_valid_resource(row):
            resource_map.append((i, row))
    return resource_map


# ----------------------------------------------------------------

def category_block_search(query, data):
    """
    Filters by the category block structure, returning (original_row_index, row_data),
    and excludes resources containing 'closed'.
    """
    if not query or not data:
        return []

    user_query = query.upper().strip()
    filtered_rows_with_index = []
    in_matching_block = False

    for i, row in enumerate(data):
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
            # We are inside the matching category block AND it must be a valid resource
            if is_valid_resource(row):
                # Return the index of the row and the row data
                filtered_rows_with_index.append((i, row))

    return filtered_rows_with_index


def keyword_search(query, data):
    """
    Performs a full-text search, returning (original_row_index, row_data),
    and excludes resources containing 'closed'.
    """
    if not query or not data:
        return []

    # Get only the valid resource rows for search with their index
    resource_rows_map = get_resource_rows_with_index(data)

    # Normalize search query
    search_term = query.upper().strip()

    matching_rows_with_index = []

    for index, row in resource_rows_map:
        row_text = " ".join(row).upper()

        # Check for the search term as a whole word (using word boundaries \b)
        if re.search(r'\b' + re.escape(search_term) + r'\b', row_text):
            # is_valid_resource check is already done in get_resource_rows_with_index
            matching_rows_with_index.append((index, row))

    return matching_rows_with_index


# --- Function: Generates buttons instead of a table ---
def build_buttons_html(values_with_index):
    """Generates the HTML string for a uniform grid of clickable service buttons."""

    if not values_with_index:
        return '<div class="loading-message">No matching resources found.</div>'

    html = '<div class="service-buttons-container">'

    for row_index, row in values_with_index:
        # Get the service name from the NAME_COL_INDEX
        service_name = row[NAME_COL_INDEX].strip() if len(row) > NAME_COL_INDEX else 'Untitled Service'

        # is_valid_resource check is already done in the search functions
        if service_name:
            detail_url = url_for('resource_detail', row_index=row_index)
            # Use the service-button class for uniform styling
            html += f'<a href="{detail_url}" class="service-button">{service_name}</a>'

    html += '</div>'
    return html


# -------------------------------------------------------------

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

# HTML for the main search page (unchanged)
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

# HTML for results page (unchanged)
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
        .error-message {
            background-color:#f8d7da; 
            color:#721c24; 
            border-color:#f5c6cb;
            padding: 15px;
            border: 1px solid;
            border-radius: 8px;
        }

        /* Styling for the new button layout */
        .service-buttons-container {
            display: grid;
            /* Creates 3 columns of equal size, adjusts for smaller screens */
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
            gap: 15px;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0,0,0,0.05);
        }
        .service-button {
            /* These properties enforce uniform size */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 80px; /* Fixed height */
            text-align: center;

            /* Styling */
            background-color: #007bff;
            color: white;
            padding: 15px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.1s, box-shadow 0.3s;
            font-weight: 600;
            text-decoration: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);

            /* Text wrapping for long names */
            word-break: break-word;
        }
        .service-button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 6px 10px rgba(0,0,0,0.15);
        }
    </style>
</head>
<body>

    <a href="/" class="back-link">&larr; Back to Search</a>
    <h2 id="results-title">{{ title }}</h2>

    <div id="data-container">
        {{ buttons_html | safe }} 
    </div>

</body>
</html>
"""

# HTML for resource detail page (unchanged)
detail_page_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ resource_name }} Details</title>
    <style>
        body { font-family: 'Inter', sans-serif; padding: 20px; background-color: #f8f9fa; }
        .detail-card {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 800px;
            margin: 0 auto;
        }
        h2 { color: #007bff; text-align: center; margin-bottom: 30px; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #6c757d; text-decoration: none; font-weight: 500; }
        .back-link:hover { text-decoration: underline; }
        .detail-item {
            display: flex;
            margin-bottom: 15px;
            padding: 10px 0;
            border-bottom: 1px dotted #e9ecef;
        }
        .detail-item:last-child {
            border-bottom: none;
        }
        .detail-header {
            font-weight: 600;
            color: #343a40;
            flex: 0 0 180px; /* Fixed width for the label */
            text-transform: uppercase;
            font-size: 0.9em;
        }
        .detail-value {
            color: #495057;
            flex-grow: 1;
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

    <div class="detail-card">
        <h2>{{ resource_name }}</h2>
        {% for header, value in details %}
            <div class="detail-item">
                <span class="detail-header">{{ header }}:</span>
                <span class="detail-value">{{ value }}</span>
            </div>
        {% endfor %}

        {% if not details %}
            <div class="error-message">Resource details could not be loaded.</div>
        {% endif %}
    </div>

</body>
</html>
"""


# -------------------------------------------------------------


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

    if not ALL_DATA or not HEADERS:
        title = "Data Error"
        buttons_html = f'<div class="error-message">Error: Could not load data from {CSV_FILE_NAME}. Please ensure the file is present.</div>'
        return render_template_string(results_page_template, title=title, buttons_html=buttons_html)

    if not query:
        title = "Please Enter a Search Term"
        buttons_html = """<div class="loading-message">
                            Please use the search bar for a keyword or a button to select a category.
                        </div>"""
        return render_template_string(results_page_template, title=title, buttons_html=buttons_html)

    # Determine search method
    if search_type == 'category':
        filtered_data = category_block_search(query, ALL_DATA)
        search_description = "Category Block Search"
    else:
        filtered_data = keyword_search(query, ALL_DATA)
        search_description = "Keyword Search"

    # Generate results
    title = f'Results for {search_description}: "{query}"'

    if not filtered_data:
        buttons_html = f"""<div class="error-message">
                           No resources found matching "{query}" or all matching resources are marked 'closed'.
                        </div>"""
    else:
        # Use the function to generate buttons
        buttons_html = build_buttons_html(filtered_data)

    # Render the results page
    return render_template_string(results_page_template, title=title, buttons_html=buttons_html)


@app.route('/resource/<int:row_index>')
def resource_detail(row_index):
    """
    Renders a page with all details for a specific resource, omitting empty fields
    and cleaning up header colons.
    """
    if not ALL_DATA or not HEADERS:
        return render_template_string(
            detail_page_template,
            resource_name="Data Error",
            details=[],
            table_html=f'<div class="error-message">Error: Could not load data from {CSV_FILE_NAME}.</div>'
        )

    try:
        resource_row = ALL_DATA[row_index]
        details = []

        # Iterate through headers and corresponding row values
        for i, header in enumerate(HEADERS):
            # 1. Check if the header exists and isn't empty
            if i < len(resource_row) and header.strip():

                # --- SOLUTION: Clean the header string ---
                # Remove any trailing colons from the CSV header before passing it to the template.
                clean_header = header.strip().rstrip(':')

                value = resource_row[i].strip()

                # 2. Check if the value is NOT empty/whitespace
                if value:
                    details.append((clean_header, value))

        # The resource name is in the NAME_COL_INDEX
        resource_name = resource_row[NAME_COL_INDEX].strip() if len(
            resource_row) > NAME_COL_INDEX else "Unknown Resource"

        return render_template_string(
            detail_page_template,
            resource_name=resource_name,
            details=details
        )

    except IndexError:
        return render_template_string(
            detail_page_template,
            resource_name="Error",
            details=[("Status", "Resource not found (invalid index).")]
        )


if __name__ == '__main__':
    # Ensure all data is reloaded before running the app
    load_data()
    app.run(debug=True)