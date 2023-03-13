# to pick random 4-character and 2-character words from the entire corpus 
# so we can see if longer words in general carry more information than shorter words
# Yanting Li
# 3/5/2023

import csv
import jieba
import random
import re


# reading in the tokenized (by jieba) corpus and counting the appearance of each word
def create_word_dict(file):
    word_dict = {}
    with open(file, 'r', encoding = 'utf-8') as f:
        for line in f:
            for word in line.split():
                if word in word_dict.keys():
                    word_dict[word] += 1
                else:
                    word_dict[word] = 1
    return word_dict

# save the dictionary
def write_new_dict(dict_to_write, file):
    with open(file, 'w', encoding = 'utf-8') as output_f:
        for key, value in dict_to_write.items():
            pair = [key, str(value)]
            output_f.writelines('\t'.join(pair))
            output_f.writelines('\n')

def load_word_dict(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    word_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        word = pair[0]
        count = int(pair[1])
        word_dict[word] = count
    return word_dict

def load_abbr_dict(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    abbr_dict = {}
    for i in range(len(lines)):
        pair = lines[i].split()
        short = pair[0]
        long = pair[1]
        abbr_dict[short] = long
    return abbr_dict

# randomly pick num_to_select of words containing num_of_char that appeared no less than min_count times
def pick_word(abbr_dict, num_to_select, num_of_char, min_count):
    word_dict = load_word_dict('word_dict.txt')
    abbr_dict = load_abbr_dict('abbr_dict_100count_new.txt')
    qualified_dict = {}
    for word, count in word_dict.items():
        if len(word) == num_of_char and count >= min_count and word not in abbr_dict.items():
            qualified_dict[word] = count
    group_of_items = qualified_dict.keys()
    list_of_random_keys = random.sample(group_of_items, num_to_select)
   
    return list_of_random_keys





# putting all words that we selected into a giant regex
def regex_generator(dict_file, num_to_select, num_of_char_short, num_of_char_long, min_count):
    short_words = pick_word(dict_file, num_to_select, num_of_char_short, min_count)
    long_words = pick_word(dict_file, num_to_select, num_of_char_long, min_count)
    words_list = short_words + long_words
    regex = '('+'|'.join(words_list)+')'

    return regex

# looking for the news containing target words in the corpus
def find_context(string, line_num, dict_file, num_to_select, num_of_char_short, num_of_char_long, min_count):
    regex = regex_generator(dict_file, num_to_select, num_of_char_short, num_of_char_long, min_count)
    target_words = re.findall(regex, string)
    target_word_idx = [m.start() for m in re.finditer(regex, string)]
    context_list = []

    if len(target_word_idx) > 0:
        for num in range(len(target_word_idx)):
            target_word = target_words[num]
            i = target_word_idx[num]
            pre = string[:i].strip()
            post = string[(i + len(target_word)):].strip()
            tuple = (target_word, pre, post, line_num)
            context_list.append(tuple)
    
    return context_list

def save_context(context_list, file):
    context_list = find_context(string, line_num, dict_file, num_to_select, num_of_char_short, num_of_char_long, min_count)
    with open(file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerows(context_list)

# pick out contexts that contain target words
def context_screener(dict_file, num_to_select, context_file, output_file):
    target_words = pick_pair(dict_file, num_to_select)
    with open(context_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            if target_word in target_words:
                save_context(output_file, row)

# randomly pick 5 contexts for each word, i.e. 10 for each pair, 1000 in total
def randomized_word_picker(input_file, num_to_pick, output_file):
    context_dict = {}
    with open(input_file, 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            if target_word in context_dict:
                context_dict[target_word].append(row)
            else:
                context_dict[target_word] = [row]

    for key in context_dict:
        group_of_items = context_dict.get(key)
        list_of_random_context = random.sample(group_of_items, num_to_pick)
        for context in list_of_random_context:
            save_context(output_file, context)        

def save_context(file, row):
    with open(file, 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    context_screener('abbr_dict_100count_vo.txt', 56, 'context_cleaned.csv', 'context_100count_vo.csv')
    # randomized_context_picker('context_100count_newpairs.csv', 100, 'context_20000_newpairs.csv')
    with open('all_pure.txt', 'r', encoding = 'utf-8') as f:
        line_num = 0
        while True:
            string = f.readline()
            if not string:
                break;
            line_num += 1
            find_context(string, line_num, dict_file, num_to_select, num_of_char_short, num_of_char_long, min_count)
