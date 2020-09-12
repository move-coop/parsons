
# Expected auth token response json
auth_token = {
    "access_token": "MYFAKETOKEN",
    "scope": "read:account write:account",
    "expires_in": 7200,
    "token_type": "Bearer"
}

organizations = {
    'items': [{
        'id': 'LePEoKzD3',
        'type': 'Organization',
        'name': 'Org A',
        'createdAt': '2018-03-01T17:05:15.386Z'
    }, {
        'id': 'lnCrK2fSD',
        'type': 'Organization',
        'name': 'Org B',
        'createdAt': '2019-01-17T19:47:18.133Z'
    }, {
        'id': 'raqlV2HGd',
        'type': 'Organization',
        'name': 'Org C',
        'createdAt': '2019-01-17T19:49:55.249Z'
    }],
    'pagination': {
        'cursor': 'WzEsMTAwMF',
        'hasNextPage': False,
        'total': 3
    }
}

organization = {
    'id': 'LePEoKzD3',
    'type': 'Organization',
    'name': 'Org A',
    'createdAt': '2018-03-01T17:05:15.386Z'
}

groups = {
    'items': [{
        'id': 'Qqp6o90Si',
        'type': 'Group',
        'name': 'Group A',
        'countryCode': 'US',
        'active': True,
        'location': 'New York, NY, USA',
        'organizationId': 'LePEoKzD3',
        'preferredAreaCodes': [],
        'timezone': 'America/New_York',
        'createdAt': '2018-08-02T14:50:39.353Z'
    }, {
        'id': 'ygEXcRLEM',
        'type': 'Group',
        'name': 'Group A',
        'countryCode': 'US',
        'active': True,
        'location': 'New York, NY, USA',
        'organizationId': 'LePEoKzD3',
        'preferredAreaCodes': [],
        'timezone': 'America/New_York',
        'createdAt': '2018-12-19T18:43:30.253Z'
    }, {
        'id': 'svwi7gGV7',
        'type': 'Group',
        'name': 'Group A',
        'countryCode': 'US',
        'active': True,
        'location': 'New York, NY, USA',
        'organizationId': 'LePEoKzD3',
        'preferredAreaCodes': [],
        'timezone': 'America/New_York',
        'createdAt': '2018-12-21T20:39:05.178Z'
    }, {
        'id': 'XtXPxbYGv',
        'type': 'Group',
        'name': 'Group A',
        'description': 'A Group.',
        'countryCode': 'US',
        'active': True,
        'location': 'New York, NY, USA',
        'organizationId': 'LePEoKzD3',
        'preferredAreaCodes': [],
        'timezone': 'America/New_York',
        'createdAt': '2018-10-11T16:36:52.245Z'
    }],
    'pagination': {
        'cursor': 'WzEsMTAwMF',
        'hasNextPage': False,
        'total': 233
    }
}

group = {
    'id': 'zajXdqtzRt',
    'type': 'Group',
    'name': 'Group A',
    'countryCode': 'US',
    'active': True,
    'location': 'Colorado, USA',
    'organizationId': 'lnCrK2fSD',
    'preferredAreaCodes': [],
    'timezone': 'America/Denver',
    'createdAt': '2019-08-27T13:52:41.986Z'
}

lead = {
    'id': 'A6ebDlAtqB',
    'type': 'Lead',
    'customFields': {},
    'globalOptedOut': False,
    'groupIds': ['cMCH0hxwGt'],
    'firstName': 'Barack',
    'lastName': 'Obama',
    'organizationId': 'LePEoKzD3Z',
    'phoneNumber': '+15126993336',
    'tagIds': [],
    'createdAt': '2019-09-18T03:53:21.381Z'
}

leads_tbl_01 = {
    'id': 'yK5jo2tlms',
    'type': 'Lead',
    'customFields': {
        'address': '123 Main Street'
    },
    'globalOptedOut': False,
    'groupIds': ['cMCH0hxwGt'],
    'firstName': 'Lyndon',
    'lastName': 'Johnson',
    'organizationId': 'LePEoKzD3Z',
    'phoneNumber': '+14435705355',
    'tagIds': [],
    'createdAt': '2019-09-20T22:15:46.706Z'
}

