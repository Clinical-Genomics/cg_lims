from typing import Optional, List
from datetime import date, datetime

from pydantic import BaseModel, Field, validator


class Lane(BaseModel):
    name: Optional[str] = ""
    percent_aligned_r1: Optional[float] = Field(None, alias="% Aligned R1")
    percent_aligned_r2: Optional[float] = Field(None, alias="% Aligned R2")
    percent_bases_q30_r1: Optional[float] = Field(None, alias="% Bases >=Q30 R1")
    percent_bases_q30_r2: Optional[float] = Field(None, alias="% Bases >=Q30 R2")
    percent_error_rate_r1: Optional[float] = Field(None, alias="% Error Rate R1")
    percent_error_rate_r2: Optional[float] = Field(None, alias="% Error Rate R2")
    percent_phasing_r1: Optional[float] = Field(None, alias="% Phasing R1")
    percent_prephasing_r1: Optional[float] = Field(None, alias="% Prephasing R1")
    percent_prephasing_r2: Optional[float] = Field(None, alias="% Prephasing R2")
    percentpf_r1: Optional[float] = Field(None, alias="%PF R1")
    percentpf_r2: Optional[float] = Field(None, alias="%PF R2")
    cluster_density_r1: Optional[float] = Field(None, alias="Cluster Density (K/mm^2) R1")
    cluster_density_r2: Optional[float] = Field(None, alias="Cluster Density (K/mm^2) R2")
    intensity_cycle_1_r1: Optional[float] = Field(None, alias="Intensity Cycle 1 R1")
    intensity_cycle_1_r2: Optional[float] = Field(None, alias="Intensity Cycle 1 R2")
    reads_pf_millions_r1: Optional[int] = Field(None, alias="Reads PF (M) R1")
    reads_pf_millions_r2: Optional[int] = Field(None, alias="Reads PF (M) R2")
    yield_pf_giga_bases_r1: Optional[float] = Field(None, alias="Yield PF (Gb) R1")
    yield_pf_giga_bases_r2: Optional[float] = Field(None, alias="Yield PF (Gb) R2")
    percent_phasing_r2: Optional[float] = Field(None, alias="% Phasing R2")


class FlowCell(BaseModel):
    instrument: Optional[str] = Field(None, alias="instrument")
    date: Optional[date]
    done: Optional[bool] = Field(None, alias="Done")
    buffer_expiration_date: Optional[date] = Field(None, alias="Buffer Expiration Date")
    buffer_lot_number: Optional[str] = Field(None, alias="Buffer Lot Number")
    buffer_part_number: Optional[str] = Field(None, alias="Buffer Part Number")
    buffer_serial_barcode: Optional[str] = Field(None, alias="Buffer Serial Barcode")
    flow_cell_expiration_date: Optional[date] = Field(None, alias="Flow Cell Expiration Date")
    flow_cell_id: Optional[str] = Field(None, alias="Flow Cell ID")
    flow_cell_lot_number: Optional[str] = Field(None, alias="Flow Cell Lot Number")
    flow_cell_mode: Optional[str] = Field(None, alias="Flow Cell Mode")
    flow_cell_part_number: Optional[str] = Field(None, alias="Flow Cell Part Number")
    pe_cycle_kit: Optional[str] = Field(None, alias="PE Cycle Kit")
    pe_expiration_date: Optional[date] = Field(None, alias="PE Expiration Date")
    pe_lot_number: Optional[str] = Field(None, alias="PE Lot Number")
    pe_part_number: Optional[str] = Field(None, alias="PE Part Number")
    pe_serial_barcode: Optional[str] = Field(None, alias="PE Serial Barcode")
    run_id: Optional[str] = Field(None, alias="Run ID")
    sbs_cycle_kit: Optional[str] = Field(None, alias="SBS Cycle Kit")
    sbs_expiration_date: Optional[date] = Field(None, alias="SBS Expiration Date")
    sbs_lot_number: Optional[str] = Field(None, alias="SBS Lot Number")
    sbs_part_number: Optional[str] = Field(None, alias="SBS Part Number")
    sbs_serial_barcode: Optional[str] = Field(None, alias="SBS Serial Barcode")
    lanes: Optional[List[Lane]] = []

    @validator(
        "sbs_expiration_date",
        "pe_expiration_date",
        "flow_cell_expiration_date",
        "buffer_expiration_date",
        "date",
        always=True,
    )
    def vali_date(cls, v, values) -> Optional[str]:
        if isinstance(v, date):
            return datetime(v.year, v.month, v.day).__str__()
        return None

    class Config:
        allow_population_by_field_name = True
