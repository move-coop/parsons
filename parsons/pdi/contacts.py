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
        `Args:`
            email: str, email address
            phone: str, phone number
            first_name: str, first name
            last_name: str, last name
            zip code: str, zip code
            search_by_email: bool, whether to search using email address
            limit: int
                The number of contacts to return.
        `Returns:`
            parsons.Table
                A Parsons table of all the data.
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
        volunteer_status="",
        donor_status="",
        member_status="",
        date_of_birth=None,
        gender=None,
        pdi_id=None,
    ):
        """
        Create new contact
        `Args:`
            pdiId (string, optional): The pdi identifier. pdiId field is ignored when updating. ,
            namePrefix (string): The name prefix.
            firstName (string): The first name.
            middleName (string): The middle name.
            lastName (string): The last name.
            nameSuffix (string): The name suffix.
            nickname (string): The nickname.
            occupation (string): The occupation.
            employer (string): The employer.
            volunteerStatus (string): The volunteer status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            donorStatus (string): The donor status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            memberStatus (string): The member status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            dateOfBirth (string, optional): The date of birth.
            Format allowed: yyyy-MM-dd ,
            gender (string, optional): The gender.
            Options are: "F", "M", "U"

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
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
            "pdiId": pdi_id,
        }
        return self._request(self.url_contacts, req_type="POST", post_data=payload)

    def get_contact(self, id: str):
        """
        Get a Contact by id.

        `Args:`
            id: str
                The Contact id
        `Returns:`
            parsons.Table
                A Parsons table of all the data.
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
        volunteer_status="",
        donor_status="",
        member_status="",
        date_of_birth=None,
        gender="U",
    ):
        """
        Update Contact
        `Args:`
            namePrefix (string): The name prefix.
            firstName (string): The first name.
            middleName (string): The middle name.
            lastName (string): The last name.
            nameSuffix (string): The name suffix.
            nickname (string): The nickname.
            occupation (string): The occupation.
            employer (string): The employer.
            volunteerStatus (string): The volunteer status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            donorStatus (string): The donor status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            memberStatus (string): The member status.
            Options are: "Prospect", "Active", "Inactive", "None", "" ,
            dateOfBirth (string, optional): The date of birth.
            Format allowed: yyyy-MM-dd ,
            gender (string, optional): The gender.
            Options are: "F", "M", "U"

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
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
        phone_type="Mobile",
        primary=True,
        extension=None,
    ):
        """Add a phone number to a contact
        `Args:`
            contact_id: int
                Unique ID of the contact you'd like to apply the phone_number to
            phone_number: str
            phone_type: str
                Options are `Home`, `Work`, `Direct`, `Mobile`, `Fax`, and `Other. Defaults to
                `Mobile`
            primary: bool
                True indicates that this phone number is the contact's primary phone number
            extension: str
        `Returns:`
            dict
                Response from PDI
        """

        payload = {
            "phoneNumber": phone_number,
            "phoneType": phone_type,
            "isPrimary": primary,
        }

        if extension:
            payload["extension"] = extension

        response = self._request(
            self.url_contacts + f"/{str(contact_id)}/phones",
            req_type="POST",
            post_data=payload,
        )

        return response

    def add_email(self, contact_id: int, email: str, primary=True):
        """Add an email address to a contact
        `Args:`
            contact_id: int
                Unique ID of the contact you'd like to apply the email to
            email: str
            primary: bool
                True indicates that this email address is the contact's primary email
        `Returns:`
            dict
                Response from PDI
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
        `Args:`
            id: str
                The Question id
        """
        return self._request(f"{self.url_contacts}/{id}", req_type="DELETE")
