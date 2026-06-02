from pypdf import PdfReader


class PdfExtractor:
    @staticmethod
    def extract(file_path: str) -> str:
        reader = PdfReader(file_path)
        pages = [page.extract_text() for page in reader.pages]
        return "\n".join(pages)
