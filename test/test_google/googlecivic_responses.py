# flake8: noqa
elections_resp = {
    "kind": "civicinfo#electionsQueryResponse",
    "elections": [
        {
            "id": "2000",
            "name": "VIP Test Election",
            "electionDay": "2021-06-06",
            "ocdDivisionId": "ocd-division/country:us",
        },
        {
            "id": "4803",
            "name": "Los Angeles County Election",
            "electionDay": "2019-05-14",
            "ocdDivisionId": "ocd-division/country:us/state:ca/county:los_angeles",
        },
        {
            "id": "4804",
            "name": "Oklahoma Special Election",
            "electionDay": "2019-05-14",
            "ocdDivisionId": "ocd-division/country:us/state:ok",
        },
        {
            "id": "4810",
            "name": "Oregon County Special Elections",
            "electionDay": "2019-05-21",
            "ocdDivisionId": "ocd-division/country:us/state:or",
        },
        {
            "id": "4811",
            "name": "Los Angeles County Special Election",
            "electionDay": "2019-06-04",
            "ocdDivisionId": "ocd-division/country:us/state:ca/county:los_angeles",
        },
        {
            "id": "4823",
            "name": "9th Congressional District Primary Election",
            "electionDay": "2019-05-14",
            "ocdDivisionId": "ocd-division/country:us/state:nc/cd:9",
        },
    ],
}

