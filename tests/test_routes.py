"""
TestShopCartsModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch
from service import app
import service.config
from service.models import db, ShopCarts
from service.common import status  # HTTP Status Codes
from service.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from .shop_cart_factory import ShopCartsFactory

######################################################################
#  T E S T   C A S E S
######################################################################

CUSTOMER_ID = 1
ITEM_ID=1

class TestShopCartsServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
        ShopCarts.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """

    def _add_new_shopcart_item(self):
        shopcart = ShopCarts(customer_id=0, product_id=0, quantities=1)
        shopcart.create()
        return shopcart

    def _delete_shopcart_item(self, shopcart_item):
        shopcart_item.delete()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_item(self):
        """ It should Create a entry in database for given customer id and item_id combination"""
        #self.app.get()
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)
        self.assertEqual(data["quantities"], 1)

    def test_item_already_exists(self):
        """ It should detect customer and item row already exists. so only update/delete requests will be accepted """
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_item_quantity_positive(self):
        """ It should update the quantity of a product if it exists in a customer's cart"""
        shop_cart = self._add_new_shopcart_item()
        customer_id = shop_cart.customer_id
        product_id = shop_cart.product_id
        quantity = 10
        resp = self.app.put(f"/shopcarts/{customer_id}/{product_id}/{quantity}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_cart_item = resp.get_json()
        self.assertEqual(updated_cart_item["quantities"], quantity)
        shop_cart.delete()

    def test_update_item_quantity_zero(self):
        """ It should delete a product from the customer's cart when it quantity goes to zero"""
        shop_cart = self._add_new_shopcart_item()
        customer_id = shop_cart.customer_id
        product_id = shop_cart.product_id
        resp = self.app.put(f"/shopcarts/{customer_id}/{product_id}/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_item_quantity_non_existent(self):
        """ It should give an error on trying to update a non existent product in the customer's cart"""
        customer_id = 0
        product_id = 0
        quantity = 10
        resp = self.app.put(f"/shopcarts/{customer_id}/{product_id}/{quantity}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)