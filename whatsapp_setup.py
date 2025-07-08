#!/usr/bin/env python3
"""
Command-line helper for setting up and testing the WhatsApp Business
integration used by the Debt-Collection Chatbot.

Usage:
  python whatsapp_setup.py verify
  python whatsapp_setup.py webhook --url https://example.com/api/whatsapp/webhook
  python whatsapp_setup.py send-test --to +15551234567 --text "Hello 👋"

Environment variables (read from your shell or a .env file):
  WB_API_VERSION        e.g. "v19.0"
  WB_PHONE_NUMBER_ID    Your WhatsApp Business phone-number ID
  WB_ACCESS_TOKEN       Permanent or long-lived access token
"""

from __future__ import annotations

import argparse
import os
import sys
from textwrap import dedent

import httpx
from dotenv import load_dotenv

API_ROOT = "https://graph.facebook.com"

load_dotenv()  # load variables from a local .env file if present


def env(var: str) -> str:
    """Helper to fetch required env vars with a friendly error."""
    try:
        value = os.environ[var]
    except KeyError:
        print(f"ERROR: environment variable {var} is not set.", file=sys.stderr)
        sys.exit(2)
    return value


def get_http_client() -> httpx.Client:
    return httpx.Client(
        base_url=f"{API_ROOT}/{env('WB_API_VERSION')}",
        headers={"Authorization": f"Bearer {env('WB_ACCESS_TOKEN')}"}
    )


def verify() -> None:
    """Checks that the access token and phone-number ID are valid."""
    phone_id = env("WB_PHONE_NUMBER_ID")
    with get_http_client() as client:
        r = client.get(f"/{phone_id}")
    if r.is_success:
        data = r.json()
        print("✅ WhatsApp credentials verified.")
        print("Phone Display Name :", data.get("name"))
        print("Verified Name      :", data.get("verified_name"))
    else:
        print("❌ Verification failed:")
        print(f"Status: {r.status_code}")
        print(f"Body  : {r.text}")
        sys.exit(1)


def register_webhook(url: str) -> None:
    """Registers or updates the webhook callback URL."""
    phone_id = env("WB_PHONE_NUMBER_ID")
    with get_http_client() as client:
        r = client.post(
            f"/{phone_id}/settings",
            json={"webhook_url": url, "webhook_version": "v1.0"}
        )
    if r.is_success:
        print(f"✅ Webhook set to: {url}")
    else:
        print("❌ Unable to set webhook:")
        print(f"Status: {r.status_code}")
        print(f"Body  : {r.text}")
        sys.exit(1)


def send_test(to: str, text: str) -> None:
    """Sends a test text message."""
    phone_id = env("WB_PHONE_NUMBER_ID")
    payload = {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
        "type": "text",
        "text": {"body": text},
    }
    with get_http_client() as client:
        r = client.post(f"/{phone_id}/messages", json=payload)
    if r.is_success:
        msg_id = r.json().get("messages", [{}])[0].get("id")
        print(f"✅ Test message queued (ID: {msg_id})")
    else:
        print("❌ Failed to send test message:")
        print(f"Status: {r.status_code}")
        print(f"Body  : {r.text}")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WhatsApp Business setup helper for the Debt-Collection Chatbot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(
            """
            Examples
            --------
            Verify credentials:
              python whatsapp_setup.py verify

            Register webhook:
              python whatsapp_setup.py webhook --url https://api.mybot.com/whatsapp/webhook

            Send test message:
              python whatsapp_setup.py send-test --to +15551234567 --text "Hello from Debt-Bot 🚀"
            """
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("verify", help="Verify credentials")

    p_webhook = sub.add_parser("webhook", help="Register or update webhook URL")
    p_webhook.add_argument("--url", required=True, help="Public HTTPS URL to receive callbacks")

    p_test = sub.add_parser("send-test", help="Send a test text message")
    p_test.add_argument("--to", required=True, help="Recipient phone number in E.164 format (+1234...)")
    p_test.add_argument("--text", default="Hello from Debt-Bot 👋", help="Message body")

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.cmd == "verify":
        verify()
    elif args.cmd == "webhook":
        register_webhook(args.url)
    elif args.cmd == "send-test":
        send_test(args.to, args.text)
    else:
        print("Unknown command", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
