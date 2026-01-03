#!/usr/bin/env python3
"""Local end-to-end test against localhost:4000.

Covers:
- register
- login
- me
- forgot-password + reset-password + login with new password
- contract create with .txt upload (R2)
- contract list
- contract detail
- contract download-url (presigned)

Run (in another terminal):
    python manage.py migrate
    python manage.py runserver 0.0.0.0:4000

Then:
  python test_localhost_4000.py
"""

import json
import time
from datetime import datetime

import requests

BASE_URL = "http://127.0.0.1:4000"
OUT_FILE = "apiresponse.json"


def _now():
    return datetime.now().isoformat()


def call(method, path, *, headers=None, json_body=None, data=None, files=None, desc=""):
    url = f"{BASE_URL}{path}"
    started = time.time()
    try:
        resp = requests.request(
            method,
            url,
            headers=headers,
            json=json_body,
            data=data,
            files=files,
            timeout=30,
        )
        elapsed = time.time() - started
        item = {
            "timestamp": _now(),
            "method": method,
            "path": path,
            "description": desc,
            "status_code": resp.status_code,
            "elapsed_seconds": round(elapsed, 4),
        }
        try:
            item["response_json"] = resp.json()
        except Exception:
            item["response_text"] = resp.text
        return item
    except Exception as e:
        return {
            "timestamp": _now(),
            "method": method,
            "path": path,
            "description": desc,
            "error": str(e),
        }


def main():
    results = []

    # 1) Register
    unique_email = f"local_{int(time.time())}@example.com"
    password = "testpass123"
    results.append(
        call(
            "POST",
            "/api/auth/register/",
            json_body={"email": unique_email, "password": password, "full_name": "Local Tester"},
            desc="Register",
        )
    )

    # 2) Login
    login = call(
        "POST",
        "/api/auth/login/",
        json_body={"email": unique_email, "password": password},
        desc="Login",
    )
    results.append(login)

    access = None
    if isinstance(login.get("response_json"), dict):
        access = login["response_json"].get("access")

    headers = {"Authorization": f"Bearer {access}"} if access else None

    # 3) Me
    results.append(call("GET", "/api/auth/me/", headers=headers, desc="Me"))

    # 4) Forgot password
    forgot = call(
        "POST",
        "/api/auth/forgot-password/",
        json_body={"email": unique_email},
        desc="Forgot password",
    )
    results.append(forgot)

    reset_token = None
    if isinstance(forgot.get("response_json"), dict):
        reset_token = forgot["response_json"].get("reset_token")

    # 5) Reset password (only if token returned)
    new_password = "newpass123"
    if reset_token:
        results.append(
            call(
                "POST",
                "/api/auth/reset-password/",
                json_body={"token": reset_token, "new_password": new_password},
                desc="Reset password",
            )
        )
        # 6) Login with new password
        results.append(
            call(
                "POST",
                "/api/auth/login/",
                json_body={"email": unique_email, "password": new_password},
                desc="Login after reset",
            )
        )

    # 7) Contract create with .txt upload
    txt_body = (
        "CONTRACT AGREEMENT\n\n"
        "This is a local test contract document.\n"
        f"Generated at: {_now()}\n"
    )
    files = {"file": ("local_test_contract.txt", txt_body, "text/plain")}
    data = {"title": "Local Test Contract", "status": "draft"}
    created = call(
        "POST",
        "/api/contracts/",
        headers=headers,
        data=data,
        files=files,
        desc="Create contract with .txt upload (R2)",
    )
    results.append(created)

    contract_id = None
    if isinstance(created.get("response_json"), dict):
        contract_id = created["response_json"].get("id")

    # 8) List contracts
    results.append(call("GET", "/api/contracts/", headers=headers, desc="List contracts"))

    # 9) Contract detail + download url
    if contract_id:
        results.append(call("GET", f"/api/contracts/{contract_id}/", headers=headers, desc="Contract detail"))
        results.append(
            call(
                "GET",
                f"/api/contracts/{contract_id}/download-url/",
                headers=headers,
                desc="Contract download-url (presigned)",
            )
        )

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # quick summary
    ok = 0
    fail = 0
    for r in results:
        sc = r.get("status_code")
        if isinstance(sc, int) and 200 <= sc < 300:
            ok += 1
        else:
            fail += 1

    print(f"Saved results to {OUT_FILE}")
    print(f"Success: {ok}, Failed: {fail}, Total: {len(results)}")


if __name__ == "__main__":
    main()
