# Bifaces Database Bulk Downloader

This repository contains a Python scraper for retrieving metadata and associated images from the Archaeology Data Service (ADS) collection *Lower Palaeolithic technology, raw material and population ecology (bifaces)*.

The source collection is:

> Marshall, G., Dupplaw, D., Roe, D. and Gamble, C. (2002). *Lower Palaeolithic technology, raw material and population ecology (bifaces).* Archaeology Data Service. https://doi.org/10.5284/1000354

The ADS collection remains the authoritative source. This repository provides the retrieval code and does not distribute the original ADS image collection.

## What the scraper does

The script iterates over the record identifiers used by the ADS bifaces collection, extracts the record metadata available in the web interface, and downloads the three associated image views when available.

For the case study used in the accompanying research, the workflow retrieved 3,556 artefact records and 10,668 images.

The script includes:

- a fixed delay between requests;
- request timeouts and retry handling;
- periodic CSV output;
- logging of failed record identifiers;
- skipping of image files that already exist locally.

## Requirements

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Running the scraper

Run:

```bash
python ads_biface_database_scraper.py
```

The script writes downloaded images to:

```text
images/
```

and record metadata to:

```text
biface_records_online.csv
```

Logs are written to:

```text
logs/
```

The `images/`, generated CSV and log files are excluded from version control.

## Responsible use

This tool was developed for research use with deliberate throttling rather than unrestricted crawling. Before running automated retrieval, users should review the current ADS Terms of Use and Access and any conditions attached to the source collection:

https://archaeologydataservice.ac.uk/about/policies/use-access-to-data/ads-terms-of-use-and-access/

Repository code and ADS source material have separate reuse conditions. The MIT licence in this repository applies only to the software authored for this project. It does not change the rights or reuse conditions attached to ADS records or images.

## Citation

Citation metadata for this software are provided in `CITATION.cff`. A permanent DOI will be added after the v1.0.0 release is archived with Zenodo.

When using the archaeological source material, cite the original ADS dataset separately:

Marshall, G., Dupplaw, D., Roe, D. and Gamble, C. (2002). *Lower Palaeolithic technology, raw material and population ecology (bifaces).* Archaeology Data Service. https://doi.org/10.5284/1000354

## Related repository

The companion image-processing workflow is available at:

https://github.com/jfpalomeque/hand_axes_image_processing

## Licence

Software in this repository is released under the MIT License. See `LICENSE`.
