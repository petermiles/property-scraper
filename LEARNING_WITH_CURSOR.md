# Learning with Cursor: How This Project Was Built

This document explains how Cursor AI was used to build this scraper, giving you insight into modern AI-assisted development.

## ⚠️ Critical Lesson: Trust, But Verify

**Before we dive in, this is the most important lesson you'll learn:**

**Never blindly trust AI-generated code.** This project was built with Cursor AI, and while it's incredibly powerful, AI tools can:

- Generate code with bugs or logic errors
- Create code that looks correct but doesn't work
- Miss edge cases or security vulnerabilities
- Produce data that's incomplete or inaccurate
- Use outdated patterns or misunderstand requirements

**Always verify:**
- ✅ Test the code yourself
- ✅ Review the logic
- ✅ Check the output accuracy
- ✅ Run it multiple times
- ✅ Understand what it's doing

AI is a powerful assistant, but **you are responsible for verifying everything it produces.** This is true for Cursor, ChatGPT, GitHub Copilot, or any AI tool.

## What is Cursor?

Cursor is an AI-powered code editor that helps developers write code faster and more effectively. Think of it as having a coding assistant that understands context and can help you build entire projects through conversation.

## The Development Journey

### Starting Point: A Simple Request

The project began with a straightforward request: "Scrape rental property information from a website."

Traditional approach would have been:

1. Research web scraping libraries
2. Write code from scratch
3. Debug issues manually
4. Iterate slowly

With Cursor, the process became:

1. Describe what you want
2. Cursor suggests the approach
3. Iterate through conversation
4. Build incrementally with AI assistance

### Key Features Used

#### 1. **Natural Language to Code**

Instead of searching documentation, you can just ask:

> "How do I handle JavaScript-rendered content in Python?"

Cursor provided working code examples using Playwright, explaining why it's needed for modern websites.

#### 2. **Iterative Refinement**

The scraper evolved through multiple iterations:

**Version 1:** Basic HTML scraping

- Problem: Missed dynamically loaded content
- Solution: Added Playwright for JavaScript execution

**Version 2:** Simple scrolling

- Problem: Only found first 24 properties
- Solution: Implemented incremental scrolling strategy

**Version 3:** Slow performance

- Problem: Visiting each property page sequentially took too long
- Solution: Added parallel processing with asyncio

**Version 4:** Still missing properties

- Problem: Virtual scrolling meant properties weren't all visible
- Solution: Scroll to bottom first, then back up to capture all items

Each iteration was guided by conversation with Cursor, explaining problems and getting solutions.

#### 3. **Error Handling**

When errors occurred, Cursor helped:

- Identify the issue
- Explain what went wrong
- Provide fixes
- Add better error handling

For example, when parallel scraping failed, Cursor helped add proper null checks and error handling.

#### 4. **Code Explanation**

Cursor can explain complex code sections, making it educational:

```python
# Cursor explained: "This semaphore limits concurrent requests to 5,
# preventing us from overwhelming the server while still being faster
# than sequential requests."
semaphore = asyncio.Semaphore(max_concurrent)
```

## What Made This Possible

### 1. **Context Awareness**

Cursor understands:

- The entire codebase
- What you're trying to accomplish
- Common patterns and best practices
- Error messages and how to fix them

### 2. **Multiple Approaches**

When one approach didn't work, Cursor suggested alternatives:

- Different scrolling strategies
- Alternative HTML parsing methods
- Various ways to handle async operations

### 3. **Learning While Building**

Instead of just copying code, Cursor explained:

- **Why** each approach works
- **What** each library does
- **How** the pieces fit together

## The Iterative Process

### Conversation Example

**User:** "The scraper only finds 24 properties but the page says there are 67."

**Cursor:** "This suggests virtual scrolling. The page only renders visible items. Let's scroll to multiple positions and check what's visible at each."

**User:** "Still only 24."

**Cursor:** "Let's try scrolling to the bottom first to trigger loading all items, then scroll back up to capture them as they render."

**User:** "How do I make it faster?"

**Cursor:** "We can visit property detail pages in parallel using asyncio. Here's how..."

### Benefits of This Approach

1. **Faster Development** - Built in hours instead of days
2. **Better Solutions** - Multiple approaches considered
3. **Learning** - Understand why solutions work
4. **Documentation** - Explanations become comments

## Key Technologies Discovered

