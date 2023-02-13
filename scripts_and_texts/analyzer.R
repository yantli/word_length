# Yanting Li
# 1/23/2023

library(tidyverse)
library(dplyr)
library(showtext)
showtext_auto()
library(lme4)
library(lmerTest)
library(ggplot2)
library(poolr)



load_data <- function(file) {
  logprob <- read_delim(file, locale=locale(encoding="UTF-8"), 
                       col_names = c("target_word",
                                     "concept",
                                     "word_form",
                                     "target_word_logprob",
                                     "disj_logprob",
                                     "line_num"))
  logprob$line_num <- as.factor(logprob$line_num)
  logprob$word_form <- as.factor(logprob$word_form)
  return(logprob)
}

data <- load_data("prob1312.csv")


# data %>% group_by(target_word, concept, word_form) %>% summarize(disj_logprob=mean(disj_logprob), target_word_logprob=mean(target_word_logprob)) %>% ungroup() %>% 
#   ggplot(aes(x=word_form, y=target_word_logprob, label=target_word, group=concept)) + geom_line() + geom_text() + theme_classic()

# data %>% group_by(target_word, concept, word_form) %>% summarize(disj_logprob=mean(disj_logprob), target_word_logprob=mean(target_word_logprob)) %>% 
#   ungroup() %>% spread(word_form, concept) %>% mutate(diff=short-long) %>% gather(word_form, target_word_logprob, short, long)

data %>% group_by(target_word, concept, word_form) %>% summarize(disj_logprob=mean(disj_logprob), target_word_logprob=mean(target_word_logprob)) %>% 
  ungroup() %>% select(-target_word, -target_word_logprob) %>% spread(word_form, disj_logprob) 

# means = data %>% group_by(target_word, concept, word_form) %>% summarize(disj_logprob=mean(disj_logprob), target_word_logprob=mean(target_word_logprob)) %>% ungroup() 
# using this can directly change logprob to surprisal
means = data %>% group_by(target_word, concept, word_form) %>% summarize(concept_surprisal=-mean(disj_logprob), target_word_surprisal=-mean(target_word_logprob)) %>% ungroup() 
head(means)

# the t test between mean_long_disj vs mean_short_disj
# t_test_data <- means %>% select(-target_word, -target_word_logprob) %>% spread(word_form, disj_logprob)
# t.test(t_test_data$long, t_test_data$short, paired = TRUE)

# the t test between mean_concept_surprisal_when_long_form_is_used vs mean_concept_surprisal_when_short_form_is_used
t_test_data <- means %>% select(-target_word, -target_word_surprisal) %>% spread(word_form, concept_surprisal)
t.test(t_test_data$long, t_test_data$short, paired = TRUE)
mean(t_test_data$long)
mean(t_test_data$short)

# plotting the difference in surprisal
# t_test_data %>% mutate(above_zero = (-long + short)>0) %>%
#   ggplot(aes(x=reorder(concept, (-long + short), mean), y= -long + short, label = concept, color=above_zero)) +
#   geom_point(size=3) + geom_text(angle = -45, hjust = 1.5, size = 3) + theme_classic() + labs(y="Difference in surprisal", x = 'Concept') + 
#   geom_hline(yintercept = 0) + theme(axis.ticks.x=element_blank(), axis.text.x=element_blank()) + guides(color=F) + scale_color_manual(values=c("red","blue" ))
t_test_data %>% mutate(above_zero = (long - short)>0) %>%
  ggplot(aes(x=reorder(concept, (long - short), mean), y= long - short, label = concept, color=above_zero)) +
  geom_point(size=3) + geom_text(angle = -45, hjust = 1.5, size = 3) + theme_classic() + labs(y="Difference in surprisal", x = 'Concept') + 
  geom_hline(yintercept = 0) + theme(axis.ticks.x=element_blank(), axis.text.x=element_blank()) + guides(color=F) + scale_color_manual(values=c("red","blue" ))


