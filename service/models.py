"""
Models for ShopCart

All of the models are stored in this module
"""
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Identity

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """ Initializes the SQLAlchemy app """
    ShopCart.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class ShopCart(db.Model):
    """
    Class that represents a ShopCart
    """
    app = None
    # Table Schema
    id = db.Column(db.Integer, Identity(start=1, cycle=True), primary_key=True)
    # Should add db.ForeignKey(customer.id) when integrate with Customer.
    customer_id = db.Column(db.Integer, index=True)
    # Should add db.ForeignKey(product.id) when integrate with product.
    product_id = db.Column(db.Integer)
    quantities = db.Column(db.Integer)
    # price = db.Column(db.Numeric(10, 2))

    def __repr__(self):
        return f"<ShopCart customer_id=[{self.customer_id}] product_id=[{self.product_id}] quantities=[{self.quantities}]>"

    def create(self):
        """
        Creates a ShopCart record to the database.
        """
        logger.info("Creating a ShopCart record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        # self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a ShopCart record to the database
        """
        if not self.id:
            raise DataValidationError("Don't exist current ShopCart record.")
        logger.info("Saving a ShopCart record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        db.session.commit()

    def delete(self):
        """ Removes a ShopCart from the data store """
        logger.info("Deleting a ShopCart record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a ShopCart into a dictionary """
        return {"id": self.id, "customer_id": self.customer_id, "product_id": self.product_id, "quantities": self.quantities}

    def deserialize(self, data):
        """
        Deserializes a ShopCart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.product_id = data["product_id"]
            self.quantities = data["quantities"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopCart: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCart: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the ShopCart items record in the database """
        logger.info("Processing all ShopCart")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a shopcart by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Finds all ShopCart item entries by customer id """
        logger.info("Processing lookup for customer id %d ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id, cls.product_id != -1).all()

    @classmethod
    def find_by_customer_id_and_product_id(cls, customer_id, product_id):
        """ Finds a ShopCart by customer id and product id """
        logger.info(
            "Processing lookup for customer id %d and product id %d", customer_id, product_id)
        return cls.query.filter(cls.customer_id == customer_id, cls.product_id == product_id).first()

    @classmethod
    def check_exist_by_customer_id_and_product_id(cls, customer_id, product_id):
        """ check if this ShopCart record is exists by customer id and product id """
        logger.info(
            "Checking record with customer id %d and product id %d", customer_id, product_id)
        return cls.query.filter(cls.customer_id == customer_id, cls.product_id == product_id).count() != 0

    @classmethod
    def all_shopcarts(cls):
        """ Returns all of the ShopCart in the database """
        logger.info("Processing all unique ShopCart")
        return cls.query.filter(cls.product_id == -1).all()

    @classmethod
    def clear_cart(cls, customer_id, delete_cart=False):
        """ Deletes a shopcart or clears a cart based on customer id """
        logger.info(
            "Deleting [%s] cart for customer id %d ...", delete_cart, customer_id)
        del_q = cls.__table__.delete().where(cls.customer_id == customer_id)
        if not delete_cart:
            del_q = cls.__table__.delete().where(
                cls.customer_id == customer_id, cls.product_id != -1)
        db.session.execute(del_q)
        db.session.commit()