leads_tbl_02 = {
    'id': 't18JdlHW7r',
    'type': 'Lead',
    'customFields': {
        'address': '124 Main Street'
    },
    'globalOptedOut': False,
    'groupIds': ['cMCH0hxwGt'],
    'firstName': 'Ann',
    'lastName': 'Richards',
    'organizationId': 'LePEoKzD3Z',
    'phoneNumber': '+14435705354',
    'tagIds': [],
    'createdAt': '2019-09-20T22:15:48.033Z'
}

leads = {
    'items': [{
        'id': 'wqy78hlz2',
        'type': 'Lead',
        'customFields': {},
        'globalOptedOut': False,
        'groupIds': ['cMCH0hxwGt'],
        'firstName': 'Elizabeth',
        'lastName': 'Warren',
        'organizationId': 'LePEoKzD3Z',
        'phoneNumber': '+14435705355',
        'tagIds': [],
        'createdAt': '2019-09-17T21:25:51.442Z'
    }, {
        'id': 'A6ebDlAtqB',
        'type': 'Lead',
        'customFields': {},
        'globalOptedOut': False,
        'groupIds': ['cMCH0hxwGt'],
        'firstName': 'Barack',
        'lastName': 'Obama',
        'organizationId': 'LePEoKzD3Z',
        'phoneNumber': '+15126993336',
        'tagIds': [],
        'createdAt': '2019-09-18T03:53:21.381Z'
    }],
    'pagination': {
        'cursor': 'WzEsMTAwMF',
        'hasNextPage': False,
        'total': 2
    }
}

updated_lead = {
    'id': 'wqy78hlz2T',
    'type': 'Lead',
    'customFields': {},
    'globalOptedOut': False,
    'groupIds': ['cMCH0hxwGt'],
    'firstName': 'Bob',
    'lastName': 'Burchard',
    'organizationId': 'LePEoKzD3Z',
    'phoneNumber': '+14435705356',
    'tagIds': [],
    'createdAt': '2019-09-17T21:25:51.442Z'
}

tags = {
    'items': [{
        'id': 'zEx5rjbg5',
        'type': 'Tag',
        'name': '2018_09_14_Hustle',
        'organizationId': 'LePEoKzD3',
        'createdAt': '2018-09-17T18:59:09.903Z'
    }, {
        'id': 'lfGhS5weS',
        'type': 'Tag',
        'name': '2018_09_19_Hustle',
        'organizationId': 'LePEoKzD3',
        'createdAt': '2018-09-18T20:53:16.096Z'
    }, {
        'id': 'a8DV7DC5E',
        'type': 'Tag',
        'name': '2018_09_21_Hustle',
        'organizationId': 'LePEoKzD3',
        'createdAt': '2018-09-25T16:28:32.868Z'
    }, {
        'id': '6bHjStnDD',
        'type': 'Tag',
        'name': 'wrong_number',
        'organizationId': 'LePEoKzD3',
        'createdAt': '2018-03-01T17:08:44.296Z'
    }],
    'pagination': {
        'cursor': 'WzEsMTAwMF0',
        'hasNextPage': False,
        'total': 4
    }
}

tag = {
  'id': 'zEx5rjbg',
  'type': 'Tag',
  'name': '2018_09_14_Hustle',
  'organizationId': 'LePEoKzD3',
  'createdAt': '2018-09-17T18:59:09.903Z'
}

agents = {
  'items': [{
    'id': 'CrJUBI1CF',
    'type': 'Agent',
    'name': 'Bob',
    'fullName': 'Bob Smith',
    'phoneNumber': '+12032498764',
    'organizationId': 'LePEoKzD3',
    'groupId': 'Qqp6o90Si',
    'createdAt': '2018-08-02T14:50:48.519Z'
  }, {
    'id': 'vnBImjcoen',
    'type': 'Agent',
    'name': 'Angela',
    'fullName': 'Jones',
    'phoneNumber': '+14156529028',
    'organizationId': 'LePEoKzD3',
    'groupId': 'Qqp6o90Si',
    'createdAt': '2018-08-02T14:50:54.254Z'
  }],
  'pagination': {
    'cursor': 'WzEsMTAwMF0',
    'hasNextPage': False,
    'total': 2
  }
}

agent = {
  'id': 'CrJUBI1CF',
  'type': 'Agent',
  'name': 'Angela',
  'fullName': 'Angela Jones',
  'phoneNumber': '+12032498764',
  'organizationId': 'LePEoKzD3',
  'groupId': 'Qqp6o90Si',
  'createdAt': '2018-08-02T14:50:48.519Z'
}
