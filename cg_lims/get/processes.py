from typing import List

from genologics.entities import Process


def get_latest_process(processes: List[Process]) -> Process:
    """Assuming processes of the same process type"""
    processes_to_sort = [(process.date_run, process.id, process) for process in processes]
    processes_to_sort.sort()
    return processes_to_sort[-1][2]
