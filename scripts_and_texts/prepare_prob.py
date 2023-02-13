# pre-process prob files before sending them to R
# Yanting Li
# 1/20/2023

import csv

def load_abbr_dict(dict_file):
    with open(dict_file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    
    return abbr_dict
    
def read_in_file(file):
    rows = []
    with open(file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            if len(row) == 5:
                rows.append(row)
    for row in rows:
        new_row = new_row_generator(row)
        save_prob('prob1312.csv', new_row)


def new_row_generator(row):
    # row = [target_word, target_form, logprob.item(), disjunction_logprob, line_num]
    target_word = row[0]
    target_form = row[1]
    concept = concept_generator(target_word, target_form)    
    row.insert(1, concept)

    return row

def concept_generator(target_word, target_form):
    abbr_dict = load_abbr_dict('cleaned_abbr_dict_by_ratio_tok.txt')
    if target_form == 'short':
        concept = target_word
    else:
        for short, long in abbr_dict.items():
            if long == target_word:
                concept = short
    
    return concept

def save_prob(output_file, row):
    with open(output_file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    read_in_file('prob_1312.csv')
    