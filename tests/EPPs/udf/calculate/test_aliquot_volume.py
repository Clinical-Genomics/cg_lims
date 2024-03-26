import pytest
from cg_lims.EPPs.udf.calculate.aliquot_volume import calculate_volumes
from cg_lims.exceptions import MissingUDFsError
from genologics.entities import Artifact, Process
from genologics.lims import Lims
from tests.conftest import server


@pytest.mark.parametrize(
    "total_volume,concentration,amount,sample_vol,water_vol",
    [
        (50, 10, 200, 20, 30),
        (30, 10, 200, 20, 10),
        (50, 2, 100, 50, 0),
        (30, 2, 10, 5, 25),
    ],
)
def test_calculate_volumes(
    lims: Lims,
    total_volume: float,
    concentration: float,
    amount: float,
    sample_vol: float,
    water_vol: float,
):
    # GIVEN:
    # - A process with the UDF 'Total Volume (ul)' <total_volume>
    # - An artifact with values for the UDFs 'Concentration' <concentration> and 'Amount needed (ul)' <amount>
    server("flat_tests")

    process = Process(lims=lims, id="24-196211")
    process.udf["Total Volume (ul)"] = total_volume
    process.put()

    artifact_1 = Artifact(lims=lims, id="1")
    artifact_1.udf["Concentration"] = concentration
    artifact_1.udf["Amount needed (ng)"] = amount
    artifact_1.put()

    # WHEN calculating the aliquot sample and water volumes
    calculate_volumes(artifacts=[artifact_1], process=process)

    # THEN the correct values are calculated for the artifact UDFs 'Volume H2O (ul)' and 'Sample Volume (ul)'
    assert artifact_1.udf["Sample Volume (ul)"] == sample_vol
    assert artifact_1.udf["Volume H2O (ul)"] == water_vol


@pytest.mark.parametrize(
    "udf_name",
    ["Concentration", "Amount needed (ng)"],
)
def test_calculate_volumes_missing_artifact_udf(lims: Lims, udf_name: str):
    # GIVEN:
    # - A process with the UDF 'Total Volume (ul)' set
    # - An artifact (artifact_1) with values missing for either 'Concentration' or 'Amount needed (ul)'
    # - Another artifact (artifact_2) with all necessary values set

    server("flat_tests")

    process = Process(lims=lims, id="24-196211")
    process.udf["Total Volume (ul)"] = 50
    process.put()

    artifact_1 = Artifact(lims=lims, id="1")
    artifact_1.udf[udf_name] = 100
    artifact_1.put()

    artifact_2 = Artifact(lims=lims, id="2")
    artifact_2.udf["Concentration"] = 10
    artifact_2.udf["Amount needed (ng)"] = 200
    artifact_2.put()

    # WHEN calculating the aliquot sample and water volumes
    # THEN MissingUDFsError is being raised, while also correctly setting the values for artifact_2
    with pytest.raises(MissingUDFsError):
        calculate_volumes(artifacts=[artifact_1, artifact_2], process=process)
    assert artifact_2.udf["Sample Volume (ul)"] == 20
    assert artifact_2.udf["Volume H2O (ul)"] == 30


def test_calculate_volumes_missing_process_udf(lims: Lims):
    # GIVEN:
    # - A process without the UDF 'Total Volume (ul)' set
    # - An artifact with values for the UDFs 'Concentration' and 'Amount needed (ul)' set
    server("flat_tests")

    process = Process(lims=lims, id="24-196211")

    artifact_1 = Artifact(lims=lims, id="1")
    artifact_1.udf["Concentration"] = 10
    artifact_1.udf["Amount needed (ng)"] = 100
    artifact_1.put()

    # WHEN calculating the aliquot sample and water volumes
    # THEN MissingUDFsError is being raised
    with pytest.raises(MissingUDFsError):
        calculate_volumes(artifacts=[artifact_1], process=process)
