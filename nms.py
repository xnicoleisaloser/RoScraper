from fastapi import FastAPI, Response

app = FastAPI()


@app.get('/')
def root():
    return Response('Success')


@app.get('/ping')
def ping():
    return Response('Success')


@app.get('/instructions')
def instructions():
    return Response('Success')
