get_campaign_json_response = {
    "langcode": "test",
    "title": "test",
    "field_call_introduction": "Hello [contact:first_name], thank you for participating in the [node:title] campaign.",
    "field_call_voice": "english-us",
    "field_communication_types": ["petition"],
    "field_country": ["US"],
    "field_datasets": [],
    "field_email_from_supporter": False,
    "field_email_replyto_supporter": True,
    "field_embedded": False,
    "field_embed_url": None,
    "field_lookup_type": "none",
    "field_message_editable": True,
    "field_moderation": "off",
    "field_org_id": "test-value",
    "field_paused": False,
    "field_randomize_targets": False,
    "field_selected_targets": [],
    "field_show_target_jurisdiction": False,
    "field_show_target_name": False,
    "field_show_target_party": False,
    "field_show_target_position": False,
    "field_symbolic_recipient": None,
    "field_target_limit": 10,
    "field_test_phone_number": None,
    "field_thankyou_email_body": {
        "value": "[contact:first_name], thank you for adding your voice in our teset campaign.\r\n\r\n\r\nLet’s amplify your voice. Can you take the next step by sharing this action with your friends and family now?\r\n[submission:share_links]\r\n\r\nThe more people that join this campaign, the stronger our impact will be.\r\n\r\n\r\nMore soon,\r\nYour Test Org team",
        "processed": "<p>[contact:first_name], thank you for adding your voice in our teset campaign.</p>\n<p>Let’s amplify your voice. Can you take the next step by sharing this action with your friends and family now?<br />\n[submission:share_links]</p>\n<p>The more people that join this campaign, the stronger our impact will be.</p>\n<p>More soon,<br />\nYour Test Org team</p>\n",
    },
    "field_thankyou_email_disable": False,
    "field_thankyou_email_subject": "Here's your next step [contact:first_name]",
    "field_thankyou_from_name": "test",
    "field_thankyou_redirect": None,
    "field_thankyou_type": "nm",
    "draft": False,
    "archived": False,
    "message": [],
    "buttons": {
        "Facebook": {"label": "Share on Facebook", "url": "", "title": None},
        "Twitter": {"label": "Tweet to your followers", "url": "", "title": None},
        "Email": {"label": "Send an email", "url": "", "title": "Add your voice to this campaign!"},
        "Copy Link": {"label": "Copy Link", "url": "", "title": None},
    },
    "description": "<div>We demand that [What your decision makers should do]</div>",
    "primary_image": "https://nwmd.social/sites/default/files/defaultSocialImg/Headersection_2.jpg",
    "form": {
        "header": {
            "name": "header",
            "type": "header",
            "builder": {"type": "header", "label": "Header", "remove": False},
        },
        "container2": {
            "name": "container2",
            "type": "group",
            "addClass": "two-column-layout",
            "schema": {
                "column1": {
                    "name": "column1",
                    "type": "group",
                    "addClass": "content-column",
                    "columns": {"container": 8},
                    "schema": {
                        "image": {
                            "name": "image",
                            "type": "image",
                            "builder": {"name": "image", "type": "image", "remove": True},
                        },
                        "recipient": {
                            "name": "recipient",
                            "type": "recipient",
                            "builder": {"type": "recipient", "label": "recipient", "remove": False},
                        },
                        "description": {
                            "name": "description",
                            "type": "description",
                            "builder": {
                                "type": "description",
                                "label": "Paragraph",
                                "remove": False,
                            },
                        },
                    },
                },
                "column2": {
                    "name": "column2",
                    "type": "group",
                    "addClass": "form-column",
                    "columns": {"container": 4},
                    "schema": {
                        "goalmeter": {
                            "name": "goalmeter",
                            "type": "goal-meter",
                            "builder": {"type": "goalmeter"},
                        },
                        "first_name": {
                            "name": "first_name",
                            "placeholder": "First name",
                            "type": "text",
                            "rules": ["required"],
                            "builder": {"type": "first_name", "remove": False},
                        },
                        "last_name": {
                            "name": "last_name",
                            "placeholder": "Last name",
                            "type": "text",
                            "rules": ["required"],
                            "builder": {"type": "last_name", "remove": False},
                        },
                        "email": {
                            "name": "email",
                            "placeholder": "Email address",
                            "type": "text",
                            "inputType": "email",
                            "rules": ["nullable", "email"],
                            "builder": {"type": "email", "remove": False},
                        },
                        "lookup": {
                            "name": "lookup",
                            "placeholder": "Address",
                            "type": "lookup",
                            "builder": {"type": "lookup", "remove": False},
                        },
                        "opt-in": {
                            "name": "opt-in",
                            "type": "opt-in",
                            "label": None,
                            "builder": {"type": "optin", "remove": False},
                            "optintype": "statement",
                            "optintext": "Yes please.",
                            "optouttext": "No thankyou.",
                            "optinprivacy": "Test Org will protect your privacy.",
                        },
                        "submit": {
                            "name": "submit",
                            "type": "button",
                            "buttonLabel": "Sign this petition now",
                            "submits": True,
                            "builder": {"type": "submit", "remove": False},
                        },
                        "disclaimer": {
                            "name": "disclaimer",
                            "type": "disclaimer",
                            "builder": {
                                "type": "disclaimer",
                                "label": "New/Mode Opt In",
                                "remove": False,
                            },
                        },
                    },
                },
            },
            "builder": {"type": "container2", "label": "2 columns"},
        },
    },
    "thank_you": {
        "header": {
            "name": "header",
            "type": "header",
            "builder": {"type": "header", "label": "Header"},
        },
        "share_buttons": {
            "name": "sharebuttons",
            "type": "share-buttons",
            "builder": {"type": "sharebuttons", "remove": False},
        },
    },
    "talking_points": {
        "header": {
            "name": "header",
            "type": "header",
            "builder": {"type": "header", "label": "Header"},
        },
        "info": {
            "name": "info",
            "type": "static",
            "tag": "p",
            "content": "You will receive a call shortly connecting you with {count} recipients",
            "builder": {"type": "p", "label": "Paragraph"},
        },
        "talking_points": {
            "name": "talking_points",
            "type": "static",
            "tag": "p",
            "content": '<div class="css-h05o44">\n<div class="ak-renderer-document">\n<p',
            "builder": {"type": "p", "label": "Paragraph"},
        },
    },
    "org_country": "US",
    "field_opt_in_type": "statement",
    "field_opt_in_text": {"processed": "Yes please."},
    "field_opt_out_text": {"processed": "No thankyou."},
    "field_privacy_statement": {
        "processed": "Test Org hosts this campaign and will keep you informed about it and others. Test Org will protect your privacy.",
        "unwrapped": "Test Org will protect your privacy.",
        "wrapper": "Test Org hosts this campaign and will keep you informed about it and others. [privacy_policy_placeholder]",
    },
    "disclaimer": "",
    "field_goal_current": 3,
    "field_goal_goal": 25,
    "field_activity_actions": None,
    "field_activity_data": None,
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
