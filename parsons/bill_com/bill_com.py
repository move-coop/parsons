import requests
import json


class BillCom(object):
    """
    `Args:`
        userName: str
            The Bill.com username
        password: str
            The Bill.com password
        orgId: str
            The Bill.com organization id
        devKey: str
            The Bill.com dev key
        endPointUrl:
            The Bill.com end point url
    """

    def __init__(self, userName, password, orgId, devKey, endPointUrl):
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        params = {
            "userName": userName,
            "password": password,
            "orgId": orgId,
            "devKey": devKey
        }
        response = requests.post(url="%sLogin.json" % endPointUrl,
                                 data=params,
                                 headers=self.headers)
        self.devKey = devKey
        self.endPointUrl = endPointUrl
        self.sessionId = response.json()['response_data']['sessionId']

    def getPayload(self, data):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The devKey and sessionId should not be included as they are
                dealt with separately.

        `Returns:`
            A dictionary of the payload to be sent in the request with the
            devKey and sessionId added.
        """
        return {"devKey": self.devKey,
                "sessionId": self.sessionId,
                "data": json.dumps(data)}

    def postRequest(self, data, action, objectId):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The devKey and sessionId should not be included as they are
                dealt with separately.
            action: str
                The action to be taken on the given object.
                Possible values are "List", "Read", "Create", and "Send".
            objectId: str
                The id of the object. Possible values are "User", "Customer", and "Invoice".

        `Returns:`
            A dictionary containing the JSON response from the post request.
        """
        payload = self.getPayload(data)
        if action in ('Read', 'Create'):
            url = "%sCrud/%s/%s.json" % (self.endPointUrl, action, objectId)
        elif action == "Send":
            url = "%s%s%s.json" % (self.endPointUrl, action, objectId)
        else:
            url = "%s%s/%s.json" % (self.endPointUrl, action, objectId)
        response = requests.post(url=url, data=payload, headers=self.headers)
        return response.json()

    def getRequestResponse(self, data, action, objectId, field="response_data"):
        """
        `Args:`
            data: dict
                A dictionary containing the payload to be sent in the request.
                The devKey and sessionId should not be included as they are
                dealt with separately.
            action: str
                The action to be taken on the given object.
                Possible values are "List", "Read", "Create", and "Send".
            objectId: str
                The id of the object. Possible values are "User", "Customer", and "Invoice".
            field: str
                The JSON field where the response data is stored. Defaults to "response_data".

        `Returns:`
            A dictionary containing the choosen field from the JSON response from the post request.
        """
        return self.postRequest(data, action, objectId)[field]

    def getUserList(self, startUser=0, maxUser=999):
        """
        `Args:`
            startUser: int
                The index of first user to return
            maxUser: str
                The index of the max user to return

        `Returns:`
            A list of dictionaries of user information for every user from startUser to maxUser.
        """
        data={
           "start": startUser,
           "max": maxUser,
        }
        return self.getRequestResponse(data, "List", "User")

    def getCustomerList(self, startCustomer=0, maxCustomer=999):
        """
        `Args:`
            startUser: int
                The index of first customer to return
            maxUser: str
                The index of the max customer to return

        `Returns:`
            A list of dictionaries of customer information for
            every user from startCustomer to maxCustomer.
        """
        data={
           "start": startCustomer,
           "max": maxCustomer,
        }
        return self.getRequestResponse(data, "List", "Customer")

    def readCustomer(self, customerId):
        """
        `Args:`
            customerId: str
                The id of the customer to query

        `Returns:`
            A dictionary of the customer's information.
        """
        data={
            'id': customerId
        }
        return self.getRequestResponse(data, "Read", "Customer")

    def readInvoice(self, invoiceId):
        """
        `Args:`
            invoiceId: str
                The id of the invoice to query

        `Returns:`
            A dictionary of the invoice information.
        """
        data={
           "id": invoiceId
        }
        return self.getRequestResponse(data, "Read", "invoice")

    def checkCustomer(self, customer1, customer2):
        """
        `Args:`
            customer1: dict
                A dictionary of data on customer1
            customer2: dict
                A dictionary of data on customer2

        `Returns:`
            True if either
                1. customer1 and customer2 have the same id
                OR
                2. all other fields match
            False otherwise
                
        """
        if "id" in customer1.keys():
            if customer1["id"] == customer2["id"]:
                return True
        for key in customer1.keys():
            if customer1[key] != customer2[key]:
                return False
        return True

    def createCustomer(self, customer):
        """
        `Args:`
            customer: dict
                A dictionary of data on the customer

        `Returns:`
            A dictionary of the customer's information including an id.
            If the customer already exists, this function will not
            create a new id and instead use the existing id.
        """
        # check if customer already exists
        customerList = self.getCustomerList()
        for existingCustomer in customerList:
            if self.checkCustomer(customer, existingCustomer):
                return existingCustomer
        # customer doesn't exist, create
        data={
            "obj": customer
        }
        return self.getRequestResponse(data, "Create", "Customer")

    def createInvoice(self, invoice):
        """
        `Args:`
            invoice: dict
                A dictionary of data on the invoice

        `Returns:`
            A dictionary of the invoice's information including an id.
        """
        data = {
            "obj": invoice
        }
        return self.getRequestResponse(data, "Create", "Invoice")

    def sendInvoice(self, invoiceId, fromUserId, toEmailAddresses, messageSubject, messageBody):
        """
        `Args:`
            invoiceId: str
                The id of the invoice to send
            fromUserId: str
                The id of the Bill.com user from whom to send the email
            toEmailAddresses:
                The customer's email address
            messageSubject:
                The subject of the email to send to the customer
            messageBody:
                The boyd of the email to send to the customer

        `Returns:`
            A dictionary of the sent invoice.
        """
        data={
          "invoiceId": invoiceId,
          "headers": {
            "fromUserId": fromUserId,
            "toEmailAddresses": toEmailAddresses,
            "subject": messageSubject
          },
          "content": {
            "body": messageBody
          }
        }
        return self.getRequestResponse(data, "Send", "Invoice")