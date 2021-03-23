PLACEMENT_MAP_HEADER = """
    <html>
    <head>
    <style>table, th, td {{border: 1px solid black; border-collapse: collapse;}}</style>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
    <link href="../css/g/queue-print.css" rel="stylesheet" type="text/css" media="screen,print">
    <title>Pooling Map</title>
    </head>
    <body>
    <div id="header">
    <h1 class="title">{process_type}</h1>
    </div>
    Created: {date}
    """

POOL_HEADER = """
    <table class="group-contents">
    <thead>
    <tr><th class="group-header" colspan="10"><h2> {pool_name}</h2>
    <table>
    <tbody>
    <tr>
    <td class="group-field-label">Pool LIMS ID: </td>
    <td class="group-field-value">{pool_id}</td>
    </tr>
    <tr>
    <td class="group-field-label">Nr samples in pool: </td>
    <td class="group-field-value">{nr_samples}</td>
    </tr>
    {pools_information}
    </tbody>
    </table>
    <br>
    """

SAMPLE_COLUMN_HEADERS = """
    <tr>
    <th style="width: 7%;" class="">Sample Lims ID</th>
    <th style="width: 7%;" class="">Source Well</th>
    <th style="width: 7%;" class="">Source Container</th>
    {extra_sample_columns}
    </tr>
    """

SAMPLE_COLUMN_VALUES = """
    <tr>
    <td style="width: 7%;">{sample_id}</td>
    <td class="" style="width: 7%;">{source_well}</td>
    <td class="" style="width: 7%;">{source_container}</td>
    {extra_sample_values}
    </tr>
    """
