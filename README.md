# Tech Buzz Crawler 🚀

A web crawler that aggregates trending tech content from Reddit and YouTube, organized by categories.

## Features

- Scrapes trending tech content from Reddit and YouTube
- Categorizes content into: AI & ML, Big Tech, Electric Vehicles, Gaming & Hardware, Crypto & Fintech
- Clean web interface with thumbnails and engagement metrics
- Auto-refreshes every 5 minutes

## Setup

1. **Install Python dependencies:**
   ```bash
   pip3 install python-dotenv
   ```

2. **Start the backend server:**
   ```bash
   python3 server.py
   ```

3. **Open the web interface:**
   Open `tech_crawler.html` in your browser

## Files

- `server.py` - Backend server that scrapes content and serves API
- `tech_crawler.html` - Frontend web interface
- `README.md` - This file

## Usage

The server runs on `http://localhost:8000` and provides:
- `/api/trending` - JSON API endpoint for trending content
- Static file serving for the HTML interface

The web interface automatically fetches and displays the top 5 trending items per category, sorted by engagement metrics.