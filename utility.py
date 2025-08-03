from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_community.tools.playwright import ClickTool, NavigateTool
from create_tools import Query_Resume, Filltext, GetAllElements
from monkey_patch import monkey_patch
from resume_parser import Resume
from typing import Dict, List
import json

import nest_asyncio
nest_asyncio.apply()

def load_browser():
    browser = create_async_playwright_browser(headless=False)
    return browser

def load_resume(resume_path:str):
    # Load Resume from file
    with open(resume_path, "r") as f:
        json_resume = f.read()

    resume = Resume.read_json(json_resume)
    return resume

from typing import Any

async def extract_relevant_info(chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    if 'agent' in chunk:
        messages = chunk['agent'].get('messages', [])
        for msg in messages:
            content = msg.content
            tool_calls = msg.tool_calls
            tool_calls_info = []
            for call in tool_calls:
                tool_calls_info.append({
                    'tool_name': call.get('name', ''),
                    'input': call.get('args', {})
                })
            results.append({
                'type': 'AIMessage',
                'content': content,
                'tool_calls': tool_calls_info
            })

    elif 'tools' in chunk:
        messages = chunk['tools'].get('messages', [])
        for msg in messages:
            content = json.loads(msg.content).get('result', '')
            if msg.name:
                tool_name = msg.name
            else:
                tool_name = 'No_Name'
            results.append({
                'type': 'ToolMessage',
                'content': content,
                'tool_name': tool_name
            })

    else:
        results.append({'content': 'Invlid message type'})

    return results


def generate_tools(resume_path:str):
    monkey_patch()
    async_browser = load_browser()
    resume = load_resume(resume_path=resume_path)

    Click_tool = ClickTool(async_browser=async_browser)
    fillText_tool = Filltext(async_browser=async_browser)
    getAllElements_tool = GetAllElements(async_browser=async_browser)
    query_resume_tool = Query_Resume(resume=resume)
    navigate_tool = NavigateTool(async_browser=async_browser)

    model_tools = [Click_tool, fillText_tool, getAllElements_tool, query_resume_tool, navigate_tool]
    return async_browser, model_tools
