import re
import math
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import backoff
import requests
import feedparser
import concurrent.futures

from io import BytesIO
from datetime import datetime, timedelta
from tqdm import tqdm
from pdfminer.high_level import extract_text

import openai
from llama_index.llms import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter


def get_tech_news():
    """
    Retrieve tech news from TechCrunch's RSS feed.
    Returns a list of tuples containing (link, title, summary, content)
    """
    # TechCrunch RSS feed URL
    feed_url = 'https://techcrunch.com/feed/'
    
    print("Fetching tech news...")
    feed = feedparser.parse(feed_url)
    news_list = []

    # Get news from the last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    
    for entry in feed.entries:
        # Convert published date to datetime object
        published_date = datetime(*entry.published_parsed[:6])
        
        if published_date >= yesterday:
            try:
                # Extract the main content from the article
                content = entry.get('content', [{'value': ''}])[0]['value']
                news_list.append((entry.link, entry.title, entry.summary, content))
            except Exception as e:
                print(f"Error processing news: {entry.title}. Error: {e}")

    print(f"Found {len(news_list)} news articles.")
    return news_list


def extract_text_from_pdf(pdf_url):
    """
    Extracts and returns text content from a PDF located at the provided URL.
    """
    response = requests.get(pdf_url)
    response.raise_for_status()
    pdf_data = BytesIO(response.content)
    
    return extract_text(pdf_data)


@backoff.on_exception(backoff.expo,
                      (openai.error.RateLimitError, concurrent.futures.TimeoutError),
                      max_tries=4)
def complete_with_retry(llm, text, timeout=120):
    """
    Send a request to llm.complete with retry, delay, and timeout.
    """
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(llm.complete, text)
            return future.result(timeout=timeout)
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise


def concatenate_news(news_items, minimum_groups=4):
    """
    Concatenate news items into groups for processing.
    """
    grouped_strings = []
    
    total_items = len(news_items)
    group_size = total_items // minimum_groups
    leftover = total_items % minimum_groups
    
    current_group = 1
    concatenated_string = ""

    for i, (link, title, summary, content) in enumerate(news_items, 1):
        concatenated_string += f"{title}: {summary}; "
        
        current_group_size = group_size + (1 if current_group <= leftover else 0)
        
        if i % current_group_size == 0:
            grouped_strings.append(concatenated_string)
            concatenated_string = ""
            current_group += 1
            
    return grouped_strings


def generate_summary(text):
    """
    Generates a summary for the given text using GPT-4.
    Uses a recursive approach to handle long texts.
    """
    llm = OpenAI(temperature=0.7, model="gpt-4")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2500,
        chunk_overlap=0,
        length_function=len,
        is_separator_regex=False,
    )

    docs = text_splitter.create_documents([text])
    docs = [doc.page_content for doc in docs]
    num_splits = int(math.log2(len(docs)))

    for _ in tqdm(range(num_splits)):
        if len(docs) % 2 == 0:
            docs = [docs[i] + docs[i + 1] for i in range(0, len(docs) - 1, 2)]
        else:
            last_doc = docs[-1]
            docs = [docs[i] + docs[i + 1] for i in range(0, len(docs) - 1, 2)]
            docs[-1] = docs[-1] + last_doc

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_index = {executor.submit(
            lambda i, doc: (i, complete_with_retry(llm, "Concisely and simply explain what this text is about: " + doc).text),
            i, doc): i for i, doc in enumerate(docs)}
    
            for future in concurrent.futures.as_completed(future_to_index):
                i, result = future.result()
                docs[i] = result

    return docs[0]


def reduce_selection(llm, news_items):
    """
    Refines the selection of news items until there are 3 or fewer items.
    Uses GPT-4 to select the most interesting news.
    """
    prompt = "Give me the top 3, in your opinion, most interesting tech news. Rank your choices. Do not change the given indexes."
    previous_news_items = []

    print("Selecting the top 3 news items.")
    while len(news_items) > 3:
        print(f"Current number of items: {len(news_items)}")
        previous_news_items = news_items.copy()
        contexts = concatenate_news(news_items)
        all_chosen_indices = set()

        def process_context(context):
            response = complete_with_retry(llm, context + prompt).text
            max_index = len(news_items)
            new_indices = [int(match) for match in re.findall(r'\b\d+\b', response) if int(match) <= max_index][1::2]
            return new_indices

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_context, context) for context in contexts]
            for future in concurrent.futures.as_completed(futures):
                new_indices = future.result()
                all_chosen_indices.update(new_indices)

        news_items = [news_items[idx-1] for idx in all_chosen_indices]

    if len(news_items) < 3:
        remaining_items_needed = 3 - len(news_items)
        if len(previous_news_items) > 3:
            additional_items = previous_news_items[:remaining_items_needed]
            news_items.extend(additional_items)
        else:
            print("Not enough news items to fulfill the 3-item requirement.")

    print("Finished selecting the top 3 news items.")
    return news_items


def create_news_strings(news_items):
    """
    Generate formatted strings for a list of news items.
    """
    news_strings = []

    for news in news_items:
        link, title, summary, content = news
        print(f"Now summarizing: {title}")

        summary = generate_summary(content)
        print(f"Summary complete: {summary}")

        news_string = f"Link: {link}\n\nTitle: {title}\n\nSummary: {summary}"
        news_strings.append(news_string)

    return news_strings


def send_email(news_strings, config):
    """
    Send the news summaries via email.
    """
    # Create message
    msg = MIMEMultipart()
    msg['From'] = config['email_sender']
    msg['To'] = config['email_recipient']
    msg['Subject'] = f"Tech News Summary - {datetime.now().strftime('%Y-%m-%d')}"

    # Create email body
    body = "Here are today's top tech news summaries:\n\n"
    for i, news in enumerate(news_strings, 1):
        body += f"--- News {i} ---\n{news}\n\n"

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['email_sender'], config['email_password'])
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as file:
    config = json.load(file)

# Initialize OpenAI
openai.api_key = config['api_key']
llm = OpenAI(temperature=0, model="gpt-4")

# Main execution
news_items = get_tech_news()
chosen_news = reduce_selection(llm, news_items)
news_strings = create_news_strings(chosen_news)
send_email(news_strings, config)
