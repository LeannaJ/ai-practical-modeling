# Tech News Summary Agent

A Python-based automated system that collects, summarizes, and delivers the most interesting tech news from TechCrunch via email.

## Features

- Fetches tech news from TechCrunch's RSS feed
- Uses GPT-4 to select the most interesting news articles
- Generates concise summaries of selected articles
- Sends daily email digests with news summaries

## Requirements

- Python 3.7+
- OpenAI API key
- Email account (Gmail recommended)

## Installation

1. Clone this repository:
```bash
git clone [repository-url]
cd "News Summary Agent"
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure the settings:
   - Copy `config.json` and fill in your credentials:
     - OpenAI API key
     - Email sender address
     - Email password
     - Email recipient address
     - SMTP server settings

## Configuration

Edit `config.json` with your credentials:
```json
{
    "api_key": "your_openai_api_key",
    "email_sender": "your_email@example.com",
    "email_password": "your_email_password",
    "email_recipient": "recipient@example.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}
```

## Usage

Run the script:
```bash
python main.py
```

The script will:
1. Fetch tech news from TechCrunch
2. Select the most interesting articles using GPT-4
3. Generate summaries for each article
4. Send an email with the summaries

## Note for Gmail Users

If you're using Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password in the `email_password` field