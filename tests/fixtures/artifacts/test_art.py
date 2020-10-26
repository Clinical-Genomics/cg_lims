url = 'https://testgenologics.com:4040'

test_art1 = f"""<art:artifact xmlns:udf="http://genologics.com/ri/userdefined" xmlns:file="http://genologics.com/ri/file" xmlns:art="http://genologics.com/ri/artifact" uri="{url}/api/v2/artifacts/2-1001313?state=749600" limsid="2-1001313">
<name>2020-14477-03 (qPCR)</name>
<type>Analyte</type>
<output-type>Analyte</output-type>
<parent-process uri="{url}/api/v2/processes/151-148238" limsid="151-148238"/>
<qc-flag>UNKNOWN</qc-flag>
<location>
<container uri="{url}/api/v2/containers/27-105973" limsid="27-105973"/>
<value>C:1</value>
</location>
<working-flag>true</working-flag>
<sample uri="{url}/api/v2/samples/ACC6955A3" limsid="ACC6955A3"/>
<reagent-label name="C09 IDT_10nt_470 (GTGAATGGTT-AGCTCTACAA)"/>
<workflow-stages>
<workflow-stage status="COMPLETE" name="Bead Purification (pre hybridization) TWIST" uri="{url}/api/v2/configuration/workflows/1201/stages/3998"/>
</workflow-stages>
</art:artifact>"""