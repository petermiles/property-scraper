#!/usr/bin/env python3
"""Web scraper for rental property listings."""

import json
import sys
import re
import asyncio
from datetime import datetime

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
    """Scrape detailed information from an individual property page (async version)."""
    try:
        # Construct full URL if it's relative
        if property_url.startswith('/'):
            property_url = base_url.rstrip('/') + property_url
        elif not property_url.startswith('http'):
            property_url = base_url.rstrip('/') + '/' + property_url.lstrip('/')
        
        # Navigate to property page
        await page.goto(property_url, wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)  # Wait for dynamic content
        
        html = await page.content()
        doc = pq(html)
        
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
        
        # Extract description
        description_selectors = [
            '.description', '[class*="description"]', '.property-description',
            '.details', '[class*="details"]', 'p.description', '.content p'
        ]
        for selector in description_selectors:
            desc_elem = doc(selector).eq(0)
            if desc_elem and len(desc_elem) > 0:
                details["description"] = desc_elem.text().strip()
                break
        
        # Extract features/amenities
        feature_selectors = [
            '.features', '.amenities', '[class*="feature"]', '[class*="amenity"]',
            '.property-features', 'ul.features', 'ul.amenities'
        ]
        for selector in feature_selectors:
            features = doc(selector + ' li, ' + selector + ' .feature, ' + selector + ' .amenity')
            if features and len(features) > 0:
                details["features"] = [pq(f).text().strip() for f in features[:20]]
                break
        
        # Extract square footage
        page_text = doc.text()
        sqft_match = re.search(r'(\d+)\s*(?:sq\.?\s*ft\.?|square\s*feet|sqft)', page_text, re.I)
        if sqft_match:
            details["square_footage"] = sqft_match.group(1)
        
        # Extract availability
        availability_patterns = [
            r'available\s*(?:now|immediately|on\s*[\d/]+)',
            r'availability[:\s]+([^\n]+)',
            r'available\s*([^\n]+)'
        ]
        for pattern in availability_patterns:
            avail_match = re.search(pattern, page_text, re.I)
            if avail_match:
                details["availability"] = avail_match.group(0).strip()
                break
        
        # Extract pet policy
        pet_patterns = [
            r'pet[s]?\s*(?:allowed|policy|friendly|restrictions?)[:\s]+([^\n]+)',
            r'(?:cats?|dogs?)\s*(?:allowed|welcome|not\s*allowed)',
        ]
        for pattern in pet_patterns:
            pet_match = re.search(pattern, page_text, re.I)
            if pet_match:
                details["pet_policy"] = pet_match.group(0).strip()
                break
        
        # Extract deposit
        deposit_match = re.search(r'deposit[:\s]*\$?([\d,]+)', page_text, re.I)
        if deposit_match:
            details["deposit"] = deposit_match.group(1)
        
        # Extract lease terms
        lease_match = re.search(r'lease[:\s]*(\d+\s*(?:month|year|mo|yr))', page_text, re.I)
        if lease_match:
            details["lease_terms"] = lease_match.group(1)
        
        # Extract utilities
        utilities_match = re.search(r'utilities?[:\s]+([^\n]+)', page_text, re.I)
        if utilities_match:
            details["utilities"] = utilities_match.group(1).strip()[:200]
        
        # Extract parking
        parking_match = re.search(r'parking[:\s]+([^\n]+)', page_text, re.I)
        if parking_match:
            details["parking"] = parking_match.group(1).strip()[:200]
        
        # Extract laundry
        laundry_match = re.search(r'laundry[:\s]+([^\n]+)', page_text, re.I)
        if laundry_match:
            details["laundry"] = laundry_match.group(1).strip()[:200]
        
        # Extract images
        images = doc('img[src*="property"], img[src*="rental"], img[src*="listing"], .property-image img, .gallery img')
        if images and len(images) > 0:
            details["images"] = [pq(img).attr('src') for img in images[:10] if pq(img).attr('src')]
        
        return details
        
    except Exception as e:
        return {
            "property_url": property_url,
            "error": str(e)
        }

