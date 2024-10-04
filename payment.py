import requests
import os, base64
from dotenv import load_dotenv

load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


REDIRECT_URL = os.getenv("PAYMENT_URL")
BASE_URL = f"{REDIRECT_URL}/api/"
GET_ORDER_URL = f"{REDIRECT_URL}/api/order"
ORDER_PATH = "/order"



HEADERS = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic ' + base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()
        }


class KapitalPayment:
    def postPay(data, path):
        r = requests.post(
            f"{BASE_URL}{path}", json=data,
            verify=False, headers=HEADERS
        )
        
        print("Post Pay > ", r.json())
        return r.json()
    

    def get_order_status(order_id):
        r = requests.get(f"{GET_ORDER_URL}/{order_id}/",  headers=HEADERS)
        print("Order Status > ", r.json())
        return r.json()


    def create_order_data(**args):
        price = args.get("price")
        description = args.get("description")
        redirect_page= args.get("redirect_page")
        
        order_type = args.get("order_type")
        if order_type == 0:
            order_type = "Order_SMS"
        return {
                "order": {
                    "typeRid":order_type,
                    "amount":price if price else 0,
                    "currency":"AZN",
                    "language": "en",
                    "description": description,
                    "hppRedirectUrl":redirect_page,
                    "hppCofCapturePurposes": ["Cit"]
                }
            }
    

    def create_payment(model, result_status,order_object):
        o_id = result_status['order']['id']
        createDate = result_status['order']['createTime']
        amount = result_status['order']['amount']
        currency = result_status['order']['currency']
        orderType = result_status['order']['typeRid']
        orderstatus = result_status['order']['status']
        new_object = model.objects.get_or_create(order_id=o_id,
                                                currency=currency,
                                                order_status=orderstatus,
                                                amount=amount,
                                                order_type=orderType,
                                                createDate=createDate,
                                                order_model=order_object)
        print("New Payment object > ", new_object[0].id)
        print("Payment model > ", model)
        return new_object
    

    def check_installment_or_cash_order(order_object, redirect_page, price, id):
        data = ''
        if hasattr(order_object, 'installment_paid'):
            description = f"TAKSIT={order_object.bank_installment_month}"
        else:
            description = id

        data = KapitalPayment.create_order_data(
            redirect_page=redirect_page,
            price=price,
            description=description,
            order_type=0)
        return data
    

    def return_final_response_for_created_payment(data):
        response = KapitalPayment.postPay(data, path="/order")
        order_id = response['order']['id']
        order_password = response["order"]["password"]
        redirectURL = response["order"]["hppUrl"]
        result_status = KapitalPayment.get_order_status(order_id=order_id)
        
        final_response = {
            'result_status':result_status,
            'url':  f"{redirectURL}?id={order_id}&password={order_password}",
            'status': result_status["order"]["status"]
        }
        return final_response
    

    def get_order_status_and_change_order_payment_status(model, payment_id):
        response = KapitalPayment.get_order_status(payment_id)
        if response:
            status = response["order"]["status"]
            return 
        


