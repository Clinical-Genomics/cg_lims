from typing import List


from genologics_mock.lims import MockLims
from genologics_mock.entities import (
    MockArtifact,
    MockProcess,
    MockProcessType,
    MockSample,
)


class Helpers:
    @staticmethod
    def ensure_lims_process(
        lims: MockLims,
        process_id: str = "SomeID",
        process_type_name: str = "SomeTypeOfName",
        date_run: str = "2020-01-01",
        output_artifacts: list = [],
        input_artifacts: list = [],
    ):
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

    @staticmethod
    def create_artifact(samples: list=[], type: str='')-> MockArtifact:
        """Create a mock artifact"""

        artifact = MockArtifact(samples=samples, type=type)
        return artifact

    @staticmethod
    def create_many_artifacts(nr_of_artifacts:int, type: str='')-> List[MockArtifact]:
        """Create a list of mock aritfacts"""
        
        artifacts = []
        for i in range(nr_of_artifacts):
            artifacts.append(MockArtifact(id=i, type=type))

        return artifacts
