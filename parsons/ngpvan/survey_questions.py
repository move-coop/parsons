"""NGPVAN Survey Questions Endpoints"""
from parsons.etl.table import Table
import logging

logger = logging.getLogger(__name__)


class SurveyQuestions(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_survey_questions(self, statuses=['Active'], name=None, sq_type=None, question=None,
                             cycle=None):
        """
        Get survey questions.

        `Args:`
            statuses: str
                Filter to a list of statuses of survey questions. One or more of ``Active``,
                ``Archived``, and ``Inactive``.
            name: str
                Filter to survey questions with names begin with the input.
            type: str
                Filter to survey questions of a given type.
            question: str
                Filter to survey questions with script questions that contain the given input.
            cycle: str
                Filter to survey suestions with the given cycle. A year in the format "YYYY".
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        params = {'statuses': statuses,
                  '$top': self.page_size,
                  'name': name,
                  'type': sq_type,
                  'question': question,
                  'cycle': cycle}

        tbl = Table(self.connection.get_request('surveyQuestions', params=params))
        logger.info(f'Found {tbl.num_rows} survey questions.')
        return tbl

    def get_survey_question(self, survey_question_id):
        """
        Get a survey question.

        `Args:`
            survey_question_id: int
                The survey question id.
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        r = self.connection.get_request(f'surveyQuestions/{survey_question_id}')
        logger.info(f'Found survey question {survey_question_id}.')
        return r
