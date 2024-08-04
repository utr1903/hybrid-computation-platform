import logging
import requests

logger = logging.getLogger(__name__)


def main():
    # Make a GET request to an endpoint
    response = requests.get("http://localhost:8081/task-to-run")

    # Check if the request was successful
    if response.status_code == 200:
        # Process the response data
        data = response.json()
        # Do something with the data
        print(data)
    else:
        # Handle the error
        print("Error:", response.status_code)


if __name__ == "__main__":
    main()
