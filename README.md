# Marmaragan
Author: Lucian McIntyre

## Description
Marmaragan attempts to leverage the power of LLM's to generate verifiable programs for the SPARK2014 subset of ADA.


## Installation

### Main Components:
- Set Environment Variable for OpenAPI Key

Either export for current session or add to shell config (.bashrc, .zshrc, etc.)
```export OPENAI_API_KEY=<OpenAPI-Key>```


- Install requirements.txt

```pip install requirements.txt```


- Alire working directory with a spark project

Have an initialised alire working directory with a spark project. Make sure ```alr gnatprove``` runs in this directory


- Set parameters in ```main.py``` file. 

Set the paths for the alire directory, as well as setting the prompt and which files to generate annotations for


## Notes





