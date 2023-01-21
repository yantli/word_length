# To analyze data generated from context_1100samples.csv
# Yanting Li
# 1/20/2023

library(tidyverse)
library(dplyr)

logprob_1100 <- read_delim("prob_1100samples.csv", locale=locale(encoding="UTF-8"), 
                        col_names = c("target_word",
                                      "word_form",
                                      "target_word_logprob",
                                      "disj_logprob",
                                      "line_num"))

