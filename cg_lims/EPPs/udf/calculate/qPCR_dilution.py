from __future__ import division

from genologics.entities import Process, Artifact

from openpyxl import load_workbook
import json
from statistics import mean, median
import numpy
from clinical_EPPs import WELL_TRANSFORMER
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from typing import Dict, List

import cg_lims.models.arnold.prep.twist.buffer_exchange

from cg_lims.get.artifacts import get_artifacts
from cg_lims.get.samples import get_one_sample_from_artifact

import logging
import sys

LOG = logging.getLogger(__name__)
# test first with one singular log-file

# get_artifacts function will be imported
# get_file function will not be needed as cli stuff will handle it


def make_dilution_data(dilution_file: str) -> Dict:
    df = pd.read_excel(dilution_file)
    dilution_data = {}
    # check if for-loop work
    for row in df.iterrows():
        well = row['Well']
        cq = round(row['Cq'], 3)
        sq = row['SQ']
        if not (numpy.isnan(cq) or numpy.isnan(sq)):
            orwell = WELL_TRANSFORMER[well]['well']
            dilut = WELL_TRANSFORMER[well]['dilut']
            if dilut in ['1E03', '2E03', '1E04']:
                if orwell not in dilution_data.keys():
                    dilution_data[orwell] = {
                        'SQ': {'1E03': [], '2E03': [], '1E04': []},
                        'Cq': {'1E03': [], '2E03': [], '1E04': []}}
                dilution_data[orwell]['SQ'][dilut].append(sq)
                dilution_data[orwell]['Cq'][dilut].append(cq)
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
    def __init__(self, artifact, dilution_data, sample_id):
        self.sample_id = sample_id
        self.dilution_data = dilution_data
        self.artifact = artifact
        self.size_bp = 470
        self.outart = artifact
        self.well = self.outart.location[1]
        self.Cq = {'1E03': self.dilution_data[self.well]['Cq']['1E03'],
                   '2E03': self.dilution_data[self.well]['Cq']['2E03'],
                   '1E04': self.dilution_data[self.well]['Cq']['1E04']}
        self.index = {'1E03': None, '2E03': None, '1E04': None}
        self.popped_dilutes = {'1E03': None, '2E03': None, '1E04': None}
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

        SQ_1E03 = mean(self.dilution_data[self.well]['SQ']['1E03'])
        SQ_2E03 = mean(self.dilution_data[self.well]['SQ']['2E03'])
        SQ_1E04 = mean(self.dilution_data[self.well]['SQ']['1E04'])
        orig_conc = (SQ_1E03*1000+SQ_2E03*2000+SQ_1E04*10000)/3
        size_adjust_conc_M = orig_conc*(452/self.size_bp)
        size_adjust_conc_nM= size_adjust_conc_M*1000000000

        try:
            self.outart.udf['Concentration'] = size_adjust_conc_M
            self.outart.udf['Size (bp)'] = int(self.size_bp)
            self.outart.udf['Concentration (nM)'] = size_adjust_conc_nM
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
        LOG.info(dil + ' Measurements : ' + str(self.Cq[dil]) + '\n')
        LOG.info('Removed measurement: ' + str(self.popped_dilutes[dil]) + '\n')
        LOG.info('One outlier removed, but distance still to big. \n\n')

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

        control_1E03 = False
        if not d1_in_range:
            array = numpy.array(self.Cq['1E03'])
            diff_from_mean_1E03 = numpy.absolute(array - mean(array))
            outlier_1E03 = max(diff_from_mean_1E03)
            array = numpy.array(self.Cq['1E04'])
            diff_from_mean_1E04 = numpy.absolute(array - mean(array))
            outlier_1E04 = max(diff_from_mean_1E04)
            if outlier_1E03 > outlier_1E04:
                ind = self.index['1E03']
                if type(ind) == int:
                    self._error_log_msg('1E03')
                    self.failed_sample = True
                    self.index['1E03'] = 'Fail'
                    return
                else:
                    control_1E03 = True
                    self.index['1E03'] = int(numpy.argmax(diff_from_mean_1E03))
            else:
                ind = self.index['1E04']
                if type(ind)==int:
                    self._error_log_msg('1E04')
                    self.failed_sample = True
                    self.index['1E04'] = 'Fail'
                    return
                else:
                    self.index['1E04'] = int(numpy.argmax(diff_from_mean_1E04))
        if not d2_in_range:
            array = numpy.array(self.Cq['2E03'])
            diff_from_mean_2E03 = numpy.absolute(array - numpy.median(array))/numpy.median(array).tolist()
            outlyer_2E03 = max(diff_from_mean_2E03)
            array = numpy.array(self.Cq['1E03'])
            diff_from_mean_1E03 = numpy.absolute(array - numpy.median(array))/numpy.median(array).tolist()
            outlier_1E03 = max(diff_from_mean_1E03)
            if outlyer_2E03 > outlier_1E03:
                ind = self.index['2E03']
                if type(ind)==int:
                    self._error_log_msg('2E03')
                    self.failed_sample = True
                    self.index['2E03'] = 'Fail'
                    return
                else:
                    self.index['2E03'] = int(numpy.argmax(diff_from_mean_2E03))
            else:
                if self.index['1E03'] is not None:
                    if control_1E03 and self.index['1E03'] != numpy.argmax(outlier_1E03):
                        LOG.info('Distance to big. Conflicting outlyers. ')
                        self.failed_sample = True
                        self.index['1E03'] = 'Fail'
                        return
                    elif not control_1E03:
                        self._error_log_msg('1E03')
                        self.failed_sample = True
                        self.index['1E03'] = 'Fail'
                        return
                else:
                    self.index['1E03'] = int(numpy.argmax(diff_from_mean_1E03))


def calculate_and_set_concentrations(artifacts: List[Artifact], dilution_data: Dict) -> None:
    """ For each sample:
        Checks dilution thresholds as described in am doc 1499.
        Calculates concentration and sets udfs for those samples that passed the check. """
    removed_replicates = 0
    failed_samples = 0
    passed_arts = 0
    failed_arts = 0
    for artifact in artifacts:
        sample = get_one_sample_from_artifact(artifact)
        sample_id = sample.id
        LOG.info('\n############################################\n')
        LOG.info('Sample: ' + sample_id + '\n')
        try:
            PA = PerArtifact(artifact, dilution_data, sample_id)
            PA.check_dilution_range()
            PA.check_distance_find_outlier()
            for dil in PA.index.keys():
                ind = PA.index[dil]
                if type(ind) == int:
                    removed_replicates += 1
                if ind != 'Fail':
                    LOG.info(dil + ' Measurements : ' + str(PA.Cq[dil]) + '\n')
                    if PA.popped_dilutes[dil]:
                        LOG.info('Removed measurement: ' + str(PA.popped_dilutes[dil]) + '\n')
            if PA.failed_sample:
                failed_samples += 1
            else:
                passed = PA.set_udfs()
                if passed:
                    passed_arts += 1
                else:
                    failed_arts += 1
        except:
            LOG.info(
                'Could not make calculations for this sample. Some data might be missing in the dilution file.\n')
            failed_arts += 1

    output_message = f"Updated {passed_arts} artifact(s), skipped {failed_arts} artifact(s)" \
                     f" with wrong and/or blank values for some udfs."


