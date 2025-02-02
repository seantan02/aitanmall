from __future__ import annotations
from webApp.classes.cart_item import Cart_item


class Cart():

    def __init__(self, cart_items = [], total = 0.00):
        self.cart_items = cart_items
        self.total = total

    def __len__(self) -> int:
        return len(self.cart_items)
    
    #=============================================================================================
    #Accessor
    #=============================================================================================
    def get_cart_items(self):
        return self.cart_items

    def get_total(self):
        return self.total
        
    def product_already_exist(self, product_id, product_variation_id = -1) -> bool | Exception:
        try:
            for cart_item in self.cart_items:
                #If it is a dict
                if isinstance(cart_item, dict):
                    if str(cart_item["prd_id"]) == str(product_id):
                        if str(cart_item["prd_var_id"]) == str(product_variation_id):
                            return True
                #If it is a Cart_item object
                else:
                    if str(cart_item.get_prd_id()) == str(product_id):
                        if str(cart_item.get_prd_var_id()) == str(product_variation_id):
                            return True
            return False
        except Exception as e:
            return e
    #=============================================================================================
    #Mutator
    #=============================================================================================

    def add_cart_item(self, cart_item: dict | Cart_item):
        try:
            self.cart_items.append(cart_item)
            if isinstance(cart_item, dict):
                cart_item = Cart_item.from_dict(cart_item)
            cart_item_total = cart_item.get_total()
            self.total += cart_item_total
        except Exception as e:
            return e
    def increase_cart_total(self, amount:float) -> bool | Exception:
        try:
            self.total += amount
            return True
        except Exception as e:
            return e
        
    def reduce_cart_total(self, amount:float) -> bool | Exception:
        try:
            self.total -= amount
            return True
        except Exception as e:
            return e

    def remove_cart_item(self, cart_item_id) -> dict | Cart_item | None:
        try:
            for i in range(len(self.cart_items)):
                cart_item = self.cart_items[i]
                #If it is a dict
                if isinstance(cart_item, dict):
                    cart_item = Cart_item.from_dict(cart_item)
                #If it is a Cart_item object
                if str(cart_item.get_id()) == str(cart_item_id):
                    self.total -= (float(cart_item.get_prd_price()) * cart_item.get_quantity())
                    return self.cart_items.pop(i)
            #If nothing is return in for loop meaning nothing was found, so we return NOne
            return None
        except Exception as e:
            return e

    def to_dict(self) -> dict:
        return {"cart_items": self.cart_items, "total": self.total}
    
    @classmethod
    def from_dict(cls, data: dict) -> Cart:
        return cls(data["cart_items"], data["total"])