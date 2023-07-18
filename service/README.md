## Build docker
```
docker build -t translate-zh-en-to-vi .
<!-- docker run --rm --gpus 3 -it --name python translate-zh-en-to-vi bash -->
docker run -d --restart=always --name translate-zh-en-to-vi -p 1233:1233 --gpus '"device=3"' translate-zh-en-to-vi

```
