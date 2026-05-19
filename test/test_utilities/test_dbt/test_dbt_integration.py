import pytest
from dbt.artifacts.resources.types import NodeType
from dbt.contracts.results import NodeStatus

from parsons.utilities.dbt.models import Manifest


class TestDbtCoreAPICompatibility:
    """Test suite verifying compatibility with dbt-core's internal API."""

    @pytest.mark.parametrize(
        ("obj_type", "attr_name"),
        [
            ("node", "status"),
            ("node", "node"),
            ("node", "adapter_response"),
            ("execution", "results"),
            ("execution", "elapsed_time"),
            ("execution", "metadata"),
        ],
    )
    def test_dbt_core_attribute_presence(
        self, dbt_node_factory, run_execution_result_factory, obj_type, attr_name
    ):
        """Verify that dbt-core objects maintain the attributes Parsons depends on."""
        target = dbt_node_factory() if obj_type == "node" else run_execution_result_factory()
        assert hasattr(target, attr_name), f"{obj_type.capitalize()}Result missing '{attr_name}'"

    @pytest.mark.parametrize(
        ("enum_class", "expected_values"),
        [
            (NodeStatus, ["Success", "Error", "Fail", "Skipped", "Warn"]),
            (NodeType, ["Model", "Test"]),
        ],
    )
    def test_dbt_core_enum_stability(self, enum_class, expected_values):
        """Verify that dbt-core hasn't renamed or removed critical enum members."""
        for val in expected_values:
            assert hasattr(enum_class, val), f"{enum_class.__name__} missing expected member: {val}"


class TestManifestDbtCoreIntegration:
    """Test suite for Manifest wrapper integration with concrete dbt-core objects."""

    def test_manifest_e2e_processing(self, dbt_node_factory, run_execution_result_factory):
        """Verify Manifest extracts and computes data correctly from real dbt-core structures."""
        nodes = [
            dbt_node_factory(status=NodeStatus.Success, bytes_processed=2 * 10**9),
            dbt_node_factory(
                status=NodeStatus.Skipped, name="skipped_model", resource_type=NodeType.Model
            ),
            dbt_node_factory(
                status=NodeStatus.Skipped, name="skipped_test", resource_type=NodeType.Test
            ),
        ]
        dbt_obj = run_execution_result_factory(nodes)
        manifest = Manifest(command="run", run_execution_result=dbt_obj)

        assert manifest.total_gb_processed == 2.0
        assert manifest.summary[NodeStatus.Success] == 1

        assert len(manifest.skips) == 1
        assert manifest.skips[0].node.name == "skipped_model"
        assert manifest.skips[0].node.resource_type == NodeType.Model

    def test_manifest_metadata_proxy(self, run_execution_result_factory):
        """Verify __getattr__ correctly proxies to concrete ManifestMetadata."""
        dbt_obj = run_execution_result_factory()
        manifest = Manifest(command="run", run_execution_result=dbt_obj)

        assert manifest.project_id == "parsons_project"
        assert hasattr(manifest, "generated_at")
