
# TargetSmart Test response

# #### District Endpoint ####

district_match = {
    'vb.vf_reg_cass_state': 'IL', 'vb.vf_reg_cass_zip': '60622',
    'vb.reg_cass_zip4': '7194', 'vb.vf_precinct_id': '36', 'vb.vf_precinct_name':
    'CITY OF CHICAGO W-26 P-36', 'vb.vf_ward': '26', 'vb.vf_township': '',
    'vb.vf_county_code': '031', 'vb.vf_county_name': 'CITY OF CHICAGO',
    'vb.vf_sd': '002', 'vb.vf_hd': '004', 'vb.vf_cd': '007', 'vb.vf_city_council':
    '', 'vb.vf_municipal_district': 'CHICAGO', 'vb.vf_county_council': '08',
    'vb.vf_judicial_district': 'CHICAGO', 'vb.vf_school_district': 'CHICAGO PUBLIC SCHOOLS',
    'distance_away_km': 0.0, 'statezip5zip4': 'il606227194', 'zip5zip4':
    '606227194', 'FilteredFirstCut.vb.vf_reg_cass_state': 'IL',
    'FilteredFirstCut.vb.vf_reg_cass_zip': '60622',
    'FilteredFirstCut.vb.reg_cass_zip4': '7194',
    'FilteredFirstCut.vb.vf_precinct_id': '36',
    'FilteredFirstCut.vb.vf_precinct_name': 'CITY OF CHICAGO W-26 P-36',
    'FilteredFirstCut.vb.vf_ward': '26', 'FilteredFirstCut.vb.vf_township': '',
    'FilteredFirstCut.vb.vf_county_code': '031',
    'FilteredFirstCut.vb.vf_county_name': 'CITY OF CHICAGO',
    'FilteredFirstCut.vb.vf_sd': '002', 'FilteredFirstCut.vb.vf_hd': '004',
    'FilteredFirstCut.vb.vf_cd': '007', 'FilteredFirstCut.vb.vf_city_council': '',
    'FilteredFirstCut.vb.vf_municipal_district': 'CHICAGO',
    'FilteredFirstCut.vb.vf_county_council': '08',
    'FilteredFirstCut.vb.vf_judicial_district': 'CHICAGO',
    'FilteredFirstCut.vb.vf_school_district': 'CHICAGO PUBLIC SCHOOLS',
    'voters_in_district': '2', 'z9_latitude': 41.898369, 'z9_longitude': -87.694382,
}

district_point = {
    'input': {
        'search_type': 'point', 'latitude': '41.898369',
        'longitude': '-87.694382'},
    'error': None, 'match_found': True,
    'match_data': district_match,
    'gateway_id': '782cbcf0-039c- 11e9-a8b0-37650c25b496',
    'function_id': '782dce4b-039c-11e9-8056-390eede430de'
}

district_zip = {
    'input': {'search_type': 'zip', 'zip5': '60622', 'zip4': '7194'},
    'error': None, 'match_found': True,
    'match_data': {
        'vb.vf_reg_cass_state': 'IL',
        'vb.vf_reg_cass_zip': '60622', 'vb.reg_cass_zip4': '7194',
        'vb.vf_precinct_id': '36', 'vb.vf_precinct_name': 'CITY OF CHICAGO W-26 P-36',
        'vb.vf_ward': '26', 'vb.vf_township': '', 'vb.vf_county_code': '031',
        'vb.vf_county_name': 'CITY OF CHICAGO', 'vb.vf_sd': '002', 'vb.vf_hd': '004',
        'vb.vf_cd': '007', 'vb.vf_city_council': '', 'vb.vf_municipal_district': 'CHICAGO',
        'vb.vf_county_council': '08', 'vb.vf_judicial_district': 'CHICAGO',
        'vb.vf_school_district': 'CHICAGO PUBLIC SCHOOLS'},
    'gateway_id': 'fd1e561c-03ad-11e9-a77a-899cbb59a220',
    'function_id': 'fd1f40fe-03ad-11e9-b9b2-8da4a145abf6'
}

