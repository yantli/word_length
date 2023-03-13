# for every piece of news, only keep the first appearance of the target words
# 3/8/2023

import csv

def save_context(row):
    with open('context_cleaned_firstapp.csv', 'a', newline='') as csvf:
        writer = csv.writer(csvf, delimiter = ',')
        writer.writerow(tuple(row))

if __name__ == "__main__":
    with open('context_cleaned.csv', 'r', encoding = 'utf-8') as f:
        tw_dict = {}
        filereader = csv.reader(f, delimiter = ',')
        for row in filereader:
            target_word = row[0]
            target_form = row[1]
            line_num = row[4]

            if target_word not in tw_dict.keys():
                tw_dict[target_word] = [line_num]
                # print(row)
                save_context(row)
            else: 
                if line_num not in tw_dict.get(target_word):
                    tw_dict.get(target_word).append(line_num)
                    # print(row)
                    save_context(row)

