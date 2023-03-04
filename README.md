# Ngonar Bank Core

This is the processing unit that receives MQ message from API and send the response back to the API after certain process is done.

The steps are :
1. wait for the incoming MQ
```python
channel = connection.channel()
channel.queue_declare(queue='rpc_queue')
```
2. parse the message
```python
body_data = str(body.decode()) \
            .replace("'", "") \
            .split(".")
```
3. process the message
```python
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
```
4. give proper response
```python
response = json.dumps(apiResp.__dict__)
```

### Web & API Module
https://github.com/ngonar/NgonarBankWeb

### Reference : 
* https://www.rabbitmq.com