# Web Search Agent

## Responsibility

Retrieve live market information using DuckDuckGo.

---

## Input

SharedMemory

Contains:

- startup_idea
- keywords

---

## Tasks

1. Read startup idea.
2. Read extracted keywords.
3. Search DuckDuckGo.
4. Return only relevant results.
5. Include title, URL, and snippet.
6. Do not analyze the results.
7. Do not call other agents.

---

## Output

```json
{
    "status": "success",
    "data": {
        "search_results": [
            {
                "title": "",
                "url": "",
                "snippet": ""
            }
        ],
        "references": [
            ""
        ]
    },
    "message": ""
}