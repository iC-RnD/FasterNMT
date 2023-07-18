## Build docker
```
docker build -t translate-zh-en-to-vi .
<!-- docker run --rm --gpus 3 -it --name python translate-zh-en-to-vi bash -->
docker run -d --restart=always --name translate-zh-en-to-vi -p 1233:1233 --gpus '"device=3"' translate-zh-en-to-vi

```

## Link model
172.16.10.240:
<br>
'en': "/home/data/linhnguyen/linhnguyen/CTranslate2_deploy1/translate-en-zh-vi/models/CT2en2vi"
<br>
'zh':"/home/data/linhnguyen/linhnguyen/CTranslate2_deploy1/translate-en-zh-vi/models/CT2zh2vi_WMTall"
<br>
TOKENIZER = '/home/data/linhnguyen/linhnguyen/CT2_B12/m2m100_418M'

#Test

CT2convert
```
ct2-transformers-converter --model facebook/m2m100_418M --output_dir translate-en-zh-vi/models/en-vi/ --quantization int8
ct2-transformers-converter --model facebook/m2m100_418M --output_dir translate-en-zh-vi/models/en-vi/ --quantization int8
```

Inference
```
CUDA_VISIBLE_DEVICES=0 python inference.py
```
