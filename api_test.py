import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Scale, HORIZONTAL
import requests
from io import BytesIO
from PIL import Image, ImageTk, ImageDraw, ImageFilter
import json
import time
import threading

# Set your PixAI API key here
_api_key = 'your_pixai_api_key_here'
_url = 'https://api.pixai.art/graphql'

def handler(request_text):
    if 'errors' in json.loads(request_text):
        messagebox.showerror("Error", json.loads(request_text)['errors'][0]['message'])
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
        handler(data.text)
        return json.loads(data.text)
    except requests.exceptions.RequestException as E:
        messagebox.showerror("Request Exception", str(E))

def get_pic_mediaid(taskId):
    try:
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
        handler(data.text)
        mediaid_list = []
        output = json.loads(data.text)['data']['task']['outputs']
        if 'batch' in output:
            for i in output['batch']:
                mediaid_list.append(i['mediaId'])
        else:
            mediaid_list.append(output['mediaId'])
        return mediaid_list
    except requests.exceptions.RequestException as E:
        messagebox.showerror("Request Exception", str(E))

def get_pic(mediaId, img_label):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + _api_key
    }
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
            handler(data.text)
            urlpic = json.loads(data.text)['data']['media']['urls'][0]['url']
            imgresponse = requests.get(urlpic)
            img_data = imgresponse.content
            img_io = BytesIO(img_data)
            img = Image.open(img_io)
            img.thumbnail((400, 600))
            img = ImageTk.PhotoImage(img)
            img_label.config(image=img)
            img_label.image = img
        except requests.exceptions.RequestException as E:
            messagebox.showerror("Request Exception", str(E))

def format_tag(prompt, model, negativeprompt, samplingSteps, samplingMethod, cfgScale, width, height, batchSize):
    model_list = {
        'AnythingV5': "1648918115270508582",
        'Moonbeam': '1648918127446573124',
        'Whimsical': '1648918121624879157',
        'Neverland': '1648918123654922298',
        'Shinymood': '1668725869389316083',
        'Hassaku': '1648918119460618288',
        'Pixai Diffusion (CG)': '1684657781067182082',
        'Animagine XL V3': '1702058694023647156',
        'Sunflower': '1709400693561386681'
    }
    model_id = model_list.get(model, '1648918115270508582')

    gendata = {
        "prompts": prompt,
        "enableTile": False,
        "negativePrompts": negativeprompt,
        "samplingSteps": samplingSteps,
        "samplingMethod": samplingMethod,
        "cfgScale": cfgScale,
        "modelId": model_id,
        "width": width,
        "height": height,
        "batchSize": batchSize,
        "lora": {}
    }
    return gendata

def on_generate():
    prompt = prompt_entry.get()
    negativeprompt = negativeprompt_entry.get()
    model = model_combobox.get()
    samplingSteps = sampling_steps_scale.get()
    samplingMethod = sampling_method_combobox.get()
    cfgScale = cfg_scale_scale.get()
    width = int(width_entry.get())
    height = int(height_entry.get())
    batchSize = int(batch_size_entry.get())

    parameter = format_tag(prompt, model, negativeprompt, samplingSteps, samplingMethod, cfgScale, width, height, batchSize)
    task_response = gen_pic(parameter)
    task_id = task_response['data']['createGenerationTask']['id']
    messagebox.showinfo("Task ID", f"Task ID: {task_id}")
    time.sleep(20)  # Wait for a sufficient time to allow image generation
    media_ids = get_pic_mediaid(task_id)
    if media_ids:
        get_pic(media_ids, image_label)

def create_gradient(width, height, color1, color2):
    base = Image.new('RGB', (width, height), color1)
    top = Image.new('RGB', (width, height), color2)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        for x in range(width):
            mask_data.append(int(255 * (y / height)))
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def animate_background():
    colors = [("#ff0000", "#ff7f00"), ("#ff7f00", "#ffff00"), ("#ffff00", "#00ff00"), 
              ("#00ff00", "#0000ff"), ("#0000ff", "#4b0082"), ("#4b0082", "#8b00ff"), 
              ("#8b00ff", "#ff0000")]
    color_index = 0
    while True:
        color1, color2 = colors[color_index]
        gradient = create_gradient(400, 600, color1, color2)
        gradient = gradient.filter(ImageFilter.GaussianBlur(15))
        gradient = ImageTk.PhotoImage(gradient)
        image_label.config(image=gradient)
        image_label.image = gradient
        color_index = (color_index + 1) % len(colors)
        time.sleep(1)  # Slow down the animation

# GUI setup
root = tk.Tk()
root.title("PixAI Image Generator")
root.geometry("1000x600")

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

controls_frame = ttk.Frame(frame)
controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

image_frame = ttk.Frame(frame)
image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

image_label = tk.Label(image_frame, width=50, height=30, relief="solid")
image_label.pack(pady=5, padx=5, expand=True, fill=tk.BOTH)

ttk.Label(controls_frame, text="Prompt").pack(pady=5)
prompt_entry = ttk.Entry(controls_frame, width=50)
prompt_entry.pack(pady=5)

ttk.Label(controls_frame, text="Negative Prompt").pack(pady=5)
negativeprompt_entry = ttk.Entry(controls_frame, width=50)
negativeprompt_entry.pack(pady=5)

ttk.Label(controls_frame, text="Model").pack(pady=5)
model_combobox = ttk.Combobox(controls_frame, values=["AnythingV5", "Moonbeam", "Whimsical", "Neverland", "Shinymood", "Hassaku", "Pixai Diffusion (CG)", "Animagine XL V3", "Sunflower"], width=47)
model_combobox.set("AnythingV5")
model_combobox.pack(pady=5)

ttk.Label(controls_frame, text="Sampling Steps").pack(pady=5)
sampling_steps_scale = Scale(controls_frame, from_=1, to_=50, orient=HORIZONTAL)
sampling_steps_scale.set(12)
sampling_steps_scale.pack(pady=5)

ttk.Label(controls_frame, text="Sampling Method").pack(pady=5)
sampling_method_combobox = ttk.Combobox(controls_frame, values=["Euler a", "Euler", "DDIM", "LMS"], width=47)
sampling_method_combobox.set("Euler a")
sampling_method_combobox.pack(pady=5)

ttk.Label(controls_frame, text="CFG Scale").pack(pady=5)
cfg_scale_scale = Scale(controls_frame, from_=1, to_=20, orient=HORIZONTAL)
cfg_scale_scale.set(5)
cfg_scale_scale.pack(pady=5)

ttk.Label(controls_frame, text="Width").pack(pady=5)
width_entry = ttk.Entry(controls_frame, width=50)
width_entry.pack(pady=5)

ttk.Label(controls_frame, text="Height").pack(pady=5)
height_entry = ttk.Entry(controls_frame, width=50)
height_entry.pack(pady=5)

ttk.Label(controls_frame, text="Batch Size").pack(pady=5)
batch_size_entry = ttk.Entry(controls_frame, width=50)
batch_size_entry.pack(pady=5)

generate_button = ttk.Button(controls_frame, text="Generate Image", command=on_generate)
generate_button.pack(pady=20)

# Start the background animation
threading.Thread(target=animate_background, daemon=True).start()

root.mainloop()
