POOL_TEMPLATE = """<table class="group-contents">
            <thead>
            <tr><th class="group-header" colspan="10"><h2> {pool_name}</h2>
            <table>
            <tbody>
            <tr>
            <td class="group-field-label">Container LIMS ID: </td>
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
