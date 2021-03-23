PLACEMENT_MAP_HEADER = """
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
    <span>Created {date} </span>"""

PLATE_HEADER_SECTION = """
<tr>
<th class="group-header" colspan="10"><h2>Sample placement map: {container_name}</h2>
<table>
<tbody>
<tr>
<td class="group-field-label">{container_type}: </td>
<td class="group-field-value">{container_name}</td>
</tr>
<tr>
<td class="group-field-label">Container LIMS ID: </td>
<td class="group-field-value">{container_id}</td>
</tr>
</tbody>
</table>
<br>
</th>
</tr>"""

TABLE_HEADERS = """
<tr>
<th style="width: 7%;" class="">Project Name</th>
<th style="width: 7%;" class="">Sample/Pool Name</th>
<th style="width: 7%;" class="">Sample/Pool ID</th>
<th style="width: 7%;" class="">{container_source} Container</th>
<th style="width: 7%;" class="">{container_source} Well</th>
<th style="width: 7%;" class="">Dest. Well</th>
</tr>"""


TABLE_ROWS = """
<tr>
<td style="width: 7%;">{project_name}</td>
<td class="" style="width: 7%;">{sample_name}</td>
<td class="" style="width: 7%;">{sample_id}</td>
<td class="" style="width: 7%;">{container_name}</td>
<td class="" style="width: 7%;">{well}</td>
<td class="" style="width: 7%;">{dest_well}</td>
</tr>"""


VISUAL_PLACEMENT_MAP_HEADER = """
<table class="print-container-view">
<thead>
<tr>
<th>&nbsp;</th>
<th>1</th>
<th>2</th>
<th>3</th>
<th>4</th>
<th>5</th>
<th>6</th>
<th>7</th>
<th>8</th>
<th>9</th>
<th>10</th>
<th>11</th>
<th>12</th>
<th>13</th>
</tr>
</thead>"""

VISUAL_PLACEMENT_MAP_WELL = """
<td class="well" style="background-color: #CCC;">
Project : {project_name}<br>
{sample_type} Name : {sample_name}<br>
{sample_type} ID : {sample_id}<br>
{container_source} : {container_name}<br>
{well_source} : {well}<br>
{exta_udf_info}
</td>"""
