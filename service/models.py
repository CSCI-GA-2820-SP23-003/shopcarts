"""
Models for ShopCarts

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
    ShopCarts.init_db(app)


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """


class ShopCarts(db.Model):
    """
    Class that represents a ShopCarts
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
        return f"<ShopCarts customer_id=[{self.customer_id}] product_id=[{self.product_id}] quantities=[{self.quantities}]>"

    def create(self):
        """
        Creates a ShopCarts record to the database.
        """
        logger.info("Creating a ShopCarts record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        # self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a ShopCarts record to the database
        """
        if not self.id:
            raise DataValidationError("Don't exist current ShopCarts record.")
        logger.info("Saving a ShopCarts record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        db.session.commit()

    def delete(self):
        """ Removes a ShopCarts from the data store """
        logger.info("Deleting a ShopCarts record for customer %d with product %d quantities %d",
                    self.customer_id, self.product_id, self.quantities)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a ShopCarts into a dictionary """
        return {"id": self.id, "customer_id": self.customer_id, "product_id": self.product_id, "quantities": self.quantities}

    def deserialize(self, data):
        """
        Deserializes a ShopCarts from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.customer_id = data["customer_id"]
            self.product_id = data["product_id"]
            self.quantities = data["quantities"]
        except KeyError as error:
            raise DataValidationError(
                "Invalid ShopCarts: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid ShopCarts: body of request contained bad or no data - "
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
        """ Returns all of the ShopCarts in the database """
        logger.info("Processing all ShopCarts")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """ Finds a shopcart by it's ID """
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Finds a ShopCarts by customer id """
        logger.info("Processing lookup for customer id %d ...", customer_id)
        return cls.query.filter(cls.customer_id == customer_id).all()

    @classmethod
    def find_by_customer_id_and_product_id(cls, customer_id, product_id):
        """ Finds a ShopCarts by customer id and product id """
        logger.info(
            "Processing lookup for customer id %d and product id %d", customer_id, product_id)
        return cls.query.filter(cls.customer_id == customer_id, cls.product_id == product_id).first()

    @classmethod
    def check_exist_by_customer_id_and_product_id(cls, customer_id, product_id):
        """ check if this ShopCarts record is exists by customer id and product id """
        logger.info(
            "Checking record with customer id %d and product id %d", customer_id, product_id)
        return cls.query.filter(cls.customer_id == customer_id, cls.product_id == product_id).count() != 0
