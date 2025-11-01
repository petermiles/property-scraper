# Property Rental Scraper

A Python web scraper that extracts rental property listings from property management websites. This tool automatically navigates websites, handles dynamic JavaScript content, and collects detailed information about available rental properties.

## ⚠️ Important Disclaimers

### Educational Purpose Only

**This software is provided for educational purposes only.**

- The author is not responsible for how this code is used
- Web scraping may violate website terms of service
- Always respect robots.txt and website terms of service
- Use responsibly and ethically
- This tool is not affiliated with any property management company or organization
- Users are solely responsible for ensuring their use complies with applicable laws and website terms

### AI-Generated Code Warning

**⚠️ CRITICAL: The accuracy of this script has NOT been verified.**

This project was built using Cursor AI, an AI-powered code assistant. While AI tools like Cursor are incredibly helpful, **you should never blindly trust AI-generated code or data**.

**Why You Must Verify:**

1. **AI makes mistakes** - Code may have bugs, logic errors, or security vulnerabilities
2. **AI doesn't test** - Generated code often hasn't been thoroughly tested
3. **AI can hallucinate** - Sometimes AI generates code that looks correct but doesn't work
4. **Context matters** - AI might misunderstand requirements or use outdated patterns
5. **Data accuracy** - Scraped data may be incomplete, incorrect, or missing fields

**What You Should Do:**

- ✅ **Test the code** before using it for anything important
- ✅ **Review the logic** to understand what it's doing
- ✅ **Verify the output** - Check if scraped data matches what you see on the website
- ✅ **Run it multiple times** - AI code may have edge cases that fail intermittently
- ✅ **Read error messages** - If something breaks, understand why before fixing
- ✅ **Compare results** - Manually verify a few properties match the website

**Remember:** AI is a powerful tool, but you are responsible for verifying everything it produces. Trust, but verify!

**See [LEARNING_WITH_CURSOR.md](LEARNING_WITH_CURSOR.md) for more on the dangers of not verifying AI code.**

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
- **[CURSOR_CHAT_LOG.md](CURSOR_CHAT_LOG.md)** - Complete conversation log from Cursor AI that created this entire project

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
├── LEARNING_WITH_CURSOR.md # Development story
└── CURSOR_CHAT_LOG.md  # Complete Cursor AI conversation log
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
