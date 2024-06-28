import requests
from io import BytesIO
from PIL import Image
import json
import time

# Set your PixAI API key here
_api_key = 'your_pixai_api_key_here'
_url = 'https://api.pixai.art/graphql'

def handler(request_text):
    if 'errors' in json.loads(request_text):
        print('message:%s' % request_text['errors'][0]['message'])
        print('loc:%s' % request_text['errors'][0]['locations'])
        if 'path' in request_text['errors'][0]:
            print('path:%s' % request_text['errors'][0]['path'])
        print('extension code:%s' % request_text['errors'][0]['extensions']['code'])
        if 'data' in request_text:
            print('returned data:%s' % request_text['data'])
        raise ConnectionError('Error occurred when handling the request')

def gen_pic(parameter):
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
        }
        data = requests.post(_url, json={
            'query': """
            mutation createGenerationTask($parameters: JSONObject!) {
                createGenerationTask(parameters: $parameters) {
                    id
                }
            }
            """,
            'variables': {
                'parameters': parameter
            }
        }, headers=headers)
        print(data.text)
        handler(data.text)
        if 'data' in data.text:
            print(json.loads(data.text)['data']['createGenerationTask']['id'])
        return json.loads(data.text)
    except requests.exceptions.RequestException as E:
        print("Request Exception:")
        print(E)

def get_pic_mediaid(taskId):
    try:
        if 'data' in taskId:
            taskId = taskId['data']['createGenerationTask']['id']

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
        }
        getpic_data = {
            'query': """
            query getTaskById($id: ID!) { 
                task(id: $id) {
                    outputs
                }
            }
            """,
            'variables': {
                'id': str(taskId)
            }
        }
        data = requests.post(_url, headers=headers, json=getpic_data)
        print(data.text)
        handler(data.text)
        mediaid_list = []
        if not (json.loads(data.text)['data']['task']):
            print('Invalid task!')
            print("Maybe your pictures are not generated yet")
            return 0
        output = json.loads(data.text)['data']['task']['outputs']
        print('parameters:%s' % json.dumps(output['detailParameters'], indent=4))
        print('duration:%s s' % output['duration'])
        if 'batch' in output:
            for i in output['batch']:
                mediaid_list.append(i['mediaId'])
        else:
            mediaid_list.append(output['mediaId'])
        return mediaid_list
    except requests.exceptions.RequestException as E:
        print("Request Exception:")
        print(E)

def get_pic(mediaId):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + _api_key
    }
    if isinstance(mediaId, list):
        for id in mediaId:
            try:
                query = {
                    'query': """
                    query getMediaById($id: String!) {
                        media(id: $id) {
                            urls {
                                variant
                                url
                            }
                        }
                    }""",
                    'variables': {
                        'id': str(id)
                    }
                }
                data = requests.post(_url, headers=headers, json=query)
                print(data.text)
                handler(data.text)
                urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
                time.sleep(1)
                imgresponse = requests.get(urlpic)
                img_data = imgresponse.content
                img_io = BytesIO(img_data)
                img = Image.open(img_io)
                img.save('%s.jpg' % (str(mediaId.index(id)) + ("%02d_%02d_%02d" % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec))))
            except requests.exceptions.RequestException as E:
                print("Request Exception:")
                print(E)
    elif isinstance(mediaId, str) or isinstance(mediaId, int):
        if mediaId == 0 or mediaId == '0':
            return 0
        try:
            query = {
                'query': """
                query getMediaById($id: String!) {
                    media(id: $id) {
                        urls {
                            variant
                            url
                        }
                    }
                }""",
                'variables': {
                    'id': str(mediaId)
                }
            }
            data = requests.post(_url, headers=headers, json=query)
            print(data.text)
            handler(data.text)
            urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
            time.sleep(1)
            imgresponse = requests.get(urlpic)
            img_data = imgresponse.content
            img_io = BytesIO(img_data)
            img = Image.open(img_io)
            img.save('%s.jpg' % ("single" + ("%02d_%02d_%02d" % (time.localtime().tm_hour, time.localtime().tm_min, time.localtime().tm_sec))))
        except requests.exceptions.RequestException as E:
            print("Request Exception:")
            print(E)

