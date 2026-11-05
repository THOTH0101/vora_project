from run_extract import extract_doc_details


def main():
    path = "samples/CvResume-1.pdf"
    print(extract_doc_details(path))


if __name__ == "__main__":
    main()
