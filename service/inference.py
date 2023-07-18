from transformers import AutoTokenizer
import ctranslate2
import torch
import config as cfg
import Sentence_spliting as senSplit
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


def another_trans_index_list_punc(src_text, model, tokenizer, src_lang, max_splited_length):
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
        self.max_length = cfg.MANY2VI[src_lang]['max_length']
        self.model = ctranslate2.Translator(cfg.MANY2VI[src_lang]['model'], device="cuda")
        self.tokenizer = AutoTokenizer.from_pretrained(cfg.TOKENIZER)

    def infer(self, sentence):
        return another_trans_index_list_punc(sentence, self.model, self.tokenizer, self.src_lang, self.max_length)


if __name__ == '__main__':
    EN_translator = many2vi('en')
    ZH_translator = many2vi('zh')

    print(ZH_translator.infer(
        '新华社印度尼西亚巴厘岛11月15日电（记者刘华　余谦梁）当地时间11月15日，二十国集团领导人第十七次峰会在印度尼西亚巴厘岛举行。国家主席习近平出席并发表题为《共迎时代挑战　共建美好未来》的重要讲话。'))
    print(EN_translator.infer(
        'Five of the deceased victims were "identified by city officials" as Lorenzo Gamble; Brian Pendleton; Kellie '
        'Pyle; Randall Blevins; and Tyneka Johnson. The sixth deceased victim was a 16-year-old boy who authorities '
        'are not naming because he was a minor, the city said. They were all Walmart employees, a company '
        'spokesperson told CNN.'))

