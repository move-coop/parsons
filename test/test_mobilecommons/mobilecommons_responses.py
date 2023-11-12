class get_profiles_response:
    status_code = 200
    text = """<?xml version="1.0" encoding="UTF-8"?>
<response success="true">
  <profiles num="1" page="1">
    <profile id="12345">
      <first_name>James</first_name>
      <last_name>Holden</last_name>
      <phone_number>13073997994</phone_number>
      <email>james.holden.boo@gmail.com</email>
      <status>Undeliverable</status>
      <created_at>2022-06-29 17:28:24 UTC</created_at>
      <updated_at>2023-03-14 21:46:58 UTC</updated_at>
      <opted_out_at>2022-09-16 01:07:50 UTC</opted_out_at>
      <opted_out_source>Opt-out from API</opted_out_source>
      <source type="Keyword" name="JOIN" id="12345" opt_in_path_id="12345" message_id="12345667"/>
      <address>
        <street1>2430 Douglas Dr</street1>
        <street2/>
        <city>Salt Lake City</city>
        <state>UT</state>
        <postal_code/>
        <country>US</country>
      </address>
      <last_saved_location>
        <latitude>41.692249</latitude>
        <longitude>-112.854408</longitude>
        <precision>rooftop</precision>
        <city>Salt Lake City</city>
        <state>UT</state>
        <postal_code>84106</postal_code>
        <country>US</country>
      </last_saved_location>
      <last_saved_districts>
        <congressional_district>UT-2</congressional_district>
        <state_upper_district>UT-13</state_upper_district>
        <state_lower_district>UT-32</state_lower_district>
        <split_district>No</split_district>
      </last_saved_districts>
      <custom_columns>
        <custom_column name="BestDecade"/>
        <custom_column name="Birthday"/>
        <custom_column name="Caregiver"/>
        <custom_column name="Contact Frequency"/>
        <custom_column
            name="f_name"
            created_at="2022-07-01T15:19:18Z"
            updated_at="2022-07-01T15:19:18Z">
            Cormac
        </custom_column>
        <custom_column name="Interest"/>
        <custom_column
            name="l_name"
            created_at="2022-07-01T15:19:30Z"
            updated_at="2022-07-01T15:19:30Z">
            Martinez del Rio
        </custom_column>
        <custom_column name="MoneyConcerns"/>
        <custom_column name="PantryType"/>
        <custom_column name="Parent"/>
        <custom_column name="PersonalFlex"/>
      </custom_columns>
      <subscriptions>
        <subscription
            campaign_id="22345"
            campaign_name="Test Campaign"
            campaign_description="This is just a test babe"
            opt_in_path_id="22233"
            status="Opted-Out"
            opt_in_source="JOIN"
            created_at="2022-06-29T17:28:24Z"
            activated_at="2022-06-29T17:28:24Z"
            opted_out_at="2022-07-01T15:18:59Z"
            opt_out_source="Texted a STOP word"/>
      </subscriptions>
      <integrations>
      </integrations>
      <clicks>
      </clicks>
    </profile>
  </profiles>
</response>
"""


