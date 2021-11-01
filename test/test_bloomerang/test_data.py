ENV_PARAMETERS = {
    'BLOOMERANG_API_KEY': 'env_api_key',
    'BLOOMERANG_CLIENT_ID': 'env_client_id',
    'BLOOMERANG_CLIENT_SECRET': 'env_client_secret'
}

ID = 123

TEST_DELETE = {
    "Id": 0,
    "Type": "string",
    "Deleted": 'true'
}

TEST_CREATE_CONSTITUENT = {
    "Type": "Individual",
    "Status": "Active",
    "FirstName": "string",
    "LastName": "string",
    "MiddleName": "string",
    "Prefix": "string",
    "Suffix": "string",
    "FullName": "string",
    "InformalName": "string",
    "FormalName": "string",
    "EnvelopeName": "string",
    "RecognitionName": "string",
    "JobTitle": "string",
    "Employer": "string",
    "Website": "string",
    "FacebookId": "string",
    "TwitterId": "string",
    "LinkedInId": "string",
    "Gender": "Male",
    "Birthdate": "2020-08-24",
    "ProfilePictureType": "None",
    "PrimaryEmail": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Value": "user@example.com",
        "IsPrimary": 'true',
        "IsBad": 'true'
    },
    "PrimaryPhone": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Extension": "string",
        "Number": "string",
        "IsPrimary": 'true'
    },
    "PrimaryAddress": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Street": "string",
        "City": "string",
        "State": "string",
        "PostalCode": "string",
        "Country": "string",
        "IsPrimary": 'true',
        "IsBad": 'true'
    }
}

TEST_GET_CONSTITUENT = {
    "Id": 0,
    "AccountNumber": 0,
    "IsInHousehold": 'true',
    "IsHeadOfHousehold": 'true',
    "IsFavorite": 'true',
    "FullCustomProfileImageId": 0,
    "FullCustomProfileImageUrl": "string",
    "CroppedCustomProfileImageId": 0,
    "CroppedCustomProfileImageUrl": "string",
    "Type": "Individual",
    "Status": "Active",
    "FirstName": "string",
    "LastName": "string",
    "MiddleName": "string",
    "Prefix": "string",
    "Suffix": "string",
    "FullName": "string",
    "InformalName": "string",
    "FormalName": "string",
    "EnvelopeName": "string",
    "RecognitionName": "string",
    "JobTitle": "string",
    "Employer": "string",
    "Website": "string",
    "FacebookId": "string",
    "TwitterId": "string",
    "LinkedInId": "string",
    "Gender": "Male",
    "Birthdate": "2020-09-08",
    "ProfilePictureType": "None",
    "PrimaryEmail": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Value": "user@example.com",
        "IsPrimary": 'true',
        "IsBad": 'true'
    },
    "PrimaryPhone": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Extension": "string",
        "Number": "string",
        "IsPrimary": 'true'
    },
    "HouseholdId": 0,
    "PreferredCommunicationChannel": "Email",
    "CommunicationRestrictions": [
        "DoNotCall"
    ],
    "CommunicationRestrictionsUpdateReason": "string",
    "EmailInterestType": "All",
    "CustomEmailInterests": [
        {
            "Id": 0,
            "Name": "string"
        }
    ],
    "EmailInterestsUpdateReason": "string",
    "PrimaryAddress": {
        "Id": 0,
        "AccountId": 0,
        "Type": "Home",
        "Street": "string",
        "City": "string",
        "State": "string",
        "PostalCode": "string",
        "Country": "string",
        "IsPrimary": 'true',
        "IsBad": 'true',
        "StateAbbreviation": "string",
        "CountryCode": "string"
    },
    "EngagementScore": "Low",
    "DonorSearchInfo": {
        "Id": 0,
        "GenerosityScore": "Low",
        "AnnualFundLikelihood": "Low",
        "MajorGiftLikelihood": "Low",
        "PlannedGiftLikelihood": "Low",
        "Quality": "Low",
        "LargestGiftMin": 0,
        "LargestGiftMax": 0,
        "WealthAskMin": 0,
        "WealthAskMax": 0,
        "BusinessExecutive": 'true',
        "NamesScreened": "string",
        "DateTimeScreenedUtc": "string"
    },
    "AddressIds": [
        0
    ],
    "EmailIds": [
        0
    ],
    "PhoneIds": [
        0
    ],
    "CustomValues": [
        {
            "FieldId": 0,
            "Value": {
                "Id": 0,
                "Value": "string"
            }
        },
        {
            "FieldId": 0,
            "Values": [
                {
                    "Id": 0,
                    "Value": "string"
                }
            ]
        }
    ],
    "AuditTrail": {
        "CreatedDate": "2020-09-08T16:06:59.945Z",
        "CreatedName": "string",
        "LastModifiedDate": "2020-09-08T16:06:59.945Z",
        "LastModifiedName": "string"
    }
}

