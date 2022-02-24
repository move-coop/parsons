class Phones:
    """A class to access the phone contacts PDI API endpoint."""

    def __init__(self):
        universes_endpoint = "/contacts"
        self.url_universes = self.base_url + universes_endpoint
        super().__init__()


    def get_phone_contact(self, id: str):
        
        pass

    def create_phone_contact(self):
        pass

    def update_phone_contact(self):
        pass

    def delete_phone_contact(self):
        pass