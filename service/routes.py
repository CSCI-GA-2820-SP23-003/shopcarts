"""
My Service

Describe what your service does here
"""

import logging
from flask import jsonify, abort
from service.common import status  # HTTP Status Codes
from service.models import ShopCarts
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
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...


# -----------------------------------------------------------
# Create counters
# -----------------------------------------------------------
@app.route("/shopcarts/<customer_id>/<item_id>", methods=["POST"])
def add_item(customer_id, item_id):
    """Creates a new entry and stores it in the database
    Args:
        customer_id (str): the id of the customer and item to add for it
        item_id (str): the id of item to be added
    Returns:
        dict: the row entry in databse which contains customer_id, item_id and quantity default to 1
    """
    app.logger.info(f"Request to add item for customer {customer_id} and item {item_id}")
    if customer_id is None or item_id is None or not customer_id.isdigit() or not item_id.isdigit():
        abort(status.HTTP_400_BAD_REQUEST, f"Bad request for {customer_id} {item_id}")

    customer_id = int(customer_id)
    item_id = int(item_id)

    if ShopCarts.check_exist_by_customer_id_and_product_id(customer_id, item_id):
        logger.info(f"Customer {customer_id} and coresponding ietm {item_id} already exists")
        abort(status.HTTP_409_CONFLICT, f"Customer {customer_id} and coresponding ietm {item_id} already exists")

    shopcart = ShopCarts(customer_id=customer_id, product_id=item_id, quantities=1)
    shopcart.create()
    logger.info(f"Added item {item_id} for customer {customer_id} sucessfully")
    return (
        jsonify(shopcart.serialize()),
        status.HTTP_201_CREATED
    )

######################################################################
# LIST ALL ITEMS IN A SHOPCART
######################################################################


@app.route("/shopcarts/<int:customer_id>/items", methods=['GET'])
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

    app.logger.info("Request for shopcart items of customer with id: %s", customer_id)
    results = ShopCarts.find_by_customer_id(customer_id)

    shopcart_list = {}
    items = []

    for record in results:
        current_item = record.serialize()
        item = {
            'item_id': current_item['product_id'],
            'quantity': current_item['quantities'],
            # 'shopcart_record_id': current_item['id']
            # will return price after integrating with product
        }
        items.append(item)

    shopcart_list['customer_id'] = customer_id
    shopcart_list['items'] = items

    app.logger.info(
        "Returning %d items of customer %d", len(shopcart_list['items']),
        shopcart_list['customer_id']
    )

    return jsonify(shopcart_list), status.HTTP_200_OK

# -----------------------------------------------------------
# UPDATE PRODUCT QUANTITY
# -----------------------------------------------------------


@app.route("/shopcarts/<int:customer_id>/<int:product_id>/<int:quantity>", methods=["PUT"])
def update_shopcart_item(customer_id, product_id, quantity):
    """Updates the quantity of an existing product"""
    app.logger.info(f"Update product-{product_id} in customer-{customer_id}'s cart to {quantity}")

    product_id = int(product_id)
    customer_id = int(customer_id)
    quantity = int(quantity)

    if quantity <= 0:
        app.logger.error(f"Quantity to be updated [{quantity}] should be positive!")
        abort(status.HTTP_400_BAD_REQUEST, f"Quantity to be updated [{quantity}] should be positive!")

    shopcart_item = ShopCarts.find_by_customer_id_and_product_id(customer_id, product_id)

    if not shopcart_item:
        app.logger.error(f"Product-{product_id} doesn't exist in customer-{customer_id}'s cart!")
        abort(status.HTTP_404_NOT_FOUND, f"Product-{product_id} doesn't exist in the customer-{customer_id}'s cart!")

    shopcart_item.quantities = quantity
    shopcart_item.update()
    app.logger.info(f"Updated Product-{product_id} quantity to {quantity} in customer-{customer_id}'s cart!")

    return jsonify(shopcart_item.serialize()), status.HTTP_200_OK
