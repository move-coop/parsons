import json

GET_ORGANIZATIONS_JSON = {
    "count": 38,
    "next": None,
    "previous": ("https://events.mobilizeamerica.io/api/v1/organizations?updated_since=1543644000"),
    "data": [
        {
            "id": 1251,
            "name": "Mike Blake for New York City",
            "slug": "mikefornyc",
            "is_coordinated": "True",
            "is_independent": "True",
            "is_primary_campaign": "False",
            "state": "",
            "district": "",
            "candidate_name": "",
            "race_type": "OTHER_LOCAL",
            "event_feed_url": "https://events.mobilizeamerica.io/mikefornyc/",
            "created_date": 1545885434,
            "modified_date": 1546132256,
        }
    ],
}

GET_EVENTS_JSON = {
    "count": 1,
    "next": None,
    "previous": None,
    "data": [
        {
            "id": 86738,
            "description": (
                "Join our team of volunteers and learn how to engage students in local "
                "high schools, communicate our mission, and register young voters."
            ),
            "timezone": "America/Chicago",
            "title": "Student Voter Initiative Training",
            "summary": "",
            "featured_image_url": (
                "https://mobilizeamerica.imgix.net/uploads/event/"
                "40667432145_6188839fe3_o_20190102224312253645.jpeg"
            ),
            "sponsor": {
                "id": 1076,
                "name": "Battleground Texas",
                "slug": "battlegroundtexas",
                "is_coordinated": True,
                "is_independent": False,
                "is_primary_campaign": False,
                "state": "",
                "district": "",
                "candidate_name": "",
                "race_type": None,
                "event_feed_url": "https://events.mobilizeamerica.io/battlegroundtexas/",
                "created_date": 1538590930,
                "modified_date": 1546468308,
            },
            "timeslots": [{"id": 526226, "start_date": 1547330400, "end_date": 1547335800}],
            "location": {
                "venue": "Harris County Democratic Party HQ",
                "address_lines": ["4619 Lyons Ave", ""],
                "locality": "Houston",
                "region": "TX",
                "postal_code": "77020",
                "location": {"latitude": 29.776446, "longitude": -95.323037},
                "congressional_district": "18",
                "state_leg_district": "142",
                "state_senate_district": None,
            },
            "event_type": "TRAINING",
            "created_date": 1546469706,
            "modified_date": 1547335800,
            "browser_url": ("https://events.mobilizeamerica.io/battlegroundtexas/event/86738/"),
            "high_priority": None,
            "contact": None,
            "visibility": "PUBLIC",
        }
    ],
}

GET_EVENTS_ORGANIZATION_JSON = json.loads(
    """
    {
        "count": 2,
        "next": null,
        "previous": null,
        "data": [
            {
            "approval_status": "APPROVED",
            "address_visibility": "PUBLIC",
            "location": {
                "venue": "Test",
                "address_lines": [
                "123 Test Road",
                ""
                ],
                "locality": "York",
                "region": "PA",
                "country": "US",
                "postal_code": "17404",
                "location": {
                "latitude": 40.0588876,
                "longitude": -76.7835604
                },
                "congressional_district": null,
                "state_leg_district": null,
                "state_senate_district": null
            },
            "timeslots": [
                {
                "id": 1,
                "start_date": 2,
                "end_date": 3,
                "instructions": ""
                },
                {
                "id": 2,
                "start_date": 3,
                "end_date": 4,
                "instructions": "Some detailed instructions for the second timeslot"
                }
            ],
            "title": "Test Event",
            "accessibility_status": null,
            "created_date": 1532629574,
            "created_by_volunteer_host": false,
            "instructions": "",
            "virtual_action_url": null,
            "summary": "",
            "sponsor": {
                "id": 1,
                "is_primary_campaign": false,
                "name": "Test Org",
                "is_independent": true,
                "candidate_name": "",
                "org_type": "OTHER",
                "created_date": 1513974036,
                "event_feed_url": "https://www.mobilize.us/test_org/",
                "state": "",
                "race_type": null,
                "logo_url": "https://mobilize-uploads-prod.s3.amazonaws.com/branding/test_logo.png",
                "is_coordinated": false,
                "district": "",
                "slug": "testorg",
                "modified_date": 1655222024
            },
            "featured_image_url": "",
            "contact": {
                "name": "Test",
                "email_address": "tester@test.org",
                "phone_number": "",
                "owner_user_id": 1234
            },
            "timezone": "America/New_York",
            "id": 7659,
            "description": "Test",
            "event_campaign": null,
            "high_priority": false,
            "accessibility_notes": null,
            "event_type": "PHONE_BANK",
            "browser_url": "https://www.mobilize.us/test_org/event/1/",
            "visibility": "PUBLIC",
            "is_virtual": false,
            "modified_date": 1601663981,
            "tags": []
            },
            {
            "approval_status": "APPROVED",
            "address_visibility": "PRIVATE",
            "location": {
                "locality": "Schenectady",
                "region": "NY",
                "country": "US",
                "postal_code": "12309",
                "congressional_district": "20",
                "state_leg_district": "110",
                "state_senate_district": "49",
                "address_lines": [
                "This event address is private. Sign up for more details",
                ""
                ],
                "venue": "This event address is private. Sign up for more details"
            },
            "timeslots": [
                {
                "id": 1,
                "start_date": 2,
                "end_date": 3,
                "instructions": ""
                },
                {
                "id": 2,
                "start_date": 3,
                "end_date": 4,
                "instructions": "Some detailed instructions for the second timeslot"
                }
            ],
            "title": "Test Phonebank",
            "accessibility_status": null,
            "created_date": 1537289907,
            "created_by_volunteer_host": false,
            "instructions": null,
            "virtual_action_url": null,
            "summary": "Help Us Call Testers!",
            "sponsor": {
                "id": 321,
                "is_primary_campaign": false,
                "name": "Test Org Two",
                "is_independent": false,
                "candidate_name": "",
                "org_type": "TEST_ORG",
                "created_date": 1537214527,
                "event_feed_url": "https://www.mobilize.us/test_org_two/",
                "state": "NY",
                "race_type": null,
                "logo_url": "https://amazonaws.com/test_org_two.jpg",
                "is_coordinated": true,
                "district": "",
                "slug": "testorgtwo",
                "modified_date": 1654183362
            },
            "featured_image_url": "https://mobilizeamerica.imgix.net/uploads/test.jpg",
            "contact": null,
            "timezone": "America/New_York",
            "id": 421,
            "description": "Join us to call people and do an automated test!",
            "event_campaign": null,
            "high_priority": false,
            "accessibility_notes": null,
            "event_type": "PHONE_BANK",
            "browser_url": "https://www.mobilize.us/test_org_two/event/2/",
            "visibility": "PUBLIC",
            "is_virtual": false,
            "modified_date": 1601665649,
            "tags": []
            }
        ],
        "metadata": {
            "url_name": "public_organization_events",
            "build_commit": "abcd",
            "page_title": null
        }
    }"""
)

GET_EVENTS_DELETED_JSON = {
    "count": 2,
    "next": None,
    "previous": None,
    "data": [
        {"id": 86765, "deleted_date": 1546705971},
        {"id": 86782, "deleted_date": 1546912779},
    ],
}
