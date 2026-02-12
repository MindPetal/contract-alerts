# ARCHIVED -- FPDS contract search and post to MS Teams
[![contract-alerts-build](https://github.com/MindPetal/contract-alerts/actions/workflows/contract-alerts-build.yaml/badge.svg)](https://github.com/MindPetal/contract-alerts/actions/workflows/contract-alerts-build.yaml) [![contract-alerts-run](https://github.com/MindPetal/contract-alerts/actions/workflows/contract-alerts-run.yaml/badge.svg)](https://github.com/MindPetal/contract-alerts/actions/workflows/contract-alerts-run.yaml)

**This repo has been archived and replaced by https://github.com/MindPetal/sam-contract-alerts**

Python client to scrape government contracts updates from the FPDS website for the prior day.

The [Contract-Alerts-Run](https://github.com/MindPetal/contract-alerts/actions/workflows/contract-alerts-run.yaml) workflow pulls contract updates for specified contracts, NAICS/agencies each day and posts to a designated MS Teams channel. To run this you must obtain and configure as actions repo secrets:
- CONTRACT_LIST: A comma separated string of contract numbers and contract names
```
   123456789:My Contract,098765432:Your Contract
```
- NAICS_LIST: A comma separated string on NAICS, agency names and abbr
```
   541512:THE+AGENCY+NAME:ABBR
```
- MS_URL: MS Teams webhook URL for your organization.

More info on setting up Teams webhooks: [Create incoming webhooks with Workflows for Microsoft Teams](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498)


## Local execution:

- Python 3.13+ required.
- Install:

```sh
pip3 install . --use-pep517
```

- Tests:

```sh
pytest test_search.py
```

- Execute: pass contract list, naics list, ms teams webhook url:

```sh
python3 search.py my-contract-list my-naics-list my-ms-webhook-url
```
