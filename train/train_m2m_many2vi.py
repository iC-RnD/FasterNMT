import argparse
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from underthesea import word_tokenize
import os
import torch
import numpy as np
from torch.utils.data import random_split
import pickle
from transformers import AutoModelForSeq2SeqLM, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from datasets import load_dataset
from datasets import load_metric
from vncorenlp import VnCoreNLP
import time
import random
from tqdm import tqdm

#ignore if segmentation is not nesscesary
rdrsegmenter = VnCoreNLP("path to VnCoreNLP jar", annotators="wseg", max_heap_size='-Xmx500m')

def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--load_data', action='store_true', help="Whether to loading data.")
    parser.add_argument('--model', default='facebook/m2m100_418M')
    parser.add_argument("--max_len", default=256, type=int, help="maximum length of input")
    parser.add_argument("--save_step", default=500, type=int)
    parser.add_argument("--epochs", default=1, type=int)
    parser.add_argument("--save_total_limit", default=3, type=int)
    parser.add_argument('--src_lang')
    parser.add_argument('--tgt_lang', default='vi')
    parser.add_argument('--file_train', default='data_pkl/train')
    parser.add_argument('--file_eval', default='data_pkl/eval')
    parser.add_argument('--dir_data')
    parser.add_argument("--batch_size", default=16, type=int)

    args = parser.parse_args()
    return args

# data_collator = DataCollatorForSeq2Seq(tokenizer, model = model)


def postprocess_text(preds, labels):
    preds = [pred.strip() for pred in preds]
    labels = [[label.strip()] for label in labels]
    return preds, labels

def compute_metrics(eval_preds):
    print('Start to compute metrics')
    preds, labels = eval_preds
    if isinstance(preds, tuple):
        preds = preds[0]
    decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
    # Replace -100 in the labels as we can't decode them.
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)
    # Some simple post-processing
    decoded_preds, decoded_labels = postprocess_text(decoded_preds, decoded_labels)
    result = metric.compute(predictions=decoded_preds, references=decoded_labels)
    result = {"bleu": result["score"]}
    prediction_lens = [np.count_nonzero(pred != tokenizer.pad_token_id) for pred in preds]
    result["gen_len"] = np.mean(prediction_lens)
    result = {k: round(v, 4) for k, v in result.items()}
    print(result)
    return result



def check(args):
    path = f"finetuned-{args.src_lang}-to-{args.tgt_lang}"
    if os.path.isdir(path):
        print('ERRORS!!!  Path for saving is exists')
        os._exit(0)
    
    if os.path.isdir(args.file_train) and args.load_data:
        print('WARNING!!!  you are overwriting an existing file')
        check = input('Do you want to continue (y/n)')
        if check != 'y':
            print('Path is exists')
            os._exit(0)
    
    if args.model == 'facebook/m2m100_418M':
        print('WARNING!!! you are using default model from huggingface')
    


if __name__ == "__main__":
    torch.set_num_threads(40)
    args = args_parser()
    print(args)
    check(args)
    batch_size = args.batch_size #batch_size=8 -> 22Gb
    source_lang = args.src_lang
    target_lang = args.tgt_lang
    max_len = args.max_len

    '''
    Loading dataset
    '''
    if args.load_data:
        data = []
        print('Reading dataset...')

        with open(args.file_train) as f1, open(args.file_eval) as f2:

                for src, tgt in tqdm(zip(f1, f2)):
                    word_segmented_texts = rdrsegmenter.tokenize(tgt)
                    data.append(
                        {
                            "translation": {
                                args.src_lang: src.strip(),
                                # args.tgt_lang: tgt.strip()
                                args.tgt_lang: (' '.join([' '.join(x) for x in word_segmented_texts])).strip()
                            }
                        }
                    )
                    
        print(f'total size of data is {len(data)}')

        # split = 0.1
        n = len(data)
        percentage = 0.99
        train_dataset, eval_dataset = random_split(data, lengths=[int(n*percentage), n-int(n*percentage)])


        '''
            Saving dataset
        '''
        # print(train_dataset)
        file_train = open(args.file_train,'wb')
        file_eval = open(args.file_eval,'wb')
        pickle.dump(train_dataset, file_train)
        pickle.dump(eval_dataset, file_eval)
        file_train.close()
        file_eval.close()
    if not args.load_data:
        print('Loading dataset.......................')

        file_train = open(args.file_train,'rb')
        train_dataset = pickle.load(file_train)
        file_eval = open(args.file_eval,'rb')
        eval_dataset = pickle.load(file_eval)

        print(len(train_dataset))
        print(len(eval_dataset))


    metric = load_metric("sacrebleu")

    model_name = args.model
    model = M2M100ForConditionalGeneration.from_pretrained(model_name)
    tokenizer = M2M100Tokenizer.from_pretrained(model_name)

    args = Seq2SeqTrainingArguments(
        output_dir = f"finetuned-{source_lang}-to-{target_lang}",
        evaluation_strategy = "epoch",
        do_train  = True,
        learning_rate=1e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        weight_decay=0.01,
        save_steps= args.save_step,
        save_total_limit=args.save_total_limit,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
    )

    # tokenizer.save_pretrained('./m2m' + str(source_lang) + '2' + str(target_lang))

    print(len(train_dataset))

    def data_collator(features:list):
        MAX_LENGTH = max_len
        labels = [f["translation"][target_lang] for f in features]
        inputs = [f["translation"][source_lang] for f in features]

        batch = tokenizer.prepare_seq2seq_batch(src_texts=inputs, src_lang=source_lang, tgt_lang=target_lang, tgt_texts=labels, max_length=MAX_LENGTH, max_target_length=MAX_LENGTH)

        # if using huggingface5 => convert batch to this 
        # with tokenizer.as_target_tokenizer():
        #     batch = tokenizer(inputs, return_tensors='pt')

        for k in batch:
            batch[k] = torch.tensor(batch[k])
        return batch

    trainer = Seq2SeqTrainer(
        model,
        args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
