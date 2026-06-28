# RSS Feed Finder

A minimal Chrome extension that detects and copies the RSS feed URL from any webpage.

## What it does

Click the extension icon on any page. If the page advertises an RSS feed via a `<link type="application/rss+xml">` tag, the feed URL is displayed and ready to copy.

## Installation

1. Clone or download this repo
2. Open Chrome and go to `chrome://extensions`
3. Enable **Developer mode** (top right)
4. Click **Load unpacked** and select this directory

## Usage

Navigate to any page with an RSS feed (a blog, podcast, news site, etc.) and click the extension icon. Hit **Copy URL** to copy the feed URL to your clipboard.

## Permissions

- `activeTab` — reads the current tab's URL
- `scripting` — fetches the page HTML to detect the RSS link tag
