'''
Did the unemployment rate move?
Did the interest rate move?
Did the economic growth rate move?

Rate type     Change
Unemployment    XX
Interest        XX
Economic        XX
'''

import os.path
import requests
import PyPDF2
import spacy
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def main_function(year, month, day):
    '''
    Reads the document and determines the direction of the unemp rate,
    interest rate and economic growth rate and prints the df containing
    the results
    '''
    
    results = {'rate type': ['unemployment', 'interest', 'economic'], 'direction': []}
    
    fname = get_pdf('2019', '03', '20')
    pages = parse_pdf(fname)
    doc = clean_and_tokenize(pages)
    
    for word in results['rate type']:
        mentions = [token for token in doc if token.text == word]
        direction = get_direction(mentions, 'rate')
        results['direction'].append(direction)
    
    print(pd.DataFrame.from_dict(results))

##Prof Levy's function
def get_pdf(year, month, day):
    '''
    Gets the federal reserve press release from the web and returns the filename.
    '''
    
    url = 'https://www.federalreserve.gov/monetarypolicy/files/monetary{}{}{}a1.pdf'.format(year, month, day)
    fname = url.split('/')[-1]
    if not os.path.exists(fname):
        response = requests.get(url)
        print('Downloading file from the web')
        assert(fname.endswith('.pdf')), 'Incorrect file type in get_statement, expected PDF, got: {}'.format(url)
        with open(fname, 'wb') as ofile:
            ofile.write(response.content)
    else:
        print('File already there')
    
    return fname

##Prof Levy's function
def parse_pdf(fname):
    '''
    Reads the pdf and retuns the text as a list of lists where each list is a page
    '''

    with open(fname, 'rb') as ifile:
        pdf_reader = PyPDF2.PdfFileReader(ifile)
        n_pages = pdf_reader.numPages
        pages = [pdf_reader.getPage(p) for p in range(n_pages)]
        pages = [p.extractText() for p in pages]
        
        return pages


def clean_and_tokenize(pages):
    '''
    Takes a list of lists were each sub-list is a page of the pdf,
    cleans the text and returns tokens.
    '''

    text = ' '.join(pages)
    text = text.strip().replace('\n', ' ')
    text = ' '.join(text.split())
    tokens = nlp(text)
    tokens = [token for token in tokens if not token.is_stop and not token.is_punct]
    
    return tokens


def get_direction(mentions, word):
    '''
    Takes a list of tokens (eg mentions of 'unemployment') and checks its ancestors for the 
    word provided in the parameters (eg 'rate').
    If the word is found the function checks the ancestors of that word to determine the 
    direction (up down or flat).
    '''
    
    words = {'up': ['raise', 'increase', 'up'], 
         'down':['lower', 'decrease', 'down', 'slowed'], 
         'flat':['unchanged', 'same', 'remain']}
    
    counter = {'up': 0, 'down':0, 'flat':0, 'no info':0.5}
    
    for token in mentions:
        ancestors = list(token.ancestors)
        for ancestor in ancestors:
            if ancestor.text == word:
                second_anc = list(ancestor.ancestors)
                for s_anc in second_anc:
                    if s_anc.lemma_ in words['up']:
                        counter['up'] += 1
                    elif s_anc.lemma_ in words['down']:
                        counter['down'] += 1
                    elif s_anc.lemma_ in words['flat']:
                        counter['flat'] += 1
                        
    return max(counter, key=counter.get)


if __name__ == "__main__":
    main_function('2019', '03', '20')

