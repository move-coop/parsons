get_campaign_json_response = {
    "contact": {
        "id": [{"value": 12345678}],
        "uuid": [{"value": "test-uuid"}],
        "revision_id": [{"value": 123456}],
        "org_id": [{"value": 1234}],
        "honorific": ["test"],
        "first_name": [{"value": "TestFirstName"}],
        "last_name": [{"value": "TestLastName"}],
        "name_suffix": ["TestSuffix"],
        "email": [{"value": "test_abc@test.com"}],
        "mobile_phone": [],
        "alternate_phone": [],
        "twitter_handle": [],
        "street_address": [],
        "city": [],
        "region": [],
        "country": [],
        "postal_code": [{"value": "test_postal_code"}],
        "latitude": [],
        "longitude": [],
        "opt_in": [{"value": True}],
        "nm_product_opt_in": [{"value": False}],
        "nm_marketing_opt_in": [{"value": False}],
        "groups": [
            {
                "target_id": 1234,
                "target_type": "contact_group",
                "target_uuid": "test-uuid",
                "url": "/contact-group/1234",
            }
        ],
        "created": [{"value": "0123456789", "format": "Y-m-d\\TH:i:sP"}],
        "changed": [{"value": "0123456789", "format": "Y-m-d\\TH:i:sP"}],
        "prefill_hash": [{"value": "test-value"}],
        "subscriber": [],
        "sync_status": [[]],
        "entitygroupfield": [
            {
                "target_id": 1234567,
                "target_type": "group_target",
                "target_uuid": "test-value",
                "url": "/group/1234/content/1234567",
            }
        ],
    },
    "links": {
        "Facebook": {
            "label": "Share on Facebook",
            "url": "https://www.facebook.com/sharer.php?s=100&u=https://win.newmode.net/test",
            "title": "",
        },
        "Twitter": {
            "label": "Tweet to your followers",
            "url": "https://nwmd.social/s/twitter/test",
            "title": "",
        },
        "Email": {
            "label": "Send an email",
            "url": "https://nwmd.social/s/email/test",
            "title": "Add your voice to this campaign!",
        },
        "Copy Link": {
            "label": "Copy Link",
            "url": "https://nwmd.social/s/copylink/test",
            "title": "",
        },
    },
    "message": "Already submitted",
    "submission": {
        "sid": [{"value": 123456}],
        "uuid": [{"value": "test-value"}],
        "revision_id": [{"value": 123456}],
        "action_id": [
            {
                "target_id": 1234,
                "target_type": "node",
                "target_uuid": "test-value",
                "url": "/node/1234",
            }
        ],
        "contact_id": [
            {
                "target_id": 1234567,
                "target_type": "contact",
                "target_uuid": "test-value",
                "url": "/contact/1234567",
            }
        ],
        "status": [
            {
                "target_id": 12,
                "target_type": "test-value",
                "target_uuid": "test-value",
                "url": "/taxonomy/term/12",
            }
        ],
        "testmode": [{"value": False}],
        "edited": [{"value": True}],
        "device": [],
        "browser": [],
        "browser_version": [],
        "os": [],
        "os_version": [],
        "parent_url": [],
        "source_code": [],
        "search_value": [],
        "created": [{"value": "0123456789", "format": "Y-m-d\\TH:i:sP"}],
        "changed": [{"value": "0123456789", "format": "Y-m-d\\TH:i:sP"}],
        "entitygroupfield": [
            {
                "target_id": 12345678,
                "target_type": "group_content",
                "target_uuid": "test-value",
                "url": "test-url",
            }
        ],
    },
    "ref_id": "test-value",
}
get_campaign_ids_json_response = {
    "jsonapi": {
        "version": "1.0",
        "meta": {"links": {"self": {"href": "http://jsonapi.org/format/1.0/"}}},
    },
    "data": {
        "type": "node--action",
        "id": "testCampaingID",
        "links": {
            "self": {
                "href": "https://base.newmode.net/jsonapi/node/action/testCampaingID?resourceVersion=id%test"
            }
        },
        "attributes": {},
        "relationships": {},
    },
}
get_recipient_json_response = {
    "subject": "test subject",
    "message": "<p>Dear [send:full_name],<br>I know that you care about this example as much as I do.</p>\n<p>[contact:full_name]<br>[contact:email], [contact:full_address]</p>, subscriber_text_lb",
    "id": "b3fc-xxxxxxxxxxxxxxxxxxxxxx-99a8",
    "first_name": "Darcy",
    "last_name": "Doogoode",
    "full_name": "Darcy Doogoode",
    "position": "MP",
    "party": "Liberal",
    "jurisdiction": "Vancouver East",
    "rendered": "Darcy Doogoode (MP), Vancouver East, Liberal",
}

