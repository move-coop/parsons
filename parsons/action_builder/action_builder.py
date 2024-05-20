import json
from parsons import Table
from parsons.utilities import check_env
from parsons.utilities.api_connector import APIConnector
import logging

logger = logging.getLogger(__name__)

API_URL = "https://{subdomain}.actionbuilder.org/api/rest/v1"


class ActionBuilder(object):
    """
    `Args:`
        api_token: str
            The OSDI API token
        subdomain: str
            The part of the web app URL preceding '.actionbuilder.org'
        campaign: str
            Optional. The 36-character "interact ID" of the campaign whose data is to be retrieved
            or edited. Can also be supplied in individual methods in case multiple campaigns need
            to be referenced.
    """

    def __init__(self, api_token=None, subdomain=None, campaign=None):
        self.api_token = check_env.check("ACTION_BUILDER_API_TOKEN", api_token)
        self.headers = {
            "Content-Type": "application/json",
            "OSDI-API-Token": self.api_token,
        }
        self.api_url = API_URL.format(subdomain=subdomain)
        self.api = APIConnector(self.api_url, headers=self.headers)
        self.campaign = campaign

    def _campaign_check(self, campaign):
        # Raise an error if campaign is not provided via instatiation nor method argument

        final_campaign = campaign or self.campaign
        if not final_campaign:
            raise ValueError("No campaign provided!")

        return final_campaign

    def _get_page(self, campaign, object_name, page, per_page=25, filter=None):
        # Returns data from one page of results

        campaign = self._campaign_check(campaign)

        if per_page > 25:
            per_page = 25
            logger.info(
                "Action Builder's API will not return more than 25 entries per page. \
            Changing per_page parameter to 25."
            )

        params = {"page": page, "per_page": per_page, "filter": filter}

        url = f"campaigns/{campaign}/{object_name}"

        return self.api.get_request(url=url, params=params)

    def _get_all_records(self, campaign, object_name, limit=None, per_page=25, filter=None):
        # Returns a list of entries for a given object, such as people, tags, or connections.
        # See Action Builder API docs for more: https://www.actionbuilder.org/docs/v1/index.html

        count = 0
        page = 1
        return_list = []

        # Keep getting the next page until record limit is exceeded or an empty result returns
        while True:
            # Get this page and increase page number to the next one
            response = self._get_page(campaign, object_name, page, per_page, filter=filter)
            page = page + 1

            # Check that there's actually data
            response_list = response.get("_embedded", {}).get(f"osdi:{object_name}")

            if not response_list:
                # This page has no data, so we're done
                return Table(return_list)

            # Assuming there's data, add it to the running response list
            return_list.extend(response_list)
            count = count + len(response_list)
            if limit:
                if count >= limit:
                    # Limit reached or exceeded, so return just the requested limit amount
                    return Table(return_list[0:limit])

    def get_campaign_tags(self, campaign=None, limit=None, per_page=25, filter=None):
        """
        Retrieve all tags (i.e. custom field values) within provided limit and filters
        `Args:`
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
            limit: int
                The number of entries to return. When None, returns all entries.
            per_page: int
                The number of entries per page to return. 25 maximum and default.
            filter
                The OData query for filtering results. E.g. "modified_date gt '2014-03-25'".
                When None, no filter is applied.
        `Returns:`
            Parsons Table of full set of tags available in Action Builder.
        """

        return self._get_all_records(
            campaign, "tags", limit=limit, per_page=per_page, filter=filter
        )

    def get_tag_by_name(self, tag_name, campaign=None):
        """
        Convenience method to retrieve data on a single tag by its name/value
        `Args:`
            tag_name: str
                The value of the tag to search for.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Parsons Table of data found on tag in Action Builder from searching by name.
        """

        filter = f"name eq '{tag_name}'"

        return self.get_campaign_tags(campaign=campaign, filter=filter)

    def insert_new_tag(self, tag_name, tag_field, tag_section, campaign=None):
        """
        Load a new tag value into Action Builder. Required before applying the value to any entity
        records.
        `Args:`
            tag_name: str
                The name of the new tag, i.e. the custom field value.
            tag_field: str
                The name of the tag category, i.e. the custom field name.
            tag_section: str
                The name of the tag section, i.e. the custom field group name.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Dict containing Action Builder tag data.
        """

        campaign = self._campaign_check(campaign)
        url = f"campaigns/{campaign}/tags"

        data = {
            "name": tag_name,
            "action_builder:field": tag_field,
            "action_builder:section": tag_section,
        }

        return self.api.post_request(url=url, data=json.dumps(data))

    def _upsert_entity(self, data, campaign):
        # Internal method leveraging the record signup helper endpoint to upsert entity records

        url = f"campaigns/{campaign}/people"

        return self.api.post_request(url=url, data=json.dumps(data))

    def insert_entity_record(self, entity_type, data=None, campaign=None):
        """
        Load a new entity record in Action Builder of the type provided.
        `Args:`
            entity_type: str
                The name of the record type being inserted. Required if identifiers are not
                provided.
            data: dict
                The details to include on the record being upserted, to be included as the value
                of the `person` key. See
                [documentation for the Person Signup Helper](https://www.actionbuilder.org/docs/v1/person_signup_helper.html#post)
                for examples, and
                [the Person endpoint](https://www.actionbuilder.org/docs/v1/people.html#field-names)
                for full entity object composition.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Dict containing Action Builder entity data.
        """  # noqa: E501

        name_keys = ("name", "action_builder:name", "given_name")
        error = "Must provide data with name or given_name when inserting new record"
        if not isinstance(data, dict):
            raise ValueError(error)
        name_check = [key for key in data.get("person", {}) if key in name_keys]
        if not name_check:
            raise ValueError(error)

        campaign = self._campaign_check(campaign)

        if not isinstance(data, dict):
            data = {}

        if "person" not in data:
            # The POST data must live inside of person key
            data["person"] = {}

        data["person"]["action_builder:entity_type"] = entity_type

        return self._upsert_entity(data=data, campaign=campaign)

    def update_entity_record(self, identifier, data, campaign=None):
        """
        Update an entity record in Action Builder based on the identifier passed.
        `Args:`
            identifier: str
                The unique identifier for a record being updated. ID strings will need to begin
                with the origin system, followed by a colon, e.g. `action_builder:abc123-...`.
            data: dict
                The details to include on the record being upserted, to be included as the value
                of the `person` key. See
                [documentation for the Person Signup Helper](https://www.actionbuilder.org/docs/v1/person_signup_helper.html#post)
                for examples, and
                [the Person endpoint](https://www.actionbuilder.org/docs/v1/people.html#field-names)
                for full entity object composition.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Dict containing Action Builder entity data.
        """  # noqa: E501

        campaign = self._campaign_check(campaign)

        if isinstance(identifier, str):
            # Ensure identifier is a list, even though singular string is called for
            identifier = [identifier]

        # Default to assuming identifier comes from Action Builder and add prefix if missing
        identifiers = [f"action_builder:{id}" if ":" not in id else id for id in identifier]

        if not isinstance(data, dict):
            data = {}

        if "person" not in data:
            # The POST data must live inside of person key
            data["person"] = {}

        data["person"]["identifiers"] = identifiers

        return self._upsert_entity(data=data, campaign=campaign)

    def add_section_field_values_to_record(self, identifier, section, field_values, campaign=None):
        """
        Add one or more tags (i.e. custom field value) to an existing entity record in Action
        Builder. The tags, along with their field and section, must already exist (except for
        date fields).
        `Args:`
            identifier: str
                The unique identifier for a record being updated. ID strings will need to begin
                with the origin system, followed by a colon, e.g. `action_builder:abc123-...`.
            section: str
                The name of the tag section, i.e. the custom field group name.
            field_values: dict
                A collection of field names and tags stored as keys and values.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Dict containing Action Builder entity data of the entity being tagged.
        """

        tag_data = [
            {
                "action_builder:name": tag,
                "action_builder:field": field,
                "action_builder:section": section,
            }
            for field, tag in field_values.items()
        ]

        data = {"add_tags": tag_data}

        return self.update_entity_record(identifier=identifier, data=data, campaign=campaign)

    def remove_tagging(
        self,
        identifier=None,
        tag_id=None,
        tag_name=None,
        tagging_id=None,
        campaign=None,
    ):
        """
        Remove one or more tags (i.e. custom field value) from an existing entity or connection
        record in Action Builder. The basis for this end point is the combination of the tag's
        interact ID and that of the specific tagging. The tag ID can usually be determined from
        the tag's name, and the tagging ID can be derived if the identifier of the entity or
        connection record is supplied instead.
        `Args:`
            identifier: str
                Optional. The unique identifier for an entity or connection record being updated.
                If omitted, `tagging_id` must be provided.
            tag_id: str
                Optional. The unique identifier for the tag being removed. If omitted, `tag_name`
                must be provided.
            tag_name: str
                Optional. The exact name of the tag being removed. May result in an error if
                multiple tags (in different fields/sections) have the same name. If omitted,
                `tag_id` must be provided.
            tagging_id: str
                Optional. The unique identifier for the specific application of the tag to an
                individual entity or connection record. If omitted, `identifier` must be provided.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            API response JSON which contains `{'message': 'Tag has been removed from Taggable
            Logbook'}` if successful.
        """

        if {tag_name, tag_id} == {None}:
            raise ValueError("Please supply a tag_name or tag_id!")

        if {identifier, tagging_id} == {None}:
            raise ValueError("Please supply an entity or connection identifier, or a tagging id!")

        campaign = self._campaign_check(campaign)
        endpoint = "tags/{}/taggings"

        if tag_name and {tag_id, tagging_id} == {None}:
            tag_data = self.get_tag_by_name(tag_name, campaign=campaign)
            tag_count = tag_data.num_rows

            if tag_count > 1:
                error_msg = f"Found {tag_count} tags with this name. "
                error_msg += "Try with using the unique interact ID"
                raise ValueError(error_msg)

            tag_id = tag_data["identifiers"][0][0].split(":")[1]
            logger.info(f"Tag {tag_name} has ID {tag_id}")

        if tagging_id and not tag_id:
            raise ValueError("Cannot search based on tagging ID alone.")

        if tag_id and not tagging_id:
            taggings = self._get_all_records(self.campaign, endpoint.format(tag_id))
            taggings_filtered = taggings.select_rows(
                lambda row: (
                    identifier in row["_links"]["action_builder:connection"]["href"]
                    if row["item_type"] == "connection"
                    else identifier in row["osdi:person"]["href"]
                )
            )
            tagging_id = [
                x.split(":")[1]
                for x in taggings_filtered["identifiers"][0]
                if "action_builder" in x
            ][0]

        logger.info(f"Removing tag {tag_id} from {identifier or tagging_id}")
        return self.api.delete_request(
            f"campaigns/{campaign}/{endpoint.format(tag_id)}/{tagging_id}"
        )

    def upsert_connection(self, identifiers, tag_data=None, campaign=None, reactivate=True):
        """
        Load or update a connection record in Action Builder between two existing entity records.
        Only one connection record is allowed per pair of entities, so if the connection already
        exists, this method will update, but will otherwise create a new connection record.
        `Args:`
            identifiers: list
                A list of two unique identifier strings for records being connected. ID strings
                will need to begin with the origin system, followed by a colon, e.g.
                `action_builder:abc123-...`. Requires exactly two identifiers.
            tag_data: list
                List of dicts of tags to be added to the connection record (i.e. Connection Info).
                See [documentation on Connection Helper](https://www.actionbuilder.org/docs/v1/connection_helper.html#post)
                for examples.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
            reactivate: bool
                Optional. Whether or not to set the `inactive` flag on a given Connection to False
                if the Connection exists and has `inactive` set to True. True by default.
        `Returns:`
            Dict containing Action Builder connection data.
        """  # noqa: E501

        # Check that there are exactly two identifiers and that campaign is provided first
        if not isinstance(identifiers, list):
            raise ValueError("Must provide identifiers as a list")

        if len(identifiers) != 2:
            raise ValueError("Must provide exactly two identifiers")

        campaign = self._campaign_check(campaign)

        url = f"campaigns/{campaign}/people/{identifiers[0]}/connections"

        data = {
            "connection": {
                # person_id is used even if entity is not Person
                "person_id": identifiers[1]
            }
        }

        if reactivate:
            data["connection"]["inactive"] = False

        if tag_data:
            if isinstance(tag_data, dict):
                tag_data = [tag_data]

            if not isinstance(tag_data[0], dict):
                raise ValueError("Must provide tag_data as a dict or list of dicts")

            data["add_tags"] = tag_data

        return self.api.post_request(url=url, data=json.dumps(data))

    def deactivate_connection(
        self,
        from_identifier,
        connection_identifier=None,
        to_identifier=None,
        campaign=None,
    ):
        """
        Deactivate an existing connection record in Action Builder between two existing entity
        records. Only one connection record is allowed per pair of entities, so this can be done
        by supplying the ID for the connection record, or for the two connected entity records.
        `Args:`
            from_identifier: str
                Unique identifier for one of the two entities with a connection.
            connection_identifier: str
                Optional. The unique identifier for an entity or connection record being updated.
                If omitted, `to_identifier` must be provided.
            to_identifier: str
                Optional. The second entity with a connection to `from_entity`. If omitted,
                `connection_identifier` must be provided.
            campaign: str
                Optional. The 36-character "interact ID" of the campaign whose data is to be
                retrieved or edited. Not necessary if supplied when instantiating the class.
        `Returns:`
            Dict containing Action Builder connection data.
        """

        # Check that either connection or second entity identifier are provided
        if {connection_identifier, to_identifier} == {None}:
            raise ValueError("Must provide a connection ID or an ID for the second entity")

        campaign = self._campaign_check(campaign)

        url = f"campaigns/{campaign}/people/{from_identifier}/connections"

        data = {"connection": {"inactive": True}}

        # Prioritize connection ID to avoid potential confusion if to_identifier is also provided
        # to_identifier entity could have duplicates, connection ID is more specific
        if connection_identifier:
            url += f"/{connection_identifier}"

            # Despite the documentation, PUT requests don't require the outer "connection" key
            data = data["connection"]

            return self.api.put_request(url=url, data=json.dumps(data))

        # If no connection ID then there must be a to_identifier not to have errored by now
        else:
            data["connection"]["person_id"] = to_identifier
            return self.api.post_request(url=url, data=json.dumps(data))