TEST_GET_CONSTITUENTS = {
    "Total": 0,
    "TotalFiltered": 0,
    "Start": 0,
    "ResultCount": 0,
    "Results": [
        {
            "Id": 0,
            "AccountNumber": 0,
            "IsInHousehold": 'true',
            "IsHeadOfHousehold": 'true',
            "IsFavorite": 'true',
            "FullCustomProfileImageId": 0,
            "FullCustomProfileImageUrl": "string",
            "CroppedCustomProfileImageId": 0,
            "CroppedCustomProfileImageUrl": "string",
            "Type": "Individual",
            "Status": "Active",
            "FirstName": "string",
            "LastName": "string",
            "MiddleName": "string",
            "Prefix": "string",
            "Suffix": "string",
            "FullName": "string",
            "InformalName": "string",
            "FormalName": "string",
            "EnvelopeName": "string",
            "RecognitionName": "string",
            "JobTitle": "string",
            "Employer": "string",
            "Website": "string",
            "FacebookId": "string",
            "TwitterId": "string",
            "LinkedInId": "string",
            "Gender": "Male",
            "Birthdate": "2020-09-05",
            "ProfilePictureType": "None",
            "PrimaryEmail": {
                "Id": 0,
                "AccountId": 0,
                "Type": "Home",
                "Value": "user@example.com",
                "IsPrimary": 'true',
                "IsBad": 'true'
            },
            "PrimaryPhone": {
                "Id": 0,
                "AccountId": 0,
                "Type": "Home",
                "Extension": "string",
                "Number": "string",
                "IsPrimary": 'true'
            },
            "HouseholdId": 0,
            "PreferredCommunicationChannel": "Email",
            "CommunicationRestrictions": [
                "DoNotCall"
            ],
            "CommunicationRestrictionsUpdateReason": "string",
            "EmailInterestType": "All",
            "CustomEmailInterests": [
                {
                    "Id": 0,
                    "Name": "string"
                }
            ],
            "EmailInterestsUpdateReason": "string",
            "EngagementScore": "Low",
            "DonorSearchInfo": {
                "Id": 0,
                "GenerosityScore": "Low",
                "AnnualFundLikelihood": "Low",
                "MajorGiftLikelihood": "Low",
                "PlannedGiftLikelihood": "Low",
                "Quality": "Low",
                "LargestGiftMin": 0,
                "LargestGiftMax": 0,
                "WealthAskMin": 0,
                "WealthAskMax": 0,
                "BusinessExecutive": 'true',
                "NamesScreened": "string",
                "DateTimeScreenedUtc": "string"
            },
            "AddressIds": [
                0
            ],
            "EmailIds": [
                0
            ],
            "PhoneIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-05T01:40:43.035Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-05T01:40:43.035Z",
                "LastModifiedName": "string"
            }
        }
    ]
}

