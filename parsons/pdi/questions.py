class Questions:
    """A class to access the Questions PDI API endpoint."""

    def __init__(self):
        questions_endpoint = "/questions"
        self.url_questions = self.base_url + questions_endpoint

        super().__init__()

    def get_questions(self, limit=None):
        """
        Get a list of Questions.

        Args:
            limit: int
                Specify limit to return.

        Returns:
            parsons.Table

        """
        return self._request(self.url_questions, limit=limit)

    def get_question(self, id: str):
        """
        Get a Question by id.

        Args:
            id: str
                The Question id

        Returns:
            parsons.Table

        """
        return self._request(f"{self.url_questions}/{id}")

    def create_question(
        self,
        question: str,
        type: str,
        category: str,
        answer_options: list,
        question_label: str | None = None,
        question_description: str | None = None,
        candidate_issue_id: str | None = None,
        default: bool = True,
        *args,
    ):
        """
        Create a new question.

        Args:
            question (str):
            type (str):
            category (str):
            answer_options (list[dict[str, str]):

                .. code-block:: python

                    [
                        {
                        "id": "string",
                        "flagId": "string",
                        "displayDescription": "string",
                        "displayCode": "string"
                        }
                    ]

            question_label (str, optional):
            question_description (str, optional):
            candidate_issue_id (str, optional):
            default (bool, optional): Defaults to `True`

        """
        payload = {
            "question": question,
            "questionLabel": question_label,
            "questionDescription": question_description,
            "type": type,
            "category": category,
            "candidateIssueId": candidate_issue_id,
            "default": default,
            "answerOptions": answer_options,
        }
        return self._request(self.locations_url, req_type="POST", post_data=payload)

    def delete_question(self, id: str):
        return self._request(f"{self.url_questions}/{id}", req_type="DELETE")
