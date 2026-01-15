# Xlsx Parser

Capture all information from a given .xlsx file and store it as RDF "raw data"

## Usage

```bash
python3 -m ekg_lib.xlsx_parser --help
```

```text
usage: python3 -m ekg_lib.xlsx_parser [-h] [--input INPUT] [--output OUTPUT]
  [--key-column-number KEY_COLUMN_NUMBER]
  [--ignored-values [IGNORED_VALUES [IGNORED_VALUES ...]]]
  [--ignored-prefixes [IGNORED_PREFIXES [IGNORED_PREFIXES ...]]]
  [--verbose] [--kgiri-base KGIRI_BASE]
  [--kgiri-prefix KGIRI_PREFIX]
  [--data-source-code DATA_SOURCE_CODE]

Capture all information from the given .xlsx file and store it as RDF "raw
data"

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         The name of the input .xlsx file
  --output OUTPUT       The name of the output RDF file (must be .ttl)
  --key-column-number KEY_COLUMN_NUMBER
                        The 1-based column number containing the "legacy ID"
  --ignored-values [IGNORED_VALUES [IGNORED_VALUES ...]]
                        A list of values to ignore
  --ignored-prefixes [IGNORED_PREFIXES [IGNORED_PREFIXES ...]]
                        A list of prefixes of cell values to ignore
  --verbose, -v         verbose output

KGIRI:
  --kgiri-base KGIRI_BASE
                        A root level URL to be used for all KGIRI types
                        (default is EKG_KGIRI_BASE=https://kg.your-
                        company.kom/)
  --kgiri-prefix KGIRI_PREFIX
                        The prefix to be used to construct KGIRIs
  --kgiri-base-replace KGIRI_BASE_REPLACE
                        The KGIRI base fragment that is to be replaced with the EKG_KGIRI_BASE
                        (default is EKG_KGIRI_BASE_REPLACE=https://placeholder.kg)

Data Source:
  --data-source-code DATA_SOURCE_CODE
                        The code of the dataset (can also be set with env var
                        EKG_DATA_SOURCE_CODE)

Currently only supports turtle.
```

## Links

- [ekg_lib](../../)
- [EKGF](https://ekgf.org)

