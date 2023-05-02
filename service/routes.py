"""
My Service

Describe what your service does here
"""
import sys
import secrets
import logging
from functools import wraps
from flask import abort, jsonify, request, url_for, make_response, render_template
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import ShopCart
from . import app,api

logger = logging.getLogger("flask.app")

# Define the model so that the docs reflect what can be sent
shopcart_create_model = api.model('ShopCart', {
    'customer_id': fields.Integer(required=True,
                          description='The customer_id of the customer'),
    'product_id': fields.Integer(required=True,
                              description='The product_id of the item)'),
    'quantities': fields.Integer(required=False,
                                description='The quantities requested by the customer'),
})

shopcart_model = api.inherit(
    'ShopCartModel', 
    shopcart_create_model,
    {
        'id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)
shopcart_list_model = api.model(
    'ListOfShopCartModel', 
    {
        'customer_id': fields.String(required=True,readOnly=True,
                            description='The customer_id of the customer'),
        'items':fields.List(fields.Nested(shopcart_model,
                                           required=True,
                                           description='List of items that the customer wants to add to the shopcart'))                  
    }
)

# query string arguments
shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument('customer_id', type=int, location='args', required=False, help='List shopcarts by customer_id')

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response - UI """
    return app.send_static_file("index.html")

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
#  SHOPCART   A P I   E N D P O I N T S
######################################################################
######################################################################
#  PATH: /shopcarts
######################################################################
@api.route('/shopcarts')
class ShopcartCollection(Resource):

    # -----------------------------------------------------------
    # LIST ALL Shopcarts
    # -----------------------------------------------------------

    @api.doc('list_shopcarts')
    @api.marshal_list_with(shopcart_model)
    def get(self):
        """
        Retrieve all shopcarts in DB
        This endpoint will return all the shopcart
        Args:
        Returns:
            list of all the shopcarts that are created by the customers.
        """

        app.logger.info("Request for all shopcart")
        shopcarts = ShopCart.all_shopcarts()
        results = [shopcart.serialize() for shopcart in shopcarts]
        app.logger.info(
            "Returning %d shopcart ", len(results)
        )
        return results, status.HTTP_200_OK


    # -----------------------------------------------------------
    # Create a Shopcart
    # -----------------------------------------------------------
    @api.doc('create_shopcart')
    @api.response(400, 'The posted data was not valid')
    @api.response(409, 'The shopcart is already created for the given customer')
    @api.expect(shopcart_create_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self):
        """Creates a new shopcart with customer id
        Args: None
        Request Body: JSON with customer_id (str): Customer ID of the customer to create shopcart for
        Returns:
            JSON: the created empty shopcart of the customer
                customer_id (int): id of the customer
                shopcarts:
                    items (list): list of all items in shopcart
            Header containing location url of the newly created shopcart for customer with ID=customer_id
        """

        check_content_type("application/json")
        shopcart = ShopCart()
        shopcart.deserialize(request.get_json())

        customer_id = shopcart.customer_id

        app.logger.info(
            f"Request to create a shopcart for customer {customer_id}")

        if customer_id is None or not str(customer_id).isdigit():
            abort(status.HTTP_400_BAD_REQUEST,
                f"Bad request for {customer_id}")

        customer_id = int(customer_id)
        if ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1):
            logger.info(f"Customer {customer_id} shopcart already exists")
            abort(status.HTTP_409_CONFLICT,
                f"Customer {customer_id} shopcart already exists")

        shopcart = ShopCart(customer_id=customer_id,
                            product_id=-1, quantities=1)
        shopcart.create()

        location_url = api.url_for(CustomerResource, customer_id=customer_id, _external=True)
        return shopcart.serialize(), status.HTTP_201_CREATED,{"Location": location_url}
       
    
@api.route('/shopcarts/<int:customer_id>')
@api.param('customer_id', 'The Customer identifier')    
class CustomerResource(Resource):
    # -----------------------------------------------------------
    # LIST ALL SHOPCARTS OF A CUSTOMER
    # -----------------------------------------------------------
    @api.doc('list_all_shopcarts_of_a_customer')
    @api.response(404, 'Customer has not created shopcart yet')
    @api.marshal_list_with(shopcart_model, code=201)
    def get(self,customer_id):
        """
        Retrieve all the shopcarts of a customer
        Args:
            customer_id (int): the id of the customer
        Returns:
            customer_id (int): id of the customer who owns the shopcart
            carts (list): list of all their carts
                cart (list): list of all items in their cart
                    item_id (int): product id
                    quantity (int): number of the product in the cart
        """
        app.logger.info(
            "Request for shopcarts of customer with id: %s", customer_id)

        if not ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1):
            logger.error(f"Customer {customer_id} does not have a cart")
            abort(status.HTTP_404_NOT_FOUND,
                f"Customer {customer_id} does not have a cart")

        items = ShopCart.find_by_customer_id(customer_id)
        results = [item.serialize() for item in items]
        app.logger.info(
            "Returning %d carts of customer %d", len(results),
            customer_id
        )

        return results, status.HTTP_200_OK

    # -----------------------------------------------------------
    # DELETE SHOPCART OF A CUSTOMER
    # -----------------------------------------------------------
    @api.doc('delete_shopcart_of_a_customer')
    @api.response(404, 'Customer has not created shopcart yet')
    def delete(self,customer_id):
        """
        Delete the shopcart of a customer
        """
        app.logger.info("delete shopcart of customer with id: %s", customer_id)
        ShopCart.clear_cart(customer_id, delete_cart=True)

        return "", status.HTTP_204_NO_CONTENT
    

    # -----------------------------------------------------------
    # Update a Shopcart
    # -----------------------------------------------------------
    @api.doc('update_shopcart')
    @api.response(400, 'The customer has not created the shopcart')
    @api.response(409, 'The customer_id provided in payload is not in sync with the one provided in the url requested')
    @api.expect(shopcart_list_model)
    @api.marshal_with(shopcart_model, code=200)
    def put(self, customer_id):
        """Updates shopcart with customer id with the query parameter True
            and Clears shopcart with query parameter False
        Args:
            customer_id (int): the id of the customer and item to add for it
        Returns:
            dict: the row entry in database which contains shopcart_id, customer_id
        """
        if not ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1):
            logger.info(
                f"Customer {customer_id} has not created any shopcart")
            abort(
                status.HTTP_409_CONFLICT,
                f"Customer {customer_id} has not created any shopcart"
            )
        query_params = request.args.to_dict(flat=False)
        query_update = query_params.get('update')
        if query_update:
            for query_val in query_update:
                if not query_val.lstrip('-').isalpha() or query_val.lower() not in ["true", "false"]:
                    logger.error("Invalid value passed for update(True/False) in query parameters")
                    abort(status.HTTP_400_BAD_REQUEST, f"query_val: {query_val} is not a valid value")
        
        query_update =query_update[0].lower()
        if query_update=="false":
            """
            Clear the shopcart of a customer
            """
            app.logger.info("clear shopcart of customer with id: %s", customer_id)
            ShopCart.clear_cart(customer_id, delete_cart=False)
            items = ShopCart.find_by_customer_id(customer_id)
            logger.info(f"Cleared shopcart for customer {customer_id} sucessfully")
            results = [item.serialize() for item in items]
            return results, status.HTTP_200_OK
        else:       
            app.logger.info(
            f"Request to update a shopcart for customer {customer_id}")
            check_content_type("application/json")
            data = request.get_json()
            if customer_id != int(data['customer_id']):
                logger.info(
                    f"Customer {customer_id} is not consistent with request")
                abort(
                    status.HTTP_409_CONFLICT,
                    f"Customer {customer_id} is not consistent with request"
                )
            ShopCart.clear_cart(customer_id, delete_cart=False)
            request_data = data['items']
            if request_data is None or len(request_data) == 0:
                logger.info(
                    f"No items are present in the request to update the shopcart of customer {customer_id}")
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    f"No items are present in the request to update the shopcart of customer {customer_id}"
                )

            for item in request_data:
                shopcart_item = ShopCart()
                shopcart_item.deserialize(item)
                if shopcart_item.customer_id != customer_id:
                    logger.info(
                        f"Customer {customer_id} is not consistent with request")
                    abort(
                        status.HTTP_409_CONFLICT,
                        f"Customer {customer_id} is not consistent with request"
                    )
                shopcart_item.create()
                logger.info(f"Added item {item['product_id']} for customer {customer_id} sucessfully")

            items = ShopCart.find_by_customer_id(customer_id)
            
            logger.info(f"Updated shopcart for customer {customer_id} sucessfully")
            results = [item.serialize() for item in items]
            return results, status.HTTP_200_OK

# ######################################################################
# #  ITEM   A P I   E N D P O I N T S
# ######################################################################
    
@api.route('/shopcarts/<int:customer_id>/items/<int:product_id>')
@api.param('customer_id', 'The Customer identifier')
@api.param('product_id', 'The Product identifier')
class ItemResource(Resource):
    # # -----------------------------------------------------------
    # # Add an item to the cart
    # # -----------------------------------------------------------
    @api.doc('add_item_to_shopcart')
    @api.response(400, 'Bad Request: inconsistent customer_id in request payload and url')
    @api.response(409, 'Conflict: product already present in the shopcart')
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model, code=201)
    def post(self, customer_id,product_id):
        """Creates a new entry and stores it in the database
        Args:
            customer_id (str): the id of the customer and item to add for it
        Request Body: JSON wit item_id (str): the id of item to be added
        Returns:
            dict: the row entry in database which contains customer_id, item_id and quantity default to 1
        """
        check_content_type("application/json")
        shopcart = ShopCart()
        shopcart.deserialize(api.payload)

        # customer_id = shopcart.customer_id
        item_id = product_id
        quantities = shopcart.quantities

        app.logger.info(
            f"Request to add item for customer {customer_id} and item {item_id}")

        if (item_id is None or quantities is None or int(customer_id) != shopcart.customer_id):
            abort(
                status.HTTP_400_BAD_REQUEST,
                f"Bad request for customer:{customer_id} & item:{item_id}"
            )

        if (not ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1)):
            logger.info(f"Customer {customer_id} does not have any cart")
            abort(status.HTTP_409_CONFLICT, f"Customer {customer_id} does not have any cart")

        if ShopCart.check_exist_by_customer_id_and_product_id(customer_id, item_id):
            logger.info(
                f"Customer {customer_id} and corresponding item {item_id} already exists")
            abort(status.HTTP_409_CONFLICT,
                  f"Customer {customer_id} and corresponding item {item_id} already exists")

        shopcart.create()
        logger.info(f"Added item {item_id} for customer {customer_id} sucessfully")
        return shopcart.serialize(), status.HTTP_201_CREATED
    
    # -----------------------------------------------------------
    # UPDATE PRODUCT QUANTITY IN CART
    # -----------------------------------------------------------
    @api.doc('update_shopcart_item_of_customer_id')
    @api.response(404, 'Bad Request: Cutomer as not created cart')
    @api.response(404, 'Bad Request: Quantity provided should be integer')
    @api.expect(shopcart_model)
    @api.marshal_with(shopcart_model, code=200)
    def put(self, customer_id, product_id):
        """Updates the quantity of an existing product"""
        app.logger.info(
            f"Update quantity of product-{product_id} in customer-{customer_id}'s cart")
        check_content_type("application/json")

        product_id = int(product_id)
        customer_id = int(customer_id)

        shopcart_item = ShopCart.find_by_customer_id_and_product_id(
            customer_id, product_id)

        if not shopcart_item:
            app.logger.error(
                f"Product-{product_id} doesn't exist in customer-{customer_id}'s cart!")
            abort(status.HTTP_404_NOT_FOUND,
                  f"Product-{product_id} doesn't exist in the customer-{customer_id}'s cart!")

        new_quantity = ShopCart().deserialize(request.get_json()).quantities

        if not new_quantity.lstrip('-').isdigit() or int(new_quantity) <= 0:
            app.logger.error("Quantity to be updated must be a valid number!")
            abort(status.HTTP_400_BAD_REQUEST,
                  f"Quantity to be updated [{new_quantity}] should be positive!")

        shopcart_item.quantities = int(new_quantity)
        shopcart_item.update()
        app.logger.info(
            f"Updated Product-{product_id} quantity to {new_quantity} in customer-{customer_id}'s cart!")

        return shopcart_item.serialize(), status.HTTP_200_OK

    # -----------------------------------------------------------
    # DELETE PRODUCT FROM CART
    # -----------------------------------------------------------
    @api.doc('delete_shopcart_item_of_customer_id')
    @api.marshal_with(shopcart_model)
    def delete(self, customer_id, product_id):
        """Deletes an existing product from cart"""
        app.logger.info(f"Delete product-{product_id} in customer-{customer_id}'s")

        product_id = int(product_id)
        customer_id = int(customer_id)

        shopcart_item = ShopCart.find_by_customer_id_and_product_id(
            customer_id, product_id)

        if shopcart_item is not None:
            shopcart_item.delete()
            app.logger.info(
                f"Deleted Product-{product_id} in customer-{customer_id}'s cart!")

        return "", status.HTTP_204_NO_CONTENT

    # -----------------------------------------------------------
    # READ AN ITEM FROM A SHOPCART
    # -----------------------------------------------------------
    @api.doc('get_shopcart_item_of_customer_id')
    @api.response(404, 'Bad Request: Customer as not created cart')
    @api.marshal_with(shopcart_model)
    def get(self,customer_id, product_id):
        """
        Read an item from a shopcart
        """
        app.logger.info(
            f"Request to read an Item-{product_id} from Customer-{customer_id} 's shopcart")
        # Read an item with item_id
        product_id = int(product_id)
        customer_id = int(customer_id)
        result = ShopCart.find_by_customer_id_and_product_id(
            customer_id, product_id)
        if result is not None:
            return result.serialize(), status.HTTP_200_OK
        # See if the item exists and abort if it doesn't
        else:
            logger.error(
                f"Customer {customer_id} and corresponding item {product_id} could not be found.")
            abort(status.HTTP_404_NOT_FOUND,
                  f"Customer {customer_id} and corresponding item {product_id} could not be found.")
            

@api.route('/shopcarts/<int:customer_id>/items')
@api.param('customer_id', 'The Customer identifier') 
class CustomerItemsCollection(Resource):

    # -----------------------------------------------------------
    # LIST ALL ITEMS IN A SHOPCART
    # -----------------------------------------------------------
    @api.doc('get_shopcart_of_customer_id')
    @api.response(404, 'Bad Request: Cutomer as not created cart')
    @api.marshal_list_with(shopcart_model)
    def get(self, customer_id):
        """
        Retrieve all the items in a customer's cart
        This endpoint will return the cart items based on customer id
        Args:
            customer_id (int): the id of the customer
        Returns:
            customer_id (int): id of the customer who owns the shopcart
            items (list): list of all items
                item_id (int): product id
                quantity (int): number of the product in the cart
        """
        app.logger.info(
            "Request for shopcart items of customer with id: %s", customer_id)

        if not ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1):
            logger.error(f"Customer {customer_id} does not have a cart")
            abort(status.HTTP_404_NOT_FOUND,
                  f"Customer {customer_id} does not have a cart")

        query_params = request.args.to_dict(flat=False)
        query_quantities = query_params.get('quantity')

        if query_quantities:
            for query_qty in query_quantities:
                if not query_qty.lstrip('-').isdigit():
                    logger.error("Invalid value passed for quantity in query parameters")
                    abort(status.HTTP_400_BAD_REQUEST, f"Quantity: {query_qty} is not a valid value")

            query_quantities = [int(qty) for qty in query_quantities]

        results = ShopCart.find_by_customer_id(customer_id)
        items = []

        for record in results:
           
            if query_quantities and record.quantities not in query_quantities:
                continue

            items.append(record)

        results = [item.serialize() for item in items]
        app.logger.info(
            "Returning %d items of customer %d", len(items), customer_id
            )

        return (results, status.HTTP_200_OK)


######################################################################
#  UTILITY FUNCTIONS
######################################################################

def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )