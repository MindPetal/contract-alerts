"""
    Tests for search.py 
"""

from datetime import date

import pytest

import client
import search


@pytest.fixture
def api_client():
    api_config = search.client.Configuration()
    api_config.host = "https://www.example.com"

    return client.ApiClient(api_config)


def test_get_value(mocker):
    mock_item = mocker.MagicMock()
    mock_locator = mocker.MagicMock()
    mock_item.nth.return_value.locator.return_value = mock_locator
    mock_locator.inner_text.return_value = " Test Value "

    result = search.get_value(mock_item)
    assert result == "Test Value"


def test_build_textblock():
    assert {
        "type": "TextBlock",
        "text": "Test",
        "wrap": True,
    } == search.build_textblock("Test")


def test_format_results():
    raw_results = [
        {
            "index": 1,
            "contract_no": "123456789",
            "contract_nm": "Test Contract Name",
            "contract_details": [
                {
                    "date": "02/25/2024",
                    "company": "Test Company",
                    "company_url": "https://example.com",
                    "reason": "Exercise An Option",
                    "obligation": "$50",
                    "desc": "This exercises option year.",
                }
            ],
            "url": "https://example.com",
        },
        {
            "index": 2,
            "naics": "541512",
            "agency": "Test Agency",
            "contract_details": [
                {
                    "date": "02/25/2024",
                    "company": "Test Company",
                    "company_url": "https://example.com",
                    "reason": "Exercise An Option",
                    "obligation": "$50",
                    "desc": "This exercises option year.",
                }
            ],
            "url": "https://example.com",
        },
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** Contract updates.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**1. Test Contract Name -** 123456789 - [View updates](https://example.com)\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**2. All of NAICS 541512 - Test Agency - [View updates](https://example.com)**\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    assert items == search.format_results(raw_results)


def test_process_search_contract_naics_results(mocker):
    contract_list = "123456789: Test Contract Name"
    naics_list = "541512:Test+Agency"
    contract_details = [
        {
            "date": "02/25/2024",
            "company": "Test Company",
            "company_url": "https://example.com",
            "reason": "Exercise An Option",
            "obligation": "$50",
            "desc": "This exercises option year.",
        }
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** Contract updates.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**1. Test Contract Name -** 123456789 - [View updates](https://example.com)\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**2. All of NAICS 541512 - Test Agency - [View updates](https://example.com)**\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    mocker.patch(
        "search.search", return_value=(contract_details, "https://example.com")
    )
    assert items == search.process_search(contract_list, naics_list)


def test_process_search_contract_results(mocker):
    contract_list = "123456789: Test Contract Name"
    naics_list = ""
    contract_details = [
        {
            "date": "02/25/2024",
            "company": "Test Company",
            "company_url": "https://example.com",
            "reason": "Exercise An Option",
            "obligation": "$50",
            "desc": "This exercises option year.",
        }
    ]

    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** Contract updates.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**1. Test Contract Name -** 123456789 - [View updates](https://example.com)\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    mocker.patch(
        "search.search", return_value=(contract_details, "https://example.com")
    )
    assert items == search.process_search(contract_list, naics_list)


def test_process_search_zero(mocker):
    contract_list = "123456789: Test Contract Name,098765432: Test Contract Name 2"
    naics_list = "541512:Test+Agency,541511:Test+Agency+2"
    contract_details = []

    mocker.patch(
        "search.search", return_value=(contract_details, "https://example.com")
    )
    assert [] == search.process_search(contract_list, naics_list)


def test_teams_post(mocker):
    items = [
        {
            "type": "TextBlock",
            "text": f'**{date.today().strftime("%A, %m/%d/%Y")}.** Contract updates.',
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**1. Test Contract Name -** 123456789 - [View updates](https://example.com)\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "**2. All of NAICS 541512 - Agency Name - [View updates](https://example.com)**\n\n- **Date Signed:** 02/25/2024 | **Company:** [Test Company](https://example.com) | **Reason:** Exercise An Option | **Obligation:** $50 | **Description:** This exercises option year.",
            "wrap": True,
        },
        {
            "type": "TextBlock",
            "text": "",
            "wrap": True,
        },
    ]

    body = {
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
    mock_teams_post = mocker.patch("search.client.MsApi.teams_post")
    search.teams_post(api_client, items)
    mock_teams_post.assert_called_once_with(body=body)
