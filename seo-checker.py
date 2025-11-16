import requests
from bs4 import BeautifulSoup
import json
import os 
import sys 
from datetime import datetime
# --- NEW IMPORT FOR PDF GENERATION ---
from fpdf import FPDF # Requires: pip install fpdf2

# --- CONFIGURATION CONSTANTS FOR QUALITY ANALYSIS ---
MAX_TITLE_CHARS = 60    # Recommended maximum character length for Google Title
MAX_DESC_CHARS = 160    # Recommended maximum character length for Google Meta Description
MIN_DESC_CHARS = 70     # Recommended minimum character length for a good description

# --- CONFIGURATION CONSTANTS FOR SCORING ---
MAX_SCORE = 100 # The total possible score
# Weights for critical factors (must sum to <= 100)
SCORE_WEIGHTS = {
    'Canonical_Present': 20,       # CRITICAL: Prevents duplication
    'Robots_Optimal': 10,          # CRITICAL: Ensures indexing
    'Title_Optimal': 15,           # Quality check (length, presence)
    'Description_Optimal': 15,     # Quality check (length, presence)
    'Hreflang_Present': 5,         # Internationalization
    'OpenGraph_Present': 5,        # Social media sharing
    'TwitterCard_Present': 5,      # Social media sharing
    'Schema_Valid': 15,            # Structured data
    'Image_Alt_Optimal': 10,       # Accessibility/Image SEO
}

# Thresholds for Letter Grades (Score % to Grade)
GRADING_SCALE = {
    95: 'A+',
    90: 'A',
    85: 'A-',
    80: 'B+',
    75: 'B',
    70: 'B-',
    60: 'C',
    50: 'D',
    0: 'F', # Anything below 50
}


# --- SCHEMA REQUIRED PROPERTY DEFINITIONS (Simplified Google set) ---
# Maps schema type to a list of properties Google requires for Rich Results
SCHEMA_REQUIREMENTS = {
    "Article": ["headline", "image", "datePublished"],
    "TechArticle": ["headline", "image", "datePublished"],
    "NewsArticle": ["headline", "image", "datePublished", "dateModified"],
    "Product": ["name", "image", "description", "offers"],
    "Recipe": ["name", "image", "description", "aggregateRating", "recipeIngredient"],
    "FAQPage": ["mainEntity"]
}

# --- EXHAUSTIVE TAG DEFINITIONS (New for v2) ---

# Link relations for icons, PWA, and device features
ICON_RELS = ['icon', 'apple-touch-icon', 'apple-touch-icon-precomposed', 'shortcut icon', 'fluid-icon', 'mask-icon']
PWA_MOBILE_RELS = ['manifest', 'apple-touch-startup-image']
PERFORMANCE_RELS = ['dns-prefetch', 'preconnect', 'preload', 'prefetch', 'prerender', 'modulepreload']
DOCUMENT_RELS = ['prev', 'next', 'license', 'author', 'search', 'help', 'pingback', 'privacy-policy']

# Meta tag names for PWA/Mobile/Microsoft/Legacy
PWA_MOBILE_NAMES = [
    'apple-mobile-web-app-capable', 'apple-mobile-web-app-status-bar-style', 'apple-mobile-web-app-title',
    'msapplication-TileColor', 'msapplication-TileImage', 'msapplication-config', 'application-name',
    'theme-color', 'viewport'
]

# All Http-Equiv directives
ALL_HTTP_EQUIVS = [
    'content-type', 'content-language', 'refresh', 'page-enter', 'page-exit', 'x-ua-compatible', 'default-style'
]


# ----------------------------------------------------------------------
# 1. CORE AUDIT LOGIC (Runs the full check on HTML content string)
# ----------------------------------------------------------------------

# --- OUTPUT FORMATTING FUNCTIONS (Modified to write to buffer list) ---

def format_audit_category(title, data, buffer_list):
    """Formats a general category and appends to the buffer list."""
    buffer_list.append(f"\n--- {title} ({len(data) if isinstance(data, dict) else len(data)}) ---")
    if data:
        if isinstance(data, dict):
            for key, value in data.items(): buffer_list.append(f"  > {key:<35}: {value}")
        elif isinstance(data, list):
            for item in data: buffer_list.append(f"  > {item}")
    else:
        buffer_list.append("  (None Found)")
    
