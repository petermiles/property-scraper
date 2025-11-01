# Running the Script

This guide will show you exactly how to run the scraper and view the results.

## Prerequisites

Make sure you've completed the setup steps in [SETUP.md](SETUP.md) before proceeding.

## Basic Usage

### Step 1: Open Your Terminal

**Mac/Linux:**
- Open Terminal (Applications > Utilities > Terminal)

**Windows:**
- Open Command Prompt or PowerShell
- Press `Win + R`, type `cmd`, press Enter

### Step 2: Navigate to the Project Folder

Change to the directory where you saved the scraper:

```bash
cd /path/to/property-scraper
```

**Tip:** You can drag and drop the folder into your terminal window (on Mac/Linux) to get the path automatically.

### Step 3: Run the Script

Simply run:

```bash
python3 main.py
```

That's it! The scraper will start working.

## Understanding the Output

When you run the script, you'll see two types of output:

### 1. Progress Messages (to stderr)

These appear in your terminal and show what's happening:

```
[16:00:00] ========================================
[16:00:00] Starting rental scraping for: https://example-property-site.com/listings
[16:00:00] ========================================
[16:00:05] Starting incremental property collection...
[16:00:05] Waiting for initial content to load...
[16:00:07] Target: 67 properties
[16:00:07] Starting multi-position scroll strategy...
[16:00:10] Found property #1 at scroll 0px...
[16:00:15] Found property #5 at scroll 0px...
...
[16:05:30] ✓ Scraping completed! Found 24 listings
```

**What you're seeing:**
- Timestamps showing when each step happens
- Progress updates as properties are found
- Completion messages

### 2. JSON Results (to stdout)

The actual data is printed as JSON at the end. This is what you'll use!

## Saving the Output

### Save Everything (including progress messages)

```bash
python3 main.py > output.json 2>&1
```

This saves both the JSON results AND the progress messages to `output.json`.

### Save Only the JSON Results

```bash
python3 main.py 2>/dev/null > output.json
```

On Windows PowerShell:
```powershell
python3 main.py 2>$null > output.json
```

This saves only the clean JSON data, filtering out the progress messages.

### View Results in Terminal

If you just want to see the results without saving:

```bash
python3 main.py 2>/dev/null | python3 -m json.tool
```

This:
1. Runs the scraper
2. Filters out progress messages (`2>/dev/null`)
3. Formats the JSON nicely (`json.tool`)

## How Long Does It Take?

The scraper typically takes:
- **2-5 minutes** to find all properties on the listing page
- **5-15 minutes** to visit each property's detail page (if many properties)
- **Total: 10-20 minutes** for a full scrape with 20-30 properties

Progress messages will keep you updated, so you know it's working!

## Viewing the Results

### Option 1: View in a Text Editor

Open `output.json` in any text editor:
- **Mac:** TextEdit, VS Code, or any editor
- **Windows:** Notepad, VS Code, or any editor
- **Linux:** nano, vim, VS Code, or any editor

### Option 2: Format and View in Terminal

```bash
cat output.json | python3 -m json.tool | less
```

This formats the JSON nicely and lets you scroll through it.

### Option 3: Use an Online JSON Viewer

1. Copy the contents of `output.json`
2. Paste into [jsonviewer.stack.hu](https://jsonviewer.stack.hu/) or [jsonformatter.org](https://jsonformatter.org/)
3. Click "Format" to see it nicely organized

### Option 4: Use Python to Explore

Create a simple script to explore the data:

```python
import json

with open('output.json', 'r') as f:
    data = json.load(f)

# Print number of listings
print(f"Found {data['data']['listing_count']} properties")

# Print first property
if data['data']['rental_listings']:
    first = data['data']['rental_listings'][0]
    print(f"\nFirst property:")
    print(f"  Address: {first.get('address', 'N/A')}")
    print(f"  Price: {first.get('price', 'N/A')}")
    print(f"  Beds/Baths: {first.get('beds', 'N/A')} / {first.get('baths', 'N/A')}")
```

Save this as `view_results.py` and run:

```bash
python3 view_results.py
```

## Understanding the Progress Messages

The progress messages tell you what's happening:

- `Starting rental scraping...` - The scraper has begun
- `Target: X properties` - Found how many properties should exist
- `Found property #X...` - Successfully discovered a new property
- `Scraping: [address]...` - Visiting a property's detail page
- `✓ Completed: [address]...` - Finished getting details for a property
- `✓ Scraping completed!` - All done!

## Common Issues

### "ModuleNotFoundError: No module named 'playwright'"

You need to install dependencies:
```bash
python3 -m pip install -r requirements.txt
python3 -m playwright install chromium
```

### "playwright install chromium" takes forever

The browser download is about 100MB. This is normal - just wait for it to finish. A slow internet connection will make this take longer.

### Script seems stuck

The scraper is probably working! Check the progress messages:
- If you see "Found property #X", it's working
- If you see "Scraping: [address]", it's visiting detail pages
- Sometimes it pauses for a few seconds while waiting for pages to load

If it's been stuck for more than 10 minutes with no new messages, something might be wrong. Check your internet connection.

### Too much output in terminal

The progress messages can be verbose. Redirect them:

```bash
python3 main.py 2>progress.log >output.json
```

This saves progress to `progress.log` and results to `output.json`.

## Customizing the Script

Want to scrape a different website? Edit `main.py` and change this line:

```python
url = "https://example-property-site.com/listings"
```

Change it to any URL you want to scrape (though the selectors might need adjustment for different sites). See [LEARNING_WITH_CURSOR.md](LEARNING_WITH_CURSOR.md) for a guide on adapting the scraper for new sites.

## ⚠️ Verify Your Results

**IMPORTANT:** This script was built with AI assistance and its accuracy has not been verified.

**Before trusting the output, you should:**

1. **Spot check manually** - Open the website and verify a few properties match
2. **Check the count** - Does `listing_count` match what the website shows?
3. **Verify fields** - Are addresses, prices, and other details correct?
4. **Compare formats** - Does the output structure make sense?
5. **Run multiple times** - Are results consistent?

**Remember:** AI-generated code can have bugs. Always verify data before using it for important decisions.

## Next Steps

Once you have the output, check out [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md) to understand the structure of the data you've collected.

## Tips for Success

1. **Be patient** - Scraping takes time, especially for many properties
2. **Check progress messages** - They tell you it's working
3. **Save the output** - Always save to a file so you don't lose the data
4. **Run during off-peak hours** - Websites may respond faster when less busy
5. **Don't run too frequently** - Be respectful of the website's resources

Happy scraping! 🎉

