import requests

def get_test_secret_key():
    toyyibpay_secret = "zyag0koc-r9eh-bhm5-9s7q-sm6ojr7edk7o"

    return toyyibpay_secret

def create_test_bill(test_secreat_key, expire_datetime, total_customer_payment_in_cent, return_url, callback_url, bill_to_name, bill_to_email, bill_to_phone_number, reference_no = ""):
    """
    This method create a testing bill with toyyibpay.
    :return: BillCode used to redirect if successful; None otherwise.
    """
    try:
        #To make sure customer pay the amount we promised
        total_customer_payment_in_cent -= 100
        toyyibpay_link = "https://dev.toyyibpay.com"
        some_data = {
            'userSecretKey': test_secreat_key,
            'categoryCode':'hnh0hfrq',
            'billName':'Orders on AiTanMall',
            'billDescription':'Order details in whatsapp or online portal',
            'billPriceSetting':1,
            'billPayorInfo':1,
            'billAmount':total_customer_payment_in_cent,
            'billReturnUrl':return_url,
            'billCallbackUrl':callback_url,
            'billExternalReferenceNo' : reference_no,
            'billTo': bill_to_name,
            'billEmail': bill_to_email,
            'billPhone': bill_to_phone_number,
            'billSplitPayment':0,
            'billSplitPaymentArgs':'',
            'billPaymentChannel':'0',
            'billContentEmail':'Thank you for purchasing our product!',
            'billChargeToCustomer':0,
            'billExpiryDate':expire_datetime,
            'billExpiryDays':1
        }  
        toyyibpay_response = requests.post(toyyibpay_link+'/index.php/api/createBill', data=some_data)
        toyyibpay_response = toyyibpay_response.json()
        toyyibpay_billcode = toyyibpay_response[0]["BillCode"]

        return toyyibpay_billcode
    except Exception as e:
        return e

def get_test_bill(bill_code, status = None):
    """
    This method get a testing bill with toyyibpay.
    :return: json if exist
    """
    try:
        toyyibpay_link = "https://dev.toyyibpay.com"
        if status == None:
            some_data = {
                'billCode': bill_code
            }  
        else:
            some_data = {
                'billCode': bill_code,
                'billpaymentStatus': status
            } 
        toyyibpay_response = requests.post(toyyibpay_link+'/index.php/api/getBillTransactions', data=some_data)
        toyyibpay_response = toyyibpay_response.json()

        return toyyibpay_response
    except Exception as e:
        return e

def get_secret_key():
    toyyibpay_secret = "vmu01mo7-0uwl-brib-b04x-olavdz9zlzvf"

    return toyyibpay_secret

def create_bill(test_secreat_key, expire_datetime, total_customer_payment_in_cent, return_url, callback_url, bill_to_name, bill_to_email, bill_to_phone_number, reference_no = ""):
    """
    This method create a testing bill with toyyibpay.
    :return: BillCode used to redirect if successful; None otherwise.
    """
    try:
        #To make sure customer pay the amount he sees
        total_customer_payment_in_cent -= 100
        toyyibpay_link = "https://toyyibpay.com"
        some_data = {
            'userSecretKey': test_secreat_key,
            'categoryCode':'jhzpu66v',
            'billName':'Orders on AiTanMall',
            'billDescription':'Order details in whatsapp or online portal',
            'billPriceSetting':1,
            'billPayorInfo':1,
            'billAmount':total_customer_payment_in_cent,
            'billReturnUrl':return_url,
            'billCallbackUrl':callback_url,
            'billExternalReferenceNo' : reference_no,
            'billTo': bill_to_name,
            'billEmail': bill_to_email,
            'billPhone': bill_to_phone_number,
            'billSplitPayment':0,
            'billSplitPaymentArgs':'',
            'billPaymentChannel':'0',
            'billContentEmail':'Thank you for purchasing our product!',
            'billChargeToCustomer':0,
            'billExpiryDate':expire_datetime,
            'billExpiryDays':1
        }  
        toyyibpay_response = requests.post(toyyibpay_link+'/index.php/api/createBill', data=some_data)
        toyyibpay_response = toyyibpay_response.json()
        toyyibpay_billcode = toyyibpay_response[0]["BillCode"]

        return toyyibpay_billcode
    except Exception as e:
        return e
    
def get_bill(bill_code, status = None):
    """
    This method get a testing bill with toyyibpay.
    :return: json if exist
    """
    try:
        toyyibpay_link = "https://toyyibpay.com"
        if status == None:
            some_data = {
                'billCode': bill_code
            }  
        else:
            some_data = {
                'billCode': bill_code,
                'billpaymentStatus': status
            } 
        toyyibpay_response = requests.post(toyyibpay_link+'/index.php/api/getBillTransactions', data=some_data)
        toyyibpay_response = toyyibpay_response.json()

        return toyyibpay_response
    except Exception as e:
        return e