entety_data = {
    "make_kapa_csv": {
        "artifacts_kapa_library_preparation": [
            {
                "id": "a1",
                "samples": [{"sample_id": "ACC7118A28"}],
                "location": ('', 'A:1'),
                "reagent_labels": ["A01 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)"],
            },
            {
                "id": "a2",
                "samples": [{"sample_id": "ACC7118A29"}],
                "location": ('', 'A:2'),
                "reagent_labels": ["A02 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)"],
            },
            {
                "id": "a3",
                "samples": [{"sample_id": "ACC7118A30"}],
                "location": ('', 'A:3'),
                "reagent_labels": ["A03 IDT_10nt_446 (AGCGTGACCT-CCATCCGAGT)"],
            },
        ],
        "artifacts_enzymatic_feragmentation": [
            {
                "id": "a1",
                "samples": [{"sample_id": "ACC7118A28"}],
                "location": ('', 'A:1'),
            },
            {
                "id": "a2",
                "samples": [{"sample_id": "ACC7118A29"}],
                "location": ('', 'B:1'),
            },
            {
                "id": "a3",
                "samples": [{"sample_id": "ACC7118A30"}],
                "location": ('', 'C:1'),
            },
        ],
        "amount_artifacts": [
            {"id": "a4", "type": "Analyte", "samples": [{"sample_id": "ACC7118A28"}], "udf": {"Amount needed (ng)": 20}},
            {"id": "a5", "type": "Analyte", "samples": [{"sample_id": "ACC7118A29"}], "udf": {"Amount needed (ng)": 300}},
            {"id": "a6", "type": "Analyte", "samples": [{"sample_id": "ACC7118A30"}], "udf": {"Amount needed (ng)": 55}},
        ],
        "amount_artifacts_missing_udf": [
            {"id": "a4", "type": "Analyte", "samples": [{"sample_id": "ACC7118A28"}], "udf": {"Amount needed (ng)": 20}},
            {"id": "a5", "type": "Analyte", "samples": [{"sample_id": "ACC7118A29"}], "udf": {"Amount needed (ng)": 300}},
            {"id": "a6", "type": "Analyte", "samples": [{"sample_id": "ACC7118A30"}]},
        ],
    }
}

