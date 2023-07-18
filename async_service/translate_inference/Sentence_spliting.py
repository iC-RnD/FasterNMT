import translate_inference.config as cfg
# import config as cfg
from nltk import sent_tokenize as en_sent_tokenize
from polyglot.text import Text
from khmernltk import sentence_tokenize as km_sent_tokenize
from pythainlp.tokenize import sent_tokenize as th_sent_tokenize
import re

import functools
from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

def breakdown_long_sentence_hieroglyphs(sentence_ls, max_length):
    max_length = int(max_length)
    res = []
    for sentence in sentence_ls:
        
        blob = Text(sentence.replace(' ', '_'))
        word_ls = blob.words
        word_ls = [str(i) for i in word_ls]
        for i in range(0,len(word_ls),max_length):
            res.append(''.join(word_ls[i:i+max_length]).replace('_', ' '))
    return res

def breakdown_long_sentence(sentence_ls, max_length):
    max_length = int(max_length)
    res = []
    for sentence in sentence_ls:
        word_ls = sentence.split(' ')
        word_ls = [str(i) for i in word_ls]
        for i in range(0,len(word_ls),max_length):
            res.append(' '.join(word_ls[i:i+max_length]))
    return res


def safe_truncate_another_text(text:str, max_length, src_lang):

    text = Text(text)
    sentence_ls = []
    for sent in text.sentences:
        sent = re.sub(r'\s+', ' ', str(sent)).strip()
        sentence_ls.append(str(sent))
    
    if src_lang in ['lo', 'ko', 'zh']:
        sentence_ls = breakdown_long_sentence_hieroglyphs(sentence_ls, max_length)
    else:
        sentence_ls = breakdown_long_sentence(sentence_ls, max_length)

    return sentence_ls


def de_sent_tokenize(input_e):
    return en_sent_tokenize(input_e, "german")

def ru_sent_tokenize(input_e):
    return en_sent_tokenize(input_e, "russian")

def ja_sent_tokenize(input_e):
    split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
    concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$", remove_former_matched=False)
    segmenter = make_pipeline(normalize, split_newline, concat_tail_no, split_punc2) 
    return (segmenter(input_e))


def safe_truncate_text(input_e, max_length, src_lang):  
    if src_lang == 'en':
        sentence_ls = en_sent_tokenize(input_e)
    if src_lang == 'th':
        sentence_ls = th_sent_tokenize(input_e)
    if src_lang == 'km':
        sentence_ls = km_sent_tokenize(input_e)
    if src_lang == 'de':
        sentence_ls = de_sent_tokenize(input_e)
    if src_lang == 'ru':
        sentence_ls = ru_sent_tokenize(input_e)
    if src_lang == 'ja':
        sentence_ls = ja_sent_tokenize(input_e)

    if src_lang in ['th', 'km', 'ja']:
        sentence_ls = breakdown_long_sentence_hieroglyphs(sentence_ls, max_length)
    else:
        sentence_ls = breakdown_long_sentence(sentence_ls, max_length)
    return sentence_ls


# #Split sentence
# def truncate(text: str, src_lang, max_length):
#     if src_lang in cfg.LIST_LANGUAGES:
#         if src_lang in ['km', 'th', 'de', 'ru', 'ja']:
#             return safe_truncate_text(text, max_length, src_lang)
#         if src_lang in ['ms', 'id', 'lo', 'tl', 'ko']:
#             return safe_truncate_another_text(text, max_length, src_lang)
#     else:
#         print('Wrong language, Check check!')
#         return 


# Split sentence
def truncate(text: str, src_lang, max_length):
    if src_lang in cfg.LIST_LANGUAGES:
        if src_lang in ['en', 'km', 'th', 'de', 'ru', 'ja']:
            return safe_truncate_text(text, max_length, src_lang)
        if src_lang in ['zh', 'ms', 'id', 'lo', 'tl', 'ko']:
            return safe_truncate_another_text(text, max_length, src_lang)
    else:
        print('Wrong language, Check check!')
        return
