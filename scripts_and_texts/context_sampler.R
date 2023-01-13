# To randomly pick 1000 contexts from context_cleaned.csv
# Yanting Li
# 1/13/2023

library(tidyverse)
library(dplyr)

context <- read_delim("context_cleaned.csv", locale=locale(encoding="UTF-8"), 
                        col_names = c("word",
                                      "form",
                                      "pre_context",
                                      "post_context",
                                      "sent_num"))
