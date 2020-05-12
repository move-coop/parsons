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
			"needs_block_refresh": false,
			"resendable": true,
			"recipients": {
				"list_id": "zyx",
				"list_is_active": true,
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
				"use_conversation": false,
				"to_name": "*|FNAME|* *|LNAME|*",
				"folder_id": "",
				"authenticate": true,
				"auto_footer": false,
				"inline_css": false,
				"auto_tweet": false,
				"fb_comments": true,
				"timewarp": false,
				"template_id": 12345,
				"drag_and_drop": true
			},
			"tracking": {
				"opens": true,
				"html_clicks": true,
				"text_clicks": false,
				"goal_tracking": false,
				"ecomm360": false,
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
				"enabled": false
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
			"needs_block_refresh": false,
			"resendable": true,
			"recipients": {
				"list_id": "wvu",
				"list_is_active": true,
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
				"use_conversation": false,
				"to_name": "*|FNAME|* *|LNAME|*",
				"folder_id": "",
				"authenticate": true,
				"auto_footer": false,
				"inline_css": false,
				"auto_tweet": false,
				"fb_comments": true,
				"timewarp": false,
				"template_id": 67890,
				"drag_and_drop": true
			},
			"tracking": {
				"opens": true,
				"html_clicks": true,
				"text_clicks": false,
				"goal_tracking": false,
				"ecomm360": false,
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
				"enabled": false
			},
			"_links": []
		}}

test_agent = [{
  'available': False,
  'occasional': True,
  'id': 47020956237,
  'signature': '<div dir="ltr"><p><br></p>\n</div>',
  'ticket_scope': 1,
  'created_at': '2020-01-17T15:07:01Z',
  'updated_at': '2020-02-05T00:58:37Z',
  'available_since': None,
  'type': 'support_agent',
  'contact': {
    'active': True,
    'email': 'person@email.org',
    'job_title': None,
    'language': 'en',
    'last_login_at': '2020-01-24T22:49:52Z',
    'mobile': None,
    'name': 'Alissa',
    'phone': None,
    'time_zone': 'Bogota',
    'created_at': '2020-01-17T15:07:00Z',
    'updated_at': '2020-01-24T22:49:52Z'
  }
}]

test_ticket = [{
  'cc_emails': ['person@email.org', 'person2@email.org'],
  'fwd_emails': [],
  'reply_cc_emails': ['person@email.org', 'person2@email.org'],
  'ticket_cc_emails': ['person@email.org', 'person2@email.org'],
  'fr_escalated': False,
  'spam': False,
  'email_config_id': None,
  'group_id': 47000643034,
  'priority': 1,
  'requester_id': 47021937449,
  'responder_id': 47017224681,
  'source': 3,
  'company_id': 47000491688,
  'status': 5,
  'subject': 'My thing is broken.',
  'association_type': None,
  'to_emails': None,
  'product_id': None,
  'id': 84,
  'type': 'Support Request 1',
  'due_by': '2020-02-19T22:00:00Z',
  'fr_due_by': '2020-02-06T17:00:00Z',
  'is_escalated': False,
  'custom_fields': {},
  'created_at': '2020-02-05T22:17:41Z',
  'updated_at': '2020-02-06T02:07:37Z',
  'associated_tickets_count': None,
  'tags': []
}]

test_company = [{
  'id': 47000491701,
  'name': 'Big Org',
  'description': None,
  'note': None,
  'domains': [],
  'created_at': '2020-01-09T20:43:09Z',
  'updated_at': '2020-01-09T20:43:09Z',
  'custom_fields': {},
  'health_score': None,
  'account_tier': 'Tier 2',
  'renewal_date': '2020-12-31T00:00:00Z',
  'industry': None
}]

test_contact = [{
  'active': False,
  'address': None,
  'company_id': 47000491686,
  'description': None,
  'email': 'person@email.org',
  'id': 47021299020,
  'job_title': None,
  'language': 'en',
  'mobile': None,
  'name': 'Percy Person',
  'phone': 'N/A',
  'time_zone': 'Bogota',
  'twitter_id': None,
  'custom_fields': {},
  'facebook_id': None,
  'created_at': '2020-01-27T16:44:34Z',
  'updated_at': '2020-01-27T16:44:34Z',
  'unique_external_id': None
}]

