from app import create_app
import logging

# Set up logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = create_app()

if __name__ == "__main__":
    logging.info("Starting Flask application")
    app.run(debug=True)