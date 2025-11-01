#!/usr/bin/env python3
"""
Web scraper for rental property listings.

This script uses Playwright (a browser automation tool) to scrape rental property
listings from property management websites. It handles:
- JavaScript-rendered content (modern websites that load dynamically)
- Virtualized/infinite scroll lists (where only visible items are in the DOM)
- Parallel scraping of individual property detail pages
- Extraction of addresses, prices, bedrooms, bathrooms, and other details

The script outputs JSON data that can be easily processed or analyzed.
"""

import json
import sys
import re
import asyncio
from datetime import datetime

# Import required libraries for web scraping
# Playwright: Controls a real browser (like Chrome) to execute JavaScript
# PyQuery: Parses HTML similar to jQuery (makes it easy to find elements)
try:
    from playwright.async_api import async_playwright
    from playwright.sync_api import sync_playwright
    from pyquery import PyQuery as pq
except ImportError:
    print(json.dumps({
        "status": "error",
        "timestamp": datetime.now().isoformat(),
        "error": "playwright and pyquery are required. Install with: pip install playwright pyquery && playwright install chromium",
        "error_type": "ImportError"
    }, indent=2))
    sys.exit(1)

async def scrape_property_details_async(page, property_url, base_url):
    """
    Scrape detailed information from an individual property page (async version).
    
    This function visits a single property's detail page and extracts:
    - Property description
    - Features and amenities
    - Square footage, availability, pet policy
    - Deposit, lease terms, utilities, parking, laundry info
    - Property images
    
    Args:
        page: Playwright page object (the browser tab/window)
        property_url: URL of the property detail page (may be relative or absolute)
        base_url: Base URL of the website (used to construct absolute URLs)
    
    Returns:
        Dictionary with extracted property details, or error info if scraping fails
    """
    try:
        # Construct full URL if it's relative
        # Some sites use relative URLs like "/listings/123" instead of full URLs
        if property_url.startswith('/'):
            property_url = base_url.rstrip('/') + property_url
        elif not property_url.startswith('http'):
            property_url = base_url.rstrip('/') + '/' + property_url.lstrip('/')
        
        # Navigate to property page
        # 'networkidle' means wait until network requests finish (content is loaded)
        # Timeout of 30 seconds prevents hanging forever if page doesn't load
        await page.goto(property_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)  # Extra wait for dynamic content (JavaScript may add content after networkidle)
        
        # Get the HTML content of the page and parse it with PyQuery
        # PyQuery lets us use CSS selectors to find elements (like jQuery)
        html = await page.content()
        doc = pq(html)
        
        # Initialize details dictionary with None/empty values
        # We'll fill these in as we find information on the page
        details = {
            "property_url": property_url,
            "description": None,
            "features": [],
            "amenities": [],
            "square_footage": None,
            "availability": None,
            "pet_policy": None,
            "deposit": None,
            "lease_terms": None,
            "utilities": None,
            "parking": None,
            "laundry": None,
            "images": []
        }
        
        # Extract description using multiple CSS selectors
        # Different websites structure their HTML differently, so we try multiple patterns
        # We try common class names like '.description', and also use attribute selectors
        # like '[class*="description"]' which matches any class containing "description"
        description_selectors = [
            '.description', '[class*="description"]', '.property-description',
            '.details', '[class*="details"]', 'p.description', '.content p'
        ]
        for selector in description_selectors:
            desc_elem = doc(selector).eq(0)  # .eq(0) gets the first matching element
            if desc_elem and len(desc_elem) > 0:
                details["description"] = desc_elem.text().strip()  # .text() gets all text content
                break  # Stop trying once we find a description
        
        # Extract features/amenities
        # Features are often in lists (ul/li) or divs with class names containing "feature"
        feature_selectors = [
            '.features', '.amenities', '[class*="feature"]', '[class*="amenity"]',
            '.property-features', 'ul.features', 'ul.amenities'
        ]
        for selector in feature_selectors:
            # Look for list items (li) or elements with .feature/.amenity classes inside the selector
            features = doc(selector + ' li, ' + selector + ' .feature, ' + selector + ' .amenity')
            if features and len(features) > 0:
                # Extract text from each feature element, limit to 20 items
                details["features"] = [pq(f).text().strip() for f in features[:20]]
                break
        
        # Extract square footage using regex (regular expressions)
        # Regex lets us find patterns in text, like "950 sq ft" or "1200 square feet"
        page_text = doc.text()  # Get all text from the page (no HTML tags)
        # Pattern breakdown: (\d+) = one or more digits, \s* = optional whitespace,
        # (?:sq\.?\s*ft\.?|square\s*feet|sqft) = matches "sq ft", "sq.ft", "square feet", or "sqft"
        # re.I = case insensitive matching
        sqft_match = re.search(r'(\d+)\s*(?:sq\.?\s*ft\.?|square\s*feet|sqft)', page_text, re.I)
        if sqft_match:
            details["square_footage"] = sqft_match.group(1)  # group(1) is the first captured group (the number)
        
        # Extract availability using multiple regex patterns
        # We try different patterns because sites format availability differently
        availability_patterns = [
            r'available\s*(?:now|immediately|on\s*[\d/]+)',  # "Available now" or "Available 12/01/2025"
            r'availability[:\s]+([^\n]+)',  # "Availability: 12/01/2025"
            r'available\s*([^\n]+)'  # "Available 12/01/2025" (catch-all)
        ]
        for pattern in availability_patterns:
            avail_match = re.search(pattern, page_text, re.I)
            if avail_match:
                details["availability"] = avail_match.group(0).strip()  # group(0) is the entire match
                break
        
        # Extract pet policy
        # Looks for phrases like "pets allowed", "pet policy: dogs welcome", etc.
        pet_patterns = [
            r'pet[s]?\s*(?:allowed|policy|friendly|restrictions?)[:\s]+([^\n]+)',  # "Pets allowed: dogs only"
            r'(?:cats?|dogs?)\s*(?:allowed|welcome|not\s*allowed)',  # "Dogs allowed" or "Cats welcome"
        ]
        for pattern in pet_patterns:
            pet_match = re.search(pattern, page_text, re.I)
            if pet_match:
                details["pet_policy"] = pet_match.group(0).strip()
                break
        
        # Extract deposit amount
        # Pattern matches "deposit: $500" or "deposit 500" (optional $ sign, optional comma)
        deposit_match = re.search(r'deposit[:\s]*\$?([\d,]+)', page_text, re.I)
        if deposit_match:
            details["deposit"] = deposit_match.group(1)  # Just the number (group 1)
        
        # Extract lease terms (e.g., "12 month", "1 year")
        lease_match = re.search(r'lease[:\s]*(\d+\s*(?:month|year|mo|yr))', page_text, re.I)
        if lease_match:
            details["lease_terms"] = lease_match.group(1)
        
        # Extract utilities, parking, and laundry info
        # These use similar patterns: "utilities: included" or "parking: street parking"
        # [^\n]+ means "match everything except newlines" (captures the rest of the line)
        # [:200] limits to 200 characters to avoid overly long text
        utilities_match = re.search(r'utilities?[:\s]+([^\n]+)', page_text, re.I)
        if utilities_match:
            details["utilities"] = utilities_match.group(1).strip()[:200]
        
        parking_match = re.search(r'parking[:\s]+([^\n]+)', page_text, re.I)
        if parking_match:
            details["parking"] = parking_match.group(1).strip()[:200]
        
        laundry_match = re.search(r'laundry[:\s]+([^\n]+)', page_text, re.I)
        if laundry_match:
            details["laundry"] = laundry_match.group(1).strip()[:200]
        
        # Extract property images
        # Look for img tags where src contains "property", "rental", or "listing"
        # Also check common image container classes like .property-image or .gallery
        # [src*="property"] is an attribute selector that matches src containing "property"
        images = doc('img[src*="property"], img[src*="rental"], img[src*="listing"], .property-image img, .gallery img')
        if images and len(images) > 0:
            # Extract src attribute from each image, limit to 10 images
            details["images"] = [pq(img).attr('src') for img in images[:10] if pq(img).attr('src')]
        
        return details
        
    except Exception as e:
        return {
            "property_url": property_url,
            "error": str(e)
        }

