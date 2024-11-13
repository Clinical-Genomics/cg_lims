import click


def config(help: str = "config file for lims connection.") -> click.option:
    return click.option("-c", "--config", required=True, help=help)


def process(help: str = "Lims id for current Process.") -> click.option:
    return click.option("-p", "--process", required=True, help=help)


def log(
    help: str = "Path to log file.",
) -> click.option:
    return click.option("-l", "--log", required=True, help=help)


def workflow_id(help: str = "Workflow id.") -> click.option:
    return click.option("-w", "--workflow-id", required=True, help=help)


def stage_id(help: str = "Stage id.") -> click.option:
    return click.option("-s", "--stage-id", required=True, help=help)


def udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-u", "--udf", required=False, help=help)


def buffer_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-b", "--buffer-udf", required=True, help=help)


def volume_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-v", "--volume-udf", required=True, help=help)


def well_field(
    help: str = "Well field in file",
) -> click.option:
    return click.option("-wf", "--well-field", required=True, help=help)


def value_field(
    help: str = "Value field in file",
) -> click.option:
    return click.option("-vf", "--value-field", required=True, help=help)


def sample_qc_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-qc", "--sample-qc-udf", default="", required=False, help=help)


def artifact_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-audf", "--artifact-udf", required=True, help=help)


def sample_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-sudf", "--sample-udf", required=True, help=help)


def process_udf(
    help: str = "UDF name",
) -> click.option:
    return click.option("-pudf", "--process-udf", required=True, help=help)


def process_udf_optional(
    help: str = "Process UDF name. Not required to specify.",
) -> click.option:
    return click.option("-pudf", "--process-udf", required=False, help=help)


def file_placeholder(
    help: str = "File.",
) -> click.option:
    return click.option("-f", "--file", required=False, help=help)


def file_placeholders(
    help: str = "File placeholder option used when multiple are possible.",
) -> click.option:
    return click.option("-f", "--files", required=True, multiple=True, help=help)


def samples_file(help: str = "Txt file with sample ids") -> click.option:
    return click.option(
        "--samples-file",
        required=False,
        help=help,
    )


def local_file(help="local file path for debug purposes.") -> click.option:
    return click.option("-lf", "--local_file", required=False, help=help)


def input(
    help: str = "Use this flag if you run the script from a QC step.",
) -> click.option:
    return click.option(
        "-i",
        "--input",
        default=False,
        is_flag=True,
        help=help,
    )


def qc_flag(
    help: str = "Use this if you want to copy cq_flag.",
) -> click.option:
    return click.option(
        "-qc",
        "--qc-flag",
        default=False,
        is_flag=True,
        help=help,
    )


def sample_artifact(
    help: str = "Use this flag if you want to get the sample artifact (the very first artifact that is created when a "
    "sample is put into the first step in workflow.).",
) -> click.option:
    return click.option(
        "-sa",
        "--sample-artifact",
        default=False,
        is_flag=True,
        help=help,
    )


def original_well(
    help: str = "Use this flag if you want original well instead of source well.",
) -> click.option:
    return click.option(
        "-o",
        "--original-well",
        default=False,
        is_flag=True,
        help=help,
    )


def measurement(
    help: str = "Use this flag if you run the script from a QC step and want "
    "to get the measurement artifacts.",
) -> click.option:
    return click.option(
        "-m",
        "--measurement",
        default=False,
        is_flag=True,
        help=help,
    )


def process_types(help: str = "Process type name.") -> click.option:
    return click.option(
        "-n",
        "--process-types",
        required=False,
        multiple=True,
        help=help,
    )


def artifact_udfs(help: str = "Artifact udfs.") -> click.option:
    return click.option(
        "-au",
        "--artifact-udfs",
        required=False,
        multiple=True,
        help=help,
    )


def concentration_replicates(help: str = "Udf name for concentration replicates.") -> click.option:
    return click.option(
        "-cr",
        "--concentration-udf",
        required=True,
        multiple=True,
        help=help,
    )


def source_artifact_udfs(help: str = "Artifact udfs.") -> click.option:
    return click.option(
        "-sau",
        "--source-artifact-udfs",
        required=False,
        multiple=True,
        help=help,
    )


def sample_udfs(help: str = "Sample udfs.") -> click.option:
    return click.option(
        "-su",
        "--sample-udfs",
        required=False,
        multiple=True,
        help=help,
    )


def pool_udfs(help: str = "Pool udfs.") -> click.option:
    return click.option(
        "-pu",
        "--pool-udfs",
        required=False,
        multiple=True,
        help=help,
    )


def process_udfs(help: str = "Process udfs.") -> click.option:
    return click.option(
        "-pru",
        "--process-udfs",
        required=False,
        multiple=True,
        help=help,
    )


def pooling_step(
    help: str = "True if run from a pooling step",
) -> click.option:
    return click.option(
        "-p",
        "--pooling-step",
        default=False,
        is_flag=True,
        help=help,
    )


def size_udf(help: str = "Udf for fetching size.") -> click.option:
    return click.option(
        "--size-udf",
        required=True,
        help=help,
    )