# plotting the word pairs against their surprisals and link each pair with a line. 
# Ideally we wish the slopes are mostly negative, i.e. going downward.
# plotdata = means %>% select(-target_word, -target_word_logprob) %>% spread(word_form, disj_logprob) %>% mutate(diff=short - long) %>% select(-short, -long) %>% inner_join(means)
# ggplot(plotdata, aes(x=word_form, y=-disj_logprob, label=target_word, group=concept)) + geom_line(aes(color = diff)) + geom_text(alpha = 0.5) + 
#   theme_classic() + scale_color_gradient2(low = "red", high = "blue") + labs(x="\nWord Form", y="Concept Surprisal (nats)\n", color="Surprisal\nDifference")
plotdata = means %>% select(-target_word, -target_word_surprisal) %>% spread(word_form, concept_surprisal) %>% mutate(diff= long-short) %>% select(-short, -long) %>% inner_join(means)
ggplot(plotdata, aes(x=word_form, y=concept_surprisal, label=target_word, group=concept)) + geom_line(aes(color = diff)) + geom_text(alpha = 0.5) + 
  theme_classic() + scale_color_gradient2(low = "red", high = "blue") + labs(x="\nWord Form", y="Concept Surprisal (nats)\n", color="Surprisal\nDifference")

# =================================================================================

# mixed model

disj <- data %>% select(-target_word, -target_word_logprob, -line_num) %>% mutate(surprisal = -disj_logprob) %>% mutate(is_short = ifelse(word_form == 'short', 0, 1))
disj$word_form <- as.factor(disj$word_form)

#mixed_ml <- glmer(if_short ~ 1 + disj_logprob + (1 + disj_logprob|concept), data = concept_disj_table, family = binomial)
# summary(mixed_ml)
mixed_ml2 <- glmer(word_form ~ 1 + surprisal + (1 + surprisal|concept), data = disj, family = binomial)
mixed_ml2 <- glmer(is_short ~ 1 + surprisal + (1 + surprisal|concept), data = disj, family = binomial)
summary(mixed_ml2)

# ============================================================================================

# Fisher's method

subconcept <- data %>% select(-target_word, -target_word_logprob, -line_num) %>% filter(concept == '东协')
sub_short <- subconcept %>% filter(word_form == 'short') %>% rename(short_disj = disj_logprob) %>% select(-word_form) %>% mutate(row = row_number())
sub_long <- subconcept %>% filter(word_form == 'long') %>% rename(long_disj = disj_logprob)%>% select(-word_form, -concept) %>% mutate(row = row_number())
combined <- full_join(sub_short, sub_long, by = "row")
t.test(combined$short_disj, combined$long_disj)

groups <- unique(data$concept)
ps <- data.frame(concept=unlist(groups))
pvalue <- c()
test_stats <- c()
for (i in 1:length(groups)) {
  group <- groups[i]                                                                                                                                                                              
  subdata <- subset(data, concept == group)
  p_value <- t.test(disj_logprob ~ word_form, data=subdata)$p.value
  t <- t.test(disj_logprob ~ word_form, data=subdata)[[1]]
  pvalue <- append(pvalue, p_value)
  test_stats <- append(test_stats, t )
}
ps$p_value <- unlist(pvalue)
ps$test_stats <- unlist(test_stats)
ps %>% filter(p_value < 0.05)
ps %>% filter(p_value < 0.05 & test_stats < 0)
ps %>% filter(p_value < 0.05 & test_stats > 0)
ps %>% filter(p_value < 0.05 & test_stats == 0)

fisher(ps$p_value)

# =================================================================================

# See if word length diff effect surprisal diff
means = data %>% group_by(target_word, concept, word_form) %>% summarize(disj_logprob=mean(disj_logprob), target_word_logprob=mean(target_word_logprob)) %>% ungroup() 
difftable = means %>% select(-target_word_logprob) %>% spread(word_form, disj_logprob)

t_test_data <- means %>% select(-target_word, -target_word_logprob) %>% spread(word_form, disj_logprob)
t.test(t_test_data$long, t_test_data$short, paired = TRUE)

# =================================================================================






# creating the mean_logprob_table containing 
# "concept", "short_words", "short_mean", "long_words", "long_mean"
concepts = c(unique(data$concept))
mean_logprob_table <- data.frame(matrix(nrow=100, ncol=1))
colnames(mean_logprob_table) <- "concept"
mean_logprob_table$concept <- concepts

