from pydantic import create_model
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer, MarianMTModel, MarianTokenizer
import torch
import translate_inference.config as cfg
import translate_inference.Sentence_spliting as senSplit
import math
import ctranslate2
import re

device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')


def split_doc(src_text):
    list_token = ['\t', '\r\n', '\\n', '\n', "[#STOP0#]", "[#STOP1#]", "[#STOP2#]", "[#STOP3#]", "[#STOP4#]",
                  "[#STOP5#]", "[#STOP6#]", "[#STOP7#]", "[#STOP8#]", "[#STOP9#]"]
    # out = []
    current = [src_text]

    for i in list_token:
        temp = []
        for j in current:
            temp.extend(j.split(i))
        current = temp

    c = []
    for i in current:
        if i.strip() != '':
            c.append(i.strip())

    current = c

    list_punctuation = [src_text[0:src_text.find(current[0])]]

    idX = 0
    for i in range(len(current) - 1):
        st_index = src_text[idX:].find(current[i]) + len(current[i]) + idX
        list_punctuation.append(src_text[st_index: src_text[st_index:].find(current[i + 1]) + st_index])
        idX = src_text[st_index:].find(current[i + 1]) + st_index

    list_punctuation.append(src_text[src_text[idX:].find(current[-1]) + len(current[-1]) + idX:])

    return list_punctuation, current


list_bracket = ['\'', '"']


def remove_rebudant_bracket(text):
    for i in list_bracket:
        text = re.sub('' + i + r'\s*(.*?)\s*' + i + '', r'"\1"', text)
    text = re.sub(r'\[\s*(.*?)\s*\]', r'[\1]', text)
    text = re.sub(r'\(\s*(.*?)\s*\)', r'(\1)', text)
    text = re.sub(r'\{\s*(.*?)\s*\}', r'{\1}', text)
    text = text.replace(' . ', '. ').replace(' , ', ', ').replace(' ? ', '? ').replace(' ; ', '; ')
    return text


def translate_sentece(src_text, model, tokenizer, src_lang, max_splited_length):
    list_punctuation, current = split_doc(src_text)

    sentence = []
    index_num_sequence_in_doc = []
    for i in current:
        temp_sent = senSplit.truncate(i, src_lang, max_splited_length)
        sentence.extend(temp_sent)
        index_num_sequence_in_doc.append(len(temp_sent))

    tokenizer.src_lang = src_lang

    translated_ = []
    for i in sentence:
        source = tokenizer.convert_ids_to_tokens(tokenizer.encode(i))
        target_prefix = [tokenizer.lang_code_to_token["vi"]]
        results = model.translate_batch([source], target_prefix=[target_prefix], beam_size=5)
        target = results[0].hypotheses[0][1:]
        translated_.append(remove_rebudant_bracket(tokenizer.decode(tokenizer.convert_tokens_to_ids(target))))

    result = list_punctuation[0]
    num = 0
    currentID = 0
    for index, i in enumerate(translated_):
        if sentence[index].strip() != '':
            result += translated_[index] + ' '
        else:
            result += i + ' '
        num += 1

        if num == index_num_sequence_in_doc[currentID]:
            num = 0
            currentID += 1
            result += list_punctuation[currentID]

    return result.replace('_', ' ')


class many2vi:
    def __init__(self, src_lang):
        self.src_lang = src_lang
        self.model_name = cfg.MANY2VI[src_lang]['model_dir']
        self.max_length = cfg.MANY2VI[src_lang]['max_length']
        self.model = ctranslate2.Translator(self.model_name, device="cuda")
        self.tokenizer = M2M100Tokenizer.from_pretrained(cfg.TOKENIZER, padding=True)

    def infer(self, sentence, src_lang: str = ""):
        if src_lang == "":
            src_lang = self.src_lang
        return translate_sentece(sentence, self.model, self.tokenizer, src_lang, self.max_length)


# if __name__ == '__main__':
#     a = many2vi('other')
#     print(a.infer('hi', 'de'))
#     b = many2vi('en')
#     print(b.infer('hi'))
#     c = many2vi('zh')
#     print(c.infer('你好'))
