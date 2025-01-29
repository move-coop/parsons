import unittest
import requests_mock
import json
from parsons import Table
from parsons.action_network import ActionNetwork
from test.utils import assert_matching_tables


class TestActionNetwork(unittest.TestCase):
    @requests_mock.Mocker()
    def setUp(self, m):
        self.api_url = "https://actionnetwork.org/api/v2"
        self.api_key = "fake_key"

        self.an = ActionNetwork(self.api_key)

        self.fake_datetime = "2019-02-29T00:00:00.000+0000"
        self.fake_date = "2019-02-29"
        self.fake_customer_email_1 = "fake_customer_email_1@fake_customer_email.com"
        self.fake_customer_email_2 = "fake_customer_email_2@fake_customer_email.com"
        self.fake_filter_by_email_1 = f"filter eq '{self.fake_customer_email_1}'"
        self.fake_person_id_1 = "action_network:fake_person_id_1"
        self.fake_person_id_2 = "action_network:fake_person_id_2"
        self.fake_tag_id_1 = "fake_tag_id_1"
        self.fake_tag_id_2 = "fake_tag_id_2"
        self.fake_tag_filter = "name eq 'fake_tag_1'"
        self.fake_people_list_1 = {
            "per_page": 2,
            "page": 1,
            "_links": {
                "next": {"href": f"{self.api_url}/people?page=2"},
                "osdi:people": [
                    {"href": f"{self.api_url}/{self.fake_person_id_1}"},
                    {"href": f"{self.api_url}/{self.fake_person_id_2}"},
                ],
                "curies": [
                    {"name": "osdi", "templated": True},
                    {"name": "action_network", "templated": True},
                ],
                "self": {"href": f"{self.api_url}/people"},
            },
            "_embedded": {
                "osdi:people": [
                    {
                        "given_name": "Fakey",
                        "family_name": "McFakerson",
                        "identifiers": [self.fake_person_id_1],
                        "email_addresses": [
                            {
                                "primary": True,
                                "address": self.fake_customer_email_1,
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
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "languages_spoken": ["en"],
                    },
                    {
                        "given_name": "Faker",
                        "family_name": "McEvenFakerson",
                        "identifiers": [self.fake_person_id_2],
                        "email_addresses": [
                            {
                                "primary": True,
                                "address": self.fake_customer_email_2,
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
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "languages_spoken": ["en"],
                    },
                ]
            },
        }
        self.fake_people_list_2 = {
            "per_page": 2,
            "page": 2,
            "_links": {
                "next": {"href": f"{self.api_url}/people?page=3"},
                "osdi:people": [
                    {"href": f"{self.api_url}/{self.fake_person_id_1}"},
                    {"href": f"{self.api_url}/{self.fake_person_id_2}"},
                ],
                "curies": [
                    {"name": "osdi", "templated": True},
                    {"name": "action_network", "templated": True},
                ],
                "self": {"href": f"{self.api_url}/people"},
            },
            "_embedded": {
                "osdi:people": [
                    {
                        "given_name": "Fakey",
                        "family_name": "McFakerson",
                        "identifiers": [self.fake_person_id_1],
                        "email_addresses": [
                            {
                                "primary": True,
                                "address": self.fake_customer_email_1,
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
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "languages_spoken": ["en"],
                    },
                    {
                        "given_name": "Faker",
                        "family_name": "McEvenFakerson",
                        "identifiers": [self.fake_person_id_2],
                        "email_addresses": [
                            {
                                "primary": True,
                                "address": self.fake_customer_email_2,
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
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "languages_spoken": ["en"],
                    },
                ]
            },
        }
        self.fake_people_list = (
            self.fake_people_list_1["_embedded"]["osdi:people"]
            + self.fake_people_list_2["_embedded"]["osdi:people"]
        )
        self.fake_tag_list = {
            "total_pages": 1,
            "per_page": 2,
            "page": 1,
            "total_records": 2,
            "_links": {
                "next": {"href": f"{self.api_url}/tags?page=2"},
                "osdi:tags": [
                    {"href": f"{self.api_url}/tags/{self.fake_tag_id_1}"},
                    {"href": f"{self.api_url}/tags/{self.fake_tag_id_2}"},
                ],
                "curies": [
                    {"name": "osdi", "templated": True},
                    {"name": "action_network", "templated": True},
                ],
                "self": {"href": f"{self.api_url}/tags"},
            },
            "_embedded": {
                "osdi:tags": [
                    {
                        "name": "fake_tag_1",
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "identifiers": [self.fake_tag_id_1],
                        "_links": {"self": {"href": self.fake_tag_id_1}},
                    },
                    {
                        "name": "fake_tag_2",
                        "created_date": self.fake_datetime,
                        "modified_date": self.fake_datetime,
                        "identifiers": [self.fake_tag_id_1],
                        "_links": {"self": {"href": self.fake_tag_id_1}},
                    },
                ]
            },
        }
        self.fake_upsert_person = {
            "given_name": "Fakey",
            "family_name": "McFakerson",
            "identifiers": [self.fake_person_id_1],
            "email_address": [
                {
                    "primary": True,
                    "address": "fakey@mcfakerson.com",
                    "status": "unsubscribed",
                }
            ],
            "created_date": self.fake_datetime,
            "modified_date": self.fake_datetime,
        }
        self.fake_person = [
            {
                "given_name": "Fakey",
                "family_name": "McFakerson",
                "identifiers": [self.fake_person_id_1],
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
                "created_date": self.fake_date,
                "modified_date": self.fake_date,
                "languages_spoken": ["en"],
            }
        ]
        self.updated_fake_person = [
            {
                "given_name": "Flakey",
                "family_name": "McFlakerson",
                "identifiers": [self.fake_person_id_1],
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
                "created_date": self.fake_date,
                "modified_date": self.fake_date,
                "languages_spoken": ["en"],
            }
        ]
        self.fake_tag = {
            "name": "fake_tag_1",
            "created_date": self.fake_datetime,
            "modified_date": self.fake_datetime,
            "identifiers": [self.fake_tag_id_1],
            "_links": {"self": {"href": self.fake_tag_id_1}},
        }
        self.fake_location = {
            "venue": "White House",
            "address_lines": ["1600 Pennsylvania Ave"],
            "locality": "Washington",
            "region": "DC",
            "postal_code": "20009",
            "country": "US",
        }
        self.fake_event = {
            "title": "fake_title",
            "start_date": self.fake_date,
            "location": self.fake_location,
            "_links": {
                "self": {"href": f"{self.api_url}/events/fake-id"},
            },
            "event_id": "fake-id",
        }
        self.fake_unique_id_list = {
            "name": "fake_list_name",
            "unique_ids": [
                "ee48622d-a584-46a4-b817-2e6f2e4bf51b",
                "1b0012d2-214a-4188-9c82-08f21ee54b27",
            ],
        }

        # Advocacy Campaigns
        self.fake_advocacy_campaigns = {
            "total_pages": 1,
            "per_page": 25,
            "page": 1,
            "total_records": 3,
            "_links": {
                "next": {"href": f"{self.api_url}/advocacy_campaigns?page=2"},
                "self": {"href": f"{self.api_url}/advocacy_campaigns"},
                "osdi:advocacy_campaigns": [
                    {"href": f"{self.api_url}/advocacy_campaigns/fake_url"},
                    {"href": f"{self.api_url}/advocacy_campaigns/fake_url"},
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
                                    "self": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:attendances": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:signatures": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:submissions": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:donations": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:outreaches": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:taggings": {"href": f"{self.api_url}/people/fake_url"},
                                },
                            }
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/advocacy_campaigns/fake_url"},
                            "osdi:outreaches": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                            "osdi:record_outreach_helper": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_url"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
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
                                    "self": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:attendances": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:signatures": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:submissions": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:donations": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:outreaches": {"href": f"{self.api_url}/people/fake_url"},
                                    "osdi:taggings": {"href": f"{self.api_url}/people/fake_url"},
                                },
                            }
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/advocacy_campaigns/fake_url"},
                            "osdi:outreaches": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                            "osdi:record_outreach_helper": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
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
                            "self": {"href": f"{self.api_url}/advocacy_campaigns/fake_url"},
                            "osdi:outreaches": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_url"},
                            "osdi:record_outreach_helper": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_url"
                            },
                        },
                    },
                ]
            },
        }
        self.fake_advocacy_campaign = {
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
                        "self": {"href": f"{self.api_url}/people/fake_id"},
                        "osdi:attendances": {"href": f"{self.api_url}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{self.api_url}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{self.api_url}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{self.api_url}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
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
                "self": {"href": f"{self.api_url}/advocacy_campaigns/fake_id"},
                "osdi:outreaches": {
                    "href": f"{self.api_url}/advocacy_campaigns/fake_id/outreaches"
                },
                "osdi:record_outreach_helper": {
                    "href": f"{self.api_url}/advocacy_campaigns/fake_id/outreaches"
                },
                "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                "action_network:embed": {
                    "href": f"{self.api_url}/advocacy_campaigns/fake_id/embed"
                },
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

        # Attendances
        self.fake_attendances = {
            "total_pages": 1,
            "per_page": 25,
            "page": 1,
            "total_records": 20,
            "_links": {
                "self": {"href": f"{self.api_url}/events/fake_id/attendances"},
                "osdi:attendance": [
                    {"href": f"{self.api_url}/events/fake_id/attendances/fake_id"},
                    {"href": f"{self.api_url}/events/fake_id/attendances/fake_id"},
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
                            "self": {"href": f"{self.api_url}/events/fake_id/attendances/fake_id"},
                            "osdi:event": {"href": f"{self.api_url}/events/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
                            "self": {"href": f"{self.api_url}/events/fake_id/attendances/fake_id"},
                            "osdi:event": {"href": f"{self.api_url}/events/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                    },
                ]
            },
        }
        self.fake_attendance = {
            "identifiers": ["action_network:d51ca19e-9fe9-11e3-a2e9-12313d316c29"],
            "created_date": "2014-02-18T20:52:59Z",
            "modified_date": "2014-02-18T20:53:00Z",
            "status": "accepted",
            "action_network:person_id": "fake_id",
            "action_network:event_id": "fake_id",
            "_links": {
                "self": {"href": f"{self.api_url}/events/fake_id/attendances/fake_id"},
                "osdi:event": {"href": f"{self.api_url}/events/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # Campaigns
        self.fake_campaigns = {
            "total_pages": 2,
            "per_page": 25,
            "page": 1,
            "total_records": 30,
            "_links": {
                "next": {"href": f"{self.api_url}/campaigns?page=2"},
                "self": {"href": f"{self.api_url}/campaigns"},
                "action_network:campaigns": [
                    {"href": f"{self.api_url}/campaigns/fake_id"},
                    {"href": f"{self.api_url}/campaigns/fake_id"},
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
                        "_links": {"self": {"href": f"{self.api_url}/campaigns/fake_id"}},
                    },
                    {
                        "identifiers": ["action_network:fake_id"],
                        "origin_system": "Action Network",
                        "created_date": "2013-09-30T15:55:44Z",
                        "modified_date": "2014-01-16T19:07:00Z",
                        "title": "Welcome to our Action Center",
                        "description": "<p>Welcome to our Action Center."
                        "Take action on the right.</p>",
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
                        "_links": {"self": {"href": f"{self.api_url}/campaigns/fake_id"}},
                    },
                ]
            },
        }
        self.fake_campaign = {
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
                "self": {"href": f"{self.api_url}/campaigns/fake_id"},
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

        # Custom Fields
        self.fake_custom_fields = {
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

        # Donations
        self.fake_donations = {
            "total_pages": 1,
            "per_page": 25,
            "page": 1,
            "total_records": 6,
            "_links": {
                "self": {"href": f"{self.api_url}/fundraising_pages/fake_id/donations"},
                "osdi:donations": [
                    {"href": f"{self.api_url}/fundraising_pages/fake_id/donations/fake_id"},
                    {"href": f"{self.api_url}/fundraising_pages/fake_id/donations/fake_id"},
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
                            "self": {"href": f"{self.api_url}/fundraising_pages/fake_url"},
                            "osdi:fundraising_page": {"href": f"{self.api_url}/fake_url"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_url"},
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
                            "osdi:fundraising_page": {
                                "href": f"{self.api_url}/fundraising_pages/fake_id"
                            },
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                    },
                ]
            },
        }
        self.fake_donation = {
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
                "self": {"href": f"{self.api_url}/fundraising_pages/fake_id/donations/fake_id"},
                "osdi:fundraising_page": {"href": f"{self.api_url}/fundraising_pages/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # Embeds
        self.fake_embed = {
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
                "self": {
                    "href": f"{self.api_url}/events/21789f03-0180-45d3-853c-91bd6fdc8c07/embed"
                },
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

        # Event Campaigns
        self.fake_event_campaigns = {
            "total_pages": 10,
            "per_page": 25,
            "page": 1,
            "total_records": 237,
            "_links": {
                "next": {"href": f"{self.api_url}/event_campaigns?page=2"},
                "self": {"href": f"{self.api_url}/event_campaigns"},
                "action_network:event_campaigns": [
                    {"href": f"{self.api_url}/event_campaigns/fake_id"},
                    {"href": f"{self.api_url}/event_campaigns/fake_id"},
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
                            "self": {"href": f"{self.api_url}/event_campaigns/fake_id"},
                            "osdi:events": {
                                "href": f"{self.api_url}/event_campaigns/fake_id/events"
                            },
                            "action_network:embed": {
                                "href": f"{self.api_url}/event_campaigns/fake_id/embed"
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
                        "host_instructions": "<p>Here's everything "
                        "you need to host a protest...</p>",
                        "browser_url": "fake_url",
                        "host_url": "fake_url",
                        "total_events": 4,
                        "total_rsvps": 11,
                        "action_network:sponsor": {
                            "title": "Progressive Action Now",
                            "url": "fake_url",
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/event_campaigns/fake_id"},
                            "osdi:events": {
                                "href": f"{self.api_url}/event_campaigns/fake_id/events"
                            },
                            "action_network:embed": {
                                "href": f"{self.api_url}/event_campaigns/fake_id/embed"
                            },
                        },
                    },
                ]
            },
        }
        self.fake_event_campaign = {
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
                "self": {"href": f"{self.api_url}/event_campaigns/fake_id"},
                "osdi:events": {"href": f"{self.api_url}/event_campaigns/fake_id/events"},
                "action_network:embed": {"href": f"{self.api_url}/event_campaigns/fake_id/embed"},
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

        # Events
        self.fake_events = {
            "total_pages": 10,
            "per_page": 25,
            "page": 1,
            "total_records": 250,
            "_links": {
                "next": {"href": f"{self.api_url}/events?page=2"},
                "self": {"href": f"{self.api_url}/events"},
                "osdi:events": [
                    {"href": f"{self.api_url}/events/fake_id"},
                    {"href": f"{self.api_url}/events/fake_id"},
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
                            "self": {"href": f"{self.api_url}/events/fake_id"},
                            "osdi:attendances": {
                                "href": f"{self.api_url}/events/fake_id/attendances"
                            },
                            "osdi:record_attendance_helper": {
                                "href": f"{self.api_url}/events/fake_id/attendances"
                            },
                            "osdi:organizer": {"href": f"{self.api_url}/people/fake_id"},
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/events/fake_id/embed"
                            },
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
                            "self": {"href": f"{self.api_url}/events/fake_id"},
                            "osdi:attendances": {
                                "href": f"{self.api_url}/events/fake_id/attendances"
                            },
                            "osdi:record_attendance_helper": {
                                "href": f"{self.api_url}/events/fake_id/attendances"
                            },
                            "osdi:organizer": {"href": f"{self.api_url}/people/fake_id"},
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/events/fake_id/embed"
                            },
                        },
                    },
                ]
            },
        }
        self.fake_event2 = {
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
                "self": {"href": f"{self.api_url}/events/fake_id"},
                "osdi:attendances": {"href": f"{self.api_url}/events/fake_id/attendances"},
                "osdi:record_attendance_helper": {
                    "href": f"{self.api_url}/events/fake_id/attendances"
                },
                "osdi:organizer": {"href": f"{self.api_url}/people/fake_id"},
                "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                "action_network:embed": {"href": f"{self.api_url}/events/fake_id/embed"},
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

        # Forms
        self.fake_forms = {
            "total_pages": 10,
            "per_page": 25,
            "page": 1,
            "total_records": 250,
            "_links": {
                "next": {"href": f"{self.api_url}/forms?page=2"},
                "self": {"href": f"{self.api_url}/forms"},
                "osdi:forms": [
                    {"href": f"{self.api_url}/forms/65345d7d-cd24-466a-a698-4a7686ef684f"},
                    {"href": f"{self.api_url}/forms/fake_id"},
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
                                    "self": {"href": f"{self.api_url}/people/fake_id"},
                                    "osdi:attendances": {
                                        "href": f"{self.api_url}/people/fake_id/attendances"
                                    },
                                    "osdi:signatures": {
                                        "href": f"{self.api_url}/people/fake_id/signatures"
                                    },
                                    "osdi:submissions": {
                                        "href": f"{self.api_url}/people/fake_id/submissions"
                                    },
                                    "osdi:donations": {
                                        "href": f"{self.api_url}/people/fake_id/donations"
                                    },
                                    "osdi:outreaches": {
                                        "href": f"{self.api_url}/people/fake_id/outreaches"
                                    },
                                    "osdi:taggings": {
                                        "href": f"{self.api_url}/people/fake_id/taggings"
                                    },
                                },
                            }
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/forms/fake_id"},
                            "osdi:submissions": {
                                "href": f"{self.api_url}/forms/fake_id/submissions"
                            },
                            "osdi:record_submission_helper": {
                                "href": f"{self.api_url}/forms/fake_id/submissions"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {"href": f"{self.api_url}/forms/fake_id/embed"},
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
                                    "self": {"href": f"{self.api_url}/people/fake_id"},
                                    "osdi:attendances": {
                                        "href": f"{self.api_url}/people/fake_id/attendances"
                                    },
                                    "osdi:signatures": {
                                        "href": f"{self.api_url}/people/fake_id/signatures"
                                    },
                                    "osdi:submissions": {
                                        "href": f"{self.api_url}/people/fake_id/submissions"
                                    },
                                    "osdi:donations": {
                                        "href": f"{self.api_url}/people/fake_id/donations"
                                    },
                                    "osdi:outreaches": {
                                        "href": f"{self.api_url}/people/fake_id/outreaches"
                                    },
                                    "osdi:taggings": {
                                        "href": f"{self.api_url}/people/fake_id/taggings"
                                    },
                                },
                            }
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/forms/fake_id"},
                            "osdi:submissions": {
                                "href": f"{self.api_url}/forms/fake_id/submissions"
                            },
                            "osdi:record_submission_helper": {
                                "href": f"{self.api_url}/forms/fake_id/submissions"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {"href": f"{self.api_url}/forms/fake_id/embed"},
                        },
                    },
                ]
            },
        }
        self.fake_form = {
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
                        "self": {"href": f"{self.api_url}/people/fake_id"},
                        "osdi:attendances": {"href": f"{self.api_url}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{self.api_url}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{self.api_url}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{self.api_url}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
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
                "self": {"href": f"{self.api_url}/forms/fake_id"},
                "osdi:submissions": {"href": f"{self.api_url}/forms/fake_id/submissions"},
                "osdi:record_submission_helper": {
                    "href": f"{self.api_url}/forms/fake_id/submissions"
                },
                "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                "action_network:embed": {"href": f"{self.api_url}/forms/fake_id/embed"},
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

        # Fundraising Pages
        self.fake_fundraising_pages = {
            "total_pages": 1,
            "per_page": 1,
            "page": 1,
            "total_records": 1,
            "_links": {
                "next": {"href": f"{self.api_url}/fundraising_pages?page=2"},
                "osdi:fundraising_pages": [
                    {"href": f"{self.api_url}/fundraising_pages/{self.fake_tag_id_1}"},
                ],
                "curies": [
                    {"name": "osdi", "templated": True},
                    {"name": "action_network", "templated": True},
                ],
                "self": {"href": f"{self.api_url}/fundraising_pages"},
            },
            "_embedded": {
                "osdi:fundraising_pages": [
                    {
                        "identifiers": [""],
                        "created_date": self.fake_date,
                        "total_donations": 0,
                        "total_amount": "0.00",
                        "currency": "USD",
                        "action_network:sponsor": {"title": "", "browser_url": ""},
                        "_links": {
                            "self": {"href": f"{self.api_url}/fundraising_pages"},
                            "osdi:creator": {"href": "fake_url"},
                            "osdi:donations": {"href": "fake_url"},
                            "osdi:record_donation_helper": {"href": "fake_url"},
                        },
                        "modified_date": self.fake_date,
                        "origin_system": "Test",
                        "title": "Hello",
                        "_embedded": {"osdi:creator": ""},
                        "action_network:hidden": False,
                    }
                ]
            },
        }
        self.fake_fundraising_page = {
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
                        "self": {"href": f"{self.api_url}/people/fake_id"},
                        "osdi:attendances": {"href": f"{self.api_url}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{self.api_url}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{self.api_url}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{self.api_url}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
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
                "self": {"href": f"{self.api_url}/fundraising_pages/fake_id"},
                "osdi:donations": {"href": f"{self.api_url}/fundraising_pages/fake_id/donations"},
                "osdi:record_donation_helper": {
                    "href": f"{self.api_url}/fundraising_pages/fake_id/donations"
                },
                "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                "action_network:embed": {"href": f"{self.api_url}/fundraising_pages/fake_id/embed"},
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

        # Items
        self.fake_items = {
            "per_page": 25,
            "page": 1,
            "_links": {
                "next": {"href": f"{self.api_url}/lists/fake_id/items?page=2"},
                "self": {"href": f"{self.api_url}/lists/fake_id/items"},
                "osdi:items": [
                    {"href": f"{self.api_url}/lists/fake_id/items/fake_id"},
                    {"href": f"{self.api_url}/lists/fake_id/items/fake_id"},
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
                            "self": {"href": f"{self.api_url}/lists/fake_id/items/fake_id"},
                            "osdi:list": {"href": f"{self.api_url}/lists/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
                            "self": {"href": f"{self.api_url}/lists/fake_id/items/fake_id"},
                            "osdi:list": {"href": f"{self.api_url}/lists/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
        self.fake_item = {
            "_links": {
                "self": {"href": f"{self.api_url}/lists/fake_id/items/fake_id"},
                "osdi:list": {"href": f"{self.api_url}/lists/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # Lists
        self.fake_lists = {
            "total_pages": 10,
            "per_page": 25,
            "page": 1,
            "total_records": 243,
            "_links": {
                "next": {"href": f"{self.api_url}/lists?page=2"},
                "self": {"href": f"{self.api_url}/lists"},
                "osdi:lists": [
                    {"href": f"{self.api_url}/lists/fake_id"},
                    {"href": f"{self.api_url}/lists/fake_id"},
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
                            "self": {"href": f"{self.api_url}/lists/fake_id"},
                            "osdi:items": {"href": f"{self.api_url}/lists/fake_id/items"},
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
                            "self": {"href": f"{self.api_url}/lists/fake_id"},
                            "osdi:items": {"href": f"{self.api_url}/lists/fake_id/items"},
                        },
                    },
                ]
            },
        }
        self.fake_list = {
            "identifiers": ["action_network:fake_id"],
            "origin_system": "Action Network",
            "created_date": "2014-03-25T17:11:33Z",
            "modified_date": "2014-03-25T17:13:33Z",
            "title": "Stop Doing The Bad Thing Petition Signers",
            "description": "Report",
            "browser_url": "fake_url",
            "_links": {
                "self": {"href": f"{self.api_url}/lists/fake_id"},
                "osdi:items": {"href": f"{self.api_url}/lists/fake_id/items"},
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

        # Messages
        self.fake_messages = {
            "total_pages": 7,
            "per_page": 25,
            "page": 1,
            "total_records": 162,
            "_links": {
                "next": {"href": f"{self.api_url}/messages?page=2"},
                "self": {"href": f"{self.api_url}/messages"},
                "osdi:messages": [
                    {"href": f"{self.api_url}/messages/fake_id"},
                    {"href": f"{self.api_url}/messages/fake_id"},
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
                        "targets": [{"href": f"{self.api_url}/queries/fake_id"}],
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
                            "self": {"href": f"{self.api_url}/messages/fake_id"},
                            "osdi:wrapper": {"href": f"{self.api_url}/wrappers/fake_id"},
                            "osdi:recipients": {
                                "href": f"{self.api_url}/lists/950e9954-606f-43e6-be99-2bc0bc2072a1"
                            },
                            "osdi:send_helper": {"href": f"{self.api_url}/messages/fake_id/send"},
                            "osdi:schedule_helper": {
                                "href": f"{self.api_url}/messages/fake_id/schedule"
                            },
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
                            "self": {"href": f"{self.api_url}/messages/fake_id"},
                            "osdi:send_helper": {"href": f"{self.api_url}/messages/fake_id/send"},
                            "osdi:schedule_helper": {
                                "href": f"{self.api_url}/messages/fake_id/schedule"
                            },
                        },
                    },
                ]
            },
        }
        self.fake_message = {
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
            "targets": [{"href": f"{self.api_url}/queries/fake_id"}],
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
                "self": {"href": f"{self.api_url}/messages/fake_id"},
                "osdi:wrapper": {"href": f"{self.api_url}/wrappers/fake_id"},
                "osdi:recipients": {
                    "href": f"{self.api_url}/lists/950e9954-606f-43e6-be99-2bc0bc2072a1"
                },
                "osdi:send_helper": {"href": f"{self.api_url}/messages/fake_id/send"},
                "osdi:schedule_helper": {"href": f"{self.api_url}/messages/fake_id/schedule"},
            },
        }

        # Metadata
        self.fake_metadata = {
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

        # Outreaches
        self.fake_outreaches = {
            "total_pages": 1,
            "per_page": 25,
            "page": 1,
            "total_records": 6,
            "_links": {
                "self": {"href": f"{self.api_url}/advocacy_campaigns/fake_id/outreaches"},
                "osdi:outreaches": [
                    {"href": f"{self.api_url}/advocacy_campaigns/fake_id/outreaches/fake_id"},
                    {"href": f"{self.api_url}/advocacy_campaigns/fake_id/outreaches/dfake_id"},
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
                            "osdi:advocacy_campaign": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_id"
                            },
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
                            "osdi:advocacy_campaign": {
                                "href": f"{self.api_url}/advocacy_campaigns/fake_id"
                            },
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                    },
                ]
            },
        }
        self.fake_outreach = {
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
                "self": {"href": f"{self.api_url}/fundraising_page/fake_id/outreaches/fake_id"},
                "osdi:advocacy_campaign": {"href": f"{self.api_url}/advocacy_campaigns/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # People
        self.fake_people = {
            "per_page": 25,
            "page": 1,
            "_links": {
                "next": {"href": f"{self.api_url}/people?page=2"},
                "osdi:people": [
                    {"href": f"{self.api_url}/people/fake_id"},
                    {"href": f"{self.api_url}/people/fake_id"},
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
                "self": {"href": f"{self.api_url}/people"},
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
                            "self": {"href": f"{self.api_url}/people/fake_id"},
                            "osdi:attendances": {
                                "href": f"{self.api_url}/people/fake_id/attendances"
                            },
                            "osdi:signatures": {
                                "href": f"{self.api_url}/people/fake_id/signatures"
                            },
                            "osdi:submissions": {
                                "href": f"{self.api_url}/people/fake_id/submissions"
                            },
                            "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                            "osdi:outreaches": {
                                "href": f"{self.api_url}/people/fake_id/outreaches"
                            },
                            "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
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
                            "self": {"href": f"{self.api_url}/people/fake_id"},
                            "osdi:attendances": {
                                "href": f"{self.api_url}/people/fake_id/attendances"
                            },
                            "osdi:signatures": {
                                "href": f"{self.api_url}/people/fake_id/signatures"
                            },
                            "osdi:submissions": {
                                "href": f"{self.api_url}/people/fake_id/submissions"
                            },
                            "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                            "osdi:outreaches": {
                                "href": f"{self.api_url}/people/fake_id/outreaches"
                            },
                            "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
                        },
                    },
                ]
            },
        }

        # Petitions
        self.fake_petitions = {
            "total_pages": 7,
            "per_page": 25,
            "page": 1,
            "total_records": 162,
            "_links": {
                "next": {"href": f"{self.api_url}/petitions?page=2"},
                "self": {"href": f"{self.api_url}/petitions"},
                "osdi:petitions": [
                    {"href": f"{self.api_url}/petitions/fake_id"},
                    {"href": f"{self.api_url}/petitions/fake_id"},
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
                                    "self": {"href": f"{self.api_url}/people/fake_id"},
                                    "osdi:attendances": {
                                        "href": f"{self.api_url}/people/fake_id/attendances"
                                    },
                                    "osdi:signatures": {
                                        "href": f"{self.api_url}/people/fake_id/signatures"
                                    },
                                    "osdi:submissions": {
                                        "href": f"{self.api_url}/people/fake_id/submissions"
                                    },
                                    "osdi:donations": {
                                        "href": f"{self.api_url}/people/fake_id/donations"
                                    },
                                    "osdi:outreaches": {
                                        "href": f"{self.api_url}/people/fake_id/outreaches"
                                    },
                                    "osdi:taggings": {
                                        "href": f"{self.api_url}/people/fake_id/taggings"
                                    },
                                },
                            }
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/petitions/fake_id"},
                            "osdi:signatures": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures"
                            },
                            "osdi:record_signature_helper": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/petitions/fake_id/embed"
                            },
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
                                    "self": {"href": f"{self.api_url}/people/fake_id"},
                                    "osdi:attendances": {
                                        "href": f"{self.api_url}/people/fake_id/attendances"
                                    },
                                    "osdi:signatures": {
                                        "href": f"{self.api_url}/people/fake_id/signatures"
                                    },
                                    "osdi:submissions": {
                                        "href": f"{self.api_url}/people/fake_id/submissions"
                                    },
                                    "osdi:donations": {
                                        "href": f"{self.api_url}/people/fake_id/donations"
                                    },
                                    "osdi:outreaches": {
                                        "href": f"{self.api_url}/people/fake_id/outreaches"
                                    },
                                    "osdi:taggings": {
                                        "href": f"{self.api_url}/people/fake_id/taggings"
                                    },
                                },
                            }
                        },
                        "action_network:sponsor": {
                            "title": "Progressive Action Now",
                            "url": "https://actionnetwork.org/groups/progressive-action-now",
                        },
                        "_links": {
                            "self": {"href": f"{self.api_url}/petitions/fake_id"},
                            "osdi:signatures": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures"
                            },
                            "osdi:record_signature_helper": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures"
                            },
                            "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                            "action_network:embed": {
                                "href": f"{self.api_url}/petitions/fake_id/embed"
                            },
                        },
                    },
                ]
            },
        }
        self.fake_petition = {
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
                        "self": {"href": f"{self.api_url}/people/fake_id"},
                        "osdi:attendances": {"href": f"{self.api_url}/people/fake_id/attendances"},
                        "osdi:signatures": {"href": f"{self.api_url}/people/fake_id/signatures"},
                        "osdi:submissions": {"href": f"{self.api_url}/people/fake_id/submissions"},
                        "osdi:donations": {"href": f"{self.api_url}/people/fake_id/donations"},
                        "osdi:outreaches": {"href": f"{self.api_url}/people/fake_id/outreaches"},
                        "osdi:taggings": {"href": f"{self.api_url}/people/fake_id/taggings"},
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
                "self": {"href": f"{self.api_url}/petitions/fake_id"},
                "osdi:signatures": {"href": f"{self.api_url}/petitions/fake_id/signatures"},
                "osdi:record_signature_helper": {
                    "href": f"{self.api_url}/petitions/fake_id/signatures"
                },
                "osdi:creator": {"href": f"{self.api_url}/people/fake_id"},
                "action_network:embed": {"href": f"{self.api_url}/petitions/fake_id/embed"},
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

        # Queries
        self.fake_queries = {
            "total_pages": 7,
            "per_page": 25,
            "page": 1,
            "total_records": 162,
            "_links": {
                "next": {"href": f"{self.api_url}/queries?page=2"},
                "self": {"href": f"{self.api_url}/queries"},
                "osdi:queries": [
                    {"href": f"{self.api_url}/queries/fake_id"},
                    {"href": f"{self.api_url}/queries/fake_id"},
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
                        "_links": {"self": {"href": f"{self.api_url}/queries/fake_id"}},
                    },
                    {
                        "identifiers": ["action_network:fake_id"],
                        "origin_system": "Action Network",
                        "created_date": "2014-03-14T15:21:05Z",
                        "modified_date": "2014-03-17T19:56:11Z",
                        "name": "Volunteer prospects",
                        "browser_url": "https://actionnetwork.org/queries/2/edit",
                        "_links": {"self": {"href": f"{self.api_url}/queries/fake_id"}},
                    },
                ]
            },
        }
        self.fake_query = {
            "identifiers": ["action_network:fake_id"],
            "origin_system": "Action Network",
            "created_date": "2014-03-24T18:03:45Z",
            "modified_date": "2014-03-25T15:00:22Z",
            "name": "All donors",
            "browser_url": "https://actionnetwork.org/queries/1/edit",
            "_links": {
                "self": {"href": f"{self.api_url}/queries/fake_id"},
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

        # Signatures
        self.fake_signatures = {
            "total_pages": 100,
            "per_page": 25,
            "page": 1,
            "total_records": 2500,
            "_links": {
                "self": {"href": f"{self.api_url}/petitions/fake_id/signatures"},
                "osdi:signatures": [
                    {"href": f"{self.api_url}/petitions/fake_id/signatures/fake_id"},
                    {"href": f"{self.api_url}/petitions/fake_id/signatures/fake_id`"},
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
                            "self": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures/fake_id"
                            },
                            "osdi:petition": {"href": f"{self.api_url}/petitions/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
                            "self": {
                                "href": f"{self.api_url}/petitions/fake_id/signatures/fake_id"
                            },
                            "osdi:petition": {"href": f"{self.api_url}/petitions/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                    },
                ]
            },
        }
        self.fake_signature = {
            "identifiers": ["action_network:fake_id"],
            "created_date": "2014-03-26T18:04:00Z",
            "modified_date": "2014-03-26T18:04:00Z",
            "action_network:person_id": "699da712-929f-11e3-a2e9-12313d316c29",
            "action_network:petition_id": "fake_id",
            "comments": "Stop doing the thing",
            "_links": {
                "self": {"href": f"{self.api_url}/petitions/fake_id/signatures/fake_id"},
                "osdi:petition": {"href": f"{self.api_url}/petitions/fake_id"},
                "osdi:person": {
                    "href": f"{self.api_url}/people/699da712-929f-11e3-a2e9-12313d316c29"
                },
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

        # Submissions
        self.fake_submissions = {
            "total_pages": 1,
            "per_page": 25,
            "page": 1,
            "total_records": 4,
            "_links": {
                "self": {"href": f"{self.api_url}/forms/fake_id/submissions"},
                "osdi:submissions": [
                    {"href": f"{self.api_url}/forms/fake_id/submissions/fake_id"},
                    {"href": f"{self.api_url}/forms/fake_id/submissions/fake_id"},
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
                            "self": {"href": f"{self.api_url}/forms/fake_id/submissions/fake_id"},
                            "osdi:form": {"href": f"{self.api_url}/forms/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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
                            "self": {"href": f"{self.api_url}/forms/fake_id/submissions/fake_id"},
                            "osdi:form": {"href": f"{self.api_url}/forms/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                    },
                ]
            },
        }
        self.fake_submission = {
            "identifiers": ["action_network:fake_id"],
            "created_date": "2014-03-25T15:26:45Z",
            "modified_date": "2014-03-25T15:26:46Z",
            "action:person_id": "fake_id",
            "action_network:form_id": "fake_id",
            "_links": {
                "self": {"href": f"{self.api_url}/forms/fake_id/submissions/fake_id"},
                "osdi:form": {"href": f"{self.api_url}/forms/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # Tags
        self.fake_tags = {
            "total_pages": 10,
            "per_page": 25,
            "page": 1,
            "total_records": 243,
            "_links": {
                "next": {"href": f"{self.api_url}/tags?page=2"},
                "self": {"href": f"{self.api_url}/tags"},
                "osdi:tags": [
                    {"href": f"{self.api_url}/tags/fake_id"},
                    {"href": f"{self.api_url}/tags/fake_id"},
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
                            "self": {"href": f"{self.api_url}/tags/fake_id"},
                            "osdi:taggings": {"href": f"{self.api_url}/tags/fake_id/taggings"},
                        },
                    },
                    {
                        "identifiers": ["action_network:fake_id"],
                        "created_date": "2014-03-24T18:26:42Z",
                        "modified_date": "2014-03-24T18:27:17Z",
                        "name": "Economic Justice",
                        "_links": {
                            "self": {"href": f"{self.api_url}/tags/fake_id"},
                            "osdi:taggings": {"href": f"{self.api_url}/tags/fake_id/taggings"},
                        },
                    },
                ]
            },
        }

        # Taggings
        self.fake_taggings = {
            "total_pages": 5,
            "per_page": 25,
            "page": 1,
            "total_records": 123,
            "_links": {
                "next": {"href": f"{self.api_url}/tags/fake_id/taggings?page=2"},
                "self": {"href": f"{self.api_url}/tags/fake_id/taggings"},
                "osdi:taggings": [
                    {"href": f"{self.api_url}/tags/fake_id/taggings/fake_id"},
                    {"href": f"{self.api_url}/tags/fake_id/taggings/fake_id"},
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
                            "self": {"href": f"{self.api_url}/tags/fake_id/taggings/fake_id"},
                            "osdi:tag": {"href": f"{self.api_url}/tags/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                        "identifiers": ["action_network:fake_id"],
                        "created_date": "2014-03-18T22:25:31Z",
                        "modified_date": "2014-03-18T22:25:38Z",
                        "item_type": "osdi:person",
                    },
                    {
                        "_links": {
                            "self": {"href": f"{self.api_url}/tags/fake_id/taggings/fake_id"},
                            "osdi:tag": {"href": f"{self.api_url}/tags/fake_id"},
                            "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
                        },
                        "identifiers": ["action_network:fake_id"],
                        "created_date": "2014-03-18T22:24:24Z",
                        "modified_date": "2014-03-18T22:24:24Z",
                        "item_type": "osdi:person",
                    },
                ]
            },
        }
        self.fake_tagging = {
            "_links": {
                "self": {"href": f"{self.api_url}/tags/fake_id/taggings/fake_id"},
                "osdi:tag": {"href": f"{self.api_url}/tags/fake_id"},
                "osdi:person": {"href": f"{self.api_url}/people/fake_id"},
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

        # Wrappers
        self.fake_wrappers = {
            "total_pages": 7,
            "per_page": 25,
            "page": 1,
            "total_records": 162,
            "_links": {
                "next": {"href": f"{self.api_url}/wrappers?page=2"},
                "self": {"href": f"{self.api_url}/wrappers"},
                "osdi:wrappers": [
                    {"href": f"{self.api_url}/wrappers/fake_id"},
                    {"href": f"{self.api_url}/wrappers/fake_id"},
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
                        "header": '<table border="0" cellpadding="10" '
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
                        '<img src="https://actionnetwork.org/images/logo.png" />',
                        "footer": "\r\n</div>\r\n    "
                        " </td>\r\n "
                        "       </tr>\r\n  "
                        "    </table>\r\n  "
                        "  </td>\r\n "
                        " </tr>\r\n</table>",
                        "action_network:suffix": " via ProgressivePower.org",
                        "wrapper_type": "email",
                        "default": True,
                        "_links": {"self": {"href": f"{self.api_url}/wrappers/fake_id"}},
                    },
                    {
                        "identifiers": ["action_network:fake_id"],
                        "origin_system": "Action Network",
                        "created_date": "2014-03-14T15:21:05Z",
                        "modified_date": "2014-03-17T19:56:11Z",
                        "name": "No logo",
                        "administrative_url": "https://actionnetwork.org/wrappers/2/edit",
                        "header": '<table border="0" cellpadding="10" '
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
                        '150%;text-align: left;">\r\n',
                        "footer": "\r\n</div>\r\n "
                        "         </td>\r\n   "
                        "     </tr>\r\n      </table>\r\n "
                        "   </td>\r\n "
                        " </tr>\r\n</table>",
                        "wrapper_type": "email",
                        "default": False,
                        "_links": {"self": {"href": f"{self.api_url}/wrappers/fake_id"}},
                    },
                ]
            },
        }
        self.fake_wrapper = {
            "identifiers": ["action_network:fake_id"],
            "origin_system": "Action Network",
            "created_date": "2014-03-24T18:03:45Z",
            "modified_date": "2014-03-25T15:00:22Z",
            "name": "Default wrapper -- logo only",
            "administrative_url": "https://actionnetwork.org/wrappers/1/edit",
            "header": '<table border="0" cellpadding="10" '
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
            '<img src="https://actionnetwork.org/images/logo.png" />',
            "footer": "\r\n</div>\r\n"
            "          </td>\r\n"
            "        </tr>\r\n"
            "      </table>\r\n"
            "    </td>\r\n "
            " </tr>\r\n</table>",
            "action_network:suffix": " via ProgressivePower.org",
            "wrapper_type": "email",
            "default": True,
            "_links": {
                "self": {"href": f"{self.api_url}/wrappers/fake_id"},
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

        self.fake_unique_id_lists = {
            "total_pages": 3,
            "per_page": 25,
            "page": 1,
            "total_records": 50,
            "_links": {
                "next": {"href": f"{self.api_url}/unique_id_lists?page=2"},
                "self": {"href": f"{self.api_url}/unique_id_lists"},
                "osdi:unique_id_lists": [
                    {"href": f"{self.api_url}/unique_id_lists/fake_id"},
                    {"href": f"{self.api_url}/unique_id_lists/fake_id"},
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

    @requests_mock.Mocker()
    def test_get_page(self, m):
        m.get(
            f"{self.api_url}/people?page=2&per_page=2",
            text=json.dumps(self.fake_people_list_2),
        )
        self.assertEqual(self.an._get_page("people", 2, 2), self.fake_people_list_2)

    @requests_mock.Mocker()
    def test_get_entry_list(self, m):
        m.get(
            f"{self.api_url}/people?page=1&per_page=25",
            text=json.dumps(self.fake_people_list_1),
        )
        m.get(
            f"{self.api_url}/people?page=2&per_page=25",
            text=json.dumps(self.fake_people_list_2),
        )
        m.get(
            f"{self.api_url}/people?page=3&per_page=25",
            text=json.dumps({"_embedded": {"osdi:people": []}}),
        )
        assert_matching_tables(self.an._get_entry_list("people"), Table(self.fake_people_list))

    @requests_mock.Mocker()
    def test_filter_get_people(self, m):
        m.get(
            f"{self.api_url}/people?page=1&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps(self.fake_people_list_1),
        )
        m.get(
            f"{self.api_url}/people?page=2&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps(self.fake_people_list_2),
        )
        m.get(
            f"{self.api_url}/people?page=3&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps({"_embedded": {"osdi:people": []}}),
        )
        assert_matching_tables(
            self.an.get_people(filter=self.fake_filter_by_email_1),
            Table(self.fake_people_list),
        )

    @requests_mock.Mocker()
    def test_filter_get_entry_list(self, m):
        m.get(
            f"{self.api_url}/people?page=1&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps(self.fake_people_list_1),
        )
        m.get(
            f"{self.api_url}/people?page=2&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps(self.fake_people_list_2),
        )
        m.get(
            f"{self.api_url}/people?page=3&per_page=25&filter={self.fake_filter_by_email_1}",
            text=json.dumps({"_embedded": {"osdi:people": []}}),
        )
        assert_matching_tables(
            self.an._get_entry_list("people", filter=self.fake_filter_by_email_1),
            Table(self.fake_people_list),
        )

    @requests_mock.Mocker()
    def test_filter_on_get_unsupported_entry(self, m):
        m.get(
            f"{self.api_url}/tags?page=1&per_page=25&filter={self.fake_tag_filter}",
            text=json.dumps(self.fake_tag_list),
        )
        m.get(
            f"{self.api_url}/tags?page=2&per_page=25&filter={self.fake_tag_filter}",
            text=json.dumps({"_embedded": {"osdi:tags": []}}),
        )
        assert_matching_tables(
            self.an._get_entry_list("tags", filter=self.fake_tag_filter),
            Table(self.fake_tag_list["_embedded"]["osdi:tags"]),
        )

    # Advocacy Campaigns
    @requests_mock.Mocker()
    def test_get_advocacy_campaigns(self, m):
        m.get(
            f"{self.api_url}/advocacy_campaigns",
            text=json.dumps(self.fake_advocacy_campaigns),
        )
        assert_matching_tables(
            self.an._get_entry_list("advocacy_campaigns", 1),
            self.fake_advocacy_campaigns["_embedded"][
                list(self.fake_advocacy_campaigns["_embedded"])[0]
            ],
        )

    @requests_mock.Mocker()
    def test_get_advocacy_campaign(self, m):
        m.get(
            f"{self.api_url}/advocacy_campaigns/123",
            text=json.dumps(self.fake_advocacy_campaign),
        )

        assert_matching_tables(
            self.an.get_advocacy_campaign("123"),
            self.fake_advocacy_campaign,
        )

    # Attendances
    @requests_mock.Mocker()
    def test_get_person_attendances(self, m):
        m.get(
            f"{self.api_url}/people/123/attendances",
            text=json.dumps(self.fake_attendances),
        )
        assert_matching_tables(
            self.an.get_person_attendances("123", 1),
            self.fake_attendances["_embedded"][list(self.fake_attendances["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_event_attendances(self, m):
        m.get(
            f"{self.api_url}/events/123/attendances",
            text=json.dumps(self.fake_attendances),
        )
        assert_matching_tables(
            self.an.get_event_attendances("123", 1),
            self.fake_attendances["_embedded"][list(self.fake_attendances["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_create_attendance(self, m):
        m.post(
            f"{self.api_url}/events/123/attendances",
            text=json.dumps(self.fake_attendance),
        )

        assert_matching_tables(
            self.an.create_attendance("123", self.fake_attendance),
            self.fake_attendance,
        )

    @requests_mock.Mocker()
    def test_update_attendance(self, m):
        m.put(
            f"{self.api_url}/events/123/attendances/123",
            text=json.dumps(self.fake_attendance),
        )

        assert_matching_tables(
            self.an.update_attendance("123", "123", self.fake_attendance),
            self.fake_attendance,
        )

    @requests_mock.Mocker()
    def test_get_person_attendance(self, m):
        m.get(
            f"{self.api_url}/people/123/attendances/123",
            text=json.dumps(self.fake_attendance),
        )

        assert_matching_tables(
            self.an.get_person_attendance("123", "123"),
            self.fake_attendance,
        )

    @requests_mock.Mocker()
    def test_get_event_attendance(self, m):
        m.get(
            f"{self.api_url}/events/123/attendances/123",
            text=json.dumps(self.fake_attendance),
        )

        assert_matching_tables(
            self.an.get_event_attendance("123", "123"),
            self.fake_attendance,
        )

    # Campaigns
    @requests_mock.Mocker()
    def test_get_campaigns(self, m):
        m.get(f"{self.api_url}/campaigns", text=json.dumps(self.fake_campaigns))
        assert_matching_tables(
            self.an.get_campaigns(1),
            self.fake_campaigns["_embedded"][list(self.fake_campaigns["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_campaign(self, m):
        m.get(
            f"{self.api_url}/campaigns/123",
            text=json.dumps(self.fake_campaign),
        )

        assert_matching_tables(
            self.an.get_campaign("123"),
            self.fake_campaign,
        )

    # Custom Fields
    @requests_mock.Mocker()
    def test_get_custom_fields(self, m):
        m.get(
            f"{self.api_url}/metadata/custom_fields",
            text=json.dumps(self.fake_custom_fields),
        )

        assert_matching_tables(
            self.an.get_custom_fields(),
            self.fake_custom_fields,
        )

    # Donations
    @requests_mock.Mocker()
    def test_get_donations(self, m):
        m.get(f"{self.api_url}/donations", text=json.dumps(self.fake_donations))
        assert_matching_tables(
            self.an.get_donations(1),
            self.fake_donations["_embedded"][list(self.fake_donations["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_fundraising_page_donations(self, m):
        m.get(
            f"{self.api_url}/fundraising_pages/123/donations",
            text=json.dumps(self.fake_donations),
        )
        assert_matching_tables(
            self.an.get_fundraising_page_donations("123", 1),
            self.fake_donations["_embedded"][list(self.fake_donations["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_person_donations(self, m):
        m.get(f"{self.api_url}/people/123/donations", text=json.dumps(self.fake_donations))
        assert_matching_tables(
            self.an.get_person_donations("123", 1),
            self.fake_donations["_embedded"][list(self.fake_donations["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_donation(self, m):
        m.get(f"{self.api_url}/donations/123", text=json.dumps(self.fake_donation))
        assert_matching_tables(
            self.an.get_donation("123"),
            self.fake_donation,
        )

    # Embeds
    @requests_mock.Mocker()
    def test_get_embeds(self, m):
        m.get(f"{self.api_url}/forms/123/embed", text=json.dumps(self.fake_embed))
        assert_matching_tables(
            self.an.get_embeds("forms", "123"),
            self.fake_embed,
        )

    # Event Campaigns
    @requests_mock.Mocker()
    def test_get_event_campaigns(self, m):
        m.get(
            f"{self.api_url}/event_campaigns",
            text=json.dumps(self.fake_event_campaigns),
        )
        assert_matching_tables(
            self.an.get_event_campaigns(1),
            self.fake_event_campaigns["_embedded"][list(self.fake_event_campaigns["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_event_campaign(self, m):
        m.get(
            f"{self.api_url}/event_campaigns/123",
            text=json.dumps(self.fake_event_campaign),
        )
        assert_matching_tables(
            self.an.get_event_campaign("123"),
            self.fake_event_campaign,
        )

    @requests_mock.Mocker()
    def test_create_event_campaign(self, m):
        payload = {"title": "Canvassing Events", "origin_system": "AmyforTexas.com"}
        m.post(f"{self.api_url}/event_campaigns", text=json.dumps(self.fake_event_campaign))
        self.assertEqual(
            self.fake_event_campaign,
            self.an.create_event_campaign(payload),
        )

    @requests_mock.Mocker()
    def test_create_event_in_event_campaign(self, m):
        payload = {
            "title": "My Canvassing Event",
            "origin_system": "CanvassingEvents.com",
        }
        m.post(
            f"{self.api_url}/event_campaigns/123/events",
            text=json.dumps(self.fake_event),
        )
        self.assertEqual(
            self.fake_event.items(),
            self.an.create_event_in_event_campaign("123", payload).items(),
        )

    @requests_mock.Mocker()
    def test_update_event_campaign(self, m):
        payload = {"description": "This is my new event campaign description"}
        m.put(
            f"{self.api_url}/event_campaigns/123",
            text=json.dumps(self.fake_event_campaign),
        )
        self.assertEqual(
            self.fake_event_campaign,
            self.an.update_event_campaign("123", payload),
        )

    # Events
    @requests_mock.Mocker()
    def test_get_events(self, m):
        m.get(f"{self.api_url}/events", text=json.dumps(self.fake_events))
        assert_matching_tables(
            self.an.get_events(1),
            self.fake_events["_embedded"][list(self.fake_events["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_event_campaign_events(self, m):
        m.get(
            f"{self.api_url}/event_campaigns/123/events",
            text=json.dumps(self.fake_events),
        )
        assert_matching_tables(
            self.an.get_event_campaign_events("123", 1),
            self.fake_events["_embedded"][list(self.fake_events["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_event(self, m):
        m.get(f"{self.api_url}/events/123", text=json.dumps(self.fake_event2))
        assert_matching_tables(
            self.an.get_event("123"),
            self.fake_event2,
        )

    @requests_mock.Mocker()
    def test_create_event(self, m):
        m.post(f"{self.api_url}/events", text=json.dumps(self.fake_event))
        self.assertEqual(
            self.fake_event.items(),
            self.an.create_event(
                "fake_title", start_date=self.fake_date, location=self.fake_location
            ).items(),
        )

    # Forms
    @requests_mock.Mocker()
    def test_get_forms(self, m):
        m.get(
            f"{self.api_url}/forms",
            text=json.dumps(self.fake_forms),
        )
        assert_matching_tables(
            self.an.get_forms(1),
            self.fake_forms["_embedded"][list(self.fake_forms["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_form(self, m):
        m.get(f"{self.api_url}/forms/123", text=json.dumps(self.fake_form))
        assert_matching_tables(
            self.an.get_form("123"),
            self.fake_form,
        )

    @requests_mock.Mocker()
    def test_create_form(self, m):
        payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
        m.post(f"{self.api_url}/forms", text=json.dumps(self.fake_form))
        self.assertEqual(
            self.fake_form.items(),
            self.an.create_form(payload).items(),
        )

    # Update Form
    @requests_mock.Mocker()
    def test_update_form(self, m):
        payload = {"title": "My Free Form", "origin_system": "FreeForms.com"}
        m.put(f"{self.api_url}/forms/123", text=json.dumps(self.fake_form))
        self.assertEqual(
            self.fake_form.items(),
            self.an.update_form("123", payload).items(),
        )

    # Fundraising Pages
    @requests_mock.Mocker()
    def test_get_fundraising_pages(self, m):
        m.get(
            f"{self.api_url}/fundraising_pages",
            text=json.dumps(self.fake_fundraising_pages),
        )
        assert_matching_tables(
            self.an.get_fundraising_pages(1),
            self.fake_fundraising_pages["_embedded"][
                list(self.fake_fundraising_pages["_embedded"])[0]
            ],
        )

    @requests_mock.Mocker()
    def test_get_fundraising_page(self, m):
        m.get(
            f"{self.api_url}/fundraising_pages/123",
            text=json.dumps(self.fake_fundraising_page),
        )
        assert_matching_tables(
            self.an.get_fundraising_page("123"),
            self.fake_fundraising_page,
        )

    @requests_mock.Mocker()
    def test_create_fundraising_page(self, m):
        payload = {
            "title": "My Free Fundraiser",
            "origin_system": "FreeFundraisers.com",
        }
        m.post(
            f"{self.api_url}/fundraising_pages",
            text=json.dumps(self.fake_fundraising_page),
        )
        self.assertEqual(
            self.fake_fundraising_page.items(),
            self.an.create_fundraising_page(payload).items(),
        )

    @requests_mock.Mocker()
    def test_update_fundraising_page(self, m):
        payload = {
            "title": "My Free Fundraiser With A New Name",
            "description": "This is my free fundraiser description",
        }
        m.put(
            f"{self.api_url}/fundraising_pages/123",
            text=json.dumps(self.fake_fundraising_page),
        )
        self.assertEqual(
            self.fake_fundraising_page.items(),
            self.an.update_fundraising_page("123", payload).items(),
        )

    # Items
    @requests_mock.Mocker()
    def test_get_items(self, m):
        m.get(
            f"{self.api_url}/lists/123/items",
            text=json.dumps(self.fake_items),
        )
        assert_matching_tables(
            self.an.get_items("123", 1),
            self.fake_items["_embedded"][list(self.fake_items["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_item(self, m):
        m.get(f"{self.api_url}/lists/123/items/123", text=json.dumps(self.fake_item))
        assert_matching_tables(
            self.an.get_item("123", "123"),
            self.fake_item,
        )

    # Lists
    @requests_mock.Mocker()
    def test_get_lists(self, m):
        m.get(
            f"{self.api_url}/lists",
            text=json.dumps(self.fake_lists),
        )
        assert_matching_tables(
            self.an.get_lists(1),
            self.fake_lists["_embedded"][list(self.fake_lists["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_list(self, m):
        m.get(f"{self.api_url}/lists/123", text=json.dumps(self.fake_list))
        assert_matching_tables(
            self.an.get_list("123"),
            self.fake_list,
        )

    # Messages
    @requests_mock.Mocker()
    def test_get_messages(self, m):
        m.get(
            f"{self.api_url}/messages",
            text=json.dumps(self.fake_messages),
        )
        assert_matching_tables(
            self.an.get_messages(1),
            self.fake_messages["_embedded"][list(self.fake_messages["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_message(self, m):
        m.get(f"{self.api_url}/messages/123", text=json.dumps(self.fake_message))
        assert_matching_tables(
            self.an.get_message("123"),
            self.fake_message,
        )

    @requests_mock.Mocker()
    def test_create_message(self, m):
        payload = {
            "subject": "Stop doing the bad thing",
            "body": "<p>The mayor should stop doing the bad thing.</p>",
            "from": "Progressive Action Now",
            "reply_to": "jane@progressiveactionnow.org",
            "targets": [{"href": "https://actionnetwork.org/api/v2/queries/123"}],
            "_links": {"osdi:wrapper": {"href": "https://actionnetwork.org/api/v2/wrappers/123"}},
        }
        m.post(f"{self.api_url}/messages", text=json.dumps(self.fake_message))
        assert_matching_tables(
            self.an.create_message(payload),
            self.fake_message,
        )

    @requests_mock.Mocker()
    def test_update_message(self, m):
        message_id = "123"
        payload = {
            "name": "Stop doing the bad thing email send 1",
            "subject": "Please! Stop doing the bad thing",
        }
        m.put(f"{self.api_url}/messages/123", text=json.dumps(self.fake_message))
        assert_matching_tables(
            self.an.update_message(message_id, payload),
            self.fake_message,
        )

    # Metadata
    @requests_mock.Mocker()
    def test_get_metadata(self, m):
        m.get(f"{self.api_url}/metadata", text=json.dumps(self.fake_metadata))
        assert_matching_tables(
            self.an.get_metadata(),
            self.fake_metadata,
        )

    # Outreaches
    @requests_mock.Mocker()
    def test_get_advocacy_campaign_outreaches(self, m):
        m.get(
            f"{self.api_url}/advocacy_campaigns/123/outreaches",
            text=json.dumps(self.fake_outreaches),
        )
        assert_matching_tables(
            self.an.get_advocacy_campaign_outreaches("123", 1),
            self.fake_outreaches["_embedded"][list(self.fake_outreaches["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_person_outreaches(self, m):
        m.get(
            f"{self.api_url}/people/123/outreaches",
            text=json.dumps(self.fake_outreaches),
        )
        assert_matching_tables(
            self.an.get_person_outreaches("123", 1),
            self.fake_outreaches["_embedded"][list(self.fake_outreaches["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_advocacy_campaign_outreach(self, m):
        m.get(
            f"{self.api_url}/advocacy_campaigns/123/outreaches/123",
            text=json.dumps(self.fake_outreach),
        )
        assert_matching_tables(
            self.an.get_advocacy_campaign_outreach("123", "123"),
            self.fake_outreach,
        )

    @requests_mock.Mocker()
    def test_get_person_outreach(self, m):
        m.get(
            f"{self.api_url}/people/123/outreaches/123",
            text=json.dumps(self.fake_outreach),
        )
        assert_matching_tables(
            self.an.get_person_outreach("123", "123"),
            self.fake_outreach,
        )

    @requests_mock.Mocker()
    def test_create_outreach(self, m):
        payload = {
            "targets": [{"given_name": "Joe", "family_name": "Schmoe"}],
            "_links": {"osdi:person": {"href": "https://actionnetwork.org/api/v2/people/123"}},
        }
        id = self.fake_advocacy_campaign["identifiers"][0].split(":")[-1]
        m.post(
            f"{self.api_url}/advocacy_campaigns/{id}/outreaches",
            text=json.dumps(self.fake_outreach),
        )
        assert_matching_tables(
            self.an.create_outreach(id, payload),
            self.fake_outreach,
        )

        @requests_mock.Mocker()
        def test_update_outreach(self, m):
            payload = {"subject": "Please vote no!"}
            id = self.fake_advocacy_campaign["identifiers"][0].split(":")[-1]
            m.put(
                f"{self.api_url}/advocacy_campaigns/{id}/outreaches/123",
                text=json.dumps(self.fake_outreach),
            )
            assert_matching_tables(
                self.an.update_outreach(
                    self.fake_advocacy_campaign["identifiers"][0].split(":")[-1],
                    "123",
                    payload,
                ),
                self.fake_outreach,
            )

    # People
    @requests_mock.Mocker()
    def test_get_people(self, m):
        m.get(
            f"{self.api_url}/people?page=1&per_page=25",
            text=json.dumps(self.fake_people_list_1),
        )
        m.get(
            f"{self.api_url}/people?page=2&per_page=25",
            text=json.dumps(self.fake_people_list_2),
        )
        m.get(
            f"{self.api_url}/people?page=3&per_page=25",
            text=json.dumps({"_embedded": {"osdi:people": []}}),
        )
        assert_matching_tables(self.an.get_people(), Table(self.fake_people_list))

    @requests_mock.Mocker()
    def test_get_person(self, m):
        m.get(
            f"{self.api_url}/people/{self.fake_person_id_1}",
            text=json.dumps(self.fake_person),
        )
        self.assertEqual(self.an.get_person(self.fake_person_id_1), self.fake_person)

    @requests_mock.Mocker()
    def test_upsert_person(self, m):
        m.post(f"{self.api_url}/people", text=json.dumps(self.fake_upsert_person))
        self.assertEqual(self.an.upsert_person(**self.fake_upsert_person), self.fake_upsert_person)

    @requests_mock.Mocker()
    def test_update_person(self, m):
        m.put(
            f"{self.api_url}/people/{self.fake_person_id_1}",
            text=json.dumps(self.updated_fake_person),
        )
        self.assertEqual(
            self.an.update_person(
                self.fake_person_id_1, given_name="Flake", family_name="McFlakerson"
            ),
            self.updated_fake_person,
        )

    # Petitions
    @requests_mock.Mocker()
    def test_get_petitions(self, m):
        m.get(
            f"{self.api_url}/petitions",
            text=json.dumps(self.fake_petitions),
        )
        assert_matching_tables(
            self.an.get_petitions(1),
            self.fake_petitions["_embedded"][list(self.fake_petitions["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_petition(self, m):
        m.get(f"{self.api_url}/petitions/123", text=json.dumps(self.fake_petition))
        assert_matching_tables(
            self.an.get_petition("123"),
            self.fake_petition,
        )

    # Queries
    @requests_mock.Mocker()
    def test_create_petition(self, m):
        fake_petition_data = {
            "title": self.fake_petition["title"],
            "description": self.fake_petition["description"],
            "petition_text": self.fake_petition["petition_text"],
            "target": self.fake_petition["target"],
        }

        m.post(
            f"{self.api_url}/petitions",
            text=json.dumps(fake_petition_data),
        )
        response = self.an.create_petition(
            self.fake_petition["title"],
            self.fake_petition["description"],
            self.fake_petition["petition_text"],
            self.fake_petition["target"],
        )
        assert_matching_tables(response, fake_petition_data)

    @requests_mock.Mocker()
    def test_update_petition(self, m):
        fake_petition_data = {
            "title": self.fake_petition["title"],
            "description": self.fake_petition["description"],
            "petition_text": self.fake_petition["petition_text"],
            "target": self.fake_petition["target"],
        }

        m.put(
            self.api_url + "/petitions/" + self.fake_petition["identifiers"][0].split(":")[1],
            text=json.dumps(fake_petition_data),
        )
        response = self.an.update_petition(
            self.fake_petition["identifiers"][0].split(":")[1],
            title=self.fake_petition["title"],
            description=self.fake_petition["description"],
            petition_text=self.fake_petition["petition_text"],
            target=self.fake_petition["target"],
        )
        assert_matching_tables(response, fake_petition_data)

    # Queries
    @requests_mock.Mocker()
    def test_get_queries(self, m):
        m.get(
            f"{self.api_url}/queries",
            text=json.dumps(self.fake_queries),
        )
        assert_matching_tables(
            self.an.get_queries(1),
            self.fake_queries["_embedded"][list(self.fake_queries["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_query(self, m):
        m.get(f"{self.api_url}/queries/123", text=json.dumps(self.fake_query))
        assert_matching_tables(
            self.an.get_query("123"),
            self.fake_query,
        )

    # Signatures
    @requests_mock.Mocker()
    def test_get_petition_signatures(self, m):
        m.get(
            f"{self.api_url}/petitions/123/signatures",
            text=json.dumps(self.fake_signatures),
        )
        assert_matching_tables(
            self.an.get_petition_signatures("123", 1),
            self.fake_signatures["_embedded"][list(self.fake_signatures["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_person_signatures(self, m):
        m.get(
            f"{self.api_url}/people/123/signatures",
            text=json.dumps(self.fake_signatures),
        )
        assert_matching_tables(
            self.an.get_person_signatures("123", 1),
            self.fake_signatures["_embedded"][list(self.fake_signatures["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_petition_signature(self, m):
        m.get(
            f"{self.api_url}/petitions/123/signatures/123",
            text=json.dumps(self.fake_signature),
        )
        assert_matching_tables(
            self.an.get_petition_signature("123", "123"),
            self.fake_signature,
        )

    @requests_mock.Mocker()
    def test_get_person_signature(self, m):
        m.get(
            f"{self.api_url}/people/123/signatures/123",
            text=json.dumps(self.fake_signature),
        )
        assert_matching_tables(
            self.an.get_person_signature("123", "123"),
            self.fake_signature,
        )

    @requests_mock.Mocker()
    def test_create_signature(self, m):
        # Define the fake signature data
        fake_signature_data = {
            "comments": self.fake_signature["comments"],
            "_links": {
                "osdi:person": {"href": self.fake_signature["_links"]["osdi:person"]["href"]}
            },
        }

        # Mock the POST request to Action Network's signatures endpoint
        m.post(
            f"{self.api_url}/petitions/456/signatures",
            text=json.dumps(self.fake_signature),
        )

        # Call the method to create the signature
        created_signature = self.an.create_signature("456", fake_signature_data)

        # Assert that the correct data is being sent and the response is handled correctly
        assert_matching_tables(created_signature, self.fake_signature)

    @requests_mock.Mocker()
    def test_update_signature(self, m):
        # Define the fake signature data with updated comments
        updated_signature_data = {
            "comments": "Updated comments",
        }

        # Mock the PATCH request to update the signature
        m.put(
            f"{self.api_url}/petitions/456/signatures/123",
            text=json.dumps(self.fake_signature),
        )

        # Call the method to update the signature
        updated_signature = self.an.update_signature("456", "123", updated_signature_data)

        # Assert that the correct data is being sent and the response is handled correctly
        assert_matching_tables(updated_signature, self.fake_signature)

    # Submissions
    @requests_mock.Mocker()
    def test_get_form_submissions(self, m):
        m.get(
            f"{self.api_url}/forms/123/submissions",
            text=json.dumps(self.fake_submissions),
        )
        assert_matching_tables(
            self.an.get_form_submissions("123", 1),
            self.fake_submissions["_embedded"][list(self.fake_submissions["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_person_submissions(self, m):
        m.get(
            f"{self.api_url}/people/123/submissions",
            text=json.dumps(self.fake_submissions),
        )
        assert_matching_tables(
            self.an.get_person_submissions("123", 1),
            self.fake_submissions["_embedded"][list(self.fake_submissions["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_form_submission(self, m):
        m.get(
            f"{self.api_url}/forms/123/submissions/123",
            text=json.dumps(self.fake_submission),
        )
        assert_matching_tables(
            self.an.get_form_submission("123", "123"),
            self.fake_submission,
        )

    @requests_mock.Mocker()
    def test_get_person_submission(self, m):
        m.get(
            f"{self.api_url}/people/123/submissions/123",
            text=json.dumps(self.fake_submission),
        )
        assert_matching_tables(
            self.an.get_person_submission("123", "123"),
            self.fake_submission,
        )

    # Submissions
    @requests_mock.Mocker()
    def test_create_submission(self, m):
        m.post(
            f"{self.api_url}/forms/123/submissions",
            text=json.dumps(self.fake_submission),
        )
        assert_matching_tables(
            self.an.create_submission("123", "123"),
            self.fake_submission,
        )

    @requests_mock.Mocker()
    def test_update_submission(self, m):
        m.put(
            f"{self.api_url}/forms/123/submissions/123",
            json={"identifiers": ["other-system:230125s"]},
        )
        assert_matching_tables(
            self.an.update_submission("123", "123", {"identifiers": ["other-system:230125s"]}),
            self.fake_submission,
        )

    # Tags
    @requests_mock.Mocker()
    def test_get_tags(self, m):
        m.get(
            f"{self.api_url}/tags?page=1&per_page=25",
            text=json.dumps(self.fake_tag_list),
        )
        m.get(
            f"{self.api_url}/tags?page=2&per_page=25",
            text=json.dumps({"_embedded": {"osdi:tags": []}}),
        )
        assert_matching_tables(
            self.an.get_tags(), Table(self.fake_tag_list["_embedded"]["osdi:tags"])
        )

    @requests_mock.Mocker()
    def test_get_tag(self, m):
        m.get(f"{self.api_url}/tags/{self.fake_tag_id_1}", text=json.dumps(self.fake_tag))
        self.assertEqual(self.an.get_tag(self.fake_tag_id_1), self.fake_tag)

    # Taggings
    @requests_mock.Mocker()
    def test_get_taggings(self, m):
        m.get(
            f"{self.api_url}/tags/123/taggings",
            text=json.dumps(self.fake_taggings),
        )
        assert_matching_tables(
            self.an.get_taggings("123", 1),
            self.fake_taggings["_embedded"][list(self.fake_taggings["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_tagging(self, m):
        m.get(f"{self.api_url}/tags/123/taggings/123", text=json.dumps(self.fake_tagging))
        assert_matching_tables(
            self.an.get_tagging("123", "123"),
            self.fake_tagging,
        )

    @requests_mock.Mocker()
    def test_create_tagging(self, m):
        m.post(
            f"{self.api_url}/tags/123/taggings",
            json=self.fake_tagging,
        )
        assert_matching_tables(
            self.an.create_tagging("123", self.fake_tagging),
            self.fake_tagging,
        )

    @requests_mock.Mocker()
    def test_delete_tagging(self, m):
        m.delete(
            f"{self.api_url}/tags/123/taggings/123",
            text=json.dumps({"notice": "This tagging was successfully deleted."}),
        )
        assert_matching_tables(
            self.an.delete_tagging("123", "123"),
            {"notice": "This tagging was successfully deleted."},
        )

    # Wrappers
    @requests_mock.Mocker()
    def test_get_wrappers(self, m):
        m.get(
            f"{self.api_url}/wrappers",
            text=json.dumps(self.fake_wrappers),
        )
        assert_matching_tables(
            self.an.get_wrappers(1),
            self.fake_wrappers["_embedded"][list(self.fake_wrappers["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_wrapper(self, m):
        m.get(f"{self.api_url}/wrappers/123", text=json.dumps(self.fake_wrapper))
        assert_matching_tables(
            self.an.get_wrapper("123"),
            self.fake_wrapper,
        )

    # Unique ID Lists
    @requests_mock.Mocker()
    def test_get_unique_id_lists(self, m):
        m.get(
            f"{self.api_url}/unique_id_lists",
            text=json.dumps(self.fake_unique_id_lists),
        )
        assert_matching_tables(
            self.an.get_unique_id_lists(1),
            self.fake_unique_id_lists["_embedded"][list(self.fake_unique_id_lists["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_get_unique_id_list(self, m):
        m.get(
            f"{self.api_url}/unique_id_lists/123",
            text=json.dumps(
                self.fake_unique_id_lists["_embedded"][
                    list(self.fake_unique_id_lists["_embedded"])[0]
                ]
            ),
        )
        assert_matching_tables(
            self.an.get_unique_id_list("123"),
            self.fake_unique_id_lists["_embedded"][list(self.fake_unique_id_lists["_embedded"])[0]],
        )

    @requests_mock.Mocker()
    def test_create_unique_id_list(self, m):
        m.post(
            f"{self.api_url}/unique_id_lists",
            text=json.dumps(
                {
                    "name": self.fake_unique_id_list["name"],
                    "count": len(self.fake_unique_id_list["unique_ids"]),
                }
            ),
        )
        self.assertEqual(
            len(self.fake_unique_id_list["unique_ids"]),
            self.an.create_unique_id_list(
                self.fake_unique_id_list["name"], self.fake_unique_id_list["unique_ids"]
            )["count"],
        )
