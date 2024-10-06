import requests
import os, base64
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

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
    

    def create_payment(model, result_status, order_object, db):
        o_id = result_status['order']['id']
        createDate = result_status['order']['createTime']
        amount = result_status['order']['amount']
        currency = result_status['order']['currency']
        orderType = result_status['order']['typeRid']
        orderstatus = result_status['order']['status']
        new_object = model(order_id=o_id,
                            currency=currency,
                            order_status=orderstatus,
                            amount=amount,
                            order_type=orderType,
                            createDate=createDate,
                            order_object_id=order_object.id)
        db.add(new_object)
        db.commit()
        return new_object
    

    def check_installment_or_cash_order(order_object, redirect_page, price, id):
        if order_object.bank_installment_paid:
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
    

    def get_order_status_and_change_order_payment_status(payment_id, new_paid_object, db, order_model):
        new_paid_object = new_paid_object.first()
        cancellation_statuses = ["Cancelled","Rejected","Refused","Expired","Declined","Refunded"]
        response = KapitalPayment.get_order_status(payment_id)
        if response:
            status = response["order"]["status"]
            if status not in cancellation_statuses:
                print("first paid > ", new_paid_object.successfully_paid)
                if not new_paid_object.successfully_paid:
                    new_paid_object.successfully_paid=True

                    db.commit()
                    db.refresh(new_paid_object)
                    print("last paid > ", new_paid_object.successfully_paid)
                order_model.order_status = status
                db.commit()
                db.refresh(order_model)
                order_model
                return "Accepted"
            else:
                return status
        

class NewOrderObject:
    def create_order(self, redirect_page, package_object, 
                     created_object, payment_model, subscribe_id, db):
        
        price = package_object.price if package_object.price else 0
        if price == 0:
            created_object.is_free = True
            db.commit()
            db.refresh(created_object)
            return JSONResponse("free", status_code=201)
        
        data = KapitalPayment.check_installment_or_cash_order(created_object, redirect_page, price, subscribe_id)

        final_response = KapitalPayment.return_final_response_for_created_payment(data)

        try:
            pay_obj = KapitalPayment.create_payment(model=payment_model, 
                                                    result_status=final_response["result_status"], 
                                                    order_object=created_object, db=db)  
            del final_response['result_status']
            if price != 0:
                created_object.successfuly_paid=False
                db.commit()
                db.refresh(created_object)
            print("cr suc paid > ", created_object.successfuly_paid)
            return JSONResponse(final_response, status_code=201)
        except Exception as err:
            return JSONResponse(str(err), status_code=400)
    

    

    def if_paid_change_the_order_status(self, order, payment_model, db):
        order_id = order.first().id 
        print("oid > ", order_id)
        order_model = db.query(payment_model).filter(payment_model.order_object_id==order_id).first()
        if order_model:
            response = KapitalPayment.get_order_status_and_change_order_payment_status(
                payment_id=order_model.order_id,
                new_paid_object=order,
                db=db,
                order_model=order_model
            )
            return {
                "order":order_model.order.item.name,
                "successfully_paid":order_model.order.successfully_paid
            }
        return JSONResponse({"error":"Order not found"}, status_code=404)