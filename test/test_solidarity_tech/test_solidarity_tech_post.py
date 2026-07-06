import random

import pytest
import requests_mock

from parsons.solidarity_tech.solidarity_tech import SolidarityTech


def test_create_agent_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "agent_assignments", text="resp")
        res = st.create_agent_assignment(
            user_id=user_id, agent_user_id=agent_user_id, is_active=is_active
        )
    assert res == "resp"


def test_enroll_user_in_automation(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "automation_enrollments", text="resp")
        res = st.enroll_user_in_automation(automation_id=automation_id, user_id=user_id)
    assert res == "resp"


@pytest.mark.parametrize(
    "field_type",
    [("input", "textarea", "number", "date", "checkbox", "select", "radios", "checkboxes")],
)
def test_create_custom_user_property(st: SolidarityTech, field_type: str) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "custom_user_properties", text="resp")
        res = st.create_custom_user_property(
            label=label,
            description=description,
            field_type=field_type,
            options=options,
            scope_type=scope_type,
            scope_id=scope_id,
        )
    assert res == "resp"


def test_create_custom_user_property_option(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + f"custom_user_properties/{user_property_id}/option", text="resp")
        res = st.create_custom_user_property_option(
            user_property_id=user_property_id,
            label=label,
            value=value,
        )
    assert res == "resp"


def test_send_email_to_user(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "emails", text="resp")
        res = st.send_email_to_user(
            user_id=user_id,
            subject=subject,
            body_html=body_html,
            body_plain=body_plain,
            email_sender_id=email_sender_id,
            reply_to=reply_to,
            attachment_urls=attachment_urls,
            track_opens=track_opens,
            track_clicks=track_clicks,
        )
    assert res == "resp"


def test_create_event_attendance(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "event_attendances", text="resp")
        res = st.create_event_attendance(
            event_id=event_id, event_session_id=event_session_id, user_id=user_id, attended=attended
        )
    assert res == "resp"


def test_create_event_rsvps(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "event_rsvps", text="resp")
        res = st.create_event_rsvps(
            event_id=event_id,
            event_session_id=event_session_id,
            user_id=user_id,
            is_attending=is_attending,
            is_confirmed=is_confirmed,
            agent_user_id=agent_user_id,
            source=source,
            source_system=source_system,
            skip_email_confirmation=skip_email_confirmation,
        )
    assert res == "resp"


def test_create_event_session(st: SolidarityTech) -> None:
    event_id = random.randrange(234876, 389759)
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "event_sessions", text="resp")
        res = st.create_event_session(
            event_id=event_id,
            start_time=start_time,
            end_time=end_time,
            event_type=event_type,
            title=title,
            location_name=location_name,
            location_data=location_data,
            location_address=location_address,
            show_rsvp_bar=show_rsvp_bar,
            show_title_in_form=show_title_in_form,
            note=note,
            max_capacity=max_capacity,
            tags=tags,
        )
    assert res == "resp"


def test_create_event(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "events", text="resp")
        res = st.create_event(
            title=title,
            event_type=event_type,
            start_time=start_time,
            end_time=end_time,
            location_address=location_address,
            virtual_url=virtual_url,
            location_name=location_name,
            scope_id=scope_id,
            scope_type=scope_type,
            session_title=session_title,
            tags=tags,
            max_capacity=max_capacity,
            latitude=latitude,
            longitude=longitude,
            skip_duplicate_check=skip_duplicate_check,
        )
    assert res == "resp"


def test_create_field_survey_url(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "field_survey_urls", text="resp")
        res = st.create_field_survey_url(
            user_id=user_id,
            agent_user_id=agent_user_id,
            page_id=page_id,
        )
    assert res == "resp"


def test_create_scheduled_task(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "scheduled_tasks", text="resp")
        res = st.create_scheduled_task(
            due_at=due_at,
            remind_at=remind_at,
            agent_user_id=agent_user_id,
            user_id=user_id,
            notes=notes,
            marked_as_completed=marked_as_completed,
        )
    assert res == "resp"


def test_create_task_agent(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "task_agents", text="resp")
        res = st.create_task_agent(
            user_id=user_id,
            task_id=task_id,
        )
    assert res == "resp"


