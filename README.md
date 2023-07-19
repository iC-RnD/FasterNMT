# FasterNMT
Neural Machine Translation (NMT) involves several stages: data preprocessing, model training, evaluation, and deployment with great performance.

## Installation and usage

CTranslate2 can be installed with pip:

```bash
pip install ctranslate2
```

The Python module is used to convert models and can translate or generate text with few lines of code:

```python
translator = ctranslate2.Translator(translation_model_path)
translator.translate_batch(tokens)

generator = ctranslate2.Generator(generation_model_path)
generator.generate_batch(start_tokens)
```

See the [documentation](https://opennmt.net/CTranslate2) for more information and examples.

## m2m100_418M

Convert model [m2m](https://huggingface.co/docs/transformers/model_doc/m2m_100) to CTranslate2

```bash
ct2-transformers-converter --model /dir_model_m2m --output_dir /dir_ct2model --quantization 'type'
```
The main entrypoint in Python is the **Translator** class which provides methods to translate files or batches as well as methods to score existing translations.
```python
import ctranslate2
import transformers

translator = ctranslate2.Translator("m2m100_418", device="cuda", compute_type="int8_float16")
tokenizer = transformers.AutoTokenizer.from_pretrained("facebook/m2m100_418M")
tokenizer.src_lang = "en"

source = tokenizer.convert_ids_to_tokens(tokenizer.encode("Hello iCOMM"))
target_prefix = [tokenizer.lang_code_to_token["de"]]
results = translator.translate_batch([source], target_prefix=[target_prefix])
target = results[0].hypotheses[0][1:]
tokenizer.decode(tokenizer.convert_tokens_to_ids(target))

```

172.16.10.240(GeForce RTX 2080 Ti)

| | Seconds per token | Max. V-RAM | Max. RAM | BLEU |
| --- | --- | --- | --- | --- |
| **m2m100_418M** | | | |
|  Pytorch(torch==1.9.0+cu111) | 0.02306 | 3889Mb | 4.4Gb | 39.0205 |
| **CTranslate2** (convert from zh2vi m2m100_418M model) | | | |
| auto | 0.00622 | 2319Mb | 1.8Gb | 39.0205 |
| int8 | 0.00397 | 847Mb | 2.1Gb | 39.6142 |
| float16 | 0.00479 | 1359Mb | 2.5Gb | 38.8939 |
| int8_float16 | 0.00474 | 847Mb | 2.13Gb | 39.9813 |

Executed with 2 threads
Note
<br>
// Create a CPU translator with 4 workers each using 1 thread:
translator = ctranslate2.Translator(model_path, device="cpu", inter_threads=4, intra_threads=1)

// Create a GPU translator with 4 workers each running on a separate GPU:
translator = ctranslate2.Translator(model_path, device="cuda", device_index=[0, 1, 2, 3])

// Create a GPU translator with 4 workers each using a different CUDA stream:
translator = ctranslate2.Translator(model_path, device="cuda", inter_threads=4)
