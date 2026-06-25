import fitz


class DocumentProcessor:

    @staticmethod
    def extract_text(pdf_path: str) -> str:

        document = fitz.open(pdf_path)

        text = ""

        for page in document:

            text += page.get_text()

            text += "\n"

        document.close()

        return text.strip()