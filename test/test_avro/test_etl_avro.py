"""Tests for Avro file operations"""

from pathlib import Path

import pytest

from parsons import Table
from test.conftest import assert_matching_tables


class TestAvroOperations:
    """Tests for Avro file read/write operations"""

    def test_to_from_avro_basic(self, tbl, tmp_path: Path):
        avro_file = tmp_path / "test.avro"

        # Test basic functionality
        tbl.to_avro(avro_file)

        # Verify the file exists
        assert avro_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(avro_file)
        assert_matching_tables(tbl, result_tbl)

    def test_to_avro_with_schema(self, tbl, tmp_path: Path):
        avro_file = tmp_path / "test.avro"

        # Test with explicit schema
        schema = {
            "doc": "Some people records.",
            "name": "People",
            "namespace": "test",
            "type": "record",
            "fields": [
                {"name": "first", "type": "string"},
                {"name": "last", "type": "string"},
            ],
        }

        tbl.to_avro(avro_file, schema=schema)

        # Read it back and verify content
        result_tbl = Table.from_avro(avro_file)
        assert_matching_tables(tbl, result_tbl)

    @pytest.mark.parametrize(
        "codec",
        ["null", "deflate", "bzip2"],
        ids=["no_compression", "deflate_compression", "bzip2_compression"],
    )
    def test_to_avro_different_codecs(self, tbl, tmp_path, codec):
        test_file = tmp_path / f"test_{codec}.avro"
        tbl.to_avro(test_file, codec=codec)

        # Verify the file exists
        assert test_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(test_file)
        assert_matching_tables(tbl, result_tbl)

    @pytest.mark.parametrize(
        "compression_level",
        [1, 5, 9],
        ids=["level_1", "level_5", "level_9"],
    )
    def test_to_avro_with_compression_level(self, tbl, tmp_path, compression_level):
        test_file = tmp_path / f"test_level_{compression_level}.avro"
        tbl.to_avro(test_file, codec="deflate", compression_level=compression_level)

        # Verify the file exists
        assert test_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(test_file)
        assert_matching_tables(tbl, result_tbl)

    @pytest.mark.parametrize(
        "sample_size",
        [1, 5, 10],
        ids=["sample_1", "sample_5", "sample_10"],
    )
    def test_to_avro_sample_size(self, tbl, tmp_path, sample_size):
        test_file = tmp_path / f"test_sample_{sample_size}.avro"
        tbl.to_avro(test_file, sample=sample_size)

        # Verify the file exists
        assert test_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(test_file)
        assert_matching_tables(tbl, result_tbl)

    def test_to_avro_with_avro_args(self, tbl, tmp_path: Path):
        avro_file = tmp_path / "test.avro"

        # Test with additional arguments to fastavro
        tbl.to_avro(
            avro_file,
            sync_interval=16000,  # Custom sync marker interval
            metadata={"created_by": "parsons_test"},
        )

        # Verify the file exists
        assert avro_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(avro_file)
        assert_matching_tables(tbl, result_tbl)

    def test_to_avro_complex_types(self, tmp_path: Path):
        # Test with more complex data types
        complex_data = [
            {
                "name": "Bob",
                "tags": ["tag1", "tag2"],
                "metadata": {"city": "NYC", "state": "NY"},
            },
            {"name": "Jim", "tags": ["tag3"], "metadata": {"city": "LA", "state": "CA"}},
        ]
        complex_tbl = Table(complex_data)

        test_file = tmp_path / "test_complex.avro"
        complex_tbl.to_avro(test_file)

        # Verify the file exists
        assert test_file.exists()

        # Read it back and verify content
        result_tbl = Table.from_avro(test_file)
        assert_matching_tables(complex_tbl, result_tbl)
