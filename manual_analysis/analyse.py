import pandas as pd

# old comparison of involved metrics
pyt = pd.read_csv('skywalker_pyterrier.csv')
touche = pd.read_csv('scores.csv')

filtered_dataframe = pyt[pyt['name'] == 'Luke Skywalker']
filtered_dataframe = filtered_dataframe[filtered_dataframe['measure'] == 'nDCG@5']

filtered_dataframe = filtered_dataframe.rename(columns={'name': 'Tag', 'qid': 'Topic', 'value': 'nDCG@5'})
filtered_dataframe['Tag'] = 'luke-skywalker'

ndcg_df = filtered_dataframe[['Tag','Topic','nDCG@5']]
ndcg_df = ndcg_df.sort_values(by=['Topic','nDCG@5'], ascending=True)
touche_df = touche
touche_df = touche_df.sort_values(by=['Topic','nDCG@5'], ascending=True)

for index in range(len(ndcg_df)):

    # Get the rows to compare
    row1 = ndcg_df.iloc[index]
    row2 = touche_df.iloc[index]

    # Find columns where values differ
    differing_columns = row1[row1 != row2].index.tolist()

    # Print the index and differing columns
    if differing_columns :
        print(f"Row {index} differs in columns: {differing_columns}")
        print(ndcg_df.iloc[index :index + 1])
        for col in differing_columns :
            print(f" - df1[{col}]: {row1[col]} vs df2[{col}]: {row2[col]}")
