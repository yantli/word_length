# Yanting Li
# 1/23/2023

library(tidyverse)
library(dplyr)
library(showtext)
showtext_auto()

lpfreq <- read_delim("prob10000samples.csv", locale=locale(encoding="UTF-8"), 
                           col_names = c("target_word",
                                         "concept",
                                         "word_form",
                                         "target_word_logprob",
                                         "disj_logprob",
                                         "line_num"))
lpfreq$line_num <- as.factor(lpfreq$line_num)
filteredata <- filter(lpfreq, word_form =='long') 
lpfreq$if_short <- c(as.factor(ifelse(lpfreq$word_form == 'short', 0, 1)))

ggplot(lpfreq) +
  geom_point(aes(x=word_form, y=disj_logprob, color = word_form)) + 
  facet_wrap(~ concept)



grouped <- group_by(lpfreq, concept)
arrange(grouped, concept)

p_values <- list()
groups <- unique(lpfull$concept)
for (i in 1:length(groups)) {
  group <- groups[i]
  subdata <- subset(lpfull, concept == group)
  p_values[[group]] <- t.test(disj_logprob ~ word_form, data=subdata)$p.value
}










# loading logprob data
logprob_1100 <- read_delim("prob1100samples.csv", locale=locale(encoding="UTF-8"), 
                           col_names = c("target_word",
                                         "concept",
                                         "word_form",
                                         "target_word_logprob",
                                         "disj_logprob",
                                         "line_num"))
logprob_1100$line_num <- as.factor(logprob_1100$line_num)
logprob_1100$if_short <- c(as.factor(ifelse(logprob_1100$word_form == 'short', 0, 1)))

ggplot(logprob_1100) +
  geom_point(aes(x=word_form, y=disj_logprob, color = word_form)) + 
  facet_wrap(~ concept)



grouped <- group_by(logprob_1100, concept)
arrange(grouped, concept)

p_values <- list()
groups <- unique(logprob_1100$concept)
for (i in 1:length(groups)) {
  group <- groups[i]
  subdata <- subset(logprob_1100, concept == group)
  p_values[[group]] <- t.test(disj_logprob ~ word_form, data=subdata)$p.value
}

