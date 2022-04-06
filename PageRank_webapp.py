# Import libraries
import streamlit as st
import pandas as pd
import os
from Streamlit_Auxiliary_Functions import *

# important function so that the app is dynamic
@st.cache(persist=True)
def get_link(id):
    link = "https://pubmed.ncbi.nlm.nih.gov/" + str(id)
    return link

# title and explanation in the website
st.title("PubMed with PageRank algorithm and with Best Match sort algorithm")
st.markdown(
"""
This is a demo of a Streamlit app that shows the publication results available in PubMed for different queries. \n
Moreover it compares the ranks of the results according to three different algorithms: one in the one used by PubMed in 
its website, one is PageRank algorithm that is the one created by Google to rank websites and the last one is the 
combination of the two.
""")
st.markdown(
"""
\n Choose a query and an algorithm; then check the results, you don't know which algorithm you are using.
""")


Formula = []
for elem in os.listdir("Objects"):
    Formula.append(elem.split(".")[0])

query = st.selectbox(
    'What are you looking for?',
    (Formula)
)

algorithms = st.selectbox("Choose Algorithm",("Algorithm 1", "Algorithm 2", "Algorithm 3"))

if query and algorithms:
    g = load(query)
    if algorithms == "Algorithm 1":
        rank = g.real_standings
    elif algorithms == "Algorithm 2":
        rank = g.myorder
    else:
        rank = g.combo_order
    rank = rank[:min(30, len(rank))]
    links = g.links
    descriptions = g.descriptions
    authors = g.authors
    st.write(str(len(rank)) + " results found")
    st.write("")

    result_str = '<html><table style="border: none;">'  # Initializing the HTML code for displaying search results
    result_df = pd.DataFrame()
    for i, article in enumerate(rank):
        href = get_link(links[article])
        description = descriptions[article]
        author = authors[article]
        result_df = result_df.append(pd.DataFrame({"Title": article, "URL": href, "Authors": author, "Description": description}, index=[i]))
        result_str += f'<tr style="border: none;"><h3><a href="{href}" target="_blank">{article}</a></h3></tr>' + \
                      f'<tr style="border: none;"><strong style="color:green;">{author}</strong></tr>' + \
                      f'<tr style="border: none;">{description}</tr>' + \
                      f'<tr style="border: none;"><td style="border: none;"></td></tr>'
    result_str += '</table></html>'

    st.markdown(f'{result_str}', unsafe_allow_html=True)
    #st.markdown('<h3>Data Frame of the above search result</h3>', unsafe_allow_html=True)
    #st.dataframe(result_df)


