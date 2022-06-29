from __future__ import division

from genologics.entities import Artifact

from statistics import mean, median
import numpy
import pandas as pd
import click
from typing import Dict, List, TextIO

from cg_lims import options
from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact
from cg_lims.EPPs.udf.calculate import WELL_TRANSFORMER
from cg_lims.exceptions import MissingFileError, FileError, LimsError

import logging
import sys

LOG = logging.getLogger(__name__)

# get_artifacts function will be imported
# get_file function will not be needed as cli stuff will handle it


def make_dilution_data(dilution_file: str) -> Dict:
    df = pd.read_excel(dilution_file)
    dilution_data = {}
    # check if for-loop works, otherwise add index to input
    for row in df.iterrows():
        well = row['Well']
        cq = round(row['Cq'], 3)
        sq = row['SQ']
        if not (numpy.isnan(cq) or numpy.isnan(sq)):
            orig_well = WELL_TRANSFORMER[well]['well']
            dilute = WELL_TRANSFORMER[well]['dilute']
            if dilute in ['1E03', '2E03', '1E04']:
                if orig_well not in dilution_data.keys():
                    dilution_data[orig_well] = {
                        'SQ': {'1E03': [], '2E03': [], '1E04': []},
                        'Cq': {'1E03': [], '2E03': [], '1E04': []}}
                dilution_data[orig_well]['SQ'][dilute].append(sq)
                dilution_data[orig_well]['Cq'][dilute].append(cq)
    return dilution_data


