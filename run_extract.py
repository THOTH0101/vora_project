from extraction.extract_text import extract_pdf_text


def extract_doc_details(path: str) -> dict:
    # function extract useful info from user document using embedings
    details = {}

    # extract text from document
    extracted_text = extract_pdf_text(path)
    details["text"] = extracted_text

    # process text using embedings
    # extract talent details using LLM
    # classifying talent details

    # return talent details in json
    print(f"details: {details}")
    return details
