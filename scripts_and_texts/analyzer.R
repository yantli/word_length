# To analyze data generated from context_1100samples.csv
# Yanting Li
# 1/20/2023

library(tidyverse)
library(dplyr)
library(showtext)
showtext_auto()

# loading logprob data
logprob_1100 <- read_delim("prob1100samples.csv", locale=locale(encoding="UTF-8"), 
                        col_names = c("target_word",
                                      "concept",
                                      "word_form",
                                      "target_word_logprob",
                                      "disj_logprob",
                                      "line_num"))
logprob_1100$line_num <- as.factor(logprob_1100$line_num)

long <-filter(logprob_1100, word_form == 'long')

ggplot(logprob_1100) +
  geom_point(aes(x=target_word, y=target_word_logprob, color=target_word), size=3, show.legend = FALSE) +
  facet_wrap(~ concept) +
  xlab("word") +
  ylab("surprisal")

ggplot(logprob_1100) +
  geom_point(aes(x=concept, y=target_word_logprob, color=target_word), size=3, show.legend = FALSE) +
  xlab("word") +
  ylab("surprisal")

ggplot(logprob_1100) +
  geom_point(aes(x=concept, y=target_word_logprob, color=as.factor(target_word)), size=3) +
  xlab("concept") +
  ylab("surprisal")


lapply(split(mtcars, factor(mtcars$cyl)), function(x)t.test(data=x, mpg ~ am, paired=FALSE))


