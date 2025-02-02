from __future__ import annotations

class Cart_item():
    def __init__(self, id:int(), prd_id, prd_name, prd_img, quantity:int, prd_price, prd_var_id, prd_var_name, prd_sku, prd_var_img, sub_total:float, total:float, merchant_id):
        self.id = id
        self.prd_id = prd_id
        self.prd_name = prd_name
        self.prd_img = prd_img
        self.quantity = int(quantity)
        self.prd_price = prd_price
        self.prd_var_id = prd_var_id
        self.prd_var_name = prd_var_name
        self.prd_sku = prd_sku
        self.prd_var_img = prd_var_img
        self.sub_total = float(sub_total)
        self.total = float(total)
        self.merchant_id = merchant_id
    #=============================================================================================
    #Accessor
    #=============================================================================================
    def get_id(self):
        return self.id
    
    def get_prd_id(self):
        return self.prd_id
    
    def get_prd_name(self):
        return self.prd_name

    def get_prd_img(self):
        return self.prd_img
    
    def get_quantity(self):
        return self.quantity

    def get_prd_price(self):
        return self.prd_price

    def get_prd_var_id(self):
        return self.prd_var_id

    def get_prd_var_name(self):
        return self.prd_var_name
    
    def get_prd_sku(self):
        return self.prd_sku

    def get_prd_var_img(self):
        return self.prd_var_img
    
    def get_sub_total(self):
        return self.sub_total
    
    def get_total(self):
        return self.total

    def get_ord_status(self):
        return self.ord_status

    def get_merchant_id(self):
        return self.merchant_id

    #=============================================================================================
    #Mutator
    #=============================================================================================
    def increase_quantity(self, amount:int):
        self.quantity += amount
        return True

    def increase_sub_total(self, amount:float):
        self.sub_total += amount
        return True
    
    def increase_total(self, amount:float):
        self.total += amount
        return True
    
    def decrease_quantity(self, amount:int):
        self.quantity -= amount
        return True

    def decrease_sub_total(self, amount:float):
        self.sub_total -= amount if amount <= self.sub_total else self.sub_total
        return True
    
    def decrease_total(self, amount:float):
        self.total -= amount if amount <= self.total else self.total
        return True
    
    def to_dict(self) -> dict:
        return {"id": self.id, "prd_id": self.prd_id, "prd_name": self.prd_name, "prd_img": self.prd_img,\
            "quantity": self.quantity, "prd_price": self.prd_price, "prd_var_id": self.prd_var_id, "prd_var_name": self.prd_var_name,\
            "prd_sku": self.prd_sku, "prd_var_img": self.prd_var_img, "sub_total": self.sub_total,\
            "total": self.total, "merchant_id": self.merchant_id}

    @classmethod
    def from_dict(cls, data: dict) -> Cart_item:
        return cls(data["id"], data["prd_id"], data["prd_name"],data["prd_img"], data["quantity"], data["prd_price"],data["prd_var_id"], data["prd_var_name"], data["prd_sku"], data["prd_var_img"], data["sub_total"], data["total"],data["merchant_id"])