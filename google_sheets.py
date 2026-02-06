"""
Google Sheets service module for handling spreadsheet operations.
"""

import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


def get_receivers_from_sheet():
    """
    Fetch email receivers from Google Sheets.

    Returns:
        list: List of email addresses from the spreadsheet
    """
    creds_json = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])

    creds = Credentials.from_service_account_info(
        creds_json,
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )

    service = build("sheets", "v4", credentials=creds)

    SPREADSHEET_ID = "1EpUEplXCxIG4qT-da5Wp1r63849u_vdl11PZ9siXFeA"
    RANGE = "Sheet1!A2:A"

    sheet = service.spreadsheets()  # pylint: disable=no-member
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE
    ).execute()

    values = result.get("values", [])

    return [row[0] for row in values if row]