def define_apikey(apikey):
    global _api_key
    _api_key = apikey
    try:
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + _api_key
        }
        query = {
            'query': """
            mutation createGenerationTask($parameters: JSONObject!) {
                createGenerationTask(parameters: $parameters) {
                    id
                }
            }""",
            'variables': {
                'parameters': {
                    "prompts": "1girl",
                    "negativePrompts": "(worst quality, low quality, large head, extra digits:1.4), easynegative",
                    "samplingSteps": 12,
                    "samplingMethod": "Euler a",
                    "cfgScale": 5,
                    "modelId": "1648918115270508582",
                    "width": 256,
                    "height": 384,
                    "batchSize": 4,
                }
            }
        }
        data = requests.post(_url, headers=headers, json=query)
        data_json = json.loads(data.text)
        if 'message' in data_json:
            print('Invalid token:')
            print("out:%s,code:%s" % (data_json['message'], data_json['code']))
        else:
            print('Successfully changed the API key')
            print('Test generated pic: task ID = %s, estimated credit: 200' % json.loads(data.text)['data']['createGenerationTask']['id'])
    except requests.exceptions.RequestException as E:
        print("Request Exception:")
        print(E)

def format_tag(prompt="1girl", model='AnythingV5', negativeprompt='(worst quality, low quality, large head, extra digits:1.4), easynegative', samplingSteps=12, samplingMethod="Euler a", cfgScale=5, width=512, height=768, batchSize=1, lora=None):
    if lora is None:
        lora = {}
    model_list = {('AnythingV5', "1648918115270508582"): "1648918115270508582",
                  ('Moonbeam', '1648918127446573124'): '1648918127446573124',
                  ('Whimsical', '1648918121624879157'): '1648918121624879157',
                  ('Neverland', '1648918123654922298'): '1648918123654922298',
                  ('Shinymood', '1668725869389316083'): '1668725869389316083',
                  ('Hassaku', '1648918119460618288'): '1648918119460618288',
                  ('Pixai Diffusion (CG)', '1684657781067182082'): '1684657781067182082',
                  ('Animagine XL V3', '1702058694023647156'): '1702058694023647156',
                  ('Sunflower', '1709400693561386681'): '1709400693561386681'
                  }
    samplingmethod_list = ['Euler a', 'Euler', 'DDIM', 'LMS', 'Restart', 'Heun', 'DPM2 Karras',
                           'DPM2 a Karras', 'DPM++ 2M Karras', 'DPM++ 2S a Karras', 'DPM++ SDEMKarras',
                           'DPM++ 2M SDEKarras']
    if samplingMethod not in samplingmethod_list:
        samplingMethod = 'Euler a'
        print('WARNING: wrong sampling method\nUsing default Euler a')
    model_out = None
    for models in list(model_list.keys()):
        if model in models:
            model_out = list(model_list.values())[list(model_list.keys()).index(models)]
    try:
        model_out = str(int(model))
    except ValueError:
        pass
    if not model_out:
        print("WARNING: invalid model\nUsing default AnythingV5")
        model_out = "1648918115270508582"

    gendata = {
        "prompts": prompt,
        "enableTile": False,
        "negativePrompts": negativeprompt,
        "samplingSteps": samplingSteps,
        "samplingMethod": samplingMethod,
        "cfgScale": cfgScale,
        "modelId": model_out,
        "width": width,
        "height": height,
        "batchSize": batchSize,
        "lora": lora
    }
    return gendata

# Example usage
if __name__ == "__main__":
    define_apikey('here')
    parameter = format_tag(prompt="A beautiful, vibrant sunset over the ocean")
    task_response = gen_pic(parameter)
    task_id = task_response['data']['createGenerationTask']['id']
    print(f"Task ID: {task_id}")
    time.sleep(20)  # Wait for a sufficient time to allow image generation
    media_ids = get_pic_mediaid(task_response)
    if media_ids:
        get_pic(media_ids)
