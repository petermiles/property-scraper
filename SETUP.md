# Setup Guide

This guide will walk you through setting up your computer to run the property scraper. Don't worry if you're new to Python - we'll take it step by step!

## What You'll Need

- A computer (Mac, Windows, or Linux)
- An internet connection
- About 30 minutes for setup
- Basic familiarity with using a terminal/command prompt

## Step 1: Install Python

### Check if Python is Already Installed

First, let's see if you already have Python installed. Open your terminal (Mac/Linux) or Command Prompt (Windows) and type:

```bash
python3 --version
```

If you see something like `Python 3.8.0` or higher, you're good to go! Skip to Step 2.

### Installing Python

**On Mac:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python 3.x version
3. Run the installer and follow the prompts
4. Make sure to check "Add Python to PATH" if that option appears

**On Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the latest Python 3.x version
3. Run the installer
4. **Important:** Check the box that says "Add Python to PATH" before clicking Install
5. Click "Install Now"

**On Linux:**
Most Linux distributions come with Python pre-installed. If not:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

After installation, verify it worked:

```bash
python3 --version
```

You should see a version number like `Python 3.8.0` or higher.

## Step 2: Install pip (Python Package Manager)

pip usually comes with Python, but let's make sure it's available:

```bash
python3 -m pip --version
```

If you see a version number, you're good! If not, install it:

**Mac/Linux:**
```bash
python3 -m ensurepip --upgrade
```

**Windows:**
pip should have been installed with Python. If not, reinstall Python and make sure to check "pip" during installation.

## Step 3: Install Project Dependencies

Navigate to the project folder in your terminal:

```bash
cd /path/to/property-scraper
```

Now install the required Python packages:

```bash
python3 -m pip install -r requirements.txt
```

This will install:
- **Playwright** - A browser automation tool that lets Python control a web browser
- **PyQuery** - A library for parsing HTML (like jQuery for Python)

## Step 4: Install the Browser

Playwright needs a browser to control. Install Chromium (an open-source browser):

```bash
python3 -m playwright install chromium
```

This downloads about 100MB, so it might take a few minutes depending on your internet speed.

**What's happening here?** Playwright doesn't use your regular browser. Instead, it downloads its own copy of Chromium (the open-source version of Chrome) so it can run automatically without interfering with your normal browsing.

## Step 5: Verify Installation

Let's make sure everything is set up correctly:

```bash
python3 -c "import playwright; print('Playwright installed!')"
python3 -c "from pyquery import PyQuery; print('PyQuery installed!')"
```

If both commands print success messages, you're all set! If you see errors, go back and make sure you completed each step.

## Troubleshooting

### "python3: command not found"

**Mac:** You might need to use `python` instead of `python3`, or install Python from python.org

**Windows:** Make sure you checked "Add Python to PATH" during installation. You may need to restart your terminal.

### "pip: command not found"

Try using `python3 -m pip` instead of just `pip`. This tells Python to run pip as a module.

### "Permission denied" errors

**Mac/Linux:** You might need to use `sudo` (but try without first):
```bash
sudo python3 -m pip install -r requirements.txt
```

**Windows:** Make sure you're running Command Prompt as Administrator if needed.

### Playwright installation fails

Make sure you have a stable internet connection. The browser download can take a few minutes. If it fails, try:

```bash
python3 -m playwright install chromium --with-deps
```

This installs additional system dependencies that might be needed.

## Next Steps

Once everything is installed, you're ready to run the scraper! Head over to [RUNNING_THE_SCRIPT.md](RUNNING_THE_SCRIPT.md) to learn how to use it.

## Understanding What We Just Installed

- **Python** - The programming language that runs our scraper
- **pip** - Python's package manager (like an app store for Python code)
- **Playwright** - Lets Python control a browser automatically
- **PyQuery** - Helps extract information from web pages
- **Chromium** - The browser that Playwright controls

Don't worry if this seems like a lot - once it's set up, you'll rarely need to do it again!

