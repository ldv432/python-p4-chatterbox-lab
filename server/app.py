from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    try:
        if request.method == 'GET':
            messages = Message.query
            return make_response([message.to_dict() for message in messages], 200)
        else:
            #1. Retrieve data from the request body (JSON)
            data = request.get_json()
            #2. Instantiate a message object (use Message class) and pass info along
            new_message = Message(body=data.get("body"), username=data.get("username"))
            #3. add the object to the session for tracking (and automatic SQL statement creation)
            db.session.add(new_message)
            #4. Commit to the bit
            db.session.commit()
            #5. return what was created!
            return make_response(new_message.to_dict(), 201)
    except Exception as e:
        return make_response({'error': str(e)})


@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    try:
        message = db.session.get(Message, id)
        if request.method == "PATCH":
            data = request.get_json()["body"]
            message.body = data
            db.session.add(message)
            db.session.commit()
            return make_response(message.to_dict(), 200)
        elif request.method == "DELETE":
            db.session.delete(message)
            db.session.commit()
            response_body = {
                "delete_successful": True,
                "message": "Message deleted."
            }
            return make_response(response_body, 200)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5555)
