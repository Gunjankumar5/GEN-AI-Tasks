import os
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
from scraper import fetch_trending_news
from script_generator import generate_script
from video_generator import create_video


def run_pipeline(topic: Optional[str] = None):
    print("=" * 60)
    print("   AI Video Generation Tool - Pipeline Starting")
    print("=" * 60)

    if topic:
        print(f"\n[Step 1] Using provided topic: {topic}")
        article = {"title": topic, "summary": topic, "url": ""}
    else:
        print("\n[Step 1] Fetching trending news articles...")
        articles = fetch_trending_news(limit=5)
        if not articles:
            print("  ERROR: No articles fetched. Check your internet or API key.")
            return
        article = articles[0]
        print(f"  Selected topic: {article['title']}")

    print("\n[Step 2] Generating AI script...")
    script = generate_script(article["title"], article.get("summary", ""))
    print(f"  Script generated ({len(script.split())} words)")
    print(f"  Preview: {script[:120]}...")

    print("\n[Step 3] Creating video with text overlays and images...")
    output_path = os.path.join(os.path.dirname(__file__), "..", "outputs", "assets", "automated_video.mp4")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    success = create_video(script, article["title"], output_path)
    if success:
        print(f"\n  Video saved to: {output_path}")
    else:
        print("\n  ERROR: Video generation failed.")
        return

    print("\n" + "=" * 60)
    print("   Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
