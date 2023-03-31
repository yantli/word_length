# use Stanza to dependency parse texts
# 3/13/2023

import stanza

nlp = stanza.Pipeline('zh', processors='tokenize,pos,lemma,depparse')
doc = nlp('发展非国有企业和发展国有企业同样重要。')
doc2 = nlp('我昨天拿到了驾照。')
doc3 = nlp('我昨天拿到了驾驶执照。')
# dep_parse = doc.sentences[0].dependencies
parse_tree = doc.sentences[0].to_dict()
