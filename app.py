
from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask.json import JSONEncoder
from bson import json_util
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os
load_dotenv()


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj): return json_util.default(obj)


app = Flask(__name__)

# client = MongoClient(os.getenv("HOST"), int(os.getenv("PORT")))
client = MongoClient(os.getenv("MONGODB_URI"))
db=client.flask
todos=db.todos


@ app.route('/')
def gets():
    data=[]
    for s in todos.find():
        data.append(
            {'_id': str(s['_id']), 'title': s['title'], 'description': s['description']})
    return jsonify({
        'status': 200,
        'todos': data
    })


@ app.route('/', methods=['POST'])
def post():
    req=request.json
    if req:
        savedTodo=todos.insert_one(req)
        return jsonify({
            "status": 201,
            "data": savedTodo.inserted_id
        })
    else:
        return jsonify({
            "status": 400,
            "message": "Insert failed"
        })


@ app.route('/<string:id>', methods=['GET'])
def get(id):
    if (len(id) != 24):
        return jsonify({
            "status": 400,
            "message": "Invalid id"
        })
    else:
        query={'_id': ObjectId(id)}
        todo=todos.find_one(query)
        if todo:
            return jsonify({
                "status": 200,
                "data": todo
            })
        else:
            return jsonify({
                "status": 404,
                "message": "Not found"
            })


@ app.route('/<string:id>', methods=['DELETE'])
def delete(id):
    if (len(id) != 24):
        return jsonify({
            "status": 400,
            "message": "Invalid id"
        })
    else:
        query={'_id': ObjectId(id)}
        todo=todos.find_one(query)
        if todo:
            data=todos.delete_one(query)
            if (data.deleted_count == 1):
                return jsonify({
                    "status": 200,
                    "message": "Deleted successfully",
                })
            else:
                return jsonify({
                    "status": 400,
                    "message": "Deleted failed",
                })
        else:
            return jsonify({
                "status": 404,
                "message": "Not found"
            })


@ app.route('/<string:id>', methods=['PUT'])
def put(id):
    req=request.json
    if (len(id) != 24):
        return jsonify({
            "status": 400,
            "message": "Invalid id"
        })
    else:
        query={'_id': ObjectId(id)}
        update={"$set": req}
        todo=todos.find_one(query)
        if todo:
            data=todos.update_one(query, update)
            if (data.modified_count == 1):
                return jsonify({
                    "status": 200,
                    "message": "Updated successfully",
                })
            else:
                return jsonify({
                    "status": 400,
                    "message": "Updated failed",
                })
        else:
            return jsonify({
                "status": 404,
                "message": "Not found"
            })


app.json_encoder=CustomJSONEncoder

if __name__ == "__main__":
    app.run(debug=True)
