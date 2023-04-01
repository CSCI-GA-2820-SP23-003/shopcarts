"""
My Service

Describe what your service does here
"""

import logging
from flask import jsonify, abort, request, url_for
from service.common import status  # HTTP Status Codes
from service.models import ShopCart
# Import Flask application
from . import app

logger = logging.getLogger("flask.app")
######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  SHOPCART   A P I   E N D P O I N T S
######################################################################


# -----------------------------------------------------------
# LIST ALL Shopcarts
# -----------------------------------------------------------

@app.route("/shopcarts", methods=['GET'])
def list_shopcarts():
    """
    Retrieve all shopcarts in DB
    This endpoint will return all the shopcart
    Args:

    Returns:
        customer_id (int): id of the customer who owns the shopcart
    """

    app.logger.info("Request for all shopcart")
    results = ShopCart.all_shopcarts()

    res = {}
    shopcart_list = []

    for record in results:
        current_shopcart = record.serialize()
        shopcart = {
            'customer_id': current_shopcart['customer_id'],
        }
        shopcart_list.append(shopcart)

    app.logger.info(
        "Returning %d shopcart ", len(shopcart_list)
    )
    res['shopcart_lists'] = shopcart_list
    return jsonify(res), status.HTTP_200_OK

# -----------------------------------------------------------
# Create a Shopcart
# -----------------------------------------------------------


@app.route("/shopcarts", methods=["POST"])
def add_shopcart():
    """Creates a new shopcart with customer id
    Args:
        customer_id (int): the id of the customer and item to add for it
    Returns:
        dict: the row entry in database which contains shopcart_id, customer_id
    """

    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())

    customer_id = shopcart.customer_id

    app.logger.info(
        f"Request to create a shopcart for customer {customer_id}")

    if customer_id is None or not customer_id.isdigit():
        abort(status.HTTP_400_BAD_REQUEST,
              f"Bad request for {customer_id}")

    customer_id = int(customer_id)

    if ShopCart.check_exist_by_customer_id_and_product_id(customer_id, -1):
        logger.info(
            f"Customer {customer_id} shopcart already exists")
        abort(status.HTTP_409_CONFLICT,
              f"Customer {customer_id} shopcart already exists")

    shopcart = ShopCart(customer_id=customer_id,
                        product_id=-1, quantities=1)
    shopcart.create()
    # message = shopcart.serialize()
    location_url = url_for("list_all_shopcarts_of_a_customer", customer_id = customer_id, _external=True)
    logger.info(f"Create a shopcart for customer {customer_id} sucessfully")
    return (
        jsonify({'customer_id': customer_id}),
        status.HTTP_201_CREATED,
        {"Location": location_url}
    )

# -----------------------------------------------------------
# LIST ALL SHOPCARTS OF A CUSTOMER
# -----------------------------------------------------------


@app.route("/shopcarts/<int:customer_id>", methods=['GET'])
def list_all_shopcarts_of_a_customer(customer_id):
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

    results = ShopCart.find_by_customer_id(customer_id)

    shopcarts = {}
    items = []

    for record in results:
        current_item = record.serialize()
        item = {
            'item_id': current_item['product_id'],
            'quantity': current_item['quantities']
        }
        items.append(item)

    cart = {}
    cart['items'] = items

    shopcarts['customer_id'] = customer_id
    shopcarts['shopcarts'] = [cart]

    app.logger.info(
        "Returning %d carts of customer %d", len(shopcarts['shopcarts']),
        customer_id
    )

    return jsonify(shopcarts), status.HTTP_200_OK

# -----------------------------------------------------------
# DELETE SHOPCART OF A CUSTOMER
# -----------------------------------------------------------


@app.route("/shopcarts/<int:customer_id>", methods=['DELETE'])
def delete_shopcart(customer_id):
    """
    Delete the shopcart of a customer
    """

    app.logger.info("delete shopcart of customer with id: %s", customer_id)
    ShopCart.clear_cart(customer_id, delete_cart=True)

    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  ITEM   A P I   E N D P O I N T S
######################################################################


# -----------------------------------------------------------
# Add an item to the cart
# -----------------------------------------------------------


