import os
import requests
from bs4 import BeautifulSoup

RESEND_API_KEY   = os.environ.get("RESEND_API_KEY", "")
RECIPIENT_EMAIL  = os.environ.get("RECIPIENT_EMAIL", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SHOP_EMPTY_SIGNAL    = "No results found"
BOWLER_CLOSED_SIGNAL = "No results found"


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def send_email(subject, body):
    print(f"Sending email: {subject}")
    if not RESEND_API_KEY or not RECIPIENT_EMAIL:
        print("Resend credentials not set — skipping send.")
        return

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": "YGM Monitor <onboarding@resend.dev>",
            "to": [RECIPIENT_EMAIL],
            "subject": subject,
            "text": body,
        },
        timeout=10,
    )

    if response.status_code == 200:
        print("Email sent.")
    else:
        print(f"Email failed: {response.status_code} {response.text}")


def check_shop():
    print("Checking shop...")
    soup = fetch("https://www.yorkghostmerchants.com/shop")

    if SHOP_EMPTY_SIGNAL not in soup.get_text():
        send_email(
            subject="YGM: Ghosts in the shop!",
            body=(
                "Something has appeared in the York Ghost Merchants shop.\n\n"
                "Check now:\nhttps://www.yorkghostmerchants.com/shop\n"
            ),
        )
    else:
        print("Shop: empty (normal).")


def check_bowler_hat():
    print("Checking Bowler Hat...")
    soup = fetch("https://www.yorkghostmerchants.com/bowlerhat")

    if BOWLER_CLOSED_SIGNAL not in soup.get_text():
        send_email(
            subject="YGM: Bowler Hat has changed!",
            body=(
                "The Bowler Hat page no longer shows the usual closed message.\n\n"
                "Check now:\nhttps://www.yorkghostmerchants.com/bowlerhat\n"
            ),
        )
    else:
        print("Bowler Hat: closed (normal).")


if __name__ == "__main__":
    check_shop()
    check_bowler_hat()
    print("Done.")
