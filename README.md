# Property Rental Scraper

A Python web scraper that extracts rental property listings from property management websites. This tool automatically navigates websites, handles dynamic JavaScript content, and collects detailed information about available rental properties.

## ⚠️ Disclaimer

**This software is provided for educational purposes only.**

- The author is not responsible for how this code is used
- Web scraping may violate website terms of service
- Always respect robots.txt and website terms
- Use responsibly and ethically
- This tool is not affiliated with any property management company

## What This Tool Does

This scraper:

- **Visits property listing websites** and finds all available rental properties
- **Handles modern websites** that load content dynamically with JavaScript
- **Extracts property details** like addresses, prices, bedrooms, bathrooms, and more
- **Visits individual property pages** to gather additional information
- **Outputs structured JSON data** that's easy to use and analyze

## Quick Start

1. **Set up your computer** - See [SETUP.md](SETUP.md) for detailed installation instructions
2. **Run the scraper** - See [RUNNING_THE_SCRIPT.md](RUNNING_THE_SCRIPT.md) for how to execute it
3. **Understand the output** - See [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md) for what the results look like

## Documentation

This project includes several guides to help you understand and use the scraper:

- **[SETUP.md](SETUP.md)** - How to install Python, dependencies, and get everything working
- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Deep dive into the technology behind the scraper
- **[RUNNING_THE_SCRIPT.md](RUNNING_THE_SCRIPT.md)** - Step-by-step guide to running the scraper and viewing results
- **[OUTPUT_FORMAT.md](OUTPUT_FORMAT.md)** - Understanding the JSON output structure
- **[LEARNING_WITH_CURSOR.md](LEARNING_WITH_CURSOR.md)** - How this project was built using Cursor AI

## Project Structure

```
property-scraper/
├── main.py              # The main scraping script
├── requirements.txt     # Python package dependencies
├── README.md           # This file
├── SETUP.md            # Installation guide
├── HOW_IT_WORKS.md     # Technical deep dive
├── RUNNING_THE_SCRIPT.md # Usage guide
├── OUTPUT_FORMAT.md    # Output documentation
└── LEARNING_WITH_CURSOR.md # Development story
```

## Requirements

- Python 3.8 or higher
- Internet connection
- About 100MB disk space for browser installation

## Example Output

The scraper outputs JSON data like this:

```json
{
  "status": "success",
  "timestamp": "2025-10-31T16:00:00",
  "source_url": "https://example-property-site.com/listings",
  "data": {
    "scraped_at": "2025-10-31T16:00:00",
    "listing_count": 24,
    "rental_listings": [
      {
        "address": "123 Main St, City, State 12345",
        "price": "$1,200/month",
        "beds": "2 bed",
        "baths": "1 bath",
        "property_link": "https://...",
        "availability": "Available 12/01/2025",
        "description": "...",
        "features": ["Hardwood floors", "Updated kitchen"]
      }
    ]
  }
}
```

## Support

If you run into issues:

1. Check [SETUP.md](SETUP.md) to ensure everything is installed correctly
2. Review [RUNNING_THE_SCRIPT.md](RUNNING_THE_SCRIPT.md) for common problems
3. Read error messages carefully - they usually tell you what's wrong

## License

This project is provided as-is for educational and personal use.

## Disclaimer

**This software is provided for educational purposes only.**

- The author is not responsible for how this code is used
- Web scraping may violate website terms of service
- Always respect robots.txt and website terms of service
- Use responsibly and ethically
- This tool is not affiliated with any property management company or organization
- Users are solely responsible for ensuring their use complies with applicable laws and website terms
