"""
Task 2: SEO Blog Post Creation Tool
Main entry point — orchestrates the full pipeline:
1. Scrape trending/best-selling products from an e-commerce site
2. Research SEO keywords for the product
3. Generate a 150-200 word SEO-optimised blog post
4. Save the blog post as a Markdown file (ready to post on Medium / WordPress)
"""

import os
from dotenv import load_dotenv
load_dotenv()  # Must be called before importing modules that read env vars at module level
from scraper import scrape_trending_products
from seo_keywords import get_seo_keywords
from blog_generator import generate_blog_post

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def run_pipeline(num_products: int = 2):
    """
    Run the full SEO blog creation pipeline.

    Args:
        num_products: How many products to generate blog posts for.
    """
    print("=" * 60)
    print("   SEO Blog Post Creation Tool - Pipeline Starting")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: Scrape trending products
    print("\n[Step 1] Scraping trending products...")
    products = scrape_trending_products(limit=num_products)
    if not products:
        print("  ERROR: No products found.")
        return
    print(f"  Found {len(products)} product(s).")

    for idx, product in enumerate(products, start=1):
        print(f"\n{'─' * 50}")
        print(f"  Product {idx}: {product['name']}")
        print(f"  Price     : {product['price']}")
        print(f"  Rating    : {product['rating']}")

        # Step 2: Research SEO keywords
        print(f"\n[Step 2] Researching SEO keywords for: {product['name'][:40]}...")
        keywords = get_seo_keywords(product["name"], product.get("category", ""))
        print(f"  Keywords  : {', '.join(keywords)}")

        # Step 3: Generate blog post
        print("\n[Step 3] Generating SEO blog post with AI...")
        blog_content = generate_blog_post(product, keywords)
        word_count = len(blog_content.split())
        print(f"  Blog post generated ({word_count} words)")

        # Save blog post
        filename = f"blog_post_{idx}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(blog_content)
        print(f"  Saved to  : outputs/{filename}")

    print("\n" + "=" * 60)
    print(f"   Done! {len(products)} blog post(s) saved in /outputs/")
    print("=" * 60)
    print("\nNext step: Copy the .md files to Medium / WordPress to publish.")


if __name__ == "__main__":
    run_pipeline(num_products=2)
