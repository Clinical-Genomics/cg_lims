from genologics.entities import Process

from cg_lims.EPPs.arnold.flow_cell import build_flow_cell_document
from cg_lims.get.artifacts import get_output_artifacts
from cg_lims.models.arnold.flow_cell import FlowCell

from tests.conftest import server


def test_load_flowcell(lims, flow_cell_fixture):
    # GIVEN: A lims with a process: "24-314318" (NovaSeq Run).

    server("novaseq_run")

    process = Process(lims=lims, id="24-314318")
    lanes = get_output_artifacts(
        process=process, output_generation_type=["PerInput"], lims=lims, output_type="ResultFile"
    )

    # WHEN running build_flow_cell_document
    flow_cell: FlowCell = build_flow_cell_document(process=process, lanes=lanes)

    # THEN assert the flow_cell document with its lanes was created.
    flow_cell_dict = flow_cell.dict()
    lanes = flow_cell_dict.pop("lanes")
    fixture_lanes = flow_cell_fixture.pop("lanes")
    for lane in fixture_lanes:
        assert lane in lanes
    assert flow_cell_dict == flow_cell_fixture
