from flask import Flask, request, abort
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import logging
import json
import os

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
YOUR_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

current_directory = os.path.dirname(os.path.abspath(__file__))  
log_file_path = os.path.join(current_directory, 'line.log')  

logger = logging.getLogger('line')
logger.setLevel(logging.DEBUG)
logging.getLogger('line.http').setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S')
handler_file = logging.FileHandler(log_file_path, encoding='utf-8')
handler_file.setFormatter(formatter)
logger.addHandler(handler_file)
print(f"The log file is located at: {log_file_path}")

@app.route("/", methods=['POST'])
def linebot():
    body = request.get_data(as_text=True)
    try:
        signature = request.headers['X-Line-Signature']
        handler.handle(body, signature)
        json_data = json.loads(body)
        events = json_data['events']
        for event in events:
            if event['type'] == 'message' and event['message']['type'] == 'text':
                reply_token = event['replyToken']
                message_text = event['message']['text']
                logger.debug(f'Received message: {message_text}')
                line_bot_api.reply_message(reply_token, TextSendMessage(text=message_text))
    except InvalidSignatureError as e:
        abort(400)
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        logger.error(body)
    return 'OK'

if __name__ == "__main__":
    app.run()
