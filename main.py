
from flask import Flask, request, render_template, url_for
import os, logging
import sys
import urllib.request
import boto3
import requests
import json

logging.basicConfig(
    format="[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s",
    level = logging.INFO,
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ])
log = logging.getLogger('server')

log.info("Instantiating handler class and app ")

s3 = boto3.resource('s3')
client = boto3.client('rekognition')

def send_message(user_id, text):
    """Send the message text to recipient with id recipient.
    """

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params={"access_token": os.environ['FB_TOKEN']},
                      data=json.dumps({
                          "recipient": {"id": str(user_id)},
                          "message": {"text": str(text)},
                          "messaging_type": "RESPONSE"
                      }),
                      headers={'Content-type': 'application/json'})

    if r.status_code != requests.codes.ok:
        logging.error(
            "Encountered error {} with sending message to user {}".format(r.text, user_id))

def handlemsg(msg):
    userid = int(msg['sender']['id'])
    msg = msg['message']

    try:
        img = msg['attachments'][0]['payload']['url']
        file_ = urllib.request.urlretrieve(img)[0]
        bucket_name = os.path.join(*file_.split("/")[-3:])

        #need to have a bucket like test-imgs-fofo
        s3.Object('test-imgs-fofo',bucket_name).put(Body=open(file_, 'rb'))
        response = client.detect_labels(
                        Image={'S3Object': {'Bucket':'test-imgs-fofo','Name':bucket_name,}}, MaxLabels=5)
        
        labels = ", ".join([el['Name'] for el in response['Labels']])
        txt = f"My best guess there is: {labels}"
        send_message(userid, txt)
    except KeyError:
    	#no payload in attachment found
        send_message(userid, "I only want images now!")

    return


app = Flask(__name__)

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token")=="YOURVERIFICATIONTOKEN":
        return request.args["hub.challenge"], 200
    else:
        return "", 200

@app.route('/', methods=['POST'])
def parsemessage():
    incoming = request.get_json(force=True)
    log.info("received: {}".format(incoming))
    try:
        for entry in incoming["entry"]:
            for mess_event in entry["messaging"]:
                handlemsg(mess_event)
    except KeyError:
        log.error(f"Not a messaging type! - {request}")
    except TypeError:
        log.error(f"None type json object - {request}")

    return "OK",200

log.debug('Starting the app')

if __name__=='__main__':
    app.run(debug=False)
