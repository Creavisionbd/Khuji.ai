from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def retrieve_messages():
	if(request.method == 'GET'):
		token = request.args.get("hub.verify_token")
		return verify_token(token)
	elif(request.method == 'POST'):
		output = request.get_json()
		for event in output['entry']:
			messaging = event['messaging']
			for message in messaging:
				if message.get('message'):
					recipient_id = message['sender']['id']
					if message['message'].get('text'):
						response_sent_text = generate_message ()
						message_send(recipient_id, response_sent_text)
					if message['message'].get('attachments'):	
						response_sent_nontext = generate_message()
						message_send(recipient_id, response_sent_nontext)
	return "Processed"

 

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5050)
