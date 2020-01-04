from requests import request
import urllib.parse as parse

headers = {
	"Content-Type": "application/x-www-form-urlencoded"
}

params = {
	"userName": "<USERNAME>",
	"password": "<PASSWORD>",
	"orgId": "<ORG ID>",
	"devKey": "<DEV KEY>"
}

r = request("POST", "https://api-sandbox.bill.com/api/v2/Login.json", data=urllib.parse.urlencode(params), headers=headers)