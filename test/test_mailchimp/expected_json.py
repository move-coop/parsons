test_campaigns = {
    "campaigns": [
        {
            "id": "abc",
            "web_id": 123,
            "type": "regular",
            "create_time": "2019-10-18T02:35:05+00:00",
            "archive_url": "http://example.com/sample-campaign-1",
            "long_archive_url": "https://mailchi.mp/abc/sample-campaign-1",
            "status": "sent",
            "emails_sent": 145,
            "send_time": "2019-10-18T14:15:00+00:00",
            "content_type": "template",
            "needs_block_refresh": False,
            "resendable": True,
            "recipients": {
                "list_id": "zyx",
                "list_is_active": True,
                "list_name": "Support Our Candidate List 1",
                "segment_text": "",
                "recipient_count": 145
            },
            "settings": {
                "subject_line": "Sample Campaign 1",
                "preview_text": "This is a sample campaign.",
                "title": "Sample Campaign Donation Ask",
                "from_name": "Our Candidate",
                "reply_to": "our_candidate@example.com",
                "use_conversation": False,
                "to_name": "*|FNAME|* *|LNAME|*",
                "folder_id": "",
                "authenticate": True,
                "auto_footer": False,
                "inline_css": False,
                "auto_tweet": False,
                "fb_comments": True,
                "timewarp": False,
                "template_id": 12345,
                "drag_and_drop": True
            },
            "tracking": {
                "opens": True,
                "html_clicks": True,
                "text_clicks": False,
                "goal_tracking": False,
                "ecomm360": False,
                "google_analytics": "",
                "clicktale": ""
            },
            "report_summary": {
                "opens": 48,
                "unique_opens": 34,
                "open_rate": 0.23776223776223776,
                "clicks": 1,
                "subscriber_clicks": 1,
                "click_rate": 0.006993006993006993,
                "ecommerce": {
                    "total_orders": 0,
                    "total_spent": 0,
                    "total_revenue": 0
                }
            },
            "delivery_status": {
                "enabled": False
            },
            "_links": []
        },
        {
            "id": "def",
            "web_id": 456,
            "type": "regular",
            "create_time": "2019-05-29T11:46:41+00:00",
            "archive_url": "http://example.com/sample-campaign-2",
            "long_archive_url": "https://mailchi.mp/abc/sample-campaign-2",
            "status": "sent",
            "emails_sent": 87,
            "send_time": "2019-05-29T21:18:15+00:00",
            "content_type": "template",
            "needs_block_refresh": False,
            "resendable": True,
            "recipients": {
                "list_id": "wvu",
                "list_is_active": True,
                "list_name": "Support Our Candidate List 2",
                "segment_text": "",
                "recipient_count": 87
            },
            "settings": {
                "subject_line": "Sample Campaign 2",
                "preview_text": "This is another sample campaign.",
                "title": "Sample Campaign 2 Donation Ask",
                "from_name": "Our Candidate",
                "reply_to": "our_candidate@example.com",
                "use_conversation": False,
                "to_name": "*|FNAME|* *|LNAME|*",
                "folder_id": "",
                "authenticate": True,
                "auto_footer": False,
                "inline_css": False,
                "auto_tweet": False,
                "fb_comments": True,
                "timewarp": False,
                "template_id": 67890,
                "drag_and_drop": True
            },
            "tracking": {
                "opens": True,
                "html_clicks": True,
                "text_clicks": False,
                "goal_tracking": False,
                "ecomm360": False,
                "google_analytics": "",
                "clicktale": ""
            },
            "report_summary": {
                "opens": 108,
                "unique_opens": 48,
                "open_rate": 0.5647058823529412,
                "clicks": 25,
                "subscriber_clicks": 14,
                "click_rate": 0.16470588235294117,
                "ecommerce": {
                    "total_orders": 0,
                    "total_spent": 0,
                    "total_revenue": 0
                }
            },
            "delivery_status": {
                "enabled": False
            },
            "_links": []
        }]}

