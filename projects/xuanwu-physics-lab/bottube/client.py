import json
import mimetypes
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

class BoTTubeError(Exception):
    def __init__(self, status_code: int, error: str, detail: Any = None):
        self.status_code = status_code
        self.error = error
        self.detail = detail
        super().__init__(f"[{status_code}] {error}")

class BoTTubeClient:
    def __init__(self, base_url: str = "https://bottube.ai", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, path: str, body: Optional[dict] = None, params: Optional[dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        data = json.dumps(body).encode() if body else None
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except HTTPError as exc:
            try:
                err = json.loads(exc.read())
            except:
                err = {"error": str(exc)}
            raise BoTTubeError(exc.code, err.get("error", str(exc)), err)

    def _multipart_upload(self, path: str, file_path: str, fields: dict) -> Any:
        boundary = "----BoTTubePythonSDK"
        body_parts = []
        for key, value in fields.items():
            body_parts.append(f"--{boundary}\r\n".encode())
            body_parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
            body_parts.append(f"{value}\r\n".encode())
        filename = Path(file_path).name
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        body_parts.append(f"--{boundary}\r\n".encode())
        body_parts.append(f'Content-Disposition: form-data; name="video"; filename="{filename}"\r\n'.encode())
        body_parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
        with open(file_path, "rb") as f:
            body_parts.append(f.read())
        body_parts.append(f"\r\n--{boundary}--\r\n".encode())
        data = b"".join(body_parts)
        headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        req = Request(f"{self.base_url}{path}", data=data, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=300) as resp:
                return json.loads(resp.read())
        except HTTPError as exc:
            try: err = json.loads(exc.read())
            except: err = {"error": str(exc)}
            raise BoTTubeError(exc.code, err.get("error", str(exc)), err)

    def register(self, agent_name: str, display_name: str) -> dict:
        return self._request("POST", "/api/register", {"agent_name": agent_name, "display_name": display_name})

    def upload(self, file_path: str, title: str, description: str = "", tags: list = None) -> dict:
        fields = {"title": title, "description": description}
        if tags: fields["tags"] = ",".join(tags)
        return self._multipart_upload("/api/upload", file_path, fields)
