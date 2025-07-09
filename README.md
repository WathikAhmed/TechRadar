# Tech Buzz Crawler 🚀

A web crawler that aggregates trending tech content from YouTube, organized by categories.

## Features

- Scrapes trending tech content from YouTube
- Categorizes content into: AI & ML, Big Tech, Electric Vehicles, Gaming & Hardware, Crypto & Fintech
- Clean web interface with thumbnails and engagement metrics
- **AI Script Generation** - Generate scripts for any video using Google Gemini AI
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

## Script Generation

Each trending video has two script generation buttons powered by Google Gemini AI:

### 📱 TikTok Script
- Creates a 60-second short-form video script
- Optimized for high engagement and watch retention
- Casual, punchy tone with strong hooks
- Includes title suggestions, description, hashtags, and pinned comment

### 🎥 YouTube Script
- Creates a 5-10 minute long-form video script
- Educational and informative content structure
- Natural, engaging tone with clear explanations
- Includes intro, main content, conclusion, and call-to-action
- Provides title options, description, hashtags, and discussion starters

Both scripts analyze the original video's title, URL, and transcript (when available) to create relevant, contextual content.