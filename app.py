import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from libs.chatbot import Chatbot
from libs.utils import debug

# TODO: Remove ?
from dotenv import load_dotenv
load_dotenv()

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)

@app.event("message")
def handle_message_events(body, logger):
    print('Message received')
    event = body["event"]
    channel_type = event.get("channel_type")
    channel = event.get("channel")
    text = event.get("text")
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")

    if not text or event.get("subtype") or event.get("bot_id"):
        return 
   
    if channel_type == "im":
        try:
            hilo_conversacion = thread_ts or ts
            chatbot = Chatbot(body["event"].get("user"), 1, hilo_conversacion)
            response = chatbot.get_response(event.get("text"))
            response_message = app.client.chat_postMessage(
                channel=channel, 
                text=response, 
                thread_ts=hilo_conversacion
            )
            debug(event, 'event')
            debug(response_message, 'response_message')
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    else:
        response = f"Mensaje detectado en canal: {channel_type} {channel} revise el codigo del bot para ajustar la respuesta o contacte al administrador"
        # debug(event, 'event')
        app.client.chat_postMessage(channel=channel, text=response)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()

@app.event("app_mention")
def handle_app_mention_events(body, logger):
    logger.info(body)
    response = f"He detectado una mención en {body['event'].get('canal')}, pero aún no soy capaz de responder!"
    app.client.chat_postMessage(channel=body["event"].get("channel"), text=response)

@app.message("pichapelua") # remove in the future
def message_hello(message, say):
    say(f"Hey pichapelua <@{message['user']}>!")

@app.command("/flow1")
def handle_flow1_command(ack, body, respond, logger):
    ack()
    message_text = body.get('text', '')
    respond(f"Has activado el comando /flow1. {message_text}")

@app.command("/flow2")
def handle_flow2_command(ack, body, respond, logger):
    ack()
    message_text = body.get('text', '')
    respond(f"Has activado el comando /flow2. {message_text}")
