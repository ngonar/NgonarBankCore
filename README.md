#Ngonar Bank Core

This is the processing unit that receives MQ message from API and send the response back to the API after certain process is done.

The steps are :
1. wait for the incoming MQ
2. parse the message
3. process the message
4. give proper response

Reference : 
* https://www.rabbitmq.com