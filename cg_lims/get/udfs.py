from genologics.lims import Lims
from genologics.entities import Sample, Artifact
from cg_lims.constants import MASTER_STEPS_UDFS
from cg_lims.get.artifacts import get_latest_artifact, get_latest_input_artifact
from cg_lims.utils.date_utils import str_to_datetime
import operator
import logging

LOG = logging.getLogger(__name__)


def get_concentration_and_nr_defrosts(
    application_tag: str, lims_id: str, lims: Lims
) -> dict:
    """Get concentration and nr of defrosts for wgs illumina PCR-free samples.
    Find the latest artifact that passed through a concentration_step and get its 
    concentration_udf. --> concentration
    Go back in history to the latest lot_nr_step and get the lot_nr_udf from that step. --> lotnr
    Find all steps where the lot_nr was used. --> all_defrosts
    Pick out those steps that were performed before our lot_nr_step --> defrosts_before_this_process
    Count defrosts_before_this_process. --> nr_defrosts"""

    if not application_tag:
        return {}

    if (
        not application_tag[0:6]
        in MASTER_STEPS_UDFS["concentration_and_nr_defrosts"]["apptags"]
    ):
        return {}

    lot_nr_steps = MASTER_STEPS_UDFS["concentration_and_nr_defrosts"]["lot_nr_step"]
    concentration_step = MASTER_STEPS_UDFS["concentration_and_nr_defrosts"][
        "concentration_step"
    ]
    lot_nr_udf = MASTER_STEPS_UDFS["concentration_and_nr_defrosts"]["lot_nr_udf"]
    concentration_udf = MASTER_STEPS_UDFS["concentration_and_nr_defrosts"][
        "concentration_udf"
    ]

    return_dict = {}
    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)
    if concentration_art:
        concentration = concentration_art.udf.get(concentration_udf)
        lotnr = concentration_art.parent_process.udf.get(lot_nr_udf)
        this_date = str_to_datetime(concentration_art.parent_process.date_run)

        # Ignore if multiple lot numbers:
        if lotnr and len(lotnr.split(",")) == 1 and len(lotnr.split(" ")) == 1:
            all_defrosts = []
            for step in lot_nr_steps:
                all_defrosts += lims.get_processes(type=step, udf={lot_nr_udf: lotnr})
            defrosts_before_this_process = []

            # Find the dates for all processes where the lotnr was used (all_defrosts),
            # and pick the once before or equal to this_date
            for defrost in all_defrosts:
                if defrost.date_run and str_to_datetime(defrost.date_run) <= this_date:
                    defrosts_before_this_process.append(defrost)

            nr_defrosts = len(defrosts_before_this_process)

            return_dict = {
                "nr_defrosts": nr_defrosts,
                "concentration": concentration,
                "lotnr": lotnr,
                "concentration_date": this_date,
            }

    return return_dict


def get_final_conc_and_amount_dna(
    application_tag: str, lims_id: str, lims: Lims
) -> dict:
    """Find the latest artifact that passed through a concentration_step and get its 
    concentration. Then go back in history to the latest amount_step and get the amount."""

    if not application_tag:
        return {}

    if (
        not application_tag[0:6]
        in MASTER_STEPS_UDFS["final_conc_and_amount_dna"]["apptags"]
    ):
        return {}

    return_dict = {}
    amount_udf = MASTER_STEPS_UDFS["final_conc_and_amount_dna"]["amount_udf"]
    concentration_udf = MASTER_STEPS_UDFS["final_conc_and_amount_dna"][
        "concentration_udf"
    ]
    concentration_step = MASTER_STEPS_UDFS["final_conc_and_amount_dna"][
        "concentration_step"
    ]
    amount_step = MASTER_STEPS_UDFS["final_conc_and_amount_dna"]["amount_step"]

    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)

    if concentration_art:
        amount_art = None
        step = concentration_art.parent_process
        # Go back in history untill we get to an output artifact from the amount_step
        while step and not amount_art:
            art = get_latest_input_artifact(step.type.name, lims_id, lims)
            processes = [
                p.type.name for p in lims.get_processes(inputartifactlimsid=art.id)
            ]
            for step in amount_step:
                if step in processes:
                    amount_art = art
                    break
            step = art.parent_process

        amount = amount_art.udf.get(amount_udf) if amount_art else None
        concentration = concentration_art.udf.get(concentration_udf)
        return_dict = {"amount": amount, "concentration": concentration}

    return return_dict


def get_microbial_library_concentration(
    application_tag: str, lims_id: str, lims: Lims
) -> float:
    """Check only samples with mictobial application tag.
    Get concentration_udf from concentration_step."""

    if not application_tag:
        return {}

    if (
        not application_tag[3:5]
        == MASTER_STEPS_UDFS["microbial_library_concentration"]["apptags"]
    ):
        return None

    concentration_step = MASTER_STEPS_UDFS["microbial_library_concentration"][
        "concentration_step"
    ]
    concentration_udf = MASTER_STEPS_UDFS["microbial_library_concentration"][
        "concentration_udf"
    ]

    concentration_art = get_latest_input_artifact(concentration_step, lims_id, lims)

    if concentration_art:
        return concentration_art.udf.get(concentration_udf)
    else:
        return None


def get_library_size(
    app_tag: str, lims_id: str, lims: Lims, workflow: str, hyb_type: str
) -> int:
    """Getting the udf Size (bp) that in fact is set on the aggregate qc librar validation step.
    But since the same qc protocol is used both for pre-hyb and post-hyb, there is no way to 
    distiguish from within the aggregation step, wether it is pre-hyb or post-hyb qc. 
    Because of that, we instead search for
        TWIST: the input artifact of the output artifacts of the steps that are AFTER the 
        aggregations step:
            For pre hyb: MASTER_STEPS_UDFS['pre_hyb']['TWIST'].get('size_step')
            For post hyb: MASTER_STEPS_UDFS['post_hyb']['TWIST'].get('size_step')
        SureSelect: the output artifacts of the steps that are BEFORE the aggregations step:
            For pre hyb: MASTER_STEPS_UDFS['pre_hyb']['SureSelect'].get('size_step')
            For post hyb: MASTER_STEPS_UDFS['post_hyb']['SureSelect'].get('size_step')"""

    size_steps = MASTER_STEPS_UDFS[hyb_type][workflow].get("size_step")

    if workflow == "TWIST":
        stage_udfs = MASTER_STEPS_UDFS[hyb_type][workflow].get("stage_udf")
        out_art = get_latest_artifact(lims, lims_id, size_steps)
        if out_art:
            sample = Sample(lims, id=lims_id)
            for inart in out_art.parent_process.all_inputs():
                stage = inart.workflow_stages[0].id
                if sample in inart.samples and stage in stage_udfs:
                    size_udf = stage_udfs[stage]
                    return inart.udf.get(size_udf)
    elif workflow == "SureSelect":
        if (
            not app_tag
            or app_tag[0:3] not in MASTER_STEPS_UDFS[hyb_type][workflow]["apptags"]
        ):
            return None
        size_art = get_latest_artifact(lims, lims_id, size_steps)
        if size_art:
            size_udf = MASTER_STEPS_UDFS[hyb_type][workflow].get("size_udf")
            return size_art.udf.get(size_udf)

    return None
