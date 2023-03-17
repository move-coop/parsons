from parsons.utilities.api_connector import APIConnector
from parsons.utilities import check_env
from parsons.bluelink.person import BluelinkPerson
import logging
import json

logger = logging.getLogger(__name__)

API_URL = "https://api.bluelink.org/webhooks/"


class Bluelink:
    """
    Instantiate a Bluelink connector.
    Allows for a simple method of inserting person data to Bluelink via a webhook.
    # see: https://bluelinkdata.github.io/docs/BluelinkApiGuide#webhook

    `Args:`:
        user: str
            Bluelink webhook user name.
        password: str
            Bluelink webhook password.
    """

    def __init__(self, user=None, password=None):
        self.user = check_env.check("BLUELINK_WEBHOOK_USER", user)
        self.password = check_env.check("BLUELINK_WEBHOOK_PASSWORD", password)
        self.headers = {
            "Content-Type": "application/json",
        }
        self.api_url = API_URL
        self.api = APIConnector(
            self.api_url, auth=(self.user, self.password), headers=self.headers
        )

    def upsert_person(self, source, person=None):
        """
        Upsert a BluelinkPerson object into Bluelink.
        Rows will update, as opposed to being inserted, if an existing person record in
        Bluelink has a matching BluelinkIdentifier (same source and id) as the BluelinkPerson object
        passed into this function.

        `Args:`
            source: str
                String to identify that the data came from your system. For example,
                your company name.
            person: BluelinkPerson
                A BluelinkPerson object.
                Will be inserted to Bluelink, or updated if a matching record is found.
        `Returns:`
            int
            An http status code from the http post request to the Bluelink webhook.
        """
        data = {"source": source, "person": person}
        jdata = json.dumps(
            data,
            default=lambda o: {k: v for k, v in o.__dict__.items() if v is not None},
        )
        resp = self.api.post_request(url=self.api_url, data=jdata)
        return resp

    def bulk_upsert_person(self, source, tbl, row_to_person):
        """
        Upsert all rows into Bluelink, using the row_to_person function to
        transform rows to BluelinkPerson objects.

        `Args:`
            source: str
                String to identify that the data came from your system.
                For example, your company name.
            tbl: Table
                A parsons Table that represents people data.
            row_to_person: Callable[[dict],BluelinkPerson]
                A function that takes a dict representation of a row from the passed in tbl
                and returns a BluelinkPerson object.

        `Returns:`
            list[int]
            A list of https response status codes, one response for each row in the table.
        """
        people = BluelinkPerson.from_table(tbl, row_to_person)
        responses = []
        for person in people:
            response = self.upsert_person(source, person)
            responses.append(response)
        return responses
