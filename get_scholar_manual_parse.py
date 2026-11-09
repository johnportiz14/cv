#!/usr/bin/env python3
"""Manual Google Scholar Parser"""
import os, sys, re
from bs4 import BeautifulSoup
from datetime import date

print("="*70)
print("Google Scholar Stats - Manual Parser")
print("="*70)
print("\n" + "="*70)
print("INSTRUCTIONS: How to update scholar.html")
print("="*70)
print("\n1. Open this link in your web browser (any browser works):")
print("\n   https://scholar.google.com/citations?user=dpngZhIAAAAJ&pagesize=100")
print("\n2. Wait for the page to FULLY load (you should see all your articles)")
print("\n3. Right-click anywhere on the page")
print("\n4. Select 'Save As...' or 'Save Page As...'")
print("\n5. In the save dialog:")
print(f"   - Filename: scholar.html")
print(f"   - Format: Webpage, HTML Only (or Web Page, Complete)")
print(f"   - Location: {os.getcwd()}")
print("\n6. Click Save (replace the existing file if prompted)")
print("\n" + "="*70)

html_file = 'scholar.html'

if not os.path.exists(html_file):
    print("\n❌ scholar.html not found!")
    print("\nPlease follow the instructions above to save the file first.")
    print(f"\nThen run this script again:")
    print(f"   cd {os.getcwd()}")
    print("   python3 manual_parse.py")
    print("\n" + "="*70)
    sys.exit(0)

print("\n✓ Found scholar.html")
print("\nParsing your Google Scholar data...")

try:
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
except Exception as e:
    print(f"\n❌ ERROR: Could not read {html_file}")
    print(f"Error: {e}")
    sys.exit(1)

soup = BeautifulSoup(html, 'html.parser')
name = soup.select_one("#gsc_prf_in")
if not name:
    print("\n❌ ERROR: Could not find profile data in the HTML file.")
    print("\nPossible issues:")
    print("  1. The page didn't fully load before you saved it")
    print("  2. You saved the wrong page")
    print("  3. The file got corrupted during save")
    print("\nTry again:")
    print("  1. Delete scholar.html")
    print("  2. Reload the page in your browser")
    print("  3. Wait for it to fully load (see all articles)")
    print("  4. Save it again")
    sys.exit(1)

print(f"\n✓ Author: {name.text}")
stats = soup.select(".gsc_rsb_std")
if len(stats) >= 6:
    print(f"✓ Total citations: {stats[0].text}")
    print(f"✓ h-index: {stats[2].text}")
    print(f"✓ i10-index: {stats[4].text}")
else:
    print("\n⚠ Warning: Could not find citation statistics")

articles = soup.select("#gsc_a_b .gsc_a_t")
citations = soup.select("#gsc_a_b .gsc_a_c")

if len(articles) == 0:
    print("\n❌ ERROR: No articles found in the HTML file")
    print("The page may not have loaded correctly before saving.")
    print("Please try saving the page again.")
    sys.exit(1)

print(f"\n✓ Found {len(articles)} articles")
print("\nExtracting citation counts:")

all_articles = []
for idx, el in enumerate(articles):
    try:
        year_text = el.select_one(".gs_gray+ .gs_gray").text[-4:]
        year = int(re.sub(r'[^\d]', '', year_text))
    except:
        year = None
    num_cit = 0
    if idx < len(citations) and citations[idx].text.strip().isdigit():
        num_cit = int(citations[idx].text.strip())
    title = el.select_one(".gsc_a_at").text
    all_articles.append({
        'title': title, 'year': year, 'article_cited_by': num_cit,
        'authors': el.select_one(".gsc_a_at+ .gs_gray").text if el.select_one(".gsc_a_at+ .gs_gray") else "",
        'publication': el.select_one(".gs_gray+ .gs_gray").text if el.select_one(".gs_gray+ .gs_gray") else ""
    })
    print(f"  {idx+1:2d}. [{num_cit:3d} cites] {title[:60]}")

print(f"\nWriting citations.tex...")
outfile = 'citations.tex'
try:
    with open(outfile, 'w') as f:
        f.write(f'\\newcommand{{\\citdate}}{{{date.today().strftime("%-d %B, %Y")}}}\n')
        if len(stats) >= 6:
            f.write(f'\\newcommand{{\\cittotal}}{{{stats[0].text}}}\n')
            f.write(f'\\newcommand{{\\cithindex}}{{{stats[2].text}}}\n')
            f.write(f'\\newcommand{{\\citiindex}}{{{stats[4].text}}}\n')
        f.write('%-------Per-article Citations-------------\n')
        commands_used = set()
        for i, art in enumerate(all_articles):
            if art['year']:
                num = art['article_cited_by']
                pub = re.sub(r'[^a-zA-Z]', '', art['publication'][:50])[:20]
                title_key = re.sub(r'[^a-zA-Z]', '', art['title'].replace(' ', ''))[:20]
                base_key = f"{pub}OOOO{title_key}"
                key = base_key
                suffix_idx = 0
                while key in commands_used:
                    # Append letters: a, b, c, ..., z, aa, ab, ac, ...
                    suffix_idx += 1
                    suffix = ''
                    n = suffix_idx
                    while n > 0:
                        n -= 1
                        suffix = chr(ord('a') + (n % 26)) + suffix
                        n //= 26
                    key = f"{base_key}{suffix}"
                commands_used.add(key)
                f.write(f'%%% ARTICLE #[{i}]: ({art["year"]}) {key}\n')
                txt = f'(Cited by: {num}).' if num > 0 else ''
                f.write(f'\\newcommand{{\\{key}}}{{{txt}}}\n')
    print(f"✓ Created {outfile}")
except Exception as e:
    print(f"\n❌ ERROR: Could not write {outfile}")
    print(f"Error: {e}")
    sys.exit(1)

print("\n" + "="*70)
print("SUCCESS!")
print("="*70)
print(f"Author: {name.text}")
if len(stats) >= 6:
    print(f"Total citations: {stats[0].text}")
    print(f"h-index: {stats[2].text}")
    print(f"i10-index: {stats[4].text}")
print(f"Articles processed: {len(all_articles)}")
print(f"\nOutput file: {os.path.abspath(outfile)}")
print("\n" + "="*70)
print("NEXT STEP: Copy to your CV folder")
print("="*70)
print("\nRun this command:")
print(f"  cp {outfile} /Users/jportiz/Documents/cv/")
print("\nOr manually copy the file from:")
print(f"  {os.path.abspath(outfile)}")
print("To:")
print("  /Users/jportiz/Documents/cv/citations.tex")
print("\n" + "="*70)
print("\nNOTE: To update with newer citation data, follow the instructions")
print("      at the top to re-save scholar.html, then run this script again.")
print("="*70)

