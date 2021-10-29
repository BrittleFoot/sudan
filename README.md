# Sudan | SUper-Duper-ANNnotator

## Installation

```sh
conda create --name sudan -c bioconda -c conda-forge --file requirements_conda.txt
conda activate sudan
pip install .
```

## Run

```
sudan --help
```

## Development

Installation in edit mode
```
pip install -e .  
```
Pytest
```
pip install -r requirements_dev.txt
pytest
```