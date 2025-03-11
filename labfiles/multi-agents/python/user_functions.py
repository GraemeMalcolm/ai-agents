import json
from typing import Any, Callable, Set, Dict, List, Optional

def send_email(recipient: str, subject: str, body: str) -> str:
    # In a real-world scenario, you'd use an SMTP server or an email service API.
    # Here, we'll just print the email.
    print("\n-----------------------------------------------------------------------")
    print(f"To: {recipient}...")
    print(f"Subject: {subject}")
    print(f"Message:\n{body}")
    print("-----------------------------------------------------------------------\n")

    message_json = json.dumps({"message": f"Email successfully sent to {recipient}."})
    return message_json

user_functions: Set[Callable[..., Any]] = {
    send_email
}