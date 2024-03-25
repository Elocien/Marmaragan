# Marmaragan
Diplom Thesis by Lucian McIntyre

## Description
Marmaragan attempts to leverage the power of LLM's to generate annotations for verifiable programs, for the SPARK2014 subset of ADA.


## Installation

### Set Environment Variable for OpenAPI Key

Save to .env file and load or or add to shell path through .bashrc, .zshrc, etc. by adding the line:
```export OPENAI_API_KEY=<OpenAPI-Key>```

### Set Environment Variable for Gnatprove path
Save to .env file and load or or add to shell path through .bashrc, .zshrc, etc. by adding the line:
```export GNATPROVE_EXECUTABLE_PATH="/path/to/.../Gnat/bin/gnatprove"```

 ### Install requirements.txt

```pip install -r requirements.txt```


## Run Application
Set appropriate variables in ```main.py```

Run ```python main.py``` and view results in benchmark log file








