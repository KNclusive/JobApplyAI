from langchain_core.callbacks import AsyncCallbackManagerForToolRun
from typing import Optional
import json
from langchain_community.tools.playwright.utils import aget_current_page
from langchain_community.tools.playwright import ClickTool, NavigateTool

async def _custom_click(
    self,
    selector: str,
    run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
) -> str:
    """Use the tool."""
    if self.async_browser is None:
        raise ValueError(f"Asynchronous browser not provided to {self.name}")

    page = await aget_current_page(self.async_browser)
    # Navigate to the desired webpage before using this tool
    # selector_effective = self._selector_effective(selector=selector)
    from playwright.async_api import TimeoutError as PlaywrightTimeoutError

    try:
        await page.wait_for_selector(selector, state='visible', timeout=10000)
        await page.click(
            selector
            # strict=self.playwright_strict,
            # timeout=self.playwright_timeout,
        )
        return json.dumps({'result': f"Clicked element '{selector}'"}, ensure_ascii=False)
    except PlaywrightTimeoutError:
        return json.dumps({'result': f"Unable to click on element '{selector}'"}, ensure_ascii=False)

async def _modified_navigate(
    self,
    url: str,
    run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
) -> str:
    """Use the tool."""
    if self.async_browser is None:
        raise ValueError(f"Asynchronous browser not provided to {self.name}")
    page = await aget_current_page(self.async_browser)
    response = await page.goto(url)
    status = response.status if response else "unknown"
    if 200 == status:
        return json.dumps({'result': f"Navigating successfull."})
    else:
        return json.dumps({'result': f"Navigation to {url} unsuccessfull. Status: {status}"})

def monkey_patch():
    global ClickTool, NavigateTool
    ClickTool._arun = _custom_click
    NavigateTool._arun = _modified_navigate