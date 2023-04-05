"""
TestShopCartsModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import random
from unittest import TestCase
from flask import jsonify
from service import app
from service.models import db, ShopCart
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
        app.config["TESTING"] = True
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
        ShopCart.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        db.session.close()

    def setUp(self):
        """ This runs before each test """
        self.app = app.test_client()
        db.session.query(ShopCart).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """ This runs after each test """
        db.session.remove()

    def _add_new_shopcart(self, customer_id):
        shopcart = ShopCart(customer_id=customer_id, product_id=-1, quantities=1)
        shopcart.create()
        return shopcart

    def _add_new_shopcart_item(self, customer_id, product_id):
        shopcart_item = ShopCart(customer_id=customer_id, product_id=product_id, quantities=1)
        shopcart_item.create()
        return shopcart_item

    def _delete_shopcart_item(self, shopcart_item):
        shopcart_item.delete()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_health(self):
        """It should test health endpoint"""
        resp = self.app.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_index(self):
        """ It should call the home page """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_add_item(self):
        """ It should Create a entry in database for given customer id and item_id combination"""
        self._add_new_shopcart(CUSTOMER_ID)

        shopcart = ShopCartsFactory()
        shopcart_json = ShopCart.serialize(shopcart)
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['product_id'] = ITEM_ID
        shopcart_json['quantities'] = abs(shopcart_json['quantities'])
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/items", json=shopcart_json)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)
        self.assertEqual(data["quantities"], abs(shopcart_json['quantities']))
    
    def test_add_item_with_wrong_customer_id(self):
        """ It should detect inconsitency/incorrect customer id provided in request body to that present in the url"""
        self._add_new_shopcart(CUSTOMER_ID)

        shopcart = ShopCartsFactory()
        shopcart_json = ShopCart.serialize(shopcart)
        shopcart_json['customer_id'] = CUSTOMER_ID*10
        shopcart_json['product_id'] = ITEM_ID
        shopcart_json['quantities'] = abs(shopcart_json['quantities'])
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/items", json=shopcart_json)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_add_item_for_nonexistent_customer(self):
        """ It should give an error on trying to add a non-existent cart for the customer"""
        shopcart = ShopCartsFactory()
        shopcart_json = ShopCart.serialize(shopcart)
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['product_id'] = ITEM_ID
        shopcart_json['quantities'] = abs(shopcart_json['quantities'])
        resp = self.app.post(f"/shopcarts/{CUSTOMER_ID}/items", json=shopcart_json)

        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)
    
    def test_item_already_exists(self):
        """ It should detect customer and item row already exists. so only update/delete requests will be accepted """
        self._add_new_shopcart(CUSTOMER_ID)

        shopcart = ShopCartsFactory()
        shopcart_json = ShopCart.serialize(shopcart)
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['product_id'] = ITEM_ID
        shopcart_json['quantities'] = abs(shopcart_json['quantities'])
        self.app.post(f"/shopcarts/{CUSTOMER_ID}/items", json=shopcart_json)

        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['product_id'] = ITEM_ID
        shopcart_json['quantities'] = abs(shopcart_json['quantities'])+10
        resp = self.app.post("/shopcarts/1/items", json=shopcart_json)

        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)


#     # TEST CASES FOR READ ITEMS OF A SHOPCART
    def test_read_shopcart_items(self):
        """ It should read all items in a shopcart given customer ID """
        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, ITEM_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, 2)

        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}/items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data['customer_id'], 1)
        self.assertEqual(len(data['items']), 2)

    def test_read_empty_shopcart(self):
        """ It should return no items if the shopcart is empty """
        self._add_new_shopcart(CUSTOMER_ID)
        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}/items')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data['customer_id'], 1)
        self.assertEqual(len(data['items']), 0)

    def test_read_items_of_nonexistent_customer(self):
        """ It should return a 404 when trying to get all items of nonexistent customer """
        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}/items')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_quantity_positive(self):
        """ It should update the quantity of a product if it exists in a customer's cart"""
        self._add_new_shopcart(CUSTOMER_ID)
        test_shopcart_item = self._add_new_shopcart_item(CUSTOMER_ID, ITEM_ID)
        quantity = "10"
        # updating the quantity
        test_shopcart_item.quantities = quantity
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}", json=test_shopcart_item.serialize())
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_cart_item = resp.get_json()
        self.assertEqual(updated_cart_item["quantities"], int(quantity))

    def test_update_item_quantity_zero(self):
        """ It should give an error on trying to set a non-positive quantity for a product in the customer's cart"""

        self._add_new_shopcart(CUSTOMER_ID)
        test_shopcart_item = self._add_new_shopcart_item(CUSTOMER_ID, ITEM_ID)

        test_shopcart_item.quantities = "-10"

        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}", json=test_shopcart_item.serialize())
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_quantity_non_existent(self):
        """ It should give an error on trying to update a non-existent product in the customer's cart"""
        self._add_new_shopcart(CUSTOMER_ID)
        nonexistent_item = ShopCart(customer_id=CUSTOMER_ID, product_id=ITEM_ID, quantities=10)
        resp = self.app.put(
            f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}", json=nonexistent_item.serialize())
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_item(self):
        """ It should delete a product if it exists in a customer's cart"""
        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, ITEM_ID)
        resp = self.app.delete(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existent_item(self):
        """ It should give an error on trying to delete a non-existent product in the customer's cart"""
        self._add_new_shopcart(CUSTOMER_ID)
        resp = self.app.delete(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_item(self):
        """It should Get an item from a shopcart"""
        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, ITEM_ID)

        resp = self.app.get(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], CUSTOMER_ID)
        self.assertEqual(data["product_id"], ITEM_ID)

    def test_get_item_item_not_found(self):
        """ It should not Read an item thats does not exist """
        self._add_new_shopcart(CUSTOMER_ID)
        resp = self.app.get(f"/shopcarts/{CUSTOMER_ID}/items/{ITEM_ID}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

# -----------------------------------------------------------
# TEST CASES FOR SHOPCART
# -----------------------------------------------------------

    def test_add_shopcart(self):
        """ It should Create a shopcart in database"""
        shopcart = ShopCartsFactory()
        shopcart_json = ShopCart.serialize(shopcart)
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['product_id'] = -1
        resp = self.app.post("/shopcarts", json=shopcart_json)

        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], 1)

    def test_update_shopcart(self):
        """ It should update the shopcart in database"""
        self._add_new_shopcart(CUSTOMER_ID)
        
        items = []
        for i in range(10):
            shopcart = ShopCartsFactory()
            shopcart_item_json = ShopCart.serialize(shopcart)
            shopcart_item_json['customer_id'] = CUSTOMER_ID
            shopcart_item_json['quantities'] = abs(shopcart_item_json['quantities'])
            items.append(shopcart_item_json)
        shopcart_json={}
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['items'] = items
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}", json = shopcart_json)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        items_list = data["items"]
        self.assertEqual(len(items_list), len(items))    
        self.assertEqual(data["customer_id"], 1)

        shopcart_json['items'] = []
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}", json = shopcart_json)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_shopcart_of_a_customer_with_no_cart(self):        
        items = []
        for i in range(10):
            shopcart = ShopCartsFactory()
            shopcart_item_json = ShopCart.serialize(shopcart)
            shopcart_item_json['customer_id'] = CUSTOMER_ID
            shopcart_item_json['quantities'] = abs(shopcart_item_json['quantities'])
            items.append(shopcart_item_json)
        shopcart_json={}
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['items'] = items
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}", json = shopcart_json)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_shopcart_of_a_customer_with_request_with_wrong_customer_id(self):        
        self._add_new_shopcart(CUSTOMER_ID)
        items = []
        for i in range(10):
            shopcart = ShopCartsFactory()
            shopcart_item_json = ShopCart.serialize(shopcart)
            shopcart_item_json['customer_id'] = CUSTOMER_ID
            shopcart_item_json['quantities'] = abs(shopcart_item_json['quantities'])
            items.append(shopcart_item_json)
        shopcart_json={}
        shopcart_json['customer_id'] = CUSTOMER_ID*10
        shopcart_json['items'] = items
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}", json = shopcart_json)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)   

    def test_update_shopcart_of_a_customer_with_request_with_wrong_customer_id_in_request_body(self):        
        self._add_new_shopcart(CUSTOMER_ID)
        items = []
        for i in range(10):
            shopcart = ShopCartsFactory()
            shopcart_item_json = ShopCart.serialize(shopcart)
            shopcart_item_json['customer_id'] = CUSTOMER_ID
            shopcart_item_json['quantities'] = abs(shopcart_item_json['quantities'])
            items.append(shopcart_item_json)
        items[5]['customer_id'] = CUSTOMER_ID*10
        shopcart_json={}
        shopcart_json['customer_id'] = CUSTOMER_ID
        shopcart_json['items'] = items
        resp = self.app.put(f"/shopcarts/{CUSTOMER_ID}", json = shopcart_json)
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)   

    def test_add_duplicate_shopcart(self):
        """ It should raise error since there is a shopcart in DB"""
        self._add_new_shopcart(CUSTOMER_ID)

        duplicate_cart = ShopCart(customer_id=str(CUSTOMER_ID), product_id="-1", quantities="1")
        resp = self.app.post("/shopcarts", json=duplicate_cart.serialize())
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_add_shopcart_with_wrong_customer_id(self):
        """ It should raise error since there is a shopcart in DB"""
        test_shopcart_1 = ShopCart(customer_id="_", product_id="-1", quantities="1")
        resp = self.app.post("/shopcarts", json=test_shopcart_1.serialize())
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_read_all_shopcart(self):
        """ It should read all shopcarts """

        self._add_new_shopcart(1)
        self._add_new_shopcart(2)

        response = self.app.get('/shopcarts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(len(data['shopcart_lists']), 2)

    def test_list_all_shopcarts_of_a_customer_with_cart(self):
        """ It should read all shopcarts of a customer"""

        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, 1)
        self._add_new_shopcart_item(CUSTOMER_ID, 2)
        response = self.app.get(f'/shopcarts/{CUSTOMER_ID}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.get_json()
        self.assertEqual(data['customer_id'], CUSTOMER_ID)
        self.assertEqual(len(data['shopcarts']), 1)
        self.assertEqual(len(data['shopcarts'][0]['items']), 2)

    def test_list_all_shopcarts_of_a_customer_without_cart(self):
        """ It should throw an error on trying get the shopcarts of a customer without a cart"""
        response = self.app.get('/shopcarts/0')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_shopcart_of_a_customer_with_cart(self):
        """ It should delete a customer's shopcart along with all the items in it"""
        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, 1)
        self._add_new_shopcart_item(CUSTOMER_ID, 2)
        response = self.app.delete(f'/shopcarts/{CUSTOMER_ID}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_shopcart_of_a_customer_with_no_cart(self):
        """ It should delete a customer's shopcart along with all the items in it"""
        response = self.app.delete('/shopcarts/0')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_clear_shopcart_of_a_customer_with_cart(self):
        """ It should clear a customer's shopcart but not delete it"""
        self._add_new_shopcart(CUSTOMER_ID)
        self._add_new_shopcart_item(CUSTOMER_ID, 1)
        self._add_new_shopcart_item(CUSTOMER_ID, 2)
        response = self.app.put(f'/shopcarts/{CUSTOMER_ID}/clear')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_clear_shopcart_of_a_customer_with_no_cart(self):
        """ It should return 404 on trying to clear a cart of a customer with no cart"""
        response = self.app.put('/shopcarts/0/clear')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # TEST CASES TO COVER STATUS CODE

    def test_405_status_code(self):
        """ It should throw 405 error on trying to post to a GET API """
        resp = self.app.put("/")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_shopcart_no_content_type(self):
        """It should not create a Shopcart with no content type"""
        response = self.app.post('/shopcarts')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_shopcart_no_data(self):
        """It should not Create a shopcart with missing data"""
        response = self.app.post('/shopcarts', json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_shopcart_wrong_data(self):
        """It should not Create a shopcart with wrong data"""
        response = self.app.post('/shopcarts', data="abc", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
