# Import libraries
from Streamlit_Auxiliary_Functions import *
import time

#st.set_page_config(layout="wide")

delete_file("pagerank")

# title and explanation in the website
st.title("PubMed with PageRank algorithm and with Best Match sort algorithm")
st.markdown(
"""
This is a demo of a Streamlit app that shows the publication results available in PubMed for different queries. \n
Moreover it compares the ranks of the results according to three different algorithms: one is the one used by PubMed in 
its website, one is PageRank algorithm that is the one created by Google to rank websites and the last one is the 
combination of the two.
""")
url = "https://docs.google.com/forms/d/19ugo_bLtkJebUGQ1IbPm-DKsg1aaVjsxbswX_P6tC6I"
st.markdown(
"""
\n Choose a query and an algorithm; then check the results, you don't know which algorithm you are using. \n
After having used the webapp please fill in the form to let us know how the three different algorithms behave in your opinion: [PageRank form](%s)""" % url)

Formula = ['<select>']
for elem in os.listdir("PubMed"):
    Formula.append(elem.split(".")[0])

query = st.selectbox(
    'What are you looking for?',
    (Formula)
)

algorithms = st.selectbox("Choose Algorithm",("Algorithm 1", "Algorithm 2", "Algorithm 3"))

st.write("")
st.write("In alternative you can search new queries; this will take some time to get the data and run the algorithms")
# Search toolbox to let users search the place that they want
text_search = st.text_input("Enter the query to search", placeholder = "Type here...")
# If button pressed then the search starts
if st.button("Submit"):
    result = text_search.title()
    result = result.lower()
    result = result.strip()
    start_search = st.success(f'Starting search of {result}. Take a cup of coffee and come back in few minutes')
    if result not in Formula:
        progress_bar = st.progress(0)
        pubmed_graph(result, progress_bar)
        progress_bar.empty()
        Formula.append(result)
    else:
        time.sleep(1.5)
    start_search.empty()
    end_search = st.success(f'Congratulation, the search {result} is completed')
    time.sleep(1.5)
    end_search.empty()
    query = result

if (query != '<select>' or (text_search in Formula or text_search.lower() in Formula)) and algorithms:
    search_term = query if query != '<select>' else text_search
    g = load(search_term)
    if algorithms == "Algorithm 1":
        rank = g.combo_order
    elif algorithms == "Algorithm 2":
        rank = g.myorder
    else:
        rank = g.real_standings
    rank = rank[:min(30, len(rank))]
    st.write(str(len(rank)) + " results found")
    st.write("")

    result_str = '<html><table style="border: none;">'  # Initializing the HTML code for displaying search results
    result_df = pd.DataFrame()
    for i, article in enumerate(rank):
        href = get_link(g.publications[article].id)
        description = g.publications[article].description
        author = g.publications[article].authors
        result_df = result_df.append(pd.DataFrame({"Title": article, "URL": href, "Authors": author, "Description": description}, index=[i]))
        result_str += f'<tr style="border: none;"><h3><a href="{href}" target="_blank">{article}</a></h3></tr>' + \
                      f'<tr style="border: none;"><strong style="color:green;">{author}</strong></tr>' + \
                      f'<tr style="border: none;">{description}</tr>' + \
                      f'<tr style="border: none;"><td style="border: none;"></td></tr>'
    result_str += '</table></html>'

    st.markdown(f'{result_str}', unsafe_allow_html=True)
    #st.markdown('<h3>Data Frame of the above search result</h3>', unsafe_allow_html=True)
    #st.dataframe(result_df)

