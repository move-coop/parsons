from datetime import datetime
from typing import Any

import pytest

from parsons import ActionNetwork
from parsons.action_network.action_network import API_URL

API_KEY = "fake_key"


@pytest.fixture
def an() -> ActionNetwork:
    return ActionNetwork(API_KEY)


@pytest.fixture
def fake_datetime_obj() -> datetime:
    return datetime.strptime("2019-02-28T00:00:00.000+0000", "%Y-%m-%dT%H:%M:%S.%f%z")


@pytest.fixture
def fake_datetime(fake_datetime_obj: datetime) -> str:
    ms = fake_datetime_obj.microsecond // 1000
    return f"{fake_datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')}.{ms:03d}{fake_datetime_obj.strftime('%z')}"


@pytest.fixture
def fake_date(fake_datetime_obj: datetime) -> str:
    return fake_datetime_obj.strftime("%Y-%m-%d")


@pytest.fixture
def fake_customer_email_1() -> str:
    return "fake_customer_email_1@fake_customer_email.com"


@pytest.fixture
def fake_customer_email_2() -> str:
    return "fake_customer_email_2@fake_customer_email.com"


@pytest.fixture
def fake_filter_by_email_1(fake_customer_email_1: str) -> str:
    return f"filter eq '{fake_customer_email_1}'"


@pytest.fixture
def fake_person_id_1() -> str:
    return "action_network:fake_person_id_1"


@pytest.fixture
def fake_person_id_2() -> str:
    return "action_network:fake_person_id_2"


@pytest.fixture
def fake_tag_id_1() -> str:
    return "fake_tag_id_1"


@pytest.fixture
def fake_tag_id_2() -> str:
    return "fake_tag_id_2"


@pytest.fixture
def fake_tag_filter() -> str:
    return "name eq 'fake_tag_1'"


@pytest.fixture
def fake_people_list_1(
    fake_person_id_1: str,
    fake_person_id_2: str,
    fake_customer_email_1: str,
    fake_customer_email_2: str,
    fake_datetime: str,
) -> dict[str, Any]:
    next_page_number = 2
    return {
        "per_page": 2,
        "page": 1,
        "_links": {
            "next": {"href": f"{API_URL}/people?page={next_page_number}"},
            "osdi:people": [
                {"href": f"{API_URL}/{fake_person_id_1}"},
                {"href": f"{API_URL}/{fake_person_id_2}"},
            ],
            "curies": [
                {"name": "osdi", "templated": True},
                {"name": "action_network", "templated": True},
            ],
            "self": {"href": f"{API_URL}/people"},
        },
        "_embedded": {
            "osdi:people": [
                {
                    "given_name": "Fakey",
                    "family_name": "McFakerson",
                    "identifiers": [fake_person_id_1],
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": fake_customer_email_1,
                            "status": "subscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "region": "",
                            "country": "US",
                            "location": {
                                "latitude": None,
                                "longitude": None,
                                "accuracy": None,
                            },
                        }
                    ],
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "languages_spoken": ["en"],
                },
                {
                    "given_name": "Faker",
                    "family_name": "McEvenFakerson",
                    "identifiers": [fake_person_id_2],
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": fake_customer_email_2,
                            "status": "subscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "region": "",
                            "country": "US",
                            "location": {
                                "latitude": None,
                                "longitude": None,
                                "accuracy": None,
                            },
                        }
                    ],
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "languages_spoken": ["en"],
                },
            ]
        },
    }


@pytest.fixture
def fake_people_list_2(
    fake_person_id_1: str,
    fake_person_id_2: str,
    fake_customer_email_1: str,
    fake_customer_email_2: str,
    fake_datetime: str,
) -> dict[str, Any]:
    next_page_number = 3
    return {
        "per_page": 2,
        "page": 2,
        "_links": {
            "next": {"href": f"{API_URL}/people?page={next_page_number}"},
            "osdi:people": [
                {"href": f"{API_URL}/{fake_person_id_1}"},
                {"href": f"{API_URL}/{fake_person_id_2}"},
            ],
            "curies": [
                {"name": "osdi", "templated": True},
                {"name": "action_network", "templated": True},
            ],
            "self": {"href": f"{API_URL}/people"},
        },
        "_embedded": {
            "osdi:people": [
                {
                    "given_name": "Fakey",
                    "family_name": "McFakerson",
                    "identifiers": [fake_person_id_1],
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": fake_customer_email_1,
                            "status": "subscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "region": "",
                            "country": "US",
                            "location": {
                                "latitude": None,
                                "longitude": None,
                                "accuracy": None,
                            },
                        }
                    ],
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "languages_spoken": ["en"],
                },
                {
                    "given_name": "Faker",
                    "family_name": "McEvenFakerson",
                    "identifiers": [fake_person_id_2],
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": fake_customer_email_2,
                            "status": "subscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "region": "",
                            "country": "US",
                            "location": {
                                "latitude": None,
                                "longitude": None,
                                "accuracy": None,
                            },
                        }
                    ],
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "languages_spoken": ["en"],
                },
            ]
        },
    }


@pytest.fixture
def fake_people_list(fake_people_list_1: dict, fake_people_list_2: dict) -> list[dict]:
    return (
        fake_people_list_1["_embedded"]["osdi:people"]
        + fake_people_list_2["_embedded"]["osdi:people"]
    )


@pytest.fixture
def fake_tag_list(fake_tag_id_1: str, fake_tag_id_2: str, fake_datetime: str) -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 2,
        "page": 1,
        "total_records": 2,
        "_links": {
            "next": {"href": f"{API_URL}/tags?page=2"},
            "osdi:tags": [
                {"href": f"{API_URL}/tags/{fake_tag_id_1}"},
                {"href": f"{API_URL}/tags/{fake_tag_id_2}"},
            ],
            "curies": [
                {"name": "osdi", "templated": True},
                {"name": "action_network", "templated": True},
            ],
            "self": {"href": f"{API_URL}/tags"},
        },
        "_embedded": {
            "osdi:tags": [
                {
                    "name": "fake_tag_1",
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "identifiers": [fake_tag_id_1],
                    "_links": {"self": {"href": fake_tag_id_1}},
                },
                {
                    "name": "fake_tag_2",
                    "created_date": fake_datetime,
                    "modified_date": fake_datetime,
                    "identifiers": [fake_tag_id_1],
                    "_links": {"self": {"href": fake_tag_id_1}},
                },
            ]
        },
    }


@pytest.fixture
def fake_upsert_person(fake_person_id_1: dict, fake_datetime: dict) -> dict[str, Any]:
    return {
        "given_name": "Fakey",
        "family_name": "McFakerson",
        "identifiers": [fake_person_id_1],
        "email_address": [
            {
                "primary": True,
                "address": "fakey@mcfakerson.com",
                "status": "unsubscribed",
            }
        ],
        "created_date": fake_datetime,
        "modified_date": fake_datetime,
    }


@pytest.fixture
def fake_person(fake_person_id_1: dict, fake_date: dict) -> list[dict]:
    return [
        {
            "given_name": "Fakey",
            "family_name": "McFakerson",
            "identifiers": [fake_person_id_1],
            "email_addresses": [
                {
                    "primary": True,
                    "address": "fakey@mcfakerson.com",
                    "status": "unsubscribed",
                }
            ],
            "postal_addresses": [
                {
                    "primary": True,
                    "locality": "Washington",
                    "region": "DC",
                    "postal_code": "20009",
                    "country": "US",
                    "location": {
                        "latitude": 38.919,
                        "longitude": -77.0378,
                        "accuracy": None,
                    },
                }
            ],
            "_links": {
                "self": {"href": "fake_url"},
                "osdi:signatures": {"href": "fake_url"},
                "osdi:submissions": {"href": "fake_url"},
                "osdi:donations": {"href": "fake_url"},
                "curies": [
                    {"name": "osdi", "href": "fake_url", "templated": True},
                    {
                        "name": "action_network",
                        "href": "fake_url",
                        "templated": True,
                    },
                ],
                "osdi:taggings": {"href": "fake_url"},
                "osdi:outreaches": {"href": "fake_url"},
                "osdi:attendances": {"href": "fake_url"},
            },
            "custom_fields": {},
            "created_date": fake_date,
            "modified_date": fake_date,
            "languages_spoken": ["en"],
        }
    ]


@pytest.fixture
def updated_fake_person(fake_person_id_1: dict, fake_date: dict) -> list[dict]:
    return [
        {
            "given_name": "Flakey",
            "family_name": "McFlakerson",
            "identifiers": [fake_person_id_1],
            "email_addresses": [
                {
                    "primary": True,
                    "address": "fakey@mcfakerson.com",
                    "status": "unsubscribed",
                }
            ],
            "postal_addresses": [
                {
                    "primary": True,
                    "locality": "Washington",
                    "region": "DC",
                    "postal_code": "20009",
                    "country": "US",
                    "location": {
                        "latitude": 38.919,
                        "longitude": -77.0378,
                        "accuracy": None,
                    },
                }
            ],
            "_links": {
                "self": {"href": "fake_url"},
                "osdi:signatures": {"href": "fake_url"},
                "osdi:submissions": {"href": "fake_url"},
                "osdi:donations": {"href": "fake_url"},
                "curies": [
                    {"name": "osdi", "href": "fake_url", "templated": True},
                    {
                        "name": "action_network",
                        "href": "fake_url",
                        "templated": True,
                    },
                ],
                "osdi:taggings": {"href": "fake_url"},
                "osdi:outreaches": {"href": "fake_url"},
                "osdi:attendances": {"href": "fake_url"},
            },
            "custom_fields": {},
            "created_date": fake_date,
            "modified_date": fake_date,
            "languages_spoken": ["en"],
        }
    ]


@pytest.fixture
def fake_tag(fake_datetime: str, fake_tag_id_1: str) -> dict[str, Any]:
    return {
        "name": "fake_tag_1",
        "created_date": fake_datetime,
        "modified_date": fake_datetime,
        "identifiers": [fake_tag_id_1],
        "_links": {"self": {"href": fake_tag_id_1}},
    }


@pytest.fixture
def fake_location() -> dict[str, Any]:
    return {
        "venue": "White House",
        "address_lines": ["1600 Pennsylvania Ave"],
        "locality": "Washington",
        "region": "DC",
        "postal_code": "20009",
        "country": "US",
    }