TEST_CREATE_TRANSACTION = {
    "AccountId": 0,
    "Date": "2020-09-08",
    "Amount": 0,
    "Method": "None",
    "CheckNumber": "string",
    "CheckDate": "2020-09-08",
    "CreditCardType": "Visa",
    "CreditCardLastFourDigits": "string",
    "CreditCardExpMonth": 0,
    "CreditCardExpYear": 0,
    "EftAccountType": "Checking",
    "EftLastFourDigits": "string",
    "EftRoutingNumber": "string",
    "InKindDescription": "string",
    "InKindType": "Goods",
    "InKindMarketValue": 0,
    "WalletItemId": 0,
    "IntegrationUrl": "string",
    "Designations": [
        {
            "Amount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Type": "Donation",
            "NonDeductibleAmount": 0,
            "FundId": 0,
            "QuickbooksAccountId": 0,
            "CampaignId": 0,
            "AppealId": 0,
            "TributeId": 0,
            "SoftCredits": [
                'null'
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": "string"
                },
                {
                    "FieldId": 0,
                    "ValueId": 0
                },
                {
                    "FieldId": 0,
                    "ValueIds": [
                        0
                    ]
                }
            ],
            "Attachments": [
                'null',
                'null'
            ]
        },
        {
            "Amount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Type": "PledgePayment",
            "PledgeId": 0,
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": "string"
                },
                {
                    "FieldId": 0,
                    "ValueId": 0
                },
                {
                    "FieldId": 0,
                    "ValueIds": [
                        0
                    ]
                }
            ],
            "Attachments": [
                'null',
                'null'
            ]
        },
        {
            "RecurringDonationEndDate": "2020-09-08",
            "Amount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "RecurringDonationFrequency": "Weekly",
            "RecurringDonationDay1": 0,
            "RecurringDonationDay2": 0,
            "RecurringDonationStartDate": "2020-09-08",
            "Type": "RecurringDonation",
            "FundId": 0,
            "QuickbooksAccountId": 0,
            "CampaignId": 0,
            "AppealId": 0,
            "TributeId": 0,
            "SoftCredits": [
                'null'
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": "string"
                },
                {
                    "FieldId": 0,
                    "ValueId": 0
                },
                {
                    "FieldId": 0,
                    "ValueIds": [
                        0
                    ]
                }
            ],
            "Attachments": [
                'null',
                'null'
            ]
        },
        {
            "Amount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Type": "RecurringDonationPayment",
            "RecurringDonationId": 0,
            "FundId": 0,
            "QuickbooksAccountId": 0,
            "CampaignId": 0,
            "AppealId": 0,
            "IsExtraPayment": 'true',
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": "string"
                },
                {
                    "FieldId": 0,
                    "ValueId": 0
                },
                {
                    "FieldId": 0,
                    "ValueIds": [
                        0
                    ]
                }
            ],
            "Attachments": [
                'null',
                'null'
            ]
        }
    ],
    "Attachments": [
        {
            "Guid": "string",
            "Name": "string",
            "Extension": "string",
            "Url": "string"
        },
        {
            "Id": 0,
            "Name": "string",
            "Extension": "string",
            "Url": "string"
        }
    ]
}