run_submit_json_response = {
    "contact": {
        "id": [{"value": 1883}],
        "uuid": [{"value": "2efe-xxxxxxxxxxxxxxxxxxxxxx-2044"}],
        "revision_id": [{"value": 1954}],
        "org_id": [{"value": 1}],
        "honorific": [],
        "first_name": [{"value": "Sammy"}],
        "last_name": [{"value": "Supporter"}],
        "name_suffix": [],
        "email": [{"value": "test_abc@test.com"}],
        "mobile_phone": [],
        "alternate_phone": [],
        "twitter_handle": [],
        "street_address": [{"value": "312 Main Street"}],
        "city": [{"value": "Vancouver"}],
        "region": [{"value": "BC"}],
        "country": [{"value": "CA"}],
        "postal_code": [{"value": "V6A 2T2"}],
        "latitude": [{"value": 49.282039}],
        "longitude": [{"value": -123.099221}],
        "opt_in": [{"value": True}],
        "nm_product_opt_in": [{"value": True}],
        "nm_marketing_opt_in": [{"value": True}],
        "groups": [
            {
                "target_id": 58,
                "target_type": "contact_group",
                "target_uuid": "f426-xxxxxxxxxxxxxxxxxxxxxx-6712",
                "url": "/contact-group/58",
            }
        ],
        "created": [{"value": "1730818224", "format": "Y-m-d\\TH:i:sP"}],
        "changed": [{"value": "1730818779", "format": "Y-m-d\\TH:i:sP"}],
        "prefill_hash": [
            {
                "value": "706a1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxe501"
            }
        ],
        "subscriber": [],
        "sync_status": [[]],
        "entitygroupfield": [
            {
                "target_id": 5648,
                "target_type": "group_content",
                "target_uuid": "68be-xxxxxxxxxxxxxxxxxxxxxx-095c",
                "url": "/group/1/content/5648",
            }
        ],
    },
    "submission": {
        "sid": [{"value": 692}],
        "uuid": [{"value": "364a-xxxxxxxxxxxxxxxxxxxxxx-d545"}],
        "revision_id": [{"value": 692}],
        "action_id": [
            {
                "target_id": 197,
                "target_type": "node",
                "target_uuid": "54f7-xxxxxxxxxxxxxxxxxxxxxx-b11f",
                "url": "/node/197",
            }
        ],
        "contact_id": [
            {
                "target_id": 1883,
                "target_type": "contact",
                "target_uuid": "2efe-xxxxxxxxxxxxxxxxxxxxxx-2044",
                "url": "/contact/1883",
            }
        ],
        "status": [
            {
                "target_id": 78,
                "target_type": "taxonomy_term",
                "target_uuid": "1sb6-xxxxxxxxxxxxxxxxxxxxxx-ba19",
                "url": "/taxonomy/term/78",
            }
        ],
        "testmode": [{"value": False}],
        "edited": [{"value": False}],
        "device": [{"value": "PC"}],
        "browser": [{"value": "Firefox"}],
        "browser_version": [{"value": "132.0"}],
        "os": [{"value": "GNU/Linux"}],
        "os_version": [],
        "parent_url": [{"value": "https://www.mysite.com/mycampaign"}],
        "source_code": [{"value": "facebook"}],
        "search_value": [],
        "created": [{"value": "1730818779", "format": "Y-m-d\\TH:i:sP"}],
        "changed": [{"value": "1730818779", "format": "Y-m-d\\TH:i:sP"}],
        "entitygroupfield": [
            {
                "target_id": 5652,
                "target_type": "group_content",
                "target_uuid": "2119-xxxxxxxxxxxxxxxxxxxxxx-ce92",
                "url": "/group/1/content/5xx2",
            }
        ],
    },
    "links": {
        "Facebook": {
            "label": "Share on Facebook",
            "url": "https://www.facebook.com/sharer.php?s=100&u=https://www.mysite.com/mycampaign",
            "title": "",
        },
        "Twitter": {
            "label": "Tweet to your followers",
            "url": "http://base.test:8020/s/twitter/9VI1xxxxxxxxxg=/b",
            "title": "",
        },
        "Email": {
            "label": "Send an email",
            "url": "http://base.test:8020/s/email/9VI1xxxxxxxxxg=/b",
            "title": "Add your voice to this campaign!",
        },
        "Copy Link": {
            "label": "Copy Link",
            "url": "http://base.test:8020/s/copylink/9VI1MbcwMCg=/b",
            "title": "",
        },
    },
    "queue_id": "3xx6",
    "ref_id": "706axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxe501",
}
