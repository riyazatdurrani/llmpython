import os
import requests
import fitz
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from bs4 import BeautifulSoup
from urllib.parse import urljoin

OLLAMA_API = "http://localhost:11434/api/chat"
HEADERS = {"Content-Type": "application/json"}
MODEL = "llama3.2"

class PDFScraperApp:
    def __init__(self, root):  # ✅ Fixed __init__ method
        self.root = root
        self.root.title("Website PDF Scraper & Summarizer")

        # URL Input
        self.url_label = tk.Label(root, text="Enter Website URL:")
        self.url_label.pack(pady=5)
        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        # Fetch Button
        self.fetch_button = tk.Button(root, text="Fetch PDFs", command=self.fetch_pdfs)
        self.fetch_button.pack(pady=5)

        # Listbox for PDFs
        self.pdf_listbox = tk.Listbox(root, width=80, height=10)
        self.pdf_listbox.pack(pady=10)

        # Download Button
        self.download_button = tk.Button(root, text="Download & Summarize", command=self.download_and_summarize)
        self.download_button.pack(pady=5)

        # Summary Display
        self.summary_label = tk.Label(root, text="Summary:")
        self.summary_label.pack(pady=5)
        self.summary_text = tk.Text(root, height=10, width=80, wrap=tk.WORD)
        self.summary_text.pack(pady=5)

        self.pdf_links = []

    def fetch_pdfs(self):
        """Fetch PDF links from the given website URL."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a website URL.")
            return

        try:
            response = requests.get(url)
            if response.status_code != 200:
                messagebox.showerror("Error", f"Failed to access {url}")
                return

            soup = BeautifulSoup(response.text, "html.parser")
            self.pdf_links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True) if
                              a["href"].endswith(".pdf")]

            self.pdf_listbox.delete(0, tk.END)
            for pdf in self.pdf_links:
                self.pdf_listbox.insert(tk.END, pdf)

            if not self.pdf_links:
                messagebox.showinfo("Info", "No PDFs found on this website.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def download_and_summarize(self):
        """Download the selected PDF and summarize it."""
        try:
            selected_idx = self.pdf_listbox.curselection()
            if not selected_idx:
                messagebox.showerror("Error", "Please select a PDF from the list.")
                return

            pdf_url = self.pdf_links[selected_idx[0]]
            pdf_filename = pdf_url.split("/")[-1]

            response = requests.get(pdf_url)
            with open(pdf_filename, "wb") as f:
                f.write(response.content)

            summary = self.summarize_pdf(pdf_filename)
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(tk.END, str(summary))  # ✅ Ensure summary is a string


            os.remove(pdf_filename)  # Remove after summarization

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process PDF: {str(e)}")

    def summarize_pdf(self, pdf_path):
        """Extract text from PDF and summarize it using Ollama."""
        try:
            text = ""
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()

            if not text.strip():
                return "No readable text found in PDF."
            #
            # response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": f"Summarize this:\n{text}"}])
            # return response["message"]["content"]
        #     --------------------

            messages = [
                {"role": "system", "content": "You are an assistant that analyzes the contents of a text file \
            and provides the summery of every pdf page, ignoring text that might be navigation related. write who is this person and what do you feel about this person "},
                {"role": "user", "content": f"Summarize this:\n{text}"}
            ]
            payload = {
                "model": MODEL,
                "messages": messages,
                "stream": False
            }

            response = requests.post(OLLAMA_API, json=payload, headers=HEADERS)




            return response.json()['message']['content']
        # ============

        except Exception as e:
            return f"Error extracting or summarizing text: {str(e)}"


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFScraperApp(root)
    root.mainloop()
