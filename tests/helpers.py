from typing import List
from copy import deepcopy
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

    # Ensure methods:
    # Creating enteties defined by arguments.
    # Appending the new enteties to the given MockLims instance.
    # Returning teh new enteties

    @staticmethod
    def ensure_lims_process(lims: MockLims, data: List[dict]) -> MockProcess:
        """Creating a MockProcess defined by <data>. 
        Appending the new MockProcess to the given MockLims instance.
        If output artifacts are provided in data, 
            Creating MockArtifacts defined by output
            setting parent_process of the artifacts to the new MockProcess.
        Returning the new MockProcess."""

        process_data = deepcopy(data)
        if process_data.get("input_artifact_list"):
            artifacts = Helpers.ensure_lims_artifacts(
                lims, process_data["input_artifact_list"]
            )
            process_data["input_artifact_list"] = artifacts
        if process_data.get("process_type"):
            process_type = MockProcessType(**process_data["process_type"])
            process_data["process_type"] = process_type
        if process_data.get("outputs"):
            artifacts = Helpers.ensure_lims_artifacts(lims, process_data["outputs"])
            process_data["outputs"] = artifacts

        process = MockProcess(**process_data)
        for artifact in process.outputs:
            artifact.parent_process = process

        lims.processes.append(process)
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
