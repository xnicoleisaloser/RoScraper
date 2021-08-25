import re

from fastapi import FastAPI, Response, Request, Form
import logging

# Configure Logging
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

valid_uuids = ['test-system',
               'ligma',
               'tctcl']

app = FastAPI()


@app.get('/<{uuid}>')
def root(uuid: str):
    return Response('RoScraper v0.1')


@app.get('/ping/<{uuid}>')
def ping(uuid: str):
    return Response('Success')


@app.get('/commands/<{uuid}>')
def command(uuid: str):
    return Response('')


@app.middleware("http")
async def log_request(request: Request, call_next):
    ip = str(request.client.host)
    full_path = str(request.url).replace(str(request.base_url), '')
    start = full_path.find('<')
    end = full_path.find('>')
    uuid = full_path[start + 1:end]
    path = full_path[0:start]

    logger.info(f'{ip}, {uuid}, {path}')

    if uuid in valid_uuids:
        response = await call_next(request)
        return response
    else:
        return Response('UUID invalid', status_code=401)
