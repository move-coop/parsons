from parsons.etl import Table
from requests import request
from parsons.utilities import check_env, json_format
import datetime
from parsons.hustle.column_map import LEAD_COLUMN_MAP
import logging

logger = logging.getLogger(__name__)

HUSTLE_URI = "https://api.hustle.com/v1/"
PAGE_LIMIT = 1000


class Hustle(object):
    """
    Instantiate Hustle Class

    `Args:`
        client_id:
            The client id provided by Hustle. Not required if ``HUSTLE_CLIENT_ID`` env variable
            set.
        client_secret:
            The client secret provided by Hustle. Not required if ``HUSTLE_CLIENT_SECRET`` env
            variable set.
    `Returns:`
        Hustle Class
    """

    def __init__(self, client_id, client_secret):

        self.uri = HUSTLE_URI
        self.client_id = check_env.check("HUSTLE_CLIENT_ID", client_id)
        self.client_secret = check_env.check("HUSTLE_CLIENT_SECRET", client_secret)
        self.token_expiration = None
        self._get_auth_token(client_id, client_secret)

    def _get_auth_token(self, client_id, client_secret):
        # Generate a temporary authorization token

        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        r = request("POST", self.uri + "oauth/token", data=data)
        logger.debug(r.json())

        self.auth_token = r.json()["access_token"]
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(
            seconds=7200
        )
        logger.info("Authentication token generated")

    def _token_check(self):
        # Tokens are only valid for 7200 seconds. This checks to make sure that it has
        # not expired and generate another one if it has.

        logger.debug("Checking token expiration.")
        if datetime.datetime.now() >= self.token_expiration:

            logger.info("Refreshing authentication token.")
            self._get_auth_token(self.client_id, self.client_secret)

        else:

            pass

    def _request(
        self, endpoint, req_type="GET", args=None, payload=None, raise_on_error=True
    ):

        url = self.uri + endpoint
        self._token_check()

        headers = {"Authorization": f"Bearer {self.auth_token}"}

        parameters = {}
        if req_type == "GET":
            parameters = {"limit": PAGE_LIMIT}

        if args:
            parameters.update(args)

        r = request(req_type, url, params=parameters, json=payload, headers=headers)

        self._error_check(r, raise_on_error)

        # If a single item return the dict
        if "items" not in r.json().keys():

            return r.json()

        else:
            result = r.json()["items"]

        # Pagination
        while r.json()["pagination"]["hasNextPage"] == "true":

            parameters["cursor"] = r.json["pagination"]["cursor"]
            r = request(req_type, url, params=parameters, headers=headers)
            self._error_check(r, raise_on_error)
            result.append(r.json()["items"])

        return result

    def _error_check(self, r, raise_on_error):
        # Check for errors

        if r.status_code in (200, 201):

            logger.debug(r.json())
            return None

        if raise_on_error:

            logger.info(r.json())
            r.raise_for_status()
            return None

        else:

            logger.info(r.json())
            return None

    def get_agents(self, group_id):
        """
        Get a list of agents.

        `Args:`
            group_id: str
                The group id.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self._request(f"groups/{group_id}/agents"))
        logger.info(f"Got {tbl.num_rows} agents from {group_id} group.")
        return tbl

    def get_agent(self, agent_id):
        """
        Get a single agent.

        `Args:`
            agent_id: str
                The agent id.
        `Returns:`
            dict
        """

        r = self._request(f"agents/{agent_id}")
        logger.info(f"Got {agent_id} agent.")
        return r

    def create_agent(
        self, group_id, name, full_name, phone_number, send_invite=False, email=None
    ):
        """
        Create an agent.

        `Args:`
            group_id: str
                The group id to assign the agent.
            name: str
                The name of the agent.
            full_name: str
                The full name of the agent.
            phone_number: str
                The valid phone number of the agent.
            send_invite: boolean
                Send an invitation to the agent.
            email:
                The email address of the agent.
        `Returns:`
            dict
        """

        agent = {
            "name": name,
            "fullName": full_name,
            "phoneNumber": phone_number,
            "sendInvite": send_invite,
            "email": email,
        }

        # Remove empty args in dictionary
        agent = json_format.remove_empty_keys(agent)

        logger.info(f"Generating {full_name} agent.")
        return self._request(
            f"groups/{group_id}/agents", req_type="POST", payload=agent
        )

    def update_agent(self, agent_id, name=None, full_name=None, send_invite=False):
        """
        Update an agent.

        `Args:`
            agent_id: str
                The agent id.
            name: str
                The name of the agent.
            full_name: str
                The full name of the agent.
            phone_number: str
                The valid phone number of the agent.
            send_invite: boolean
                Send an invitation to the agent.
        `Returns:`
            dict
        """

        agent = {"name": name, "fullName": full_name, "sendInvite": send_invite}

        # Remove empty args in dictionary
        agent = json_format.remove_empty_keys(agent)

        logger.info(f"Updating agent {agent_id}.")
        return self._request(f"agents/{agent_id}", req_type="PUT", payload=agent)

    def get_organizations(self):
        """
        Get organizations.

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self._request("organizations"))
        logger.info(f"Got {tbl.num_rows} organizations.")
        return tbl

    def get_organization(self, organization_id):
        """
        Get a single organization.

        `Args:`
            organization_id: str
                The organization id.
        `Returns:`
            dict
        """

        r = self._request(f"organizations/{organization_id}")
        logger.info(f"Got {organization_id} organization.")
        return r

    def get_groups(self, organization_id):
        """
        Get a list of groups.

        `Args:`
            organization_id: str
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self._request(f"organizations/{organization_id}/groups"))
        logger.info(f"Got {tbl.num_rows} groups.")
        return tbl

    def get_group(self, group_id):
        """
        Get a single group.

        `Args:`
            group_id: str
                The group id.
        """

        r = self._request(f"groups/{group_id}")
        logger.info(f"Got {group_id} group.")
        return r

    def create_group_membership(self, group_id, lead_id):
        """
        Add a lead to a group.

        `Args:`
            group_id: str
                The group id.
            lead_id: str
                The lead id.
        """

        return self._request(
            f"groups/{group_id}/memberships",
            req_type="POST",
            payload={"leadId": lead_id},
        )

    def get_lead(self, lead_id):
        """
        Get a single lead.

        `Args`:
            lead_id: str
                The lead id.
        `Returns:`
            dict
        """

        r = self._request(f"leads/{lead_id}")
        logger.info(f"Got {lead_id} lead.")
        return r

    def get_leads(self, organization_id=None, group_id=None):
        """
        Get leads metadata. One of ``organization_id`` and ``group_id`` must be passed
        as an argument. If both are passed, an error will be raised.

        `Args:`
            organization_id: str
                The organization id.
            group_id: str
                The group id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        if organization_id is None and group_id is None:
            raise ValueError("Either organization_id or group_id required.")

        if organization_id is not None and group_id is not None:
            raise ValueError(
                "Only one of organization_id and group_id may be populated."
            )

        if organization_id:
            endpoint = f"organizations/{organization_id}/leads"
            logger.info(f"Retrieving {organization_id} organization leads.")
        if group_id:
            endpoint = f"groups/{group_id}/leads"
            logger.info(f"Retrieving {group_id} group leads.")

        tbl = Table(self._request(endpoint))
        logger.info(f"Got {tbl.num_rows} leads.")
        return tbl

    def create_lead(
        self,
        group_id,
        phone_number,
        first_name,
        last_name=None,
        email=None,
        notes=None,
        follow_up=None,
        custom_fields=None,
        tag_ids=None,
    ):
        """

        Create a lead.

        `Args:`
            group_id: str
                The group id to assign the leads.
            first_name: str
                The first name of the lead.
            phone_number: str
                The phone number of the lead.
            last_name: str
                The last name of the lead.
            email: str
                The email address of the lead.
            notes: str
                The notes for the lead.
            follow_up: str
                Follow up for the lead.
            custom_fields: dict
                A dictionary of custom fields, with key as the value name, and
                value as the value.
            tag_ids: list
                A list of tag ids.
        `Returns:`
                ``None``
        """

        lead = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phoneNumber": phone_number,
            "notes": notes,
            "followUp": follow_up,
            "customFields": custom_fields,
            "tagIds": tag_ids,
        }

        # Remove empty args in dictionary
        lead = json_format.remove_empty_keys(lead)
        logger.info(f"Generating lead for {first_name} {last_name}.")
        return self._request(f"groups/{group_id}/leads", req_type="POST", payload=lead)

    def create_leads(self, table, group_id=None):
        """
        Create multiple leads. All unrecognized fields will be passed as custom fields. Column
        names must map to the following names.

        .. list-table::
            :widths: 20 80
            :header-rows: 1

            * - Column Name
              - Valid Column Names
            * - first_name
              - ``first_name``, ``first``, ``fn``, ``firstname``
            * - last_name
              - ``last_name``, ``last``, ``ln``, ``lastname``
            * - phone_number
               - ``phone_number``, ``phone``, ``cell``, ``phonenumber``, ``cell_phone``
                ``cellphone``
            * - email
              - ``email``, ``email_address``, ``emailaddress``
            * - follow_up
              - ``follow_up``, ``followup``

        `Args:`
            table: Parsons table
                A Parsons table containing leads
            group_id:
                The group id to assign the leads. If ``None``, must be passed as a column
                value.
        `Returns:`
            A table of created ids with associated lead id.
        """

        table.map_columns(LEAD_COLUMN_MAP)

        arg_list = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "follow_up",
            "tag_ids",
            "group_id",
        ]

        created_leads = []

        for row in table:

            lead = {"group_id": group_id}
            custom_fields = {}

            # Check for column names that map to arguments, if not assign
            # to custom fields
            for k, v in row.items():
                if k in arg_list:
                    lead[k] = v
                else:
                    custom_fields[k] = v

            lead["custom_fields"] = custom_fields

            # Group Id check
            if not group_id and "group_id" not in table.columns:
                raise ValueError(
                    "Group Id must be passed as an argument or a column value."
                )
            if group_id:
                lead["group_id"] = group_id

            created_leads.append(self.create_lead(**lead))

        logger.info(f"Created {table.num_rows} leads.")
        return Table(created_leads)

    def update_lead(
        self,
        lead_id,
        first_name=None,
        last_name=None,
        email=None,
        global_opt_out=None,
        notes=None,
        follow_up=None,
        tag_ids=None,
    ):
        """
        Update a lead.

        `Args`:
            lead_id: str
                The lead id
            first_name: str
                The first name of the lead
            last_name: str
                The last name of the lead
            email: str
                The email address of the lead
            global_opt_out: boolean
                Opt out flag for the lead
            notes: str
                The notes for the lead
            follow_up: str
                Follow up for the lead
            tag_ids: list
                Tags to apply to lead
        `Returns:`
            dict
        """

        lead = {
            "leadId": lead_id,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "globalOptedOut": global_opt_out,
            "notes": notes,
            "followUp": follow_up,
            "tagIds": tag_ids,
        }

        # Remove empty args in dictionary
        lead = json_format.remove_empty_keys(lead)

        logger.info(f"Updating lead for {first_name} {last_name}.")
        return self._request(f"leads/{lead_id}", req_type="PUT", payload=lead)

    def get_tags(self, organization_id):
        """
        Get an organization's tags.

        `Args:`
            organization_id: str
                The organization id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        tbl = Table(self._request(f"organizations/{organization_id}/tags"))
        logger.info(f"Got {tbl.num_rows} tags for {organization_id} organization.")
        return tbl

    def get_tag(self, tag_id):
        """
        Get a single tag.

        `Args:`
            tag_id: str
                The tag id.
        `Returns:`
            dict
        """

        r = self._request(f"tags/{tag_id}")
        logger.info(f"Got {tag_id} tag.")
        return r
