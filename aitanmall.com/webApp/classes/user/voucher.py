from webApp.helper import general
from webApp.helper import voucher

class Voucher():

    def __init__(self, voucher_id, voucher_code ,voucher_description, voucher_discount_amount:float, voucher_discount_type, voucher_expire_date, voucher_max_usage, voucher_usage_count, voucher_status = "active"):
        self.voucher_id = voucher_id
        self.voucher_code = voucher_code
        self.voucher_description = voucher_description
        self.voucher_discount_amount = voucher_discount_amount
        self.voucher_discount_type = voucher_discount_type
        self.voucher_created_date = general.get_current_datetime()
        self.voucher_expire_date = voucher_expire_date
        self.voucher_max_usage = voucher_max_usage
        self.voucher_usage_count = voucher_usage_count
        self.voucher_status = voucher_status
    #============================================================================================
    #Accessor
    #=============================================================================================
    def get_voucher_id(self):
        return self.voucher_id

    def get_voucher_code(self):
        return self.voucher_code

    def get_voucher_description(self):
        return self.voucher_description
    
    def get_voucher_discount_amount(self):
        return self.voucher_discount_amount

    def get_voucher_discount_type(self):
        return self.voucher_discount_type
    
    def get_voucher_created_date(self):
        return self.voucher_created_date
    
    def get_voucher_expire_date(self):
        return self.voucher_expire_date

    def get_voucher_max_usage(self):
        return self.voucher_max_usage
    
    def get_voucher_usage_count(self):
        return self.voucher_usage_count

    def get_voucher_status(self):
        return self.voucher_status

    #=============================================================================================
    #Mutator
    #=============================================================================================
