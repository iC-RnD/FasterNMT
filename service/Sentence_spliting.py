import config as cfg
from nltk import sent_tokenize as en_sent_tokenize
from polyglot.text import Text
import re


def breakdown_long_sentence_anotherlanguage(sentence_ls, max_length):
    max_length = int(max_length)
    res = []
    for sentence in sentence_ls:
        blob = Text(sentence.replace(' ', '_'))
        word_ls = blob.words
        word_ls = [str(i) for i in word_ls]
        for i in range(0,len(word_ls),max_length):
            res.append(''.join(word_ls[i:i+max_length]).replace('_', ' '))
    return res
def safe_truncate_another_text(text:str, max_length):

    text = Text(text)
    sentence_ls = []
    for sent in text.sentences:
        sent = re.sub(r'\s+', ' ', str(sent)).strip()
        sentence_ls.append(str(sent))
    
    sentence_ls = breakdown_long_sentence_anotherlanguage(sentence_ls, max_length)

    return sentence_ls

def breakdown_long_sentence(sentence_ls, max_length):
    max_length = int(max_length)
    res = []
    for sentence in sentence_ls:
        word_ls = sentence.split(' ')
        word_ls = [str(i) for i in word_ls]
        for i in range(0,len(word_ls),max_length):
            res.append(' '.join(word_ls[i:i+max_length]))
    return res


def safe_truncate_text(input_e, max_length):  

    sentence_ls = en_sent_tokenize(input_e)
    sentence_ls = breakdown_long_sentence(sentence_ls, max_length)
    return sentence_ls


#Split sentence
def truncate(text: str, src_lang, max_length):
    if src_lang in cfg.LIST_LANGUAGES:
        if src_lang == 'en':
            return safe_truncate_text(text, max_length)
        if src_lang == 'zh':
            return safe_truncate_another_text(text, max_length)
    else:
        print('Wrong language, Check check!')
        return 

