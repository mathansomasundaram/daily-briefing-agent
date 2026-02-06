"""
Main execution module.
"""

from openai import OpenAI
from dotenv import load_dotenv

from google_sheets import get_receivers_from_sheet
from email_service import send_email
from config import PROMPT, OPENAI_MODEL, MAX_OUTPUT_TOKENS, EMAIL_SUBJECT

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI()  # API key picked automatically from env


def generate_daily_digest():
    """Generate daily market and tech digest using OpenAI."""
    response = client.responses.create(
        model=OPENAI_MODEL,
        input=PROMPT,
        max_output_tokens=MAX_OUTPUT_TOKENS
    )
    return response.output_text


def main():
    """Main execution function."""
    try:
        # Generate the daily digest
        digest_content = generate_daily_digest()

        # Get email receivers from Google Sheets
        receivers = get_receivers_from_sheet()

         # Send the digest via email
        send_email(
            subject=EMAIL_SUBJECT,
            body=digest_content,
            receivers=receivers
        )
    except Exception as e:
        raise


if __name__ == "__main__":
    main()