# flake8: noqa
elections_resp = {
    'kind': 'civicinfo#electionsQueryResponse',
    'elections': [{
        'id': '2000',
        'name': 'VIP Test Election',
        'electionDay': '2021-06-06',
        'ocdDivisionId': 'ocd-division/country:us'
    }, {
        'id': '4803',
        'name': 'Los Angeles County Election',
        'electionDay': '2019-05-14',
        'ocdDivisionId': 'ocd-division/country:us/state:ca/county:los_angeles'
    }, {
        'id': '4804',
        'name': 'Oklahoma Special Election',
        'electionDay': '2019-05-14',
        'ocdDivisionId': 'ocd-division/country:us/state:ok'
    }, {
        'id': '4810',
        'name': 'Oregon County Special Elections',
        'electionDay': '2019-05-21',
        'ocdDivisionId': 'ocd-division/country:us/state:or'
    }, {
        'id': '4811',
        'name': 'Los Angeles County Special Election',
        'electionDay': '2019-06-04',
        'ocdDivisionId': 'ocd-division/country:us/state:ca/county:los_angeles'
    }, {
        'id': '4823',
        'name': '9th Congressional District Primary Election',
        'electionDay': '2019-05-14',
        'ocdDivisionId': 'ocd-division/country:us/state:nc/cd:9'
    }]
}