class PerArtifact:
    """Artifact specific class do determine measurement outliers and calculate dilution.
    CHECK 1.
        Compares the Cq-values within each dilution for the sample.
        If they differ by more than 0.4 within the dilution:
            a)  The the Cq-value differing most from the mean, is removed and
                its index is stored in self.index.
            b)  If the two remaining Cq-values still differ by more than 0.4,
                The self.failed_sample is set to true
    CHECK 2.
        Compares the Cq-values between the different dilution series; 1E03, 2E03 and 1E04:
        If 0.7 >mean(2E03)-mean(1E03)> 1.5:
            The biggest outlier from the two series are compared and the biggest one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(2E03)-2E03|))
                Its index is stored in self.index
        If 2.5 >mean(1E04)-mean(1E03)> 5:
            The biggest outlier from the two series are compared and the biggest one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(1E04)-1E04|))
                Its index is stored in self.index
        This is repeated until 0.7 <mean(2E03)-mean(1E03)< 1.5 and 2.5 <mean(1E04)-mean(1E03)< 5,
        or until a dilution series contains only one value. If this happens, self.failed_sample is set to true."""
    def __init__(self, artifact, dilution_data, sample_id, log):
        self.dilution_log = log
        self.sample_id = sample_id
        self.dilution_data = dilution_data
        self.artifact = artifact
        self.size_bp = 470
        self.outart = artifact
        self.well = self.outart.location[1]
        self.Cq = {'1E03': self.dilution_data[self.well]['Cq']['1E03'],
                   '2E03': self.dilution_data[self.well]['Cq']['2E03'],
                   '1E04': self.dilution_data[self.well]['Cq']['1E04']}
        self.index = {'1E03': '', '2E03': '', '1E04': ''}
        self.popped_dilutes = {'1E03': '', '2E03': '', '1E04': ''}
        self.failed_sample = False

    def check_dilution_range(self):
        """CHECK 1.
        Compares the Cq-values within each dilution for the sample.
        If they differ by more than 0.4 within the dilution:
            a)  The the Cq-value differing most from the mean, is removed and
                its index is stored in self.index.
            b)  If the two remaining Cq-values still differ by more than 0.4,
                The self.failed_sample is set to true"""
        for dil, values in self.Cq.items():
            error_msg = 'To vide range of values for dilution: ' + dil + ' : ' + str(values)
            array = numpy.array(self.Cq[dil])
            diff_from_mean = numpy.absolute(array - mean(array))
            while max(self.Cq[dil])-min(self.Cq[dil]) > 0.4:
                ind = self.index[dil]
                if type(ind) == int:
                    LOG.info(error_msg)
                    self.failed_sample = True
                    self.index[dil] = 'Fail'
                    return
                else:
                    ind = numpy.argmax(diff_from_mean)
                    self.index[dil] = int(ind)
                    self.popped_dilutes[dil] = self.Cq[dil].pop(ind)
                    array = numpy.array(self.Cq[dil])
                    diff_from_mean = numpy.absolute(array - mean(array))

    def check_distance_find_outlier(self):
        """CHECK 2.
        Compares the Cq-values between the different dilution series; 1E03, 2E03 and 1E04:
        If 0.7 >mean(2E03)-mean(1E03)> 1.5:
            The biggest outlier from the two series are compared and the biggest one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(2E03)-2E03|))
                Its index is stored in self.index
        If 2.5 >mean(1E04)-mean(1E03)> 5:
            The biggest outlier from the two series are compared and the bigegst one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(1E04)-1E04|))
                Its index is stored in self.index
        This is repeated until 0.7 <mean(2E03)-mean(1E03)< 1.5 and 2.5 <mean(1E04)-mean(1E03)< 5,
        or until a dilution series contains only one value. If this happens, self.failed_sample is set to true."""

        d1_in_range, d2_in_range = self._check_distance()
        while not (d1_in_range and d2_in_range):
            self._find_outlier(d1_in_range, d2_in_range)
            if self.failed_sample:
                return
            for dilute, ind in self.index.items():
                if type(ind) == int and len(self.Cq[dilute]) == 3:
                    self.popped_dilutes[dilute] = self.Cq[dilute].pop(ind)
            d1_in_range, d2_in_range = self._check_distance()

    def set_udfs(self):
        """ This will only happen if failed_sample is still False:
        1. For every outlier stored in self.index, removes its corresponding SQ measurement.
        2. Calculates the size adjusted concentration based on the remaining SQ measurements.
        3. Sets the artifact udfs; Concentration, Concentration (nM) and Size (bp)"""

        for dilute, ind in self.index.items():
            if type(ind) == int:
                self.dilution_data[self.well]['SQ'][dilute].pop(ind)
                # removing outlier

        sq_1e03 = mean(self.dilution_data[self.well]['SQ']['1E03'])
        sq_2e03 = mean(self.dilution_data[self.well]['SQ']['2E03'])
        sq_1e04 = mean(self.dilution_data[self.well]['SQ']['1E04'])
        orig_conc = (sq_1e03*1000+sq_2e03*2000+sq_1e04*10000)/3
        size_adjust_conc_molar = orig_conc*(452/self.size_bp)
        size_adjust_conc_n_molar = size_adjust_conc_molar*1000000000

        try:
            self.outart.udf['Concentration'] = size_adjust_conc_molar
            self.outart.udf['Size (bp)'] = int(self.size_bp)
            self.outart.udf['Concentration (nM)'] = size_adjust_conc_n_molar
            if self.outart.udf['Concentration (nM)'] < 2:
                self.outart.qc_flag = "FAILED"
            else:
                self.outart.qc_flag = "PASSED"
            self.outart.put()
            return True
        except:
            return False

    def _error_log_msg(self, dil):
        """Log for failed sample"""
        self.dilution_log.write(dil + ' Measurements : ' + str(self.Cq[dil]) + '\n')
        self.dilution_log.write('Removed measurement: ' + str(self.popped_dilutes[dil]) + '\n')
        self.dilution_log.write('One outlier removed, but distance still to big. \n\n')

    def _check_distance(self):
        """Compares the difference between the mean of the triplicates for the different dilutions.
        Checks whether the differences are within accepted ranges:
        0.7 <mean(2E03)-mean(1E03)< 1.5 and 2.5 <mean(1E04)-mean(1E03)< 5"""
        d1 = mean(self.Cq['1E04'])-mean(self.Cq['1E03'])
        d1_in_range = 2.5 < d1 < 5
        d2 = mean(self.Cq['2E03'])-mean(self.Cq['1E03'])
        d2_in_range = 0.7 < d2 < 1.5
        return d1_in_range, d2_in_range

    def _find_outlier(self, d1_in_range, d2_in_range):
        """
        If 0.7 >mean(2E03)-mean(1E03)> 1.5:
            The biggest outlier from the two series are compared and the biggest one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(2E03)-2E03|))
                Its index is stored in self.index
        If 2.5 >mean(1E04)-mean(1E03)> 5:
            The biggest outlier from the two series are compared and the biggest one, removed:
                max(max(|mean(1E03)-1E03|), max(|mean(1E04)-1E04|))
                Its index is stored in self.index"""

        control_1e03 = False
        if not d1_in_range:
            array = numpy.array(self.Cq['1E03'])
            diff_from_mean_1e03 = numpy.absolute(array - mean(array))
            outlier_1e03 = max(diff_from_mean_1e03)
            array = numpy.array(self.Cq['1E04'])
            diff_from_mean_1e04 = numpy.absolute(array - mean(array))
            outlier_1e04 = max(diff_from_mean_1e04)
            if outlier_1e03 > outlier_1e04:
                ind = self.index['1E03']
                if type(ind) == int:
                    self._error_log_msg('1E03')
                    self.failed_sample = True
                    self.index['1E03'] = 'Fail'
                    return
                else:
                    control_1e03 = True
                    self.index['1E03'] = str(int(numpy.argmax(diff_from_mean_1e03)))
            else:
                ind = self.index['1E04']
                if type(ind) == int:
                    self._error_log_msg('1E04')
                    self.failed_sample = True
                    self.index['1E04'] = 'Fail'
                    return
                else:
                    self.index['1E04'] = str(int(numpy.argmax(diff_from_mean_1e04)))
        if not d2_in_range:
            array = numpy.array(self.Cq['2E03'])
            diff_from_mean_2e03 = numpy.absolute(array - numpy.median(array))/numpy.median(array).tolist()
            outlier_2e03 = max(diff_from_mean_2e03)
            array = numpy.array(self.Cq['1E03'])
            diff_from_mean_1e03 = numpy.absolute(array - numpy.median(array))/numpy.median(array).tolist()
            outlier_1e03 = max(diff_from_mean_1e03)
            if outlier_2e03 > outlier_1e03:
                ind = self.index['2E03']
                if type(ind) == int:
                    self._error_log_msg('2E03')
                    self.failed_sample = True
                    self.index['2E03'] = 'Fail'
                    return
                else:
                    self.index['2E03'] = str(int(numpy.argmax(diff_from_mean_2e03)))
            else:
                if self.index['1E03'] is not None:
                    if control_1e03 and self.index['1E03'] != numpy.argmax(outlier_1e03):
                        LOG.info('Distance to big. Conflicting outliers. ')
                        self.failed_sample = True
                        self.index['1E03'] = 'Fail'
                        return
                    elif not control_1e03:
                        self._error_log_msg('1E03')
                        self.failed_sample = True
                        self.index['1E03'] = 'Fail'
                        return
                else:
                    self.index['1E03'] = str(int(numpy.argmax(diff_from_mean_1e03)))


