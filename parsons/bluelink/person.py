import logging
import json

logger = logging.getLogger(__name__)


class BluelinkPerson(object):
    """
    Instantiate BluelinkPerson Class.
    Used for to upserting via Bluelink connector.
    See: https://bluelinkdata.github.io/docs/BluelinkApiGuide#person-object

    `Args:`
        identifiers: list[BluelinkIdentifier]
            A list of BluelinkIdentifier objects.
            A BluelinkPerson must have at least 1 identifier.
        given_name: str
            First name / given name.
        family_name: str
            Last name / family name.
        phones: list[BluelinkPhone]
            A list of BluelinkPhone objects representing phone numbers.
        emails: list[BluelinkEmail]
            A list of BluelinkEmail objects representing email addresses.
        addresses: list[BluelinkAddress]
            A list of BluelinkAddress objects representing postal addresses.
        tags: list[BluelinkTag]
            Simple tags that apply to the person, eg DONOR.
        employer: str
            Name of the persons employer.
        employer_address: BluelinkAddress
            BluelinkAddress of the persons employer.
        occupation: str
            Occupation.
        scores: list[BluelinkScore]
            List of BluelinkScore objects. Scores are numeric scores, ie partisanship model.
        birthdate: str
            ISO 8601 formatted birth date: 'YYYY-MM-DD'
        details: dict
            additional custom data. must be json serializable.
    """

    def __init__(
        self,
        identifiers,
        given_name=None,
        family_name=None,
        phones=None,
        emails=None,
        addresses=None,
        tags=None,
        employer=None,
        employer_address=None,
        occupation=None,
        scores=None,
        birthdate=None,
        details=None,
    ):

        if not identifiers:
            raise Exception(
                "BluelinkPerson requires list of BluelinkIdentifiers with "
                "at least 1 BluelinkIdentifier"
            )

        self.identifiers = identifiers
        self.addresses = addresses
        self.emails = emails
        self.phones = phones
        self.tags = tags
        self.scores = scores

        self.given_name = given_name
        self.family_name = family_name

        self.employer = employer
        self.employer_address = employer_address
        self.occupation = occupation
        self.birthdate = birthdate
        self.details = details

    def __json__(self):
        """The json str representation of this BluelinkPerson object"""
        return json.dumps(self, default=lambda obj: obj.__dict__)

    def __eq__(self, other):
        """A quick and dirty equality check"""
        dself = json.loads(self.__json__())
        dother = json.loads(other.__json__())
        return dself == dother

    def __repr__(self):
        return self.__json__()

    @staticmethod
    def from_table(tbl, dict_to_person):
        """
        Return a list of BluelinkPerson objects from a Parsons Table.

        `Args:`
            tbl: Table
                A parsons Table.
            dict_to_person: Callable[[dict],BluelinkPerson]
                A function that takes a dictionary representation of a table row,
                and returns a BluelinkPerson.
        `Returns:`
           list[BluelinkPerson]
           A list of BluelinkPerson objects.
        """
        return [dict_to_person(row) for row in tbl]


class BluelinkIdentifier(object):
    """
    Instantiate an BluelinkIdentifier object.
    BluelinkIdentifier is necessary for updating BluelinkPerson records.

    `Args:`
        source: str
            External system to which this ID belongs, e.g., “VAN:myCampaign”.
            Bluelink has standardized strings for source. Using these will
            allow Bluelink to correctly understand the external IDs you add.
            source (unlike identifier) is case insensitive.
            examples: BLUELINK, PDI, SALESFORCE, VAN:myCampaign, VAN:myVoters
        identifier: str
            Case-sensitive ID in the external system.
        details: dict
            dictionary of custom fields. must be serializable to json.
    """

    def __init__(self, source, identifier, details=None):
        self.source = source
        self.identifier = identifier
        self.details = details


class BluelinkEmail(object):
    """
    Instantiate an BluelinkEmail object.

    `Args:`
        address: str
            An email address. ie "user@example.com"
        primary: bool
            True if this is known to be the primary email.
        type: str
            Type, eg: "personal", "work"
        status: str
            One of "Potential", "Subscribed", "Unsubscribed", "Bouncing", or "Spam Complaints"
    """

    def __init__(self, address, primary=None, type=None, status=None):
        self.address = address
        self.primary = primary
        self.type = type
        self.status = status


class BluelinkAddress(object):
    """
    Instantiate an BluelinkAddress object.

    `Args`:
        address_lines: list[str]
            A list of street address lines.
        city: str
            City or other locality.
        state: str
            State in ISO 3166-2.
        postal_code: str
            Zip or other postal code.
        country: str
            ISO 3166-1 Alpha-2 country code.
        type: str
            The type. ie: "home", "mailing".
        venue: str
            The venue name, if relevant.
        status: str
            A value representing the status of the address. "Potential", "Verified" or "Bad"
    """

    def __init__(
        self,
        address_lines=None,
        city=None,
        state=None,
        postal_code=None,
        country=None,
        type=None,
        venue=None,
        status=None,
    ):

        self.address_lines = address_lines or []
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.country = country

        self.type = type
        self.venue = venue
        self.status = status


class BluelinkPhone(object):
    """
    Instantiate a BluelinkPhone object.

    `Args:`
        number: str
            A phone number. May or may not include country code.
        primary: bool
            True if this is known to be the primary phone.
        description: str
            Free for description.
        type: str
            Type, eg: "Home", "Work", "Mobile"
        country: str
            ISO 3166-1 Alpha-2 country code.
        sms_capable: bool
            True if this number can accept SMS.
        do_not_call: bool
            True if this number is on the US FCC Do Not Call Registry.
        details: dict
            Additional data dictionary. Must be json serializable.
    """

    def __init__(
        self,
        number,
        primary=None,
        description=None,
        type=None,
        country=None,
        sms_capable=None,
        do_not_call=None,
        details=None,
    ):
        self.number = number
        self.primary = primary
        self.description = description
        self.type = type
        self.country = country
        self.sms_capable = sms_capable
        self.do_not_call = do_not_call
        self.details = details


class BluelinkTag(object):
    """
    Instantiate a BluelinkTag object.

    `Args:`
        tag: str
            A tag string; convention is either a simple string
            or a string with a prefix separated by a colon, e.g., “DONOR:GRASSROOTS”
    """

    def __init__(self, tag):
        self.tag = tag


class BluelinkScore(object):
    """
    Instantiate a score object.
    Represents some kind of numeric score.

    `Args`:
        score: float
            Numeric score.
        score_type: str
            Type, eg: "Partisanship model".
        source: str
            Original source of this score.
    """

    def __init__(self, score, score_type, source):
        self.score = score
        self.score_type = score_type
        self.source = source