async def scrape_properties_parallel(rentals_with_links, base_url, max_concurrent=5):
    """Scrape multiple property pages in parallel using async Playwright."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def scrape_with_semaphore(index, rental, browser):
        async with semaphore:
            try:
                rental_address = rental.get('address') if rental else None
                address_display = (rental_address[:50] if rental_address else 'Unknown') if rental_address else 'Unknown'
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [{index+1}/{len(rentals_with_links)}] Scraping: {address_display}...", file=sys.stderr)
                # Create a new context for each page to avoid conflicts
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = await context.new_page()
                
                details = await scrape_property_details_async(page, rental['property_link'], base_url)
                rental.update(details)
                
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
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Launching {len(rentals_with_links)} parallel scraping tasks (max {max_concurrent} concurrent)...", file=sys.stderr)
            # Create tasks for all properties
            tasks = [scrape_with_semaphore(i, rental, browser) for i, rental in rentals_with_links]
            
            # Run all tasks in parallel
            await asyncio.gather(*tasks)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ All property detail scraping completed!", file=sys.stderr)
        finally:
            await browser.close()

def scrape_rentals(url):
    """Scrape rental information from a property management website using Playwright to execute JavaScript."""
    try:
        with sync_playwright() as p:
            # Launch browser (headless by default)
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            # Navigate to the page and wait for it to load
            page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Wait for potential dynamic content (property listings, etc.)
            page.wait_for_timeout(3000)  # Wait 3 seconds for dynamic content
            
            # Scroll to load all virtualized/infinite scroll content incrementally
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting incremental property collection...", file=sys.stderr)
            
            # Wait for initial content
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Waiting for initial content to load...", file=sys.stderr)
            page.wait_for_timeout(2000)
            
            # Track all unique properties we've found
            all_properties = {}  # key: listable_uid, value: property data
            scroll_position = 0
            scroll_attempts = 0
            max_scroll_attempts = 200
            no_new_properties_count = 0
            target_count = None
            
            # First, check what the target count should be
            page_text = page.evaluate("document.body.innerText")
            import re as re_module
            count_match = re_module.search(r'(\d+)\s+of\s+(\d+)', page_text)
            if count_match:
                target_count = int(count_match.group(2))
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Target: {target_count} properties", file=sys.stderr)
            
            # Strategy: Scroll to multiple positions to capture all virtualized items
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting multi-position scroll strategy...", file=sys.stderr)
            
            # First, get the total page height
            max_scroll = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            viewport_height = page.evaluate("window.innerHeight")
            
            # Calculate scroll positions to hit different sections
            num_positions = max(5, (target_count or 68) // 24 + 2)  # Extra positions to be safe
            scroll_positions = []
            for i in range(num_positions):
                pos = int((i / (num_positions - 1)) * max_scroll) if num_positions > 1 else 0
                scroll_positions.append(pos)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Will check {len(scroll_positions)} different scroll positions", file=sys.stderr)
            
            # Try to extract all properties from JavaScript state first
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting to extract properties from JavaScript state...", file=sys.stderr)
            
            # Try to find properties in window/global state
            js_properties = page.evaluate("""
                () => {
                    const results = [];
                    const scripts = Array.from(document.querySelectorAll('script'));
                    for (const script of scripts) {
                        try {
                            const text = script.textContent || script.innerText;
                            if (text.includes('listable_uid')) {
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
                        base_domain = '/'.join(url.split('/')[:3])
                        all_properties[prop['uid']] = {'uid': prop['uid'], 'property_link': f"{base_domain}/listings/rental_applications/new?listable_uid={prop['uid']}&source=Website"}
            
            # Strategy: Scroll to bottom first to trigger loading all items, then scroll back up
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Scrolling to absolute bottom to trigger all items...", file=sys.stderr)
            
            # Scroll to bottom multiple times to ensure all content loads
            for bottom_scroll in range(10):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
                page.evaluate("window.scrollBy(0, 1000)")  # Try scrolling past bottom
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
        
        # Find phone numbers
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, page_text)
        contact_info["phone"] = list(set(phones[:10]))  # Limit to 10 unique
        
        # Find email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, page_text)
        contact_info["email"] = list(set(emails[:10]))  # Limit to 10 unique
        
        # Try to find addresses in text
        address_pattern = r'\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|way|blvd|boulevard|ct|court|circle|cir|place|pl)[\s,]*[\w\s]*(?:,\s*)?[A-Z]{2}\s+\d{5}?'
        addresses = re.findall(address_pattern, page_text, re.IGNORECASE)
        contact_info["address"] = list(set(addresses[:10]))  # Limit to 10 unique
        
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
    """Main function that scrapes rental information and returns results in JSON format."""
    # Update this URL to scrape a different property management website
    url = "https://www.emeraldpm.com/home_rentals"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting rental scraping for: {url}", file=sys.stderr)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
    
    try:
        rental_data = scrape_rentals(url)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Scraping completed! Found {rental_data.get('listing_count', 0)} listings", file=sys.stderr)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ========================================", file=sys.stderr)
        
        results = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "source_url": url,
            "data": rental_data
        }
        
        print(json.dumps(results, indent=2))
        return results
        
    except Exception as e:
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

