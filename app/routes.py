from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from app.sheets import GoogleSheetsService
import logging
from urllib.parse import unquote, urlparse, parse_qs

# Set up logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

main = Blueprint("main", __name__)

def extract_sheet_id(url):
    """Extract Sheet ID from Google Sheet URL."""
    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc != "docs.google.com" or not parsed_url.path.startswith("/spreadsheets/d/"):
            raise ValueError("Invalid Google Sheet URL")
        sheet_id = parsed_url.path.split("/")[3]
        if not sheet_id:
            raise ValueError("Sheet ID not found in URL")
        return sheet_id
    except Exception as e:
        logging.error(f"Error parsing Sheet URL: {str(e)}")
        raise ValueError(f"Invalid Google Sheet URL: {str(e)}")

@main.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            sheet_url = request.form.get("sheet_url")
            if not sheet_url:
                flash("Please provide a Google Sheet URL.", "error")
                return render_template("index.html", sheet_titles=[])
            
            # Extract Sheet ID and store in session
            sheet_id = extract_sheet_id(sheet_url)
            session["sheet_id"] = sheet_id
            logging.debug(f"Stored Sheet ID in session: {sheet_id}")
            
            # Fetch sheet titles
            sheets_service = GoogleSheetsService()
            sheet_titles = sheets_service.get_all_sheets()
            flash("Successfully loaded sheet tabs!", "success")
            return render_template("index.html", sheet_titles=sheet_titles, sheet_url=sheet_url)
        except (FileNotFoundError, ValueError) as e:
            logging.error(f"Configuration error in index route: {str(e)}")
            flash(f"Configuration error: {str(e)}", "error")
            return render_template("index.html", sheet_titles=[])
        except Exception as e:
            logging.error(f"Error in index route: {str(e)}")
            if "SpreadsheetNotFound" in str(e) or "Permission denied" in str(e):
                flash("Failed to access the Google Sheet. Please share the sheet with the service account email (found in credentials.json) with Viewer or Editor access.", "error")
            else:
                flash(f"Failed to load sheet tabs: {str(e)}", "error")
            return render_template("index.html", sheet_titles=[])
    
    # GET request: Show input form or sheet tabs if session has Sheet ID
    try:
        if "sheet_id" in session:
            sheets_service = GoogleSheetsService()
            sheet_titles = sheets_service.get_all_sheets()
            return render_template("index.html", sheet_titles=sheet_titles)
        return render_template("index.html", sheet_titles=[])
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Configuration error in index route: {str(e)}")
        flash(f"Configuration error: {str(e)}", "error")
        return render_template("index.html", sheet_titles=[])
    except Exception as e:
        logging.error(f"Error in index route: {str(e)}")
        if "SpreadsheetNotFound" in str(e) or "Permission denied" in str(e):
            flash("Failed to access the Google Sheet. Please share the sheet with the service account email (found in credentials.json) with Viewer or Editor access.", "error")
        else:
            flash(f"Failed to load sheet tabs: {str(e)}", "error")
        return render_template("index.html", sheet_titles=[])

@main.route("/sheet/<path:sheet_name>", methods=["GET"])
def get_sheet_data(sheet_name):
    try:
        sheet_name = unquote(sheet_name)
        logging.debug(f"Decoded sheet name: {sheet_name}")
        sheets_service = GoogleSheetsService()
        headers, data = sheets_service.get_sheet_data(sheet_name)
        sheet_titles = sheets_service.get_all_sheets()
        if not headers or not data:
            flash(f"Sheet {sheet_name} is empty or has no valid data.", "warning")
        else:
            flash(f"Successfully loaded data from {sheet_name}!", "success")
        return render_template("index.html", sheet_titles=sheet_titles, headers=headers, data=data, active_sheet=sheet_name)
    except (FileNotFoundError, ValueError) as e:
        logging.error(f"Configuration error for sheet {sheet_name}: {str(e)}")
        flash(f"Configuration error: {str(e)}", "error")
        return render_template("index.html", sheet_titles=[])
    except Exception as e:
        logging.error(f"Error fetching data for sheet {sheet_name}: {str(e)}")
        if "SpreadsheetNotFound" in str(e) or "Permission denied" in str(e):
            flash("Failed to access the Google Sheet. Please share the sheet with the service account email (found in credentials.json) with Viewer or Editor access.", "error")
        else:
            flash(f"Failed to load data for {sheet_name}: {str(e)}", "error")
        return render_template("index.html", sheet_titles=[])