@ app.route("/shopcarts/<customer_id>/items", methods=["POST"])
def add_item(customer_id):
    """Creates a new entry and stores it in the database
    Args:
        customer_id (str): the id of the customer and item to add for it
        item_id (str): the id of item to be added
    Returns:
        dict: the row entry in database which contains customer_id, item_id and quantity default to 1
    """
    check_content_type("application/json")
    shopcart = ShopCart()
    shopcart.deserialize(request.get_json())

    customer_id = shopcart.customer_id
    item_id = shopcart.product_id
    quantities = shopcart.quantities

    app.logger.info(
        f"Request to add item for customer {customer_id} and item {item_id}")

    if customer_id is None or item_id is None or quantities is None or not customer_id.isdigit() or not item_id.isdigit() or not quantities.isdigit():
        abort(status.HTTP_400_BAD_REQUEST,
              f"Bad request for {customer_id} {item_id}")

    customer_id = int(customer_id)
    item_id = int(item_id)
    quantities = int(quantities)

    if ShopCart.check_exist_by_customer_id_and_product_id(customer_id, item_id):
        logger.info(
            f"Customer {customer_id} and corresponding item {item_id} already exists")
        abort(status.HTTP_409_CONFLICT,
              f"Customer {customer_id} and corresponding item {item_id} already exists")

    shopcart = ShopCart(customer_id=customer_id,
                        product_id=item_id, quantities=quantities)
    shopcart.create()
    logger.info(f"Added item {item_id} for customer {customer_id} sucessfully")
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED
    )

# -----------------------------------------------------------
# LIST ALL ITEMS IN A SHOPCART
# -----------------------------------------------------------


@ app.route("/shopcarts/<int:customer_id>/items", methods=['GET'])
def list_shopcart_items(customer_id):
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

    results = ShopCart.find_by_customer_id(customer_id)

    shopcart_list = {}
    items = []

    for record in results:
        current_item = record.serialize()
        item = {
            'item_id': current_item['product_id'],
            'quantity': current_item['quantities'],
        }
        items.append(item)

    shopcart_list['customer_id'] = customer_id
    shopcart_list['items'] = items

    app.logger.info(
        "Returning %d items of customer %d", len(
            shopcart_list['items']), customer_id
    )

    return jsonify(shopcart_list), status.HTTP_200_OK

# -----------------------------------------------------------
# UPDATE PRODUCT QUANTITY IN CART
# -----------------------------------------------------------


@ app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["PUT"]) #TODO
def update_shopcart_item(customer_id, product_id):
    """Updates the quantity of an existing product"""
    app.logger.info(
        f"Update quantity of product-{product_id} in customer-{customer_id}'s cart")
    check_content_type("application/json")

    product_id = int(product_id)
    customer_id = int(customer_id)
    # quantity = int(quantity)

    shopcart_item = ShopCart.find_by_customer_id_and_product_id(
        customer_id, product_id)

    if not shopcart_item:
        app.logger.error(
            f"Product-{product_id} doesn't exist in customer-{customer_id}'s cart!")
        abort(status.HTTP_404_NOT_FOUND,
              f"Product-{product_id} doesn't exist in the customer-{customer_id}'s cart!")

    # req_item = ShopCart()
    new_quantity = ShopCart().deserialize(request.get_json()).quantities
    # quantity = req_item.quantities

    if not new_quantity.isdigit():
        app.logger.error("Quantity to be updated must be a number!")
        abort(status.HTTP_400_BAD_REQUEST, f"Quantity [{new_quantity}] is not valid.")

    new_quantity = int(new_quantity)
    if new_quantity <= 0:
        app.logger.error(
            f"Quantity to be updated [{new_quantity}] should be positive!")
        abort(status.HTTP_400_BAD_REQUEST,
              f"Quantity to be updated [{new_quantity}] should be positive!")
    
    # shopcart_item.customer_id = customer_id
    # shopcart_item.product_id = product_id
    shopcart_item.quantities = new_quantity

    shopcart_item.update()

    app.logger.info(
        f"Updated Product-{product_id} quantity to {new_quantity} in customer-{customer_id}'s cart!")

    return jsonify(shopcart_item.serialize()), status.HTTP_200_OK

# -----------------------------------------------------------
# DELETE PRODUCT FROM CART
# -----------------------------------------------------------


@ app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["DELETE"])
def delete_shopcart_item(customer_id, product_id):
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


@ app.route("/shopcarts/<int:customer_id>/items/<int:product_id>", methods=["GET"])
def get_item(customer_id, product_id):
    """
    Read an item from a shopcart
    """
    app.logger.info(
        f"Request to read an Item-{product_id} from Customer-{customer_id} 's shopcart")
    # Read an item with item_id
    result = ShopCart.find_by_customer_id_and_product_id(
        customer_id, product_id)
    if result is not None:
        return jsonify(result.serialize()), status.HTTP_200_OK
    # See if the item exists and abort if it doesn't
    else:

        logger.error(
            f"Customer {customer_id} and corresponding item {product_id} could not be found.")
        abort(status.HTTP_404_NOT_FOUND,
              f"Customer {customer_id} and corresponding item {product_id} could not be found.")


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
