from build.lib.test.utils import validate_list
from parsons.controlshift.controlshift import Controlshift
from test.utils import mark_live_test


@mark_live_test
def test_get_petitions():
    cs = Controlshift()
    tbl = cs.get_petitions()
    expected_columns = [
        'admin_events_status', 'admin_status', 'alias', 'campaigner_contactable',
        'can_download_signers', 'created_at', 'custom_goal', 'delivery_details',
        'external_facebook_page', 'external_site', 'goal', 'hide_petition_creator',
        'hide_recent_signers', 'hide_signature_form', 'id', 'launched', 'locale',
        'petition_creator_name_override', 'redirect_to', 'show_progress_bar',
        'signature_count_add_amount', 'slug',
        'source', 'title', 'updated_at', 'what', 'who', 'why', 'title_locked', 'who_locked',
        'what_locked', 'why_locked', 'delivery_details_locked', 'external_facebook_page_locked',
        'external_site_locked', 'categories_locked', 'url', 'public_who', 'ended', 'successful',
        'image', 'public_signature_count', 'admin_notes', 'creator', 'mentor', 'reviewer',
        'location', 'decision_makers', 'effort', 'partnership', 'labels', 'categories']
    assert validate_list(expected_columns, tbl)