def concantration_udf(help: str = "Udf for Concantration (??).") -> click.option:
    return click.option(
        "--conc-udf",
        required=True,
        help=help,
    )


def concantration_nm_udf(help: str = "Udf for Concantration (nM).") -> click.option:
    return click.option(
        "--conc-nm-udf",
        required=True,
        help=help,
    )


def file_extension(help: str = "Define file extension") -> click.option:
    return click.option("-e", "--extension", required=False, default="", help=help)


def file_suffix(help: str = "Define file name suffix") -> click.option:
    return click.option("--suffix", required=False, default="", help=help)


def amount_udf_option(
    help: str = "String of UDF used to get amount value",
) -> click.option:
    return click.option("--amount-udf", required=True, help=help)


def volume_udf_option(
    help: str = "String of UDF used to get volume value",
) -> click.option:
    return click.option("--volume-udf", required=False, help=help)


def concentration_udf(
    help: str = "String of UDF used to get concentration value",
) -> click.option:
    return click.option("--concentration-udf", required=True, help=help)


def final_concentration_udf(
    help: str = "String of UDF used to get final concentration value",
) -> click.option:
    return click.option("--final-concentration-udf", required=True, help=help)


def prep(help: str = "Prep type") -> click.option:
    return click.option(
        "--prep-type",
        required=True,
        help=help,
        type=click.Choice(["wgs", "twist", "micro", "cov", "rna"]),
    )


def sequencing_method(help: str = "Sequencing Method") -> click.option:
    return click.option(
        "--sequencing-method",
        required=True,
        help=help,
        type=click.Choice(["novaseq-6000", "novaseq-x"]),
    )


def subtract_volume_option(
    help: str = "Subtracts volume taken from samples in QC checks",
) -> click.option:
    return click.option("--subtract-volume", type=click.Choice(["0", "3"]), default="3", help=help)


def automation_string(
    help: str = "Search string for automation",
) -> click.option:
    return click.option("--automation-string", required=True, help=help)


def lower_threshold(help: str = "Set lower threshold value") -> click.option:
    return click.option("-lt", "--lower-threshold", required=False, help=help, type=float)


def upper_threshold(help: str = "Set upper threshold value") -> click.option:
    return click.option("-ut", "--upper-threshold", required=False, help=help, type=float)


def ignore_fail(
    help: str = "Use this flag if you don't want to raise exception errors",
) -> click.option:
    return click.option(
        "--ignore-fail",
        default=False,
        is_flag=True,
        help=help,
    )


def sample_volume_limit(help: str = "Set sample volume limit") -> click.option:
    return click.option("-svl", "--sample-volume-limit", required=False, help=help, type=float)


def keep_failed_flags(
    help: str = "Stops the overwriting of failed QC flags.",
) -> click.option:
    return click.option(
        "--keep-failed-flags",
        default=False,
        is_flag=True,
        help=help,
    )


def container_type(
    help: str = "Specific container type, Tube or Plate.",
) -> click.option:
    return click.option(
        "-ct",
        "--container-type",
        required=False,
        multiple=False,
        help=help,
    )


def udf_values(
    help: str = "Possible UDF values",
) -> click.option:
    return click.option(
        "-uv",
        "--udf-values",
        required=False,
        multiple=True,
        help=help,
    )


def replicate_threshold(help: str = "Threshold for replicate difference.") -> click.option:
    return click.option("--replicate-threshold", required=True, help=help)


def concentration_threshold(help: str = "Threshold for concentrations.") -> click.option:
    return click.option("--concentration-threshold", required=True, help=help)


def size_bp(help: str = "Fragment size in base pairs.") -> click.option:
    return click.option("--size-bp", required=True, help=help)


def root_path(
    help: str = "Root path to be used by the script to find files.",
) -> click.option:
    return click.option("--root-path", required=True, help=help)


def preset_volume(
    help: str = "Give a pre-set volume to use for the calculations. Use only if no volume UDF is given.",
) -> click.option:
    return click.option("--preset-volume", required=False, help=help)


def subtract_volume(
    help: str = "Subtracts volume taken from samples.",
) -> click.option:
    return click.option("--subtract-volume", required=False, default=0, help=help)


def add_volume(
    help: str = "Add volume taken from samples.",
) -> click.option:
    return click.option("--add-volume", required=False, default=0, help=help)


def amount_fmol_udf(
    help: str = "String of UDF used to get amount (fmol)",
) -> click.option:
    return click.option(
        "--amount-fmol-udf", required=False, help=help, default="Amount needed (fmol)"
    )


def amount_ng_udf(
    help: str = "String of UDF used to get amount (ng)",
) -> click.option:
    return click.option("--amount-ng-udf", required=False, help=help, default="Amount needed (ng)")


def total_volume_udf(
    help: str = "String of process UDF used to get the total volume",
) -> click.option:
    return click.option("--total-volume-udf", required=False, help=help)


