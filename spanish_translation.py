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

# Spanish equivalents for keywords
COMMON_KEYWORDS_ES = [
    'iglesia', 'centro', 'azul', 'montaña', 'servicios', 'umatilla', 'niños',
    'club', 'sociedad', 'niño', 'ywca', 'consejería', 'línea directa', 'católico',
    'comunidad', 'programa', 'colegio', 'freewater', 'salud', 'milton',
    'juventud', 'cuidado', 'caridades', 'columbia', 'departamento', 'familia',
    'hogar', 'nacional', 'wwcc', 'ymca'
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

# --- (All helper functions from your original code remain here, unchanged) ---
# get_unique_categories(), load_data(), is_valid_resource(), get_resource_rows_with_index(),
# category_block_search(), keyword_search(), build_buttons_html(), generate_category_buttons_html(),
# generate_keyword_list_html()
# -------------------------------------------------------------

# Load data on startup
load_data()

# --- HTML Templates with Spanish Integration (only search page active) ---
search_page_template = """
<!DOCTYPE html>
<html lang="{{ lang }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ 'Resource Search' if lang=='en' else 'Búsqueda de Recursos' }}</title>
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
        #language-select {
            position: absolute;
            top: 15px;
            right: 15px;
            padding: 5px 10px;
            border-radius: 6px;
            border: 1px solid #ced4da;
        }
    </style>
</head>
<body>
    <select id="language-select" onchange="changeLang(this.value)">
        <option value="en" {% if lang=='en' %}selected{% endif %}>English</option>
        <option value="es" {% if lang=='es' %}selected{% endif %}>Español</option>
    </select>

    <div class="card">
        <h2>{{ 'Resource Search' if lang=='en' else 'Búsqueda de Recursos' }}</h2>

        <form id="search-form" action="{{ url_for('results') }}" method="get">
            <input type="text" id="category-search" name="query" placeholder="{{ 'Search by Keyword (e.g., CHURCH, COUNSELING, YWCA)' if lang=='en' else 'Buscar por palabra clave (ej., IGLESIA, CONSEJERÍA, YWCA)' }}" required>
            <input type="hidden" name="search_type" value="keyword">
            <input type="hidden" name="lang" value="{{ lang }}">
            <button type="submit" id="filter-button">{{ 'Search' if lang=='en' else 'Buscar' }}</button> 
        </form>

        <div class="keyword-list-container">
            <strong>{{ 'Try searching for common terms like:' if lang=='en' else 'Intenta buscar términos comunes como:' }}</strong>
            {% if lang=='en' %}
                {{ common_keywords_html | safe }}
            {% else %}
                {{ common_keywords_html_es | safe }}
            {% endif %}
        </div>

        <div class="section-title">{{ '-- OR BROWSE BY CATEGORY --' if lang=='en' else '-- O EXPLORA POR CATEGORÍA --' }}</div>

        <div class="category-buttons">
            {{ category_buttons_html | safe }}
        </div>

    </div>

<script>
function changeLang(lang) {
    const url = new URL(window.location.href);
    url.searchParams.set('lang', lang);
    window.location.href = url.toString();
}
</script>
</body>
</html>
"""

# --- (results_page_template and detail_page_template remain unchanged) ---
# They can be fully translated later.

# -------------------------------------------------------------
# Flask Routes
@app.route('/')
def home():
    lang = request.args.get('lang', 'en')
    button_html = generate_category_buttons_html(CATEGORIES)
    keyword_html = generate_keyword_list_html(COMMON_KEYWORDS)
    keyword_html_es = generate_keyword_list_html(COMMON_KEYWORDS_ES)

    return render_template_string(
        search_page_template,
        category_buttons_html=button_html,
        common_keywords_html=keyword_html,
        common_keywords_html_es=keyword_html_es,
        lang=lang
    )

# --- results() and resource_detail() remain unchanged ---
# --- main block ---
if __name__ == '__main__':
    load_data()
    app.run(debug=True)
