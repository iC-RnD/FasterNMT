import uvicorn

if __name__ == '__main__':
    uvicorn.run("api:app", host="0.0.0.0", port=9900, workers=3)
