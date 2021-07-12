category = adapter.get_category(application_tag)
mongo_sample={}
mongo_sample['sequenced_to_delivered'] = get_number_of_days(sequenced_at, delivered_at)
mongo_sample['prepped_to_sequenced'] = get_number_of_days(prepared_at, sequenced_at)
mongo_sample['received_to_prepped'] = get_number_of_days(received_at, prepared_at)
mongo_sample['received_to_delivered'] = get_number_of_days(received_at, delivered_at)
mongo_sample['application_tag'] = application_tag
mongo_sample['category'] = category

conc_and_amount = get_final_conc_and_amount_dna(application_tag, sample.id,
                                                    lims)
mongo_sample['amount'] = conc_and_amount.get('amount')
mongo_sample['amount-concentration'] = conc_and_amount.get('concentration')

    concentration_and_nr_defrosts = get_concentration_and_nr_defrosts(
        application_tag, sample.id, lims)
 mongo_sample['nr_defrosts'] = concentration_and_nr_defrosts.get(
        'nr_defrosts')
mongo_sample[
        'nr_defrosts-concentration'] = concentration_and_nr_defrosts.get(
            'concentration')
mongo_sample['lotnr'] = concentration_and_nr_defrosts.get('lotnr')

mongo_sample[
        'microbial_library_concentration'] = get_microbial_library_concentration(
            application_tag, sample.id, lims)

mongo_sample['library_size_pre_hyb'] = get_library_size(
        application_tag, sample.id, lims, 'TWIST', 'library_size_pre_hyb')
mongo_sample['library_size_post_hyb'] = get_library_size(
        application_tag, sample.id, lims, 'TWIST', 'library_size_post_hyb')
if not mongo_sample['library_size_post_hyb']:
    if not received_at or received_at < dt(2019, 1, 1):
        mongo_sample['library_size_pre_hyb'] = get_library_size(
            application_tag, sample.id, lims, 'SureSelect',
            'library_size_pre_hyb')
        mongo_sample['library_size_post_hyb'] = get_library_size(
            application_tag, sample.id, lims, 'SureSelect',
            'library_size_post_hyb')