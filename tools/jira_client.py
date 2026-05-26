"""JIRA API client for reading issues and posting comments."""

import os
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv
load_dotenv()



class JiraClient:
    def __init__(
        self,
        base_url: str = None,
        email: str = None,
        api_token: str = None,
    ):
        self.base_url = (base_url or os.getenv("JIRA_BASE_URL", "")).strip().rstrip("/")
        self.email = (email or os.getenv("JIRA_USER_EMAIL", "")).strip()
        self.api_token = (api_token or os.getenv("JIRA_API_TOKEN", "")).strip()
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError(
                "JIRA credentials must be provided via the UI or set as environment variables "
                "(JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN)"
            )
        self.auth = (self.email, self.api_token)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        response = requests.get(url, auth=self.auth, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_project(self, project_key: str) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/project/{project_key}"
        response = requests.get(url, auth=self.auth, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def search_issues(self, jql: str, max_results: int = 20) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,description,issuetype,status,priority,labels",
        }
        response = requests.get(
            url, auth=self.auth, headers=self.headers, params=params, timeout=30
        )
        response.raise_for_status()
        return response.json().get("issues", [])

    def add_comment(self, issue_key: str, adf_body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        response = requests.post(
            url, auth=self.auth, headers=self.headers, json={"body": adf_body}, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def extract_text_from_issue(self, issue: Dict[str, Any]) -> str:
        """Convert a JIRA issue into a plain-text requirements document."""
        fields = issue.get("fields", {})
        parts = []

        summary = fields.get("summary", "")
        if summary:
            parts.append(f"# {summary}")

        issue_type = fields.get("issuetype", {}).get("name", "")
        if issue_type:
            parts.append(f"Issue Type: {issue_type}")

        description = fields.get("description")
        if description:
            desc_text = self._extract_adf_text(description).strip()
            if desc_text:
                parts.append(f"## Description\n{desc_text}")

        labels = fields.get("labels", [])
        if labels:
            parts.append(f"Labels: {', '.join(labels)}")

        return "\n\n".join(parts)

    def _extract_adf_text(self, node: Any) -> str:
        """Recursively extract plain text from an Atlassian Document Format node."""
        if node is None:
            return ""
        if isinstance(node, str):
            return node
        if isinstance(node, list):
            # Top-level list of block nodes — join with newlines
            return "\n".join(self._extract_adf_text(item) for item in node)
        if not isinstance(node, dict):
            return str(node)

        node_type = node.get("type", "")
        content = node.get("content", [])

        if node_type == "text":
            return node.get("text", "")
        if node_type == "hardBreak":
            return "\n"
        if node_type in ("paragraph", "heading"):
            # Inline content — join without separator, then add trailing newline
            return "".join(self._extract_adf_text(c) for c in content) + "\n"
        if node_type == "bulletList":
            items = []
            for item in content:
                # Each item is a listItem node whose content is paragraphs
                item_text = "".join(
                    self._extract_adf_text(c) for c in item.get("content", [])
                ).strip()
                items.append(f"- {item_text}")
            return "\n".join(items) + "\n"
        if node_type == "orderedList":
            items = []
            for i, item in enumerate(content, 1):
                item_text = "".join(
                    self._extract_adf_text(c) for c in item.get("content", [])
                ).strip()
                items.append(f"{i}. {item_text}")
            return "\n".join(items) + "\n"
        if node_type == "codeBlock":
            inner = "".join(self._extract_adf_text(c) for c in content)
            return f"```\n{inner}\n```\n"

        # doc, blockquote, listItem, tableCell, etc. — recurse into content
        return "".join(self._extract_adf_text(c) for c in content)

    @staticmethod
    def build_comment_adf(
        project_name: str,
        entities: List[Dict[str, Any]],
        issue_key: str,
        issue_summary: str = "",
        all_issue_keys: List[str] = None,
        llm_summary: str = "",
    ) -> Dict[str, Any]:
        """Build an ADF document body for the generation summary comment.

        entities: list of dicts with keys 'name' and 'operations' (list of operation dicts).
        all_issue_keys: full list of issue keys when multiple tickets were used together.
        llm_summary: LLM-generated contextual description of what was built for this ticket.
        """
        # Multi-ticket note
        other_keys = [k for k in (all_issue_keys or []) if k != issue_key]
        multi_note = f" alongside {', '.join(other_keys)}" if other_keys else ""

        # Entity bullet list
        entity_items = []
        for e in entities:
            name = e.get("name", "Unknown")
            ops = e.get("operations", [])
            op_types = [o.get("type", "") for o in ops if o.get("type")]
            op_str = f" — {', '.join(op_types)}" if op_types else ""
            entity_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": f"{name}{op_str}"}],
                }],
            })
        if not entity_items:
            entity_items = [{
                "type": "listItem",
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": "No entities detected"}]}],
            }]

        content = [
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "Spring Boot Code Generated"}],
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Project "},
                    {"type": "text", "text": project_name, "marks": [{"type": "strong"}]},
                    {"type": "text", "text": f" was generated from this ticket{multi_note}."},
                ],
            },
        ]

        # LLM-generated contextual summary — the main intelligent section
        if llm_summary:
            content.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": llm_summary}],
            })

        content += [
            {
                "type": "heading",
                "attrs": {"level": 4},
                "content": [{"type": "text", "text": "Entities & Operations"}],
            },
            {
                "type": "bulletList",
                "content": entity_items,
            },
            {
                "type": "paragraph",
                "content": [{
                    "type": "text",
                    "text": "Generated by AI Code Starter via MCP pipeline.",
                    "marks": [{"type": "em"}],
                }],
            },
        ]

        return {"type": "doc", "version": 1, "content": content}
