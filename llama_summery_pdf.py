import pdfplumber
import requests
from bs4 import BeautifulSoup


def extract_text_with_pdfplumber(pdf_path):
    full_text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
        with open("rel.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        print("Extracted text saved to output.txt")
    return full_text

def download_pdf_from_website(url, save_path="downloaded.pdf"):
    # Step 1: Fetch the website content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to access the website.")
        return

    # Step 2: Parse the HTML to find a PDF link
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_link = None

    # Look for <a> tags containing '.pdf'
    for link in soup.find_all("a", href=True):
        if link["href"].endswith(".pdf"):
            pdf_link = link["href"]
            break

    if not pdf_link:
        print("No PDF file found on the website.")
        return

    # Step 3: Handle relative URLs
    if not pdf_link.startswith("http"):
        from urllib.parse import urljoin
        pdf_link = urljoin(url, pdf_link)

    # Step 4: Download the PDF
    pdf_response = requests.get(pdf_link, stream=True)

    if pdf_response.status_code == 200:
        with open(save_path, "wb") as pdf_file:
            for chunk in pdf_response.iter_content(1024):
                pdf_file.write(chunk)
        print(f"PDF downloaded successfully: {save_path}")


    else:
        print("Failed to download the PDF.")


# Example Usage


try:
    website_url = "https://www.tatamotors.com/annual-reports/"  # Replace with the actual website URL
    download_pdf_from_website(website_url, "scraped_pdf.pdf")
except requests.exceptions.RequestException as e:
    print(f"Error accessing the website: {e}")


extract_text_with_pdfplumber("scraped_pdf.pdf")

try:
    with open("rel.txt", "r", encoding="ISO-8859-1") as file:
        content = file.read()
except requests.exceptions.RequestException as e:
    print(f"cant read anything: {e}")



OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"
messages = [
    {"role": "system", "content": "You are an assistant that analyzes the contents of a text file \
and provides the summery of every pdf page, ignoring text that might be navigation related. write who is this person and what do you feel about this person "},
    {"role": "user","content": f"{content}"}
]
payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }

response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)
print(response.json()['message']['content'])