voterinfo_resp = {
    'kind': 'civicinfo#voterInfoResponse',
    'election': {
        'id': '2000',
        'name': 'VIP Test Election',
        'electionDay': '2021-06-06',
        'ocdDivisionId': 'ocd-division/country:us'
    },
    'normalizedInput': {
        'line1': '900 North Washtenaw Avenue',
        'city': 'Chicago',
        'state': 'IL',
        'zip': '60622'
    },
    'pollingLocations': [{
        'address': {
            'locationName': 'UKRAINIAN ORTHDX PATRONAGE CH',
            'line1': '904 N WASHTENAW AVE',
            'city': 'CHICAGO',
            'state': 'IL',
            'zip': '60622'
        },
        'notes': '',
        'pollingHours': '',
        'sources': [{
            'name': 'Voting Information Project',
            'official': True
        }]
    }],
    'contests': [{
        'type': 'General',
        'office': 'United States Senator',
        'level': ['country'],
        'roles': ['legislatorUpperBody'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'James D. "Jim" Oberweis',
            'party': 'Republican',
            'candidateUrl': 'http://jimoberweis.com',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/Oberweis2014'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/Oberweis2014'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UCOVqW3lh9q9cnk-R2NedLTw'
            }]
        }, {
            'name': 'Richard J. Durbin',
            'party': 'Democratic',
            'candidateUrl': 'http://www.dickdurbin.com/home',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/dickdurbin'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/DickDurbin'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/SenatorDickDurbin'
            }]
        }, {
            'name': 'Sharon Hansen',
            'party': 'Libertarian',
            'candidateUrl': 'http://www.sharonhansenforussenate.org/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/USSenate2014'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/nairotci'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'US House of Representatives - District 7',
        'level': ['country'],
        'roles': ['legislatorLowerBody'],
        'district': {
            'name': "Illinois's 7th congressional district",
            'scope': 'congressional',
            'id': 'ocd-division/country:us/state:il/cd:7'
        },
        'candidates': [{
            'name': 'Danny K. Davis',
            'party': 'Democratic',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/dkdforcongress'
            }]
        }, {
            'name': 'Robert L. Bumpers',
            'party': 'Republican'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Governor/ Lieutenant Governor',
        'level': ['administrativeArea1'],
        'roles': ['headOfGovernment'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'Bruce Rauner/ Evelyn Sanguinetti',
            'party': 'Republican',
            'candidateUrl': 'http://brucerauner.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/BruceRauner'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/BruceRauner'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/117459818564381220425'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/brucerauner'
            }]
        }, {
            'name': 'Chad Grimm/ Alexander Cummings',
            'party': 'Libertarian',
            'candidateUrl': 'http://www.grimmforliberty.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/grimmforgovernor'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/GrimmForLiberty'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/118063028184706045944'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UC7RjCAp7oAGM8iykNl5aCsQ'
            }]
        }, {
            'name': 'Pat Quinn/ Paul Vallas',
            'party': 'Democratic',
            'candidateUrl': 'https://www.quinnforillinois.com/00/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/quinnforillinois'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/quinnforil'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/QuinnForIllinois'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Comptroller',
        'level': ['administrativeArea1'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'Judy Baar Topinka',
            'party': 'Republican',
            'candidateUrl': 'http://judybaartopinka.com',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/153417423039'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/ElectTopinka'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/118116620949235387993'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UCfbQXLS2yrY1wAJQH2oq4Kg'
            }]
        }, {
            'name': 'Julie Fox',
            'party': 'Libertarian',
            'candidateUrl': 'http://juliefox2014.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/154063524725251'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/JulieFox1214'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/+Juliefox2014'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UCz2A7-6e0_pJJ10bXvBvcIA'
            }]
        }, {
            'name': 'Sheila Simon',
            'party': 'Democratic',
            'candidateUrl': 'http://www.sheilasimon.org',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/SheilaSimonIL'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/SheilaSimonIL'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/SheilaSimonIL'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Secretary Of State',
        'level': ['administrativeArea1'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'Christopher Michel',
            'party': 'Libertarian',
            'candidateUrl': 'http://chrisforillinois.org/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/ChrisMichelforIllinois'
            }]
        }, {
            'name': 'Jesse White',
            'party': 'Democratic'
        }, {
            'name': 'Michael Webster',
            'party': 'Republican',
            'candidateUrl': 'http://websterforillinois.net/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/MikeWebsterIL'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/MikeWebsterIL'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/106530502764515758186'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/MikeWebsterIL'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Attorney General',
        'level': ['administrativeArea1'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'Ben Koyl',
            'party': 'Libertarian',
            'candidateUrl': 'http://koyl4ilattorneygeneral.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/Koyl4AttorneyGeneral'
            }]
        }, {
            'name': 'Lisa Madigan',
            'party': 'Democratic',
            'candidateUrl': 'http://lisamadigan.org/splash',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/lisamadigan'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/LisaMadigan'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/106732728212286274178'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/LisaMadigan'
            }]
        }, {
            'name': 'Paul M. Schimpf',
            'party': 'Republican',
            'candidateUrl': 'http://www.schimpf4illinois.com/contact_us?splash=1',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/136912986515438'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/Schimpf_4_IL_AG'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Treasurer',
        'level': ['administrativeArea1'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'candidates': [{
            'name': 'Matthew Skopek',
            'party': 'Libertarian',
            'candidateUrl': 'http://www.matthewskopek.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/TransparentandResponsibleGoverment'
            }]
        }, {
            'name': 'Michael W. Frerichs',
            'party': 'Democratic',
            'candidateUrl': 'http://frerichsforillinois.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/mikeforillinois'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/mikeforillinois'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/116963380840614292664'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UCX77L5usHWxrr0BdOv0r8Dg'
            }]
        }, {
            'name': 'Tom Cross',
            'party': 'Republican',
            'candidateUrl': 'http://jointomcross.com',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/JoinTomCross'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/JoinTomCross'
            }, {
                'type': 'GooglePlus',
                'id': 'https://plus.google.com/117776663930603924689'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/channel/UCDBLEvIGHJX1kIc_eZL5qPw'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'State House - District 4',
        'level': ['administrativeArea1'],
        'roles': ['legislatorLowerBody'],
        'district': {
            'name': 'Illinois State House district 4',
            'scope': 'stateLower',
            'id': 'ocd-division/country:us/state:il/sldl:4'
        },
        'candidates': [{
            'name': 'Cynthia Soto',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook County Treasurer',
        'level': ['administrativeArea2'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Maria Pappas',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook County Clerk',
        'level': ['administrativeArea2'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'David D. Orr',
            'party': 'Democratic',
            'candidateUrl': 'http://www.davidorr.org/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/ClerkOrr'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/cookcountyclerk'
            }, {
                'type': 'YouTube',
                'id': 'https://www.youtube.com/user/TheDavidOrr'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook County Sheriff',
        'level': ['administrativeArea2'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Thomas J. Dart',
            'party': 'Democratic',
            'candidateUrl': 'http://www.sherifftomdart.com/',
            'channels': [{
                'type': 'Twitter',
                'id': 'https://twitter.com/TomDart'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook County Assessor',
        'level': ['administrativeArea2'],
        'roles': ['governmentOfficer'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Joseph Berrios',
            'party': 'Democratic',
            'candidateUrl': 'http://www.electjoeberrios.com/'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook County Board President',
        'level': ['administrativeArea2'],
        'roles': ['legislatorUpperBody'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Toni Preckwinkle',
            'party': 'Democratic',
            'candidateUrl': 'http://www.tonipreckwinkle.org/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/196166530417661'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/ToniPreckwinkle'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Arnold Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Bridget Anne Mitchell',
            'party': 'Democratic',
            'candidateUrl': 'http://mitchellforjudge.com',
            'email': 'bridget@mitchellforjudge.com'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Reyes Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Diana Rosario',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Howse, Jr. Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Caroline Kate Moreland',
            'party': 'Democratic',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/judgemoreland'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Neville, Jr. Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'William B. Raines',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Egan Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Daniel J. Kubasiak',
            'party': 'Democratic',
            'candidateUrl': 'http://www.judgedank.org/',
            'email': 'Info@JudgeDanK.org'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Connors Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Kristal Rivers',
            'party': 'Democratic',
            'candidateUrl': 'http://rivers4judge.org/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/193818317451678'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/Rivers4Judge'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - McDonald Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Cynthia Y. Cobbs',
            'party': 'Democratic',
            'candidateUrl': 'http://judgecobbs.com/',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/1387935061420024'
            }, {
                'type': 'Twitter',
                'id': 'https://twitter.com/judgecobbs'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Lowrance Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Thomas J. Carroll',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Veal Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Andrea Michele Buford',
            'party': 'Democratic',
            'channels': [{
                'type': 'Facebook',
                'id': 'https://www.facebook.com/ElectJudgeBufordForTheBench'
            }]
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Burke Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': 'Maritza Martinez',
            'party': 'Democratic'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'General',
        'office': 'Cook Circuit - Felton Vacancy',
        'level': ['administrativeArea2'],
        'roles': ['judge'],
        'district': {
            'name': 'Cook County',
            'scope': 'countywide',
            'id': 'ocd-division/country:us/state:il/county:cook'
        },
        'candidates': [{
            'name': "Patricia O'Brien Sheahan",
            'party': 'Democratic',
            'candidateUrl': 'http://sheahanforjudge.com/'
        }],
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'Referendum',
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'referendumTitle': 'CONSTITUTION BALLOT PROPOSED AMENDMENT TO THE 1970 ILLINOIS CONSTITUTION (1)',
        'referendumSubtitle': '"NOTICE THE FAILURE TO VOTE THIS BALLOT MAY BE THE EQUIVALENT OF A NEGATIVE VOTE, BECAUSE A CONVENTION SHALL BE CALLED OR THE AMENDMENT SHALL BECOME EFFECTIVE IF APPROVED BY EITHER THREE-FIFTHS OF THOSE VOTING ON THE QUESTION OR A MAJORITY OF THOSE VOTING IN THE ELECTION. (THIS IS NOT TO BE CONSTRUED AS A DIRECTION THAT YOUR VOTE IS REQUIRED TO BE CAST EITHER IN FAVOR OF OR IN OPPOSITION TO THE PROPOSITION HEREIN CONTAINED.) WHETHER YOU VOTE THIS BALLOT OR NOT YOU MUST RETURN IT TO THE ELECTION JUDGE WHEN YOU LEAVE THE VOTING BOOTH".',
        'referendumUrl': 'http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15966',
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'Referendum',
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'referendumTitle': 'CONSTITUTION BALLOT PROPOSED AMENDMENT TO THE 1970 ILLINOIS CONSTITUTION (2)',
        'referendumSubtitle': '"NOTICE THE FAILURE TO VOTE THIS BALLOT MAY BE THE EQUIVALENT OF A NEGATIVE VOTE, BECAUSE A CONVENTION SHALL BE CALLED OR THE AMENDMENT SHALL BECOME EFFECTIVE IF APPROVED BY EITHER THREE-FIFTHS OF THOSE VOTING ON THE QUESTION OR A MAJORITY OF THOSE VOTING IN THE ELECTION. (THIS IS NOT TO BE CONSTRUED AS A DIRECTION THAT YOUR VOTE IS REQUIRED TO BE CAST EITHER IN FAVOR OF OR IN OPPOSITION TO THE PROPOSITION HEREIN CONTAINED.) WHETHER YOU VOTE THIS BALLOT OR NOT YOU MUST RETURN IT TO THE ELECTION JUDGE WHEN YOU LEAVE THE VOTING BOOTH".',
        'referendumUrl': 'http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15967',
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'Referendum',
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'referendumTitle': 'STATEWIDE ADVISORY QUESTION (1)',
        'referendumUrl': 'http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15738',
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'Referendum',
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'referendumTitle': 'STATEWIDE ADVISORY QUESTION (2)',
        'referendumUrl': 'http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15739',
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }, {
        'type': 'Referendum',
        'district': {
            'name': 'Illinois',
            'scope': 'statewide',
            'id': 'ocd-division/country:us/state:il'
        },
        'referendumTitle': 'STATEWIDE ADVISORY QUESTION (3)',
        'referendumUrl': 'http://www.elections.il.gov/ReferendaProfile/ReferendaDetail.aspx?ID=15740',
        'sources': [{
            'name': 'Ballot Information Project',
            'official': False
        }]
    }],
    'state': [{
        'name': 'Illinois',
        'electionAdministrationBody': {
            'name': 'Illinois State Board of Elections',
            'electionInfoUrl': 'http://www.elections.il.gov',
            'votingLocationFinderUrl': 'https://ova.elections.il.gov/PollingPlaceLookup.aspx',
            'ballotInfoUrl': 'https://www.elections.il.gov/ElectionInformation/OfficesUpForElection.aspx?ID=2GLMQa4Rilk%3d',
            'correspondenceAddress': {
              'line1': '2329 S Macarthur Blvd.',
              'city': 'Springfield',
              'state': 'Illinois',
              'zip': '62704-4503'
              }
        },
        'local_jurisdiction': {
            'name': 'CITY OF CHICAGO',
            'sources': [{
                'name': 'Voting Information Project',
                'official': True
            }]
        },
        'sources': [{
            'name': '',
            'official': False
        }]
    }]
}

polling_data = [{
    'passed_address': '900 N Washtenaw, Chicago, IL 60622',
    'polling_locationName': 'UKRAINIAN ORTHDX PATRONAGE CH',
    'polling_address': '904 N WASHTENAW AVE',
    'polling_city': 'CHICAGO',
    'polling_state': 'IL',
    'polling_zip': '60622',
    'source_name': 'Voting Information Project',
    'source_official': True,
    'pollingHours': '',
    'notes': ''},
    {
    'passed_address': '900 N Washtenaw, Chicago, IL 60622',
    'polling_locationName': 'UKRAINIAN ORTHDX PATRONAGE CH',
    'polling_address': '904 N WASHTENAW AVE',
    'polling_city': 'CHICAGO',
    'polling_state': 'IL',
    'polling_zip': '60622',
    'source_name': 'Voting Information Project',
    'source_official': True,
    'pollingHours': '',
    'notes': ''
	}]