district_expected = [
    'vb.vf_reg_cass_state', 'vb.vf_reg_cass_zip', 'vb.reg_cass_zip4',
    'vb.vf_precinct_id', 'vb.vf_precinct_name', 'vb.vf_ward',
    'vb.vf_township', 'vb.vf_county_code', 'vb.vf_county_name',
    'vb.vf_sd', 'vb.vf_hd', 'vb.vf_cd', 'vb.vf_city_council',
    'vb.vf_municipal_district', 'vb.vf_county_council',
    'vb.vf_judicial_district', 'vb.vf_school_district',
    'distance_away_km', 'statezip5zip4', 'zip5zip4',
    'FilteredFirstCut.vb.vf_reg_cass_state',
    'FilteredFirstCut.vb.vf_reg_cass_zip',
    'FilteredFirstCut.vb.reg_cass_zip4',
    'FilteredFirstCut.vb.vf_precinct_id',
    'FilteredFirstCut.vb.vf_precinct_name',
    'FilteredFirstCut.vb.vf_ward',
    'FilteredFirstCut.vb.vf_township',
    'FilteredFirstCut.vb.vf_county_code',
    'FilteredFirstCut.vb.vf_county_name',
    'FilteredFirstCut.vb.vf_sd',
    'FilteredFirstCut.vb.vf_hd', 'FilteredFirstCut.vb.vf_cd',
    'FilteredFirstCut.vb.vf_city_council',
    'FilteredFirstCut.vb.vf_municipal_district',
    'FilteredFirstCut.vb.vf_county_council',
    'FilteredFirstCut.vb.vf_judicial_district',
    'FilteredFirstCut.vb.vf_school_district',
    'voters_in_district', 'z9_latitude',
    'z9_longitude'
]

address_response = {
    'input': {
        'address': '100 N Main St, Chicago, IL 60622',
        'search_type': 'address'},
    'error': None, 'match_found': True, 'match_data': district_match,
    'gateway_id': 'febd57bc-03bb-11e9-ad98-592b0545ec68',
    'function_id': 'febdf462-03bb-11e9-a944-25816baaec7e'}

address_expected = [
    'vb.vf_reg_cass_state', 'vb.vf_reg_cass_zip', 'vb.reg_cass_zip4', 'vb.vf_precinct_id',
    'vb.vf_precinct_name', 'vb.vf_ward', 'vb.vf_township', 'vb.vf_county_code', 'vb.vf_county_name',
    'vb.vf_sd', 'vb.vf_hd', 'vb.vf_cd', 'vb.vf_city_council', 'vb.vf_municipal_district',
    'vb.vf_county_council', 'vb.vf_judicial_district', 'vb.vf_school_district', 'distance_away_km',
    'statezip5zip4', 'zip5zip4', 'FilteredFirstCut.vb.vf_reg_cass_state',
    'FilteredFirstCut.vb.vf_reg_cass_zip', 'FilteredFirstCut.vb.reg_cass_zip4',
    'FilteredFirstCut.vb.vf_precinct_id', 'FilteredFirstCut.vb.vf_precinct_name',
    'FilteredFirstCut.vb.vf_ward', 'FilteredFirstCut.vb.vf_township',
    'FilteredFirstCut.vb.vf_county_code', 'FilteredFirstCut.vb.vf_county_name',
    'FilteredFirstCut.vb.vf_sd', 'FilteredFirstCut.vb.vf_hd', 'FilteredFirstCut.vb.vf_cd',
    'FilteredFirstCut.vb.vf_city_council', 'FilteredFirstCut.vb.vf_municipal_district',
    'FilteredFirstCut.vb.vf_county_council', 'FilteredFirstCut.vb.vf_judicial_district',
    'FilteredFirstCut.vb.vf_school_district', 'voters_in_district', 'z9_latitude', 'z9_longitude'
]

zip_expected = [
    'vb.vf_reg_cass_state', 'vb.vf_reg_cass_zip', 'vb.reg_cass_zip4', 'vb.vf_precinct_id',
    'vb.vf_precinct_name', 'vb.vf_ward', 'vb.vf_township', 'vb.vf_county_code', 'vb.vf_county_name',
    'vb.vf_sd', 'vb.vf_hd', 'vb.vf_cd', 'vb.vf_city_council', 'vb.vf_municipal_district',
    'vb.vf_county_council', 'vb.vf_judicial_district', 'vb.vf_school_district'
]

# ### Radius Endpoint ###

