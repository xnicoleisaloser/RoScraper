from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def root():
    return 'RoScraper NMS v0.1'


@app.get('/ping')
def ping():
    return 'Success'
