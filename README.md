# cg_lims [![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/cg_lims/badge.svg)](https://coveralls.io/github/Clinical-Genomics/cg_lims)  ![Latest Release](https://img.shields.io/github/v/release/clinical-genomics/cg_lims)

A package for lims interactions. The aim is to replace all other lims interactions at CG with this new package.

## Database access
The lims ststem is built upon a postgress database. Illumina provides a [REST API](https://clinical-lims-stage.scilifelab.se/api/v2/) for accessing the database. On top of that there is a python API, the [genologics](https://github.com/SciLifeLab/genologics) packge wich simply translates the rest into python. cg_lims is hevily depending upon the genologics python API. 

## Release model

cg_lims is using github flow release model as described in our development manual.


### Steps to make a new release:

1) Get you PR approved.
2) Append the version bump to PR title. Eg. __Update README__ becomes __Update Readme (patch)__
3) Select __squash and merge__
4) Write a change log comment.
5) Merge.

## Config files
   
The genologics package requires a config: **~/.genologicsrc**
Read about this [here](https://github.com/SciLifeLab/genologics).



## Production and Stage

The production lims system is set up on hippocampus and the stage lims system is set up on amygdala.

ssh into the servers:

`ssh gls@clinical-lims-stage.scilifelab.se`

`ssh gls@clinical-lims.scilifelab.se`

You will need a password wich is kept in the safety locker at clinical genomics.

Testing of new code or new workflows takes place on the stage server.


## About Arnold

### What is Arnold and why?
[Arnold](https://github.com/Clinical-Genomics/arnold) is a  REST-API and database with two collections - `sample` and `step`. Currently soring lims-data only. 

Data is continuously pushed into the database from lims steps via cg_lims commands, using the arnold REST-API.

So why do we want to store lims data in another database? 
Two reasons: The design of the lims postgres database doesn't fit the kind of queries that we often need to do at cg. And 
we are not allowed to redesign the original postgres database on wich our lims is built. 

#### Step Type and Workflow - General arnold fields that make querying easy
The problem with the design of the lims postgres database is that there is nothing linking two versions of a master step,
protocol or workflow. But when we update a version of a workflow in lims, we are obviously still working within the same 
lab process in real life. 

This lack of linking creates problems when you want to track lims data over time. Say you need to look at some volume 
measured in the Buffer Exchange step in the TWIST workflow over time. In order to get those concentrations, you need to 
know the name of all versions of the Buffer Exchange master steps that has been. 

In the writing moment we have 33 distinct lims-protocols where each protocol has approximately four distinct steps and 
where each step exist in several versions and continuously get new versions. There are a lot of master step names to keep 
track of if we want to trend stuff!

In Arnold, steps contains two general fields **workflow** and **step_type**, which solve the problem above.

Example: The lims workflows: "Twist v1", "TWist v2", "TWIST_v3", ect, are all just twist workflows in arnold

Example: The steps "cg001 Buffer Exchange",  "Buffer Exchange v1" and  "Buffer Exchange v2" are all just buffer_exchange steps in arnold.

A arnold step is allso allways part of a specific prep (or sequencing workflow), with a specific **prep_id** (or sequencing id. Not in place yet.)

#### The prep_id
Labb prep steps in arnold are joind by prep_id. The prep_id is created from the step where the arnold prep is being uploaded. 

Ex. the upload of a arnold WGS prep is being run from the last prep step in the WGS workflow, before sequecning *Aggregate QC (Library Validation)*. 

The step id together with the sample id creates the prep id for that sample: <sample_id>_< the id of the last step in prep workflow>

All steps that are being created, defined by the WGS prep model, will get the same prep id. Note that if a sample has run through the same step several times, its the last step that will be picked up as part of the prep and be loaded into arnold with the prep_id. 

This means a prep will allways have only one of each step_type that defines the preop. And all the steps withion the same sample prep will have the same prep_id.

#### A arnold step is in fact a sample-step
A step document in arnold is sample_id-step_id specific. We have collected all the information that we from experience 
know are relevant for us, into one sample-step centric document. 

This is the general model for a arnold step document. 

```
class Step(BaseModel):
    id: str = Field(..., alias="_id")
    prep_id: str
    step_type: str
    sample_id: str
    workflow: str
    lims_step_name: Optional[str]
    step_id: str
    well_position: Optional[str]
    artifact_name: Optional[str]
    container_name: Optional[str]
    container_id: Optional[str]
    container_type: Optional[str]
    index_name: Optional[str]
    nr_samples_in_pool: Optional[int]
    date_run: Optional[datetime]
    artifact_udfs: Optional[dict]
    process_udfs: Optional[dict]
```

### Arnold Step Models in cg_lims

So the step model above is general for all steps and each step-type inherits from the general step model, but has some extra constraints to it - making it step-type specific. 
This is to enforce eg a buffer-exchange step to always hold the specific buffer-exchange data. 
Each step type has its own definition - Model. 
The arnold models are all stored under [cg_lims/cg_lims/models/arnold/prep/](https://github.com/Clinical-Genomics/cg_lims/tree/master/cg_lims/models/arnold/prep). 

```
├── prep
│    ├── base_step.py
│    ├── microbial_prep
│    │    ├── buffer_exchange.py
│    │    ├── microbial_library_prep_nextera.py
│    │    ├── normailzation_of_microbial_samples_for_sequencing.py
│    │    ├── normalization_of_microbial_samples.py
│    │    ├── post_pcr_bead_purification.py
│    │    └── reception_control.py
│    ├── rna
│    │    ├── a_tailing_and_adapter_ligation.py
│    │    ├── aliquot_samples_for_fragmentation.py
│    │    ├── normalization_of_samples_for_sequencing.py
│    │    └── reception_control.py
│    ├── sars_cov_2_prep
│    │    ├── library_preparation.py
│    │    ├── pooling_and_cleanup.py
│    │    └── reception_control.py
│    ├── twist
│    │    ├── aliquot_samples_for_enzymatic_fragmentation_twist.py
│    │    ├── amplify_captured_libraries.py
│    │    ├── bead_purification_twist.py
│    │    ├── buffer_exchange.py
│    │    ├── capture_and_wash_twist.py
│    │    ├── enzymatic_fragmentation_twist.py
│    │    ├── hybridize_library_twist.py
│    │    ├── kapa_library_preparation_twist.py
│    │    ├── pool_samples_twist.py
│    │    └── reception_control.py
│    └── wgs
│    │    ├── aliquot_sampels_for_covaris.py
│    │    ├── endrepair_size_selection_a_tailing_adapter_ligation.py
│    │    ├── fragment_dna_truseq_dna.py
│    │    └── reception_control.py

```


#### Update a step-type model
What defines a stpe type model beside the step_type and workflow fields, are the *process udfs* and *artifact udfs* relevant to the step. 


>**NOTE** Not all process and artifact udfs from a lims process are being stoired in the arnold step, only the once that are important for cg outside the lims system - eg. for trending, trouble shooting, report generation etc.


The models need to be up to date with our lims system all the time, meaning that if a master step gets a new version, the new version neame needs to be updated in the step model. If a process or artifact udf is removed from step in lims, it needs to be removed from the arnold step model as well. And the same if new UFDs are added to lims - if we want them as part of the arnold step, they obvously need to be added to the step model.


Example: This is a step modle for Post-PCR bead purification. 


<img width="554" alt="Skärmavbild 2022-03-13 kl  08 11 54" src="https://user-images.githubusercontent.com/1306333/158049460-b6846201-6099-4737-ae6a-c16715de9f07.png">

If you remove the artifact udf 'Average Size (bp)' from the process in lims, it needs to be removed from ther step model. 

If you update the master step 'Post-PCR bead purification v1' in lims to 'Post-PCR bead purification v2', it needs to be updated in the step model.


## About EPPs

The External Program Plug-in (EPP) is a script that is configured to be run from within a lims step.

Clinical Genomics LIMS is using both scripts that are developed and maintained by Genologics, and scripts that are developed by developers at Clinical Genomics. Scripts developed and maintained by Clinical Genomics are located in [cg_lims/cg_lims/EPPs](https://github.com/Clinical-Genomics/cg_lims/tree/master/cg_lims/EPPs).

Development of new EPPs is preferably done locally, but the final testing is done on the stage server.



### Install
The procedure for installing is the same on both servers.

Curently cg_lims is cloned into `/home/glsai/opt/` and installed by the glsai user under the conda environment `cg_lims`.

```
sudo -iu glsai
source activate cg_lims
pip install -U "git+https://github.com/Clinical-Genomics/cg_lims@<branch name>"
```
The branch that has been installed is now avalibe from within the [lims web interface](https://clinical-lims-stage.scilifelab.se/clarity/).

Test it from the command line:

```
(python3)glsai@clinical-lims-stage:~$ epps --help
Usage: epps [OPTIONS] COMMAND [ARGS]...

Options:
  -l, --log TEXT      Path to log file.  [required]
  -p, --process TEXT  Lims id for current Process.  [required]
  --help              Show this message and exit.

Commands:
  move-samples              Script to move aritfats to another stage.
  place-samples-in-seq-agg  Queueing artifacts with given udf==True, to...
  rerun-samples             Script to requeue samples for sequencing.
```




### Configure EPPs

The branch with the new script has been installed, and you want to test the script through the web interface. (Or deploy it to production. The procedure is the same.)

Let us call the new script we want to test: `move-samples`. Running it from the command line looks like this:

```
(python3)glsai@clinical-lims-stage:~$ epps -p 'some-process' -l 'log' move-samples  --help
Usage: epps move-samples [OPTIONS]

  Script to move aritfats to another stage.

  Queueing artifacts with <udf==True>, to stage with <stage-id> in workflow
  with <workflow-id>. Raising error if quiueing fails.

Options:
  -w, --workflow-id TEXT  Destination workflow id.  [required]
  -s, --stage-id TEXT     Destination stage id.  [required]
  -u, --udf TEXT          UDF that will tell wich artifacts to move.
                          [required]

  -i, --input-artifacts   Use this flag if you want to queue the input
                          artifacts of the current process. Default is to
                          queue the output artifacts (analytes) of the
                          process.

  --help                  Show this message and exit.

```

When the script is configured in the lims step, arguments bust be replaced by `tokens`. They function as placeholders that are replaced with actual values at runtime. You can read more about tokens [here](https://genologics.zendesk.com/hc/en-us/articles/115000028563-Step-Automation-Tokens.

To make the new script avalible in the [web interface](https://clinical-lims-stage.scilifelab.se/clarity), go to the `CONFIGURATON` tab and then select `AUTOMATION`. Klick the `NEW AUTOMATON` button.

- Choose a Automation Name
- Channel Name should always be `limsserver`.
- Enter the command line string. If you need help selecting a token for an argument, klick the `TOKENS` tab wich will show the list of avalible tokens. In this case the string is
`bash -c "source activate python3 && epps -l {compoundOutputFileLuid0} -p {processLuid} move-samples -w '801' -s '1532' -u 'HiSeq2500'"`
- Under `AUTOMATION USE`, select master step(s) in which the new EPP should be available.
- Save


![](img/Automation_details.png)


Once the EPP is in place on the master step you need to configure its usage. This can be done both on master step and on step level. 

Klick the `LAB WORK` tab and select a step in which you have enabeled the EPP. 


![](img/configuration_labwork.png)



Choose `STEP` or `MASTER STEP`, and scroll down to the `AUTOMATION` section. The new EPP should be seen there. 


![](img/step_settings.png)


Select Trigger Location - at what point in the step the script should be run, and Trigger Style - how the script should be triggered.

The script is now avalible from within the step. Queue some samples to the step to try it!

![](img/record_details_view.png)

Read more about EPPs in the [Clarity LIMS API Cookbook](https://genologics.zendesk.com/hc/en-us/restricted?return_to=https%3A%2F%2Fgenologics.zendesk.com%2Fhc%2Fen-us%2Fcategories%2F201688743-Clarity-LIMS-API-Cookbook)


### Trouble shooting

When a script is failing, usually as a developer, you will get this information from the lims user who has run the script from within a specific lims step. It´s easiest to trouble shoot if the step is still opened.

**Trouble shooting - step by step:**
* Ask the user to keep the step opened for you to trouble shoot, if possible. (Sometimes they need to continue the step)
* Go to the step to see what EPP was failing. The name of the EPP is the label on blue button. In this case: **1. Copy UDFs from AggregateQC - Twist**
* Go to configuration/automation in the web interface and search for the button name. There might be many buttons with the same name. Find the button that is active in the masterstep tht you are debugging. 
* The issue can be in how the script has been configured (the "command line" text box), it can be some bug in the script, or it can be that the script is expecting the artifacts/process/samples/containers or whatever has some fields or features that are not in place. 
* One way to debug is to run the script from command line. ssh into productuoin as described above and run the script with the same argument that are given in the "command line" text box. The process id {processLuid} is allmost allways asked for. 


`{processLuid} = <prefix>-<the last section of the url of the step>` 

In this case: 24-144356. 
  
Prefixes:

24- for configured processes

122- for pooling processes

151- for indexing/reagent tag processes

```
cd /home/glsai/opt/cg_lims/EPPs/
python copyUDFs_from_aggregateQC.py -p '24-144356' -l testlog -u 'Concentration' 'Amount (ng)' -q 'Aggregate QC (DNA) TWIST v1'
```


### Scripts developt by Illumina
In our Clinical Genomics lims system we are also using a fiew scripts that are developed and maintained by Illumina.
Programs written and maintained by Illumina are located in

Java scripts:
`/opt/gls/clarity/extensions/ngs-common/`

Python scripts:
`/opt/gls/clarity/customextensions`

Don't thouch these directories. Insted, if a script developed by Illumina is failing, contact them for help support. 


