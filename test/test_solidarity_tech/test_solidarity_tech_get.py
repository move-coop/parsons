import random

import requests_mock

from parsons.solidarity_tech.solidarity_tech import SolidarityTech


def test_get_activities(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "activities", text="resp")
        activities = st.get_activities(
            limit=limit, cursor=cursor, since=since, include_count=include_count, user_id=user_id
        )
    assert activities == "resp"


def test_get_agent_assignments(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "agent_assignments", text="resp")
        activities = st.get_agent_assignments(
            limit=limit, offset=offset, since=since, user_id=user_id, agent_user_id=agent_user_id
        )
    assert activities == "resp"


def test_get_agent_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"agent_assignments/{agent_assignment_id}", text="resp")
        activities = st.get_agent_assignment(id=agent_assignment_id)
    assert activities == "resp"


def test_get_calls(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "calls", text="resp")
        activities = st.get_calls(user_id=user_id, limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_chapter_phone_numbers(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "chapter_phone_numbers", text="resp")
        activities = st.get_chapter_phone_numbers(
            limit=limit, offset=offset, since=since, chapter_id=chapter_id
        )
    assert activities == "resp"


def test_get_chapters(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "chapters", text="resp")
        activities = st.get_chapters(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_custom_user_properties(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "custom_user_properties", text="resp")
        activities = st.get_custom_user_properties(
            limit=limit, offset=offset, since=since, scope_id=scope_id, scope_type=scope_type
        )
    assert activities == "resp"


def test_get_donation_charges(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "donation_charges", text="resp")
        activities = st.get_donation_charges(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_donation_charge(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"donation_charges/{donation_id}", text="resp")
        activities = st.get_donation_charge(id=donation_id)
    assert activities == "resp"


def test_get_email_blasts(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "email_blasts", text="resp")
        activities = st.get_email_blasts(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_email_blast(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"email_blasts/{email_blast_id}", text="resp")
        activities = st.get_email_blast(id=email_blast_id)
    assert activities == "resp"


def test_get_email_senders(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "email_senders", text="resp")
        activities = st.get_email_senders(limit=limit, offset=offset)
    assert activities == "resp"


def test_get_event_attendances(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "event_attendances", text="resp")
        activities = st.get_event_attendances(
            limit=limit, offset=offset, since=since, event_id=event_id, session_id=session_id
        )
    assert activities == "resp"


def test_get_event_rsvps(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "event_rsvps", text="resp")
        activities = st.get_event_rsvps(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
            session_id=session_id,
            user_id=user_id,
            full_user_payload=full_user_payload,
        )
    assert activities == "resp"


def test_get_event_rsvp(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"event_rsvps/{event_rsvp_id}", text="resp")
        activities = st.get_event_rsvp(id=event_rsvp_id)
    assert activities == "resp"


def test_get_event_sessions(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "event_sessions", text="resp")
        activities = st.get_event_sessions(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
        )
    assert activities == "resp"


def test_get_event_session(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"event_sessions/{event_session_id}", text="resp")
        activities = st.get_event_session(id=event_session_id)
    assert activities == "resp"


def test_get_events(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "events", text="resp")
        activities = st.get_events(
            limit=limit,
            offset=offset,
            since=since,
            scope_id=scope_id,
            scope_type=scope_type,
        )
    assert activities == "resp"


def test_get_event(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"events/{event_id}", text="resp")
        activities = st.get_event(id=event_id)
    assert activities == "resp"


def test_get_organizations(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "organizations", text="resp")
        activities = st.get_organizations(
            limit=limit,
            offset=offset,
            since=since,
        )
    assert activities == "resp"


def test_get_organization(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"organizations/{organization_id}", text="resp")
        activities = st.get_organization(id=organization_id)
    assert activities == "resp"


def test_get_pages(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "pages", text="resp")
        activities = st.get_pages(
            limit=limit,
            offset=offset,
            since=since,
        )
    assert activities == "resp"


def test_get_page(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"pages/{page_id}", text="resp")
        activities = st.get_page(id=page_id)
    assert activities == "resp"


def test_get_phonebanks(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "phonebanks", text="resp")
        activities = st.get_phonebanks(
            limit=limit,
            offset=offset,
            since=since,
            event_id=event_id,
        )
    assert activities == "resp"


def test_get_phonebank(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"phonebanks/{phonebank_id}", text="resp")
        activities = st.get_phonebank(id=phonebank_id)
    assert activities == "resp"


def test_get_scheduled_calls(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "scheduled_calls", text="resp")
        activities = st.get_scheduled_calls(
            limit=limit,
            offset=offset,
            since=since,
            user_id=user_id,
            agent_user_id=agent_user_id,
        )
    assert activities == "resp"


def test_get_scheduled_call(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"scheduled_calls/{scheduled_call_id}", text="resp")
        activities = st.get_scheduled_call(id=scheduled_call_id)
    assert activities == "resp"


def test_get_scheduled_tasks(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "scheduled_tasks", text="resp")
        activities = st.get_scheduled_tasks(
            limit=limit, offset=offset, since=since, user_id=user_id, agent_user_id=agent_user_id
        )
    assert activities == "resp"


def test_get_scheduled_task(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"scheduled_tasks/{scheduled_task_id}", text="resp")
        activities = st.get_scheduled_task(id=scheduled_task_id)
    assert activities == "resp"


def test_get_task_agents(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "task_agents", text="resp")
        activities = st.get_task_agents(limit=limit, offset=offset, since=since, task_id=task_id)
    assert activities == "resp"


def test_get_task_agent(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"task_agents/{task_agent_id}", text="resp")
        activities = st.get_task_agent(id=task_agent_id)
    assert activities == "resp"


def test_get_task_assignments(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "task_assignments", text="resp")
        activities = st.get_task_assignments(
            limit=limit, offset=offset, since=since, task_id=task_id, agent_user_id=agent_user_id
        )
    assert activities == "resp"


def test_get_task_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"task_assignments/{task_assignment_id}", text="resp")
        activities = st.get_task_assignment(id=task_assignment_id)
    assert activities == "resp"


def test_get_team_members(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "team_members", text="resp")
        activities = st.get_team_members(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_text_blasts(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "text_blasts", text="resp")
        activities = st.get_text_blasts(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_text_blast(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"text_blasts/{text_blast_id}", text="resp")
        activities = st.get_text_blast(id=text_blast_id)
    assert activities == "resp"


def test_get_text_templates(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "text_templates", text="resp")
        activities = st.get_text_templates(
            limit=limit, offset=offset, since=since, event_id=event_id
        )
    assert activities == "resp"


def test_get_text_template(st: SolidarityTech) -> None:
    text_template_id = random.randrange(234876, 389759)
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"text_templates/{text_template_id}", text="resp")
        activities = st.get_text_template(text_template_id)
    assert activities == "resp"


def test_get_textbanks(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "textbanks", text="resp")
        activities = st.get_textbanks(limit=limit, offset=offset, since=since, event_id=event_id)
    assert activities == "resp"


def test_get_textbank(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"textbanks/{textbank_id}", text="resp")
        activities = st.get_textbank(id=textbank_id)
    assert activities == "resp"


def test_get_texts(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "texts", text="resp")
        activities = st.get_texts(
            user_id=user_id,
            limit=limit,
            offset=offset,
            since=since,
        )
    assert activities == "resp"


def test_get_user_actions(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "user_actions", text="resp")
        activities = st.get_user_actions(
            user_id=user_id, page_id=page_id, limit=limit, offset=offset, since=since
        )
    assert activities == "resp"


def test_get_user_lists(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "user_lists", text="resp")
        activities = st.get_user_lists(limit=limit, offset=offset, since=since)
    assert activities == "resp"


def test_get_user_list(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"user_lists/{user_list_id}", text="resp")
        activities = st.get_user_list(id=user_list_id)
    assert activities == "resp"


def test_get_user_relationship_types(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"user_relationships/{user_id}", text="resp")
        activities = st.get_user_relationships_types(id=user_id)
    assert activities == "resp"


def test_get_users(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + "users", text="resp")
        activities = st.get_users(
            limit=limit,
            offset=offset,
            since=since,
            user_list_ids=user_list_ids,
            phone_number=phone_number,
            email=email,
        )
    assert activities == "resp"


def test_get_user(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.get(st.api_url + f"users/{user_id}", text="resp")
        activities = st.get_user(id=user_id)
    assert activities == "resp"