test_lists = {
    "lists": [
        {
            "id": "zyx",
            "web_id": 98765,
            "name": "Support Our Candidate List 1",
            "contact": {
                "company": "Support Our Candidate",
                "address1": "123 Main Street",
                "address2": "",
                "city": "Townsville",
                "state": "OH",
                "zip": "43358",
                "country": "US",
                "phone": ""
            },
            "permission_reminder": (
                "You are receiving this email because you signed up at an event, while being "
                "canvassed, or on our website."),
            "use_archive_bar": True,
            "campaign_defaults": {
                "from_name": "Our Candidate",
                "from_email": "our_candidate@example.com",
                "subject": "",
                "language": "en"
            },
            "notify_on_subscribe": "",
            "notify_on_unsubscribe": "",
            "date_created": "2019-03-25T22:55:44+00:00",
            "list_rating": 3,
            "email_type_option": False,
            "subscribe_url_short": "http://example.com/sample-subscribe_url_2",
            "subscribe_url_long": "https://mailchi.mp/zyx/sample-subscribe-url-2",
            "beamer_address": "us00-sample-2@inbound.mailchimp.com",
            "visibility": "pub",
            "double_optin": False,
            "has_welcome": True,
            "marketing_permissions": False,
            "modules": [],
            "stats": {
                "member_count": 140,
                "unsubscribe_count": 8,
                "cleaned_count": 16,
                "member_count_since_send": 0,
                "unsubscribe_count_since_send": 1,
                "cleaned_count_since_send": 0,
                "campaign_count": 21,
                "campaign_last_sent": "2020-01-06T01:54:32+00:00",
                "merge_field_count": 5,
                "avg_sub_rate": 0,
                "avg_unsub_rate": 1,
                "target_sub_rate": 3,
                "open_rate": 38.40236686390532,
                "click_rate": 4.016786570743405,
                "last_sub_date": "2019-09-24T01:07:56+00:00",
                "last_unsub_date": "2020-01-06T01:55:02+00:00"
            },
            "_links": []
        },
        {
            "id": "xvu",
            "web_id": 43210,
            "name": "Support Our Candidate List 2",
            "contact": {
                "company": "Support Our Candidate",
                "address1": "123 Main Street",
                "address2": "",
                "city": "Townsville",
                "state": "OH",
                "zip": "43358",
                "country": "US",
                "phone": ""
            },
            "permission_reminder": (
                "You are receiving this email because you signed up at an event, while being "
                "canvassed, or on our website."),
            "use_archive_bar": True,
            "campaign_defaults": {
                "from_name": "Our Candidate",
                "from_email": "our_candidate@example.com",
                "subject": "",
                "language": "en"
            },
            "notify_on_subscribe": "",
            "notify_on_unsubscribe": "",
            "date_created": "2018-09-15T22:15:21+00:00",
            "list_rating": 3,
            "email_type_option": False,
            "subscribe_url_short": "http://example.com/sample-subscribe_url_1",
            "subscribe_url_long": "https://mailchi.mp/zyx/sample-subscribe-url-1",
            "beamer_address": "us00-sample-1@inbound.mailchimp.com",
            "visibility": "pub",
            "double_optin": False,
            "has_welcome": True,
            "marketing_permissions": False,
            "modules": [],
            "stats": {
                "member_count": 73,
                "unsubscribe_count": 3,
                "cleaned_count": 7,
                "member_count_since_send": 1,
                "unsubscribe_count_since_send": 1,
                "cleaned_count_since_send": 0,
                "campaign_count": 13,
                "campaign_last_sent": "2020-01-03T14:38:11+00:00",
                "merge_field_count": 5,
                "avg_sub_rate": 0,
                "avg_unsub_rate": 1,
                "target_sub_rate": 3,
                "open_rate": 64.19236186394533,
                "click_rate": 3.746759370417411,
                "last_sub_date": "2020-01-01T00:19:46+00:00",
                "last_unsub_date": "2019-12-23T11:44:31+00:00"
            },
            "_links": []
        },
    ],
    "total_items": 1,
    "constraints": {
        "may_create": False,
        "max_instances": 1,
        "current_total_instances": 1
    },
    "_links": []
}

