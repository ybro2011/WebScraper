from flask import Flask, render_template, request, flash, Response, stream_with_context, send_file, jsonify
import googlemaps
import openpyxl
import time
import os
import re
from playwright.sync_api import sync_playwright
import json
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', os.urandom(24))

# Log environment variables
logger.info(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
logger.info(f"PORT: {os.getenv('PORT')}")
logger.info(f"PYTHONPATH: {os.getenv('PYTHONPATH')}")

def search_places(gmaps, location, industry, radius=500):
    places = []
    response = gmaps.places_nearby(location=location, radius=radius, keyword=industry)
    places.extend(response.get('results', []))
    while 'next_page_token' in response:
        time.sleep(2)  # Comply with API requirements
        response = gmaps.places_nearby(page_token=response['next_page_token'])
        places.extend(response.get('results', []))
    return places

def get_place_details(gmaps, place_id):
    fields = ['name', 'formatted_address', 'website']
    detail = gmaps.place(place_id=place_id, fields=fields)
    return detail.get('result', {})

def fetch_emails_from_website(url):
    emails = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=10000)
            # Extract emails from mailto links
            mailto_links = page.query_selector_all('a[href^="mailto:"]')
            for link in mailto_links:
                email = link.get_attribute('href').replace('mailto:', '').split('?')[0]
                emails.add(email)
            # Extract emails from the text content
            page_content = page.content()
            found_emails = re.findall(r'[\w\.-]+@[\w\.-]+', page_content)
            emails.update(found_emails)
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
        finally:
            browser.close()
    return ', '.join(emails)

def save_to_excel(businesses, filename):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Businesses"
    headers = ["Name", "Website", "Address", "Email"]
    ws.append(headers)
    for b in businesses:
        ws.append([
            b.get("name"),
            b.get("website", ""),
            b.get("formatted_address", ""),
            b.get("email", "")
        ])
    wb.save(filename)
    return filename

def generate_updates(api_key, location, industry):
    try:
        gmaps = googlemaps.Client(key=api_key)
        businesses = {}
        lat, lng = map(float, location.split(','))

        # Define grid offsets (in degrees) for approximately 500m spacing
        offsets = [-0.0045, 0, 0.0045]

        for lat_offset in offsets:
            for lng_offset in offsets:
                new_location = (lat + lat_offset, lng + lng_offset)
                yield f"data: Searching around coordinates {new_location}...\n\n"
                places = search_places(gmaps, new_location, industry)
                yield f"data: Found {len(places)} places in this area\n\n"
                
                for place in places:
                    place_id = place['place_id']
                    if place_id not in businesses:
                        yield f"data: Processing {place.get('name', 'Unknown')}...\n\n"
                        details = get_place_details(gmaps, place_id)
                        website = details.get('website')
                        if website:
                            yield f"data: Fetching emails from {website}...\n\n"
                            emails = fetch_emails_from_website(website)
                            details['email'] = emails
                        else:
                            details['email'] = ""
                        businesses[place_id] = details

        # Save results to Excel
        documents_dir = os.path.join(os.path.expanduser('~'), 'Documents')
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)
        filename = f"{industry.replace(' ', '_')}_businesses.xlsx"
        file_path = os.path.join(documents_dir, filename)
        save_to_excel(businesses.values(), file_path)
        yield f"data: Success! Found {len(businesses)} businesses. Results saved to {file_path}\n\n"
        
    except Exception as e:
        logger.error(f"Error in generate_updates: {e}")
        yield f"data: Error: {str(e)}\n\n"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    api_key = request.form['api_key']
    location = request.form['location']
    industry = request.form['industry']
    
    return Response(stream_with_context(generate_updates(api_key, location, industry)),
                  mimetype='text/event-stream')

@app.route('/preview')
def preview():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        return jsonify([])
    
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    data = []
    
    # Skip header row
    for row in list(ws.rows)[1:]:
        data.append({
            'name': row[0].value,
            'website': row[1].value,
            'formatted_address': row[2].value,
            'email': row[3].value
        })
    
    return jsonify(data)

@app.route('/download')
def download():
    file_path = request.args.get('file')
    if not file_path or not os.path.exists(file_path):
        return "File not found", 404
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )


