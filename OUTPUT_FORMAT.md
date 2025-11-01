# Understanding the Output

This guide explains the structure of the JSON data the scraper produces.

## Overview

The scraper outputs a JSON file containing all the scraped property information. JSON (JavaScript Object Notation) is a common data format that's easy for both humans and computers to read.

## Top-Level Structure

The output has this basic structure:

```json
{
  "status": "success",
  "timestamp": "2025-10-31T16:00:00.123456",
  "source_url": "https://example-property-site.com/listings",
  "data": {
    // All the actual property data goes here
  }
}
```

### Top-Level Fields

- **`status`** - Either `"success"` or `"error"` - tells you if scraping worked
- **`timestamp`** - When the scraping happened (ISO format)
- **`source_url`** - The website that was scraped
- **`data`** - Contains all the actual property information

## The `data` Object

Inside `data`, you'll find:

```json
{
  "scraped_at": "2025-10-31T16:00:00",
  "url": "https://example-property-site.com/listings",
  "title": "Page Title",
  "description": "Page description",
  "contact_info": { ... },
  "rental_listings": [ ... ],
  "listing_count": 24
}
```

### Data Fields Explained

- **`scraped_at`** - When the data was collected
- **`url`** - The URL that was scraped
- **`title`** - The page title (from `<title>` tag)
- **`description`** - Page meta description
- **`contact_info`** - Contact information found on the page
- **`rental_listings`** - Array of all property listings (this is the main data!)
- **`listing_count`** - Total number of properties found

## Contact Information

The `contact_info` object contains:

```json
{
  "phone": ["(541) 555-1234", "(541) 555-5678"],
  "email": ["contact@example.com"],
  "address": ["123 Main St, City, State 12345"]
}
```

These are extracted from anywhere on the page using pattern matching. They might include business addresses, contact numbers, etc.

## Rental Listings Array

The `rental_listings` array is where the real property data lives. Each item in the array represents one property:

```json
{
  "address": "123 Main Street, City, State 12345",
  "price": "$1,200/month",
  "beds": "2 bed",
  "baths": "1 bath",
  "property_link": "https://example-site.com/listings/...",
  "property_url": "https://example-site.com/listings/...",
  "description": "Beautiful 2-bedroom apartment...",
  "features": ["Hardwood floors", "Updated kitchen"],
  "amenities": ["Laundry", "Parking"],
  "square_footage": "950",
  "availability": "Available 12/01/2025",
  "pet_policy": "Cats allowed, dogs not allowed",
  "deposit": "1200",
  "lease_terms": "12 month",
  "utilities": "Tenant pays electric",
  "parking": "Street parking available",
  "laundry": "Coin-operated laundry on-site",
  "images": ["https://...", "https://..."]
}
```

### Property Fields Explained

#### Basic Information
- **`address`** - Property street address (may be `null` if not found)
- **`price`** - Monthly rent (e.g., "$1,200/month")
- **`beds`** - Number of bedrooms (e.g., "2 bed")
- **`baths`** - Number of bathrooms (e.g., "1 bath")
- **`property_link`** - Link to the property listing page
- **`property_url`** - Same as property_link (for convenience)

#### Detailed Information (from individual property pages)
- **`description`** - Full property description text
- **`features`** - Array of property features
- **`amenities`** - Array of amenities
- **`square_footage`** - Size in square feet (as string)
- **`availability`** - When the property becomes available
- **`pet_policy`** - Information about pet restrictions
- **`deposit`** - Security deposit amount
- **`lease_terms`** - Length of lease (e.g., "12 month")
- **`utilities`** - What utilities are included/payable
- **`parking`** - Parking information
- **`laundry`** - Laundry facilities information
- **`images`** - Array of image URLs

### Missing Data

Some fields might be `null` if:
- The information wasn't on the page
- The scraper couldn't find it (wrong selectors)
- The property detail page wasn't visited (if there's no `property_link`)

This is normal - not every property page has all information.

## Example: Complete Output

Here's what a minimal but complete output might look like:

```json
{
  "status": "success",
  "timestamp": "2025-10-31T16:00:00.123456",
  "source_url": "https://example-property-site.com/listings",
  "data": {
    "scraped_at": "2025-10-31T16:00:00",
    "url": "https://example-property-site.com/listings",
    "title": "Property Listings | Example Site",
    "description": "We offer a wide range of affordable homes...",
    "contact_info": {
      "phone": ["(555) 555-1234"],
      "email": ["contact@example-site.com"],
      "address": []
    },
    "rental_listings": [
      {
        "address": "123 Main St, City, State 12345",
        "price": "$1,200/month",
        "beds": "2 bed",
        "baths": "1 bath",
        "property_link": "https://example-site.com/listings/...",
        "property_url": "https://example-site.com/listings/...",
        "description": "Cozy 2-bedroom apartment in downtown area...",
        "features": [],
        "amenities": [],
        "square_footage": "950",
        "availability": "Available 12/01/2025",
        "pet_policy": null,
        "deposit": "1200",
        "lease_terms": null,
        "utilities": null,
        "parking": null,
        "laundry": null,
        "images": []
      }
    ],
    "listing_count": 1
  }
}
```

## Working with the Data

### Count Properties

```python
import json

with open('output.json') as f:
    data = json.load(f)

count = data['data']['listing_count']
print(f"Found {count} properties")
```

### List All Addresses

```python
for listing in data['data']['rental_listings']:
    print(listing.get('address', 'No address'))
```

### Find Properties Under $1500

```python
import re

for listing in data['data']['rental_listings']:
    price = listing.get('price', '')
    # Extract number from price string
    match = re.search(r'\$([\d,]+)', price)
    if match:
        price_num = int(match.group(1).replace(',', ''))
        if price_num < 1500:
            print(f"{listing.get('address')}: ${price_num}")
```

### Export to CSV

```python
import json
import csv

with open('output.json') as f:
    data = json.load(f)

with open('properties.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['address', 'price', 'beds', 'baths'])
    writer.writeheader()
    for listing in data['data']['rental_listings']:
        writer.writerow({
            'address': listing.get('address', ''),
            'price': listing.get('price', ''),
            'beds': listing.get('beds', ''),
            'baths': listing.get('baths', '')
        })
```

## Error Output

If something goes wrong, the output will look like:

```json
{
  "status": "error",
  "timestamp": "2025-10-31T16:00:00",
  "error": "Error message here",
  "error_type": "Exception"
}
```

Check the error message to understand what went wrong. Common issues:
- Network connection problems
- Website structure changed (selectors need updating)
- Missing dependencies

## Tips for Using the Data

1. **Save multiple runs** - Name files with timestamps: `output-2025-10-31.json`
2. **Validate the data** - Check `listing_count` matches what you expect
3. **Handle nulls** - Always check if fields exist before using them
4. **Parse prices** - Price is a string, extract numbers if you need to compare
5. **Use the links** - `property_link` lets you visit the original listing

## Next Steps

Now that you understand the output format, you can:
- Write scripts to analyze the data
- Import into spreadsheets or databases
- Create visualizations
- Compare data across multiple scraping runs

The data is in a standard format, so you can use it with any tool that understands JSON!

