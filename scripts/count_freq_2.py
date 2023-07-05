# Take all untokenized texts from cmn_gw_5, find the short and long form 
# that appeared in the text, as well as the contexts proceeding & following them.
# Yanting Li
# 12/1/2022
 

import re
import csv

# def find_short_context(string, line_num, short_context_list):
#     for key in abbr_dict.keys():
#         # change key to the compiled regex (that includes both short and long forms?), string is still one line
#         key_idx = [m.start() for m in re.finditer(key, string)]
#         if len(key_idx) > 0:
#             for i in key_idx:
#                 pre = string[:i].strip()
#                 post = string[(i+len(key)):].strip()
#                 tuple = (key, 'short', pre, post, line_num)
#                 short_context_list.append(tuple)
#     return

# def find_long_context(string, line_num, long_context_list):
#     for value in abbr_dict.values():
#         value_idx = [m.start() for m in re.finditer(value, string)]
#         if len(value_idx) > 0:
#             for i in value_idx:
#                 pre = string[:i].strip()
#                 post = string[(i+len(value)):].strip()
#                 tuple = (value, 'long', pre, post, line_num)
#                 long_context_list.append(tuple)
#     return 

# the "topic" argument only applies to cluecommunity texts
def find_context(string, line_num, topic):
    context_list = []
    target_words = re.findall(regex, string)
    target_word_idx = [m.start() for m in re.finditer(regex, string)]
    if len(target_word_idx) > 0:
            for num in range(len(target_word_idx)):
                target_word = target_words[num]
                if target_word in abbr_dict.keys():
                    word_length = 'short'
                else:
                    word_length = 'long'
                i = target_word_idx[num]
                pre = string[:i].strip()
                post = string[(i + len(target_word)):].strip()
                tuple = (target_word, word_length, pre, post, line_num, topic)
                context_list.append(tuple)
    return context_list
    
# writing all contexts found in one news into a .csv file
# the "topic" argument only applies to cluecommunity texts
def string_to_csv(string, line_num, topic):
    context_list = find_context(string, line_num, topic)
    # with open('context_2.csv', 'a', newline='') as csvf:
    with open('/Users/yanting/Desktop/word_length/data/context_cluecommunity_w_topic.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerows(context_list)

    return 

# creating a dict to store short-long word pairs
def creating_abbr_dict():
    with open('/Users/yanting/Desktop/word_length/abbr_dict/abbr_list_full.txt', 'r', encoding = 'utf-8') as f:
        lines = f.readlines()

    abbr_dict = {}
    for i in range(len(lines)):
        if lines[i].startswith('n'):
            continue
        else:
            pair = lines[i].split(": ")
            short = pair[0]
            longlist = [i.strip() for i in re.split('/[a-z]+', pair[1].strip())]
            long = ''.join(longlist)
            if short in abbr_dict.keys():
                with open('abbr_list_overlap.txt', 'a', encoding = 'utf-8') as f:
                    f.write(short + '\t' + long + '\t' + abbr_dict[short] + '\n')
                del abbr_dict[short]
            else:
                abbr_dict[short] = long
    return abbr_dict
    # the dictionary contains 7455 pairs

if __name__ == "__main__":
    abbr_dict = creating_abbr_dict()
    # putting all words in the dict into a giant regex
    short_words = [key for key in abbr_dict.keys()]
    long_words = [value for value in abbr_dict.values()]
    words_list = short_words + long_words
    regex = '('+'|'.join(words_list)+')'

    # looking for short/long words in the text - when the input is a .txt file
    # with open('/Users/yanting/Desktop/word_length/corpora/cluecorpus/community_text/communitytest.txt', 'r', encoding = 'utf-8') as f:
    #     line_num = 0
    #     while True:
    #         string = f.readline()
    #         if not string:
    #             break;
    #         line_num += 1
    #         string_to_csv(string, line_num)

    # looking for short/long words in the text - when the input is a .csv file
    with open('/Users/yanting/Desktop/word_length/corpora/cluecorpus/community_text/community_w_topic.csv', 'r', encoding = 'utf-8') as f:
        filereader = csv.reader(f, delimiter = ',')
        for i, row in enumerate(filereader, start=1):
            topic = row[0]
            title = row[1]
            content = row[2]
            string = title + content
            string_to_csv(string, i, topic)

