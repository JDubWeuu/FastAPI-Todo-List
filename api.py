from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/get_user/<user_id>")
def get_user(user_id):
    # dictionary to store user data when we retrieve it based on passed in user_id
    user_data = {
        "user_id": int(user_id),
        "name": "John Doe",
        "email": "johndoe@example.com",
        "extra": False
    }
    # strip the quotes away, because it converts it to a string anyways
    extra = request.args.get("extra", "false").strip(' " ')
    print(type(extra))
    if extra.lower() == "true":
        user_data["extra"] = True
    return jsonify(user_data), 200

@app.route("/create_user", methods=["POST"])
def create_user():
    data = request.get_json()

    return jsonify(data), 201


# run our Flask server and set it up
if __name__ == "__main__":
    app.run(debug=True)

#GET, POST, PUT, DELETE
