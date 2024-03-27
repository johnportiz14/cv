import edustats
from datetime import date

#  def write_tex(output_filename, author, citations):
    #  with open(output_filename, 'w') as f:
        #  write_generic_command(f, 'cittotal', author.citedby)
        #  write_generic_command(f, 'cithindex', author.hindex)
        #  for kcit, vcit in citations.items():
            #  write_generic_command(f, f'cit{kcit}', vcit['num_cit'])
            #  write_render_citations_command(f, f'fullcit{kcit}', vcit['num_cit'], vcit['id_scholarcitedby'])

def write_tex(output_filename, author, citations, date):
    with open(output_filename, 'w') as f:
        write_generic_command(f, 'citdate', date)
        write_generic_command(f, 'cittotal', citations['citations'])
        write_generic_command(f, 'cithindex', citations['h_index'])
        #  write_generic_command(f, 'citi10index', citations['i10_index'])
        #  for kcit, vcit in citations.items():
            #  write_generic_command(f, f'cit{kcit}', vcit)
            #  #  write_generic_command(f, f'cit{kcit}', vcit['num_cit'])
            #  #  write_render_citations_command(f, f'fullcit{kcit}', vcit['num_cit'], vcit['id_scholarcitedby'])

def write_generic_command(f, name, value):
    f.write(f'\\newcommand{{\\{name}}}{{{value}}}\n')

def write_render_citations_command(f, name, ncit, id_scholarcitedby):
    f.write(f'\\newcommand{{\\{name}}}{{\\href{{https://scholar.google.com/scholar?cites={id_scholarcitedby}}}{{Cit. {ncit}}}}}\n')




if __name__=='__main__':

    print('Getting Google Scholar stats...')

    # Google Scholar User ID
    google_user = "dpngZhIAAAAJ&hl"
    # Today's Date (for 'Last updated'...)
    today = date.today()
    date = today.strftime('%d %B, %Y')
    stats = edustats.google_scholar(google_user)
    for k in stats: print(k, stats[k])


    outfile = 'citations.tex'
    print('Writing stats to LaTeX file ({})...'.format(outfile))
    write_tex(outfile, 'John P. Ortiz',  stats, date)