async def scrape_properties_parallel(rentals_with_links, base_url, max_concurrent=5):
    """
    Scrape multiple property pages in parallel using async Playwright.
    
    This function speeds up scraping by visiting multiple property detail pages
    at the same time instead of one at a time. It uses:
    - asyncio for concurrent execution
    - Semaphore to limit concurrent requests (prevents overwhelming the server)
    
    Args:
        rentals_with_links: List of tuples (index, rental_dict) for properties with links
        base_url: Base URL of the website
        max_concurrent: Maximum number of pages to scrape simultaneously (default: 5)
    
    Why max_concurrent=5?
    - Too many concurrent requests can overwhelm the server or get us blocked
    - 5 is a good balance between speed and being respectful to the website
    """
    # Semaphore acts like a gatekeeper - only allows max_concurrent tasks at once
    # When a task finishes, the next one waiting can start
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_semaphore(index, rental, browser):
        # async with semaphore: waits if 5 tasks are already running
        async with semaphore:
            try:
                rental_address = rental.get('address') if rental else None
                address_display = (rental_address[:50] if rental_address else 'Unknown') if rental_address else 'Unknown'
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{index+1}/{len(rentals_with_links)}] Scraping: {address_display}...", file=sys.stderr)
                # Create a new browser context for each page to avoid conflicts
                # A context is like an isolated browser session - cookies and state don't interfere
                # This prevents one property page from affecting another
                context = await browser.new_context(
                    # User agent makes us look like a real browser (some sites block bots)
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}  # Set browser window size
                )
                page = await context.new_page()  # Create a new tab/page in this context
                
                # Scrape the property details and merge them into the rental dictionary
                details = await scrape_property_details_async(page, rental['property_link'], base_url)
                rental.update(details)  # Merge details into rental (adds description, features, etc.)
                
                rental_address = rental.get('address') if rental else None
                address_display = (rental_address[:50] if rental_address else 'Unknown') if rental_address else 'Unknown'
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{index+1}/{len(rentals_with_links)}] ✓ Completed: {address_display}...", file=sys.stderr)
                
                await context.close()
            except Exception as e:
                rental['details_error'] = str(e)
                rental_address = rental.get('address') if rental else None
                address_display = (rental_address[:50] if rental_address else 'Unknown') if rental_address else 'Unknown'
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{index+1}/{len(rentals_with_links)}] ✗ Error: {address_display}... - {str(e)[:100]}", file=sys.stderr)
    
    # Create a single browser instance to share across all tasks
    # This is more efficient than creating a new browser for each property
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless=True means no visible browser window
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching {len(rentals_with_links)} parallel scraping tasks (max {max_concurrent} concurrent)...", file=sys.stderr)
            # Create tasks for all properties
            # Each task will scrape one property, but they'll run concurrently (up to max_concurrent)
            tasks = [scrape_with_semaphore(i, rental, browser) for i, rental in rentals_with_links]
            
            # Run all tasks in parallel
            # asyncio.gather waits for all tasks to complete before continuing
            # The semaphore inside scrape_with_semaphore ensures only max_concurrent run at once
            await asyncio.gather(*tasks)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ All property detail scraping completed!", file=sys.stderr)
        finally:
            await browser.close()

