import factory
from service.models import ShopCart


class ShopCartsFactory(factory.Factory):
    """Create fake shop cart records"""
    class Meta:
        model = ShopCart
    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    product_id = factory.Sequence(lambda n: n)
    quantities = factory.Sequence(lambda n: n)
    # price = factory.Sequence(lambda n: n)
