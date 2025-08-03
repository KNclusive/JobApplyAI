from pydantic import BaseModel, Field
from typing import List, Type
from langchain_community.tools.playwright.utils import aget_current_page
from playwright.async_api import (
    Page as AsyncPage,
    Browser as AsyncBrowser
)
import json
from typing import Literal
from langchain_core.tools import StructuredTool, BaseTool
from resume_parser import Resume
# --------------------------Create Fill text Tool ---------------------------------------------------

class FillTextInput(BaseModel):
    selector: str = Field(description="CSS selector of the element to fill")
    text: str = Field(description="Text to fill into the element")

class Filltext(BaseTool):
    name: str = "fill_element"
    description: str = "Requires {'selector': '<selector-here>', 'text': '<value-here>'}. Fills Text into element."
    async_browser: AsyncBrowser = Field(description="Async browser instance")
    args_schema: Type[BaseModel] = FillTextInput

    def __init__(self, async_browser):
        super().__init__(async_browser = async_browser)

    def _run(self, selector: str, text: str) -> str:
        raise NotImplementedError("Synchronous run is not supported for this tool.")

    async def _arun(self, selector: str, text: str) -> str:
        """Use the tool."""
        if self.async_browser is None:
            raise ValueError(f"Asynchronous browser not provided to {self.name}")
        page = await aget_current_page(self.async_browser)

        try:
            await page.locator(selector).fill(text)
            return json.dumps({'result': f"Filled element {selector} with text {text}"}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'result': f"Exception occred: {e}"}, ensure_ascii=False)

# --------------------------Create Get All Elements---------------------------------------------------

class GetAllElementsInput(BaseModel):
    pass  # No fields

async def _aget_elements(page: AsyncPage, selector: str, attributes: List[str]) -> List[dict]:
    """Get elements matching the given CSS selector."""
    elements = await page.query_selector_all(selector)
    results = []

    for element in elements:
        tag = await (await element.get_property('tagName')).json_value()
        tag = tag.lower() if tag else ""
        visible = await element.is_visible()
        interactable = await element.is_enabled()

        # Generate CSS selector
        selector_str = await element.evaluate("""
            el => {
                if (el.id) return `#${el.id}`;
                let selector = el.tagName.toLowerCase();
                if (el.className) {
                    selector += '.' + el.className.trim().replace(/\s+/g, '.');
                }
                return selector;
            }
        """)

        attr_list = {attr: await element.get_attribute(attr) for attr in attributes}

        # Determine possible actions
        actions = []
        if tag in ["a", "button"]:
            actions.append("click")
        elif tag == "input":
            input_type = await element.get_attribute("type") or "text"
            if input_type in ["text", "email", "number", "password", "search", "tel", "url"]:
                actions.append("fill")
            elif input_type in ["checkbox", "radio"]:
                actions.append("toggle")
        elif tag == "textarea":
            actions.append("fill")
        else:
            actions.append("")


        # ARIA role-based actions
        role = await element.get_attribute("role")
        if role in ["button", "link", "menuitem"] and "click" not in actions:
            actions.append("click")

        # Clear actions if not visible or interactable
        if not visible or not interactable:
            actions = []

        results.append({
            "selector": selector_str,
            "attributes": attr_list,
            "possible_actions": actions
        })
    return results


class GetAllElements(BaseTool):
    name: str = "get_all_elements"
    description: str = "Requires {''}. Returns Title elements summary for the current page."
    async_browser: AsyncBrowser = Field(description="Async browser instance")
    args_schema: Type[BaseModel] = GetAllElementsInput
    selector:str = (
            "input[type=text]:not([role=combobox]):not([aria-autocomplete=list]):not([aria-autocomplete=both]),"
            "input[type=email],"
            "input[type=tel],"
            "input[type=password],"
            "input[type=number],"
            "input[type=url],"
            "input[type=search],"
            "textarea,"
            "button")
    attributes: List[str] = ['id', 'aria-label', 'type', 'maxlength']

    def __init__(self, async_browser):
        super().__init__(async_browser=async_browser)

    def _run(self) -> str:
        raise NotImplementedError("Synchronous run is not supported for this tool.")

    async def _arun(self) -> str:
        """Use the tool."""
        if self.async_browser is None:
            raise ValueError(f"Asynchronous browser not provided to {self.name}")
        page = await aget_current_page(self.async_browser)
        title = await page.title()
        # Navigate to the desired webpage before using this tool
        results = await _aget_elements(page, self.selector, self.attributes)
        return json.dumps({'result': {'Page Title': title, 'Page Elements Summary': results}}, ensure_ascii=False)
    
# --------------------------Create Resume Tool---------------------------------------------------

class Query_ResumeInput(BaseModel):
    query: Literal["experience", "education", "personal details", "certificates", "research", "skills", "objective", "login"]

def load_resume(resume_path:str):
    # Load Resume from file
    with open(resume_path, "r") as f:
        json_resume = f.read()

    resume = Resume.read_json(json_resume)
    return resume

class Query_Resume(BaseTool):
    name: str = "query_resume"
    description: str = "Requires {'query': '<query-here>'}. Valid query values are experience | education | personal details | certificates | research | skills | objective | login"
    args_schema: Type[BaseModel] = Query_ResumeInput
    resume: Resume

    def __init__(self, resume:Resume):
        super().__init__(resume = resume)

    def _run(self, query: str) -> str:
        raise NotImplementedError("Synchronous run is not supported for this tool.")

    async def _arun(self, query: str) -> str:
        """Use the tool."""
        try:
            return json.dumps({'result': self.resume.query_resume(query)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'result': f"Exception occred: {e}"}, ensure_ascii=False)
