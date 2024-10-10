#!/usr/bin/env python3
import os, sys
import requests
from bs4 import BeautifulSoup
from datetime import date
from unicodedata import normalize
import re
import json

# Function to get author profile data with pagination
def getAuthorProfileData(scholar_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    }
    author_results = {}
    all_articles = []
    cstart = 0
    page_size = 20  # Number of articles per page
    
    while True:
        url = f"https://scholar.google.com/citations?hl=en&user={scholar_id}&cstart={cstart}&pagesize={page_size}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract author information (only done once, so outside the loop for articles)
        if cstart == 0:
            author_results['name'] = soup.select_one("#gsc_prf_in").text
            author_results['position'] = soup.select_one("#gsc_prf_inw+ .gsc_prf_il").text
            author_results['email'] = soup.select_one("#gsc_prf_ivh").text
            author_results['departments'] = soup.select_one("#gsc_prf_int").text

        # Parse articles on the current page
        articles_on_page = soup.select("#gsc_a_b .gsc_a_t")
        if not articles_on_page:  # Stop if no more articles are found
            break

        for el in articles_on_page:
            # Try to extract the publication year, handle cases where it may not be a valid year
            try:
                year_text = el.select_one(".gs_gray+ .gs_gray").text[-4:]  # Extract the last 4 characters
                year = int(re.sub(r'[^\d]', '', year_text))  # Remove non-digit characters and convert to int
            except (ValueError, AttributeError):
                print(f"Warning: Could not parse the year for article '{el.select_one('.gsc_a_at').text[:25]}...'")
                year = None  # Set year to None or some default if parsing fails
        
            article = {
                'title': el.select_one(".gsc_a_at").text,
                'year': year,  # Use the parsed year or None
                'link': "https://scholar.google.com" + el.select_one(".gsc_a_at")['href'],
                'authors': el.select_one(".gsc_a_at+ .gs_gray").text,
                'publication': el.select_one(".gs_gray+ .gs_gray").text,
                'article_cited_by': -999,
            }
        
            # Get the number of citations by visiting the article page
            resp = requests.get(article['link'], headers=headers)
            s = BeautifulSoup(resp.text, 'html.parser')
            s_str = str(s)
            try:
                art_cit_by = s_str.split("Cited by ", 1)[1][:10].replace('"', '')
                art_cit_by_ascii = normalize('NFKD', art_cit_by).encode('ascii', 'ignore')
                art_cit_by_num = re.findall(r'\d+', str(art_cit_by_ascii))[0]
                article['article_cited_by'] = int(art_cit_by_num)
                print(f'Article ({article["title"][:25]}...) cite by number: {art_cit_by_num}')
                #  print(art_cit_by_num)

            except (IndexError, ValueError):
                print(f"Article ({article['title'][:25]}...) has no citations!")
                article['article_cited_by'] = 0
        
            # Append the article only if we successfully parsed the year (optional, based on your needs)
            if year is not None:
                all_articles.append(article)
            else:
                print(f"Skipping article '{article['title']}' due to missing or invalid year.")

        
        # Move to the next page
        cstart += page_size

    # Parse citation stats
    cited_by = {}
    cited_by['table'] = []
    cited_by['table'].append({})
    cited_by['table'][0]['citations'] = {}
    cited_by['table'][0]['citations']['all'] = soup.select_one("tr:nth-child(1) .gsc_rsb_sc1+ .gsc_rsb_std").text
    cited_by['table'][0]['citations']['since_2017'] = soup.select_one("tr:nth-child(1) .gsc_rsb_std+ .gsc_rsb_std").text
    cited_by['table'].append({})
    cited_by['table'][1]['h_index'] = {}
    cited_by['table'][1]['h_index']['all'] = soup.select_one("tr:nth-child(2) .gsc_rsb_sc1+ .gsc_rsb_std").text
    cited_by['table'][1]['h_index']['since_2017'] = soup.select_one("tr:nth-child(2) .gsc_rsb_std+ .gsc_rsb_std").text
    cited_by['table'].append({})
    cited_by['table'][2]['i_index'] = {}
    cited_by['table'][2]['i_index']['all'] = soup.select_one("tr~ tr+ tr .gsc_rsb_sc1+ .gsc_rsb_std").text
    cited_by['table'][2]['i_index']['since_2017'] = soup.select_one("tr~ tr+ tr .gsc_rsb_std+ .gsc_rsb_std").text

    print('Fetched all articles across pages.')

    return author_results, all_articles, cited_by['table']


# Function to write LaTeX commands
def write_tex(output_filename, author, citations, article_stats, date):
    with open(output_filename, 'w') as f:
        write_generic_command(f, 'citdate', date)
        for entry in citations:
            if 'citations' in entry:
                write_generic_command(f, 'cittotal', entry['citations']['all'])
            elif 'h_index' in entry:
                write_generic_command(f, 'cithindex', entry['h_index']['all'])
            elif 'i_index' in entry:
                write_generic_command(f, 'citiindex', entry['i_index']['all'])
        
        f.write('%-------Per-article Citations-------------\n')
        for counter, article in enumerate(article_stats):
            num_citations = article.get('article_cited_by', 0)
            yyyy = article['year']
            pub = article['publication'][:-4]
            rule = re.compile('[^a-zA-Z]')
            pubkey = rule.sub('', pub)[:20]
            titlekey = rule.sub('', article['title'].replace(' ', ''))[:20]
            article_key = f"{pubkey}OOOO{titlekey}"
            f.write(f'%%% ARTICLE #[{counter}]: ({yyyy}) {pubkey}_{titlekey}\n')
            display_text = f'(Cited by: {num_citations}).' if num_citations > 0 else ''
            write_generic_command(f, article_key, display_text)


def write_generic_command(f, name, value):
    f.write(f'\\newcommand{{\\{name}}}{{{value}}}\n')


if __name__ == '__main__':
    print('Getting Google Scholar stats...\n')

    # Google Scholar User ID
    google_user = "dpngZhIAAAAJ&hl"
    today = date.today()
    date_str = today.strftime('%-d %B, %Y')

    author_results, articles_stats, stats = getAuthorProfileData(google_user)
    for entry in stats:
        print(entry)

    # Write the stats as LaTeX newcommands in `citations.tex`
    file_path = os.path.dirname(os.path.realpath(__file__))
    outfile = os.path.join(file_path, 'citations.tex')
    print(f'Writing stats to LaTeX file ({outfile})...')
    write_tex(outfile, 'John P. Ortiz', stats, articles_stats, date_str)
    print('Done.')

