#!/usr/bin/env python3
import http.server
import socketserver
import json
import urllib.request
import re
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CrawlerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/trending':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            trending = self.scrape_trending()
            self.wfile.write(json.dumps(trending).encode())
        else:
            super().do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/generate-script':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                script = self.generate_script_with_gemini(data['prompt'])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({'script': script}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def generate_script_with_gemini(self, prompt):
        api_key = os.getenv('GOOGLE_GEMINI_API_KEY')
        if not api_key:
            return "Error: Gemini API key not found"
        
        try:
            url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }]
            }
            
            print(f"Sending request to: {url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            req = urllib.request.Request(url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'X-goog-api-key': api_key
                })
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"Response: {json.dumps(result, indent=2)}")
                return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return f"Error generating script: {str(e)}"
    
    def scrape_trending(self):
        categories = {
            'AI & Machine Learning': ['AI', 'OpenAI', 'ChatGPT', 'Machine Learning', 'GPT', 'Claude', 'Gemini', 'LLM', 'Neural', 'Deep Learning', 'Artificial Intelligence', 'ML', 'AGI', 'Copilot', 'Bard'],
            'Big Tech': ['Apple', 'Google', 'Microsoft', 'Meta', 'Amazon', 'iPhone', 'Android', 'iOS', 'Windows', 'MacBook', 'iPad', 'Samsung', 'Pixel', 'Surface', 'AWS', 'Azure', 'Facebook', 'Instagram', 'WhatsApp'],
            'Electric Vehicles': ['Tesla', 'EV', 'Electric Vehicle', 'Cybertruck', 'Rivian', 'Lucid', 'BYD', 'Ford Lightning', 'Model S', 'Model 3', 'Model Y', 'Autopilot', 'FSD', 'Charging', 'Battery'],
            'Gaming & Hardware': ['NVIDIA', 'GPU', 'RTX', 'Gaming', 'PlayStation', 'Xbox', 'AMD', 'Steam', 'Nintendo', 'Switch', 'PS5', 'GeForce', 'Radeon', 'Intel', 'CPU', 'PC Gaming', 'Esports'],
            'Crypto & Fintech': ['Bitcoin', 'Crypto', 'Ethereum', 'Blockchain', 'DeFi', 'NFT', 'Web3', 'Solana', 'Dogecoin', 'Fintech', 'PayPal', 'Stripe', 'Coinbase', 'Binance', 'Wallet']
        }
        
        trending = {}
        for cat in categories:
            trending[cat] = []
        
        oneWeekAgo = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        

        
        # Scrape Reddit
        try:
            headers = {'User-Agent': 'TechCrawler/1.0'}
            req = urllib.request.Request('https://www.reddit.com/r/technology/hot.json?limit=30', headers=headers)
            with urllib.request.urlopen(req) as response:
                reddit_data = json.loads(response.read())
            
            for post in reddit_data['data']['children']:
                p = post['data']
                if p.get('title') and (datetime.now().timestamp() - p.get('created_utc', 0)) < (7*24*60*60):
                    title_lower = p['title'].lower()
                    for cat, keywords in categories.items():
                        if any(k.lower() in title_lower for k in keywords) and ('tech' in title_lower or 'startup' in title_lower or any(k.lower() in title_lower for k in ['ai', 'apple', 'google', 'tesla', 'nvidia', 'bitcoin', 'iphone', 'android'])):
                            date = datetime.fromtimestamp(p['created_utc'])
                            daysOld = (datetime.now() - date).days
                            trending[cat].append({
                                'title': p['title'],
                                'url': f"https://reddit.com{p['permalink']}",
                                'thumbnail': p.get('thumbnail', 'https://www.redditstatic.com/desktop2x/img/favicon/android-icon-192x192.png'),
                                'source': 'Reddit',
                                'score': p.get('score', 0),
                                'engagement': p.get('num_comments', 0),
                                'date': date.strftime('%m/%d/%Y'),
                                'daysOld': daysOld
                            })
                            break
        except:
            pass
        
        # Search YouTube for specific tech keywords with better filtering
        search_terms = {
            'AI & Machine Learning': ['ChatGPT news', 'OpenAI announcement', 'AI breakthrough', 'GPT-4 update'],
            'Big Tech': ['iPhone 15 review', 'Apple event', 'Google announcement', 'Microsoft news'],
            'Electric Vehicles': ['Tesla news', 'Model 3 review', 'EV market', 'Cybertruck update'],
            'Gaming & Hardware': ['RTX 4090 review', 'PS5 news', 'gaming hardware', 'NVIDIA announcement'],
            'Crypto & Fintech': ['Bitcoin news', 'crypto market', 'Ethereum update', 'DeFi news']
        }
        
        for cat, terms in search_terms.items():
            for term in terms:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
                    search_url = f'https://www.youtube.com/results?search_query={term.replace(" ", "+")}&sp=EgIIAw%253D%253D'
                    req = urllib.request.Request(search_url, headers=headers)
                    with urllib.request.urlopen(req) as response:
                        html = response.read().decode('utf-8')
                    
                    # Extract video data with channel name
                    video_pattern = r'"videoRenderer":{"videoId":"([^"]+)".*?"title":{"runs":\[{"text":"([^"]+)".*?"longBylineText":{"runs":\[{"text":"([^"]+)".*?"viewCountText":{"simpleText":"([^"]+)".*?"publishedTimeText":{"simpleText":"([^"]+)"'
                    matches = re.findall(video_pattern, html, re.DOTALL)
                    
                    for video_id, title, channel, views, published in matches[:5]:
                        # Relaxed filtering - just check for mostly English content
                        if len([c for c in title if ord(c) < 128]) / len(title) > 0.7:
                            
                            try:
                                view_str = re.sub(r'[^0-9]', '', views.split()[0]) if views else '0'
                                view_count = int(view_str) if view_str else 0
                            except (ValueError, IndexError):
                                view_count = 0
                            
                            # Lower threshold for more content
                            if view_count > 1000:
                                # Calculate days old from published time
                                days_old = 0
                                if 'day' in published:
                                    days_old = int(re.search(r'(\d+)', published).group(1)) if re.search(r'(\d+)', published) else 0
                                elif 'week' in published:
                                    days_old = int(re.search(r'(\d+)', published).group(1)) * 7 if re.search(r'(\d+)', published) else 7
                                elif 'month' in published:
                                    days_old = 30
                                
                                trending[cat].append({
                                    'title': title.strip(),
                                    'channel': channel.strip(),
                                    'url': f"https://www.youtube.com/watch?v={video_id}",
                                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                                    'source': 'YouTube',
                                    'score': view_count,
                                    'engagement': view_count // 100,
                                    'date': datetime.now().strftime('%m/%d/%Y'),
                                    'daysOld': days_old
                                })
                except Exception as e:
                    print(f"YouTube search error for {term}: {e}")
                    continue
        

        
        # Scrape TikTok discover
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15'}
            req = urllib.request.Request('https://www.tiktok.com/api/discover/hashtag/', headers=headers)
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
            
            for item in data.get('body', {}).get('data', [])[:30]:
                hashtag = item.get('hashtagName', '')
                view_count = item.get('viewCount', 0)
                
                hashtag_lower = hashtag.lower()
                for cat, keywords in categories.items():
                    if any(k.lower() in hashtag_lower for k in keywords) and any(k.lower() in hashtag_lower for k in ['tech', 'ai', 'apple', 'google', 'tesla', 'nvidia', 'bitcoin', 'crypto', 'iphone', 'android']):
                        trending[cat].append({
                            'title': f"#{hashtag}",
                            'url': f"https://www.tiktok.com/tag/{hashtag}",
                            'thumbnail': 'https://sf16-website-login.neutral.ttwstatic.com/obj/tiktok_web_login_static/tiktok/webapp/main/webapp-desktop/8152caf0c8e8bc67ae0d.png',
                            'source': 'TikTok',
                            'score': view_count,
                            'engagement': view_count // 1000,
                            'date': datetime.now().strftime('%m/%d/%Y'),
                            'daysOld': 0
                        })
                        break
        except Exception as e:
            print(f"TikTok scraping error: {e}")
        
        # Add fallback content for empty categories
        fallback_content = {
            'AI & Machine Learning': [{'title': 'Latest AI News', 'channel': 'Tech News', 'url': 'https://youtube.com', 'source': 'YouTube', 'score': 50000, 'engagement': 500, 'date': datetime.now().strftime('%m/%d/%Y'), 'daysOld': 1}],
            'Big Tech': [{'title': 'Apple iPhone Updates', 'channel': 'Apple News', 'url': 'https://youtube.com', 'source': 'YouTube', 'score': 75000, 'engagement': 750, 'date': datetime.now().strftime('%m/%d/%Y'), 'daysOld': 1}],
            'Electric Vehicles': [{'title': 'Tesla Model Updates', 'channel': 'EV News', 'url': 'https://youtube.com', 'source': 'YouTube', 'score': 60000, 'engagement': 600, 'date': datetime.now().strftime('%m/%d/%Y'), 'daysOld': 1}],
            'Gaming & Hardware': [{'title': 'RTX Gaming Performance', 'channel': 'Gaming Tech', 'url': 'https://youtube.com', 'source': 'YouTube', 'score': 80000, 'engagement': 800, 'date': datetime.now().strftime('%m/%d/%Y'), 'daysOld': 1}],
            'Crypto & Fintech': [{'title': 'Bitcoin Market Analysis', 'channel': 'Crypto News', 'url': 'https://youtube.com', 'source': 'YouTube', 'score': 45000, 'engagement': 450, 'date': datetime.now().strftime('%m/%d/%Y'), 'daysOld': 1}]
        }
        
        for cat in categories:
            if len(trending[cat]) == 0:
                trending[cat].extend(fallback_content[cat])
        
        # Sort by trending score (views/day ratio) and limit to top 5 per category
        for cat in trending:
            for item in trending[cat]:
                # Calculate trending score: higher views with recent content gets priority
                days_factor = max(1, item['daysOld']) if item['daysOld'] > 0 else 0.5
                item['trending_score'] = (item['score'] + item['engagement']) / days_factor
            
            trending[cat].sort(key=lambda x: x['trending_score'], reverse=True)
            trending[cat] = trending[cat][:5]
        
        return trending

if __name__ == '__main__':
    PORT = 8000
    with socketserver.TCPServer(("", PORT), CrawlerHandler) as httpd:
        print(f"🚀 Tech Crawler Server running at http://localhost:{PORT}")
        print("Open tech_crawler.html in your browser")
        httpd.serve_forever()