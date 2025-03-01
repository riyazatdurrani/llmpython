import requests

# URL of the CSV file
csv_url = "https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD"

# Local filename to save the CSV
local_filename = "xyz.csv"


def download_csv(url, filename):
    """Downloads a CSV file from a given URL and saves it locally."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print(f"CSV file downloaded successfully: {filename}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading CSV: {e}")



download_csv(csv_url, local_filename)


OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"
messages = [
    {"role": "system", "content": "You are an assistant that analyzes the contents of a text file \
and provides the summery of every pdf page, ignoring text that might be navigation related. write who is this person and what do you feel about this person "},
    {"role": "user","content": f"{local_filename}"}
]
payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
print(response.json()['message']['content'])