def format_link_rel_category(title, data, buffer_list):
    """Formats a link rel category and appends to the buffer list."""
    buffer_list.append(f"\n--- {title} ({len(data)}) ---")
    if data:
        for key, value in data.items(): 
            if isinstance(value, dict) and 'href' in value: # Handle icon links
                buffer_list.append(f"  > {key:<25}: {value['href']} (Sizes: {value['sizes'] if 'sizes' in value else 'N/A'})")
            else:
                buffer_list.append(f"  > {key:<25}: {value}")
    else:
        buffer_list.append("  (None Found)")

def perform_metadata_audit(html_content, source_name):
    """
    Parses HTML content, extracts all metadata, generates reports, and returns 
    the complete report as a single string.
    """
    output_buffer = [] # The list that will hold all report lines
    
    output_buffer.append(f"\n--- Running Audit for: {source_name} ---")
    output_buffer.append(f"--- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    
    try:
        # Comprehensive results dictionary structure
        results = {
            'ESSENTIAL_HTML_TAGS': {},
            'CORE_SEO_TAGS': {'Canonical': '❌ MISSING', 'Hreflang_Tags': [], 'Robots': '❌ MISSING', 'Description': '❌ MISSING'},
            'SOCIAL_MEDIA_TAGS': {'OPEN_GRAPH': {}, 'TWITTER_CARD': {}},
            'PWA_MOBILE_TAGS': {},
            'TECHNICAL_BROWSER_TAGS': {},
            'CRITICAL_LINK_TAGS': {},
            'ALL_OTHER_META_TAGS': {}, 
            'JSON_LD_STRUCTURED_DATA': []
        }
        soup = BeautifulSoup(html_content, 'html.parser')
        
    except Exception as e:
        output_buffer.append(f"❌ ERROR: An unexpected error occurred during parsing. ({e})\n")
        # Print to console immediately
        print("".join(output_buffer))
        return None

    # --- CORE EXTRACTION LOGIC (Same as before) ---
    title_tag = soup.find('title')
    results['ESSENTIAL_HTML_TAGS']['<title>'] = title_tag.string.strip() if title_tag and title_tag.string else '❌ MISSING'
    charset_tag = soup.find('meta', charset=True) or soup.find('meta', attrs={'http-equiv': 'Content-Type'})
    results['ESSENTIAL_HTML_TAGS']['<meta charset>'] = charset_tag.get('charset', charset_tag.get('content')) if charset_tag else '❌ MISSING'

    # 1. LINK TAG EXTRACTION
    for tag in soup.find_all('link'):
        rel = tag.get('rel')
        if not rel: continue

        if isinstance(rel, list):
            rel = ' '.join(rel).lower()
        else:
            rel = rel.lower()
        
        href = tag.get('href', 'N/A')
        tag_key = f"rel='{rel}'"
        
        if rel == 'canonical':
            results['CORE_SEO_TAGS']['Canonical'] = href
        elif 'alternate' in rel and tag.get('hreflang'):
             results['CORE_SEO_TAGS']['Hreflang_Tags'].append({'hreflang': tag['hreflang'], 'href': href})
        
        elif any(r in rel.split() for r in PWA_MOBILE_RELS):
             results['PWA_MOBILE_TAGS'][tag_key] = href
        
        elif any(r in rel.split() for r in PERFORMANCE_RELS):
             results['TECHNICAL_BROWSER_TAGS'][tag_key] = f"{href} (as='{tag.get('as', 'N/A')}', type='{tag.get('type', 'N/A')}')"
        
        elif any(r in rel.split() for r in ICON_RELS):
            results['CRITICAL_LINK_TAGS'][tag_key] = {'href': href, 'sizes': tag.get('sizes', 'N/A'), 'type': tag.get('type', 'N/A')}
        
        elif rel != 'alternate':
            results['CRITICAL_LINK_TAGS'][tag_key] = href
            
    # 2. META TAG EXTRACTION
    for tag in soup.find_all('meta'):
        if tag.get('charset'): continue
        name = tag.get('name', '').lower()
        prop = tag.get('property', '').lower()
        http_equiv = tag.get('http-equiv', '').lower()
        content = tag.get('content', '')
        
        if prop.startswith('og:'):
            results['SOCIAL_MEDIA_TAGS']['OPEN_GRAPH'][prop] = content
        elif name.startswith('twitter:'):
            results['SOCIAL_MEDIA_TAGS']['TWITTER_CARD'][name] = content
        elif name == 'description':
            results['CORE_SEO_TAGS']['Description'] = content
        elif name == 'robots':
             results['CORE_SEO_TAGS']['Robots'] = content
        elif name == 'keywords':
             results['CORE_SEO_TAGS']['Keywords'] = content
        elif name in PWA_MOBILE_NAMES:
            results['PWA_MOBILE_TAGS'][name] = content
        elif http_equiv in ALL_HTTP_EQUIVS:
            results['TECHNICAL_BROWSER_TAGS'][f"http-equiv: {http_equiv}"] = content
        elif name or prop:
            key = name if name else prop
            results['ALL_OTHER_META_TAGS'][key] = content

    # 3. JSON-LD STRUCTURED DATA
    for i, script in enumerate(soup.find_all('script', type='application/ld+json'), 1):
        try:
            json_string = script.string.strip()
            json_content = json.loads(json_string)
            results['JSON_LD_STRUCTURED_DATA'].append(
                {'Script_ID': f"#{i}", 
                 'Schema_Type': json_content.get('@type', 'Unknown Type'), 
                 'Content_Snippet': json_string.replace('\n', '')[:100] + '...',
                 'Full_Content_Object': json_content 
                }
            )
        except:
             results['JSON_LD_STRUCTURED_DATA'].append({'Script_ID': f"#{i}", 'Schema_Type': '⚠️ PARSE ERROR', 'Content_Snippet': 'Error parsing JSON', 'Full_Content_Object': None})

    # 4. Generate Audit Report to Buffer (This section is unchanged)
    output_buffer.append("="*70)
    output_buffer.append("           C O M P R E H E N S I V E   M E T A D A T A   A U D I T")
    output_buffer.append("="*70)
    format_audit_category("1. ESSENTIAL HTML TAGS (Title, Charset)", results['ESSENTIAL_HTML_TAGS'], output_buffer)
    
    output_buffer.append("\n--- 2. CORE SEO TAGS ---")
    output_buffer.append(f"  > {'Canonical URL':<35}: {results['CORE_SEO_TAGS']['Canonical']}")
    output_buffer.append(f"  > {'Meta Description':<35}: {results['CORE_SEO_TAGS']['Description']}")
    output_buffer.append(f"  > {'Meta Robots':<35}: {results['CORE_SEO_TAGS']['Robots']}")
    if 'Keywords' in results['CORE_SEO_TAGS']:
        output_buffer.append(f"  > {'Meta Keywords (Legacy)':<35}: {results['CORE_SEO_TAGS']['Keywords']}")
    
    output_buffer.append("\n--- 3. INTERNATIONALIZATION (Hreflang) ---")
    output_buffer.append(f"  Hreflang Tags Found ({len(results['CORE_SEO_TAGS']['Hreflang_Tags'])}):")
    if not results['CORE_SEO_TAGS']['Hreflang_Tags']: output_buffer.append("    (None Found)")
    for link in results['CORE_SEO_TAGS']['Hreflang_Tags']: output_buffer.append(f"    - {link['hreflang']:<5}: {link['href']}")

    format_audit_category("4. SOCIAL MEDIA TAGS - OPEN GRAPH (Facebook, LinkedIn)", results['SOCIAL_MEDIA_TAGS']['OPEN_GRAPH'], output_buffer)
    format_audit_category("4. SOCIAL MEDIA TAGS - TWITTER CARD (X)", results['SOCIAL_MEDIA_TAGS']['TWITTER_CARD'], output_buffer)
    
    format_audit_category("\n5. PWA, MOBILE, AND DEVICE CONFIGURATION - Meta Tags", results['PWA_MOBILE_TAGS'], output_buffer)
    pwa_links = {k: v for k, v in results['CRITICAL_LINK_TAGS'].items() if 'manifest' in k or 'startup-image' in k}
    format_link_rel_category("5. PWA, MOBILE, AND DEVICE CONFIGURATION - Link Tags (Manifest, Startup Image)", pwa_links, output_buffer)
    
    perf_hints = {k: v for k, v in results['TECHNICAL_BROWSER_TAGS'].items() if not k.startswith('http-equiv')}
    http_equivs = {k: v for k, v in results['TECHNICAL_BROWSER_TAGS'].items() if k.startswith('http-equiv')}
    format_link_rel_category("\n6. PERFORMANCE HINTS & HTTP-EQUIVS - Performance Link Hints", perf_hints, output_buffer)
    format_audit_category("6. PERFORMANCE HINTS & HTTP-EQUIVS - HTTP-EQUIV Meta Tags", http_equivs, output_buffer)

    other_links = {k: v for k, v in results['CRITICAL_LINK_TAGS'].items() if 'manifest' not in k and 'startup-image' not in k}
    format_link_rel_category("\n7. OTHER CRITICAL LINK RELATIONS (Icons, Stylesheet, Next/Prev)", other_links, output_buffer)

    format_audit_category("8. ALL OTHER/CUSTOM META TAGS", results['ALL_OTHER_META_TAGS'], output_buffer)
    
    output_buffer.append("\n--- 9. JSON-LD STRUCTURED DATA ---")
    if results['JSON_LD_STRUCTURED_DATA']:
        output_buffer.append(f"✅ Found {len(results['JSON_LD_STRUCTURED_DATA'])} JSON-LD Script(s).")
        for item in results['JSON_LD_STRUCTURED_DATA']:
            output_buffer.append(f"  {item['Script_ID']} [Type: {item['Schema_Type']}]")
            output_buffer.append(f"    Snippet: {item['Content_Snippet']}")
    else:
        output_buffer.append("❌ No JSON-LD Structured Data Found.")
    output_buffer.append("="*70)

    # 5. Run Quality Analysis
    quality_checks = analyze_tag_quality(results, soup)
    
    # --- NEW SCORING FEATURE INTEGRATION ---
    score_percent, letter_grade = generate_overall_score_and_grade(results, quality_checks)
    
    output_buffer.append("\n\n" + "#"*70)
    output_buffer.append(f"       🌟 O V E R A L L   S E O   S C O R E   &   G R A D E 🌟")
    output_buffer.append("#"*70)
    output_buffer.append(f"          Current Score: {score_percent}%")
    output_buffer.append(f"          Final Grade: **{letter_grade}**")
    output_buffer.append("#"*70)

    # 6. Generate the detailed remediation report
    output_buffer.extend(generate_remediation_report(results, quality_checks))
    
    # Print the full report to the console before returning
    print("\n".join(output_buffer))
    
    # Return the full report string
    return "\n".join(output_buffer)

# ----------------------------------------------------------------------
# 2. HELPER FUNCTIONS (Quality Analysis and Remediation)
# ----------------------------------------------------------------------

def analyze_tag_quality(results, soup):
    """Analyzes the content quality, length, and technical elements."""
    quality_checks = {
        'Title': {'Status': '❌ MISSING', 'Length': 0, 'Recommendation': ''},
        'Description': {'Status': '❌ MISSING', 'Length': 0, 'Recommendation': ''},
        'Image_Alt_Text': {'Total': 0, 'Missing': 0, 'Recommendation': ''},
        'Render_Blocking_JS': [],
        'Schema_Validation': []
    }
    
    # Title Quality Check
    title = results['ESSENTIAL_HTML_TAGS'].get('<title>', '')
    if title and title != '❌ MISSING':
        length = len(title)
        quality_checks['Title']['Length'] = length
        if length > MAX_TITLE_CHARS:
            quality_checks['Title']['Status'] = '⚠️ TOO LONG'
            quality_checks['Title']['Recommendation'] = f'Title is {length - MAX_TITLE_CHARS} characters over the recommended limit. It may be truncated in search results.'
        else:
            quality_checks['Title']['Status'] = '✅ OPTIMAL'
            quality_checks['Title']['Recommendation'] = f'Title length is good ({length}/{MAX_TITLE_CHARS} chars).'

    # Meta Description Quality Check
    description = results['CORE_SEO_TAGS'].get('Description', '')
    if description and description != '❌ MISSING':
        length = len(description)
        quality_checks['Description']['Length'] = length
        if length > MAX_DESC_CHARS:
            quality_checks['Description']['Status'] = '⚠️ TOO LONG'
            quality_checks['Description']['Recommendation'] = f'Description is {length - MAX_DESC_CHARS} characters over the recommended limit. It will likely be truncated.'
        elif length < MIN_DESC_CHARS:
            quality_checks['Description']['Status'] = '⚠️ TOO SHORT'
            quality_checks['Description']['Recommendation'] = f'Description is too short. Try to elaborate to use the full {MIN_DESC_CHARS} characters for better CTR.'
        else:
            quality_checks['Description']['Status'] = '✅ OPTIMAL'
            quality_checks['Description']['Recommendation'] = f'Description length is good ({length}/{MAX_DESC_CHARS} chars).'
    
    # Image Alt Text Check (UX/Accessibility)
    all_images = soup.find_all('img')
    missing_alt = sum(1 for img in all_images if not img.get('alt'))
    quality_checks['Image_Alt_Text']['Total'] = len(all_images)
    quality_checks['Image_Alt_Text']['Missing'] = missing_alt
    if len(all_images) > 0:
        if missing_alt > 0:
            quality_checks['Image_Alt_Text']['Recommendation'] = f'❌ {missing_alt} out of {len(all_images)} images are missing "alt" text. Fix this for accessibility and Image SEO.'
        else:
            quality_checks['Image_Alt_Text']['Recommendation'] = '✅ All images have "alt" text.'
    else:
        quality_checks['Image_Alt_Text']['Recommendation'] = 'No <img> tags found.'

    # Render-Blocking JS Check (Performance)
    for script in soup.find_all('script'):
        src = script.get('src')
        if src and not script.get('async') and not script.get('defer') and not src.startswith('//cdnjs'):
            quality_checks['Render_Blocking_JS'].append(f'JS: {src[:50]}...')
            
    if quality_checks['Render_Blocking_JS']:
        quality_checks['Render_Blocking_JS'].insert(0, '⚠️ Potential render-blocking script(s) found. Consider adding `defer` or `async` to these tags.')
    else:
        quality_checks['Render_Blocking_JS'] = ['✅ No obvious render-blocking JavaScript files detected.']

    # Schema Validation Check
    for item in results['JSON_LD_STRUCTURED_DATA']:
        schema_type = item['Schema_Type'].split()[0].replace('⚠️', '') 
        full_json_content = item.get('Full_Content_Object')

        if not full_json_content:
             quality_checks['Schema_Validation'].append(f'❌ {schema_type}: Cannot validate, original JSON was malformed or could not be loaded.')
             continue

        if schema_type in SCHEMA_REQUIREMENTS:
            try:
                required_props = SCHEMA_REQUIREMENTS[schema_type]
                missing_props = [
                    prop for prop in required_props 
                    if prop not in full_json_content or not full_json_content.get(prop)
                ]
                
                if not missing_props:
                    quality_checks['Schema_Validation'].append(f'✅ {schema_type}: All required properties are present.')
                else:
                    quality_checks['Schema_Validation'].append(f'⚠️ {schema_type}: Missing required properties: {", ".join(missing_props)}.')
            except Exception as e:
                quality_checks['Schema_Validation'].append(f'❌ {schema_type}: Validation failed unexpectedly. ({e})')
        else:
            quality_checks['Schema_Validation'].append(f'ℹ️ {schema_type}: Unknown schema type or no specific Google requirements.')

    return quality_checks

def generate_overall_score_and_grade(results, quality_checks):
    """Calculates the overall SEO score and converts it to a letter grade."""
    current_score = 0
    
    # 1. Canonical Link (20 Points)
    if results['CORE_SEO_TAGS']['Canonical'] != '❌ MISSING':
        current_score += SCORE_WEIGHTS['Canonical_Present']
    
    # 2. Robots Tag (10 Points)
    robots = results['CORE_SEO_TAGS']['Robots'].lower()
    if robots != '❌ MISSING' and 'noindex' not in robots:
        current_score += SCORE_WEIGHTS['Robots_Optimal']
        
    # 3. Title Quality (15 Points)
    if quality_checks['Title']['Status'] == '✅ OPTIMAL':
        current_score += SCORE_WEIGHTS['Title_Optimal']
    elif quality_checks['Title']['Status'] in ['⚠️ TOO LONG', '⚠️ TOO SHORT']:
        # Assign partial credit if present but not optimal (e.g., half points)
        current_score += SCORE_WEIGHTS['Title_Optimal'] * 0.5 
        
    # 4. Description Quality (15 Points)
    if quality_checks['Description']['Status'] == '✅ OPTIMAL':
        current_score += SCORE_WEIGHTS['Description_Optimal']
    elif quality_checks['Description']['Status'] in ['⚠️ TOO LONG', '⚠️ TOO SHORT']:
        current_score += SCORE_WEIGHTS['Description_Optimal'] * 0.5 
        
    # 5. Hreflang Tags (5 Points)
    if results['CORE_SEO_TAGS']['Hreflang_Tags']:
        current_score += SCORE_WEIGHTS['Hreflang_Present']
        
    # 6. Open Graph Tags (5 Points)
    if results['SOCIAL_MEDIA_TAGS']['OPEN_GRAPH']:
        current_score += SCORE_WEIGHTS['OpenGraph_Present']
        
    # 7. Twitter Card Tags (5 Points)
    if results['SOCIAL_MEDIA_TAGS']['TWITTER_CARD']:
        current_score += SCORE_WEIGHTS['TwitterCard_Present']

    # 8. Schema Validation (15 Points)
    valid_schemas = sum(1 for status in quality_checks['Schema_Validation'] if status.startswith('✅'))
    total_schemas = len(results['JSON_LD_STRUCTURED_DATA'])
    if total_schemas > 0:
        # Score proportional to the number of valid schemas
        schema_points = SCORE_WEIGHTS['Schema_Valid'] * (valid_schemas / total_schemas)
        current_score += schema_points

    # 9. Image Alt Text (10 Points)
    total_images = quality_checks['Image_Alt_Text']['Total']
    missing_alt = quality_checks['Image_Alt_Text']['Missing']
    if total_images > 0:
        # Score proportional to the number of images with alt text
        alt_points = SCORE_WEIGHTS['Image_Alt_Optimal'] * (1 - (missing_alt / total_images))
        current_score += alt_points
    # If no images, we don't penalize, so we assume optimal (10 points)
    elif total_images == 0:
        current_score += SCORE_WEIGHTS['Image_Alt_Optimal']
        
    # Calculate the final percentage and round the score
    percentage = round((current_score / MAX_SCORE) * 100)

    # Determine the letter grade
    final_grade = 'N/A'
    # Iterate through the scale keys in descending order
    for threshold, grade in sorted(GRADING_SCALE.items(), reverse=True):
        if percentage >= threshold:
            final_grade = grade
            break
            
    return percentage, final_grade

def generate_remediation_report(results, quality_checks):
    """Generates a list of missing and required items with actionable fixes."""
    output_buffer = [] # Local buffer for this section
    
    output_buffer.append("\n\n" + "#"*70)
    output_buffer.append("           🛠️  M E T A D A T A   R E M E D I A T I O N   R E P O R T")
    output_buffer.append("#"*70)
    
    missing_items = []
    
    # Get values from new results structure
    title = results['ESSENTIAL_HTML_TAGS'].get('<title>', 'YOUR PAGE TITLE')
    description_meta = results['CORE_SEO_TAGS'].get('Description', 'YOUR PAGE DESCRIPTION')
    
    # Try to find a sensible image from OG/Twitter/Schema
    suggested_image = "https://www.yourdomain.com/social-image-1200x630.jpg"
    og_image = results['SOCIAL_MEDIA_TAGS']['OPEN_GRAPH'].get('og:image')
    twitter_image = results['SOCIAL_MEDIA_TAGS']['TWITTER_CARD'].get('twitter:image')
    json_ld_scripts = results['JSON_LD_STRUCTURED_DATA']

    if og_image:
        suggested_image = og_image
    elif twitter_image:
        suggested_image = twitter_image
    elif json_ld_scripts and json_ld_scripts[0]['Schema_Type'] != '⚠️ PARSE ERROR':
        try:
            full_content = json_ld_scripts[0]['Full_Content_Object']
            if full_content.get('image'):
                suggested_image = full_content['image']
            elif full_content.get('publisher', {}).get('logo', {}).get('url'):
                suggested_image = full_content['publisher']['logo']['url']
        except:
             pass 
    
    example_url = "https://www.yourdomain.com/this-page-path"

    # CRITICAL SEO FIXES
    if results['CORE_SEO_TAGS']['Canonical'] == '❌ MISSING':
        missing_items.append({
            'Item': 'Canonical Link',
            'Why_It_Matters': 'Tells Google the definitive URL, preventing duplicate content dilution. **CRITICAL for SEO.**',
            'How_To_Fix': (f'<link rel="canonical" href="{example_url}">\n')
        })
    if 'Keywords' in results['CORE_SEO_TAGS']:
         missing_items.append({
            'Item': 'Meta Keywords Tag',
            'Why_It_Matters': 'Google officially ignores this tag. Remove it for cleaner, lighter code.',
            'How_To_Fix': 'Remove the `<meta name="keywords" ...>` tag from your HTML.',
            'Warning': True
        })

    # SOCIAL MEDIA FIXES
    if not results['SOCIAL_MEDIA_TAGS']['OPEN_GRAPH']:
        missing_items.append({
            'Item': 'Open Graph (og:) Tags',
            'Why_It_Matters': 'Controls the rich snippet when shared on Facebook, LinkedIn, etc.',
            'How_To_Fix': (
                f'<meta property="og:title" content="{title}">\n'
                f'<meta property="og:description" content="{description_meta}">\n'
                f'<meta property="og:type" content="article">\n'
                f'<meta property="og:url" content="{example_url}">\n'
                f'<meta property="og:image" content="{suggested_image}">\n'
            )
        })
    if not results['SOCIAL_MEDIA_TAGS']['TWITTER_CARD']:
        missing_items.append({
            'Item': 'Twitter Card Tags (twitter:)',
            'Why_It_Matters': 'Controls the rich media display for your link when shared on X (formerly Twitter).',
            'How_To_Fix': (
                f'<meta name="twitter:card" content="summary_large_image">\n'
                f'<meta name="twitter:site" content="@yourhandle"> (Replace with your X handle)\n'
                f'<meta name="twitter:title" content="{title}">\n'
                f'<meta name="twitter:description" content="{description_meta}">\n'
                f'<meta name="twitter:image" content="{suggested_image}">\n'
            )
        })
    
    # QUALITY CHECK SUMMARY
    output_buffer.append("\n" + "="*70)
    output_buffer.append("           ✨ C O N T E N T   Q U A L I T Y   A N A L Y S I S ✨")
    output_buffer.append("="*70)
    output_buffer.append(f"\n--- Title Tag Length ({quality_checks['Title']['Status']}) ---")
    output_buffer.append(f"  Length: {quality_checks['Title']['Length']} chars. (Goal: max {MAX_TITLE_CHARS})")
    output_buffer.append(f"  > {quality_checks['Title']['Recommendation']}")
    output_buffer.append(f"\n--- Meta Description Length ({quality_checks['Description']['Status']}) ---")
    output_buffer.append(f"  Length: {quality_checks['Description']['Length']} chars. (Goal: {MIN_DESC_CHARS} to {MAX_DESC_CHARS})")
    output_buffer.append(f"  > {quality_checks['Description']['Recommendation']}")
    output_buffer.append(f"\n--- Image Alt Text Check ---")
    output_buffer.append(f"  > {quality_checks['Image_Alt_Text']['Recommendation']}")
    output_buffer.append(f"\n--- Performance Check (Render Blocking JS) ---")
    for item in quality_checks['Render_Blocking_JS']: output_buffer.append(f"  > {item}")
    output_buffer.append(f"\n--- Structured Data (Schema) Validation ---")
    for item in quality_checks['Schema_Validation']: output_buffer.append(f"  > {item}")
    output_buffer.append("\n" + "="*70)
    
    # FINAL REMEDIATION OUTPUT
    if missing_items:
        output_buffer.append(f"\n**Action Required! Found {len(missing_items)} critical metadata item(s) to add/fix.**\n")
        for i, item in enumerate(missing_items, 1):
            output_buffer.append(f"--- {i}. {item['Item']} ---")
            output_buffer.append(f"**Reason**: {item['Why_It_Matters']}")
            if item.get('Warning'):
                 output_buffer.append(f"**Action**: {item['How_To_Fix']}\n")
            else:
                output_buffer.append(f"**Action**: Insert the following code into your `<head>` section:")
                output_buffer.append(f"```html\n{item['How_To_Fix']}```")
                output_buffer.append("\n(Remember to replace placeholder URLs/text!)\n")
    else:
        output_buffer.append("\n🎉 **Congratulations!** All critical SEO and Social Sharing tags are present.")
    
    output_buffer.append("#"*70)
    return output_buffer

# ----------------------------------------------------------------------
# 3. CONTENT SOURCE WRAPPERS (With robust headers for URL fetch)
# ----------------------------------------------------------------------

def save_report_to_pdf(report_content, filename):
    """Saves the report content to a PDF file using FPDF."""
    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    try:
        # Prepare content: strip down formatting that won't transfer (like **)
        cleaned_content = report_content.replace('**', '')
        
        # Use MultiCell to handle automatic line wrapping and page breaks
        pdf.multi_cell(w=0, h=5, txt=cleaned_content.encode('latin-1', 'replace').decode('latin-1'))
        
        pdf.output(filename)
        print(f"✅ Results successfully saved to PDF: {filename}")
        return True
    except Exception as e:
        print(f"❌ ERROR: Could not save file as PDF. Check installation of fpdf2. ({e})")
        return False

def save_results_to_file(report_content, source_name):
    """Asks the user to save the report and handles file I/O for TXT or PDF."""
    
    # Clean the source name to create a default filename base
    clean_name = os.path.basename(source_name).split('.')[0].replace('https://', '').replace('http://', '').strip('/')
    clean_name = clean_name if clean_name else "website"
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    while True:
        print("\nChoose save format:")
        print("1. Text File (.txt)")
        print("2. PDF Document (.pdf)")
        print("3. Don't save")
        save_choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if save_choice == '1':
            default_filename = f"{clean_name}_audit_report_{timestamp}.txt"
            filename = input(f"Enter filename (default: {default_filename}): ").strip() or default_filename
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ Results successfully saved to: {filename}")
            except Exception as e:
                print(f"❌ ERROR: Could not save file. Check permissions or the path provided. ({e})")
            break
            
        elif save_choice == '2':
            default_filename = f"{clean_name}_audit_report_{timestamp}.pdf"
            filename = input(f"Enter PDF filename (default: {default_filename}): ").strip() or default_filename
            # Ensure the filename ends with .pdf
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
                
            if save_report_to_pdf(report_content, filename):
                break # Exit loop on successful PDF save
            else:
                break # Exit loop on failed PDF save
        
        elif save_choice == '3':
            print("Report not saved.")
            break
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

        
def run_audit_from_url(url):
    """
    Fetches content from a URL, passes it to the core audit, and returns
    the report string on success, None on failure.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"✅ Successfully fetched content from: {url}")
        
        report = perform_metadata_audit(response.text, url)
        return report # Returns the full report string
        
    except requests.exceptions.RequestException as e:
        if '403 Client Error' in str(e):
             print(f"❌ ERROR: Access Denied (403). The server at '{url}' is actively blocking automated requests.")
             print("💡 Tip: Try the Local File option, or check if the server requires a different User-Agent.")
        else:
            print(f"❌ ERROR: Failed to fetch URL '{url}'. Check the URL, your internet connection, or if the server is blocking your request. ({e})")
        return None # Failure

def run_audit_from_file(file_path):
    """
    Reads content from a local file, passes it to the core audit, and returns
    the report string on success, None on failure.
    """
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found at path: {file_path}")
        if sys.platform.startswith('win'):
            print("💡 Hint: On Windows, use backslashes (\\) and make sure the file extension (.html) is included.")
        else:
            print("💡 Hint: Ensure you've provided the full, correct path.")
        return None # Failure

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        print(f"✅ Successfully loaded content from local file: {file_path}")
        
        report = perform_metadata_audit(html_content, file_path)
        return report # Returns the full report string
    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred during file reading or initial parsing. ({e})\n")
        return None # Failure
        
# ----------------------------------------------------------------------
# 4. MAIN EXECUTION (User Interface)
# ----------------------------------------------------------------------

if __name__ == "__main__":
    while True:
        print("\n" + "="*70)
        print("           W E L C O M E   T O   T H E   S E O   A S S I S T A N T")
        print("="*70)
        print("Choose your audit source:")
        print("1. Local File (HTML file on your computer)")
        print("2. Web URL (Live website address)")
        print("3. Exit")
        
        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            target = input("Enter the full path to the HTML file: ").strip()
            report_content = run_audit_from_file(target)
            if report_content:
                save_results_to_file(report_content, target)
                break
        elif choice == '2':
            target = input("Enter the full URL (e.g., https://www.example.com): ").strip()
            # Basic protocol check for convenience
            if not target.startswith(('http://', 'https://')):
                target = 'https://' + target
            report_content = run_audit_from_url(target)
            if report_content:
                save_results_to_file(report_content, target)
                break
        elif choice == '3':
            print("Exiting SEO Assistant. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
