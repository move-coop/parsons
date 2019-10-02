class SurveyQuestions(object):

    def __init__(self, van_connection):

        self.connection = van_connection

    def get_survey_questions(self, statuses=None, name=None,
                             sq_type=None, question=None, cycle=None,
                             page_size=200):
        """
        Get survey questions.

        `Args:`
            statuses: str
                Comma delimited list of statuses of Survey Questions. One or
                more of Active (default), Archived, and Inactive.
            name: str
                Filter to survey questions with names begin with the input
            sq_type: str
                Filter to survey questions of the given type
            question: str
                Filter to survey questions with script questions that
                contain the given input
            cycle: str
                A year in the format YYYY; filters to Survey Questions with
                the given cycle
        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + 'surveyQuestions'

        args = {'statuses': statuses,
                '$top': page_size,
                'name': name,
                'type': sq_type,
                'question': question,
                'cycle': cycle
                }

        return self.connection.request_paginate(url, args=args)

    def get_survey_question(self, survey_question_id):
        """
        Get a survey question

        `Returns:`
            Parsons Table
                See :ref:`parsons-table` for output options.
        """

        url = self.connection.uri + \
            'surveyQuestions/{}'.format(survey_question_id)

        return self.connection.request(url)