def test_create_task_assignment(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "task_assignments", text="resp")
        res = st.create_task_assignment(
            user_id=user_id,
            task_id=task_id,
            agent_user_id=agent_user_id,
        )
    assert res == "resp"


def test_create_team_member(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "team_members", text="resp")
        res = st.create_team_member(
            member_id=member_id,
            phone_number=phone_number,
            email=email,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            role_id=role_id,
            scope_type=scope_type,
            scope_id=scope_id,
            invite_via=invite_via,
            task_id=task_id,
        )
    assert res == "resp"


def test_create_text_template(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "text_templates", text="resp")
        res = st.create_text_template(
            name=name,
            scope_id=scope_id,
            scope_type=scope_type,
            template=template,
            event_id=event_id,
        )
    assert res == "resp"


def test_send_test_message(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "texts", text="resp")
        res = st.send_test_message(
            user_id=user_id,
            body=body,
            media_urls=media_urls,
            attach_contact_card=attach_contact_card,
            shorten_urls=shorten_urls,
        )
    assert res == "resp"


def test_create_user_action(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "user_actions", text="resp")
        res = st.create_user_action(
            page_id=page_id,
            user_id=user_id,
            created_at=created_at,
            data=data,
        )
    assert res == "resp"


def test_create_user_list(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "user_lists", text="resp")
        res = st.create_user_list(
            name=name,
            scope_id=scope_id,
            scope_type=scope_type,
            event_id=event_id,
            user_id=user_id,
            parameters=parameters,
        )
    assert res == "resp"


def test_create_user_note(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "user_notes", text="resp")
        res = st.create_user_note(
            user_id=user_id,
            agent_id=agent_id,
            content=content,
            created_at=created_at,
            restricted=restricted,
            interaction_method=interaction_method,
        )
    assert res == "resp"


def test_create_user_relationship(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "user_relationships", text="resp")
        res = st.create_user_relationship(
            user_id=user_id,
            related_user_id=related_user_id,
            relationship_type=relationship_type,
        )
    assert res == "resp"


def test_create_user(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "users", text="resp")
        res = st.create_user(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            alternate_name=alternate_name,
            preferred_language=preferred_language,
            second_language=second_language,
            chapter_id=chapter_id,
            chapter_ids=chapter_ids,
            referred_by_user_id=referred_by_user_id,
            custom_user_properties=custom_user_properties,
            append_custom_user_properties=append_custom_user_properties,
            add_tags=add_tags,
            remove_tags=remove_tags,
            donation_charge=donation_charge,
            address=address,
            assessment=assessment,
            sms_permission=sms_permission,
            call_permission=call_permission,
            email_permission=email_permission,
            timezone=timezone,
            require_contact_info=require_contact_info,
            phone_number_textable_validation=phone_number_textable_validation,
            lookup_key=lookup_key,
        )
    assert res == "resp"


def test_update_user(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "users", text="resp")
        res = st.update_user(
            phone_number=phone_number,
            email=email,
            first_name=first_name,
            last_name=last_name,
            alternate_name=alternate_name,
            preferred_language=preferred_language,
            second_language=second_language,
            chapter_id=chapter_id,
            chapter_ids=chapter_ids,
            referred_by_user_id=referred_by_user_id,
            custom_user_properties=custom_user_properties,
            append_custom_user_properties=append_custom_user_properties,
            add_tags=add_tags,
            remove_tags=remove_tags,
            donation_charge=donation_charge,
            address=address,
            assessment=assessment,
            sms_permission=sms_permission,
            call_permission=call_permission,
            email_permission=email_permission,
            timezone=timezone,
            require_contact_info=require_contact_info,
            phone_number_textable_validation=phone_number_textable_validation,
            lookup_key=lookup_key,
        )
    assert res == "resp"


def test_duplicate_users(st: SolidarityTech) -> None:
    with requests_mock.Mocker() as m:
        m.post(st.api_url + "users/merge", text="resp")
        res = st.duplicate_users(
            primary_user_id=primary_user_id,
            user_ids=user_ids,
        )
    assert res == "resp"
