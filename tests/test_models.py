"""
Test cases for ShopCarts Model

"""
import unittest
from service import app
from service.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from service.models import ShopCarts, DataValidationError, db
from .shop_cart_factory import ShopCartsFactory


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
        db.session.close()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # def test_example_replace_this(self):
    #     """ It should always be true """
    #     self.assertTrue(True)
    def test_create_shopcarts(self):
        """Test create shopcarts record"""
        shop_cart = ShopCarts(customer_id=1, product_id=1, quantities=1)
        shop_cart.create()
        self.assertNotEqual(shop_cart, None)
        self.assertEqual(shop_cart.customer_id, 1)
        self.assertEqual(shop_cart.product_id, 1)
        self.assertEqual(shop_cart.quantities, 1)
        self.assertIsInstance(shop_cart.id, int)

    def test__repr__(self):
        """test shopcart __repr__"""
        shop_cart = ShopCarts(customer_id=1, product_id=1, quantities=1)
        shop_cart.create()
        self.assertEqual(repr(shop_cart),
                         "<ShopCarts customer_id=[1] product_id=[1] quantities=[1]>")

    def test_find_shopcarts(self):
        """Test get a shopcarts record by its id"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart3 = ShopCartsFactory()
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()
        uid = shop_cart2.id
        shop_cart = ShopCarts.find(uid)
        self.assertEqual(shop_cart2.id, shop_cart.id)
        self.assertEqual(shop_cart2.customer_id, shop_cart.customer_id)
        self.assertEqual(shop_cart2.quantities, shop_cart.quantities)

    def test_update_shopcarts(self):
        """Test update shopcarts record"""
        shop_cart = ShopCartsFactory()
        shop_cart.create()

        shop_cart = ShopCarts.find(shop_cart.id)
        shop_cart.customer_id = 15
        shop_cart.product_id = 15
        shop_cart.quantities = 15
        shop_cart.update()

        shop_cart = ShopCarts.find(shop_cart.id)
        self.assertEqual(shop_cart.customer_id, 15)
        self.assertEqual(shop_cart.product_id, 15)
        self.assertEqual(shop_cart.quantities, 15)

    def test_update_shopcarts_not_exist(self):
        """ Test update not existing record"""
        shop_cart2 = ShopCartsFactory()
        shop_cart2.id = 100
        shop_cart2.update()
        self.assertRaises(DataValidationError)

    def test_delete_shopcarts(self):
        """Test delete shopcarts record by its id"""
        shop_cart = ShopCartsFactory()
        shop_cart.create()
        uid = shop_cart.id
        shop_cart.delete()

        shop_cart = ShopCarts.find(uid)
        self.assertIsNone(shop_cart)

    def test_serialize_shopcarts(self):
        """Test serialize shopcarts record"""
        shop_cart = ShopCarts(customer_id=1, product_id=1, quantities=1)
        shop_cart.create()
        shop_cart_dict = shop_cart.serialize()

        self.assertEqual(shop_cart_dict['customer_id'], 1)
        self.assertEqual(shop_cart_dict['product_id'], 1)
        self.assertEqual(shop_cart_dict['quantities'], 1)

    def test_deserialize_shopcarts(self):
        """Test deserialize shopcarts record"""
        shop_cart_dict = {"id": 3, "customer_id": 1,
                          "product_id": 1, "quantities": 1}
        shop_cart = ShopCarts()
        shop_cart.deserialize(shop_cart_dict)
        self.assertEqual(shop_cart.customer_id, 1)
        self.assertEqual(shop_cart.product_id, 1)
        self.assertEqual(shop_cart.quantities, 1)

    def test_deserialize_shopcarts_missing(self):
        """Test deserialize shopcarts record with missing key word """
        shop_cart_dict = {"id": 3,
                          "product_id": 1, "quantities": 1}
        shop_cart = ShopCarts()
        self.assertRaises(DataValidationError,
                          shop_cart.deserialize, shop_cart_dict)

    def test_deserialize_shopcarts_bad(self):
        """Test deserialize shopcarts record with bad data """
        # shop_cart_dict = {"id": 3, "custome": 1,
        #                   "product_id": 1, "quantities": 1}
        # shop_cart = ShopCarts()
        self.assertRaises(DataValidationError)

    def test_all(self):
        """Test get all shopcarts items record"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart3 = ShopCartsFactory()
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()

        all_shopcarts = ShopCarts.all()
        self.assertEqual(len(all_shopcarts), 3)

    def test_find_by_customer_id(self):
        """Test get a shopcarts record by its customer id"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart3 = ShopCartsFactory()
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()
        cid = shop_cart2.customer_id
        shop_cart = ShopCarts(customer_id=cid, product_id=1, quantities=1)
        shop_cart.create()
        shop_cart = ShopCarts(customer_id=cid, product_id=1, quantities=1)
        shop_cart.create()
        shop_cart = ShopCarts.find_by_customer_id(cid)

        self.assertEqual(len(shop_cart), 3)

    def test_find_by_customer_id_and_product_id(self):
        """Test get a shopcarts record by its customer id and product id"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart2.product_id = 3
        shop_cart3 = ShopCartsFactory()
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()
        cid = shop_cart2.customer_id
        pid = 3
        uid = shop_cart2.id
        shop_cart = ShopCarts(customer_id=cid, product_id=1, quantities=1)
        shop_cart.create()
        shop_cart = ShopCarts(customer_id=cid, product_id=2, quantities=1)
        shop_cart.create()
        shop_cart = ShopCarts.find_by_customer_id_and_product_id(cid, pid)

        self.assertEqual(uid, shop_cart.id)

    def test_check_exist_by_customer_id_and_product_id(self):
        """Test check if shopcarts record exits by its customer id and product id"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart2.product_id = 3
        shop_cart3 = ShopCartsFactory()
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()
        cid = shop_cart2.customer_id
        pid = 3
        # uid = shop_cart2.id
        shop_cart = ShopCarts(customer_id=cid, product_id=1, quantities=1)
        shop_cart.create()
        shop_cart = ShopCarts(customer_id=cid, product_id=2, quantities=1)
        shop_cart.create()

        bool1 = ShopCarts.check_exist_by_customer_id_and_product_id(
            cid, pid)
        bool2 = ShopCarts.check_exist_by_customer_id_and_product_id(
            cid, 5)
        self.assertEqual(bool1, True)
        self.assertEqual(bool2, False)

    def test_all_shopcart(self):
        """Test get all shopcarts record"""
        shop_cart1 = ShopCartsFactory()
        shop_cart2 = ShopCartsFactory()
        shop_cart3 = ShopCartsFactory()
        shop_cart1.product_id = -1
        shop_cart2.product_id = 2
        shop_cart3.product_id = 3
        shop_cart1.create()
        shop_cart2.create()
        shop_cart3.create()

        all_shopcarts = ShopCarts.all_shopcarts()
        self.assertEqual(len(all_shopcarts), 1)

    def test_clear_shopcart_delete_false(self):
        """Test clear shopcart"""
        shop_cart = ShopCartsFactory()
        shop_cart.product_id = -1
        shop_cart_item = ShopCartsFactory()
        customer_id = shop_cart.customer_id
        shop_cart_item.product_id = 1
        shop_cart_item.customer_id = customer_id
        shop_cart.create()
        shop_cart_item.create()

        item_count = ShopCarts.find_by_customer_id(customer_id)
        self.assertEqual(len(item_count), 1)
        self.assertTrue(ShopCarts.check_exist_by_customer_id_and_product_id(customer_id, -1))

        ShopCarts.clear_cart(customer_id, delete_cart=False)

        item_count = ShopCarts.find_by_customer_id(customer_id)
        self.assertEqual(len(item_count), 0)
        self.assertTrue(ShopCarts.check_exist_by_customer_id_and_product_id(customer_id, -1))

    def test_clear_shopcart_delete_true(self):
        """Test clear shopcart"""
        shop_cart = ShopCartsFactory()
        shop_cart.product_id = -1
        shop_cart_item = ShopCartsFactory()
        customer_id = shop_cart.customer_id
        shop_cart_item.product_id = 1
        shop_cart_item.customer_id = customer_id
        shop_cart.create()
        shop_cart_item.create()

        items = ShopCarts.find_by_customer_id(customer_id)
        self.assertEqual(len(items), 1)
        self.assertTrue(ShopCarts.check_exist_by_customer_id_and_product_id(customer_id, -1))

        ShopCarts.clear_cart(customer_id, delete_cart=True)

        self.assertFalse(ShopCarts.check_exist_by_customer_id_and_product_id(customer_id, -1))
