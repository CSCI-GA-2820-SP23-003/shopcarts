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

from tests.shop_cart_factory import ShopCartsFactory

######################################################################
#  T E S T   C A S E S
######################################################################

CUSTOMER_ID = 1
ITEM_ID = 1
class TestShopCartsServer(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.config['TESTING'] = True
        app.config["DEBUG"] = False
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
        db.session.query(ShopCarts).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_item(self):
        """ It should Create a enry in database for given customer if and item_id combination"""
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

    # TEST CASES FOR READ ITEMS OF A SHOPCART
    def test_read_shopcart_items(self):

        """ It should read all items in a shopcart given customer ID """

        records = ShopCartsFactory.create_batch(2)
        for item in records:
            item.create()

        customer_id = records[0].customer_id
        count_items = len([item for item in records if item.customer_id == customer_id])

        response = self.app.get(f'/shopcarts/{customer_id}/items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data['customer_id'], customer_id)
        self.assertEqual(len(data['items']), count_items)

    def test_read_empty_shopcart(self):
        """ It should return no items if the shopcart is empty """
        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}/items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['customer_id'], CUSTOMER_ID)
        self.assertEqual(len(data['items']), 0)

    def test_get_item(self):
        """It should Get an item from a shopcart"""
        resp = self.app.get(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)

    def test_get_item_item_not_found(self):
        """ It should not Read an item if the corresponding customer_id and item_id do not exist """
        resp = self.app.get(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.status.HTTP_404_NOT_FOUND)  