Through the development process, Cursor introduced:

- **Playwright** - For handling JavaScript-heavy sites
- **PyQuery** - For easy HTML parsing
- **asyncio** - For parallel processing
- **Virtual scrolling** - Understanding modern web patterns

Each technology was explained in context, making the learning more effective.

## Patterns Used

### 1. **Progressive Enhancement**

Started simple, added complexity as needed:

- Basic scraping → JavaScript support
- Sequential → Parallel processing
- Single page → Multiple pages

### 2. **Error-First Development**

Built error handling early:

- Try/except blocks
- Graceful degradation
- Helpful error messages

### 3. **User Feedback**

Added progress logging so users know it's working:

- Timestamps
- Progress indicators
- Clear status messages

## What You Can Learn

### For Beginners

1. **Start Simple** - Build a basic version first
2. **Iterate** - Improve incrementally
3. **Ask Questions** - Understanding is as important as code
4. **Read Error Messages** - They usually tell you what's wrong

### For More Experienced Developers

1. **AI as Pair Programming** - Use it like a coding partner
2. **Rapid Prototyping** - Try multiple approaches quickly
3. **Documentation** - AI explanations become documentation
4. **Best Practices** - AI suggests modern patterns

## Limitations and Considerations

### What AI Helps With

- ✅ Generating boilerplate code
- ✅ Explaining concepts
- ✅ Suggesting approaches
- ✅ Debugging common issues
- ✅ Finding relevant libraries

### What You Still Need

- ❌ Understanding the problem domain
- ❌ Making architectural decisions
- ❌ Testing and validation
- ❌ Understanding business requirements
- ❌ Critical thinking about solutions

## The Result

This project demonstrates:

- Modern web scraping techniques
- Handling dynamic content
- Parallel processing
- Error handling
- User-friendly output

All built through iterative conversation with Cursor, making the development process both efficient and educational.

## The Dangers of Not Verifying AI Code

### Real-World Consequences

When you don't verify AI-generated code, you risk:

1. **Security Vulnerabilities**
   - AI might generate code that exposes sensitive data
   - Missing input validation can lead to injection attacks
   - Authentication/authorization might be implemented incorrectly

2. **Data Loss or Corruption**
   - Code might delete or modify data incorrectly
   - Race conditions in concurrent code
   - Missing error handling can cause silent failures

3. **Financial Loss**
   - Bugs in payment processing code
   - Incorrect calculations in financial systems
   - Automation that makes wrong decisions

4. **Legal Issues**
   - Code that violates privacy laws (GDPR, CCPA)
   - Scraping that violates terms of service
   - Missing consent mechanisms

5. **Wasted Time**
   - Code that doesn't work and needs complete rewrite
   - Debugging issues that could have been caught early
   - Relying on incorrect data for decisions

### The Verification Process

**Every time Cursor generates code, follow these steps:**

1. **Read the code** - Don't just copy-paste
2. **Understand the logic** - What is it trying to do?
3. **Test immediately** - Run it with simple inputs
4. **Check edge cases** - What happens with empty data? Invalid input?
5. **Review for security** - Are there any obvious vulnerabilities?
6. **Verify output** - Does the result match expectations?
7. **Test in production-like environment** - Don't deploy untested code

### Example: Why Verification Matters

During the development of this scraper, Cursor generated code that:

- Initially missed most properties (only found 14 out of 68)
- Had bugs in scrolling logic that required multiple iterations
- Needed manual fixes for address extraction patterns
- Required verification that all 68 properties were actually captured

**Without verification, we would have had incorrect data.**

## Trying It Yourself

If you want to use Cursor for your own projects:

