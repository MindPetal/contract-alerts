"""
    Script executes via github actions to scrape contract updates
    from fpds and post results to MS Teams. 
"""

import logging
import sys
from datetime import date, datetime, timedelta

from playwright.sync_api import Locator, sync_playwright
import client
from client.rest import ApiException
import time


log = logging.getLogger("search")
logging.basicConfig(level=logging.INFO)


def get_value(item: Locator) -> str:
    # Extract value
    return item.nth(0).locator("xpath=following-sibling::td[1]").inner_text().strip()


def search(criteria: dict, yday: str) -> tuple[list[dict], str]:
    # Execute fpds search

    base_url = "https://www.fpds.gov/ezsearch/fpdsportal?q="

    if "contract_no" in criteria:
        contract_no = criteria["contract_no"]
        url = f"{base_url}{contract_no}%20%20SIGNED_DATE%3A%5B{yday}%2C%29&templateName=1.5.3&indexName=awardfull&sortBy=SIGNED_DATE&desc=Y"
    elif "naics" in criteria:
        naics = criteria["naics"]
        agency = criteria["agency"]
        url = f"{base_url}CONTRACTING_AGENCY_NAME%3A%22{agency}%22+PRINCIPAL_NAICS_CODE%3A%22{naics}%22++SIGNED_DATE%3A%5B{yday}%2C%29&templateName=1.5.3&indexName=awardfull&sortBy=SIGNED_DATE&desc=Y"

    contract_details = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(60000)
        page.goto(url)
        tables = page.locator('table[class^="resultbox"]')
        count = tables.count()

        if count > 0:
            # Updates found

            for i in range(count):
                contract_info = {}
                table = tables.nth(i)

                # Extract data from table
                contract_info["date"] = get_value(
                    table.locator('td:has(span:has-text("Date Signed:"))')
                )
                company = get_value(
                    table.locator('td:has(span:has-text("Legal Business Name:"))')
                )
                contract_info["company"] = company
                company_url_encoded = company.replace(" ", "%20")
                contract_info["company_url"] = (
                    f"{base_url}UEI_NAME%3A%22{company_url_encoded}%22&templateName=1.5.3&indexName=awardfull&sortBy=SIGNED_DATE&desc=Y"
                )
                contract_info["obligation"] = get_value(
                    table.locator('td:has(span:has-text("Action Obligation:"))')
                )

                # Go to View hyperlink
                view_link = table.locator('a:has-text("(View)")')

                with page.context.expect_page(timeout=60000) as new_page_info:
                    view_link.nth(0).click()

                new_page = new_page_info.value
                new_page.wait_for_load_state("load", timeout=60000)

                contract_info["reason"] = new_page.locator(
                    'input[name="reasonForModification"]'
                ).input_value()

                contract_info["desc"] = new_page.locator(
                    "textarea#descriptionOfContractRequirement"
                ).input_value()

                contract_details.append(contract_info)

        browser.close()

        return contract_details, url


def build_textblock(content: str) -> dict:
    # Build TextBlock for MS Teams
    return {"type": "TextBlock", "text": content, "wrap": True}


def format_results(raw_results: list[dict]) -> list:
    # Format results strings

    items = []

    if raw_results:
        header = f'**{date.today().strftime("%A, %m/%d/%Y")}.** Contract updates.'
        items += [build_textblock(header), build_textblock("")]

        for result in raw_results:

            if "contract_no" in result:
                content = f'**{result["index"]}. {result["contract_nm"]} -** {result["contract_no"]} - [View updates]({result["url"]})'
            elif "naics" in result:
                agency = result["agency"]
                content = f'**{result["index"]}. All of NAICS {result["naics"]} - {agency} - [View updates]({result["url"]})**'

            for detail in result["contract_details"]:
                desc = detail["desc"].replace("\n", " ")
                content += f'\n\n- **Date Signed:** {detail["date"]} | **Company:** [{detail["company"]}]({detail["company_url"]}) | **Reason:** {detail["reason"]} | **Obligation:** {detail["obligation"]} | **Description:** {desc}'

            items += [build_textblock(content), build_textblock("")]

    return items


def process_search(contract_list: str, naics_list: str) -> list:
    # Prepare fpds search and format results
    contract_pairs = []
    naics_triplets = []
    raw_results = []
    yday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")

    if contract_list:
        contract_pairs = contract_list.split(",")

    if naics_list:
        naics_triplets = naics_list.split(",")

    for pair in contract_pairs:
        log.info("Processing contract number search")

        contract_no, contract_nm = pair.split(":", 1)
        contract_no = contract_no.strip()
        contract_nm = contract_nm.strip()
        contract_details, url = search({"contract_no": contract_no}, yday)

        if contract_details:
            raw_results.append(
                {
                    "contract_no": contract_no,
                    "contract_nm": contract_nm,
                    "contract_details": contract_details,
                    "url": url,
                }
            )

        time.sleep(5)

    for triplet in naics_triplets:
        log.info("Processing NAICS search")

        naics, agency, abbr = triplet.split(":")
        naics = naics.strip()
        agency = agency.strip()
        abbr = abbr.strip()
        contract_details, url = search({"naics": naics, "agency": agency}, yday)

        if contract_details:
            raw_results.append(
                {
                    "naics": naics,
                    "agency": abbr,
                    "contract_details": contract_details,
                    "url": url,
                }
            )

        time.sleep(5)

    if raw_results:
        # Inject index into results
        n = 1

        for result in raw_results:
            result["index"] = n
            n += 1

    return format_results(raw_results)


def teams_post(api_client: client.ApiClient, items: list[dict]) -> None:
    # Execute MS Teams post
    api_instance = client.MsApi(api_client)

    try:
        api_instance.teams_post(
            body={
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.0",
                            "body": [{"type": "Container", "items": items}],
                            "msteams": {"width": "Full"},
                        },
                    }
                ],
            }
        )

    except ApiException as e:
        log.exception("Exception when calling MsApi->teams_post: %s\n" % e)
        raise


def main(contract_list: str, naics_list: str, ms_webhook_url: str) -> None:
    # Primary processing fuction

    log.info("Start processing")
    contract_results = process_search(contract_list, naics_list)

    if contract_results:
        log.info("Process Teams posts")
        api_config = client.Configuration()
        api_config.host = ms_webhook_url
        api_client = client.ApiClient(api_config)
        teams_post(api_client, contract_results)
    else:
        log.info("No contract updates found")


""" Read in contract_list, naics_list, ms_webhook_url
"""
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
