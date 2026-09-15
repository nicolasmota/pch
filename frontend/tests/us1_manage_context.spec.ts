import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.e2e
@pytest.mark.skip(reason="Playwright e2e requires a running app; covered by API journeys")
def test_us1_placeholder():
    assert True
