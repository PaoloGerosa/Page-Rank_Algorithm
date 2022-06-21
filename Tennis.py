# Import Libraries to create a Graph object and to save it in local
from Class import Tennis
from Auxiliary_Functions import save

# It generates a Graph object using a twitter dataframe derived from Gephi
def tennis_graph(df, save_term, threshold = 0):
    new_df = adjust_df(df)
    g = Tennis(df = new_df, threshold = threshold)
    save(save_term, g, "tennis")

    g.print_details()
    return g

def adjust_df(df):
    aux_df = df[["Series", "Winner", "Loser"]]
    aux_df = aux_df.rename(columns={'Winner': 'Target', 'Loser': 'Source'})
    aux_df = aux_df.loc[aux_df['Series'].isin(["Grand Slam", "Masters 1000"])]
    aux_df = aux_df.reset_index()
    return aux_df