voterinfo_resp = {
    "kind": "civicinfo#voterInfoResponse",
    "election": {
        "id": "2000",
        "name": "VIP Test Election",
        "electionDay": "2021-06-06",
        "ocdDivisionId": "ocd-division/country:us",
    },
    "normalizedInput": {
        "line1": "900 North Washtenaw Avenue",
        "city": "Chicago",
        "state": "IL",
        "zip": "60622",
    },
    "pollingLocations": [
        {
            "address": {
                "locationName": "UKRAINIAN ORTHDX PATRONAGE CH",
                "line1": "904 N WASHTENAW AVE",
                "city": "CHICAGO",
                "state": "IL",
                "zip": "60622",
            },
            "notes": "",
            "pollingHours": "",
            "sources": [{"name": "Voting Information Project", "official": True}],
        }
    ],
    "contests": [
        {
            "type": "General",
            "office": "United States Senator",
            "level": ["country"],
            "roles": ["legislatorUpperBody"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": 'James D. "Jim" Oberweis',
                    "party": "Republican",
                    "candidateUrl": "http://jimoberweis.com",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/Oberweis2014",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/Oberweis2014"},
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UCOVqW3lh9q9cnk-R2NedLTw",
                        },
                    ],
                },
                {
                    "name": "Richard J. Durbin",
                    "party": "Democratic",
                    "candidateUrl": "http://www.dickdurbin.com/home",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/dickdurbin",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/DickDurbin"},
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/SenatorDickDurbin",
                        },
                    ],
                },
                {
                    "name": "Sharon Hansen",
                    "party": "Libertarian",
                    "candidateUrl": "http://www.sharonhansenforussenate.org/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/USSenate2014",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/nairotci",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "US House of Representatives - District 7",
            "level": ["country"],
            "roles": ["legislatorLowerBody"],
            "district": {
                "name": "Illinois's 7th congressional district",
                "scope": "congressional",
                "id": "ocd-division/country:us/state:il/cd:7",
            },
            "candidates": [
                {
                    "name": "Danny K. Davis",
                    "party": "Democratic",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/dkdforcongress",
                        }
                    ],
                },
                {"name": "Robert L. Bumpers", "party": "Republican"},
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Governor/ Lieutenant Governor",
            "level": ["administrativeArea1"],
            "roles": ["headOfGovernment"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": "Bruce Rauner/ Evelyn Sanguinetti",
                    "party": "Republican",
                    "candidateUrl": "http://brucerauner.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/BruceRauner",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/BruceRauner"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/117459818564381220425",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/brucerauner",
                        },
                    ],
                },
                {
                    "name": "Chad Grimm/ Alexander Cummings",
                    "party": "Libertarian",
                    "candidateUrl": "http://www.grimmforliberty.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/grimmforgovernor",
                        },
                        {
                            "type": "Twitter",
                            "id": "https://twitter.com/GrimmForLiberty",
                        },
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/118063028184706045944",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UC7RjCAp7oAGM8iykNl5aCsQ",
                        },
                    ],
                },
                {
                    "name": "Pat Quinn/ Paul Vallas",
                    "party": "Democratic",
                    "candidateUrl": "https://www.quinnforillinois.com/00/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/quinnforillinois",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/quinnforil"},
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/QuinnForIllinois",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Comptroller",
            "level": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": "Judy Baar Topinka",
                    "party": "Republican",
                    "candidateUrl": "http://judybaartopinka.com",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/153417423039",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/ElectTopinka"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/118116620949235387993",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UCfbQXLS2yrY1wAJQH2oq4Kg",
                        },
                    ],
                },
                {
                    "name": "Julie Fox",
                    "party": "Libertarian",
                    "candidateUrl": "http://juliefox2014.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/154063524725251",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/JulieFox1214"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/+Juliefox2014",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UCz2A7-6e0_pJJ10bXvBvcIA",
                        },
                    ],
                },
                {
                    "name": "Sheila Simon",
                    "party": "Democratic",
                    "candidateUrl": "http://www.sheilasimon.org",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/SheilaSimonIL",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/SheilaSimonIL"},
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/SheilaSimonIL",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Secretary Of State",
            "level": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": "Christopher Michel",
                    "party": "Libertarian",
                    "candidateUrl": "http://chrisforillinois.org/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/ChrisMichelforIllinois",
                        }
                    ],
                },
                {"name": "Jesse White", "party": "Democratic"},
                {
                    "name": "Michael Webster",
                    "party": "Republican",
                    "candidateUrl": "http://websterforillinois.net/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/MikeWebsterIL",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/MikeWebsterIL"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/106530502764515758186",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/MikeWebsterIL",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Attorney General",
            "level": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": "Ben Koyl",
                    "party": "Libertarian",
                    "candidateUrl": "http://koyl4ilattorneygeneral.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/Koyl4AttorneyGeneral",
                        }
                    ],
                },
                {
                    "name": "Lisa Madigan",
                    "party": "Democratic",
                    "candidateUrl": "http://lisamadigan.org/splash",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/lisamadigan",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/LisaMadigan"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/106732728212286274178",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/LisaMadigan",
                        },
                    ],
                },
                {
                    "name": "Paul M. Schimpf",
                    "party": "Republican",
                    "candidateUrl": "http://www.schimpf4illinois.com/contact_us?splash=1",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/136912986515438",
                        },
                        {
                            "type": "Twitter",
                            "id": "https://twitter.com/Schimpf_4_IL_AG",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Treasurer",
            "level": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "candidates": [
                {
                    "name": "Matthew Skopek",
                    "party": "Libertarian",
                    "candidateUrl": "http://www.matthewskopek.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/TransparentandResponsibleGoverment",
                        }
                    ],
                },
                {
                    "name": "Michael W. Frerichs",
                    "party": "Democratic",
                    "candidateUrl": "http://frerichsforillinois.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/mikeforillinois",
                        },
                        {
                            "type": "Twitter",
                            "id": "https://twitter.com/mikeforillinois",
                        },
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/116963380840614292664",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UCX77L5usHWxrr0BdOv0r8Dg",
                        },
                    ],
                },
                {
                    "name": "Tom Cross",
                    "party": "Republican",
                    "candidateUrl": "http://jointomcross.com",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/JoinTomCross",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/JoinTomCross"},
                        {
                            "type": "GooglePlus",
                            "id": "https://plus.google.com/117776663930603924689",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/channel/UCDBLEvIGHJX1kIc_eZL5qPw",
                        },
                    ],
                },
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "State House - District 4",
            "level": ["administrativeArea1"],
            "roles": ["legislatorLowerBody"],
            "district": {
                "name": "Illinois State House district 4",
                "scope": "stateLower",
                "id": "ocd-division/country:us/state:il/sldl:4",
            },
            "candidates": [{"name": "Cynthia Soto", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook County Treasurer",
            "level": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [{"name": "Maria Pappas", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook County Clerk",
            "level": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "David D. Orr",
                    "party": "Democratic",
                    "candidateUrl": "http://www.davidorr.org/",
                    "channels": [
                        {"type": "Facebook", "id": "https://www.facebook.com/ClerkOrr"},
                        {
                            "type": "Twitter",
                            "id": "https://twitter.com/cookcountyclerk",
                        },
                        {
                            "type": "YouTube",
                            "id": "https://www.youtube.com/user/TheDavidOrr",
                        },
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook County Sheriff",
            "level": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Thomas J. Dart",
                    "party": "Democratic",
                    "candidateUrl": "http://www.sherifftomdart.com/",
                    "channels": [
                        {"type": "Twitter", "id": "https://twitter.com/TomDart"}
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook County Assessor",
            "level": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Joseph Berrios",
                    "party": "Democratic",
                    "candidateUrl": "http://www.electjoeberrios.com/",
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook County Board President",
            "level": ["administrativeArea2"],
            "roles": ["legislatorUpperBody"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Toni Preckwinkle",
                    "party": "Democratic",
                    "candidateUrl": "http://www.tonipreckwinkle.org/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/196166530417661",
                        },
                        {
                            "type": "Twitter",
                            "id": "https://twitter.com/ToniPreckwinkle",
                        },
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Arnold Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Bridget Anne Mitchell",
                    "party": "Democratic",
                    "candidateUrl": "http://mitchellforjudge.com",
                    "email": "bridget@mitchellforjudge.com",
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Reyes Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [{"name": "Diana Rosario", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Howse, Jr. Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Caroline Kate Moreland",
                    "party": "Democratic",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/judgemoreland",
                        }
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Neville, Jr. Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [{"name": "William B. Raines", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Egan Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Daniel J. Kubasiak",
                    "party": "Democratic",
                    "candidateUrl": "http://www.judgedank.org/",
                    "email": "Info@JudgeDanK.org",
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Connors Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Kristal Rivers",
                    "party": "Democratic",
                    "candidateUrl": "http://rivers4judge.org/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/193818317451678",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/Rivers4Judge"},
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - McDonald Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Cynthia Y. Cobbs",
                    "party": "Democratic",
                    "candidateUrl": "http://judgecobbs.com/",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/1387935061420024",
                        },
                        {"type": "Twitter", "id": "https://twitter.com/judgecobbs"},
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Lowrance Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [{"name": "Thomas J. Carroll", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Veal Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Andrea Michele Buford",
                    "party": "Democratic",
                    "channels": [
                        {
                            "type": "Facebook",
                            "id": "https://www.facebook.com/ElectJudgeBufordForTheBench",
                        }
                    ],
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Burke Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [{"name": "Maritza Martinez", "party": "Democratic"}],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "General",
            "office": "Cook Circuit - Felton Vacancy",
            "level": ["administrativeArea2"],
            "roles": ["judge"],
            "district": {
                "name": "Cook County",
                "scope": "countywide",
                "id": "ocd-division/country:us/state:il/county:cook",
            },
            "candidates": [
                {
                    "name": "Patricia O'Brien Sheahan",
                    "party": "Democratic",
                    "candidateUrl": "http://sheahanforjudge.com/",
                }
            ],
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "Referendum",
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "referendumTitle": "CONSTITUTION BALLOT PROPOSED AMENDMENT TO THE 1970 ILLINOIS CONSTITUTION (1)",
            "referendumSubtitle": '"NOTICE THE FAILURE TO VOTE THIS BALLOT MAY BE THE EQUIVALENT OF A NEGATIVE VOTE, BECAUSE A CONVENTION SHALL BE CALLED OR THE AMENDMENT SHALL BECOME EFFECTIVE IF APPROVED BY EITHER THREE-FIFTHS OF THOSE VOTING ON THE QUESTION OR A MAJORITY OF THOSE VOTING IN THE ELECTION. (THIS IS NOT TO BE CONSTRUED AS A DIRECTION THAT YOUR VOTE IS REQUIRED TO BE CAST EITHER IN FAVOR OF OR IN OPPOSITION TO THE PROPOSITION HEREIN CONTAINED.) WHETHER YOU VOTE THIS BALLOT OR NOT YOU MUST RETURN IT TO THE ELECTION JUDGE WHEN YOU LEAVE THE VOTING BOOTH".',
            "referendumUrl": "http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15966",
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "Referendum",
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "referendumTitle": "CONSTITUTION BALLOT PROPOSED AMENDMENT TO THE 1970 ILLINOIS CONSTITUTION (2)",
            "referendumSubtitle": '"NOTICE THE FAILURE TO VOTE THIS BALLOT MAY BE THE EQUIVALENT OF A NEGATIVE VOTE, BECAUSE A CONVENTION SHALL BE CALLED OR THE AMENDMENT SHALL BECOME EFFECTIVE IF APPROVED BY EITHER THREE-FIFTHS OF THOSE VOTING ON THE QUESTION OR A MAJORITY OF THOSE VOTING IN THE ELECTION. (THIS IS NOT TO BE CONSTRUED AS A DIRECTION THAT YOUR VOTE IS REQUIRED TO BE CAST EITHER IN FAVOR OF OR IN OPPOSITION TO THE PROPOSITION HEREIN CONTAINED.) WHETHER YOU VOTE THIS BALLOT OR NOT YOU MUST RETURN IT TO THE ELECTION JUDGE WHEN YOU LEAVE THE VOTING BOOTH".',
            "referendumUrl": "http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15967",
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "Referendum",
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "referendumTitle": "STATEWIDE ADVISORY QUESTION (1)",
            "referendumUrl": "http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15738",
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "Referendum",
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "referendumTitle": "STATEWIDE ADVISORY QUESTION (2)",
            "referendumUrl": "http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15739",
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
        {
            "type": "Referendum",
            "district": {
                "name": "Illinois",
                "scope": "statewide",
                "id": "ocd-division/country:us/state:il",
            },
            "referendumTitle": "STATEWIDE ADVISORY QUESTION (3)",
            "referendumUrl": "http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15740",
            "sources": [{"name": "Ballot Information Project", "official": False}],
        },
    ],
    "state": [
        {
            "name": "Illinois",
            "electionAdministrationBody": {
                "name": "Illinois State Board of Elections",
                "electionInfoUrl": "http://www.elections.il.gov",
                "votingLocationFinderUrl": "https://ova.elections.il.gov/PollingPlaceLookup.aspx",
                "ballotInfoUrl": "https://www.elections.il.gov/ElectionInformation/OfficesUpForElection.aspx?ID=2GLMQa4Rilk%3d",
                "correspondenceAddress": {
                    "line1": "2329 S Macarthur Blvd.",
                    "city": "Springfield",
                    "state": "Illinois",
                    "zip": "62704-4503",
                },
            },
            "local_jurisdiction": {
                "name": "CITY OF CHICAGO",
                "sources": [{"name": "Voting Information Project", "official": True}],
            },
            "sources": [{"name": "", "official": False}],
        }
    ],
}

polling_data = [
    {
        "passed_address": "900 N Washtenaw, Chicago, IL 60622",
        "polling_locationName": "UKRAINIAN ORTHDX PATRONAGE CH",
        "polling_address": "904 N WASHTENAW AVE",
        "polling_city": "CHICAGO",
        "polling_state": "IL",
        "polling_zip": "60622",
        "source_name": "Voting Information Project",
        "source_official": True,
        "pollingHours": "",
        "notes": "",
    },
    {
        "passed_address": "900 N Washtenaw, Chicago, IL 60622",
        "polling_locationName": "UKRAINIAN ORTHDX PATRONAGE CH",
        "polling_address": "904 N WASHTENAW AVE",
        "polling_city": "CHICAGO",
        "polling_state": "IL",
        "polling_zip": "60622",
        "source_name": "Voting Information Project",
        "source_official": True,
        "pollingHours": "",
        "notes": "",
    },
]

representatives_resp = {
    "normalizedInput": {
        "line1": "1600 Amphitheatre Parkway",
        "city": "Mountain View",
        "state": "CA",
        "zip": "94043",
    },
    "kind": "civicinfo#representativeInfoResponse",
    "divisions": {
        "ocd-division/country:us/state:ca/county:santa_clara": {
            "name": "Santa Clara County",
            "officeIndices": [14, 15, 16],
        },
        "ocd-division/country:us": {"name": "United States", "officeIndices": [0, 1]},
        "ocd-division/country:us/state:ca/cd:16": {
            "name": "California's 16th congressional district",
            "officeIndices": [3],
        },
        "ocd-division/country:us/state:ca/place:mountain_view": {
            "name": "Mountain View city"
        },
        "ocd-division/country:us/state:ca/sldl:23": {
            "name": "California Assembly district 23",
            "officeIndices": [12],
        },
        "ocd-division/country:us/state:ca": {
            "name": "California",
            "officeIndices": [2, 4, 5, 6, 7, 8, 9, 10, 11, 13],
        },
    },
    "offices": [
        {
            "name": "President of the United States",
            "divisionId": "ocd-division/country:us",
            "levels": ["country"],
            "roles": ["headOfGovernment", "headOfState"],
            "officialIndices": [0],
        },
        {
            "name": "Vice President of the United States",
            "divisionId": "ocd-division/country:us",
            "levels": ["country"],
            "roles": ["deputyHeadOfGovernment"],
            "officialIndices": [1],
        },
        {
            "name": "U.S. Senator",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["country"],
            "roles": ["legislatorUpperBody"],
            "officialIndices": [2, 3],
        },
        {
            "name": "U.S. Representative",
            "divisionId": "ocd-division/country:us/state:ca/cd:16",
            "levels": ["country"],
            "roles": ["legislatorLowerBody"],
            "officialIndices": [4],
        },
        {
            "name": "Governor of California",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["headOfGovernment"],
            "officialIndices": [5],
        },
        {
            "name": "Lieutenant Governor of California",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["deputyHeadOfGovernment"],
            "officialIndices": [6],
        },
        {
            "name": "CA State Superintendent of Public Instruction",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [7],
        },
        {
            "name": "CA Secretary of State",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [8],
        },
        {
            "name": "CA State Insurance Commissioner",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [9],
        },
        {
            "name": "CA State Treasurer",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [10],
        },
        {
            "name": "CA State Attorney General",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [11],
        },
        {
            "name": "CA State Controller",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["governmentOfficer"],
            "officialIndices": [12],
        },
        {
            "name": "CA State Assembly Member",
            "divisionId": "ocd-division/country:us/state:ca/sldl:23",
            "levels": ["administrativeArea1"],
            "roles": ["legislatorLowerBody"],
            "officialIndices": [13],
        },
        {
            "name": "CA State Supreme Court Justice",
            "divisionId": "ocd-division/country:us/state:ca",
            "levels": ["administrativeArea1"],
            "roles": ["judge"],
            "officialIndices": [14, 15, 16, 17, 18, 19, 20],
        },
        {
            "name": "Santa Clara County District Attorney",
            "divisionId": "ocd-division/country:us/state:ca/county:santa_clara",
            "levels": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "officialIndices": [21],
        },
        {
            "name": "Santa Clara County Assessor",
            "divisionId": "ocd-division/country:us/state:ca/county:santa_clara",
            "levels": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "officialIndices": [22],
        },
        {
            "name": "Santa Clara County Sheriff",
            "divisionId": "ocd-division/country:us/state:ca/county:santa_clara",
            "levels": ["administrativeArea2"],
            "roles": ["governmentOfficer"],
            "officialIndices": [23],
        },
    ],
    "officials": [
        {
            "name": "Joseph R. Biden",
            "address": [
                {
                    "line1": "1600 Pennsylvania Avenue Northwest",
                    "city": "Washington",
                    "state": "DC",
                    "zip": "20500",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(202) 456-1111"],
            "urls": [
                "https://www.whitehouse.gov/",
                "https://en.wikipedia.org/wiki/Joe_Biden",
            ],
            "channels": [{"type": "Twitter", "id": "potus"}],
        },
        {
            "name": "Kamala D. Harris",
            "address": [
                {
                    "line1": "1600 Pennsylvania Avenue Northwest",
                    "city": "Washington",
                    "state": "DC",
                    "zip": "20500",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(202) 456-1111"],
            "urls": [
                "https://www.whitehouse.gov/",
                "https://en.wikipedia.org/wiki/Kamala_Harris",
            ],
            "channels": [{"type": "Twitter", "id": "VP"}],
        },
        {
            "name": "Alex Padilla",
            "address": [
                {"line1": "B03", "city": "Washington", "state": "DC", "zip": "20510"}
            ],
            "party": "Democratic Party",
            "phones": ["(202) 224-3553"],
            "urls": [
                "https://www.padilla.senate.gov/",
                "https://en.wikipedia.org/wiki/Alex_Padilla",
            ],
            "channels": [
                {"type": "Facebook", "id": "SenAlexPadilla"},
                {"type": "Twitter", "id": "SenAlexPadilla"},
            ],
        },
        {
            "name": "LaPhonza R. Butler",
            "party": "Democratic Party",
            "phones": ["(202) 224-3841"],
            "urls": ["https://www.butler.senate.gov/"],
        },
        {
            "name": "Anna G. Eshoo",
            "address": [
                {
                    "line1": "272 Cannon House Office Building",
                    "city": "Washington",
                    "state": "DC",
                    "zip": "20515",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(202) 225-8104"],
            "urls": [
                "https://eshoo.house.gov/",
                "https://en.wikipedia.org/wiki/Anna_Eshoo",
            ],
            "channels": [
                {"type": "Facebook", "id": "RepAnnaEshoo"},
                {"type": "Twitter", "id": "RepAnnaEshoo"},
            ],
        },
        {
            "name": "Gavin Newsom",
            "address": [
                {
                    "line1": "1303 10th Street",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(916) 445-2841"],
            "urls": [
                "https://www.gov.ca.gov/",
                "https://en.wikipedia.org/wiki/Gavin_Newsom",
            ],
            "photoUrl": "http://www.ltg.ca.gov/images/newsimages/i2.png",
            "channels": [
                {"type": "Facebook", "id": "CAgovernor"},
                {"type": "Twitter", "id": "CAgovernor"},
            ],
        },
        {
            "name": "Eleni Kounalakis",
            "address": [
                {
                    "line1": "1315 10th Street",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(916) 445-8994"],
            "urls": [
                "https://ltg.ca.gov/",
                "https://en.wikipedia.org/wiki/Eleni_Kounalakis",
            ],
            "channels": [
                {"type": "Facebook", "id": "EleniKounalakis"},
                {"type": "Twitter", "id": "CALtGovernor"},
            ],
        },
        {
            "name": "Tony Thurmond",
            "address": [
                {
                    "line1": "1430 N Street",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(916) 319-0800"],
            "urls": [
                "https://www.cde.ca.gov/eo/",
                "https://en.wikipedia.org/wiki/Tony_Thurmond",
            ],
            "channels": [
                {"type": "Facebook", "id": "CAEducation"},
                {"type": "Twitter", "id": "CADeptEd"},
            ],
        },
        {
            "name": "Shirley N. Weber",
            "address": [
                {
                    "line1": "1500 11th Street",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(916) 653-6814"],
            "urls": [
                "https://www.sos.ca.gov/",
                "https://en.wikipedia.org/wiki/Shirley_Weber",
            ],
            "channels": [
                {"type": "Facebook", "id": "CaliforniaSOS"},
                {"type": "Twitter", "id": "CASOSvote"},
            ],
        },
        {
            "name": "Ricardo Lara",
            "address": [
                {
                    "line1": "300 Capitol Mall",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(800) 927-4357"],
            "urls": [
                "http://www.insurance.ca.gov/",
                "https://en.wikipedia.org/wiki/Ricardo_Lara",
            ],
            "channels": [
                {"type": "Facebook", "id": "ICRicardoLara"},
                {"type": "Twitter", "id": "ICRicardoLara"},
            ],
        },
        {
            "name": "Fiona Ma",
            "address": [
                {
                    "line1": "915 Capitol Mall",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(916) 653-2995"],
            "urls": [
                "https://www.treasurer.ca.gov/",
                "https://en.wikipedia.org/wiki/Fiona_Ma",
            ],
            "channels": [
                {"type": "Facebook", "id": "CaliforniaSTO"},
                {"type": "Twitter", "id": "CalTreasurer"},
            ],
        },
        {
            "name": "Rob Bonta",
            "party": "Democratic Party",
            "phones": ["(916) 445-9555"],
            "urls": ["https://oag.ca.gov/", "https://en.wikipedia.org/wiki/Rob_Bonta"],
            "channels": [
                {"type": "Facebook", "id": "AGRobBonta"},
                {"type": "Twitter", "id": "AGRobBonta"},
            ],
        },
        {
            "name": "Malia M. Cohen",
            "address": [
                {
                    "line1": "300 Capitol Mall",
                    "city": "Sacramento",
                    "state": "CA",
                    "zip": "95814",
                }
            ],
            "party": "Democratic Party",
            "phones": ["(916) 445-2636"],
            "urls": [
                "https://www.sco.ca.gov/index.html",
                "https://en.wikipedia.org/wiki/Malia_Cohen",
            ],
            "channels": [
                {"type": "Facebook", "id": "CAController"},
                {"type": "Twitter", "id": "CAController"},
            ],
        },
        {
            "name": "Marc Berman",
            "party": "Democratic Party",
            "phones": ["(916) 319-2023"],
            "urls": [
                "https://a23.asmdc.org/",
                "https://en.wikipedia.org/wiki/Marc_Berman",
            ],
            "channels": [
                {"type": "Facebook", "id": "AsmMarcBerman"},
                {"type": "Twitter", "id": "AsmMarcBerman"},
            ],
        },
        {
            "name": "Carol A. Corrigan",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Carol_Corrigan",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Goodwin H. Liu",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Goodwin_Liu",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Joshua P. Groban",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Joshua_Groban",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Kelli Evans",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Kelli_Evans",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Leondra R. Kruger",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Leondra_Kruger",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Martin J. Jenkins",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Martin_Jenkins",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Patricia Guerrero",
            "address": [
                {
                    "line1": "350 McAllister Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(415) 865-7000"],
            "urls": [
                "https://www.courts.ca.gov/supremecourt.htm",
                "https://en.wikipedia.org/wiki/Patricia_Guerrero_%28judge%29",
            ],
            "channels": [{"type": "Twitter", "id": "CaSupremeCourt"}],
        },
        {
            "name": "Jeffrey F. Rosen",
            "address": [
                {
                    "line1": "70 West Hedding Street",
                    "city": "San Jose",
                    "state": "CA",
                    "zip": "95110",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(408) 299-7500"],
            "urls": ["https://countyda.sccgov.org/home"],
            "emails": ["jrosen@dao.sccgov.org"],
            "channels": [
                {"type": "Facebook", "id": "SantaClaraDA"},
                {"type": "Twitter", "id": "SantaClaraDA"},
            ],
        },
        {
            "name": "Lawrence E. Stone",
            "address": [
                {
                    "line1": "70 West Hedding Street",
                    "city": "San Jose",
                    "state": "CA",
                    "zip": "95110",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(408) 299-5500"],
            "urls": ["https://www.sccassessor.org/"],
            "emails": ["assessor@asr.sccgov.org"],
        },
        {
            "name": "Robert Jonsen",
            "address": [
                {
                    "line1": "55 West Younger Avenue",
                    "city": "San Jose",
                    "state": "CA",
                    "zip": "95110",
                }
            ],
            "party": "Nonpartisan",
            "phones": ["(408) 808-4400"],
            "urls": ["https://countysheriff.sccgov.org/home"],
            "emails": ["so.website@shf.sccgov.org"],
            "channels": [
                {"type": "Facebook", "id": "santaclarasheriff"},
                {"type": "Twitter", "id": "SCCoSheriff"},
            ],
        },
    ],
}
