import pika
import sqlite3
import json

db_url = "/Users/ngonar/PycharmProjects/NgonarBank/ngonarbank/db.sqlite3"

class AccountApiResponse:
    rc = ""
    current_balance = ""
    last_balance = ""
    description = ""

def get_balance(norek):
    con = sqlite3.connect(db_url)
    cur = con.cursor()

    for row in cur.execute("SELECT account_balance FROM account_bankaccount WHERE account_no='"+norek+"'"):
        print(row)

    con.close()

    return row

def deduct_balance(norek=None, amount=None):

    if norek and amount:
        con = sqlite3.connect(db_url)
        cur = con.cursor()

        query = "UPDATE account_bankaccount set account_balance = account_balance - "+amount+" WHERE account_no='"+norek+"'"

        cur.execute(query)
        con.commit()

        con.close()

def topup_balance(norek=None, amount=None):

    if norek and amount:
        con = sqlite3.connect(db_url)
        cur = con.cursor()

        query = "UPDATE account_bankaccount set account_balance = account_balance + "+amount+" WHERE account_no='"+norek+"'"

        cur.execute(query)
        con.commit()

        con.close()

def processing_the_request():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='localhost',
            credentials=pika.PlainCredentials(username='rabbit', password='admin')
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue='rpc_queue')

    def on_request(ch, method, props, body):

        print("[x] received %r" % body)

        body_data = str(body.decode()) \
            .replace("'", "") \
            .split(".")

        norek = body_data[1]
        amount = body_data[2]

        response = ""

        if body_data[0] == "deduct":
            current_balance = get_balance(norek)
            print(current_balance[0])

            if (int(current_balance[0]) >= int(amount)):
                deduct_balance(norek, amount)
                apiResp = AccountApiResponse()
                apiResp.rc = "0000"
                apiResp.last_balance = str(current_balance[0])
                apiResp.current_balance = str(get_balance(norek)[0])
                apiResp.description = "Deduct Success to account "+norek+" for $"+amount
                response = json.dumps(apiResp.__dict__)
            else:
                apiResp = AccountApiResponse()
                apiResp.rc = "0046"
                apiResp.last_balance = str(current_balance[0])
                apiResp.current_balance = str(get_balance(norek)[0])
                apiResp.description = "Insufficient Balance "
                response = json.dumps(apiResp.__dict__)

        elif body_data[0] == "topup":
            current_balance = get_balance(norek)
            print(current_balance[0])
            topup_balance(norek, amount)
            apiResp = AccountApiResponse()
            apiResp.rc = "0000"
            apiResp.last_balance = str(current_balance[0])
            apiResp.current_balance = str(get_balance(norek)[0])
            apiResp.description = "Topup Success to account " + norek + " for $" + amount
            response = json.dumps(apiResp.__dict__)


        print("Response : ", response)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

    print(" [x] Awaiting RPC requests")
    channel.start_consuming()

def main():
    processing_the_request()

if __name__ == "__main__":
    main()