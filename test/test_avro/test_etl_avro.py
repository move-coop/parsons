import tempfile
from pathlib import Path

from parsons import Table
from test.test_etl import BaseTableTest


class TestAvroOperations(BaseTableTest):
    """Tests for Avro file operations"""

    def test_to_avro_basic(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test basic functionality
            tbl.to_avro(avro_file)

            # Verify the file exists
            assert Path.exists(avro_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(avro_file)
            assert len(result_tbl) == len(tbl)
            assert sorted(result_tbl.columns) == sorted(tbl.columns)

            # Check data values match
            for i in range(len(tbl)):
                for col in tbl.columns:
                    assert result_tbl[i][col] == tbl[i][col]

    def test_to_avro_with_schema(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

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
            assert len(result_tbl) == len(tbl)
            assert sorted(result_tbl.columns) == sorted(tbl.columns)

    def test_to_avro_different_codecs(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with different compression codecs
            for codec in ["null", "deflate", "bzip2"]:
                test_file = Path(temp_dir) / f"test_{codec}.avro"
                tbl.to_avro(test_file, codec=codec)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)
                assert sorted(result_tbl.columns) == sorted(tbl.columns)

    def test_to_avro_with_compression_level(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with compression level
            codec = "deflate"
            for level in [1, 5, 9]:
                test_file = Path(temp_dir) / f"test_level_{level}.avro"
                tbl.to_avro(test_file, codec=codec, compression_level=level)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)

    def test_to_avro_sample_size(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with different sample sizes for schema inference
            for sample in [1, 5, 10]:
                test_file = Path(temp_dir) / f"test_sample_{sample}.avro"
                tbl.to_avro(test_file, sample=sample)

                # Verify the file exists
                assert Path.exists(test_file)

                # Read it back and verify content
                result_tbl = Table.from_avro(test_file)
                assert len(result_tbl) == len(tbl)

    def test_to_avro_with_avro_args(self):
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as temp_dir:
            avro_file = Path(temp_dir) / "test.avro"

            # Create a test table
            tbl = Table([{"first": "Bob", "last": "Smith"}])

            # Test with additional arguments to fastavro
            tbl.to_avro(
                avro_file,
                sync_interval=16000,  # Custom sync marker interval
                metadata={"created_by": "parsons_test"},
            )

            # Verify the file exists
            assert Path.exists(avro_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(avro_file)
            assert len(result_tbl) == len(tbl)

    def test_to_avro_complex_types(self):
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
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

            test_file = Path(temp_dir) / "test_complex.avro"
            complex_tbl.to_avro(test_file)

            # Verify the file exists
            assert Path.exists(test_file)

            # Read it back and verify content
            result_tbl = Table.from_avro(test_file)
            assert len(result_tbl) == len(complex_tbl)
