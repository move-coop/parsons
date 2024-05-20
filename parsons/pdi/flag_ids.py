class FlagIDs:
    """A class to access the FlagIDs PDI API endpoint."""

    def __init__(self):
        flags_endpoint = "/flags"
        flag_ids_endpoint = "/flag_ids"
        self.url_flags = self.base_url + flags_endpoint
        self.url_flag_ids = self.base_url + flag_ids_endpoint

        super().__init__()

    def get_flag_ids(self, limit=None):
        """Get a list of flag ids.

        `Args:`
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """
        return self._request(self.url_flag_ids, limit=limit)

    def get_flag_id(self, id):
        """Get a specified flag id.

        `Args:`
            id: str
                The flag id identifier.

        `Returns:`
            dict
                FlagID object.
        """
        return self._request(f"{self.url_flag_ids}/{id}")

    def create_flag_id(self, flag_id, is_default, flag_description=None, compile=None):
        """Save a new flag id.

        `Args:`
            flag_id: str
                The flag id type. One of: "AMM", "BNH", "BNM", "DEAD", "DNC",
                "DNR", "ENDR", "GTD", "HH", "L2VT", "LBO", "LM", "LO", "LS",
                "LSD", "LSR", "MAYBE", "MOV", "NAH", "NO", "REF", "SO", "SS",
                "SUP", "U", "UL2VT", "VL2VT", "VOL", "VTD".
            is_default: bool
                The default.
            flag_description: str
                (Optional) The flag id description.
            compile: str
                 (Optional) The compile.


        `Returns:`
            str
                The identifier for the new flag id.
        """
        payload = {
            "flagId": flag_id,
            "flagIdDescription": flag_description,
            "compile": compile,
            "isDefault": is_default,
        }
        data = self._request(self.url_flag_ids, req_type="POST", post_data=payload)

        return data["id"]

    def delete_flag_id(self, id):
        """Delete a flag id.

        NOTE: The function returns True (even if the id doesn't exist) unless
        there is an error.

        `Args:`
            id: str
                The flag id identifier.

        `Returns:`
            bool
                True if the operation is successful.
        """
        self._request(f"{self.url_flag_ids}/{id}", req_type="DELETE")

        return True

    def update_flag_id(self, id, flag_id, is_default, flag_description=None, compile=None):
        """Update a flag id.

        `Args:`
            id: str
                The flag id identifier.
            flag_id: str
                The flag id type. One of: "AMM", "BNH", "BNM", "DEAD", "DNC",
                "DNR", "ENDR", "GTD", "HH", "L2VT", "LBO", "LM", "LO", "LS",
                "LSD", "LSR", "MAYBE", "MOV", "NAH", "NO", "REF", "SO", "SS",
                "SUP", "U", "UL2VT", "VL2VT", "VOL", "VTD".
            is_default: bool
                The default.
            flag_description: str
                (Optional) The flag id description.
            compile: str
                 (Optional) The compile.

        `Returns:`
            str
                The identifier for the udpated flag id.
        """
        payload = {
            "flagId": flag_id,
            "flagIdDescription": flag_description,
            "compile": compile,
            "isDefault": is_default,
        }
        data = self._request(f"{self.url_flag_ids}/{id}", req_type="PUT", post_data=payload)

        return data["id"]
