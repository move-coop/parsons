import logging
import json

logger = logging.getLogger(__name__)

class Contacts():
    """A PDI class for interacting with PDI Campaign Contacts"""

    def __init__(self):
        self.contacts_url = self.base_url + '/contacts'

        super().__init__()

    def add_phone(self, contact_id: int, phone_number: str, phone_type='Mobile', primary=True,
                  extension=None):
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
            'phoneNumber': phone_number,
            'phoneType': phone_type,
            'isPrimary': primary
        }

        if extension:
            payload['extension'] = extension

        response = self._request(self.contacts_url + f'/{str(contact_id)}/phones', req_type='POST',
                                 post_data=payload)

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

        payload = {
            'emailAddress': email,
            'isPrimary': primary
        }

        response = self._request(self.contacts_url + f'/{str(contact_id)}/emails', req_type='POST',
                                 post_data=payload)

        return response

    def create_contact(self, given_name: str, family_name: str, pdi_id=None, phone_number=None,
                       phone_type='Mobile', primary_phone=True, email=None, primary_email=True,
                       name_prefix='', name_suffix='', nickname='', middle_name='', occupation='',
                       employer='', volunteer_status='', donor_status='', member_status='',
                       dob=None, gender=None):

        """Create a new contacts in your PDI campaign

        `Args:`
            given_name: str
                Contact's first name
            family_name: str
                Contact's last name
            pdi_id: str
                The PDI Voter ID associated with this contact
            phone_number: str
            phone_type: str
                Options are `Home`, `Work`, `Direct`, `Mobile`, `Fax`, and `Other. Defaults to
                `Mobile`
            primary_phone: bool
                Indicates whether this is the contacts primary phone number
            email: str
            primary_email: str
                Indicates whether this is the contacts primary email address
            name_prefix: str
            name_suffix: str
            nickname: str
            middle_name: str
            occupation: str
            employer: str
            volunteer_status: str
                Options are: `Prospect`, `Active`, `Inactive`, `None`. Defaults to an empty string
            donor_status: str
                Options are: `Prospect`, `Active`, `Inactive`, `None`. Defaults to an empty string
            member_status: str
                Options are: `Prospect`, `Active`, `Inactive`, `None`. Defaults to an empty string
            dob: str
                Date of birth. Should be formatted as yyy-MM-dd
            gender: str
                Options are `F`, `M`, `U`

        `Returns:`
            A nested dictionary with keys 'contact', 'phone', 'email'.
        """

        contact_payload = {
            "namePrefix": name_prefix,
            "firstName": given_name,
            "middleName": middle_name,
            "lastName": family_name,
            "nameSuffix": name_suffix,
            "nickname": nickname,
            "occupation": occupation,
            "employer": employer,
            "volunteerStatus": volunteer_status,
            "donorStatus": donor_status,
            "memberStatus": member_status,
        }

        if pdi_id:
            contact_payload['pdiId'] = pdi_id
        if dob:
            contact_payload['dateOfBirth'] = dob
        if gender:
            contact_payload['gender'] = gender

        contact_response = self._request(self.contacts_url, req_type='POST',
                                         post_payload=contact_payload)

        # Start building the final dictionary to return
        final_dict = {
            'contact': contact_response
        }

        contact_id = contact_response['id']

        # Add phone number to contact
        if phone_number:

            phone_payload = {
                'phoneNumber': phone_number,
                'phoneType': phone_type,
                'isPrimary': primary_phone
            }

            try:
                phone_response = self._request(self.contacts_url + f'/{contact_id}/phones',
                                               req_type='POST', post_data=phone_payload)

            except Exception as e:
                raise Exception(f'''
Contact {contact_id} was created but there was an error assigning the phone number:
Contact:{contact_payload}
Error: {str(e)}
''')

            final_dict['phone'] = phone_response

        if email:
            email_payload = {
                'emailAddress': email,
                'isPrimary': primary_email
            }

            try:
                email_response = self._request(self.contacts_url + f'/{contact_id}/emails',
                                               req_type='POST', post_data=email_payload)
            except Exception as e:
                raise Exception(f'''
Contact {contact_id} was created but there was an error assigning the phone number:
Contact:{contact_payload}
Error: {str(e)}
''')
            final_dict['email'] = email_response

        return final_dict
    