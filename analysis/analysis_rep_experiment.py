from utils.save_runs import load_runs

import pandas as pd

# is used for comparing several dataframes
def compare_dataframes(df1, df2):
    """
    Compares two DataFrames row by row.

    Parameters:
    - df1, df2: The DataFrames to compare.

    Returns:
    - A message indicating whether the DataFrames are identical.
    - If there are differences, a list of the differing rows with details.
    """
    if df1.equals(df2):
        return "The DataFrames are identical."

    differences = []

    for i in range(len(df1)):
        if not df1.iloc[i].equals(df2.iloc[i]):
            differences.append((i, df1.iloc[i], df2.iloc[i]))

    if differences:
        result = "Differences found in the following rows:\n"
        for diff in differences:
            result += f"Row {diff[0]}:\nDF1: {diff[1].to_dict()}\nDF2: {diff[2].to_dict()}\n\n"
        return result
    else:
        return "All rows are identical."

cmp1 = load_runs('touche-21-reranking-rep1')
cmp2 = load_runs('touche-21-reranking-rep2')

mewo = 1

for i,group in enumerate(cmp1):
    print(group[0])
    df_group_1 = group[1]
    assert group[0] == cmp2[i][0]
    df_group_2 = cmp2[i][1]
    df_group_2 = df_group_2[df_group_1.columns.tolist()]
    sort_columns = df_group_1.columns.tolist()  # Assumes both DataFrames have the same columns in the same order
    sorted_df1 = df_group_1.sort_values(by=sort_columns).reset_index(drop=True)
    sorted_df2 = df_group_2.sort_values(by=sort_columns).reset_index(drop=True)

    #sorted_df1 = sorted_df1[sorted_df1['name']== group[0]]
    #sorted_df2 = sorted_df2[sorted_df2['name']== group[0]]


    print(compare_dataframes(sorted_df1,sorted_df2))