1. **Install Cursor** - [cursor.sh](https://cursor.sh)
2. **Start with a clear goal** - Know what you want to build
3. **Describe problems** - Explain what's not working
4. **Ask for explanations** - Don't just accept code, understand it
5. **Iterate** - Improve incrementally

## Ideas for Community Tenant Organizations

Here are 5 feature ideas you could build using Cursor that would be valuable for tenant advocacy and assistance:

### 1. **Rent Price Tracker**

**What it does:** Track rental prices over time to identify trends and help tenants understand if rents are fair.

**How to build with Cursor:**

```
"I want to save scraped rental data to a database with timestamps,
then create a script that compares current prices to prices from
30/60/90 days ago and generates a report showing price trends."
```

**Features:**

- Store each scraping run with a timestamp
- Calculate average rent by neighborhood/bedroom count
- Generate graphs showing price trends
- Alert when prices change significantly

**Why it's useful:** Helps tenants negotiate rent or understand market trends.

### 2. **Affordability Calculator**

**What it does:** Calculate which properties are affordable based on income and typical rental ratios.

**How to build with Cursor:**

```
"Create a script that takes income as input, applies standard
affordability ratios (like 30% of income), and filters the scraped
properties to show only those within budget. Also flag properties
that might be too good to be true."
```

**Features:**

- Input: Annual/monthly income
- Calculate max affordable rent (30% rule)
- Filter properties by price range
- Flag suspiciously low prices
- Show percentage of listings that are affordable

**Why it's useful:** Helps tenants quickly find properties they can actually afford.

### 3. **Pet-Friendly Property Finder**

**What it does:** Filter and highlight properties that allow pets, with details about pet policies.

**How to build with Cursor:**

```
"Modify the scraper to better extract pet policy information, then
create a separate script that filters properties by pet-friendliness
and extracts details like pet deposits, weight limits, breed restrictions."
```

**Features:**

- Extract pet policy details (cats allowed, dogs allowed, etc.)
- Show pet deposits if mentioned
- Filter by pet type (cats only, dogs only, both)
- Generate a pet-friendly properties report

**Why it's useful:** Finding pet-friendly rentals is hard - this makes it easier.

### 4. **Rental Comparison Dashboard**

**What it does:** Compare multiple properties side-by-side with all key metrics.

**How to build with Cursor:**

```
"Create a web dashboard (using Flask or simple HTML) that displays
scraped properties in a table format with sortable columns. Allow
users to select properties to compare side-by-side showing price
per square foot, amenities, location, etc."
```

**Features:**

- Sortable table of all properties
- Side-by-side comparison view
- Calculate price per square foot
- Filter by any field (price, beds, location)
- Export comparison to PDF

**Why it's useful:** Makes it easy to compare options and make informed decisions.

### 5. **Housing Availability Alert System**

**What it does:** Monitor for new properties or price drops and send alerts.

**How to build with Cursor:**

```
"Create a system that runs the scraper daily, compares results to
previous runs, identifies new properties or significant price changes,
and sends email alerts to subscribers who are looking for specific
criteria (like 2-bedroom under $1200 in a specific area)."
```

**Features:**

- Run scraper on a schedule (daily/weekly)
- Compare new data to previous runs
- Identify new listings and price changes
- User preferences (beds, baths, max price, location)
- Email notifications for matches

**Why it's useful:** Rentals go fast - alerts help tenants act quickly.

## How to Add a New Site

Want to scrape a different property management website? Here's how to use Cursor to adapt the scraper:

### Step 1: Provide Context to Cursor

Start a conversation in Cursor like this:

```
"I want to scrape rental listings from [WEBSITE_URL].
I already have a scraper that works for one property management site.
Can you help me adapt it for this new site?

The site structure might be different, so we'll need to:
1. Update the URL
2. Adjust the selectors for finding property links
3. Update how we extract address, price, beds, baths
4. Possibly adjust scrolling behavior if they use different virtualization

Let's start by examining the new site structure."
```

### Step 2: Get Initial Analysis

Cursor can help you inspect the new site:

```
"Can you help me write a simple script that loads [NEW_URL]
with Playwright and shows me:
- What HTML structure they use for property listings
- How properties are identified (what makes a property link unique)
- Whether they use virtual scrolling
- What selectors might work for addresses, prices, etc."
```

### Step 3: Iterative Adaptation

Work through each part:

**Updating Selectors:**

```
"The property links on this site use [PATTERN] instead of 'listable_uid'.
Can you update the scraper to find links using [NEW_PATTERN]?
For example, they might use 'property-id' or '/listing/' in the URL."
```

**Extracting Data:**

```
"On this site, the address is in a <h3> with class 'property-address'
instead of the patterns we're currently using. Can you add this selector
to the address extraction logic?"
```

**Handling Differences:**

```
"This site doesn't use virtual scrolling - all properties load at once.
Can you remove the scrolling logic and just extract all properties
from the initial page load?"
```

### Step 4: Testing and Refinement

```
"I'm getting [ERROR/MISSING_DATA]. Can you help debug why the scraper
isn't finding [SPECIFIC_FIELD]? Here's what I'm seeing in the HTML: [PASTE_RELEVANT_HTML]"
```

### Prompt Template for Adding New Sites

Copy and customize this template:

```
I want to adapt my property scraper for a new website: [URL]

Current scraper works for: [EXAMPLE_URL]

For the new site, I need help with:

1. **Finding property links:**
   - Current method: Looking for links with 'listable_uid' in href
   - New site pattern: [DESCRIBE WHAT YOU SEE]
   - Question: What selector/pattern should I use?

2. **Extracting basic info (address, price, beds, baths):**
   - Can you help me inspect the HTML structure?
   - What CSS selectors would work?

3. **Property detail pages:**
   - Does each property have a detail page?
   - What's the URL pattern?
   - What additional info is available there?

4. **Scrolling/virtualization:**
   - Does the site load all properties at once?
   - Or does it use virtual scrolling/infinite scroll?
   - Do I need to click "Load More" buttons?

5. **Any special considerations:**
   - Rate limiting?
   - Authentication required?
   - Different page structure?

Let's start by examining the site structure together.
```

### Step-by-Step Instructions

1. **Open the target website** in your browser
2. **Inspect the page** - Right-click → Inspect Element
3. **Look for patterns:**
   - How are properties listed? (cards, list items, etc.)
   - What makes property links unique?
   - Where is the address/price displayed?
4. **Ask Cursor specific questions:**
   - "How do I select all property cards on this page?"
   - "This site uses `data-property-id` - how do I extract that?"
   - "The price is in a `<span class='rent-price'>` - what selector?"
5. **Test incrementally:**
   - Update one part at a time
   - Test each change
   - Ask Cursor to explain what changed

### Common Patterns You'll Encounter

**Different Link Patterns:**

- `listable_uid` → `property_id`, `listing_id`, `unit_id`
- Query parameters → Path segments (`/property/12345` instead of `?id=12345`)

**Different HTML Structures:**

- Cards vs. table rows vs. list items
- Different class names for the same information
- Nested structures (property in a card, card in a container)

**Different Loading Behaviors:**

- All at once (easy!)
- Infinite scroll (needs scrolling)
- Pagination (needs clicking "Next")
- JavaScript API calls (might need to intercept network requests)

### Example: Adapting for a New Site

Here's how a conversation might go:

**You:** "I want to scrape https://example-properties.com/listings"

**Cursor:** "Let me help you adapt the scraper. First, let's create a simple inspection script to see the structure."

**You:** "I see properties are in `<div class='listing-card'>` elements. Each has a link like `/property/12345`"

**Cursor:** "Great! Let's update the selector from `a[href*="listable_uid"]` to `div.listing-card a[href*="/property/"]`. Here's the change..."

**You:** "The price is in `<span class='monthly-rent'>$1,200</span>`. Current selector isn't finding it."

**Cursor:** "Let's add `.monthly-rent` to the price selectors. Here's how to update the extraction logic..."

**You:** "Perfect! Now how do I get the property ID from the URL `/property/12345`?"

**Cursor:** "You can extract it with a regex: `r'/property/(\d+)'`. Here's how to add that..."

### Tips for Success

1. **Start small** - Get basic extraction working first
2. **Test frequently** - Run the scraper after each change
3. **Ask for explanations** - Understand why selectors work
4. **Save working versions** - Comment out old code, don't delete it
5. **Handle edge cases** - Ask Cursor: "What if a property doesn't have a price?"

### Getting Help from Cursor

If something isn't working:

```
"I'm trying to extract [FIELD] from [SITE], but I'm getting [RESULT/ERROR].
The HTML structure is: [PASTE_HTML]
Can you help me find the right selector?"
```

Cursor can:

- Suggest better selectors
- Explain why current selectors fail
- Provide alternative approaches
- Help debug extraction logic

## Final Thoughts

AI-assisted development isn't about replacing coding skills - it's about:

- **Amplifying** your abilities
- **Accelerating** learning
- **Enabling** more ambitious projects
- **Teaching** while building

This scraper project showcases how AI can help you build complex tools while learning the underlying concepts. The result is both functional code and deeper understanding of web scraping, async programming, and modern web technologies.

With Cursor, you can:

- Build features for your community
- Adapt tools for different websites
- Learn by doing
- Create solutions that matter

Happy coding! 🚀
