# to analyze the surprisal data
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
library(ggrepel)
library(broom)


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

data <- load_data("/Users/yanting/Desktop/word_length/probs/prob_line100newpairslong1024.csv")

load_fb_data <- function(file) {
  logprob <- read_delim(file, locale=locale(encoding="UTF-8"), 
                        col_names = c("target_word",
                                      "concept",
                                      "word_form",
                                      "forward_target_form_logprob",
                                      "forward_disj_logprob",
                                      "backward_target_form_logprob",
                                      "backward_disj_logprob",
                                      "line_num"))
  logprob$line_num <- as.factor(logprob$line_num)
  logprob$word_form <- as.factor(logprob$word_form)
  return(logprob)
}

fbdata <- load_fb_data("/Users/yanting/Desktop/word_length/probs/fb_prob_100newpairslong200.csv")
fb_surprisal <- fbdata %>% select(-target_word, -forward_target_form_logprob, -backward_target_form_logprob, -line_num) %>% mutate(forward_surprisal = -forward_disj_logprob) %>% mutate(backward_surprisal = -backward_disj_logprob) %>% mutate(is_short = ifelse(word_form == 'short', 0, 1))
mixed_mlfb <- glmer(is_short ~ 1 + forward_surprisal + backward_surprisal + (1 + forward_surprisal + backward_surprisal|concept), data = fb_surprisal, family = binomial)
summary(mixed_mlfb)

################# 
#for dealing with clue data only:
data <- data %>% group_by(target_word, concept, word_form) %>% filter(n() >= 50) %>% ungroup()
# this is to only look at data overlapping with the old pairs
oldpairs <- c('空运','和谈','国有企业','成飞','央行','男网','中央银行','汽车市场','管理委员会','中东和谈','石油市场','东协','专业人才','巴勒斯坦解放组织','外销','东南亚国家协会','网球协会','粮食援助','粮援','新加坡航空公司','油市','高级干部','修宪','国内资本','特别委员会','驾照','和平谈判','越战','修改宪法','男子网球','公平交易委员会','专才','报备','新航','飞安','西北航空公司','驾驶执照','中东和平谈判','飞行安全','网协','海缆','海底电缆','环境卫生','体育协会','高干','国际电信联盟','空中作战','管委','国家标准','时空','国企','学生运动','实际控制线','轻型卡车','越南战争','马列主义','补税','人口老化','股票价值','学运','科学仪器','吉大','空战','航空运输','童子军','童军','巴解组织','县府','政治体制改革','金市','女子柔道','内资','世界运动会','股值','财政年度','地价','无人驾驶飞机','土地价格','武大','游泳健将','深大','宣教','对外销售','运输能力','政改','男子曲棍球','童装','环卫','体协','公平会','展览馆','农科','防止贪污','电联','时间和空间','深圳证券交易所','农业科学','监委','高知','车市','无人机','国标','黄金市场','展馆','宣传教育','护校','监察委员会','运输管理','羽毛球协会','投入运行','财年','护士学校','运能','公路铁路','成人教育','西航','早期教育','美术学院','武汉大学','黄河水利委员会','心血管外科','运管','知识青年','亚冬会','科考队','成都飞机','扩招','黄委会','人口老龄化','深交所','参赌','参加赌博','直属机关','工美','马克思列宁主义','政策研究室','军事体育','知青','深圳大学','军体','县人民政府','实控线','吉林大学','牡丹信用卡','女柔','美院','工艺美术品','补交税款','联交所','高级知识分子','男子花剑','男花','欧洲航天局','香港联合交易所','尤伯杯','投运','防贪','扩大招生','男曲','亚洲冬季运动会','世俱杯','申报备案','心内科','纠风','科仪','公铁','帮贫','血吸虫病防治','血防','成教','纠正行业不正之风','科学考察队','沈阳铁路局','游将','早教','心外科','心血管内科','牡丹卡','羽协','沈铁','直机关','儿童服装','特委','专干','尤杯','轻卡','欧航局','世界俱乐部杯','武术协会','武协','政研室','打私','专职干部','打击走私活动','世运会','桥牌联合会','桥联','帮助贫困户','展览交易会','展交会')
data <- data[data$target_word %in% oldpairs,]
#################

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
################# 
# same step as above but for dealing with clue data only:
t_test_data <- means %>% select(-target_word, -target_word_surprisal) %>% spread(word_form, concept_surprisal)
t_test_data <- na.omit(t_test_data)
t.test(t_test_data$long, t_test_data$short, paired = TRUE)
mean(t_test_data$long)
mean(t_test_data$short)
#################

