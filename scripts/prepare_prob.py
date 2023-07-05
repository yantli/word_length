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
    
def read_in_file(input_file, output_file):
    rows = []
    with open(input_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            if len(row) == 5:
                rows.append(row)
    for row in rows:
        new_row = new_row_generator(row)
        save_prob(output_file, new_row)


def new_row_generator(row):
    # row = [target_word, target_form, logprob.item(), disjunction_logprob, line_num]
    target_word = row[0]
    target_form = row[1]
    concept = concept_generator(dict_file, target_word, target_form)    
    row.insert(1, concept)

    return row

def concept_generator(dict_file, target_word, target_form):
    abbr_dict = load_abbr_dict(dict_file)
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
    dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/clue_new_abbr_dict.txt'
    input_file = '/Users/yanting/Desktop/word_length/probs/prob_trigram_clue117.csv'
    output_file = '/Users/yanting/Desktop/word_length/probs/prob_trigramclue117.csv'
    read_in_file(input_file, output_file)