records_response = {
    "records": [
        {
            "id": "recaBMSHTgXREa5ef",
            "fields": {"Name": "This is a row!"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recObtmLUrD5dOnmD",
            "fields": {},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recmeBNnj4cuHPOSI",
            "fields": {},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
    ]
}

insert_response = {
    "id": "recD4aEaEjQKYZABZ",
    "fields": {"Name": "Another row!"},
    "createdTime": "2019-05-13T16:28:18.000Z",
}

insert_responses = {
    "records": [
        {
            "id": "recIYuf51JgbmHCHo",
            "fields": {"Name": "Another!"},
            "createdTime": "2019-05-13T16:37:03.000Z",
        },
        {
            "id": "recJMqCfPwFVV5qfc",
            "fields": {"Name": "Another row!"},
            "createdTime": "2019-05-13T16:37:03.000Z",
        },
    ]
}

records_response_with_more_columns = {
    "records": [
        {
            "id": "recaBMSHTgXREa5ef",
            "fields": {"Name": "This is a row!"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recaBMSHTgXvEa5ef",
            "fields": {"Name": "This is a row!"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recaBMSHTgXREsaef",
            "fields": {"Name": "This is a row!"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recObtmLUrD5dOnmD",
            "fields": {"Name": "This is a row!", "SecondColumn": ""},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recmeBNnj4cuHPOSI",
            "fields": {"Name": "This is a row!", "SecondColumn": ""},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
    ]
}

update_responses = {
    "records": [
        {
            "id": "recaBMSHTgXREa5ef",
            "fields": {"Name": "Updated Name1"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recObtmLUrD5dOnmD",
            "fields": {"Name": "Updated Name2"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recmeBNnj4cuHPOSI",
            "fields": {"Name": "Updated Name3"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
    ]
}

upsert_with_id_responses = {
    "records": [
        {
            "id": "recz9W2ojGNwMdN2y",
            "fields": {"Name": "Updated Name1"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recB5njCET7AvHBbg",
            "fields": {"Name": "Updated Name2"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recz9W2ojgPwMdN2y",
            "fields": {"Name": "New Name3"},
            "createdTime": "2024-06-23T15:06:58.000Z",
        },
    ],
    "updatedRecords": [
        "recz9W2ojGNwMdN2y",
        "recB5njCET7AvHBbg",
    ],
    "createdRecords": [
        "recz9W2ojgPwMdN2y",
    ],
}

upsert_with_key_responses = {
    "records": [
        {
            "id": "recz9W2ojGNwMdN2y",
            "fields": {"key": "1", "Name": "New Name1"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recB5njCET7AvHBbg",
            "fields": {"key": "2", "Name": "New Name2"},
            "createdTime": "2019-05-08T19:37:58.000Z",
        },
        {
            "id": "recz9W2ojgPwMdN2y",
            "fields": {"key": "3", "Name": "Updated Name3"},
            "createdTime": "2024-06-23T15:06:58.000Z",
        },
    ],
    "updatedRecords": [
        "recz9W2ojgPwMdN2y",
    ],
    "createdRecords": [
        "recz9W2ojGNwMdN2y",
        "recB5njCET7AvHBbg",
    ],
}

delete_responses = {
    "records": [
        {
            "id": "recaBMSHTgXREa5ef",
            "deleted": True,
        },
        {
            "id": "recObtmLUrD5dOnmD",
            "deleted": True,
        },
        {
            "id": "recmeBNnj4cuHPOSI",
            "deleted": True,
        },
    ]
}
