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
        app.config['TESTING'] = True
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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_item(self):
        """ It should Create a enry in database for given customer if and itemid combination"""
        #self.app.get()
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)
        self.assertEqual(data["quantities"], 1)

    def test_item_already_exists(self):
        """ It should detect counter already exists """
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)  




