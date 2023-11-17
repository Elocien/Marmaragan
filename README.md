# Marmaragan
Diplom Thesis by Lucian McIntyre

## Description
Marmaragan attempts to leverage the power of LLM's to generate verifiable programs for the SPARK2014 subset of ADA.


## Installation

### Set Environment Variable for OpenAPI Key

Either export for current session or add to shell config (.bashrc, .zshrc, etc.)   
```export OPENAI_API_KEY=<OpenAPI-Key>```


 ### Install requirements.txt

```pip install requirements.txt```


### Alire working directory with a spark project

Have an initialised Alire working directory with a spark project. Make sure ```alr gnatprove``` runs in this directory  

An example project is included, under ```spark_projects/spark-by-example```, initialised with an Alire config. The original project can be found here: [spark-by-example](https://github.com/tofgarion/spark-by-example)


### Set parameters in ```main.py``` file. 

Set the paths for the alire directory, as well as setting the prompt and which files to generate annotations for


## Notes

### Source File in main.py
The source_file param in main.py should likely be a copy of the destination_file from the spark directory, with a given annotation removed and a possible comment giving the position and name of the annotation to be generated

### Alire
Documentation: https://alire.ada.dev/docs/