def calculate_and_set_concentrations(artifacts: List[Artifact], dilution_data: Dict, dilution_log: TextIO) -> str:
    """ For each sample:
        Checks dilution thresholds as described in AM doc 1499.
        Calculates concentration and sets UDFs for those samples that passed the check. """
    removed_replicates = 0
    failed_samples = 0
    passed_arts = 0
    failed_arts = 0
    for artifact in artifacts:
        sample = get_one_sample_from_artifact(artifact)
        sample_id = sample.id
        dilution_log.write('\n############################################\n')
        dilution_log.write('Sample: ' + sample_id + '\n')
        try:
            pa = PerArtifact(artifact, dilution_data, sample_id)
            pa.check_dilution_range()
            pa.check_distance_find_outlier()
            for dil in pa.index.keys():
                ind = pa.index[dil]
                if type(ind) == int:
                    removed_replicates += 1
                if ind != 'Fail':
                    dilution_log.write(dil + ' Measurements : ' + str(pa.Cq[dil]) + '\n')
                    if pa.popped_dilutes[dil]:
                        dilution_log.write('Removed measurement: ' + str(pa.popped_dilutes[dil]) + '\n')
            if pa.failed_sample:
                failed_samples += 1
            else:
                passed = pa.set_udfs()
                if passed:
                    passed_arts += 1
                else:
                    failed_arts += 1
        except:
            dilution_log.write(
                'Could not make calculations for this sample. Some data might be missing in the dilution file.\n')
            failed_arts += 1

    output_message = f"Updated {passed_arts} artifact(s), skipped {failed_arts} artifact(s)" \
                     f" with wrong and/or blank values for some UDFs."

    if removed_replicates:
        output_message += f" WARNING: Removed replicate from {removed_replicates} samples. See log file for details."

    if failed_samples:
        output_message += f" WARNING: Failed to set UDFs on {failed_samples} samples, " \
                          f"due to unstable dilution measurements"

    if failed_arts or failed_samples:
        raise FileError(message=output_message)
    else:
        return output_message


@click.command()
@options.dilution_file()
@options.dilution_log()
@click.pass_context
def qpcr_dilution_calculation(ctx, dilution_file: str, dilution_log: str) -> None:
    """Script for calculating qPCR dilutions. Requires an input qPCR result file and produces an output log file."""

    LOG.info(f"Running {ctx.command_path} with params: {ctx.params}")
    process = ctx.obj["process"]

    try:
        dilution_log_file = open(dilution_log, 'a')
        artifacts: List[Artifact] = get_artifacts(process=process, input=True)
        dilution_data: Dict = make_dilution_data(dilution_file=dilution_file)
        message: str = calculate_and_set_concentrations(
            artifacts=artifacts,
            dilution_data=dilution_data,
            dilution_log=dilution_log_file
        )
        dilution_log_file.close()
        LOG.info(message)
        click.echo(message)
    except LimsError as e:
        LOG.error(e.message)
        sys.exit(e.message)
