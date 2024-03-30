import os
import logging
from pypdf import PdfReader
import pandas as pd
import re
from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s -  %(levelname)s - %(message)s')

class PDFDataExtractor:
    def __init__(self):
        # Retrieve the API key from environment variables
        self.api_key = os.environ.get('GOOGLE_PALM_API_KEY')
        if not self.api_key:
            logging.error("API key not found. Please set the GOOGLE_PALM_API_KEY environment variable.")
            raise ValueError("API key not found. Please set the GOOGLE_PALM_API_KEY environment variable.")
        else:
            logging.info("API key loaded successfully..")

    def get_pdf_text(self, pdf_doc):
        text = ""
        pdf_reader = PdfReader(pdf_doc)
        for page in pdf_reader.pages:
            page_text = page.extract_text() or "" # Ensure text is added even if None is returned
            text += page_text
        logging.info(f"Extracted text from {pdf_doc}")
        return text
    
    def extracted_data(self, pages_data):
        template = """Extract all the following values : invoice no., Description, Quantity, date, 
                      Unit price , Amount, Total, email, phone number and address from this data: {pages}

                    Expected output: remove any dollar symbols {{'Invoice no.': '1001329','Description': 'Office Chair','Quantity': '2','Date': '5/4/2023','Unit price': '1100.00','Amount': '2200.00','Total': '2200.00','Email': 'Santoshvarma0988@gmail.com','Phone number': '9999999999','Address': 'Mumbai, India'}}
                   """
        prompt_template = PromptTemplate(input_variables=["pages"], template=template)
        llm = GooglePalm(google_api_key=self.api_key, temperature=0.1)
        full_response=llm(prompt_template.format(pages=pages_data))
        return full_response
    
    def create_docs(self, user_pdf_list):
        df = pd.DataFrame({'Invoice no.': pd.Series(dtype='str'),
                   'Description': pd.Series(dtype='str'),
                   'Quantity': pd.Series(dtype='str'),
                   'Date': pd.Series(dtype='str'),
	               'Unit price': pd.Series(dtype='str'),
                   'Amount': pd.Series(dtype='int'),
                   'Total': pd.Series(dtype='str'),
                   'Email': pd.Series(dtype='str'),
	               'Phone number': pd.Series(dtype='str'),
                   'Address': pd.Series(dtype='str')
                    })
        
        for filename in user_pdf_list:
            logging.info(f"Processing file: {filename}")
            raw_data = self.get_pdf_text(filename)
            llm_extracted_data = self.extracted_data(raw_data)
            pattern = r'{(.+)}'
            match = re.search(pattern, llm_extracted_data, re.DOTALL)
            if match:
                extracted_text = match.group(1)
                data_dict = eval('{' + extracted_text + '}')
                logging.info(f"Extracted data: {data_dict}")
                new_row_df = pd.DataFrame([data_dict])
                df = pd.concat([df, new_row_df], ignore_index=True)
            else:
                logging.warning("No match found. Unable to extract data.")
            logging.info("********************DONE with file processing***************")

        return df
    
# # Usage example
# if __name__ == "__main__":
#     # Set the GOOGLE_PALM_API_KEY environment variable before running this script
#     extractor = PDFDataExtractor()
#     user_pdf_list = ['path_to_pdf1.pdf', 'path_to_pdf2.pdf']  # Replace with actual paths to PDFs
#     df = extractor.create_docs(user_pdf_list)
#     print(df)    
