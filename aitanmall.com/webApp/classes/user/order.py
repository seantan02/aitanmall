from webApp.helper import general

class Order():

    def __init__(self, id:int, ord_id:int, ord_prd_id:int, ord_quantity:int, ord_price:float, ord_date:str, ord_prd_name:str, merchant_id):
        self.id = int(id)
        self.ord_id = ord_id
        self.ord_prd_id = ord_prd_id
        self.ord_prd_var_id = -1
        self.ord_prd_var_name = ""
        self.ord_prd_var_img = ""
        self.ord_quantity = int(ord_quantity)
        self.ord_price = float(ord_price)
        self.ord_date = ord_date
        self.ord_payment_method_id = -1
        self.ord_payment_method_name = ""
        self.ord_status = "pending"
        self.ord_prd_name = ord_prd_name
        self.ord_prd_img = ""
        self.ord_prd_sku = "none"
        self.merchant_id = merchant_id
        self.sub_total = round(self.ord_quantity*self.ord_price, 2)
    #=============================================================================================
    #Accessor
    #=============================================================================================
    def get_id(self):
        return self.id
    
    def get_ord_id(self):
        return self.ord_id

    def get_ord_prd_id(self):
        return self.ord_prd_id
    
    def get_ord_prd_var_id(self):
        return self.ord_prd_var_id

    def get_ord_prd_var_name(self):
        return self.ord_prd_var_name

    def get_ord_prd_var_img(self):
        return self.ord_prd_var_img

    def get_ord_quantity(self):
        return self.ord_quantity
    
    def get_ord_price(self):
        return self.ord_price

    def get_ord_date(self):
        return self.ord_date
    
    def get_ord_payment_method_id(self):
        return self.ord_payment_method_id
    
    def get_ord_payment_method_name(self):
        return self.ord_payment_method_name

    def get_ord_status(self):
        return self.ord_status

    def get_ord_prd_name(self):
        return self.ord_prd_name

    def get_ord_prd_img(self):
        return self.ord_prd_img
    
    def get_ord_prd_sku(self):
        return self.ord_prd_sku

    def get_merchant_id(self):
        return self.merchant_id
    
    def get_sub_total(self):
        return self.sub_total

    #=============================================================================================
    #Mutator
    #=============================================================================================

    def update_ord_id(self, new_id) -> AssertionError|bool:
        FIXED_ORDER_ID_LENGTH = 18
        assert len(str(new_id)) == FIXED_ORDER_ID_LENGTH, f"Order ID has to be length {FIXED_ORDER_ID_LENGTH}"
        self.ord_id = new_id

    def update_ord_prd_id(self, new_id) -> AssertionError|bool:
        self.ord_prd_id = new_id

    def update_ord_prd_var_id(self, new_id):
        assert isinstance(new_id, int), f"Product variation ID has to be integer"
        self.ord_prd_var_id = new_id

    def update_ord_prd_var_name(self, variation_name):
        assert isinstance(variation_name, str), f"Product variation name has to be string"
        self.ord_prd_var_name = variation_name

    def update_ord_prd_var_img(self, variation_image_name):
        assert isinstance(variation_image_name, str), f"Product variation image name has to be string"
        self.ord_prd_var_img = variation_image_name

    def update_ord_quantity(self, quantity:int):
        assert isinstance(quantity, int), f"Purchase quantity has to be integer"
        assert quantity >= 1, f"Purchase quantity has to be more than or equal to 1"
        self.ord_quantity = quantity
    
    def update_ord_price(self, new_price):
        MINIMUM_PRICE = 5.00
        assert isinstance(new_price, float), f"Product price has to be float"
        assert new_price >= MINIMUM_PRICE or new_price == 0.00, f"Purchase quantity has to be at least {MINIMUM_PRICE} or 0.00"
        self.ord_price = new_price

    def update_ord_date(self, new_date):
        assert isinstance(new_date, str), f"Order date has to be str"
        assert general.is_datetime(new_date), f"Order date has to be in datetime format following MYSQL style."
        self.ord_date = new_date
    
    def update_ord_payment_method_id(self, new_payment_method_id):
        assert isinstance(new_payment_method_id, int), f"Payment method has to be integer"
        self.ord_payment_method_id = new_payment_method_id
    
    def update_ord_payment_method_name(self, new_payment_method_name):
        assert isinstance(new_payment_method_name, str), f"Payment method name has to be string"
        self.ord_payment_method_name = new_payment_method_name

    def update_ord_status(self, new_status):
        assert isinstance(new_status, str), f"Order status has to be string"
        self.ord_status = new_status

    def update_ord_prd_name(self, new_product_name):
        assert isinstance(new_product_name, str), f"Product name has to be string"
        self.ord_prd_name = new_product_name

    def update_ord_prd_img(self, new_product_image_name):
        assert isinstance(new_product_image_name, str), f"Product image name has to be string"
        self.ord_prd_img = new_product_image_name
    
    def update_ord_prd_sku(self, new_sku):
        assert isinstance(new_sku, str), f"Product sku has to be string"
        self.ord_prd_sku = new_sku

    def update_sub_total(self, new_sub_total:float):
        assert isinstance(new_sub_total, float), f"Order sub total has to be float"
        self.sub_total = round(new_sub_total, 2)