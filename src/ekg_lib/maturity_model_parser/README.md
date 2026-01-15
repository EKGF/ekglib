# maturity_model_parser

The `maturity_model_parser` generates Markdown files from RDF files
that describe the pillars, levels, capabilities and "KGIs" of the
EKG Maturity Model for [maturity.ekgf.org](https://maturity.ekgf.org).

## Scope

This generator is only used to produce the content for the
["Maturity Model" section](https://maturity.ekgf.org/pillar/) of
the maturity.ekgf.org website. It does not generate other parts
of that site.

## Why is this in ekg_lib?

The primary purpose of including this generator in ekg_lib is to
serve as a test case for the
[maturity model ontology](https://github.com/EKGF/ontology-maturity-model).
By using the ontology to generate real documentation, we can
validate that the ontology structure is correct and complete.

## Status

This work is currently in progress.