def scrape_rentals(url):
    """
    Main scraping function - scrapes rental listings from a property management website.
    
    This function handles the main listing page and implements a sophisticated scrolling
    strategy to capture all properties from virtualized/infinite scroll lists.
    
    The scraping process:
    1. Load the main listings page
    2. Extract property count from page text (e.g., "Showing 68 of 68 results")
    3. Try to extract property UIDs from JavaScript state
    4. Scroll to bottom to trigger loading all items
    5. Scroll back up slowly, checking for properties at each position
    6. Extract property details (address, price, beds, baths) from visible cards
    7. Visit each property's detail page in parallel to get full information
    
    Args:
        url: URL of the property listings page to scrape
    
    Returns:
        Dictionary with scraped data including rental_listings, contact_info, etc.
    """
    try:
        with sync_playwright() as p:
            # Launch browser (headless by default - no visible window)
            # We use sync_playwright here (not async) because this function is synchronous
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                # User agent string makes requests look like they come from a real browser
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}  # Browser window size
            )
            page = context.new_page()
            
            # Navigate to the page and wait for it to load
            # 'networkidle' waits until network requests finish (content is loaded)
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for potential dynamic content (property listings, etc.)
            # JavaScript may add content after 'networkidle', so we wait a bit more
            page.wait_for_timeout(3000)  # Wait 3 seconds for dynamic content
            
            # Scroll to load all virtualized/infinite scroll content incrementally
            # Virtualized lists only render items that are visible, so we need to scroll
            # to make all items appear in the DOM before we can scrape them
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting incremental property collection...", file=sys.stderr)
            
            # Wait for initial content
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for initial content to load...", file=sys.stderr)
            page.wait_for_timeout(2000)
            
            # Track all unique properties we've found
            # Dictionary key is listable_uid (unique ID for each property)
            # Value is property data (address, price, link, etc.)
            all_properties = {}  # key: listable_uid, value: property data
            scroll_position = 0
            scroll_attempts = 0
            max_scroll_attempts = 200
            no_new_properties_count = 0
            target_count = None
            
            # First, check what the target count should be
            # Many sites show "Showing X of Y results" - we want to find Y
            # page.evaluate() runs JavaScript in the browser and returns the result
            page_text = page.evaluate("document.body.innerText")  # Get all visible text
            import re as re_module
            # Look for pattern like "24 of 68" or "Showing 1 of 67"
            count_match = re_module.search(r'(\d+)\s+of\s+(\d+)', page_text)
            if count_match:
                target_count = int(count_match.group(2))  # group(2) is the total count
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Target: {target_count} properties", file=sys.stderr)
            
            # Strategy: Scroll to multiple positions to capture all virtualized items
            # Virtualized lists only render visible items, so we need to scroll through
            # the entire page to trigger rendering of all items
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting multi-position scroll strategy...", file=sys.stderr)
            
            # First, get the total page height
            # scrollHeight is the total height of the page content (may be taller than viewport)
            max_scroll = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            viewport_height = page.evaluate("window.innerHeight")  # Height of visible browser window
            
            # Calculate scroll positions to hit different sections
            # We calculate positions evenly spaced throughout the page
            # Extra positions (+2) to be safe - ensures we don't miss items at boundaries
            num_positions = max(5, (target_count or 68) // 24 + 2)  # Extra positions to be safe
            scroll_positions = []
            for i in range(num_positions):
                # Evenly distribute positions from top (0) to bottom (max_scroll)
                pos = int((i / (num_positions - 1)) * max_scroll) if num_positions > 1 else 0
                scroll_positions.append(pos)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Will check {len(scroll_positions)} different scroll positions", file=sys.stderr)
            
            # Try to extract all properties from JavaScript state first
            # Sometimes properties are embedded in JavaScript variables before they're rendered
            # This is faster than scrolling if it works
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting to extract properties from JavaScript state...", file=sys.stderr)
            
            # Try to find properties in window/global state
            # This JavaScript runs in the browser and searches through all <script> tags
            # looking for property UIDs (unique identifiers) embedded in the code
            js_properties = page.evaluate("""
                () => {
                    const results = [];
                    const scripts = Array.from(document.querySelectorAll('script'));
                    for (const script of scripts) {
                        try {
                            const text = script.textContent || script.innerText;
                            // Look for patterns like "listable_uid=abc-123-def-456"
                            if (text.includes('listable_uid')) {
                                // Match UUIDs (36 character hex strings with dashes)
                                const uidMatches = text.match(/listable_uid=([a-f0-9-]{36})/g);
                                if (uidMatches) {
                                    uidMatches.forEach(match => {
                                        const uid = match.split('=')[1];
                                        if (uid && !results.find(r => r.uid === uid)) {
                                            results.push({uid: uid, source: 'script'});
                                        }
                                    });
                                }
                            }
                        } catch(e) {}
                    }
                    return results;
                }
            """)
            
            if js_properties and len(js_properties) > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(js_properties)} property UIDs in JavaScript", file=sys.stderr)
                for prop in js_properties:
                    if prop['uid'] not in all_properties:
                        # Construct property link URL (adjust domain as needed for different sites)
                        # Extract base domain (e.g., "https://example.com") from the URL
                        base_domain = '/'.join(url.split('/')[:3])
                        # Build the full property link URL
                        all_properties[prop['uid']] = {'uid': prop['uid'], 'property_link': f"{base_domain}/listings/rental_applications/new?listable_uid={prop['uid']}&source=Website"}
            
            # Strategy: Scroll to bottom first to trigger loading all items, then scroll back up
            # Many virtualized lists load items as you scroll down, so scrolling to the bottom
            # first ensures all items are loaded/tracked by the JavaScript framework
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Scrolling to absolute bottom to trigger all items...", file=sys.stderr)
            
            # Scroll to bottom multiple times to ensure all content loads
            # Sometimes the page height increases as you scroll (more content loads)
            # So we scroll multiple times until the page stops growing
            for bottom_scroll in range(10):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # Scroll to absolute bottom
                page.wait_for_timeout(2000)  # Wait for content to load
                page.evaluate("window.scrollBy(0, 1000)")  # Try scrolling past bottom (sometimes triggers loading)
                page.wait_for_timeout(1500)
            
            # Wait extra long at bottom
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting at bottom for all items to load...", file=sys.stderr)
            page.wait_for_timeout(5000)
            
            # Update max scroll after loading
            max_scroll = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Page height after bottom scroll: {max_scroll}px", file=sys.stderr)
            
            # Now scroll back up slowly, checking at each position
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 2: Scrolling back up slowly to capture all properties...", file=sys.stderr)
            scroll_pos = max_scroll
            scroll_increment = 150  # Smaller increments for more thorough coverage
            no_new_count = 0
            
            while scroll_pos > 0 and len(all_properties) < (target_count or 100) and no_new_count < 150:
                page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                page.wait_for_timeout(3000)  # Wait longer for virtualization
                
                # Check multiple times at this position to catch items as they render
                for check_iteration in range(3):
                    if check_iteration > 0:
                        page.wait_for_timeout(1500)  # Additional wait between checks
                    
                    # Extract properties at this position
                    current_html = page.content()
                    current_doc = pq(current_html)
                    property_links = current_doc('a[href*="listable_uid"]')
                    
                    found_new = False
                    for link in property_links:
                        href = pq(link).attr('href')
                        if href and 'listable_uid' in href:
                            uid_match = re_module.search(r'listable_uid=([a-f0-9-]+)', href)
                            if uid_match:
                                uid = uid_match.group(1)
                                if uid not in all_properties:
                                    # Extract this property (simplified extraction here)
                                    all_properties[uid] = {'uid': uid, 'property_link': href}
                                    found_new = True
                                    no_new_count = 0
                                    if len(all_properties) % 5 == 0 or len(all_properties) <= 10:
                                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found property #{len(all_properties)} at scroll {scroll_pos}px (check {check_iteration+1}): {uid[:20]}...", file=sys.stderr)
                    
                    # If we found new properties or reached target, break early
                    if found_new and len(all_properties) >= (target_count or 100):
                        break
                
                if not found_new:
                    no_new_count += 1
                    if no_new_count % 10 == 0:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] No new properties for {no_new_count} checks at scroll {scroll_pos}px (have {len(all_properties)}/{target_count or '?'})", file=sys.stderr)
                
                # Scroll backward (up) in increments
                scroll_pos = max(0, scroll_pos - scroll_increment)
                
                # Check if we've reached target
                if target_count and len(all_properties) >= target_count:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Reached target of {target_count} properties!", file=sys.stderr)
                    break
                
                # Update max_scroll in case page grew
                current_max = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                if current_max > max_scroll:
                    max_scroll = current_max
                    no_new_count = 0  # Reset counter if page grew
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Page height increased to {max_scroll}px, resetting counter", file=sys.stderr)
                
                # If we haven't found new properties for a while, try scrolling faster to different areas
                if no_new_count == 15:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new properties for 15 checks. Trying larger jumps...", file=sys.stderr)
                    scroll_pos = min(scroll_pos + 2000, max_scroll)
                    page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                    page.wait_for_timeout(4000)
                    no_new_count = 0  # Reset counter
                elif no_new_count == 30:
                    # Try scrolling to absolute bottom
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Still stuck. Scrolling to absolute bottom...", file=sys.stderr)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(5000)
                    scroll_pos = page.evaluate("window.pageYOffset || window.scrollY || 0")
                    max_scroll = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
                    no_new_count = 0
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Finished scrolling. Collected {len(all_properties)} properties", file=sys.stderr)
            
            # Now extract full details for properties that only have UID and link
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Extracting full details for {len(all_properties)} properties...", file=sys.stderr)
            
            # Scroll through positions again to extract details for each property
            properties_needing_details = [uid for uid, prop in all_properties.items() if not prop.get('address') and not prop.get('price')]
            
            if properties_needing_details:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {len(properties_needing_details)} properties need detail extraction. Scrolling to find them...", file=sys.stderr)
                
                # Scroll through positions to find and extract details
                for pos_idx, scroll_pos in enumerate(scroll_positions):
                    page.evaluate(f"window.scrollTo(0, {scroll_pos})")
                    page.wait_for_timeout(3000)
                    
                    current_html = page.content()
                    current_doc = pq(current_html)
                    property_links = current_doc('a[href*="listable_uid"]')
                    
                    for link in property_links:
                        href = pq(link).attr('href')
                        if href and 'listable_uid' in href:
                            uid_match = re_module.search(r'listable_uid=([a-f0-9-]+)', href)
                            if uid_match:
                                uid = uid_match.group(1)
                                if uid in all_properties and (not all_properties[uid].get('address') or not all_properties[uid].get('price')):
                                    # This property needs details - extract them now
                                    prop_data = all_properties[uid]
                                    
                                    # Find the parent card
                                    parent = pq(link)
                                    card_element = None
                                    
                                    for level in range(15):
                                        parent = parent.parent()
                                        if parent and len(parent) > 0:
                                            try:
                                                tag = parent[0].tag if hasattr(parent[0], 'tag') else None
                                                classes = parent.attr('class') or ''
                                                parent_text = parent.text()[:100] if parent else ""
                                                
                                                if (tag in ['div', 'article', 'section', 'li'] and 
                                                    (any(keyword in classes.lower() for keyword in ['card', 'property', 'listing', 'rental', 'item', 'result', 'unit']) or
                                                     '$' in parent_text or
                                                     any(street in parent_text.lower() for street in ['street', 'st', 'ave', 'road', 'drive', 'lane', 'way']))):
                                                    card_element = parent[0]
                                                    break
                                            except:
                                                continue
                                    
                                    if not card_element:
                                        try:
                                            immediate_parent = pq(link).parent()
                                            if immediate_parent and len(immediate_parent) > 0:
                                                card_element = immediate_parent[0]
                                            else:
                                                card_element = link
                                        except:
                                            card_element = link
                                    
                                    # Extract details using the same logic as before
                                    card_pq = pq(card_element)
                                    card_text = card_pq.text()
                                    
                                    # Extract address
                                    if not prop_data.get('address'):
                                        address_elem = card_pq('h2, h3, h4, .address, [class*="address"], [class*="location"]').eq(0)
                                        if address_elem and len(address_elem) > 0:
                                            addr_text = address_elem.text().strip()
                                            if not addr_text.startswith('RENT') and '$' not in addr_text:
                                                prop_data['address'] = addr_text
                                        
                                        if not prop_data.get('address'):
                                            address_match = re_module.search(r'(\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Way|Blvd|Boulevard|Ct|Court|Circle|Cir|Place|Pl|Apt|Apartment|Unit|#)[\s,]*[\w\s]*(?:,\s*)?[A-Z][a-z]+\s*,\s*[A-Z]{2}\s+\d{5})', card_text, re_module.I)
                                            if address_match:
                                                prop_data['address'] = address_match.group(1).strip()
                                    
                                    # Extract price
                                    if not prop_data.get('price'):
                                        price_elem = card_pq('.price, [class*="price"], .rent, [class*="rent"], .cost, [class*="cost"]').eq(0)
                                        if price_elem and len(price_elem) > 0:
                                            price_text = price_elem.text().strip()
                                            price_match = re_module.search(r'\$[\d,]+(?:\s*/\s*(?:month|mo|week|wk))?', price_text)
                                            if price_match:
                                                prop_data['price'] = price_match.group(0).strip()
                                        
                                        if not prop_data.get('price'):
                                            price_match = re_module.search(r'\$[\d,]+(?:\s*/\s*(?:month|mo|week|wk))?', card_text)
                                            if price_match:
                                                prop_data['price'] = price_match.group(0).strip()
                                    
                                    # Extract beds/baths
                                    card_html = card_pq.html() or ''
                                    if not prop_data.get('beds'):
                                        beds_match = re_module.search(r'\d+\s*(?:bed|br|bedroom)', card_html, re_module.I)
                                        if beds_match:
                                            prop_data['beds'] = beds_match.group(0).strip()
                                    
                                    if not prop_data.get('baths'):
                                        baths_match = re_module.search(r'\d+\s*(?:bath|bathroom)', card_html, re_module.I)
                                        if baths_match:
                                            prop_data['baths'] = baths_match.group(0).strip()
                                    
                                    all_properties[uid] = prop_data
            
            # All properties have been collected and details extracted
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Collected {len(all_properties)} unique properties", file=sys.stderr)
            
            # Convert collected properties to rental objects
            rentals = []
            for uid, prop_data in all_properties.items():
                rental = {
                    'address': prop_data.get('address'),
                    'price': prop_data.get('price'),
                    'beds': prop_data.get('beds'),
                    'baths': prop_data.get('baths'),
                    'property_link': prop_data.get('property_link')
                }
                
                # Include rental if it has a property_link (most important) OR has address/price
                if rental.get('property_link') or rental.get('address') or rental.get('price'):
                    rentals.append(rental)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Extracted {len(rentals)} valid rental listings", file=sys.stderr)
            
            # Get final HTML for metadata extraction (page is still loaded)
            html = page.content()
        
        # Extract contact information and page metadata from HTML
        doc = pq(html)
        page_text = doc.text()
        
        # Extract contact information
        contact_info = {
            "phone": [],
            "email": [],
            "address": []
        }
        
        # Find phone numbers using regex
        # Pattern matches formats like: (555) 123-4567, 555-123-4567, 555.123.4567, 5551234567
        # \(? = optional opening parenthesis, \d{3} = exactly 3 digits, etc.
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, page_text)
        contact_info["phone"] = list(set(phones[:10]))  # Remove duplicates (set) and limit to 10 unique
        
        # Find email addresses using regex
        # Pattern matches standard email format: username@domain.com
        # \b = word boundary (ensures we match complete emails, not parts of words)
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        contact_info["email"] = list(set(emails[:10]))  # Remove duplicates and limit to 10 unique
        
        # Try to find addresses in text
        # Pattern matches: "123 Main Street, City, ST 12345" or similar formats
        # Looks for street numbers, street names (Street, St, Avenue, etc.), state, zip
        address_pattern = r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard|ct|court|circle|cir|place|pl)[\s,]*[\w\s]*(?:,\s*)?[A-Z]{2}\s+\d{5}?'
        addresses = re.findall(address_pattern, page_text, re.IGNORECASE)
        contact_info["address"] = list(set(addresses[:10]))  # Remove duplicates and limit to 10 unique
        
        # Extract page metadata
        title_elem = doc('title')
        title_text = title_elem.text().strip() if title_elem else None
        
        meta_description = doc('meta[name="description"]')
        description = meta_description.attr('content') if meta_description else None
        
        # Prepare final result
        result = {
            "scraped_at": datetime.now().isoformat(),
            "url": url,
            "title": title_text,
            "description": description,
            "contact_info": contact_info,
            "rental_listings": rentals,
            "listing_count": len(rentals)
        }
        
        # Add note if no rentals found
        if not rentals:
            result["note"] = "No structured rental listings found on page. Page may load listings dynamically via JavaScript. Contact information extracted from page."
            return result
        
        # Now scrape detailed information from each property page in parallel
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {len(rentals)} properties. Starting parallel detail scraping...", file=sys.stderr)
        
        # Extract base URL for constructing absolute URLs
        base_url = '/'.join(url.split('/')[:3])
        
        # Filter rentals that have property links
        rentals_with_links = [(i, rental) for i, rental in enumerate(rentals) if rental and rental.get('property_link')]
        
        if rentals_with_links:
            # Run async scraping in parallel
            asyncio.run(scrape_properties_parallel(rentals_with_links, base_url))
        
        return result
        
    except Exception as e:
        raise Exception(f"Error scraping {url}: {str(e)}")

