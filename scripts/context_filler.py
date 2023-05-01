# to make up for the entries thrown away in the process of cal_prob 
# so each word can have the equal number of entries
# 4/27/2023

import csv
import random
import math

def check_good_entry(prob_file):
    with open(prob_file, 'r', encoding = 'utf-8') as f:
        goodprob_dict = {}
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            word = row[0]
            # line = row[5]
            if word not in goodprob_dict.keys():
                goodprob_dict[word] = [row]
            else:
                goodprob_dict[word].append(row)
    
    return goodprob_dict

def entry_counter(prob_file):
    goodprob_dict = check_good_entry(prob_file)
    makeup_list = []
    for key, value in goodprob_dict.items():
        if len(value)<50:
            num = 50 - len(value)
            makeup_list.append(tuple([key, num]))
    
    return makeup_list

def backup_pool(prob_file, backup_context_file):
    goodprob_dict = check_good_entry(prob_file)
    makeup_list = entry_counter(prob_file)
    with open(backup_context_file, 'r', encoding = 'utf-8') as f:
        pool = []
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            word = row[0]
            if word in [item[0] for item in makeup_list]:
                pool.append(row)
        uniq_pool = []
        for row in pool:
            if row not in goodprob_dict.get(row[0]):
                uniq_pool.append(row)
        pool_dict = {}
        for row in uniq_pool:
            if row[0] not in pool_dict.keys():
                pool_dict[row[0]] = [row]
            else:
                pool_dict[row[0]].append(row)
    
    return pool_dict
 
def draw_backup(prob_file, backup_context_file, word, num_to_draw):
    pool_dict = backup_pool(prob_file, backup_context_file)
    group_of_items = pool_dict.get(word)
    backup_list = random.sample(group_of_items, num_to_draw)
    
    return backup_list

def collect_backup(prob_file, backup_context_file, num_of_entry):
    makeup_list = entry_counter(prob_file)
    pool_dict = backup_pool(prob_file, backup_context_file)
    all_backups = []
    for item in makeup_list:
        word = item[0]
        num_to_fill = item[1]
        if num_to_fill < 5:
            idea_num_to_draw = 10
        elif num_to_fill <= 15:
            idea_num_to_draw = 2 * num_to_fill
        else:
            idea_num_to_draw = 4 * num_to_fill
        num_available = len(pool_dict.get(word))
        num_to_draw = min(idea_num_to_draw, num_available)
        backup_list = draw_backup(prob_file, backup_context_file, word, num_to_draw)
        all_backups += backup_list

    return all_backups

def read_in_prob(prob_file):
    with open(prob_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        probs = []
        for row in filereader:
            probs.append(row)
    return probs

def combine_probs(original_prob_file, supp_prob_file):
    original_probs = read_in_prob(original_prob_file)
    supp_pool = read_in_prob(supp_prob_file)
    supp_probs = []

    makeup_list = entry_counter(original_prob_file)
    for item in makeup_list:
        word = item[0]
        num_to_draw = item[1]

        group_of_items = [line for line in supp_pool if line[0]==word]
        if len(group_of_items) >= num_to_draw:
            supp_list = random.sample(group_of_items, num_to_draw)
            # print([word, 'ok'])
        else:
            supp_list = group_of_items
            print([word, num_to_draw - len(group_of_items)])
        supp_probs += supp_list

    return sorted(original_probs + supp_probs)

def save_content(output_file, row):
    with open(output_file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    # save back_up contexts
    # rows = collect_backup('/Users/yanting/Desktop/word_length/probs/prob_lineoldpair200.csv', '/Users/yanting/Desktop/word_length/data/context_20000_oldpairs.csv', 50)
    # for row in rows:
    #     save_content('/Users/yanting/Desktop/word_length/data/context_oldpairsupp2.csv', row)
    
    # save back_up probs calculated using the back_up contexts
    rows = combine_probs('/Users/yanting/Desktop/word_length/probs/prob_lineoldpair200.csv', "/Users/yanting/Desktop/word_length/probs/prob_lineoldpairsupp2-200.csv")
    for row in rows:
        save_content('/Users/yanting/Desktop/word_length/probs/prob_oldpairfilled2-200.csv', row)    