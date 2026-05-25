"""JIRA API client for reading issues and posting comments."""

import os
import requests
from typing import Any, Dict, List
from dotenv import load_dotenv
load_dotenv()



class JiraClient:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL", "").strip().rstrip("/")
        self.email = os.getenv("JIRA_USER_EMAIL", "").strip()
        self.api_token = os.getenv("JIRA_API_TOKEN", "").strip()
        if not all([self.base_url, self.email, self.api_token]):
            raise ValueError(
                "JIRA_BASE_URL, JIRA_USER_EMAIL, and JIRA_API_TOKEN environment variables must be set"
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
        entities: List[str],
        features: List[str],
        issue_key: str,
    ) -> Dict[str, Any]:
        """Build an ADF document body for the generation summary comment."""
        entity_text = ", ".join(entities) if entities else "None detected"
        feature_text = ", ".join(features) if features else "None detected"

        return {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "heading",
                    "attrs": {"level": 3},
                    "content": [{"type": "text", "text": "Spring Boot Project Generated"}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": "Project "},
                        {
                            "type": "text",
                            "text": project_name,
                            "marks": [{"type": "strong"}],
                        },
                        {
                            "type": "text",
                            "text": f" was successfully generated from issue {issue_key}.",
                        },
                    ],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 4},
                    "content": [{"type": "text", "text": "Generated Entities"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": entity_text}],
                },
                {
                    "type": "heading",
                    "attrs": {"level": 4},
                    "content": [{"type": "text", "text": "Detected Features"}],
                },
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": feature_text}],
                },
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "Generated by AI Code Starter via MCP pipeline.",
                            "marks": [{"type": "em"}],
                        }
                    ],
                },
            ],
        }