def main():
    """
    Main function that scrapes rental information and returns results in JSON format.
    
    This is the entry point for the script. It:
    1. Sets the URL to scrape (change this to scrape different sites)
    2. Calls scrape_rentals() to do the actual scraping
    3. Formats the results as JSON and prints to stdout
    4. Returns the results dictionary
    
    Progress messages are printed to stderr (so they don't interfere with JSON output)
    Final JSON output goes to stdout (can be redirected to a file)
    """
    # Update this URL to scrape a different property management website
    url = "https://www.emeraldpm.com/home_rentals"
    
    # Print progress to stderr (standard error) so it doesn't interfere with JSON output
    # JSON output goes to stdout (standard output) so it can be redirected to a file
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting rental scraping for: {url}", file=sys.stderr)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
    
    try:
        # Call the main scraping function
        rental_data = scrape_rentals(url)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Scraping completed! Found {rental_data.get('listing_count', 0)} listings", file=sys.stderr)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
        
        # Format results as JSON
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "source_url": url,
            "data": rental_data
        }
        
        # Print JSON to stdout (can be redirected: python main.py > output.json)
        print(json.dumps(results, indent=2))
        return results
        
    except Exception as e:
        # If anything goes wrong, format error as JSON and raise exception
        error_result = {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "error_type": type(e).__name__
        }
        print(json.dumps(error_result, indent=2))
        raise

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        sys.exit(1)

