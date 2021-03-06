# Pigeon

## Introduction
Tool for pipeing inputs and outputs of multiple cli tools.
Pigeon takes in only a config file as input. Everything required to run the pipeline are specified in config file. The config file is specified according to [python configparser](https://docs.python.org/3.4/library/configparser.html).

## Quick Install
#### Linux&Mac  

> sudo pip3 install --index-url https://test.pypi.org/simple/ pigeon

#### Windows  
  
> pip install --index-url https://test.pypi.org/simple/ pigeon

## Resources for NGS
None of the tools or data files are supplemented by pigeon so they need to be downloaded.
For example configuration file, exome sequencing pipeline,

* Tools
    + [FastQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
    + [BWA](https://github.com/lh3/bwa)
    + [Picard](https://broadinstitute.github.io/picard/)
    + [GATK](https://software.broadinstitute.org/gatk/)
    + [Annotation Tool](https://test.pypi.org/project/dove/)
* Reference Files
    + [Reference genome and known SNP&INDELS](https://software.broadinstitute.org/gatk/download/bundle)
        * hg19 or
        * hg38
    + Bed file
        * See website of capture kit used in sequencing

## How to use
Create yourself a configuration file

> pigeon createconfig

Modify for your analysis. (See below.)

> pigeon -c my_config.conf -d

If everything looks alright run for real.

> pigeon -c my_config.conf

## Config File

Config file consists of three parts.

* General
* Pipeline
* Individual tool blocks

## General
Area used to define project name, output directory, input files, and resource files like reference genome or target file. Following variables are necessary for run.

Required:

* project_name : name of your project
* output_dir : where to write output files
* input_files : input files for analysis, space separated, pairs should be next to each other. e.g.

  > input_files = A.txt B.txt C.txt  

  or for paired 

  > input_files = A1.txt A2.txt B1.txt B2.txt C1.txt C2.txt

Optional variable can also be decleared here. Based on your or tool requirements. Later these variables can be called in the config file using ${GENERAL:optional_variable}.

Optional(example): 

> reference_genome = /path/to/my/reference_genome.fa

> bed_file = /path/to/my/target.bed

> known_snp = /path/to/my/snp.vcf

> my_database = /path/to/my/favorite.db

## Pipeline
This area should contain paths to tools that is understanble by your shell. As well as the run order of tools. e.g.

> pipeline = job1 job2 job3

> A = path/to/A

> B = path/to/B

> C = path/to/C

## Tool Blocks
Name of the block should be same as in **pipeline**. By continuing example above;

> [job1]

> [job2]

> [job3]

Arguments that can be used in these blocks as follows:

#### Run Args

* tool: tool variable from pipeline block. e.g.

  > tool = ${PIPELINE:A}

* sub_tool: if tool has a sub tool like 'bwa mem'. e.g.

  > sub_tool = mem

* args: arguments of the tools
* java: if tool is a jar file add java -jar before it.
* pass: if True it won't run the block. But the block still be part of the pipeline. This option is helpful for resuming interrupted pipeline.

#### Input Args
* input_from: Name of the block that that's output is this jobs input. First jobs input_from should be input_files.
* input_multi: can be 'paired' or 'all'. Paired option splits input files stream into groups of two. All option uses all of the input files.
* input_flag_repeat: If tool requires input flag for each input this command will add given flag before each input.

* secondary_in_placeholder

#### Output Args

* suffix: add suffix to output file name
* ext: file extension of the output
* dump_dir: creates a directory and outputs there.

* paired_output: this option will pair the input and the output of the tool.

* secondary_out_placeholder
* secondary_suffix
* secondary_ext
* secondary_dump_dir

#### Placeholders
These are joker words that can be used in **args**. 

* input_placeholder
* secondary_input_placeholder

* output_placeholder
* secondary_output_placeholder

### Example Config

> [[GENERAL]]  
> project_name = my_project  
> output_dir = /path/to/output_directory  
> input_files = A.txt B.txt C.txt  
> my_db = /path/to/my.db  
  
> [[PIPELINE]]  
> pipeline = job1 job2 job3  
> A = /path/to/A  
> B = /path/to/B  
> C = /path/to/C  
  
> [job1]  
> tool = A  
> input_from = input_files  
> args = -i input_placeholder -o output_placeholder  
> suffix = job1_A  
> ext = txt  
  
> [job2]  
> tool = B  
> input_from = job1  
> args = -i input_placeholder -o output_placeholder  
> suffix = job2_B  
> ext = txt  
  
> [job3]  
> tool = C  
> input_from = job2  
> args = -i input_placeholder -o output_placeholder  
> suffix = job3_C  
> ext = txt  

