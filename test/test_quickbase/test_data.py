test_get_app_tables = [
  {
    "alias": "_DBID_MEMBERSHIP",
    "created": "2020-09-01T20:16:15Z",
    "defaultSortFieldId": 4,
    "defaultSortOrder": "ASC",
    "description": "",
    "id": "abcdef",
    "keyFieldId": 3,
    "name": "Members",
    "nextFieldId": 100,
    "nextRecordId": 250,
    "pluralRecordName": "Members",
    "singleRecordName": "Member",
    "sizeLimit": "500 MB",
    "spaceRemaining": "500 MB",
    "spaceUsed": "50 KB",
    "updated": "2020-10-11T15:25:53Z"
  },
  {
    "alias": "_DBID_MEETINGS",
    "created": "2020-07-10T03:16:15Z",
    "defaultSortFieldId": 7,
    "defaultSortOrder": "DESC",
    "description": "",
    "id": "brqdmcesd",
    "keyFieldId": 7,
    "name": "Meetings",
    "nextFieldId": 18,
    "nextRecordId": 81,
    "pluralRecordName": "Meetings",
    "singleRecordName": "Meeting",
    "sizeLimit": "500 MB",
    "spaceRemaining": "500 MB",
    "spaceUsed": "100 KB",
    "updated": "2020-09-11T14:17:23Z"
  }]

test_query_records = {
  "data": [
    {
      "1": {
        "value": "2020-01-31T15:13:35Z"
      },
      "11": {
        "value": ""
      },
      "5": {
        "value": ""
      },
      "10": {
        "value": ""
      },
      "2": {
        "value": "First name"
      },
      "12": {
        "value": ""
      },
      "3": {
        "value": "Last name"
      },
      "6": {
        "value": "exampleemail@example.com"
      },
      "4": {
        "value": "(555) 555-5555"
      },
      "9": {
        "value": "Wirdd"
      },
      "8": {
        "value": "99999"
      }
    }
  ],
  "fields": [
    {
      "id": 1,
      "label": "Date Created",
      "type": "timestamp"
    },
    {
      "id": 2,
      "label": "First Name",
      "type": "text"
    },
    {
      "id": 3,
      "label": "Last Name",
      "type": "text"
    },
    {
      "id": 4,
      "label": "Phone Number",
      "type": "phone"
    },
    {
      "id": 5,
      "label": "Address: City",
      "type": "text"
    },
    {
      "id": 6,
      "label": "Email",
      "type": "email"
    },
    {
      "id": 8,
      "label": "ZIP Code",
      "type": "text"
    },
    {
      "id": 9,
      "label": "City",
      "type": "text"
    },
    {
      "id": 10,
      "label": "State/Region",
      "type": "text-multiple-choice"
    },
    {
      "id": 11,
      "label": "Street 1",
      "type": "text"
    },
    {
      "id": 12,
      "label": "Gender Identity",
      "type": "text-multi-line"
    }
  ],
  "metadata": {
    "numFields": 11,
    "numRecords": 1,
    "skip": 0,
    "totalRecords": 1
  }
}
