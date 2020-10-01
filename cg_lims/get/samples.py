from genologics.entities import Process, Sample
from typing import List



def get_process_samples(process: Process) -> List[Sample]:
    """Get all samples in a process"""

    all_samples = []
    for art in process.all_inputs():
        all_samples += art.samples

    return list(set(all_samples))