class get_broadcasts_response:
    status_code = 200
    text = """<?xml version="1.0" encoding="UTF-8"?>
<response success="true">
  <broadcasts page="1" limit="23" page_count="2">
<broadcast id="2543129" status="generated">
  <name>Test Round 2</name>
  <body>Test :)  http://lil.ms/m9c2</body>
  <campaign id="233056" active="true">
    <name>TEST DH DD</name>
  </campaign>
  <delivery_time>2023-06-23 18:45:00 UTC</delivery_time>
  <include_subscribers>true</include_subscribers>
  <throttled>false</throttled>
  <localtime>false</localtime>
  <automated>false</automated>
  <estimated_recipients_count>2</estimated_recipients_count>
  <replies_count>2</replies_count>
  <opt_outs_count>0</opt_outs_count>
  <included_groups>
  </included_groups>
  <excluded_groups>
  </excluded_groups>
  <tags>
    <tag>808sandheartbreaks@gmail.com</tag>
  </tags>
</broadcast>
<broadcast id="2541464" status="generated">
  <name>Test 6/6 DD DH </name>
  <body>Hey {{first_name}}!! On a scale of 1-5, how is your day going?
Reply STOP to quit. Msg&amp;DataRatesMayApply</body>
  <campaign id="233056" active="true">
    <name>TEST DH DD</name>
  </campaign>
  <delivery_time>2023-06-06 20:08:56 UTC</delivery_time>
  <include_subscribers>true</include_subscribers>
  <throttled>false</throttled>
  <localtime>false</localtime>
  <automated>false</automated>
  <estimated_recipients_count>2</estimated_recipients_count>
  <replies_count>2</replies_count>
  <opt_outs_count>0</opt_outs_count>
  <included_groups>
  </included_groups>
  <excluded_groups>
  </excluded_groups>
  <tags>
    <tag>how.to.eat.water.with.a.fork@gmail.com</tag>
  </tags>
</broadcast>
<broadcast id="2536296" status="draft">
  <name>Broadcast 04/10/2023 01:34PM test</name>
  <body>hi name, what's your email? Recurring Msgs. Reply STOP to quit, HELP for info.
    Msg&amp;DataRatesMayApply</body>
  <campaign id="228634" active="true">
    <name>Dog King 2024</name>
  </campaign>
  <delivery_time/>
  <include_subscribers>false</include_subscribers>
  <throttled>false</throttled>
  <localtime>false</localtime>
  <automated>false</automated>
  <estimated_recipients_count/>
  <replies_count>0</replies_count>
  <opt_outs_count>0</opt_outs_count>
  <included_groups>
    <group name="testing" id="889110" type="UploadedGroup">
    </group>
  </included_groups>
  <excluded_groups>
  </excluded_groups>
  <tags>
  </tags>
</broadcast>
</broadcasts>
</response>
"""


class post_profile_response:
    status_code = 200
    text = """<?xml version="1.0" encoding="UTF-8"?>
<response success="true">
  <profile id="602169563">
    <first_name>Hardcoremac</first_name>
    <last_name>Del Sangre</last_name>
    <phone_number>13073997990</phone_number>
    <email>hardcore.smack@gmail.com</email>
    <status>Undeliverable</status>
    <created_at>2022-06-29 17:28:24 UTC</created_at>
    <updated_at>2023-03-14 21:46:58 UTC</updated_at>
    <opted_out_at>2022-09-16 01:07:50 UTC</opted_out_at>
    <opted_out_source>Opt-out from API</opted_out_source>
    <source
        type="Keyword"
        name="JOIN" id="8657035"
        opt_in_path_id="328887"
        message_id="1776761263"
    />
    <address>
      <street1>2430 Douglas Dr</street1>
      <street2/>
      <city>Salt Lake City</city>
      <state>UT</state>
      <postal_code/>
      <country>US</country>
    </address>
    <last_saved_location>
      <latitude>41.692249</latitude>
      <longitude>-112.854408</longitude>
      <precision>rooftop</precision>
      <city>Salt Lake City</city>
      <state>UT</state>
      <postal_code>84106</postal_code>
      <country>US</country>
    </last_saved_location>
    <last_saved_districts>
      <congressional_district>UT-2</congressional_district>
      <state_upper_district>UT-13</state_upper_district>
      <state_lower_district>UT-32</state_lower_district>
      <split_district>No</split_district>
    </last_saved_districts>
    <custom_columns>
      <custom_column name="BestDecade"/>
      <custom_column name="Birthday"/>
      <custom_column name="Caregiver"/>
      <custom_column name="Contact Frequency"/>
      <custom_column name="f_name"
        created_at="2022-07-01T15:19:18Z"
        updated_at="2022-07-01T15:19:18Z">
        Cormac
      </custom_column>
      <custom_column name="Interest"/>
      <custom_column
        name="l_name"
        created_at="2022-07-01T15:19:30Z"
        updated_at="2022-07-01T15:19:30Z">
        Martinez del Rio
      </custom_column>
      <custom_column name="MoneyConcerns"/>
      <custom_column name="PantryType"/>
      <custom_column name="Parent"/>
      <custom_column name="PersonalFlex"/>
    </custom_columns>
    <subscriptions>
      <subscription
        campaign_id="227047"
        campaign_name="Primary Campaign "
        campaign_description="Campaigntest"
        opt_in_path_id="328887"
        status="Opted-Out"
        opt_in_source="JOIN"
        created_at="2022-06-29T17:28:24Z"
        activated_at="2022-06-29T17:28:24Z"
        opted_out_at="2022-07-01T15:18:59Z"
        opt_out_source="Texted a STOP word"
      />
    </subscriptions>
    <integrations>
    </integrations>
    <clicks>
    </clicks>
  </profile>
</response>
"""
