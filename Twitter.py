from Class import Graph
from Auxiliary_Functions import save, load

def twitter_graph(df, save_term, threshold = 0):
    g = Graph(df = df, mode = "Quote", threshold = threshold)
    save(save_term, g)

    g.print_details()
    return g