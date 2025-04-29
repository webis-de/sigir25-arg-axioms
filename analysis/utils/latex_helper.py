import re
import pandas as pd
from collections import defaultdict
from axioms.axioms_names import arg_axiom_list_new_axioms,arg_axiom_name_list_new_axioms,axiom_list_old_axioms,axiom_names_list_old_axioms
from utils.save_runs import load_runs

maximum_characters_per_line = 70


def columns_to_rows(final_table_columns_list) :

    full_table_rows = []

    header_row = []
    for key, value in final_table_columns_list :
        header_row.append(key)
    full_table_rows.append(header_row)

    nbr_of_rows = set([len(value) for key, value in final_table_columns_list])
    assert len(nbr_of_rows) == 1
    nbr_of_rows = list(nbr_of_rows)[0]

    for i in range(nbr_of_rows) :
        current_row = []
        for key, value in final_table_columns_list :
            current_row.append(value[i])
        full_table_rows.append(current_row)

    return full_table_rows

def fill_rows(text_list):
    ''''Works on specified input table'''

    nbr_columns = len(text_list[0])
    cols_entries = [[] for x in range(nbr_columns)]
    for row in text_list:
        assert len(row) == nbr_columns
        for ind,entry in enumerate(row):
            cols_entries[ind].append(len(entry))
    cols_entries_max = [max(x) for x in cols_entries]

    for row in text_list:
        for ind,entry in enumerate(row):
            spaces_to_add = cols_entries_max[ind] - len(entry)
            if spaces_to_add > 0:
                entry += " " * spaces_to_add
            row[ind] = entry
    return text_list


def latex_row_command(table, name, ident=0,command='\\textcolor{gray}',columns_to_ignore=[]):
    table_to_return = []
    for row in table:
        row_tmp = row
        if row[ident] == name:
            row_tmp = []
            for i,x in enumerate(row):
                if (x == '') or (i in columns_to_ignore):
                    row_tmp.append(x)
                else:
                    row_tmp.append(f"{command}{{{x}}}")
        table_to_return.append(row_tmp)
    return table_to_return

def latex_mark_highest_column(table,command='\\textbf',index_to_ignore=[]):
    table  = table.copy()
    pattern = r"\d+\.\d+"

    nbr_of_rows = len(table)
    length_of_columns_tmp = list(set([len(x) for x in table]))
    assert len(length_of_columns_tmp) == 1
    nbr_of_columns = length_of_columns_tmp[0]

    for i in range(nbr_of_columns):
        if i in index_to_ignore:
            continue
        values_tmp = []
        for row in table:
            match = re.search(pattern, row[i])
            if match :
                number = float(match.group())
                values_tmp.append(number)
        if len(values_tmp) == nbr_of_rows:
            max_value = max(values_tmp)
            for row in table:
                match = re.search(pattern, row[i])
                if match :
                    val = match.group()
                    number = float(val)
                    if number == max_value:
                        row[i] = row[i].replace(val, f"{command}{{{val}}}")
    return table



