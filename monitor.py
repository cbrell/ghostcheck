import os
import smtplib
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup

EMAIL_ADDRESS     = os.environ.get("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD", "")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SHOP_EMPTY_SIGNAL    = "No results found"
BOWLER_CLOSED_SIGNAL = "entry period has now ended"


def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")


def send_email(subject, body):
    print(f"Sending email: {subject}")
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        print("Email credentials not set — skipping send.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = EMAIL_ADDRESS  # sends to yourself
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)
    print("Email sent.")


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

    if BOWLER_CLOSED_SIGNAL not in soup.get_text().lower():
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
