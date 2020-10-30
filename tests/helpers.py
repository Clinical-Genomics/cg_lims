from typing import List
from copy import deepcopy
import json
from pathlib import Path


from genologics_mock.lims import MockLims
from genologics_mock.entities import (
    MockArtifact,
    MockProcess,
    MockProcessType,
    MockSample,
)


class Helpers:
    """Fixure Help functions to create fixures."""


    @staticmethod
    def read_json(file_path: str, key: str) -> list:
        with open(file_path) as json_file:
            data = json.load(json_file)
        return data[key]

    # Ensure methods: 
    # Creating enteties defined by arguments. 
    # Appending the new enteties to the given MockLims instance.
    # Returning teh new enteties

    @staticmethod
    def ensure_lims_process(
        lims: MockLims,
        process_id: str = "SomeID",
        process_type_name: str = "SomeTypeOfName",
        date_run: str = "2020-01-01",
        output_artifacts: list = [],
        input_artifacts: list = [],
    ) -> MockProcess:
        """Setting up a complete process with input and output artifacts."""

        process_type = MockProcessType(name=process_type_name)
        process = MockProcess(
            pid=process_id, process_type=process_type, date_run=date_run
        )
        process.input_artifact_list = input_artifacts

        lims.processes.append(process)
        lims.process_types.append(process_type)

        for artifact in output_artifacts:
            artifact.parent_process = process
            lims.artifacts.append(artifact)
        return process

    @staticmethod
    def ensure_lims_artifacts(
        lims: MockLims, artifacts_data: List[dict]
    ) -> List[MockArtifact]:
        """Creating MockArtifacts defined by <artifacts_data>. 
        Appending the new MockArtifacts to the given MockLims instance.
        Returning the new MockArtifacts"""

        artifacts = []
        for data in artifacts_data:
            artifact_data = deepcopy(data)
            if artifact_data.get("samples"):
                samples = Helpers.create_samples(artifact_data["samples"])
                artifact_data["samples"] = samples

            if artifact_data.get("parent_process"):
                process = Helpers.ensure_lims_process(
                    **artifact_data.get("parent_process")
                )
                artifact_data["parent_process"] = process
            artifact = MockArtifact(**artifact_data)

            artifacts.append(artifact)
        lims.artifacts.extend(artifacts)
        return artifacts


    # Create methods:
    # Creating and returning enteties defined by arguments. 

    @staticmethod
    def create_samples(samples_data: List[dict] = []) -> List[MockSample]:
        """Create a mock samples"""

        samples = []
        for sample_data in samples_data:
            sample = MockSample(**sample_data)
            samples.append(sample)

        return samples

    @staticmethod
    def create_artifact(samples: list = [], type: str = "") -> MockArtifact:
        """Create a mock artifact"""

        artifact = MockArtifact(samples=samples, type=type)
        return artifact

    @staticmethod
    def create_many_artifacts(
        nr_of_artifacts: int, type: str = ""
    ) -> List[MockArtifact]:
        """Create a list of mock aritfacts"""

        artifacts = []
        for i in range(nr_of_artifacts):
            artifacts.append(MockArtifact(id=i, type=type))

        return artifacts