test_members = {
  "members": [
    {
      "id": "9eb69db8d0371811aa18803a1ae21584",
      "email_address": "member_1@example.com",
      "unique_email_id": "c82a25d939",
      "web_id": 24816326,
      "email_type": "html",
      "status": "subscribed",
      "merge_fields": {
        "FNAME": "Member",
        "LNAME": "One",
        "ADDRESS": {
          "addr1": "",
          "addr2": "",
          "city": "",
          "state": "",
          "zip": "",
          "country": "US"
        },
        "PHONE": "",
        "BIRTHDAY": ""
      },
      "stats": {
        "avg_open_rate": 0.3571,
        "avg_click_rate": 0
      },
      "ip_signup": "",
      "timestamp_signup": "",
      "ip_opt": "174.59.50.35",
      "timestamp_opt": "2019-03-25T22:55:44+00:00",
      "member_rating": 4,
      "last_changed": "2019-03-25T22:55:44+00:00",
      "language": "en",
      "vip": False,
      "email_client": "Gmail",
      "location": {
        "latitude": 40.0293,
        "longitude": -76.2656,
        "gmtoff": 0,
        "dstoff": 0,
        "country_code": "US",
        "timezone": "717/223"
      },
      "source": "Unknown",
      "tags_count": 0,
      "tags": [],
      "list_id": "67fdf4b1f4",
      "_links": []
    },
    {
      "id": "4f315641dbad7b74acc0f4a5d3741ac6",
      "email_address": "member_2@example.com",
      "unique_email_id": "8d308d69d3",
      "web_id": 12233445,
      "email_type": "html",
      "status": "subscribed",
      "merge_fields": {
        "FNAME": "Member",
        "LNAME": "Two",
        "ADDRESS": "",
        "PHONE": "",
        "BIRTHDAY": ""
      },
      "stats": {
        "avg_open_rate": 0.5,
        "avg_click_rate": 0
      },
      "ip_signup": "",
      "timestamp_signup": "",
      "ip_opt": "174.59.50.35",
      "timestamp_opt": "2019-03-25T23:04:46+00:00",
      "member_rating": 4,
      "last_changed": "2019-03-25T23:04:46+00:00",
      "language": "",
      "vip": False,
      "email_client": "iPhone",
      "location": {
        "latitude": 40.0459,
        "longitude": -76.3542,
        "gmtoff": 0,
        "dstoff": 0,
        "country_code": "US",
        "timezone": "717/223"
      },
      "source": "Import",
      "tags_count": 2,
      "tags": [
        {
          "id": 17493,
          "name": "canvass"
        },
        {
          "id": 17497,
          "name": "canvass-03-17-2019"
        }
      ],
      "list_id": "67fdf4b1f4",
      "_links": []
    }]}

test_unsubscribes = {
  "unsubscribes": [
    {
      "email_id": "e542e5cd7b414e5ff8409ff57cf154be",
      "email_address": "unsubscribe_1@exmaple.com",
      "merge_fields": {
        "FNAME": "Unsubscriber",
        "LNAME": "One",
        "ADDRESS": "",
        "PHONE": "5558754307",
        "BIRTHDAY": ""
      },
      "vip": False,
      "timestamp": "2019-12-09T21:18:06+00:00",
      "reason": "None given",
      "campaign_id": "abc",
      "list_id": "zyx",
      "list_is_active": True,
      "_links": []
    }
  ],
  "campaign_id": "abc",
  "total_items": 1,
  "_links": []
}
