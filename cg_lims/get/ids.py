from typing import List


def unique_list_of_ids(entity_list: list) -> List[str]:
    """Arg: entity_list: list of any type of genologics entity.
    Retruning unique list of entity ids."""

    return list(set([e.id for e in entity_list]))
