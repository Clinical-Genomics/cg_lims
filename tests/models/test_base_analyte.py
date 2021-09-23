import pytest
from genologics.entities import Process
from pydantic import ValidationError

from cg_lims.exceptions import MissingArtifactError
from tests.conftest import server, ArtifactUDFModel, ProcessUDFModel, MegedUdfModel

from cg_lims.objects import BaseAnalyte


def test_base_analyte(lims):
    # GIVEN: A lims with a sample ACC8074A1 that passed through a step of mater step type 'Some Process Type'
    # and given that the derived sample got the artifact udfs requiered by the ArtifactUDFModel model,
    # and the process got the udfs requiered by the ProcessUDFModel model:
    server("base_analyte")

    # WHEN creating a BaseStep instance with the lims, the sample_id, the process_type and the udf models
    base_analyte = BaseAnalyte(
        lims=lims,
        sample_id="ACC8074A1",
        process_type="Some Process Type",
        artifact_udf_model=ArtifactUDFModel,
        process_udf_model=ProcessUDFModel,
    )

    # THEN the BaseStep instance is created with no errors and can be validated with the MegedUdfModel model with no errors
    merged_udfs_dict = base_analyte.merge_process_and_artifact_udfs()
    merged_udfs = MegedUdfModel(**merged_udfs_dict)

    assert "tjojo"


def test_base_analyte_missing_artifac(lims):
    # GIVEN: A lims with a sample ACC8074A1 that did never passe through a step of mater step type
    # "Some Process Type That The Sample Didnt Pass Through"
    server("base_analyte")

    # WHEN creating a BaseStep instance with the lims, the sample_id, the process_type and some udf models
    # THEN MissingArtifactError is being raised
    with pytest.raises(MissingArtifactError):
        base_analyte = BaseAnalyte(
            lims=lims,
            sample_id="ACC8074A1",
            process_type="Some Process Type That The Sample Didnt Pass Through",
            artifact_udf_model=ArtifactUDFModel,
            process_udf_model=ProcessUDFModel,
        )


def test_base_analyte_optional_missing_artifac(lims):
    # GIVEN: A lims with a sample ACC8074A1 that did never passe through a step of mater step type
    # "Some Process Type That The Sample Didnt Pass Through"
    server("base_analyte")

    # WHEN creating a BaseStep instance with the lims, the sample_id, the process_type and some
    # udf models and the optional_step field set to True

    base_analyte = BaseAnalyte(
        lims=lims,
        sample_id="ACC8074A1",
        process_type="Some Process Type That The Sample Didnt Pass Through",
        artifact_udf_model=ArtifactUDFModel,
        process_udf_model=ProcessUDFModel,
        optional_step=True,
    )

    merged_udfs_dict = base_analyte.merge_process_and_artifact_udfs()

    # THEN the merged udf dict is generated but empty
    assert merged_udfs_dict == {}


def test_base_analyte_missing_artifact_udf(lims):
    # GIVEN: A lims with a sample ACC8074A2 that passed through a step of mater step type 'Some Process Type'
    # but given that the derived sample dont have the artifact udfs requiered by the ArtifactUDFModel model,

    server("base_analyte")

    # WHEN creating a BaseStep instance with the lims, the sample_id, the process_type and the udf models
    # and trying to run base_analyte.merge_process_and_artifact_udfs()
    base_analyte = BaseAnalyte(
        lims=lims,
        sample_id="ACC8074A2",
        process_type="Some Process Type",
        artifact_udf_model=ArtifactUDFModel,
        process_udf_model=ProcessUDFModel,
    )

    # THEN ValidationError is being raised
    with pytest.raises(ValidationError):
        merged_udfs_dict = base_analyte.merge_process_and_artifact_udfs()


def test_base_analyte_missing_process_udf(lims):
    # GIVEN: A lims with a sample ACC8074A2 that passed through a step of mater step type 'Some Process Type'
    # but given that the process dont have the process udfs requiered by the ProcessUDFModel model,

    server("base_analyte")
    process = Process(lims, id="24-225661")
    process.udf.clear()
    process.put()

    # WHEN creating a BaseStep instance with the lims, the sample_id, the process_type and the udf models
    # and trying to run base_analyte.merge_process_and_artifact_udfs()
    base_analyte = BaseAnalyte(
        lims=lims,
        sample_id="ACC8074A2",
        process_type="Some Process Type",
        artifact_udf_model=ArtifactUDFModel,
        process_udf_model=ProcessUDFModel,
    )

    # THEN ValidationError is being raised
    with pytest.raises(ValidationError):
        merged_udfs_dict = base_analyte.merge_process_and_artifact_udfs()