TEST_GET_TRANSACTION = {
    "Id": 0,
    "TransactionNumber": 0,
    "NonDeductibleAmount": 0,
    "AccountId": 0,
    "Date": "2020-09-08",
    "Amount": 0,
    "Method": "None",
    "CheckNumber": "string",
    "CheckDate": "2020-09-08",
    "CreditCardType": "Visa",
    "CreditCardLastFourDigits": "string",
    "CreditCardExpMonth": 0,
    "CreditCardExpYear": 0,
    "EftAccountType": "Checking",
    "EftLastFourDigits": "string",
    "EftRoutingNumber": "string",
    "InKindDescription": "string",
    "InKindType": "Goods",
    "InKindMarketValue": 0,
    "IntegrationUrl": "string",
    "Designations": [
        {
            "Id": 0,
            "DesignationNumber": 0,
            "TransactionId": 0,
            "Amount": 0,
            "NonDeductibleAmount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Fund": {
                "Id": 0,
                "Name": "string"
            },
            "QuickbooksAccount": {
                "Id": 0,
                "Name": "string"
            },
            "Campaign": {
                "Id": 0,
                "Name": "string"
            },
            "Appeal": {
                "Id": 0,
                "Name": "string"
            },
            "Tribute": {
                "Id": 0,
                "Name": "string"
            },
            "TributeType": "InHonorOf",
            "SoftCreditIds": [
                0
            ],
            "AttachmentIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T14:15:24.293Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T14:15:24.293Z",
                "LastModifiedName": "string"
            },
            "Type": "Donation"
        },
        {
            "Id": 0,
            "DesignationNumber": 0,
            "TransactionId": 0,
            "Amount": 0,
            "NonDeductibleAmount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Fund": {
                "Id": 0,
                "Name": "string"
            },
            "QuickbooksAccount": {
                "Id": 0,
                "Name": "string"
            },
            "Campaign": {
                "Id": 0,
                "Name": "string"
            },
            "Appeal": {
                "Id": 0,
                "Name": "string"
            },
            "Tribute": {
                "Id": 0,
                "Name": "string"
            },
            "TributeType": "InHonorOf",
            "SoftCreditIds": [
                0
            ],
            "AttachmentIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T14:15:24.293Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T14:15:24.293Z",
                "LastModifiedName": "string"
            },
            "Type": "Pledge",
            "PledgePaymentIds": [
                0
            ],
            "PledgeInstallments": [
                {
                    "Id": 0,
                    "PledgeId": 0,
                    "Date": "2020-09-08",
                    "Amount": 0
                }
            ],
            "PledgeBalance": 0,
            "PledgeStatus": "InGoodStanding",
            "PledgeAmountInArrears": 0,
            "PledgeNextInstallmentDate": "2020-09-08"
        },
        {
            "Id": 0,
            "DesignationNumber": 0,
            "TransactionId": 0,
            "Amount": 0,
            "NonDeductibleAmount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Fund": {
                "Id": 0,
                "Name": "string"
            },
            "QuickbooksAccount": {
                "Id": 0,
                "Name": "string"
            },
            "Campaign": {
                "Id": 0,
                "Name": "string"
            },
            "Appeal": {
                "Id": 0,
                "Name": "string"
            },
            "Tribute": {
                "Id": 0,
                "Name": "string"
            },
            "TributeType": "InHonorOf",
            "SoftCreditIds": [
                0
            ],
            "AttachmentIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T14:15:24.293Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T14:15:24.293Z",
                "LastModifiedName": "string"
            },
            "Type": "PledgePayment",
            "PledgeId": 0
        },
        {
            "Id": 0,
            "DesignationNumber": 0,
            "TransactionId": 0,
            "Amount": 0,
            "NonDeductibleAmount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Fund": {
                "Id": 0,
                "Name": "string"
            },
            "QuickbooksAccount": {
                "Id": 0,
                "Name": "string"
            },
            "Campaign": {
                "Id": 0,
                "Name": "string"
            },
            "Appeal": {
                "Id": 0,
                "Name": "string"
            },
            "Tribute": {
                "Id": 0,
                "Name": "string"
            },
            "TributeType": "InHonorOf",
            "SoftCreditIds": [
                0
            ],
            "AttachmentIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T14:15:24.293Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T14:15:24.293Z",
                "LastModifiedName": "string"
            },
            "RecurringDonationEndDate": "2020-09-08",
            "RecurringDonationFrequency": "Weekly",
            "RecurringDonationDay1": 0,
            "RecurringDonationDay2": 0,
            "RecurringDonationStartDate": "2020-09-08",
            "Type": "RecurringDonation",
            "RecurringDonationPaymentIds": [
                0
            ],
            "RecurringDonationNextInstallmentDate": "2020-09-08",
            "RecurringDonationLastPaymentStatus": "AtRisk",
            "RecurringDonationStatus": "Active"
        },
        {
            "Id": 0,
            "DesignationNumber": 0,
            "TransactionId": 0,
            "Amount": 0,
            "NonDeductibleAmount": 0,
            "Note": "string",
            "AcknowledgementStatus": 'true',
            "AcknowledgementInteractionIds": [
                0
            ],
            "Fund": {
                "Id": 0,
                "Name": "string"
            },
            "QuickbooksAccount": {
                "Id": 0,
                "Name": "string"
            },
            "Campaign": {
                "Id": 0,
                "Name": "string"
            },
            "Appeal": {
                "Id": 0,
                "Name": "string"
            },
            "Tribute": {
                "Id": 0,
                "Name": "string"
            },
            "TributeType": "InHonorOf",
            "SoftCreditIds": [
                0
            ],
            "AttachmentIds": [
                0
            ],
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T14:15:24.293Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T14:15:24.293Z",
                "LastModifiedName": "string"
            },
            "Type": "RecurringDonationPayment",
            "RecurringDonationId": 0
        }
    ],
    "AttachmentIds": [
        0
    ],
    "IsRefunded": 'true',
    "RefundIds": [
        0
    ],
    "AuditTrail": {
        "CreatedDate": "2020-09-08T14:15:24.293Z",
        "CreatedName": "string",
        "LastModifiedDate": "2020-09-08T14:15:24.293Z",
        "LastModifiedName": "string"
    }
}

