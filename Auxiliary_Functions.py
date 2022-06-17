import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import plotly.express as px
from functools import cmp_to_key
from scipy.stats import geom
import plotly.graph_objs as go

chomp = "Objects"

# Save an object of the class graph locally
def save(filename, object, mode):
    new_chomp = chomp + "\Twitter\\" if mode == "twitter" else chomp + "\PubMed\\"
    try:
        file_to_store = open(new_chomp + filename + ".pickle", "wb")
        pickle.dump(object, file_to_store)

        file_to_store.close()

    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

# Load an object of the class graph locally
def load(filename, mode):
    new_chomp = chomp + "\Twitter\\" if mode == "twitter" else chomp + "\PubMed\\"
    try:
        file_to_read = open(new_chomp + filename + ".pickle", "rb")
        loaded_object = pickle.load(file_to_read)

        file_to_read.close()
        return loaded_object

    except Exception as ex:
        print("Error during loading data:", ex)

# PCA analysis in order to personalize teleportation distribution
# mode = 1 if we want to plot the results
def pca_analysis(g, mode = 0):
    # features to use to create the standing
    columns = ['cited_by_feeds_count', 'cited_by_posts_count', 'cited_by_tweeters_count', 'cited_by_policies_count', 'cited_by_patents_count', 'cited_by_wikipedia_count', 'cited_by_accounts_count', 'score', 'readers_count', 'mendeley', 'connotea']
    # features that are under readers in the details of the publication
    sub_columns = ['mendeley', 'connotea']
    # articles that have non empty details
    articles_list = []
    m = len(columns)
    article_dict = {col: [] for col in columns}
    for article in g.publications:
        details = g.publications[article].details
        if details:
            articles_list.append(article)
            for i, col in enumerate(columns):
                if col in sub_columns:
                    info = details["readers"].get(col, 0)
                else:
                    info = details.get(col, 0)
                article_dict[col].append(info)
    details_df = pd.DataFrame(data = article_dict)

    features = columns
    x = details_df.loc[:, features].values
    # Standardizing the features
    x = MinMaxScaler().fit_transform(x)

    fig = px.imshow(np.corrcoef(np.transpose(x)),
                    labels=dict(color="Productivity"),
                    x=columns,
                    y=columns)
    fig.update_layout(font=dict(size=18))
    fig.show()
    if mode:
        pca = PCA()
        principalComponents = pca.fit_transform(x)
        # plt.bar([i for i in range(1, m + 1)], np.cumsum(pca.explained_variance_ratio_))
        # plt.plot(np.linspace(0.5, m+0.5, m), [0.7 for _ in range(m)], color = "k")
        # plt.show()

        exp_var_cumul = np.cumsum(pca.explained_variance_ratio_)
        fig = px.area(
            x=range(1, exp_var_cumul.shape[0] + 1),
            y=exp_var_cumul,
            labels={"x": "# Components", "y": "Explained Variance"}
        )
        fig.update_layout(font=dict(size=30))
        fig.show()


        pca = PCA(n_components=3)
        principalComponents = pca.fit_transform(x)
        # print(principalComponents)
        # print(pca.explained_variance_ratio_)
        # principalDf = pd.DataFrame(data = principalComponents, columns = ['principal component 1', 'principal component 2'])

        labels = {
            str(i): f"PC {i + 1}" # ({var:.1f}%)
            for i, var in enumerate(pca.explained_variance_ratio_ * 100)}

        fig = px.scatter_matrix(
            principalComponents,
            labels=labels,
            dimensions=range(3)
        )
        fig.update_layout(font=dict(size=30))
        fig.update_traces(diagonal_visible=False)
        fig.show()

        loadings = pd.DataFrame(pca.components_, columns=columns)
        # print(loadings)
        fig = px.bar(loadings.iloc[0].values.tolist(), labels={"index": "Components", "value": "Loadings"})
        fig.update_layout(font=dict(size=30))
        fig.show()

        fig = px.bar(loadings.iloc[1].values.tolist(), labels={"index": "Components", "value": "Loadings"})
        fig.update_layout(font=dict(size=30))
        fig.show()

    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(x)
    return principalComponents, articles_list

# Comparison used to sort and create the standing
def compare(item1, item2):
    if item1[1] > item2[1] + 0.5:
        return 1
    elif item2[1] > item1[1] + 0.5:
        return -1
    else:
        if item1[2] > item2[2]:
            return 1
        elif item2[2] > item1[2]:
            return -1
    return 0

# It creates the standing and return the final personalized distribution
def personalized_altmetric(g):
    pc, articles_list = pca_analysis(g)
    pc = [[i, pc[i][0], pc[i][1]] for i in range(len(pc))]
    pc.sort(key=cmp_to_key(compare), reverse=True)
    standing = [pc[i][0] for i in range(len(pc))]
    return create_pca_distribution(g, standing, articles_list)

# It creates the geometric distribution to use in the Montecarlo simulation
def create_pca_distribution(g, standing, articles_list):
    X = [i+1 for i in range(len(standing))]
    p = 0.2
    geom_pd = geom.pmf(X, p)
    prob_left = 1 - sum(geom_pd)
    geom_standing = {articles_list[standing[i]]: geom_pd[i] for i in range(len(articles_list))}

    elements_left = g.count - len(geom_pd)
    personalized_vector = [float(prob_left / elements_left) if elements_left else 0 for _ in range(g.count)]
    for elem in geom_standing:
        personalized_vector[g.users[elem]] = geom_standing[elem]

    return personalized_vector

def create_distribution(g, standing):
    X = [i + 1 for i in range(len(standing))]
    p = 0.2
    geom_pd = geom.pmf(X, p)
    total_prob = sum(geom_pd)
    geom_standing = {standing[i]: geom_pd[i] for i in range(len(standing))}

    personalized_vector = [0.0 for _ in range(g.count)]
    for elem in geom_standing:
        personalized_vector[g.users[elem]] = float(geom_standing[elem] / total_prob)

    return personalized_vector



"""
from scipy.stats import geom
test = [i+1 for i in range(6)]
X = [i+1 for i in range(6)]
Y = ["p = 0.2" for i in range(6)]
Y.extend(["p = 0.5" for i in range(6)])
Y.extend(["p = 0.8" for i in range(6)])
X.extend([i+1 for i in range(6)])
X.extend([i+1 for i in range(6)])
p1 = 0.2
p2 = 0.5
p3 = 0.8
geom_pd = list(geom.pmf(test, p1))
geom_pd.extend(list(geom.pmf(test, p2)))
geom_pd.extend(list(geom.pmf(test, p3)))
data = pd.DataFrame({'x' : X, 'Parameter p' : Y, 'P(X = x)' : geom_pd}, columns=['x','Parameter p','P(X = x)'])
import plotly.express as px

fig = px.line(data, y="P(X = x)", x="x", color="Parameter p", markers = True)
fig.update_traces(marker_size=10)
fig.update_layout(font=dict(size=30))
fig.show()
"""