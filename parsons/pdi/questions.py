class Questions:
    """A class to access the Questions PDI API endpoint."""

    def __init__(self):
        questions_endpoint = "/questions"
        self.url_questions = self.base_url + questions_endpoint

        super().__init__()

    def get_questions(self, limit=None):
        """Get a list of Questions.

        `Args:`
            limit: int
                Specify limit to return.

        `Returns:`
            parsons.Table
                A Parsons table of all the data.
        """

        return self._request(self.url_questions, limit=limit)
