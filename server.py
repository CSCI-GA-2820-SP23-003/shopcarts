# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from flask import Flask, jsonify, request, url_for, make_response
from flasgger import Swagger
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# Pull options from environment
debug = (os.getenv('DEBUG', 'False') == 'True')
port = os.getenv('PORT', '5000')

# Initialize Flask
app = Flask(__name__)

# Configure Swagger before initilaizing it
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "DevOps Swagger Pet App",
            "description": "This is a sample server Petstore server.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}

# Initialize Swagger after configuring it
Swagger(app)

######################################################################
# ERROR Handling
######################################################################
@app.errorhandler(ValueError)
def request_validation_error(e):
    """ Handles validation errors """
    return bad_request(e)

@app.errorhandler(404)
def not_found(e):
    """ Handles 404 Not Fund errors """
    return make_response(jsonify(status=404, error='Not Found',
                                 message=e.description), status.HTTP_404_NOT_FOUND)

@app.errorhandler(400)
def bad_request(e):
    """ Handles 400 Bad Requests """
    return make_response(jsonify(status=400, error='Bad Request',
                                 message=e.message), status.HTTP_400_BAD_REQUEST)

@app.errorhandler(405)
def method_not_allowed(e):
    """ Handles 405 Method Not Allowed """
    return make_response(jsonify(status=405, error='Method not Allowed',
                                 message='Your request method is not supported. Check your HTTP method and try again.'), status.HTTP_405_METHOD_NOT_ALLOWED)

@app.errorhandler(500)
def internal_error(e):
    """ Handles 500 Server Errors """
    return make_response(jsonify(status=500, error='Internal Server Error',
                                 message='Huston... we have a problem.'), status.HTTP_500_INTERNAL_SERVER_ERROR)


######################################################################
#  Index
######################################################################
@app.route("/")
def index():
    """ Home Page """
    return jsonify(name='Pet Demo REST API Service',
                   version='1.0',
                   docs=request.base_url + 'apidocs/index.html'), status.HTTP_200_OK

######################################################################
#  List Pets
######################################################################
@app.route("/pets", methods=['GET'])
def list_pets():
    """
    Retrieve a list of Pets
    This endpoint will return all Pets unless a query parameter is specificed
    ---
    tags:
      - Pets
    description: The Pets endpoint allows you to query Pets
    parameters:
      - name: category
        in: query
        description: the category of Pet you are looking for
        required: false
        type: string
      - name: name
        in: query
        description: the name of Pet you are looking for
        required: false
        type: string
    definitions:
      Pet:
        type: object
        properties:
          id:
            type: integer
            description: unique id assigned internallt by service
          name:
            type: string
            description: the pets's name
          category:
            type: string
            description: the category of pet (e.g., dog, cat, fish, etc.)
    responses:
      200:
        description: An array of Pets
        schema:
          type: array
          items:
            schema:
              $ref: '#/definitions/Pet'
    """
    pets = []
    category = request.args.get('category')
    name = request.args.get('name')
    if category:
        pets = Pet.find_by_category(category)
    elif name:
        pets = Pet.find_by_name(name)
    else:
        pets = Pet.all()

    results = [pet.serialize() for pet in pets]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
#  Retrieve a Pet
######################################################################
@app.route("/pets/<int:id>", methods=['GET'])
def get_pets(id):
    """
    Retrieve a single Pet
    This endpoint will return a Pet based on it's id
    ---
    tags:
      - Pets
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of pet to retrieve
        type: integer
        required: true
    responses:
      200:
        description: Pet returned
        schema:
          $ref: '#/definitions/Pet'
      404:
        description: Pet not found
    """
    pet = Pet.find(id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(id))
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
#  Create a Pet
######################################################################
@app.route("/pets", methods=['POST'])
def create_pets():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    ---
    tags:
      - Pets
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          id: data
          required:
            - name
            - category
          properties:
            name:
              type: string
              description: name for the Pet
            category:
              type: string
              description: the category of pet (dog, cat, etc.)
    responses:
      201:
        description: Pet created
        schema:
          $ref: '#/definitions/Pet'
      400:
        description: Bad Request (the posted data was not valid)
    """
    pet = Pet()
    pet.deserialize(request.get_json())
    pet.save()
    message = pet.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': pet.self_url() })

######################################################################
#  Update a Pet
######################################################################
@app.route("/pets/<int:id>", methods=['PUT'])
def update_pets(id):
    """
    Update a Pet
    This endpoint will update a Pet based the body that is posted
    ---
    tags:
      - Pets
    consumes:
      - application/json
    produces:
      - application/json
    parameters:
      - name: id
        in: path
        description: ID of pet to retrieve
        type: integer
        required: true
      - in: body
        name: body
        schema:
          id: data
          required:
            - name
            - category
          properties:
            name:
              type: string
              description: name for the Pet
            category:
              type: string
              description: the category of pet (dog, cat, etc.)
    responses:
      200:
        description: Pet Updated
        schema:
          $ref: '#/definitions/Pet'
      400:
        description: Bad Request (the posted data was not valid)
    """
    pet = Pet.find(id)
    if not pet:
        raise NotFound("Pet with id '{}' was not found.".format(id))
    pet.deserialize(request.get_json())
    pet.save()
    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)

######################################################################
#  Delete a Pet
######################################################################
@app.route("/pets/<int:id>", methods=['DELETE'])
def delete_pets(id):
    """
    Delete a Pet
    This endpoint will delete a Pet based the id specified in the path
    ---
    tags:
      - Pets
    description: Deletes a Pet from the database
    parameters:
      - name: id
        in: path
        description: ID of pet to delete
        type: integer
        required: true
    responses:
      204:
        description: Pet deleted
    """
    pet = Pet.find(id)
    if pet:
        pet.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port), debug=debug)