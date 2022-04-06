import pandas as pd
from PubMed import get_soup, get_total_page, get_citations
from Class import Graph
import streamlit as st
import pickle
chomp = "PubMed//"

# important function so that the app is dynamic
@st.cache(persist=True)
def get_link(id):
    link = "https://pubmed.ncbi.nlm.nih.gov/" + str(id)
    return link

# It construct the link of the URL of pubmed web page using the search_term that the user is looking for
def constructLink(search, page, mode = 1):
    term = search.replace(" ", "+")      # In pubmed if two or more words are searched URL substitutes the space with +
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


# Save an object of the class graph locally
def save(filename, object):
    try:
        file_to_store = open(chomp + filename + ".pickle", "wb")
        pickle.dump(object, file_to_store)

        file_to_store.close()

    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

# Load an object of the class graph locally
def load(filename):
    try:
        file_to_read = open(chomp + filename + ".pickle", "rb")
        loaded_object = pickle.load(file_to_read)

        file_to_read.close()
        return loaded_object

    except Exception as ex:
        print("Error during loading data:", ex)


# It constructs a dataframe of a network of articles-citations in pubmed given in input a search query
def search(search, progress_bar):
    link = constructLink(search, page = 1)
    st.write("ciao")
    soup = get_soup(link)
    pages = min(get_total_page(soup), 10)
    articles = []
    set_of_articles = set()
    standings = []
    memo_links = dict()
    memo_authors = dict()
    memo_description = dict()
    for page in range(1, pages+1):
        st.write("ciao")
        link = constructLink(search, page = page)
        soup = get_soup(link)
        main_text = soup.find('div', class_="search-results", id="search-results")  # useful content of the page
        main_text = main_text.find('section', class_="search-results-list")         # more focused content
        for article in main_text.find_all('article', class_="full-docsum"):         # list of articles
            article_info = article.find('div', class_="docsum-wrap")                # detailed information of the article
            description = article_info.find('div', class_="docsum-snippet")         # description of the article
            description = description.div.text
            article = article_info.div.a                                            # information of the article
            author = article_info.div.div.span.text                                 # author of the article
            author = author.split(",")
            author = ", ".join(author[:min(10, len(author))])
            further_link = article["href"].split("/")[1]                            # id of the article
            article_name = article.text.strip()                                     # remove useless space from the name
            memo_links[article_name] = further_link                                 # It saves the link of the article
            memo_authors[article_name] = author                                     # It saves the author of the article
            memo_description[article_name] = description                            # It saves the description of the article
            if article_name not in set_of_articles:
                set_of_articles.add(article_name)
                standings.append(article_name)
                get_citations(further_link, articles, article_name)
        progress_bar.progress(page / pages)
    return pd.DataFrame(articles, columns =['Source', 'Target']), standings, memo_links, memo_authors, memo_description


# It generates a Graph object in the pubmed web site using a query
def pubmed_graph(search_term, progress_bar, threshold = 0):
    articles, standings, memo_links, memo_authors, memo_descriptions = search(search_term, progress_bar)
    g = Graph(articles, threshold = threshold, standings = standings)
    g.add_info(memo_links, memo_authors, memo_descriptions)
    g.print_details()
    g.montecarlo(query = search_term)
    g.compare_order()
    save(search_term, g)
    return g

