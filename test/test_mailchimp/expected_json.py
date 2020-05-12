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
			"permission_reminder": "You are receiving this email because you signed up at an event, while being canvassed, or on our website.",
			"use_archive_bar": true,
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
			"permission_reminder": "You are receiving this email because you signed up at an event, while being canvassed, or on our website.",
			"use_archive_bar": true,
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

test_members = {}

test_unsubscribes = {}