# to check which concepts changed the most:
longcontext <- means %>% select(-target_word, -target_word_surprisal) %>% spread(word_form, concept_surprisal) %>% mutate(diff200 = long - short)
shortcontext <- means %>% select(-target_word, -target_word_surprisal) %>% spread(word_form, concept_surprisal) %>% mutate(diff10 = long - short)
firstmerge <- merge(longcontext, shortcontext, by="concept") %>% mutate(change = diff200 - diff10)


# plotting the difference in surprisal
# t_test_data %>% mutate(above_zero = (-long + short)>0) %>%
#   ggplot(aes(x=reorder(concept, (-long + short), mean), y= -long + short, label = concept, color=above_zero)) +
#   geom_point(size=3) + geom_text(angle = -45, hjust = 1.5, size = 3) + theme_classic() + labs(y="Difference in surprisal", x = 'Concept') + 
#   geom_hline(yintercept = 0) + theme(axis.ticks.x=element_blank(), axis.text.x=element_blank()) + guides(color=F) + scale_color_manual(values=c("red","blue" ))
t_test_data %>% mutate(above_zero = (long - short)>0) %>%
  ggplot(aes(x=reorder(concept, (long - short), mean), y= long - short, label = concept, color=above_zero)) +
  geom_point(size=3) + geom_text(angle = -45, hjust = 1.5, size = 3) + theme_classic() + labs(y="Difference in surprisal", x = 'Concept') + 
  geom_hline(yintercept = 0) + scale_x_discrete(expand = c(0.02, 0.05)) + 
  scale_y_discrete(expand = c(1, 0)) + 
  #ylim(-6,6) +
  theme(axis.ticks.x=element_blank(), axis.text.x=element_blank()) + guides(color=F) + scale_color_manual(values=c("red","blue" ))

# plotting according to the review:
t_test_data %>% 
  mutate(diff = long - short) %>% mutate(above_zero = (long - short) > 0) %>%
  group_by(concept) %>%
  pivot_longer(cols = c("long", "short"), names_to = "form", values_to = "surprisal")  %>%
  ggplot(aes(x = reorder(concept, diff, mean), y = surprisal, color = form, group = interaction(concept, form))) +
  geom_point(size = 3) +
  geom_line(aes(group = interaction(concept, above_zero)), size = 0.5, color = "black") +
  theme_classic() +
  labs(y = "Surprisal", x = 'Concept') +
  scale_color_manual(values = c("blue", "red")) +
  theme(axis.ticks.x = element_blank(), axis.text.x = element_text(angle = 90, hjust = 1)) + 
  scale_x_discrete(labels = function(x) t_test_data$concept[match(x, t_test_data$concept)])

# try to add a vertical line
diffline <- t_test_data %>% 
  mutate(diff = long - short) %>% mutate(above_zero = if_else(diff > 0, "above 0", "below 0")) %>% mutate(long_sur = long) %>% 
  group_by(concept) %>%
  pivot_longer(cols = c("long", "short"), names_to = "form", values_to = "surprisal")  %>% arrange(long_sur)

diffline %>%
  ggplot(aes(x = reorder(concept, long_sur, mean), y = surprisal, group = concept)) +
  geom_point(aes(shape = form), size = 3) + 
  geom_line(aes(color = above_zero), size = 0.5) + 
  scale_shape_manual(values = c(16, 1)) +
  scale_color_manual(values = c("blue", "red")) +
#  geom_vline(xintercept = diffline$concept[which.max(diffline$diff > 0)]) + 
  theme_classic() +
  labs(y = "Surprisal", x = 'Concept (represented by the short forms)', color = "Surprisal difference \n (long - short)", shape = "Word form") +
  theme(axis.ticks.x = element_blank(), axis.text.x = element_text(angle = 90, hjust = 1)) + 
  scale_x_discrete(labels = function(x) diffline$concept[match(x, diffline$concept)])








t_test_data %>% mutate(above_zero = (long - short)>0) %>% filter(above_zero == TRUE)

t_test_data %>% mutate(above_zero = (long - short)>0) %>%
  ggplot(aes(x=reorder(concept, (long - short), mean), y= long - short, label = concept, color=above_zero)) +
  geom_point(size=3) + geom_text(angle = -45, hjust = 1.5, size = 3) + theme_classic() + labs(y="Difference in surprisal", x = 'Concept') + 
  geom_hline(yintercept = 0) + theme(axis.ticks.x=element_blank(), axis.text.x=element_blank()) + guides(color=F) + scale_color_manual(values=c("red","blue" )) +
  theme(axis.text.y = element_text(size = 20),
        axis.title.x = element_text(size = 20),
        axis.title.y = element_text(size = 20))