radius_response = {
    'input': {
        'first_name': 'Billy', 'last_name': 'Blanks',
        'address': '100 N Main St, Chicago, IL', 'radius_size': '100',
        'radius_unit': 'miles', 'max_results': '10', 'gender': 'a',
        'composite_score_min': '1', 'composite_score_max': '100',
        'last_name_exact': 'True', 'last_name_is_prefix': 'False',
        'last_name_prefix_length': '10'},
    'error': None,
    'output': [{'similarity_score': 92, 'data_fields': {
        'vb.vf_g2014': 'Y',
        'vb.tsmart_middle_name': 'H', 'vb.vf_reg_cass_city': 'CHICAGO',
        'vb.vf_reg_cass_state': 'IL', 'ts.tsmart_midterm_general_turnout_score': '85.5',
        'vb.vf_g2016': 'Y', 'vb.vf_precinct_name': 'CITY OF CHICAGO W-26 P-36',
        'vb.voterid': 'Q8W8682Y', 'vb.voterbase_phone': '4435705356',
        'vb.tsmart_precinct_id': '36', 'vb.tsmart_city': 'CHICAGO',
        'vb.vf_earliest_registration_date': '20141104',
        'vb.vf_registration_date': '20141104', 'vb.vf_reg_cass_zip4': '4455',
        'vb.vf_reg_cass_zip': '60622',
        'vb.tsmart_precinct_name': 'CITY OF CHICAGO W-26 P-36',
        'vb.voterbase_gender': 'Male', 'vb.voterbase_age': '37',
        'vb.tsmart_full_address': '100 N Main St AVE APT 2',
        'vb.voterbase_id': 'IL-12568678',
        'vb.vf_reg_cass_address_full': '100 N Main St AVE # 2',
        'vb.tsmart_zip': '60622', 'vb.voterbase_registration_status': 'Registered',
        'vb.tsmart_state': 'IL', 'vb.vf_precinct_id': '36',
        'vb.tsmart_partisan_score': '99.6', 'vb.tsmart_name_suffix': '',
        'vb.tsmart_last_name': 'Blanks', 'vb.tsmart_first_name': 'Billy',
        'vb.tsmart_zip4': '4455'}, 'distance_km': '0.0119', 'distance_meters': '11',
        'distance_miles': '0.0074', 'distance_feet': '38', 'proximity_score': 100,
        'composite_score': 96, 'uniqueness_score': 100,
        'confidence_indicator': 'Excellent Match'}],
    'output_size': 1,
    'search_latitude': 41.897826, 'search_longitude': -87.69465,
    'gateway_id': '24639609-fb58-11e8-b8af-61c17d74b690',
    'function_id': '2464a7ac-fb58-11e8-8fc5-fd9b1d4a95a4',
}

radius_expected = [
    'similarity_score', 'distance_km', 'distance_meters', 'distance_miles',
    'distance_feet', 'proximity_score', 'composite_score', 'uniqueness_score',
    'confidence_indicator', 'ts.tsmart_midterm_general_turnout_score',
    'vb.tsmart_city', 'vb.tsmart_first_name', 'vb.tsmart_full_address',
    'vb.tsmart_last_name', 'vb.tsmart_middle_name', 'vb.tsmart_name_suffix',
    'vb.tsmart_partisan_score', 'vb.tsmart_precinct_id', 'vb.tsmart_precinct_name',
    'vb.tsmart_state', 'vb.tsmart_zip', 'vb.tsmart_zip4',
    'vb.vf_earliest_registration_date', 'vb.vf_g2014', 'vb.vf_g2016',
    'vb.vf_precinct_id', 'vb.vf_precinct_name', 'vb.vf_reg_cass_address_full',
    'vb.vf_reg_cass_city', 'vb.vf_reg_cass_state', 'vb.vf_reg_cass_zip',
    'vb.vf_reg_cass_zip4', 'vb.vf_registration_date', 'vb.voterbase_age',
    'vb.voterbase_gender', 'vb.voterbase_id', 'vb.voterbase_phone',
    'vb.voterbase_registration_status', 'vb.voterid'
]

phone_response = {
    'input': {'phones': '4435705356'},
    'error': None, 'result': [{
        'vb.voterid': 'Q8W8652Y',
        'vb.tsmart_full_address': '908 N MAIN AVE APT 2',
        'vb.voterbase_age': '37',
        'vb.tsmart_first_name': 'BILLY',
        'vb.voterbase_phone': '4435705355',
        'vb.vf_g2014': 'Y',
        'vb.tsmart_last_name': 'BLANKS',
        'vb.tsmart_zip': '50622',
        'vb.tsmart_state': 'IL',
        'vb.voterbase_gender': 'Male',
        'vb.tsmart_city': 'CHICAGO',
        'vb.tsmart_partisan_score': '99.6',
        'ts.tsmart_midterm_general_turnout_score': '85.5',
        'vb.voterbase_id': 'IL-12568678',
        'vb.voterbase_registration_status': 'Registered',
        'vb.vf_g2016': 'Y',
        'vb.tsmart_middle_name': 'H',
        'vb.tsmart_name_suffix': ''}],
    'gateway_id': '17d19715-062c-11e9-aedb-3d74ea11c29c',
    'function_id': '17d2818d-062c-11e9-a4a2-edee7fb1f969'
}

phone_expected = [
    'vb.voterid', 'vb.tsmart_full_address', 'vb.voterbase_age', 'vb.tsmart_first_name',
    'vb.voterbase_phone', 'vb.vf_g2014', 'vb.tsmart_last_name', 'vb.tsmart_zip',
    'vb.tsmart_state', 'vb.voterbase_gender', 'vb.tsmart_city', 'vb.tsmart_partisan_score',
    'ts.tsmart_midterm_general_turnout_score', 'vb.voterbase_id',
    'vb.voterbase_registration_status', 'vb.vf_g2016', 'vb.tsmart_middle_name',
    'vb.tsmart_name_suffix'
]
