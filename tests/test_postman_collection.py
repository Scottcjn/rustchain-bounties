# SPDX-License-Identifier: MIT
"""
Tests for the RustChain API Postman collection.

Validates that docs/rustchain-api.postman_collection.json is a well-formed
Postman v2.1 collection covering every documented endpoint.

Run: python -m pytest tests/test_postman_collection.py -v
"""

import json
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COLLECTION_PATH = os.path.join(
    REPO_ROOT, "docs", "rustchain-api.postman_collection.json"
)

# Every endpoint listed in docs/API_REFERENCE.md and docs/protocol/API_SPEC.md
EXPECTED_ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/epoch"),
    ("GET", "/api/miners"),
    ("GET", "/wallet/balance"),
    ("POST", "/attest/challenge"),
    ("POST", "/attest/submit"),
    ("POST", "/epoch/enroll"),
    ("GET", "/lottery/eligibility"),
    ("GET", "/explorer"),
]


def _load_collection():
    with open(COLLECTION_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _collect_requests(items, acc=None):
    """Recursively walk the item tree and return (method, path) tuples."""
    if acc is None:
        acc = []
    for item in items:
        if "item" in item:
            _collect_requests(item["item"], acc)
        if "request" in item:
            req = item["request"]
            method = req["method"]
            url = req["url"]
            # Rebuild path from the url.path list
            path = "/" + "/".join(url.get("path", []))
            acc.append((method, path))
    return acc


# ---------------------------------------------------------------------------
# Structure tests
# ---------------------------------------------------------------------------


class TestCollectionStructure:
    """Verify the collection file exists and uses the correct schema."""

    def test_file_exists(self):
        assert os.path.isfile(COLLECTION_PATH), (
            f"Postman collection not found at {COLLECTION_PATH}"
        )

    def test_valid_json(self):
        data = _load_collection()
        assert isinstance(data, dict)

    def test_schema_version(self):
        data = _load_collection()
        schema = data.get("info", {}).get("schema", "")
        assert "collection/v2.1.0" in schema, (
            "Collection must use Postman schema v2.1"
        )

    def test_has_name(self):
        data = _load_collection()
        name = data.get("info", {}).get("name", "")
        assert name, "Collection must have a name"

    def test_has_description(self):
        data = _load_collection()
        desc = data.get("info", {}).get("description", "")
        assert desc, "Collection must have a description"


# ---------------------------------------------------------------------------
# Variable tests
# ---------------------------------------------------------------------------


class TestCollectionVariables:
    """Verify collection-level variables are defined."""

    def test_base_url_variable(self):
        data = _load_collection()
        variables = {v["key"]: v for v in data.get("variable", [])}
        assert "baseUrl" in variables, "Collection must define a baseUrl variable"
        assert "50.28.86.131" in variables["baseUrl"]["value"]

    def test_miner_id_variable(self):
        data = _load_collection()
        variables = {v["key"]: v for v in data.get("variable", [])}
        assert "minerId" in variables, (
            "Collection must define a minerId variable"
        )
        assert variables["minerId"]["value"], "minerId must have a default value"


# ---------------------------------------------------------------------------
# Endpoint coverage tests
# ---------------------------------------------------------------------------


class TestEndpointCoverage:
    """Every documented API endpoint must appear in the collection."""

    def test_all_endpoints_present(self):
        data = _load_collection()
        found = _collect_requests(data.get("item", []))
        for method, path in EXPECTED_ENDPOINTS:
            assert (method, path) in found, (
                f"Missing endpoint: {method} {path}"
            )

    def test_no_empty_folders(self):
        """Top-level folders must each contain at least one request."""
        data = _load_collection()
        for folder in data.get("item", []):
            if "item" in folder:
                reqs = _collect_requests(folder["item"])
                assert len(reqs) > 0, (
                    f"Folder '{folder.get('name', '?')}' has no requests"
                )


# ---------------------------------------------------------------------------
# Request quality tests
# ---------------------------------------------------------------------------


class TestRequestQuality:
    """Each request should have a description, use variables, and include
    at least one example response."""

    def _all_requests(self):
        data = _load_collection()
        items = []

        def _walk(node):
            for item in node:
                if "item" in item:
                    _walk(item["item"])
                if "request" in item:
                    items.append(item)

        _walk(data.get("item", []))
        return items

    def test_every_request_has_description(self):
        for item in self._all_requests():
            desc = item["request"].get("description", "")
            assert desc, (
                f"Request '{item.get('name', '?')}' is missing a description"
            )

    def test_every_request_uses_base_url_variable(self):
        for item in self._all_requests():
            raw = item["request"]["url"].get("raw", "")
            assert "{{baseUrl}}" in raw, (
                f"Request '{item.get('name', '?')}' should use "
                "the {{baseUrl}} variable"
            )

    def test_every_request_has_example_response(self):
        for item in self._all_requests():
            responses = item.get("response", [])
            assert len(responses) >= 1, (
                f"Request '{item.get('name', '?')}' needs at least "
                "one example response"
            )

    def test_post_requests_have_body(self):
        for item in self._all_requests():
            req = item["request"]
            if req["method"] == "POST":
                body = req.get("body", {})
                assert body.get("raw"), (
                    f"POST request '{item.get('name', '?')}' must include "
                    "an example body"
                )

    def test_post_requests_have_content_type_header(self):
        for item in self._all_requests():
            req = item["request"]
            if req["method"] == "POST":
                headers = {
                    h["key"].lower(): h["value"]
                    for h in req.get("header", [])
                }
                assert "content-type" in headers, (
                    f"POST request '{item.get('name', '?')}' must set "
                    "Content-Type header"
                )


# ---------------------------------------------------------------------------
# Example response quality tests
# ---------------------------------------------------------------------------


class TestExampleResponses:
    """Example responses should be valid JSON where applicable."""

    def _all_responses(self):
        data = _load_collection()
        items = []

        def _walk(node):
            for item in node:
                if "item" in item:
                    _walk(item["item"])
                if "request" in item:
                    for resp in item.get("response", []):
                        items.append(
                            (item.get("name", "?"), resp)
                        )

        _walk(data.get("item", []))
        return items

    def test_json_responses_parse(self):
        for req_name, resp in self._all_responses():
            if resp.get("_postman_previewlanguage") == "json":
                body = resp.get("body", "")
                if body:
                    try:
                        json.loads(body)
                    except json.JSONDecodeError:
                        raise AssertionError(
                            f"Response '{resp.get('name', '?')}' in "
                            f"'{req_name}' has invalid JSON body"
                        )

    def test_responses_have_status_code(self):
        for req_name, resp in self._all_responses():
            assert "code" in resp, (
                f"Response '{resp.get('name', '?')}' in '{req_name}' "
                "is missing a status code"
            )
