#!/usr/bin/env python3

"""
AI/SRE Portfolio - Problem Extractor
Scrapes Reddit & Hacker News for real SRE/AI pain points
"""

import json
import os
import sys
from datetime import datetime, timedelta
import requests

# Optional: PRAW for Reddit (install: pip install praw)
try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False

# Perplexity API
import urllib.request
import urllib.error


def log(msg):
    """Structured logging"""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {msg}", flush=True)


def get_perplexity_response(prompt):
    """Call Perplexity API to analyze problems"""
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        log("❌ PERPLEXITY_API_KEY not set")
        return None

    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are an SRE expert problem analyzer. Extract and score pain points from user comments. Return JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.7,
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(
            "https://api.perplexity.ai/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('choices', [{}])[0].get('message', {}).get('content')
    except Exception as e:
        log(f"❌ Perplexity API error: {e}")
        return None


def scrape_hackernews():
    """Scrape HN Top Stories for SRE/AI keywords"""
    log("📰 Scraping Hacker News...")
    problems = []

    try:
        # Get top stories from past week
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10)
        story_ids = response.json()[:30]  # Top 30

        for story_id in story_ids[:10]:  # Sample 10
            story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
            story = requests.get(story_url, timeout=5).json()

            title = story.get("title", "")
            text = story.get("text", "")

            # Filter for SRE/AI keywords
            keywords = ["sre", "observability", "incident", "scaling", "reliability", "ai", "automation", "kubernetes"]
            if any(kw in title.lower() or kw in text.lower() for kw in keywords):
                problems.append({
                    "source": "hackernews",
                    "title": title,
                    "url": story.get("url", ""),
                    "score": story.get("score", 0),
                    "time": story.get("time", 0)
                })

    except Exception as e:
        log(f"⚠️  HN scrape error: {e}")

    log(f"✅ Found {len(problems)} relevant HN stories")
    return problems


def scrape_reddit():
    """Scrape Reddit r/sre, r/devops, r/observability"""
    if not PRAW_AVAILABLE:
        log("⚠️  PRAW not installed. Skipping Reddit scraping. (pip install praw)")
        return []

    log("📱 Scraping Reddit...")
    problems = []

    # Note: Requires Reddit API credentials (optional for this demo)
    # For now, we'll skip actual Reddit auth and log a note
    log("⚠️  Reddit scraping requires API credentials. Skipping for now.")
    log("💡 To enable: Get credentials from https://www.reddit.com/prefs/apps, set REDDIT_CLIENT_ID & REDDIT_CLIENT_SECRET")

    return problems


def extract_top_problems(all_posts):
    """Use Perplexity to extract and rank top problems"""
    if not all_posts:
        log("⚠️  No posts found to analyze")
        return []

    log("🧠 Analyzing problems with Perplexity...")

    # Prepare prompt
    posts_text = "\n".join([
        f"- {p['title']} (Score: {p.get('score', 0)}, Source: {p['source']})"
        for p in all_posts[:20]
    ])

    prompt = f"""
Analyze these SRE/AI community discussions and extract the TOP 5 REAL PROBLEMS (pain points) that practitioners face:

{posts_text}

For each problem:
1. Give it a clear title
2. Provide a brief description (1-2 sentences)
3. Explain why it matters in production
4. Suggest a tool/solution category that could address it
5. Rate severity: HIGH/MEDIUM/LOW

Return as JSON array with keys: [title, description, importance, solution_category, severity]
"""

    response = get_perplexity_response(prompt)
    if not response:
        log("❌ Failed to analyze problems")
        return []

    log("✅ Problems analyzed and ranked")

    # Try to parse JSON from response
    try:
        # Extract JSON from markdown code blocks if present
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            json_str = response

        problems = json.loads(json_str)
        return problems if isinstance(problems, list) else [problems]
    except json.JSONDecodeError:
        log(f"⚠️  Could not parse JSON response: {response[:200]}")
        return []


def save_problems(problems, output_file):
    """Save problems to file"""
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "problems": problems
        }, f, indent=2)
    log(f"💾 Saved {len(problems)} problems to {output_file}")


def main():
    """Main extraction pipeline"""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(repo_root, "problems")
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"problems_{datetime.now().strftime('%Y-%m-%d')}.json")

    log("=" * 50)
    log("🔍 Starting Problem Extraction")
    log("=" * 50)

    # Scrape sources
    hn_posts = scrape_hackernews()
    reddit_posts = scrape_reddit()

    all_posts = hn_posts + reddit_posts
    log(f"📊 Total posts collected: {len(all_posts)}")

    if not all_posts:
        log("⚠️  No posts found. Exiting.")
        return 1

    # Extract and rank problems
    problems = extract_top_problems(all_posts)

    if problems:
        save_problems(problems, output_file)
        log("✅ Problem extraction complete!")
        return 0
    else:
        log("❌ No problems extracted")
        return 1


if __name__ == "__main__":
    sys.exit(main())
