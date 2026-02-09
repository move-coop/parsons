"""NGPVAN Survey Questions Endpoints"""

import logging

from parsons.etl.table import Table

logger = logging.getLogger(__name__)


class SurveyQuestions:
    def __init__(self, van_connection):
        self.connection = van_connection

    def get_survey_questions(
        self, statuses=None, name=None, sq_type=None, question=None, cycle=None
    ):
        """
        Get survey questions.

        Args:
            statuses: List Filter to a list of statuses of survey questions. One or more of ``Active``,
                ``Archived``, and ``Inactive``. Defaults to None.
            name (str, optional): Filter to survey questions with names begin with the input.
                Defaults to None.
            sq_type (str, optional): Filter to survey questions of a given type. Defaults to None.
            question (str, optional): Filter to survey questions with script questions that contain the given input.
                Defaults to None.
            cycle (str, optional): Filter to survey suestions with the given cycle. A year in the format
                "YYYY". Defaults to None.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        if statuses is None:
            statuses = ["Active"]
        params = {
            "statuses": statuses,
            "$top": self.page_size,
            "name": name,
            "type": sq_type,
            "question": question,
            "cycle": cycle,
        }

        tbl = Table(self.connection.get_request("surveyQuestions", params=params))
        logger.info(f"Found {tbl.num_rows} survey questions.")
        return tbl

    def get_survey_question(self, survey_question_id):
        """
        Get a survey question.

        Args:
            survey_question_id (int): The survey question id.

        Returns:
            Table: See :ref:`parsons-table` for output options.

        """
        r = self.connection.get_request(f"surveyQuestions/{survey_question_id}")
        logger.info(f"Found survey question {survey_question_id}.")
        return r

    def apply_survey_response(
        self,
        id,
        survey_question_id,
        survey_response_id,
        id_type="vanid",
        result_code_id=None,
        contact_type_id=None,
        input_type_id=None,
        date_canvassed=None,
    ):
        """
        Apply a single survey response to a person.

        Args:
            id (str): A valid person id.
            survey_question_id (int): A valid survey question id.
            survey_response_id (int): A valid survey response id.
            id_type (str, optional): A known person identifier type available on this VAN instance such as
                ``dwid``. Defaults to "vanid".
            result_code_id (int, optional): Specifies the result code of the response. If not included,responses
                must be specified. Conversely, if responses are specified, result_code_id must be null.
                Valid ids can be found by using the
                :meth:`get_canvass_responses_result_codes`. Defaults to None.
            contact_type_id (int, optional): A valid contact type id. Defaults to None.
            input_type_id (int, optional): Defaults to None.
            date_canvassed (str, optional): ISO 8601 formatted date. Defaults to None.

        """
        response = {
            "surveyQuestionId": survey_question_id,
            "surveyResponseId": survey_response_id,
            "type": "surveyResponse",
        }

        logger.info(f"Applying survey question {survey_question_id} to {id_type} {id}")
        self.apply_response(
            id,
            response,
            id_type,
            result_code_id=result_code_id,
            contact_type_id=contact_type_id,
            input_type_id=input_type_id,
            date_canvassed=date_canvassed,
        )
