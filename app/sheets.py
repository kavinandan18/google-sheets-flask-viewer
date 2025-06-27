import gspread
from google.oauth2.service_account import Credentials
import logging
import os
import json
from config.config import Config
from flask import session

# Set up logging
logging.basicConfig(
    filename=Config.LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class GoogleSheetsService:
    def __init__(self):
        try:
            # Use Sheet ID from session if available, else fallback to config
            sheet_id = session.get("sheet_id", Config.GOOGLE_SHEET_ID)
            if not sheet_id:
                raise ValueError("No Google Sheet ID provided")

            # Validate credentials
            Config.validate(Config.CREDENTIALS_PATH)
            logging.debug(f"Using credentials file: {Config.CREDENTIALS_PATH}")
            logging.debug(f"Google Sheet ID: {sheet_id}")

            # Verify JSON validity
            with open(Config.CREDENTIALS_PATH, 'r') as f:
                json.load(f)
                logging.debug("Credentials JSON is valid")

            scopes = ["https://www.googleapis.com/auth/spreadsheets"]
            creds = Credentials.from_service_account_file(Config.CREDENTIALS_PATH, scopes=scopes)
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(sheet_id)
            logging.info("Successfully connected to Google Sheets API")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in credentials file: {str(e)}")
            raise ValueError(f"Invalid JSON in credentials file: {str(e)}")
        except FileNotFoundError as e:
            logging.error(f"Configuration error: {str(e)}")
            raise
        except ValueError as e:
            logging.error(f"Configuration error: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Failed to initialize Google Sheets service: {str(e)}")
            raise

    def get_all_sheets(self):
        """Get list of all sheet titles."""
        try:
            sheets = self.spreadsheet.worksheets()
            sheet_titles = [sheet.title for sheet in sheets if sheet.title.strip()]
            logging.info(f"Retrieved sheet titles: {sheet_titles}")
            return sheet_titles
        except Exception as e:
            logging.error(f"Error fetching sheet titles: {str(e)}")
            raise

    def get_sheet_data(self, sheet_name):
        """Get data from a specific sheet."""
        try:
            logging.debug(f"Fetching data for sheet: {sheet_name}")
            sheet = self.spreadsheet.worksheet(sheet_name)
            all_values = sheet.get_all_values()
            if not all_values:
                logging.warning(f"Sheet {sheet_name} is empty")
                return [], []
            
            # Use first row as headers
            headers = all_values[0]
            headers = [h if h.strip() else f"Column {i+1}" for i, h in enumerate(headers)]
            
            # Convert remaining rows to list of dictionaries
            data = []
            for row in all_values[1:]:
                row_data = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
                data.append(row_data)
            
            logging.info(f"Retrieved data from sheet: {sheet_name} (Headers: {headers}, Rows: {len(data)})")
            return headers, data
        except Exception as e:
            logging.error(f"Error fetching data from sheet {sheet_name}: {str(e)}")
            raise