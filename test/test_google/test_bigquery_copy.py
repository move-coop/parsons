# testing bigquery copy method of google class

from unittest import TestCase
from unittest.mock import Mock
import logging
from testfixtures import log_capture
from parsons import GoogleBigQuery


class TestGoogleBigQuery(TestCase):
    def setUp(self):
        # mock the GoogleBigQuery class
        self.bq = Mock(spec=GoogleBigQuery)

        # define inputs to copy method
        self.source_project = ("project1",)
        self.source_dataset = ("dataset1",)
        self.source_table = ("table1",)
        self.destination_project = ("project2",)
        self.destination_dataset = ("dataset2",)
        self.destination_table = ("table2",)
        self.if_dataset_not_exists = ("fail",)
        self.if_table_exists = "fail"

    def tearDown(self):
        pass

    def test_copy_called_once_with(self):
        self.bq.copy_between_projects(
            source_project=self.source_project,
            source_dataset=self.destination_dataset,
            source_table=self.source_table,
            destination_project=self.destination_project,
            destination_dataset=self.destination_dataset,
            destination_table=self.destination_table,
            if_dataset_not_exists=self.if_dataset_not_exists,
            if_table_exists=self.if_table_exists,
        )
        self.bq.copy_between_projects.assert_called_once_with(
            source_project=self.source_project,
            source_dataset=self.destination_dataset,
            source_table=self.source_table,
            destination_project=self.destination_project,
            destination_dataset=self.destination_dataset,
            destination_table=self.destination_table,
            if_dataset_not_exists=self.if_dataset_not_exists,
            if_table_exists=self.if_table_exists,
        )

    @log_capture()
    def test_logger_fail_on_dataset_does_not_exist(self, capture):
        # create and set up logger
        logger = logging.getLogger()
        logger.error(
            "Dataset {0} does not exist and if_dataset_not_exists set to {1}".format(
                self.destination_dataset, self.if_dataset_not_exists
            )
        )

        # call the method to generate log message
        self.bq.copy_between_projects(
            source_project=self.source_project,
            source_dataset=self.destination_dataset,
            source_table=self.source_table,
            destination_project=self.destination_project,
            destination_dataset=self.destination_dataset,
            destination_table=self.destination_table,
            if_dataset_not_exists=self.if_dataset_not_exists,
            if_table_exists=self.if_table_exists,
        )

        # check that the log message was generated correctly
        capture.check(
            (
                "root",
                "ERROR",
                "Dataset {0} does not exist and if_dataset_not_exists set to {1}".format(
                    self.destination_dataset, self.if_dataset_not_exists
                ),
            )
        )

    @log_capture()
    def test_logger_fail_on_table_exists(self, capture):
        # create and set up logger
        logger = logging.getLogger()

        ## now test with table copy error
        logger.error(
            "BigQuery copy failed, Table {0} exists and if_table_exists set to {1}".format(
                self.destination_table, self.if_table_exists
            )
        )

        # call the method to generate log message
        self.bq.copy_between_projects(
            source_project=self.source_project,
            source_dataset=self.destination_dataset,
            source_table=self.source_table,
            destination_project=self.destination_project,
            destination_dataset=self.destination_dataset,
            destination_table=self.destination_table,
            if_dataset_not_exists=self.if_dataset_not_exists,
            if_table_exists=self.if_table_exists,
        )

        # check that the log message was generated correctly
        capture.check(
            (
                "root",
                "ERROR",
                "BigQuery copy failed, Table {0} exists and if_table_exists set to {1}".format(
                    self.destination_table, self.if_table_exists
                ),
            )
        )
