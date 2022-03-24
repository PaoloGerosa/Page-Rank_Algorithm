import requests
from bs4 import BeautifulSoup
import time
from Class import Graph
from Auxiliary_Functions import save
import pandas as pd

def constructLink(search, page, mode = 1):
    term = search.replace(" ", "+")
    if mode:
        if page == 1:
            link = f'https://pubmed.ncbi.nlm.nih.gov/?term={term}'
        else:
            link = f'https://pubmed.ncbi.nlm.nih.gov/?term={term}&page={page}'
    else:
        if page == 1:
            link = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={search}'
        else:
            link = f'https://pubmed.ncbi.nlm.nih.gov/?linkname=pubmed_pubmed_citedin&from_uid={search}&page={page}'
    return link

def get_soup(URL):
    while True:
        try:
            source = requests.get(URL).text
            soup = BeautifulSoup(source, 'lxml')
            break
        except:
            print("Connessione rifiutata dal server..")
            print("Pausa di 5 secondi")
            time.sleep(5)
    return soup

def get_total_page(soup):
    bottom = soup.find("div", class_="bottom-pagination")
    try:
        text = bottom.div.find("label", class_="of-total-pages").text
        pages = int(text.split(" ")[-1].replace(",", ""))
    except:
        pages = 0
    return pages

def search(search):
    link = constructLink(search, page = 1)
    soup = get_soup(link)
    pages = get_total_page(soup)
    articles = []
    for page in range(1, pages+1):
        print(page)
        link = constructLink(search, page = page)
        soup = get_soup(link)
        main_text = soup.find('div', class_="search-results", id="search-results")
        main_text = main_text.find('section', class_="search-results-list")
        for article in main_text.find_all('article', class_="full-docsum"):
            article = article.find('div', class_="docsum-wrap").div.a
            further_link = article["href"].split("/")[1]
            article_name = article.text.strip()
            get_citations(further_link, articles, article_name)
    return pd.DataFrame(articles, columns =['Source', 'Target'])

def get_citations(id, articles, name):
    link = constructLink(id, page = 1, mode = 0)
    soup = get_soup(link)
    pages = get_total_page(soup)
    citations = set()
    for page in range(1, pages+1):
        link = constructLink(id, page = page, mode = 0)
        soup = get_soup(link)
        main_text = soup.find('div', class_="search-results", id="search-results")
        main_text = main_text.find('section', class_="search-results-list")
        for article in main_text.find_all('article', class_="full-docsum"):
            article = article.find('div', class_="docsum-wrap").div.a
            article_name = article.text.strip()
            articles.append([article_name, name])
            citations.add(article_name)

def pubmed_graph(search_term, threshold = 0):
    articles = search(search_term)
    g = Graph(articles, threshold = threshold)
    g.print_details()
    save(search_term, g)
    return g


