from typing import Literal


class Contacts:
    """A class to access the contacts PDI API endpoint."""

    def __init__(self):
        self.url_contacts = self.base_url + "/contacts"
        super().__init__()

    def get_contacts(
        self,
        email: str | None = None,
        phone: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        zip_code: str | None = None,
        search_by_email: bool = False,
        limit: int | None = None,
    ):
        """
        Get a list of Contacts.

        Args:
            email (str):
            phone (str):
            first_name (str):
            last_name (str):
            zip_code (str):
            search_by_email (bool): whether to search using email address
            limit (int): The number of contacts to return

        Returns:
            parsons.Table

        """
        params = {
            "email": email,
            "phone": phone,
            "firstName": first_name,
            "lastName": last_name,
            "zipCode": zip_code,
            "searchByEmail": search_by_email,
        }
        return self._request(self.url_contacts, args=params, limit=limit)

    def create_contact(
        self,
        name_prefix="",
        first_name="",
        last_name="",
        middle_name="",
        name_suffix="",
        nickname="",
        occupation="",
        employer="",
        volunteer_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        donor_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        member_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        date_of_birth=None,
        gender: Literal["F", "M", "U"] | None = None,
        email="",
        pdi_id=None,
    ):
        """
        Create new contact

        Args:
            name_prefix (str): Prefix for the name.
            first_name (str): The contact's first name.
            last_name (str): The contact's last name.
            middle_name (str): The contact's middle name.
            name_suffix (str): Suffix for the name.
            nickname (str): The contact's nickname.
            occupation (str): The contact's occupation.
            employer (str): The contact's employer.
            volunteer_status (str): Options are "Prospect", "Active", "Inactive", "None", or "".
            donor_status (str): Options are "Prospect", "Active", "Inactive", "None", or "".
            member_status (str): Options are "Prospect", "Active", "Inactive", "None", or "".
            date_of_birth (str, optional): Format allowed yyyy-MM-dd.
            gender (str, optional): Options are "F", "M", or "U".
            email (str, optional): The contact's email.
            pdi_id (str, optional): Ignored when updating.

        Returns:
            parsons.Table: A Table containing the response data.

        """
        payload = {
            "namePrefix": name_prefix,
            "firstName": first_name,
            "lastName": last_name,
            "nameSuffix": name_suffix,
            "nickname": nickname,
            "middleName": middle_name,
            "occupation": occupation,
            "employer": employer,
            "volunteerStatus": volunteer_status,
            "donorStatus": donor_status,
            "memberStatus": member_status,
            "dateOfBirth": date_of_birth,
            "gender": gender,
            "emailAddress": email,
            "pdiId": pdi_id,
        }
        return self._request(self.url_contacts, req_type="POST", post_data=payload)

    def get_contact(self, id: str):
        """
        Get a Contact by id.

        Args:
            id: str
                The Contact id

        Returns:
            parsons.Table

        """
        # todo not working quite right
        return self._request(f"{self.url_contacts}/{id}")

    def update_contact(
        self,
        id,
        first_name,
        last_name,
        name_prefix="",
        middle_name="",
        name_suffix="",
        nickname="",
        occupation="",
        employer="",
        volunteer_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        donor_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        member_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        date_of_birth=None,
        gender: Literal["F", "M", "U"] | None = None,
    ):
        """
        Update Contact

        Args:
            name_prefix (str):
            first_name (str):
            middle_name (str):
            last_name (str):
            name_suffix (str):
            nickname (str):
            occupation (str):
            employer (str):
            volunteer_status (str): Options are "Prospect", "Active", "Inactive", "None", ""
            donor_status (str): Options are "Prospect", "Active", "Inactive", "None", ""
            member_status (str): Options are "Prospect", "Active", "Inactive", "None", ""
            date_of_birth (str, optional): Format must be yyyy-MM-dd
            gender (str, optional): Options are "F", "M", "U"

        Returns:
            parsons.Table:
                See :ref:`parsons-table` for output options

        """
        payload = {
            "namePrefix": name_prefix,
            "firstName": first_name,
            "middleName": middle_name,
            "lastName": last_name,
            "nameSuffix": name_suffix,
            "nickname": nickname,
            "occupation": occupation,
            "employer": employer,
            "volunteerStatus": volunteer_status,
            "donorStatus": donor_status,
            "memberStatus": member_status,
            "dateOfBirth": date_of_birth,
            "gender": gender,
        }
        res = self._request(f"{self.url_contacts}/{id}", req_type="PUT", post_data=payload)
        if res["code"] == 201:
            return True

    def add_phone(
        self,
        contact_id: int,
        phone_number: str,
        phone_type: Literal["Home", "Work", "Direct", "Mobile", "Fax", "Other"] = "Mobile",
        primary: bool = True,
        extension: str = "",
    ):
        """
        Add a phone number to a contact.

        Args:
            contact_id (int):
            phone_number (str):
            phone_type (str): Options are "Home", "Work", "Direct", "Mobile", "Fax", and "Other". Defaults to "Mobile".
            primary (bool): Whether this is the contact's primary phone number. Defaults to True.
            extension (str): Defaults to "".

        Returns:
            dict
                Response from PDI

        """

        payload = {
            "phoneNumber": phone_number,
            "phoneType": phone_type,
            "isPrimary": primary,
            "extension": extension,
        }

        response = self._request(
            self.url_contacts + f"/{str(contact_id)}/phones",
            req_type="POST",
            post_data=payload,
        )

        return response

    def add_email(self, contact_id: int, email: str, primary: bool = True):
        """
        Add an email address to a contact.

        Args:
            contact_id (int): The ID of the contact.
            email (str): The email address to add.
            primary (bool): Whether this is the contact's primary email.

        Returns:
            dict: Response from PDI

        """

        payload = {"emailAddress": email, "isPrimary": primary}

        response = self._request(
            self.url_contacts + f"/{str(contact_id)}/emails",
            req_type="POST",
            post_data=payload,
        )

        return response

    def delete_contact(self, id: str):
        """
        Delete a Question by id.

        Args:
            id: str
                The Question id

        """
        return self._request(f"{self.url_contacts}/{id}", req_type="DELETE")
