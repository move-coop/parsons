def main():
pipeline_van_to_zoom = Pipeline(
    load_voters_from_van(),
    strip_pii_data_from_voters(),
    merge_duplicates("van_id"),
    convert_van_contacts_to_intermediate_contacts(),
    upload_contacts_to_zoom(),
)

load_in_meetings = Pipeline(
    load_meetings_from_zoom(),
    convert_zoom_meeting_to_intermediate_event(),
)

load_in_webinars = Pipeline(
    load_webinars_from_zoom(),
    convert_zoom_webinar_to_intermediate_event(),
)

pipeline_zoom_attendance_to_van = Pipeline(
    combine_data(
        load_in_meetings,
        load_in_webinars
    ),
    validate(
        no_duplicate_values("event_id"),
        failure_strategy="log_and_defer"
    ),
    [
        Pipeline(
            convert_intermediate_event_to_van_event(
                failure_strategy="end_run"
            ),
            upload_van_events()
        ),
        Pipeline(
            load_zoom_attendees(),
            convert_zoom_attendees_to_intermediate_person(),
            match_person_with_voterfile(if_not_found="remove"),
            upload_voterfile_match_to_van()
        )
    ]
)

pipelines = [pipeline_van_to_zoom, pipeline_zoom_attendance_to_van]

HttpDashboard.run_pipelines(
    pipelines,
    ip_addr="127.0.0.1",
    logging_strategy=SampleEachStepInCSV(n=50)
)
