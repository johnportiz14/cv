#!/usr/bin/env python3
'''
https://medium.com/@darshankhandelwal12/scrape-google-scholar-using-python-3f35a3a6597b
'''
import os,sys
import requests
from bs4 import BeautifulSoup
from datetime import date

def getAuthorProfileData(scholar_id):
    try:
        #  url = "https://scholar.google.com/citations?hl=en&user=cOsxSDEAAAAJ"
        url = "https://scholar.google.com/citations?hl=en&user={}".format(scholar_id)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        author_results = {}
        articles = []
        author_results['name'] = soup.select_one("#gsc_prf_in").text
        author_results['position'] = soup.select_one("#gsc_prf_inw+ .gsc_prf_il").text
        author_results['email'] = soup.select_one("#gsc_prf_ivh").text
        author_results['departments'] = soup.select_one("#gsc_prf_int").text
        for el in soup.select("#gsc_a_b .gsc_a_t"):
            article = {
                'title': el.select_one(".gsc_a_at").text,
                'link': "https://scholar.google.com" + el.select_one(".gsc_a_at")['href'],
                'authors': el.select_one(".gsc_a_at+ .gs_gray").text,
                'publication': el.select_one(".gs_gray+ .gs_gray").text
            }
            articles.append(article)
        for i in range(len(articles)):
            articles[i] = {k: v for k, v in articles[i].items() if v and v != ""}
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
        #  print(author_results)
        #  print(articles)
        #  print(cited_by['table'])
    except Exception as e:
        print(e)

    return author_results, articles, cited_by['table']


def write_tex(output_filename, author, citations, date):
    with open(output_filename, 'w') as f:
        write_generic_command(f, 'citdate', date)
        #  write_generic_command(f, 'cittotal', citations['citations'])
        #  write_generic_command(f, 'cithindex', citations['h_index'])
        #  #  write_generic_command(f, 'citi10index', citations['i10_index'])
        #  #  for kcit, vcit in citations.items():
            #  #  write_generic_command(f, f'cit{kcit}', vcit)
            #  #  #  write_generic_command(f, f'cit{kcit}', vcit['num_cit'])
            #  #  #  write_render_citations_command(f, f'fullcit{kcit}', vcit['num_cit'], vcit['id_scholarcitedby'])
        # Loop through each stat category (total citations, h-index, i-index)
        for entry in citations:
            if   'citations' in entry.keys():
                write_generic_command(f, 'cittotal', entry['citations']['all'])
            elif 'h_index' in entry.keys():
                write_generic_command(f, 'cithindex', entry['h_index']['all'])
            elif 'i_index' in entry.keys():
                write_generic_command(f, 'citiindex', entry['i_index']['all'])

def write_generic_command(f, name, value):
    f.write(f'\\newcommand{{\\{name}}}{{{value}}}\n')

def write_render_citations_command(f, name, ncit, id_scholarcitedby):
    f.write(f'\\newcommand{{\\{name}}}{{\\href{{https://scholar.google.com/scholar?cites={id_scholarcitedby}}}{{Cit. {ncit}}}}}\n')




if __name__=='__main__':


    # Test that proxy settings are set
    print()
    print('PROXY VARS')
    print(os.environ['HTTPS_PROXY'])
    print()

    print('Getting Google Scholar stats...')
    print()

    # Google Scholar User ID
    google_user = "dpngZhIAAAAJ&hl"         # (ME)
    # Today's Date (for 'Last updated'...)
    today = date.today()
    #  date = today.strftime('%d %B, %Y')
    date = today.strftime('%-d %B, %Y')  # the "minus" removes leading 0 in day number
    # Get stats
    author_results, articles, stats = getAuthorProfileData(google_user)
    # Print out the stats
    for entry in stats:
        print(entry)

    # Write the stats as LaTeX newcommands in `citations.tex` file
    file = os.path.realpath(__file__)
    file_path = os.path.split(file)[0]
    outfile = os.path.join(file_path,'citations.tex')
    print()
    print('Writing stats to LaTeX file ({})...'.format(outfile))
    write_tex(outfile, 'John P. Ortiz',  stats, date)
    print('    Done.')