@pytest.fixture
def fake_event(fake_date: str, fake_location: dict) -> dict[str, Any]:
    return {
        "title": "fake_title",
        "start_date": fake_date,
        "location": fake_location,
        "_links": {
            "self": {"href": f"{API_URL}/events/fake-id"},
        },
        "event_id": "fake-id",
    }


@pytest.fixture
def fake_unique_id_list() -> dict[str, Any]:
    return {
        "name": "fake_list_name",
        "unique_ids": [
            "ee48622d-a584-46a4-b817-2e6f2e4bf51b",
            "1b0012d2-214a-4188-9c82-08f21ee54b27",
        ],
    }


@pytest.fixture
def fake_advocacy_campaigns() -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 25,
        "page": 1,
        "total_records": 3,
        "_links": {
            "next": {"href": f"{API_URL}/advocacy_campaigns?page=2"},
            "self": {"href": f"{API_URL}/advocacy_campaigns"},
            "osdi:advocacy_campaigns": [
                {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:advocacy_campaigns": [
                {
                    "origin_system": "FreeAdvocacy.com",
                    "identifiers": [
                        "action_network:65345d7d-cd24-466a-a698-4a7686ef684f",
                        "free_forms:1",
                    ],
                    "created_date": "2014-03-25T14:40:07Z",
                    "modified_date": "2014-03-25T14:47:44Z",
                    "title": "Tell your Senator to stop the bad thing!",
                    "targets": "U.S. Senate",
                    "type": "email",
                    "total_outreaches": 25,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave"],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 32.935,
                                        "longitude": -73.1338,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:attendances": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:submissions": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:donations": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_url"},
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:outreaches": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:record_outreach_helper": {
                            "href": f"{API_URL}/advocacy_campaigns/fake_url"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_url"},
                        "action_network:embed": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-21T23:39:53Z",
                    "modified_date": "2014-03-25T15:26:45Z",
                    "title": "Thank Acme's CEO for going green",
                    "description": "<p>Write a letter today!</p>",
                    "browser_url": "https://actionnetwork.org/letters/thanks-acme",
                    "featured_image_url": "https://actionnetwork.org/images/acme.jpg",
                    "targets": "Acme CEO",
                    "type": "email",
                    "total_outreaches": 6,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 32.934,
                                        "longitude": -74.5319,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:attendances": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:submissions": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:donations": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_url"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_url"},
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:outreaches": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:record_outreach_helper": {
                            "href": f"{API_URL}/advocacy_campaigns/fake_url"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                    },
                },
                {
                    "created_date": "2021-01-06T21:02:39Z",
                    "modified_date": "2021-01-11T19:34:59Z",
                    "identifiers": ["action_network:44618be7-29cb-439e-bc68-70e6e85dda1b"],
                    "origin_system": "Action Network",
                    "name": "Call your elected officials",
                    "title": "Call your elected officials",
                    "type": "phone",
                    "total_outreaches": 9,
                    "action_network:sponsor": {"title": "Progressive Action Now"},
                    "action_network:hidden": False,
                    "_links": {
                        "curies": [
                            {
                                "name": "osdi",
                                "href": "https://actionnetwork.org/docs/v2/{rel}",
                                "templated": True,
                            },
                            {
                                "name": "action_network",
                                "href": "https://actionnetwork.org/docs/v2/{rel}",
                                "templated": True,
                            },
                        ],
                        "self": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:outreaches": {"href": f"{API_URL}/advocacy_campaigns/fake_url"},
                        "osdi:creator": {"href": f"{API_URL}/people/fake_url"},
                        "osdi:record_outreach_helper": {
                            "href": f"{API_URL}/advocacy_campaigns/fake_url"
                        },
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_advocacy_campaign() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-21T23:39:53Z",
        "modified_date": "2014-03-25T15:26:45Z",
        "title": "Thank Acme's CEO for going green",
        "description": "<p>Write a letter today!</p>",
        "browser_url": "https://actionnetwork.org/letters/thanks-acme",
        "featured_image_url": "https://actionnetwork.org/images/acme.jpg",
        "targets": "Acme CEO",
        "type": "email",
        "total_outreaches": 6,
        "action_network:hidden": True,
        "_embedded": {
            "osdi:creator": {
                "given_name": "John",
                "family_name": "Doe",
                "identifiers": ["action_network:fake_id"],
                "created_date": "2014-03-24T18:03:45Z",
                "modified_date": "2014-03-25T15:00:22Z",
                "email_addresses": [
                    {
                        "primary": True,
                        "address": "jdoe@mail.com",
                        "status": "subscribed",
                    }
                ],
                "phone_numbers": [
                    {
                        "primary": True,
                        "number": "12021234444",
                        "number_type": "Mobile",
                        "status": "subscribed",
                    }
                ],
                "postal_addresses": [
                    {
                        "primary": True,
                        "address_lines": ["1600 Pennsylvania Ave"],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 32.934,
                            "longitude": -72.0377,
                            "accuracy": "Approximate",
                        },
                    }
                ],
                "languages_spoken": ["en"],
                "_links": {
                    "self": {"href": f"{API_URL}/people/fake_id"},
                    "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                    "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                    "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                    "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                    "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                    "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    "curies": [
                        {
                            "name": "osdi",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                        {
                            "name": "action_network",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                    ],
                },
            }
        },
        "_links": {
            "self": {"href": f"{API_URL}/advocacy_campaigns/fake_id"},
            "osdi:outreaches": {"href": f"{API_URL}/advocacy_campaigns/fake_id/outreaches"},
            "osdi:record_outreach_helper": {
                "href": f"{API_URL}/advocacy_campaigns/fake_id/outreaches"
            },
            "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
            "action_network:embed": {"href": f"{API_URL}/advocacy_campaigns/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_attendances() -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 25,
        "page": 1,
        "total_records": 20,
        "_links": {
            "self": {"href": f"{API_URL}/events/fake_id/attendances"},
            "osdi:attendance": [
                {"href": f"{API_URL}/events/fake_id/attendances/fake_id"},
                {"href": f"{API_URL}/events/fake_id/attendances/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:attendances": [
                {
                    "identifiers": ["action_network:d51ca19e-9fe9-11e3-a2e9-12313d316c29"],
                    "created_date": "2014-02-18T20:52:59Z",
                    "modified_date": "2014-02-18T20:53:00Z",
                    "status": "accepted",
                    "action_network:person_id": "fake_id",
                    "action_network:event_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/events/fake_id/attendances/fake_id"},
                        "osdi:event": {"href": f"{API_URL}/events/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-02-18T20:23:42Z",
                    "modified_date": "2014-02-18T20:23:42Z",
                    "status": "accepted",
                    "action_network:person_id": "fake_id",
                    "action_network:event_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/events/fake_id/attendances/fake_id"},
                        "osdi:event": {"href": f"{API_URL}/events/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_attendance() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:d51ca19e-9fe9-11e3-a2e9-12313d316c29"],
        "created_date": "2014-02-18T20:52:59Z",
        "modified_date": "2014-02-18T20:53:00Z",
        "status": "accepted",
        "action_network:person_id": "fake_id",
        "action_network:event_id": "fake_id",
        "_links": {
            "self": {"href": f"{API_URL}/events/fake_id/attendances/fake_id"},
            "osdi:event": {"href": f"{API_URL}/events/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_campaigns() -> dict[str, Any]:
    return {
        "total_pages": 2,
        "per_page": 25,
        "page": 1,
        "total_records": 30,
        "_links": {
            "next": {"href": f"{API_URL}/campaigns?page=2"},
            "self": {"href": f"{API_URL}/campaigns"},
            "action_network:campaigns": [
                {"href": f"{API_URL}/campaigns/fake_id"},
                {"href": f"{API_URL}/campaigns/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "action_network:campaigns": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2013-10-02T14:21:32Z",
                    "modified_date": "2013-10-02T14:22:06Z",
                    "title": "Join our week of actions!",
                    "description": "<p>Our week of action is here --"
                    "click the links on the right to join in!</p>",
                    "browser_url": "fake_url",
                    "featured_image_url": "fake_url",
                    "action_network:hidden": False,
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "browser_url": "fake_url",
                    },
                    "actions": [
                        {
                            "title": "Sign the petition",
                            "browser_url": "fake_url",
                        },
                        {
                            "title": "Attend the rally",
                            "browser_url": "fake_url",
                        },
                    ],
                    "_links": {"self": {"href": f"{API_URL}/campaigns/fake_id"}},
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2013-09-30T15:55:44Z",
                    "modified_date": "2014-01-16T19:07:00Z",
                    "title": "Welcome to our Action Center",
                    "description": "<p>Welcome to our Action Center.Take action on the right.</p>",
                    "browser_url": "fake_url",
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "browser_url": "fake_url",
                    },
                    "actions": [
                        {
                            "title": "Sign up for email updates",
                            "browser_url": "fake_url",
                        },
                        {
                            "title": "Take our survey",
                            "browser_url": "fake_url",
                        },
                    ],
                    "_links": {"self": {"href": f"{API_URL}/campaigns/fake_id"}},
                },
            ]
        },
    }


@pytest.fixture
def fake_campaign() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2013-10-02T14:21:32Z",
        "modified_date": "2013-10-02T14:22:06Z",
        "title": "Join our week of actions!",
        "description": "<p>Our week of action is here --"
        "click the links on the right to join in!</p>",
        "browser_url": "https://actionnetwork.org/campaigns/join-our-week-of-action",
        "featured_image_url": "https://actionnetwork.org/images/week-of-action.jpg",
        "action_network:hidden": False,
        "action_network:sponsor": {
            "title": "Progressive Action Now",
            "browser_url": "https://actionnetwork.org/groups/progressive-action-now",
        },
        "actions": [
            {
                "title": "Sign the petition",
                "browser_url": "https://actionnetwork.org/petitions/sign-the-petition",
            },
            {
                "title": "Attend the rally",
                "browser_url": "https://actionnetwork.org/events/attend-the-rally",
            },
        ],
        "_links": {
            "self": {"href": f"{API_URL}/campaigns/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_custom_fields() -> dict[str, Any]:
    return {
        "origin_system": "Action Network",
        "name": "Custom Fields",
        "description": "The collection of custom fields available at this endpoint.",
        "_links": {
            "self": [{"href": "https://dev.actionnetwork.org/api/v2/metadata/custom_fields"}],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://dev.actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://dev.actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "action_network:custom_fields": [
            {
                "name": "employer",
                "created_date": "2020-04-21T18:24:11Z",
                "modified_date": "2020-04-21T18:24:11Z",
                "notes": None,
            },
            {
                "name": "mobile_message_referrer",
                "created_date": "2020-04-22T15:39:25Z",
                "modified_date": "2020-04-22T15:39:25Z",
                "notes": None,
            },
            {
                "name": "occupation",
                "created_date": "2020-04-21T18:25:35Z",
                "modified_date": "2020-04-21T18:25:35Z",
                "notes": None,
            },
            {
                "name": "volunteer",
                "created_date": "2019-09-26T18:06:06Z",
                "modified_date": "2019-09-26T18:06:06Z",
                "notes": None,
            },
        ],
    }


@pytest.fixture
def fake_donations() -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 25,
        "page": 1,
        "total_records": 6,
        "_links": {
            "self": {"href": f"{API_URL}/fundraising_pages/fake_id/donations"},
            "osdi:donations": [
                {"href": f"{API_URL}/fundraising_pages/fake_id/donations/fake_id"},
                {"href": f"{API_URL}/fundraising_pages/fake_id/donations/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "Ttemplated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:donations": [
                {
                    "identifiers": ["action_network:f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16"],
                    "created_date": "2014-03-27T17:42:21Z",
                    "modified_date": "2014-03-27T17:42:24Z",
                    "currency": "USD",
                    "amount": "20.01",
                    "recipients": [
                        {"display_name": "John Doe", "amount": "6.67"},
                        {
                            "display_name": "Progressive Action Now",
                            "amount": "6.67",
                        },
                        {"display_name": "Jane Black", "amount": "6.67"},
                    ],
                    "payment": {
                        "method": "Credit Card",
                        "reference_number": "f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16",
                        "authorization_stored": False,
                    },
                    "action_network:recurrence": {
                        "recurring": True,
                        "period": "Monthly",
                    },
                    "action_network:person_id": "fake_id",
                    "action_network:fundraising_page_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/fundraising_pages/fake_url"},
                        "osdi:fundraising_page": {"href": f"{API_URL}/fake_url"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_url"},
                    },
                },
                {
                    "identifiers": ["action_network:d86538c1-e8f7-46e1-8320-552da81bd48d"],
                    "created_date": "2014-03-27T17:40:56Z",
                    "modified_date": "2014-03-27T17:41:11Z",
                    "currency": "USD",
                    "amount": "20.00",
                    "recipients": [
                        {"display_name": "John Doe", "amount": "10.00"},
                        {
                            "display_name": "Progressive Action Now",
                            "amount": "10.00",
                        },
                    ],
                    "payment": {
                        "method": "Credit Card",
                        "reference_number": "d86538c1-e8f7-46e1-8320-552da81bd48d",
                        "authorization_stored": False,
                    },
                    "action_network:recurrence": {"recurring": False},
                    "action_network:person_id": "fake_id",
                    "action_network:fundraising_page_id": "fake_id",
                    "_links": {
                        "self": {"href": "fundraising_pages/fake_id/donations/fake_id"},
                        "osdi:fundraising_page": {"href": f"{API_URL}/fundraising_pages/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_donation() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16"],
        "created_date": "2014-03-27T17:42:21Z",
        "modified_date": "2014-03-27T17:42:24Z",
        "currency": "USD",
        "amount": "20.01",
        "recipients": [
            {"display_name": "John Doe", "amount": "6.67"},
            {"display_name": "Progressive Action Now", "amount": "6.67"},
            {"display_name": "Jane Black", "amount": "6.67"},
        ],
        "payment": {
            "method": "Credit Card",
            "reference_number": "f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16",
            "authorization_stored": False,
        },
        "action_network:recurrence": {"recurring": True, "period": "Monthly"},
        "action_network:person_id": "fake_id",
        "action_network:fundraising_page_id": "fake_id",
        "_links": {
            "self": {"href": f"{API_URL}/fundraising_pages/fake_id/donations/fake_id"},
            "osdi:fundraising_page": {"href": f"{API_URL}/fundraising_pages/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_embed() -> dict[str, Any]:
    return {
        "embed_standard_default_styles": "<link href='fake_url'"
        " rel='stylesheet' type='text/css' /><script "
        "src='https://actionnetwork.org/widgets/event/my-free-event?"
        "format=js&source=widget'></script><div id='can-event-area-my-free-event'"
        " style='width: 100%'><!-- this div is the target for our HTML insertion -->"
        "</div>",
        "embed_standard_layout_only_styles": "<link href='√"
        "-whitelabel.css' rel='stylesheet' type='text/css' "
        "/><script"
        " src='fake_url"
        "ent?format=js&source=widget'>"
        "</script><div id='can-event-area-my-free-event'"
        " style='width: undefined'>"
        "<!-- this div is the target for our HTML insertion --></div>",
        "embed_standard_no_styles": "<script src='fake_url"
        "&source=widget'></script>"
        "<div id='can-event-area-my-free-event' "
        "style='width: undefined'>"
        "<!-- this div is "
        "the target for our HTML insertion --></div>",
        "embed_full_default_styles": "<link href='fake_url' rel='stylesheet'"
        " type='text/css' /><script src='fake_url"
        "/event/my-free-event?format=js&source=widget&style=full'></script>"
        "<div id='can-event-area-my-free-event' style='width: undefined'>"
        "<!-- this div is the target for our HTML insertion --></div>",
        "embed_full_layout_only_styles": "<link href='fake_url' "
        "rel='stylesheet' type='text/css' /><script "
        "src='fake_url"
        "&source=widget&style=full'>"
        "</script><div id='can-event-area-my-free-event'"
        " style='width: undefined'>"
        "<!-- this div is the target for our HTML insertion -->"
        "</div>",
        "embed_full_no_styles": "<script src='fake_url'"
        "&source=widget&style=full'></script><div id='can-event-area-my-free-event' "
        "style='width: undefined'><!-- this div is the target for our HTML insertion -->"
        "</div>",
        "_links": {
            "self": {"href": f"{API_URL}/events/21789f03-0180-45d3-853c-91bd6fdc8c07/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_event_campaigns() -> dict[str, Any]:
    return {
        "total_pages": 10,
        "per_page": 25,
        "page": 1,
        "total_records": 237,
        "_links": {
            "next": {"href": f"{API_URL}/event_campaigns?page=2"},
            "self": {"href": f"{API_URL}/event_campaigns"},
            "action_network:event_campaigns": [
                {"href": f"{API_URL}/event_campaigns/fake_id"},
                {"href": f"{API_URL}/event_campaigns/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "action_network:event_campaigns": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-07T16:50:29Z",
                    "modified_date": "2014-03-07T16:51:16Z",
                    "title": "House parties to help us win!",
                    "description": "<p>Host house parties next "
                    "week to help us win our campaign!</p>",
                    "host_pitch": "Hosting a house party is easy! Sign up and we'll give "
                    "you what you need to know.",
                    "host_instructions": "<p>Download our toolkit for all the "
                    "instructions you need to host an event.</p>",
                    "browser_url": "fake_url",
                    "host_url": "fake_url",
                    "featured_image_url": "fake_url",
                    "total_events": 35,
                    "total_rsvps": 467,
                    "action_network:hidden": False,
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "url": "fake_url",
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/event_campaigns/fake_id"},
                        "osdi:events": {"href": f"{API_URL}/event_campaigns/fake_id/events"},
                        "action_network:embed": {
                            "href": f"{API_URL}/event_campaigns/fake_id/embed"
                        },
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-02-03T16:32:34Z",
                    "modified_date": "2014-02-03T16:42:10Z",
                    "title": "Protest the bad bill in your town",
                    "description": "<p>Help us stop this bad bill from "
                    "becoming law by joining a local protest.</p>",
                    "host_pitch": "Hosting is easy, we'll help you out, do it now!",
                    "host_instructions": "<p>Here's everything you need to host a protest...</p>",
                    "browser_url": "fake_url",
                    "host_url": "fake_url",
                    "total_events": 4,
                    "total_rsvps": 11,
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "url": "fake_url",
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/event_campaigns/fake_id"},
                        "osdi:events": {"href": f"{API_URL}/event_campaigns/fake_id/events"},
                        "action_network:embed": {
                            "href": f"{API_URL}/event_campaigns/fake_id/embed"
                        },
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_event_campaign() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-02-03T16:32:34Z",
        "modified_date": "2014-02-03T16:42:10Z",
        "title": "Protest the bad bill in your town",
        "description": "<p>Help us stop this bad bill from becoming"
        "law by joining a local protest.</p>",
        "host_pitch": "Hosting is easy, we'll help you out, do it now!",
        "host_instructions": "<p>Here's everything you need to host a protest...</p>",
        "browser_url": "fake_url",
        "host_url": "fake_url",
        "featured_image_url": "fake_url",
        "total_events": 4,
        "total_rsvps": 11,
        "action_network:hidden": False,
        "action_network:sponsor": {
            "title": "Progressive Action Now",
            "url": "fake_url",
        },
        "_links": {
            "self": {"href": f"{API_URL}/event_campaigns/fake_id"},
            "osdi:events": {"href": f"{API_URL}/event_campaigns/fake_id/events"},
            "action_network:embed": {"href": f"{API_URL}/event_campaigns/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_events() -> dict[str, Any]:
    return {
        "total_pages": 10,
        "per_page": 25,
        "page": 1,
        "total_records": 250,
        "_links": {
            "next": {"href": f"{API_URL}/events?page=2"},
            "self": {"href": f"{API_URL}/events"},
            "osdi:events": [
                {"href": f"{API_URL}/events/fake_id"},
                {"href": f"{API_URL}/events/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:events": [
                {
                    "origin_system": "FreeEvents.com",
                    "identifiers": [
                        "action_network:fake_id",
                        "free_events:1",
                    ],
                    "status": "confirmed",
                    "created_date": "2014-03-18T22:17:36Z",
                    "modified_date": "2014-03-19T14:07:41Z",
                    "title": "House Party for Justice",
                    "transparence": "opaque",
                    "visibility": "public",
                    "guests_can_invite_others": True,
                    "capacity": 10,
                    "reminders": [{"method": "email", "minutes": 1440}],
                    "total_accepted": 5,
                    "action_network:hidden": False,
                    "location": {
                        "venue": "My House",
                        "address_lines": ["1600 Pennsylvania Ave"],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 33.1037330420451,
                            "longitude": -72.0439414557911,
                            "accuracy": "Rooftop",
                        },
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/events/fake_id"},
                        "osdi:attendances": {"href": f"{API_URL}/events/fake_id/attendances"},
                        "osdi:record_attendance_helper": {
                            "href": f"{API_URL}/events/fake_id/attendances"
                        },
                        "osdi:organizer": {"href": f"{API_URL}/people/fake_id"},
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/events/fake_id/embed"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "status": "confirmed",
                    "created_date": "2014-03-18T21:08:18Z",
                    "modified_date": "2014-03-18T22:15:11Z",
                    "origin_system": "Action Network",
                    "title": "Movie Screening",
                    "description": "<p>Come watch this awesome movie!</p>",
                    "instructions": "<p>Feel free to bring a friend</p>",
                    "browser_url": "https://actionnetwork.org/events/movie-screening",
                    "featured_image_url": "https://actionnetwork.org/images/screening.jpg",
                    "start_date": "2014-03-22T17:45:00Z",
                    "transparence": "opaque",
                    "visibility": "public",
                    "guests_can_invite_others": True,
                    "reminders": [{"method": "email", "minutes": 1440}],
                    "total_accepted": 7,
                    "action_network:hidden": False,
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "browser_url": "fake_url",
                    },
                    "location": {
                        "venue": "My house",
                        "address_lines": ["1600 Pennsylvania Ave"],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 32.9135624691629,
                            "longitude": -76.0487183148486,
                            "accuracy": "Rooftop",
                        },
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/events/fake_id"},
                        "osdi:attendances": {"href": f"{API_URL}/events/fake_id/attendances"},
                        "osdi:record_attendance_helper": {
                            "href": f"{API_URL}/events/fake_id/attendances"
                        },
                        "osdi:organizer": {"href": f"{API_URL}/people/fake_id"},
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/events/fake_id/embed"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_event2() -> dict[str, Any]:
    return {
        "origin_system": "FreeEvents.com",
        "identifiers": [
            "action_network:fake_id",
            "free_events:1",
        ],
        "status": "confirmed",
        "created_date": "2014-03-18T22:17:36Z",
        "modified_date": "2014-03-19T14:07:41Z",
        "title": "House Party for Justice",
        "transparence": "opaque",
        "visibility": "public",
        "guests_can_invite_others": True,
        "capacity": 10,
        "reminders": [{"method": "email", "minutes": 1440}],
        "total_accepted": 5,
        "action_network:hidden": False,
        "location": {
            "venue": "My House",
            "address_lines": ["1600 Pennsylvania Ave"],
            "locality": "Washington",
            "region": "DC",
            "postal_code": "20009",
            "country": "US",
            "language": "en",
            "location": {
                "latitude": 33.1037330420451,
                "longitude": -72.0439414557911,
                "accuracy": "Rooftop",
            },
        },
        "_links": {
            "self": {"href": f"{API_URL}/events/fake_id"},
            "osdi:attendances": {"href": f"{API_URL}/events/fake_id/attendances"},
            "osdi:record_attendance_helper": {"href": f"{API_URL}/events/fake_id/attendances"},
            "osdi:organizer": {"href": f"{API_URL}/people/fake_id"},
            "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
            "action_network:embed": {"href": f"{API_URL}/events/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_forms() -> dict[str, Any]:
    return {
        "total_pages": 10,
        "per_page": 25,
        "page": 1,
        "total_records": 250,
        "_links": {
            "next": {"href": f"{API_URL}/forms?page=2"},
            "self": {"href": f"{API_URL}/forms"},
            "osdi:forms": [
                {"href": f"{API_URL}/forms/65345d7d-cd24-466a-a698-4a7686ef684f"},
                {"href": f"{API_URL}/forms/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:forms": [
                {
                    "origin_system": "FreeForms.com",
                    "identifiers": [
                        "action_network:65345d7d-cd24-466a-a698-4a7686ef684f",
                        "free_forms:1",
                    ],
                    "created_date": "2014-03-25T14:40:07Z",
                    "modified_date": "2014-03-25T14:47:44Z",
                    "title": "Tell your story",
                    "total_submissions": 25,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave"],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 32.935,
                                        "longitude": -73.1338,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_id"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/people/fake_id/attendances"
                                },
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                                "osdi:submissions": {
                                    "href": f"{API_URL}/people/fake_id/submissions"
                                },
                                "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/forms/fake_id"},
                        "osdi:submissions": {"href": f"{API_URL}/forms/fake_id/submissions"},
                        "osdi:record_submission_helper": {
                            "href": f"{API_URL}/forms/fake_id/submissions"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/forms/fake_id/embed"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-21T23:39:53Z",
                    "modified_date": "2014-03-25T15:26:45Z",
                    "title": "Take our end of year survey",
                    "description": "<p>Let us know what you think!</p>",
                    "call_to_action": "Let us know",
                    "browser_url": "https://actionnetwork.org/forms/end-of-year-survey",
                    "featured_image_url": "https://actionnetwork.org/images/survey.jpg",
                    "total_submissions": 6,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 32.934,
                                        "longitude": -74.5319,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_id"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/people/fake_id/attendances"
                                },
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                                "osdi:submissions": {
                                    "href": f"{API_URL}/people/fake_id/submissions"
                                },
                                "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/forms/fake_id"},
                        "osdi:submissions": {"href": f"{API_URL}/forms/fake_id/submissions"},
                        "osdi:record_submission_helper": {
                            "href": f"{API_URL}/forms/fake_id/submissions"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/forms/fake_id/embed"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_form() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-21T23:39:53Z",
        "modified_date": "2014-03-25T15:26:45Z",
        "title": "Take our end of year survey",
        "description": "<p>Let us know what you think!</p>",
        "call_to_action": "Let us know",
        "browser_url": "https://actionnetwork.org/forms/end-of-year-survey",
        "featured_image_url": "https://actionnetwork.org/images/survey.jpg",
        "total_submissions": 6,
        "action_network:hidden": False,
        "_embedded": {
            "osdi:creator": {
                "given_name": "John",
                "family_name": "Doe",
                "identifiers": ["action_network:fake_id"],
                "created_date": "2014-03-24T18:03:45Z",
                "modified_date": "2014-03-25T15:00:22Z",
                "email_addresses": [
                    {
                        "primary": True,
                        "address": "jdoe@mail.com",
                        "status": "subscribed",
                    }
                ],
                "phone_numbers": [
                    {
                        "primary": True,
                        "number": "12021234444",
                        "number_type": "Mobile",
                        "status": "subscribed",
                    }
                ],
                "postal_addresses": [
                    {
                        "primary": True,
                        "address_lines": ["1600 Pennsylvania Ave"],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 32.934,
                            "longitude": -72.0377,
                            "accuracy": "Approximate",
                        },
                    }
                ],
                "languages_spoken": ["en"],
                "_links": {
                    "self": {"href": f"{API_URL}/people/fake_id"},
                    "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                    "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                    "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                    "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                    "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                    "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    "curies": [
                        {
                            "name": "osdi",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                        {
                            "name": "action_network",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                    ],
                },
            }
        },
        "_links": {
            "self": {"href": f"{API_URL}/forms/fake_id"},
            "osdi:submissions": {"href": f"{API_URL}/forms/fake_id/submissions"},
            "osdi:record_submission_helper": {"href": f"{API_URL}/forms/fake_id/submissions"},
            "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
            "action_network:embed": {"href": f"{API_URL}/forms/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_fundraising_pages(fake_tag_id_1: str, fake_date: str) -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 1,
        "page": 1,
        "total_records": 1,
        "_links": {
            "next": {"href": f"{API_URL}/fundraising_pages?page=2"},
            "osdi:fundraising_pages": [
                {"href": f"{API_URL}/fundraising_pages/{fake_tag_id_1}"},
            ],
            "curies": [
                {"name": "osdi", "templated": True},
                {"name": "action_network", "templated": True},
            ],
            "self": {"href": f"{API_URL}/fundraising_pages"},
        },
        "_embedded": {
            "osdi:fundraising_pages": [
                {
                    "identifiers": [""],
                    "created_date": fake_date,
                    "total_donations": 0,
                    "total_amount": "0.00",
                    "currency": "USD",
                    "action_network:sponsor": {"title": "", "browser_url": ""},
                    "_links": {
                        "self": {"href": f"{API_URL}/fundraising_pages"},
                        "osdi:creator": {"href": "fake_url"},
                        "osdi:donations": {"href": "fake_url"},
                        "osdi:record_donation_helper": {"href": "fake_url"},
                    },
                    "modified_date": fake_date,
                    "origin_system": "Test",
                    "title": "Hello",
                    "_embedded": {"osdi:creator": ""},
                    "action_network:hidden": False,
                }
            ]
        },
    }


@pytest.fixture
def fake_fundraising_page() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-04T18:14:03Z",
        "modified_date": "2014-03-24T16:07:13Z",
        "title": "Year end fundraising",
        "description": "<p>Donate today!</p>",
        "browser_url": "https://actionnetwork.org/fundraising/year-end-fundraising-2",
        "featured_image_url": "https://actionnetwork.org/images/donate.jpg",
        "total_donations": 5,
        "total_amount": "302.14",
        "currency": "USD",
        "action_network:hidden": False,
        "_embedded": {
            "osdi:creator": {
                "given_name": "John",
                "family_name": "Doe",
                "identifiers": ["action_network:fake_id"],
                "created_date": "2014-03-24T19:39:40Z",
                "modified_date": "2014-03-24T19:48:23Z",
                "email_addresses": [
                    {
                        "primary": True,
                        "address": "jdoe@mail.com",
                        "status": "subscribed",
                    }
                ],
                "phone_numbers": [
                    {
                        "primary": True,
                        "number": "12021234444",
                        "number_type": "Mobile",
                        "status": "subscribed",
                    }
                ],
                "postal_addresses": [
                    {
                        "primary": True,
                        "address_lines": ["1600 Pennsylvania Ave"],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 32.945,
                            "longitude": -76.3477,
                            "accuracy": "Approximate",
                        },
                    }
                ],
                "languages_spoken": ["en"],
                "_links": {
                    "self": {"href": f"{API_URL}/people/fake_id"},
                    "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                    "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                    "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                    "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                    "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                    "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    "curies": [
                        {
                            "name": "osdi",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                        {
                            "name": "action_network",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                    ],
                },
            }
        },
        "action_network:sponsor": {
            "title": "Progressive Action Now",
            "url": "https://actionnetwork.org/groups/progressive-action-now",
        },
        "_links": {
            "self": {"href": f"{API_URL}/fundraising_pages/fake_id"},
            "osdi:donations": {"href": f"{API_URL}/fundraising_pages/fake_id/donations"},
            "osdi:record_donation_helper": {
                "href": f"{API_URL}/fundraising_pages/fake_id/donations"
            },
            "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
            "action_network:embed": {"href": f"{API_URL}/fundraising_pages/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_items() -> dict[str, Any]:
    return {
        "per_page": 25,
        "page": 1,
        "_links": {
            "next": {"href": f"{API_URL}/lists/fake_id/items?page=2"},
            "self": {"href": f"{API_URL}/lists/fake_id/items"},
            "osdi:items": [
                {"href": f"{API_URL}/lists/fake_id/items/fake_id"},
                {"href": f"{API_URL}/lists/fake_id/items/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:items": [
                {
                    "_links": {
                        "self": {"href": f"{API_URL}/lists/fake_id/items/fake_id"},
                        "osdi:list": {"href": f"{API_URL}/lists/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-18T22:25:31Z",
                    "modified_date": "2014-03-18T22:25:38Z",
                    "item_type": "osdi:person",
                    "action_network:person_id": "fake_id",
                    "action_network:list_id": "fake_id",
                },
                {
                    "_links": {
                        "self": {"href": f"{API_URL}/lists/fake_id/items/fake_id"},
                        "osdi:list": {"href": f"{API_URL}/lists/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-18T22:24:24Z",
                    "modified_date": "2014-03-18T22:24:24Z",
                    "item_type": "osdi:person",
                    "action_network:person_id": "fake_id",
                    "action_network:list_id": "fake_id",
                },
            ]
        },
    }


@pytest.fixture
def fake_item() -> dict[str, Any]:
    return {
        "_links": {
            "self": {"href": f"{API_URL}/lists/fake_id/items/fake_id"},
            "osdi:list": {"href": f"{API_URL}/lists/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-18T22:25:31Z",
        "modified_date": "2014-03-18T22:25:38Z",
        "item_type": "osdi:person",
        "action_network:person_id": "fake_id",
        "action_network:list_id": "fake_id",
    }


@pytest.fixture
def fake_lists() -> dict[str, Any]:
    return {
        "total_pages": 10,
        "per_page": 25,
        "page": 1,
        "total_records": 243,
        "_links": {
            "next": {"href": f"{API_URL}/lists?page=2"},
            "self": {"href": f"{API_URL}/lists"},
            "osdi:lists": [
                {"href": f"{API_URL}/lists/fake_id"},
                {"href": f"{API_URL}/lists/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:lists": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-25T17:11:33Z",
                    "modified_date": "2014-03-25T17:13:33Z",
                    "title": "Stop Doing The Bad Thing Petition Signers",
                    "description": "Report",
                    "browser_url": "fake_url",
                    "_links": {
                        "self": {"href": f"{API_URL}/lists/fake_id"},
                        "osdi:items": {"href": f"{API_URL}/lists/fake_id/items"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:26:42Z",
                    "modified_date": "2014-03-24T18:27:17Z",
                    "title": "Sign our new petition!",
                    "description": "Email",
                    "browser_url": "fake_url",
                    "_links": {
                        "self": {"href": f"{API_URL}/lists/fake_id"},
                        "osdi:items": {"href": f"{API_URL}/lists/fake_id/items"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_list() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-03-25T17:11:33Z",
        "modified_date": "2014-03-25T17:13:33Z",
        "title": "Stop Doing The Bad Thing Petition Signers",
        "description": "Report",
        "browser_url": "fake_url",
        "_links": {
            "self": {"href": f"{API_URL}/lists/fake_id"},
            "osdi:items": {"href": f"{API_URL}/lists/fake_id/items"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_messages() -> dict[str, Any]:
    return {
        "total_pages": 7,
        "per_page": 25,
        "page": 1,
        "total_records": 162,
        "_links": {
            "next": {"href": f"{API_URL}/messages?page=2"},
            "self": {"href": f"{API_URL}/messages"},
            "osdi:messages": [
                {"href": f"{API_URL}/messages/fake_id"},
                {"href": f"{API_URL}/messages/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:messages": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:03:45Z",
                    "modified_date": "2014-03-25T15:00:22Z",
                    "subject": "Stop doing the bad thing",
                    "body": "<p>The mayor should stop doing the bad thing.</p>",
                    "from": "Progressive Action Now",
                    "reply_to": "jane@progressiveactionnow.org",
                    "administrative_url": "fake_url",
                    "total_targeted": 2354,
                    "status": "sent",
                    "sent_start_date": "2014-03-26T15:00:22Z",
                    "type": "email",
                    "targets": [{"href": f"{API_URL}/queries/fake_id"}],
                    "statistics": {
                        "sent": 2354,
                        "opened": 563,
                        "clicked": 472,
                        "actions": 380,
                        "action_network:donated": 14,
                        "action_network:total_amount": 320.25,
                        "unsubscribed": 12,
                        "bounced": 2,
                        "spam_reports": 1,
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/messages/fake_id"},
                        "osdi:wrapper": {"href": f"{API_URL}/wrappers/fake_id"},
                        "osdi:recipients": {
                            "href": f"{API_URL}/lists/950e9954-606f-43e6-be99-2bc0bc2072a1"
                        },
                        "osdi:send_helper": {"href": f"{API_URL}/messages/fake_id/send"},
                        "osdi:schedule_helper": {"href": f"{API_URL}/messages/fake_id/schedule"},
                    },
                },
                {
                    "identifiers": [
                        "action_network:fake_id",
                        "foreign_system:1",
                    ],
                    "origin_system": "My Email Making System",
                    "created_date": "2014-03-27T18:03:45Z",
                    "modified_date": "2014-03-28T15:00:22Z",
                    "subject": "FWD: Stop doing the bad thing",
                    "body": "<p>Have you signed yet? "
                    "The mayor should stop doing the bad thing.</p>",
                    "from": "Progressive Action Now",
                    "reply_to": "jane@progressiveactionnow.org",
                    "administrative_url": "fake_url",
                    "total_targeted": 12673,
                    "status": "draft",
                    "type": "email",
                    "targets": [],
                    "_links": {
                        "self": {"href": f"{API_URL}/messages/fake_id"},
                        "osdi:send_helper": {"href": f"{API_URL}/messages/fake_id/send"},
                        "osdi:schedule_helper": {"href": f"{API_URL}/messages/fake_id/schedule"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_message() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-03-24T18:03:45Z",
        "modified_date": "2014-03-25T15:00:22Z",
        "subject": "Stop doing the bad thing",
        "body": "<p>The mayor should stop doing the bad thing.</p>",
        "from": "Progressive Action Now",
        "reply_to": "jane@progressiveactionnow.org",
        "administrative_url": "fake_url",
        "total_targeted": 2354,
        "status": "sent",
        "sent_start_date": "2014-03-26T15:00:22Z",
        "type": "email",
        "targets": [{"href": f"{API_URL}/queries/fake_id"}],
        "statistics": {
            "sent": 2354,
            "opened": 563,
            "clicked": 472,
            "actions": 380,
            "action_network:donated": 14,
            "action_network:total_amount": 320.25,
            "unsubscribed": 12,
            "bounced": 2,
            "spam_reports": 1,
        },
        "_links": {
            "self": {"href": f"{API_URL}/messages/fake_id"},
            "osdi:wrapper": {"href": f"{API_URL}/wrappers/fake_id"},
            "osdi:recipients": {"href": f"{API_URL}/lists/950e9954-606f-43e6-be99-2bc0bc2072a1"},
            "osdi:send_helper": {"href": f"{API_URL}/messages/fake_id/send"},
            "osdi:schedule_helper": {"href": f"{API_URL}/messages/fake_id/schedule"},
        },
    }


@pytest.fixture
def fake_metadata() -> dict[str, Any]:
    return {
        "name": "Action Network",
        "_links": {
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://dev.actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://dev.actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
            "self": {"href": "https://dev.actionnetwork.org/api/v2/metadata"},
            "action_network:custom_fields": {
                "href": "https://dev.actionnetwork.org/api/v2/metadata/custom_fields"
            },
        },
    }


@pytest.fixture
def fake_outreaches() -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 25,
        "page": 1,
        "total_records": 6,
        "_links": {
            "self": {"href": f"{API_URL}/advocacy_campaigns/fake_id/outreaches"},
            "osdi:outreaches": [
                {"href": f"{API_URL}/advocacy_campaigns/fake_id/outreaches/fake_id"},
                {"href": f"{API_URL}/advocacy_campaigns/fake_id/outreaches/dfake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:outreaches": [
                {
                    "identifiers": ["action_network:f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16"],
                    "created_date": "2014-03-27T17:42:21Z",
                    "modified_date": "2014-03-27T17:42:24Z",
                    "type": "email",
                    "subject": "Please vote no!",
                    "message": "Please vote no on bill 12345.",
                    "targets": [
                        {
                            "title": "Representative",
                            "given_name": "Jill",
                            "family_name": "Black",
                            "ocdid": "ocd-division/country:us/state:ny/cd:18",
                        }
                    ],
                    "action_network:person_id": "fake_id",
                    "action_network:advocacy_campaign_id": "fake_id",
                    "_links": {
                        "self": {"href": "/advocacy_campaigns/fake_id/outreaches/fake_id"},
                        "osdi:advocacy_campaign": {"href": f"{API_URL}/advocacy_campaigns/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
                {
                    "identifiers": ["action_network:d86538c1-e8f7-46e1-8320-552da81bd48d"],
                    "created_date": "2014-03-27T17:40:56Z",
                    "modified_date": "2014-03-27T17:41:11Z",
                    "type": "email",
                    "subject": "Don't do it!",
                    "message": "Please vote no on this bill!",
                    "targets": [
                        {
                            "title": "Representative",
                            "given_name": "Liam",
                            "family_name": "Hoover",
                            "ocdid": "ocd-division/country:us/state:ca/sldl:110",
                        }
                    ],
                    "action_network:person_id": "fake_id",
                    "action_network:advocacy_campaign_id": "fake_id",
                    "_links": {
                        "self": {"href": "advocacy_campaigns/fake_id/outreaches/fake_id"},
                        "osdi:advocacy_campaign": {"href": f"{API_URL}/advocacy_campaigns/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_outreach() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:f1119c4e-b8ca-44ff-bfa7-f78f7ca3ec16"],
        "created_date": "2014-03-27T17:42:21Z",
        "modified_date": "2014-03-27T17:42:24Z",
        "type": "email",
        "subject": "Please vote no!",
        "message": "Please vote no on bill 12345.",
        "targets": [
            {
                "title": "Representative",
                "given_name": "Jill",
                "family_name": "Black",
                "ocdid": "ocd-division/country:us/state:ny/cd:18",
            }
        ],
        "action_network:person_id": "fake_id",
        "action_network:advocacy_campaign_id": "fake_id",
        "_links": {
            "self": {"href": f"{API_URL}/fundraising_page/fake_id/outreaches/fake_id"},
            "osdi:advocacy_campaign": {"href": f"{API_URL}/advocacy_campaigns/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_people() -> dict[str, Any]:
    return {
        "per_page": 25,
        "page": 1,
        "_links": {
            "next": {"href": f"{API_URL}/people?page=2"},
            "osdi:people": [
                {"href": f"{API_URL}/people/fake_id"},
                {"href": f"{API_URL}/people/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
            "self": {"href": f"{API_URL}/people"},
        },
        "_embedded": {
            "osdi:people": [
                {
                    "given_name": "John",
                    "family_name": "Smith",
                    "identifiers": [
                        "action_network:fake_id",
                        "foreign_system:1",
                    ],
                    "created_date": "2014-03-20T21:04:31Z",
                    "modified_date": "2014-03-20T21:04:31Z",
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": "johnsmith@mail.com",
                            "status": "subscribed",
                        }
                    ],
                    "phone_numbers": [
                        {
                            "primary": True,
                            "number": "12024444444",
                            "number_type": "Mobile",
                            "status": "subscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "address_lines": ["1900 Pennsylvania Ave"],
                            "locality": "Washington",
                            "region": "DC",
                            "postal_code": "20009",
                            "country": "US",
                            "language": "en",
                            "location": {
                                "latitude": 38.919,
                                "longitude": -77.0379,
                                "accuracy": "Approximate",
                            },
                        }
                    ],
                    "languages_spoken": ["en"],
                    "custom_fields": {
                        "phone": "310.753.8209",
                        "I am a parent": "1",
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/people/fake_id"},
                        "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    },
                },
                {
                    "given_name": "Jane",
                    "family_name": "Doe",
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-20T20:44:13Z",
                    "modified_date": "2014-03-20T20:44:13Z",
                    "email_addresses": [
                        {
                            "primary": True,
                            "address": "janedoe@mail.com",
                            "status": "unsubscribed",
                        }
                    ],
                    "phone_numbers": [
                        {
                            "primary": True,
                            "number_type": "Mobile",
                            "status": "unsubscribed",
                        }
                    ],
                    "postal_addresses": [
                        {
                            "primary": True,
                            "locality": "Washington",
                            "region": "DC",
                            "postal_code": "20009",
                            "country": "US",
                            "language": "en",
                            "location": {
                                "latitude": 38.919,
                                "longitude": -77.0379,
                                "accuracy": "Approximate",
                            },
                        }
                    ],
                    "languages_spoken": ["en"],
                    "_links": {
                        "self": {"href": f"{API_URL}/people/fake_id"},
                        "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_petitions() -> dict[str, Any]:
    return {
        "total_pages": 7,
        "per_page": 25,
        "page": 1,
        "total_records": 162,
        "_links": {
            "next": {"href": f"{API_URL}/petitions?page=2"},
            "self": {"href": f"{API_URL}/petitions"},
            "osdi:petitions": [
                {"href": f"{API_URL}/petitions/fake_id"},
                {"href": f"{API_URL}/petitions/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:petitions": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:03:45Z",
                    "modified_date": "2014-03-25T15:00:22Z",
                    "title": "Stop doing the bad thing",
                    "description": "<p>The mayor should stop doing the bad.</p>",
                    "petition_text": "Mayor, stop doing the bad thing",
                    "browser_url": "fake_url",
                    "featured_image_url": "fake_url",
                    "total_signatures": 2354,
                    "target": [{"name": "The Mayor"}],
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 35.919,
                                        "longitude": -72.0379,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_id"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/people/fake_id/attendances"
                                },
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                                "osdi:submissions": {
                                    "href": f"{API_URL}/people/fake_id/submissions"
                                },
                                "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/petitions/fake_id"},
                        "osdi:signatures": {"href": f"{API_URL}/petitions/fake_id/signatures"},
                        "osdi:record_signature_helper": {
                            "href": f"{API_URL}/petitions/fake_id/signatures"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/petitions/fake_id/embed"},
                    },
                },
                {
                    "identifiers": [
                        "action_network:fake_id",
                        "foreign_system:1",
                    ],
                    "origin_system": "Another System",
                    "created_date": "2014-03-14T15:21:05Z",
                    "modified_date": "2014-03-17T19:56:11Z",
                    "title": "We need to do this now!",
                    "total_signatures": 123,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:fake_id"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 35.919,
                                        "longitude": -72.0379,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/people/fake_id"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/people/fake_id/attendances"
                                },
                                "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                                "osdi:submissions": {
                                    "href": f"{API_URL}/people/fake_id/submissions"
                                },
                                "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                                "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                                "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                            },
                        }
                    },
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "url": "https://actionnetwork.org/groups/progressive-action-now",
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/petitions/fake_id"},
                        "osdi:signatures": {"href": f"{API_URL}/petitions/fake_id/signatures"},
                        "osdi:record_signature_helper": {
                            "href": f"{API_URL}/petitions/fake_id/signatures"
                        },
                        "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
                        "action_network:embed": {"href": f"{API_URL}/petitions/fake_id/embed"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_petition() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-03-24T18:03:45Z",
        "modified_date": "2014-03-25T15:00:22Z",
        "title": "Stop doing the bad thing",
        "description": "<p>The mayor should stop doing the bad.</p>",
        "petition_text": "Mayor, stop doing the bad thing",
        "browser_url": "https://actionnetwork.org/petitions/stop-doing-the-bad-thing",
        "featured_image_url": "https://actionnetwork.org/images/stop-doing-the-bad-thing.jpg",
        "total_signatures": 2354,
        "target": [{"name": "The Mayor"}],
        "action_network:hidden": False,
        "_embedded": {
            "osdi:creator": {
                "given_name": "John",
                "family_name": "Doe",
                "identifiers": ["action_network:fake_id"],
                "origin_system": "Action Network",
                "created_date": "2014-03-24T18:03:45Z",
                "modified_date": "2014-03-25T15:00:22Z",
                "email_addresses": [
                    {
                        "primary": True,
                        "address": "jdoe@mail.com",
                        "status": "subscribed",
                    }
                ],
                "phone_numbers": [
                    {
                        "primary": True,
                        "number": "12021234444",
                        "number_type": "Mobile",
                        "status": "subscribed",
                    }
                ],
                "postal_addresses": [
                    {
                        "primary": True,
                        "address_lines": ["1600 Pennsylvania Ave."],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 35.919,
                            "longitude": -72.0379,
                            "accuracy": "Approximate",
                        },
                    }
                ],
                "languages_spoken": ["en"],
                "_links": {
                    "self": {"href": f"{API_URL}/people/fake_id"},
                    "osdi:attendances": {"href": f"{API_URL}/people/fake_id/attendances"},
                    "osdi:signatures": {"href": f"{API_URL}/people/fake_id/signatures"},
                    "osdi:submissions": {"href": f"{API_URL}/people/fake_id/submissions"},
                    "osdi:donations": {"href": f"{API_URL}/people/fake_id/donations"},
                    "osdi:outreaches": {"href": f"{API_URL}/people/fake_id/outreaches"},
                    "osdi:taggings": {"href": f"{API_URL}/people/fake_id/taggings"},
                    "curies": [
                        {
                            "name": "osdi",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                        {
                            "name": "action_network",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                    ],
                },
            }
        },
        "_links": {
            "self": {"href": f"{API_URL}/petitions/fake_id"},
            "osdi:signatures": {"href": f"{API_URL}/petitions/fake_id/signatures"},
            "osdi:record_signature_helper": {"href": f"{API_URL}/petitions/fake_id/signatures"},
            "osdi:creator": {"href": f"{API_URL}/people/fake_id"},
            "action_network:embed": {"href": f"{API_URL}/petitions/fake_id/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_queries() -> dict[str, Any]:
    return {
        "total_pages": 7,
        "per_page": 25,
        "page": 1,
        "total_records": 162,
        "_links": {
            "next": {"href": f"{API_URL}/queries?page=2"},
            "self": {"href": f"{API_URL}/queries"},
            "osdi:queries": [
                {"href": f"{API_URL}/queries/fake_id"},
                {"href": f"{API_URL}/queries/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:queries": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:03:45Z",
                    "modified_date": "2014-03-25T15:00:22Z",
                    "name": "All donors",
                    "browser_url": "https://actionnetwork.org/queries/1/edit",
                    "_links": {"self": {"href": f"{API_URL}/queries/fake_id"}},
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-14T15:21:05Z",
                    "modified_date": "2014-03-17T19:56:11Z",
                    "name": "Volunteer prospects",
                    "browser_url": "https://actionnetwork.org/queries/2/edit",
                    "_links": {"self": {"href": f"{API_URL}/queries/fake_id"}},
                },
            ]
        },
    }


@pytest.fixture
def fake_query() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-03-24T18:03:45Z",
        "modified_date": "2014-03-25T15:00:22Z",
        "name": "All donors",
        "browser_url": "https://actionnetwork.org/queries/1/edit",
        "_links": {
            "self": {"href": f"{API_URL}/queries/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_signatures() -> dict[str, Any]:
    return {
        "total_pages": 100,
        "per_page": 25,
        "page": 1,
        "total_records": 2500,
        "_links": {
            "self": {"href": f"{API_URL}/petitions/fake_id/signatures"},
            "osdi:signatures": [
                {"href": f"{API_URL}/petitions/fake_id/signatures/fake_id"},
                {"href": f"{API_URL}/petitions/fake_id/signatures/fake_id`"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:signatures": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-26T18:04:00Z",
                    "modified_date": "2014-03-26T18:04:00Z",
                    "action_network:person_id": "699da712-929f-11e3-a2e9-12313d316c29",
                    "action_network:petition_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/petitions/fake_id/signatures/fake_id"},
                        "osdi:petition": {"href": f"{API_URL}/petitions/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
                {
                    "identifiers": ["action_network:71497ab2-b3e7-4896-af46-126ac7287dab"],
                    "created_date": "2014-03-26T16:07:10Z",
                    "modified_date": "2014-03-26T16:07:10Z",
                    "comments": "Stop doing the thing",
                    "action_network:person_id": "fake_id",
                    "action_network:petition_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/petitions/fake_id/signatures/fake_id"},
                        "osdi:petition": {"href": f"{API_URL}/petitions/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_signature() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-26T18:04:00Z",
        "modified_date": "2014-03-26T18:04:00Z",
        "action_network:person_id": "699da712-929f-11e3-a2e9-12313d316c29",
        "action_network:petition_id": "fake_id",
        "comments": "Stop doing the thing",
        "_links": {
            "self": {"href": f"{API_URL}/petitions/fake_id/signatures/fake_id"},
            "osdi:petition": {"href": f"{API_URL}/petitions/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/699da712-929f-11e3-a2e9-12313d316c29"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_submissions() -> dict[str, Any]:
    return {
        "total_pages": 1,
        "per_page": 25,
        "page": 1,
        "total_records": 4,
        "_links": {
            "self": {"href": f"{API_URL}/forms/fake_id/submissions"},
            "osdi:submissions": [
                {"href": f"{API_URL}/forms/fake_id/submissions/fake_id"},
                {"href": f"{API_URL}/forms/fake_id/submissions/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:submissions": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-25T15:26:45Z",
                    "modified_date": "2014-03-25T15:26:46Z",
                    "action:person_id": "fake_id",
                    "action_network:form_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/forms/fake_id/submissions/fake_id"},
                        "osdi:form": {"href": f"{API_URL}/forms/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
                {
                    "identifiers": [
                        "action_network:fake_id",
                        "free_forms:1",
                    ],
                    "created_date": "2014-03-24T17:00:42Z",
                    "modified_date": "2014-03-24T17:00:42Z",
                    "action:person_id": "fake_id",
                    "action_network:form_id": "fake_id",
                    "_links": {
                        "self": {"href": f"{API_URL}/forms/fake_id/submissions/fake_id"},
                        "osdi:form": {"href": f"{API_URL}/forms/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_submission() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-25T15:26:45Z",
        "modified_date": "2014-03-25T15:26:46Z",
        "action:person_id": "fake_id",
        "action_network:form_id": "fake_id",
        "_links": {
            "self": {"href": f"{API_URL}/forms/fake_id/submissions/fake_id"},
            "osdi:form": {"href": f"{API_URL}/forms/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_surveys() -> dict[str, Any]:
    return {
        "total_pages": 7,
        "per_page": 25,
        "page": 1,
        "total_records": 162,
        "_links": {
            "next": {"href": f"{API_URL}/surveys?page=2"},
            "self": {"href": f"{API_URL}/surveys"},
            "action_network:surveys": [
                {"href": f"{API_URL}/surveys/123"},
                {"href": f"{API_URL}/surveys/123"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "action_network:surveys": [
                {
                    "identifiers": ["action_network:123"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:03:45Z",
                    "modified_date": "2014-03-25T15:00:22Z",
                    "title": "Tell us about yourself!",
                    "description": "<p>Tell us a bit more about yourself.</p>",
                    "call_to_action": "Let us know",
                    "browser_url": "https://actionnetwork.org/surveys/my-survey",
                    "featured_image_url": "https://actionnetwork.org/images/my-image.jpg",
                    "total_responses": 2354,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:123"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 35.919,
                                        "longitude": -72.0379,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/api/v2/people/123"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/api/v2/people/123/attendances"
                                },
                                "osdi:signatures": {
                                    "href": f"{API_URL}/api/v2/people/123/signatures"
                                },
                                "osdi:submissions": {
                                    "href": f"{API_URL}/api/v2/people/123/submissions"
                                },
                                "osdi:donations": {
                                    "href": f"{API_URL}/api/v2/people/123/donations"
                                },
                                "osdi:outreaches": {
                                    "href": f"{API_URL}/api/v2/people/123/outreaches"
                                },
                                "osdi:taggings": {"href": f"{API_URL}/api/v2/people/123/taggings"},
                                "action_network:responses": {
                                    "href": f"{API_URL}/api/v2/people/123/responses"
                                },
                            },
                        }
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/api/v2/surveys/123"},
                        "action_network:responses": {
                            "href": f"{API_URL}/api/v2/surveys/123/responses"
                        },
                        "action_network:record_response_helper": {
                            "href": f"{API_URL}/api/v2/surveys/123/responses"
                        },
                        "osdi:creator": {"href": f"{API_URL}/api/v2/people/123"},
                        "action_network:embed": {"href": f"{API_URL}/api/v2/surveys/123/embed"},
                    },
                },
                {
                    "identifiers": ["action_network:123", "foreign_system:1"],
                    "origin_system": "Another System",
                    "created_date": "2014-03-14T15:21:05Z",
                    "modified_date": "2014-03-17T19:56:11Z",
                    "title": "Volunteer survey",
                    "total_responses": 123,
                    "action_network:hidden": False,
                    "_embedded": {
                        "osdi:creator": {
                            "given_name": "John",
                            "family_name": "Doe",
                            "identifiers": ["action_network:123"],
                            "created_date": "2014-03-24T18:03:45Z",
                            "modified_date": "2014-03-25T15:00:22Z",
                            "email_addresses": [
                                {
                                    "primary": True,
                                    "address": "jdoe@mail.com",
                                    "status": "subscribed",
                                }
                            ],
                            "phone_numbers": [
                                {
                                    "primary": True,
                                    "number": "12021234444",
                                    "number_type": "Mobile",
                                    "status": "subscribed",
                                }
                            ],
                            "postal_addresses": [
                                {
                                    "primary": True,
                                    "address_lines": ["1600 Pennsylvania Ave."],
                                    "locality": "Washington",
                                    "region": "DC",
                                    "postal_code": "20009",
                                    "country": "US",
                                    "language": "en",
                                    "location": {
                                        "latitude": 35.919,
                                        "longitude": -72.0379,
                                        "accuracy": "Approximate",
                                    },
                                }
                            ],
                            "languages_spoken": ["en"],
                            "_links": {
                                "self": {"href": f"{API_URL}/api/v2/people/123"},
                                "osdi:attendances": {
                                    "href": f"{API_URL}/api/v2/people/123/attendances"
                                },
                                "osdi:signatures": {
                                    "href": f"{API_URL}/api/v2/people/123/signatures"
                                },
                                "osdi:submissions": {
                                    "href": f"{API_URL}/api/v2/people/123/submissions"
                                },
                                "osdi:donations": {
                                    "href": f"{API_URL}/api/v2/people/123/donations"
                                },
                                "osdi:outreaches": {
                                    "href": f"{API_URL}/api/v2/people/123/outreaches"
                                },
                                "osdi:taggings": {"href": f"{API_URL}/api/v2/people/123/taggings"},
                                "action_network:responses": {
                                    "href": f"{API_URL}/api/v2/people/123/responses"
                                },
                            },
                        }
                    },
                    "action_network:sponsor": {
                        "title": "Progressive Action Now",
                        "url": f"{API_URL}/groups/progressive-action-now",
                    },
                    "_links": {
                        "self": {"href": f"{API_URL}/api/v2/surveys/123"},
                        "action_network:responses": {
                            "href": f"{API_URL}/api/v2/surveys/123/responses"
                        },
                        "action_network:record_response_helper": {
                            "href": f"{API_URL}/api/v2/surveys/123/respnoses"
                        },
                        "osdi:creator": {"href": f"{API_URL}/api/v2/people/123"},
                        "action_network:embed": {"href": f"{API_URL}/api/v2/surveys/123/embed"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_survey() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:123"],
        "origin_system": "Action Network",
        "created_date": "2014-03-24T18:03:45Z",
        "modified_date": "2014-03-25T15:00:22Z",
        "title": "Tell us about yourself",
        "description": "<p>Tell us a bit more about yourself.</p>",
        "call_to_action": "Let us know",
        "browser_url": "https://actionnetwork.org/surveys/tell-us-about-yourself",
        "featured_image_url": "https://actionnetwork.org/images/tell-us-about-yourself.jpg",
        "total_responses": 2354,
        "action_network:hidden": False,
        "_embedded": {
            "osdi:creator": {
                "given_name": "John",
                "family_name": "Doe",
                "identifiers": ["action_network:123"],
                "origin_system": "Action Network",
                "created_date": "2014-03-24T18:03:45Z",
                "modified_date": "2014-03-25T15:00:22Z",
                "email_addresses": [
                    {"primary": True, "address": "jdoe@mail.com", "status": "subscribed"}
                ],
                "phone_numbers": [
                    {
                        "primary": True,
                        "number": "12021234444",
                        "number_type": "Mobile",
                        "status": "subscribed",
                    }
                ],
                "postal_addresses": [
                    {
                        "primary": True,
                        "address_lines": ["1600 Pennsylvania Ave."],
                        "locality": "Washington",
                        "region": "DC",
                        "postal_code": "20009",
                        "country": "US",
                        "language": "en",
                        "location": {
                            "latitude": 35.919,
                            "longitude": -72.0379,
                            "accuracy": "Approximate",
                        },
                    }
                ],
                "languages_spoken": ["en"],
                "_links": {
                    "self": {"href": f"{API_URL}/people/123"},
                    "osdi:attendances": {"href": f"{API_URL}/people/123/attendances"},
                    "osdi:signatures": {"href": f"{API_URL}/people/123/signatures"},
                    "osdi:submissions": {"href": f"{API_URL}/people/123/submissions"},
                    "osdi:donations": {"href": f"{API_URL}/people/123/donations"},
                    "osdi:outreaches": {"href": f"{API_URL}/people/123/outreaches"},
                    "osdi:taggings": {"href": f"{API_URL}/people/123/taggings"},
                    "action_network:responses": {"href": f"{API_URL}/people/123/responses"},
                    "curies": [
                        {
                            "name": "osdi",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                        {
                            "name": "action_network",
                            "href": "https://actionnetwork.org/docs/v2/{rel}",
                            "templated": True,
                        },
                    ],
                },
            }
        },
        "_links": {
            "self": {"href": f"{API_URL}/surveys/123"},
            "action_network:responses": {"href": f"{API_URL}/surveys/123/responses"},
            "action_network:record_response_helper": {"href": f"{API_URL}/surveys/123/responses"},
            "osdi:creator": {"href": f"{API_URL}/people/123"},
            "action_network:embed": {"href": f"{API_URL}/surveys/123/embed"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_survey_with_creator_payload() -> dict[str, Any]:
    return {
        "title": "My Free Survey",
        "origin_system": "FreeSurveys.com",
        "_links": {"osdi:creator": {"href": f"{API_URL}/people/1234567890"}},
    }


@pytest.fixture
def fake_survey_payload() -> dict[str, Any]:
    return {
        "title": "My Free Survey",
        "origin_system": "FreeSurveys.com",
    }


@pytest.fixture
def fake_tags() -> dict[str, Any]:
    return {
        "total_pages": 10,
        "per_page": 25,
        "page": 1,
        "total_records": 243,
        "_links": {
            "next": {"href": f"{API_URL}/tags?page=2"},
            "self": {"href": f"{API_URL}/tags"},
            "osdi:tags": [
                {"href": f"{API_URL}/tags/fake_id"},
                {"href": f"{API_URL}/tags/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:tags": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-25T17:11:33Z",
                    "modified_date": "2014-03-25T17:13:33Z",
                    "name": "Volunteers",
                    "_links": {
                        "self": {"href": f"{API_URL}/tags/fake_id"},
                        "osdi:taggings": {"href": f"{API_URL}/tags/fake_id/taggings"},
                    },
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-24T18:26:42Z",
                    "modified_date": "2014-03-24T18:27:17Z",
                    "name": "Economic Justice",
                    "_links": {
                        "self": {"href": f"{API_URL}/tags/fake_id"},
                        "osdi:taggings": {"href": f"{API_URL}/tags/fake_id/taggings"},
                    },
                },
            ]
        },
    }


@pytest.fixture
def fake_taggings() -> dict[str, Any]:
    return {
        "total_pages": 5,
        "per_page": 25,
        "page": 1,
        "total_records": 123,
        "_links": {
            "next": {"href": f"{API_URL}/tags/fake_id/taggings?page=2"},
            "self": {"href": f"{API_URL}/tags/fake_id/taggings"},
            "osdi:taggings": [
                {"href": f"{API_URL}/tags/fake_id/taggings/fake_id"},
                {"href": f"{API_URL}/tags/fake_id/taggings/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:taggings": [
                {
                    "_links": {
                        "self": {"href": f"{API_URL}/tags/fake_id/taggings/fake_id"},
                        "osdi:tag": {"href": f"{API_URL}/tags/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-18T22:25:31Z",
                    "modified_date": "2014-03-18T22:25:38Z",
                    "item_type": "osdi:person",
                },
                {
                    "_links": {
                        "self": {"href": f"{API_URL}/tags/fake_id/taggings/fake_id"},
                        "osdi:tag": {"href": f"{API_URL}/tags/fake_id"},
                        "osdi:person": {"href": f"{API_URL}/people/fake_id"},
                    },
                    "identifiers": ["action_network:fake_id"],
                    "created_date": "2014-03-18T22:24:24Z",
                    "modified_date": "2014-03-18T22:24:24Z",
                    "item_type": "osdi:person",
                },
            ]
        },
    }


@pytest.fixture
def fake_tagging() -> dict[str, Any]:
    return {
        "_links": {
            "self": {"href": f"{API_URL}/tags/fake_id/taggings/fake_id"},
            "osdi:tag": {"href": f"{API_URL}/tags/fake_id"},
            "osdi:person": {"href": f"{API_URL}/people/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "identifiers": ["action_network:fake_id"],
        "created_date": "2014-03-18T22:25:31Z",
        "modified_date": "2014-03-18T22:25:38Z",
        "item_type": "osdi:person",
    }


@pytest.fixture
def fake_wrappers() -> dict[str, Any]:
    return {
        "total_pages": 7,
        "per_page": 25,
        "page": 1,
        "total_records": 162,
        "_links": {
            "next": {"href": f"{API_URL}/wrappers?page=2"},
            "self": {"href": f"{API_URL}/wrappers"},
            "osdi:wrappers": [
                {"href": f"{API_URL}/wrappers/fake_id"},
                {"href": f"{API_URL}/wrappers/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:wrappers": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-24T18:03:45Z",
                    "modified_date": "2014-03-25T15:00:22Z",
                    "name": "Default wrapper -- logo only",
                    "administrative_url": "https://actionnetwork.org/wrappers/1/edit",
                    "header": (
                        '<table border="0" cellpadding="10" '
                        'cellspacing="0" style="border-collapse:collapse; '
                        'mso-table-lspace:0pt; mso-table-rspace:0pt;">\r\n'
                        '  <tr>\r\n    <td valign="top" '
                        'style="border-collapse: collapse; background-color: #FFFFFF;'
                        ' padding:10px 10px 40px;">\r\n      <table border="0" cellpadding="10" '
                        'cellspacing="0" style="border-collapse:collapse; mso-table-lspace:0pt; '
                        'mso-table-rspace:0pt;">\r\n        <tr>\r\n       '
                        '   <td valign="top" style="border-collapse: collapse;"'
                        ' width="600">\r\n          '
                        '  <div style="color: #505050;font-family:'
                        "Arial;font-size: 14px;line-height: "
                        '150%;text-align: left;">\r\n'
                        '<img src="https://actionnetwork.org/images/logo.png" />'
                    ),
                    "footer": (
                        "\r\n</div>\r\n    "
                        " </td>\r\n "
                        "       </tr>\r\n  "
                        "    </table>\r\n  "
                        "  </td>\r\n "
                        " </tr>\r\n</table>"
                    ),
                    "action_network:suffix": " via ProgressivePower.org",
                    "wrapper_type": "email",
                    "default": True,
                    "_links": {"self": {"href": f"{API_URL}/wrappers/fake_id"}},
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "origin_system": "Action Network",
                    "created_date": "2014-03-14T15:21:05Z",
                    "modified_date": "2014-03-17T19:56:11Z",
                    "name": "No logo",
                    "administrative_url": "https://actionnetwork.org/wrappers/2/edit",
                    "header": (
                        '<table border="0" cellpadding="10" '
                        'cellspacing="0" style="border-collapse:collapse;'
                        ' mso-table-lspace:0pt; mso-table-rspace:0pt;">\r\n  <tr>\r\n    '
                        '<td valign="top" style="border-collapse:'
                        "collapse; background-color: #FFFFFF;"
                        ' padding:10px 10px 40px;">\r\n    '
                        '  <table border="0" cellpadding="10" cellspacing="0" '
                        'style="border-collapse:collapse; '
                        'mso-table-lspace:0pt; mso-table-rspace:0pt;">\r\n  '
                        "      <tr>\r\n        "
                        '  <td valign="top" style="border-collapse: collapse;" width="600">\r\n '
                        '<div style="color: #505050;font-family: Arial;font-size: 14px;line-height:'
                        '150%;text-align: left;">\r\n'
                    ),
                    "footer": (
                        "\r\n</div>\r\n "
                        "         </td>\r\n   "
                        "     </tr>\r\n      </table>\r\n "
                        "   </td>\r\n "
                        " </tr>\r\n</table>"
                    ),
                    "wrapper_type": "email",
                    "default": False,
                    "_links": {"self": {"href": f"{API_URL}/wrappers/fake_id"}},
                },
            ]
        },
    }


@pytest.fixture
def fake_wrapper() -> dict[str, Any]:
    return {
        "identifiers": ["action_network:fake_id"],
        "origin_system": "Action Network",
        "created_date": "2014-03-24T18:03:45Z",
        "modified_date": "2014-03-25T15:00:22Z",
        "name": "Default wrapper -- logo only",
        "administrative_url": "https://actionnetwork.org/wrappers/1/edit",
        "header": (
            '<table border="0" cellpadding="10" '
            'cellspacing="0" style="border-collapse:collapse;'
            ' mso-table-lspace:0pt; mso-table-rspace:0pt;">\r\n'
            "  <tr>\r\n"
            '    <td valign="top" style="border-collapse: collapse; '
            'background-color: #FFFFFF; padding:10px 10px 40px;">\r\n '
            '     <table border="0" cellpadding="10"'
            ' cellspacing="0" style="border-collapse:collapse;'
            ' mso-table-lspace:0pt; mso-table-rspace:0pt;">\r\n        <tr>\r\n '
            '         <td valign="top" style="border-collapse: collapse;" width="600">\r\n  '
            '          <div style="color: #505050;font-family: Arial;font-size: '
            '14px;line-height: 150%;text-align: left;">\r\n'
            '<img src="https://actionnetwork.org/images/logo.png" />'
        ),
        "footer": (
            "\r\n</div>\r\n"
            "          </td>\r\n"
            "        </tr>\r\n"
            "      </table>\r\n"
            "    </td>\r\n "
            " </tr>\r\n</table>"
        ),
        "action_network:suffix": " via ProgressivePower.org",
        "wrapper_type": "email",
        "default": True,
        "_links": {
            "self": {"href": f"{API_URL}/wrappers/fake_id"},
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
    }


@pytest.fixture
def fake_unique_id_lists() -> dict[str, Any]:
    return {
        "total_pages": 3,
        "per_page": 25,
        "page": 1,
        "total_records": 50,
        "_links": {
            "next": {"href": f"{API_URL}/unique_id_lists?page=2"},
            "self": {"href": f"{API_URL}/unique_id_lists"},
            "osdi:unique_id_lists": [
                {"href": f"{API_URL}/unique_id_lists/fake_id"},
                {"href": f"{API_URL}/unique_id_lists/fake_id"},
            ],
            "curies": [
                {
                    "name": "osdi",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
                {
                    "name": "action_network",
                    "href": "https://actionnetwork.org/docs/v2/{rel}",
                    "templated": True,
                },
            ],
        },
        "_embedded": {
            "osdi:unique_id_lists": [
                {
                    "identifiers": ["action_network:fake_id"],
                    "name": "Example Unique ID List",
                    "created_date": "2022-01-01T00:00:00Z",
                    "modified_date": "2022-01-01T00:00:00Z",
                    "description": "This is an example unique ID list.",
                    "administrative_url": "https://actionnetwork.org/unique_id_lists/1/edit",
                },
                {
                    "identifiers": ["action_network:fake_id"],
                    "name": "Another Unique ID List",
                    "created_date": "2022-01-02T00:00:00Z",
                    "modified_date": "2022-01-02T00:00:00Z",
                    "description": "This is another example unique ID list.",
                    "administrative_url": "https://actionnetwork.org/unique_id_lists/2/edit",
                },
            ],
        },
    }
