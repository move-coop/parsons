from typing import Literal


class Contacts:
    """A class to access the contacts PDI API endpoint."""

    def __init__(self):
        self.url_contacts = self.base_url + "/contacts"
        super().__init__()

    def get_contacts(
        self,
        email: str = None,
        phone: str = None,
        first_name: str = None,
        last_name: str = None,
        zip_code: str = None,
        search_by_email: bool = False,
        limit: int = None,
    ):
        """
        Get a list of Contacts.

        Args:
            email (str, optional): Str. Defaults to None.
            phone (str, optional): Str. Defaults to None.
            first_name (str, optional): Str. Defaults to None.
            last_name (str, optional): Str. Defaults to None.
            zip_code (str, optional): Str. Defaults to None.
            search_by_email (bool, optional): Whether to search using email address. Defaults to False.
            limit (int, optional): The number of contacts to return. Defaults to None.

        Returns:
            parsons.Table: A Parsons table of all the data.

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
        name_prefix: str = "",
        first_name: str = "",
        last_name: str = "",
        middle_name: str = "",
        name_suffix: str = "",
        nickname: str = "",
        occupation: str = "",
        employer: str = "",
        volunteer_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        donor_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        member_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        date_of_birth: str = None,
        gender: Literal["F", "M", "U"] | None = None,
        email: str = "",
        pdi_id: str = None,
    ):
        """
        Create new contact.

        Args:
            name_prefix (str, optional): Str. Defaults to "".
            first_name (str, optional): Str. Defaults to "".
            last_name (str, optional): Str. Defaults to "".
            middle_name (str, optional): Str. Defaults to "".
            name_suffix (str, optional): Str. Defaults to "".
            nickname (str, optional): Str. Defaults to "".
            occupation (str, optional): Str. Defaults to "".
            employer (str, optional): Str. Defaults to "".
            volunteer_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            donor_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            member_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            date_of_birth (str, optional): Format allowed: yyyy-MM-dd. Defaults to None.
            gender (Literal["F", "M", "U"] | None, optional): Literal["F", "M", "U"], optional.
                Defaults to None.
            email (str, optional): Str. Defaults to "".
            pdi_id (str, optional): Str, optional. Defaults to None.

        Returns:
            parsons.Table: A Parsons table of the contact data.

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
            id (str): The Contact id.

        Returns:
            parsons.Table: A Parsons table of all the data.

        """
        # todo not working quite right
        return self._request(f"{self.url_contacts}/{id}")

    def update_contact(
        self,
        id: str,
        first_name: str,
        last_name: str,
        name_prefix: str = "",
        middle_name: str = "",
        name_suffix: str = "",
        nickname: str = "",
        occupation: str = "",
        employer: str = "",
        volunteer_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        donor_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        member_status: Literal["Prospect", "Active", "Inactive", "None", ""] = "",
        date_of_birth: str = None,
        gender: Literal["F", "M", "U"] = "U",
    ):
        """
        Update Contact.

        Args:
            id (str): Str: pdi_id.
            first_name (str)
            last_name (str)
            name_prefix (str, optional): Str. Defaults to "".
            middle_name (str, optional): Str. Defaults to "".
            name_suffix (str, optional): Str. Defaults to "".
            nickname (str, optional): Str. Defaults to "".
            occupation (str, optional): Str. Defaults to "".
            employer (str, optional): Str. Defaults to "".
            volunteer_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            donor_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            member_status (Literal["Prospect", "Active", "Inactive", "None", ""], optional): Literal["Prospect",
                "Active", "Inactive", "None", ""]. Defaults to "".
            date_of_birth (str, optional): Format allowed: yyyy-MM-dd. Defaults to None.
            gender (Literal["F", "M", "U"], optional): Literal["F", "M", "U"], optional. Defaults to "U".

        Returns:
            parsons.Table: A Parsons table of the contact data.

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
        return None

    def add_phone(
        self,
        contact_id: int,
        phone_number: str,
        phone_type: Literal["Home", "Work", "Direct", "Mobile", "Fax", "Other"] = "Mobile",
        primary: bool = True,
        extension="",
    ):
        """
        Add a phone number to a contact.

        Args:
            contact_id (int): Unique ID of the contact you'd like to apply the phone_number to.
            phone_number (str)
            phone_type (Literal["Home", "Work", "Direct", "Mobile", "Fax", "Other"], optional): Str Options are
                "Home", "Work", "Direct", "Mobile", "Fax", and "Other". Defaults to "Mobile".
            primary (bool, optional): True indicates that this phone number is the contact's primary phone number.
                Defaults to True.
            extension: Str. Defaults to "".

        Returns:
            dict: Response from PDI.

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
            contact_id (int): Unique ID of the contact you'd like to apply the email to.
            email (str)
            primary (bool, optional): True indicates that this email address is the contact's primary email.
                Defaults to True.

        Returns:
            dict: Response from PDI.

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
            id (str): The Question id.

        """
        return self._request(f"{self.url_contacts}/{id}", req_type="DELETE")
