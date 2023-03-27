"""
TestShopCartsModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
from unittest import TestCase
from service import app
from service.models import db, ShopCarts
from service.common import status  # HTTP Status Codes
from service.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from .shop_cart_factory import ShopCartsFactory

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
        app.config["TESTING"] = True
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
        # self.app.get()
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)
        self.assertEqual(data["quantities"], 1)
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/_")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

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
        count_items = len(
            [item for item in records if item.customer_id == customer_id])

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

    def test_update_item_quantity_positive(self):
        """ It should update the quantity of a product if it exists in a customer's cart"""
        shop_cart = self._add_new_shopcart_item()
        customer_id = shop_cart.customer_id
        product_id = shop_cart.product_id
        quantity = 10
        resp = self.app.put(
            f"/shopcarts/{customer_id}/{product_id}/{quantity}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_cart_item = resp.get_json()
        self.assertEqual(updated_cart_item["quantities"], quantity)
        shop_cart.delete()

    def test_update_item_quantity_zero(self):
        """ It should give an error on trying to set a non-positive quantity for a product in the customer's cart"""
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}/0")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_quantity_non_existent(self):
        """ It should give an error on trying to update a non-existent product in the customer's cart"""
        customer_id = 0
        product_id = 0
        quantity = 10
        resp = self.app.put(
            f"/shopcarts/{customer_id}/{product_id}/{quantity}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_item(self):
        """ It should delete a product if it exists in a customer's cart"""
        shop_cart = self._add_new_shopcart_item()
        customer_id = shop_cart.customer_id
        product_id = shop_cart.product_id
        resp = self.app.delete(f"/shopcarts/{customer_id}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existent_item(self):
        """ It should give an error on trying to delete a non-existent product in the customer's cart"""
        customer_id = 0
        product_id = 0
        resp = self.app.delete(f"/shopcarts/{customer_id}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_item(self):
        """It should Get an item from a shopcart"""
        shop_cart = self._add_new_shopcart_item()
        customer_id = shop_cart.customer_id
        product_id = shop_cart.product_id
        resp = self.app.get(f"/shopcarts/{customer_id}/{product_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], customer_id)
        self.assertEqual(data["product_id"], product_id)

    def test_get_item_item_not_found(self):
        """ It should not Read an item thats does not exist """
        resp = self.app.get(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------
# TEST CASES FOR SHOPCART
# -----------------------------------------------------------

    def test_add_shopcart(self):
        """ It should Create a shopcart in database"""
        # self.app.get()
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)

    def test_add_duplicate_shopcart(self):
        """ It should raise error since there is a shopcart in DB"""
        # self.app.get()
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}")
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_add_shopcart_with_wrong_customer_id(self):
        """ It should raise error since there is a shopcart in DB"""
        # self.app.get()
        resp = self.app.post("/shopcarts/_")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_all_shopcart(self):
        """ It should read all shopcarts """
        self.app.post(f"/shopcarts/{CUSTOMER_ID}/{ITEM_ID}")
        self.app.post("/shopcarts/1")
        self.app.post("/shopcarts/2")

        response = self.app.get('/shopcarts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(len(data['shopcart_lists']), 2)

    def test_list_all_shopcarts_of_a_customer(self):
        """ It should read all shopcarts of a customer"""
        self.app.post(f"/shopcarts/{CUSTOMER_ID}")
        self.app.post(f"/shopcarts/{CUSTOMER_ID}/12")
        self.app.post(f"/shopcarts/{CUSTOMER_ID}/13")

        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data['customer_id'], CUSTOMER_ID)
        self.assertEqual(len(data['shopcarts']), 1)
        self.assertEqual(len(data['shopcarts'][0]['items']), 2)

    # TEST CASES TO COVER STATUS CODE

    def test_405_status_code(self):
        """ It should throw 405 error on trying to post to a GET API """
        resp = self.app.put("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
