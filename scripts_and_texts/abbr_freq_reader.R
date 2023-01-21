# To check frequency counts for short and long forms
# Yanting Li
# 12/13/2022

library(tidyverse)
library(dplyr)

abbr_freq <- read_delim("abbr_freq.csv", locale=locale(encoding="UTF-8"), 
           col_names = c("short_form",
                         "short_count",
                         "long_form",
                         "long_count",
                         "short_long_ratio"))

arrange(abbr_freq, short_long_ratio) %>%
  print(n=400)
# starting from row 365, ratio >= 0.1

arrange(abbr_freq, desc(short_long_ratio)) %>%
  print(n=400)
# starting from row 158, ratio < 1000

arrange(abbr_freq, long_count) %>%
  print(n=1200)
# long forms with count of 1: 242
#                          2: 171 
#                          3: 136
#                          4: 104
#                          5: 112
#                          6: 69
#                          7: 84
#                          8: 81
#                          9: 69
#                      Total: 1068

arrange(abbr_freq, short_count) %>%
  print(n=900)
# short forms with count of 1: 68
#                           2: 72 
#                           3: 51
#                           4: 61
#                           5: 36
#                           6: 35
#                           7: 37
#                           8: 39
#                           9: 25
#                       Total: 424

ratio1 <- filter(abbr_freq, long_count < 10)
ratio1

balanced_ratio10 <- abbr_freq %>% 
  filter(short_count > 10) %>%
  filter(long_count > 10) %>%
  filter(short_long_ratio > 0.1) %>%
  filter(short_long_ratio < 10)

unbalanced_ratio10 <- anti_join(abbr_freq, balanced, by='short_form')

balanced_ratio100 <- abbr_freq %>% 
  filter(short_count > 10) %>%
  filter(long_count > 10) %>%
  filter(short_long_ratio > 0.1) %>%
  filter(short_long_ratio < 100)

unbalanced_ratio100 <- anti_join(abbr_freq, balanced, by='short_form')

write_csv(unbalanced_ratio10, "abbr_unbalanced10.csv")
write_csv(balanced_ratio10, "abbr_balanced10.csv")

# Propose to throw out:
# 1) pairs with either short_ and long_count <= 10
# 2) pairs with 0.1 < short_long_ratio < 10
# 3) wrong short form for long form by eyeballing

cleaned_abbr_freq <- read_delim("cleaned_abbr_freq.csv", locale=locale(encoding="UTF-8"), 
                        col_names = c("short_form",
                                      "short_count",
                                      "long_form",
                                      "long_count",
                                      "short_long_ratio"))
