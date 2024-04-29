# pre-process prob files before sending them to R
# Yanting Li
# 1/20/2023

import csv
import math

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
    
def read_prob_file(input_file):
    rows = []
    with open(input_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            if len(row) == 5:
                rows.append(row)
    
    return rows

def new_row_generator(row):
    # row = [target_word, target_form, logprob.item(), disjunction_logprob, line_num]
    target_word = row[0]
    target_form = row[1]
    concept = concept_generator(dict_file, target_word, target_form)    
    row.insert(1, concept)
    
    return row

def concept_generator(dict_file, target_word, target_form):
    abbr_dict = load_abbr_dict(dict_file)
    concept = None
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

def output_new_prob(prob_file, output_file):
    all_probs = read_prob_file(prob_file)
    for row in all_probs:
        new_row = new_row_generator(row)
        save_prob(output_file, new_row)

def get_comparison(longprob_path, shortprob_path):
    long_rows = []
    with open(longprob_path, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            long_rows.append(row)
    short_rows = []
    with open(shortprob_path, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            short_rows.append(row)
    # a line should contain: target_word, concept, target_form, target_prob_longcontext, alt_prob_longcontext, disj_prob_longcontext, target_prob_shortcontext, alt_prob_shortcontext, disj_prob_shortcontext, line_num
    context_comparison = []
    for i in range(len(long_rows)):
        target_word = long_rows[i][0]
        concept = long_rows[i][1]
        target_form = long_rows[i][2]
        target_prob_longcontext = float(long_rows[i][3])
        disj_prob_longcontext = float(long_rows[i][4])
        if disj_prob_longcontext > target_prob_longcontext:
            alt_prob_longcontext = math.log(math.exp(disj_prob_longcontext) - math.exp(target_prob_longcontext))
        else:
            alt_prob_longcontext = 0
        target_prob_shortcontext = float(short_rows[i][3])
        disj_prob_shortcontext = float(short_rows[i][4])
        if disj_prob_shortcontext > target_prob_shortcontext:
            alt_prob_shortcontext = math.log(math.exp(disj_prob_shortcontext) - math.exp(target_prob_shortcontext))        
        else:
            alt_prob_shortcontext = 0
        line_num = long_rows[i][5]
        newrow = target_word, concept, target_form, target_prob_longcontext, alt_prob_longcontext, disj_prob_longcontext, target_prob_shortcontext, alt_prob_shortcontext, disj_prob_shortcontext, line_num
        if alt_prob_longcontext != 0 and alt_prob_shortcontext != 0:
            context_comparison.append(newrow)
    
    return context_comparison

def flip_detector(context_comparison):
    flip_cases = []
    for item in context_comparison:
        word_form = item[2]
        target_prob_longcontext = item[3]
        alt_prob_longcontext = item[4]        
        target_prob_shortcontext = item[6]
        alt_prob_shortcontext = item[7]
        if item[2] == 'short':
            if target_prob_longcontext > alt_prob_longcontext and target_prob_shortcontext < alt_prob_shortcontext:
                flip_cases.append(item)
    
    return flip_cases           

def read_position_file(input_file):
    # format: target_word, target_form, char_position_full, tok_position_full, char_position, tok_position
    rows = []
    with open(input_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            rows.append(row)
    
    return rows

def combine_prob_pos(prob, position, output_file):
    for n in range(len(prob)):
        newprob = new_row_generator(prob[n])
        positions = position[n][2:]
        combined = newprob[:5] + positions + [newprob[-1]]
        save_prob(output_file, combined)
        
if __name__ == "__main__":
    dict_file = '/Users/yanting/Desktop/word_length/abbr_dict/new_abbr_dict.txt'
    prob_file = '/Users/yanting/Desktop/word_length/probs/prob_line_newpairs1024.csv'
    output_file = '/Users/yanting/Desktop/word_length/probs/prob_linenewpairs1024test.csv'
    #output_new_prob(prob_file, output_file)

    position_file = '/Users/yanting/Desktop/word_length/probs/position_full_newpairs1024.csv'
    probpos_file = '/Users/yanting/Desktop/word_length/probs/probpos_linenewpairs1024.csv'
    prob = read_prob_file(prob_file)
    position = read_position_file(position_file)
    if len(prob) == len(position):
        combine_prob_pos(prob, position, probpos_file)
        
    