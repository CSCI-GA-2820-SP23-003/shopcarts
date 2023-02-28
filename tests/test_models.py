"""
Test cases for ShopCarts Model

"""
import os
import logging
import unittest
from service import app
from service.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from service.models import ShopCarts, DataValidationError, db
import ShopCartsFactory


######################################################################
#  ShopCarts   M O D E L   T E S T   C A S E S
######################################################################
class TestShopCartsModel(unittest.TestCase):
    """ Test Cases for ShopCarts Model """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        # app = Flask(__name__)
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
        db.drop_all()
        db.create_all()

    def tearDown(self):
        """ This runs after each test """

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # def test_example_replace_this(self):
    #     """ It should always be true """
    #     self.assertTrue(True)
