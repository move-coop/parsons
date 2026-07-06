import requests_mock

from parsons.solidarity_tech.solidarity_tech import SolidarityTech


def test_delete_agent_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"agent_assignments/{agent_assignment_id}", text="resp")
        resp = st.delete_agent_assignment(id=agent_assignment_id)
    assert resp == "resp"


def test_delete_custom_user_property_option(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(
            st.api_url + f"custom_user_properties/{custom_user_property_id}/options/{option_id}",
            text="resp",
        )
        resp = st.delete_custom_user_property_option(
            custom_user_property_id=custom_user_property_id, id=option_id
        )
    assert resp == "resp"


def test_delete_event_attendance(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"event_attendances/{event_attendance_id}", text="resp")
        resp = st.delete_event_attendance(id=event_attendance_id)
    assert resp == "resp"


def test_delete_event_rsvp(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"event_rsvps/{event_rsvp_id}", text="resp")
        resp = st.delete_event_rsvp(id=event_rsvp_id)
    assert resp == "resp"


def test_delete_event_session(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"event_sessions/{event_session_id}", text="resp")
        resp = st.delete_event_session(id=event_session_id)
    assert resp == "resp"


def test_delete_scheduled_task(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"scheduled_tasks/{scheduled_task_id}", text="resp")
        resp = st.delete_scheduled_task(id=scheduled_task_id)
    assert resp == "resp"


def test_delete_task_agent(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"task_agents/{task_agent_id}", text="resp")
        resp = st.delete_task_agent(id=task_agent_id)
    assert resp == "resp"


def test_delete_task_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"task_assignments/{task_assignment_id}", text="resp")
        resp = st.delete_task_assignment(id=task_assignment_id)
    assert resp == "resp"


def test_delete_text_template(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"text_templates/{text_template_id}", text="resp")
        resp = st.delete_text_template(id=text_template_id)
    assert resp == "resp"


def test_delete_user_list(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"user_lists/{user_list_id}", text="resp")
        resp = st.delete_user_list(id=user_list_id)
    assert resp == "resp"


def test_delete_user_note(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"user_notes/{user_note_id}", text="resp")
        resp = st.delete_user_note(id=user_note_id)
    assert resp == "resp"


def test_delete_user_relationship(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.delete(st.api_url + f"user_relationships/{user_relationship_id}", text="resp")
        resp = st.delete_user_relationship(id=user_relationship_id)
    assert resp == "resp"
