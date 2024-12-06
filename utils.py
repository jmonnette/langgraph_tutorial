import os, getpass, logging
from pprint import pprint
from pydantic import BaseModel

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "application"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },

    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
    }

def configure_logging():
    """Configure logging for the server"""
    from logging.config import dictConfig
    logConfig = LogConfig()
    dictConfig(logConfig.model_dump())
    return logging.getLogger(logConfig.LOGGER_NAME)

def set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

def debug_print(output):
    pprint(output)
    return output

# class that wraps another class and logs all function calls being executed
class Wrapper:
    def __init__(self, wrapped_class):
        self.wrapped_class = wrapped_class

    def __getattr__(self, attr):
        original_func = getattr(self.wrapped_class, attr)

        def wrapper(*args, **kwargs):
            print(f"Calling function: {attr}")
            print(f"Arguments: {args}, {kwargs}")
            result = original_func(*args, **kwargs)
            print(f"Response: {result}")
            return result

        return wrapper
    
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import BaseTool

# Define a custom tool for retrieving and parsing content from a URL
class   URLRetrievalTool(BaseTool):
    """
    A tool for retrieving and parsing text content from a given URL.

    This tool fetches the HTML content of a webpage and extracts the text content,
    removing all HTML tags. It is useful for obtaining the main textual content from
    web pages for further processing or analysis.

    Methods:
        _run(url: str) -> str: Retrieves and parses the text content from the specified URL.
    """

    def __init__(self):
        super().__init__(name="url_retrieval", description="Retrieve and parse text from a URL.  Can be used to gather more details on a topic from a list of URLs.  For example, these Urls could be retrieved from search results.")

    def _run(self, url: str) -> str:
        """
        Retrieve and parse text content from the specified URL.

        Parameters:
            url (str): The URL of the webpage to retrieve and parse.

        Returns:
            str: The plain text content of the webpage, or an error message if retrieval fails.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator='\n')  # Extract text with newlines
            return text.strip()  # Return the parsed text
        except requests.RequestException as e:
            return f"Error retrieving content from {url}: {e}"