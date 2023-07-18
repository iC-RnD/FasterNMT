import uvicorn

import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

if __name__ == '__main__':
    uvicorn.run("service:app", host="0.0.0.0", port=8000, workers=1)