#ggsave("diff_plot.jpeg", scale = 4, width = 14, height = 2, units = c("cm"))
#geom_text_repel(nudge_x = -1.4, nudge_y = 1, segment.alpha = 0, angle = -45, size = 1)

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

################# 
# one more step for dealing with clue data only:
disj <- disj[disj$concept %in% t_test_data$concept,]
#################

#mixed_ml <- glmer(if_short ~ 1 + disj_logprob + (1 + disj_logprob|concept), data = concept_disj_table, family = binomial)
# summary(mixed_ml)
mixed_ml2 <- glmer(word_form ~ 1 + surprisal + (1 + surprisal|concept), data = disj, family = binomial)
mixed_ml2 <- glmer(is_short ~ 1 + surprisal + (1 + surprisal|concept), data = disj, family = binomial)
summary(mixed_ml2)

mixed_ml3 <- glm(is_short ~ 1 + surprisal, data = disj, family = binomial)
summary(mixed_ml3)
# ============================================================================================

# looking at token position
load_probpos_data <- function(file) {
  logprob <- read_delim(file, locale=locale(encoding="UTF-8"), 
                        col_names = c("target_word",
                                      "concept",
                                      "word_form",
                                      "target_word_logprob",
                                      "disj_logprob",
                                      "char_position_full",
                                      "tok_position_full",
                                      "char_position_fed",
                                      "tok_position_fed",
                                      "line_num"))
  logprob$line_num <- as.factor(logprob$line_num)
  logprob$word_form <- as.factor(logprob$word_form)
  return(logprob)
}

probpos <- load_probpos_data("/Users/yanting/Desktop/word_length/probs/probpos_line100newpairslong1024.csv")
probpos <- load_probpos_data("/Users/yanting/Desktop/word_length/probs/probpos_lineoldpairs1024.csv")
probpos <- load_probpos_data("/Users/yanting/Desktop/word_length/probs/probpos_linenewpairs1024.csv")

pos_disj <- probpos %>% select(-target_word, -target_word_logprob, -line_num) %>% mutate(surprisal = -disj_logprob) %>% mutate(is_short = ifelse(word_form == 'short', 0, 1))
pos_disj$word_form <- as.factor(pos_disj$word_form)

mixed_ml_pos <- glmer(is_short ~ 1 + surprisal + char_position_full + (1 + surprisal|concept), data = pos_disj, family = binomial)
summary(mixed_ml_pos)
mixed_ml_pos <- glm(is_short ~ 1 + surprisal * char_position_full, data = pos_disj, family = binomial)
summary(mixed_ml_pos)

ml_pos <- glm(is_short ~ 1 + surprisal * tok_position_fed, data = pos_disj, family = binomial)
summary(ml_pos)

effect_size_calculater <- function(n) {
  ml_pos <- glm(is_short ~ 1 + surprisal * tok_position_fed, data = filter(pos_disj, tok_position_fed==n), family = binomial)
  tidy(ml_pos) %>% filter(term == 'surprisal') %>% mutate('tok_position'=n)
}

effect_sizes <- bind_rows(map(unique(pos_disj$tok_position_fed), effect_size_calculater))
mean_estimate <- mean(effect_sizes$estimate, na.rm = TRUE)
sd_estimate <- sd(effect_sizes$estimate, na.rm = TRUE)
effect_sizes %>% filter(estimate >= mean_estimate - 3 * sd_estimate,
                        estimate <= mean_estimate + 3 * sd_estimate) %>% 
          ggplot(aes(x = tok_position, y = estimate, color = ifelse(p.value < 0.05, "S", "NS"))) + 
          geom_point() + theme_classic() + geom_hline(yintercept=0) + ylim(-0.5,0.5) + geom_smooth()
# throw away outliers, color significant results, look at words with a reasonable number of datapoints

pos_disj %>% mutate(position = cut_interval(tok_position_fed, 15)) %>%
              group_by(position, word_form) %>% 
              summarize(m=n()) %>% 
              ungroup %>% 
              spread(word_form, m) %>% 
              mutate(diff = long-short) %>%
              ggplot(aes(x=position, y= m)) + geom_point() + geom_line() + theme_classic() + geom_hline(yintercept=0)

pos_disj %>% mutate(surp = cut_interval(-disj_logprob, 15)) %>%
  group_by(surp) %>% 
  summarize(m=mean(word_form == 'long')) %>% 
  ungroup %>% 
  ggplot(aes(x=surp, y= m)) + geom_point() + geom_line() + theme_classic() + geom_hline(yintercept=0.5)















# Fisher's method

subconcept <- data %>% select(-target_word, -target_word_logprob, -line_num)
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