TEST_GET_TRANSACTIONS = {
    "Total": 0,
    "TotalFiltered": 0,
    "Start": 0,
    "ResultCount": 0,
    "Results": [
        {
            "Id": 0,
            "TransactionNumber": 0,
            "NonDeductibleAmount": 0,
            "AccountId": 0,
            "Date": "2020-09-08",
            "Amount": 0,
            "Method": "None",
            "CheckNumber": "string",
            "CheckDate": "2020-09-08",
            "CreditCardType": "Visa",
            "CreditCardLastFourDigits": "string",
            "CreditCardExpMonth": 0,
            "CreditCardExpYear": 0,
            "EftAccountType": "Checking",
            "EftLastFourDigits": "string",
            "EftRoutingNumber": "string",
            "InKindDescription": "string",
            "InKindType": "Goods",
            "InKindMarketValue": 0,
            "IntegrationUrl": "string",
            "Designations": [
                'null',
                'null',
                'null',
                'null',
                'null'
            ],
            "AttachmentIds": [
                0
            ],
            "IsRefunded": 'true',
            "RefundIds": [
                0
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T16:11:30.821Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T16:11:30.821Z",
                "LastModifiedName": "string"
            }
        }
    ]
}

TEST_CREATE_INTERACTION = {
    "AccountId": 0,
    "Date": "2020-09-08",
    "Note": "string",
    "Channel": "Email",
    "Purpose": "Acknowledgement",
    "Subject": "string",
    "IsInbound": 'true',
    "CustomValues": [
        {
            "FieldId": 0,
            "Value": "string"
        },
        {
            "FieldId": 0,
            "ValueId": 0
        },
        {
            "FieldId": 0,
            "ValueIds": [
                0
            ]
        }
    ],
    "Attachments": [
        {
            "Guid": "string",
            "Name": "string",
            "Extension": "string",
            "Url": "string"
        },
        {
            "Id": 0,
            "Name": "string",
            "Extension": "string",
            "Url": "string"
        }
    ]
}

TEST_GET_INTERACTION = {
    "Id": 0,
    "Date": "2020-09-08",
    "Note": "string",
    "Channel": "Email",
    "Purpose": "Acknowledgement",
    "Subject": "string",
    "IsInbound": 'true',
    "AccountId": 0,
    "TweetId": "string",
    "IsBcc": 'true',
    "EmailAddress": "user@example.com",
    "AttachmentIds": [
        0
    ],
    "LetterAttachmentIds": [
        0
    ],
    "SurveyLapsedResponses": [
        "string"
    ],
    "SurveyEmailInteractionId": 0,
    "SurveyResponseInteractionId": 0,
    "CustomValues": [
        {
            "FieldId": 0,
            "Value": {
                "Id": 0,
                "Value": "string"
            }
        },
        {
            "FieldId": 0,
            "Values": [
                {
                    "Id": 0,
                    "Value": "string"
                }
            ]
        }
    ],
    "AuditTrail": {
        "CreatedDate": "2020-09-08T15:27:32.767Z",
        "CreatedName": "string",
        "LastModifiedDate": "2020-09-08T15:27:32.767Z",
        "LastModifiedName": "string"
    }
}

TEST_GET_INTERACTIONS = {
    "Total": 0,
    "TotalFiltered": 0,
    "Start": 0,
    "ResultCount": 0,
    "Results": [
        {
            "Id": 0,
            "Date": "2020-09-08",
            "Note": "string",
            "Channel": "Email",
            "Purpose": "Acknowledgement",
            "Subject": "string",
            "IsInbound": 'true',
            "AccountId": 0,
            "TweetId": "string",
            "IsBcc": 'true',
            "EmailAddress": "user@example.com",
            "AttachmentIds": [
                0
            ],
            "LetterAttachmentIds": [
                0
            ],
            "SurveyLapsedResponses": [
                "string"
            ],
            "SurveyEmailInteractionId": 0,
            "SurveyResponseInteractionId": 0,
            "CustomValues": [
                {
                    "FieldId": 0,
                    "Value": {
                        "Id": 0,
                        "Value": "string"
                    }
                },
                {
                    "FieldId": 0,
                    "Values": [
                        {
                            "Id": 0,
                            "Value": "string"
                        }
                    ]
                }
            ],
            "AuditTrail": {
                "CreatedDate": "2020-09-08T16:10:36.389Z",
                "CreatedName": "string",
                "LastModifiedDate": "2020-09-08T16:10:36.389Z",
                "LastModifiedName": "string"
            }
        }
    ]
}
