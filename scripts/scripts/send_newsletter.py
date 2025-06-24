#!/usr/bin/env python3
# scripts/send_newsletter.py

import os, glob, datetime, pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMTP_HOST       = os.getenv("SMTP_HOST","smtp.gmail.com")
SMTP_PORT       = int(os.getenv("SMTP_PORT",587))
SMTP_USER       = os.getenv("SMTP_USER")
SMTP_PASS       = os.getenv("SMTP_PASS")

def latest_csv():
    files = glob.glob("hot_repos_*.csv")
    return max(files, key=os.path.getmtime)

def build_html(df):
    df = df.copy()
    df["Project"] = df.apply(
      lambda r: f'<a href="{r.url}">{r.repo}</a>', axis=1)
    return df[["Project","delta","language","description"]].to_html(
      index=False, escape=False)

def main():
    path = latest_csv()
    df   = pd.read_csv(path)
    html = build_html(df)
    date = datetime.date.today().isoformat()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Weekly Hyper-Growth Repos: {date}"
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL

    body = f"""
    <p>Hi,</p>
    <p>Here are this week’s top {len(df)} hyper-growth GitHub repos:</p>
    {html}
    <p>— The Hyper-Growth Digest</p>
    """
    msg.attach(MIMEText(body,"html"))

    with smtplib.SMTP(SMTP_HOST,SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER,SMTP_PASS)
        s.send_message(msg)
        print(f"✅ Sent to {RECIPIENT_EMAIL}")

if __name__=="__main__":
    main()
