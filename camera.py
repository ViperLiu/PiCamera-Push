import websocket
try:
    import thread
except ImportError:
    import _thread as thread
from pushbullet import Pushbullet
import json
from picamera import PiCamera
from time import sleep
import datetime

api_key = "<your_access_token>"
pb = Pushbullet(api_key)

def on_message(ws, message):
    print(message)
    res = json.loads(message)
    if res["type"] == "tickle" and res["subtype"] == "push":
        push = pb.get_pushes(limit = 1)[0]
        
        if push["type"] == "file" or push["dismissed"] == True:
            return

        print(push)
        if push["body"] == "pic":
            take_picture()

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    print("Connected !")

def take_picture():
    img_name = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_path = '<path_to_the_img>' + img_name + '.jpg'
    
    camera = PiCamera()
    camera.resolution = (2592, 1944)
    camera.framerate = 15
    camera.start_preview()
    sleep(3)
    camera.capture(full_path)
    camera.stop_preview()
    camera.close()
    
    with open(full_path, "rb") as pic:
        file_data = pb.upload_file(pic, img_name + '.jpg')

    push = pb.push_file(**file_data)

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.pushbullet.com/websocket/<your_access_token>",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()