df1 <- inner_join(mean_logprob_table, data, by = "concept")
df1_subset <- subset(df1, df1$word_form == "short")
short_words <- unique(df1_subset$target_word)
mean_logprob_table$short_words <- short_words

df1_grouped <- df1_subset %>% group_by(concept) %>% summarize(short_mean = mean(target_word_logprob))
mean_logprob_table <- merge(mean_logprob_table, df1_grouped, "concept")

df3 <- inner_join(mean_logprob_table, data, by = "concept")
df3_subset <- subset(df3, df3$word_form == "long")
long_words <- unique(df3_subset$target_word)
mean_logprob_table$long_words <- long_words

df3_grouped <- df3_subset %>% group_by(concept) %>% summarize(long_mean = mean(target_word_logprob))
mean_logprob_table <- merge(mean_logprob_table, df3_grouped, "concept")

ggplot(mean_logprob_table) +
  geom_point(aes(x=concept, y=short_mean), size=3) + 
  geom_point(aes(x=concept, y=long_mean), size=1) 


# =================================================================================

# creating the word_word_table containing 
# "words" containing both short and long words, "means", "if_short" (1 for yes and 0 for no)
short_table <- mean_logprob_table %>%
                    select(words = short_words, means = short_mean)
short_table$if_short <- replicate(100, 1)
long_table <- mean_logprob_table %>%
                    select(words = long_words, means = long_mean)
long_table$if_short <- replicate(100, 0)

word_mean_table <- dplyr::bind_rows(short_table, long_table)
word_mean_table$if_short <- as.factor(word_mean_table$if_short)

# creating the concept_disj_table containing 
# "concepts", "disj_prob", "if_short" (1 for yes and 0 for no)
df1_disj_grouped <- df1_subset %>% select(concept, disj_logprob) %>% group_by(concept) 
df1_disj_grouped$if_short <- replicate(4862, 1)

df3_disj_grouped <- df3_subset %>% select(concept, disj_logprob) %>% group_by(concept) 
df3_disj_grouped$if_short <- replicate(4958, 0)

concept_disj_table <- dplyr::bind_rows(df1_disj_grouped, df3_disj_grouped)
concept_disj_table$if_short <- as.factor(concept_disj_table$if_short)

# need to change means to disj_mean
head(plotdata)
t.test(plotdata$disj_logprob[plotdata$word_form=="short"], plotdata$disj_logprob[plotdata$word_form=="long"], a var.equal=TRUE)
model = lm(mean~if_short, data=word_mean_table)

# paired T test
t.test(mean_logprob_table$short_mean, mean_logprob_table$long_mean, paired=T)
boxplot(mean_logprob_table$short_mean, mean_logprob_table$long_mean)
ggplot(word_mean_table) +
  geom_boxplot(aes(x=if_short, y=mean)) +
  xlab("word_form") +
  ylab("logprob")
ggplot(word_mean_table, aes(x=if_short, y=means, label=words, group=words)) + geom_text() + geom_line()










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

zhongdonghetan <- filter(lpfreq, concept =='中东和谈') 

groups <- unique(lpfreq$concept)
ps <- data.frame(concept=unlist(groups))
pvalue <- c()
for (i in 1:length(groups)) {
  group <- groups[i]
  subdata <- subset(lpfreq, concept == group)
  p_value <- t.test(disj_logprob ~ word_form, data=subdata)$p.value
  print(p_value)
  pvalue <- append(pvalue, p_value)
}
ps$p_value <- unlist(pvalue)

good <- filter(ps, p_value < 0.05)

t_test_according_to_concept <- function(data) {
  groups <- unique(data$concept)
  ptable <- data.frame(concept=unlist(groups))
  pvalue <- c()
  for (i in 1:length(groups)) {
    group <- groups[i]
    subdata <- subset(data, concept == group)
    p_value <- t.test(disj_logprob ~ word_form, data=subdata)$p.value
    pvalue <- append(pvalue, p_value)
  }
  ptable$p_value <- unlist(pvalue)
  return(ptable)
}

significant_percentage <- function(data) {
  ptable <- t_test_according_to_concept(data)
  sig <- filter(ptable, p_value < 0.05)
  return(nrow(sig)/nrow(ptable))
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



# frequency: check a frequency dictionary
# t_test on dividual pairs