def total_volume_process_udf(
    help: str = "String of process UDF used to get the total volume from a process",
) -> click.option:
    return click.option("--total-volume-pudf", required=False, help=help)


def well_udf(help: str = "UDF name for artifact well.") -> click.option:
    return click.option("--well-udf", required=False, default=None, help=help)


def container_name_udf(help: str = "UDF name for container name.") -> click.option:
    return click.option("--container-name-udf", required=False, default=None, help=help)


def apptag(
    help: str = "String of UDF Sequencing Analysis, also known as apptag",
) -> click.option:
    return click.option(
        "--apptag",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_wgs(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for WGS samples",
) -> click.option:
    return click.option(
        "--apptag-wgs",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_wgs_tumor(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for WGS tumor samples",
) -> click.option:
    return click.option(
        "--apptag-wgs-tumor",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_tga(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for TGA samples",
) -> click.option:
    return click.option(
        "--apptag-tga",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_micro(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for micro samples",
) -> click.option:
    return click.option(
        "--apptag-micro",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_rml(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for RML samples",
) -> click.option:
    return click.option(
        "--apptag-rml",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_virus(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for virus samples",
) -> click.option:
    return click.option(
        "--apptag-virus",
        required=True,
        multiple=True,
        help=help,
    )


def apptag_rna(
    help: str = "String of UDF Sequencing Analysis, also known as apptag, for RNA samples",
) -> click.option:
    return click.option(
        "--apptag-rna",
        required=True,
        multiple=True,
        help=help,
    )


def factor(
    help: str = "Factor to multiply Reads to sequence (M) with",
) -> click.option:
    return click.option(
        "--factor",
        required=True,
        multiple=False,
        help=help,
    )


def factor_wgs_tumor(
    help: str = "Factor to multiply Reads to sequence (M) with for WGS tumor samples",
) -> click.option:
    return click.option(
        "--factor-wgs-tumor",
        required=True,
        multiple=False,
        help=help,
    )


def factor_tga(
    help: str = "Factor to multiply Reads to sequence (M) with for TGA samples",
) -> click.option:
    return click.option(
        "--factor-tga",
        required=True,
        multiple=False,
        help=help,
    )


def factor_micro(
    help: str = "Factor to multiply Reads to sequence (M) with for micro samples",
) -> click.option:
    return click.option(
        "--factor-micro",
        required=True,
        multiple=False,
        help=help,
    )


def factor_rml(
    help: str = "Factor to multiply Reads to sequence (M) with for RML samples",
) -> click.option:
    return click.option(
        "--factor-rml",
        required=True,
        multiple=False,
        help=help,
    )


def factor_rna(
    help: str = "Factor to multiply Reads to sequence (M) with for RNA samples",
) -> click.option:
    return click.option(
        "--factor-rna",
        required=True,
        multiple=False,
        help=help,
    )


def factor_rna_topups(
    help: str = "Factor to multiply Reads to sequence (M) with for RNA topup samples",
) -> click.option:
    return click.option(
        "--factor-rna-topups",
        required=True,
        multiple=False,
        help=help,
    )


def factor_rml_topups(
    help: str = "Factor to multiply Reads to sequence (M) with for RML topup samples",
) -> click.option:
    return click.option(
        "--factor-rml-topups",
        required=True,
        multiple=False,
        help=help,
    )


def factor_tga_topups(
    help: str = "Factor to multiply Reads to sequence (M) with for TGA topup samples",
) -> click.option:
    return click.option(
        "--factor-tga-topups",
        required=True,
        multiple=False,
        help=help,
    )


def factor_wgs_lower(
    help: str = "Lower factor to multiply Reads to sequence (M) with for WGS samples",
) -> click.option:
    return click.option(
        "--factor-wgs-lower",
        required=True,
        multiple=False,
        help=help,
    )


def factor_wgs_higher(
    help: str = "Higher factor to multiply Reads to sequence (M) with for WGS samples",
) -> click.option:
    return click.option(
        "--factor-wgs-higher",
        required=True,
        multiple=False,
        help=help,
    )


def threshold_reads(
    help: str = "Threshold for Reads to sequence (M) during adjustment",
) -> click.option:
    return click.option(
        "--threshold-reads",
        required=True,
        multiple=False,
        help=help,
    )


def reset_micro_reads(
    help: str = "A value to re-set Reads to sequence (M) for microbial samples",
) -> click.option:
    return click.option(
        "--reset-micro-reads",
        required=True,
        multiple=False,
        help=help,
    )


def reset_virus_reads(
    help: str = "A value to re-set Reads to sequence (M) for virus samples",
) -> click.option:
    return click.option(
        "--reset-virus-reads",
        required=True,
        multiple=False,
        help=help,
    )


def maximum_amount(
    help: str = "Maximum amount",
) -> click.option:
    return click.option("--max-amount", required=True, help=help)


def maximum_volume(
    help: str = "Maximum volume",
) -> click.option:
    return click.option("--max-volume", required=True, help=help)


def minimum_volume(
    help: str = "Minimum volume",
) -> click.option:
    return click.option("--min-volume", required=False, default=0, help=help)
