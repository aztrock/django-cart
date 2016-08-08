import datetime
import models

CART_ID = 'CART-ID'

class ItemAlreadyExists(Exception):
    pass

class ItemDoesNotExist(Exception):
    pass

class Cart:
    def __init__(self, request, ref=None):
        self.cart_id = request.session.get(CART_ID)
        if self.cart_id:
            try:
                cart = models.Cart.objects.get(id=self.cart_id, checked_out=False)
            except models.Cart.DoesNotExist:
                cart = self.new(request, ref)
        else:
            cart = self.new(request, ref)
        self.cart = cart

    def __iter__(self):
        for item in self.cart.item_set.all():
            yield item

    def new(self, request, ref=None):
        if ref:
           cart = models.Cart(creation_date=datetime.datetime.now())
        else:
           cart = models.Cart(creation_date=datetime.datetime.now(), ref=ref)
        cart.save()
        request.session[CART_ID] = cart.id
        self.cart_id = cart.id
        return cart

    def add(self, product, unit_price, quantity=1):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            item = models.Item()
            item.cart = self.cart
            item.product = product
            item.unit_price = unit_price
            item.quantity = quantity
            item.save()
        else: #ItemAlreadyExists
            item.unit_price = unit_price
            item.quantity = item.quantity + int(quantity)
            item.save()

    def remove(self, product):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else:
            item.delete()

    def update(self, product, quantity, unit_price=None):
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        else: #ItemAlreadyExists
            if quantity == 0:
                item.delete()
            else:
                item.unit_price = unit_price
                item.quantity = int(quantity)
                item.save()

    def count(self):
        result = 0
        for item in self.cart.item_set.all():
            result += 1 * item.quantity
        return result
        
    def summary(self):
        result = 0
        for item in self.cart.item_set.all():
            result += item.total_price
        return result

    def get_id(self):
        return self.cart_id.pk

    def clear(self):
        for item in self.cart.item_set.all():
            item.delete()

