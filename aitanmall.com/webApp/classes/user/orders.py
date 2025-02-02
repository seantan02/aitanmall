from webApp.helper import general
from webApp.classes.user.order import Order


class Orders():

    def __init__(self, cust_id ,ord_date:str, ord_total:float, ord_payment_gateway_fees = 0.00, ord_status = "pending", ord_receipt = "pending"):
        self.mysql_conn = general.create_general_mysql_conn()
        self.mysql_cursor = self.mysql_conn.cursor()
        self.ord_id = general.generate_unique_order_id(self.mysql_cursor,"SAMYORD",11)
        self.cust_id = cust_id
        self.ord_date = ord_date
        self.ord_total = ord_total
        self.ord_payment_method_nku = ""
        self.ord_payment_gateway_fees = ord_payment_gateway_fees
        self.ord_status = ord_status
        self.ord_receipt = ord_receipt
        self.ord_count = 0
        self.ord_details = list()
        self.mysql_cursor.close()
        self.mysql_conn.close()

    #=============================================================================================
    #Accessor
    #=============================================================================================
    def get_ord_id(self):
        return self.ord_id

    def get_cust_id(self):
        return self.cust_id
    
    def get_ord_date(self):
        return self.ord_date

    def get_ord_total(self):
        return self.ord_total

    def get_ord_payment_method_nku(self):
        return self.ord_payment_method_nku
    
    def get_ord_payment_gateway_fees(self):
        return self.ord_payment_gateway_fees

    def get_ord_status(self):
        return self.ord_status
    
    def get_ord_receipt(self):
        return self.ord_receipt
    
    def get_ord_count(self):
        return self.ord_count
    
    def get_ord_details(self):
        return self.ord_details

    def get_ord_total_amount(self) -> None | float:
        try:
            total_amount = 0.00
            for i in range(len(self.ord_details)):
                ord_sub_total = self.ord_details[i].get_sub_total()
                ord_sub_total = float(ord_sub_total)
                total_amount += ord_sub_total
            return round(total_amount, 2)
        except:
            return None

    #=============================================================================================
    #Mutator
    #=============================================================================================

    def update_cust_id(self, new_id) -> AssertionError|bool:
        self.ord_id = new_id
        return True
    
    def update_ord_date(self, new_date):
        assert isinstance(new_date, str), f"Order date has to be str"
        assert general.is_datetime(new_date), f"Order date has to be in datetime format following MYSQL style."
        self.ord_date = new_date
    
    def update_ord_total(self, new_total):
        assert isinstance(new_total, float), f"Order total has to be float"
        self.ord_total = round(new_total, 2)
    
    def update_ord_payment_method_nku(self, new_payment_method_nku):
        assert isinstance(new_payment_method_nku, str), f"Payment method nku has to be string"
        self.ord_payment_method_nku = new_payment_method_nku

    def update_ord_payment_gateway_fees(self, new_ord_payment_gateway_fees):
        assert isinstance(new_ord_payment_gateway_fees, float), f"Order gateway fees need to be float"
        self.ord_payment_gateway_fees = new_ord_payment_gateway_fees

    def update_ord_status(self, new_status):
        assert isinstance(new_status, str), f"Order status has to be string"
        self.ord_status = new_status

    def update_ord_receipt(self, new_ord_receipt:str):
        assert isinstance(new_ord_receipt, str), f"Order receipt status has to be string"
        self.ord_receipt = round(new_ord_receipt, 2)

    #method to add order details 
    def add_ord_details(self, ord_details:Order) -> AssertionError|bool:
        assert isinstance(ord_details, Order), f"Only order object can be added"
        self.ord_details.append(ord_details)
        self.ord_count += 1
        return True
    
    def remove_ord_details(self, ord_details_id:int) -> AssertionError|Order|None:
        assert isinstance(ord_details_id, int), f"Order details ID need to be integer"
        assert ord_details_id > 0, f"Order details ID is always bigger or equal to 1"
        for i in range(len(self.ord_details)):
            ord_detail = self.ord_details[i]
            if ord_detail.get_id() == ord_details_id:
                removed = self.ord_details.pop(i)
                self.ord_count -= 1
                return removed
        return None