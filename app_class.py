import streamlit as st
from dotenv import load_dotenv
import logging
from utility_class import PDFDataExtractor  # Import the class instead of the method

# Configuring logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InvoiceExtractionApp:
    def __init__(self):
        """Initialize the app and the PDFDataExtractor instance."""
        load_dotenv()
        self.pdf_extractor = PDFDataExtractor()
        logging.info("PDFDataExtractor instance created.")
        self.setup_streamlit()

    def setup_streamlit(self):
        """Set up Streamlit page configurations and title."""
        st.set_page_config(page_title="Invoice Extraction Bot")
        st.title("Invoice Extraction Bot 💁")
        st.subheader("I can help you extracting invoice data")
        logging.info("Streamlit page configured.")

    def upload_invoice(self):
        """Handle invoice PDF file upload."""
        pdf_files = st.file_uploader("Upload Invoice here only PDF files allowed ", type=["pdf"], accept_multiple_files=True)
        if pdf_files:
            logging.info(f"{len(pdf_files)} file(s) uploaded.")
        return pdf_files
    
    def extract_data(self, pdf_files):
        """Extract data from uploaded PDF files and display results."""
        if pdf_files:
            with st.spinner('Wait for it...'):
                logging.info("Starting data extraction...")
                df = self.pdf_extractor.create_docs(pdf_files)  # Use the create_docs method from PDFDataExtractor
                logging.info("Data extraction completed.")
                st.write(df.head())

                data_as_csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download data as CSV",
                    data_as_csv,
                    "extracted-invoice-data.csv",
                    "text/csv",
                    key="download-csv"
                )
                logging.info("Data displayed and download button provided.")
                st.success("Hope I was able to save your time ❤️")

    def run(self):
        """Run the Streamlit app."""
        logging.info("App started.")
        pdf_files = self.upload_invoice()
        submit = st.button("Extract Data")
        if submit:
            logging.info("Extract Data button clicked.")
            self.extract_data(pdf_files)

if __name__ == '__main__':
    app = InvoiceExtractionApp()
    app.run()

        
