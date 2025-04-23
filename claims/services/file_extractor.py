import base64
import mimetypes
import os
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2

load_dotenv()  # Load environment variables from .env

class FileExtractor:
    def __init__(self, file):
        self.file = file
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def extract(self):
        content_type = self._get_file_content_type()

        if content_type.startswith('image/'):
            return self._extract_from_image()
        elif content_type == 'application/pdf':
            return self._extract_from_pdf()
        elif content_type == 'text/csv':
            return self._extract_from_csv()
        else:
            return "Unsupported file type."

    def _extract_from_image(self):
        image_base64 = base64.b64encode(self.file.read()).decode('utf-8')
        content_type = mimetypes.guess_type(self.file.name)[0]
        base64_data_url = f"data:{content_type};base64,{image_base64}"

        prompt = (
            "You're an expert medical insurance claim processor. "
            "From the given image (prescription or medical document), extract all relevant data "
            "that can help generate a structured insurance claim. Ensure no useful information is missed. "
            "Respond in bullet points. This data will be used for an insurance automation software."
        )

        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{content_type};base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000 
        )

        return response.choices[0].message.content.strip()

    def _extract_from_pdf(self):
        pdf_reader = PyPDF2.PdfReader(self.file)
        text = ""

        for page in pdf_reader.pages:
            text += page.extract_text() or ""

        return self._call_gpt_text_api(text)

    def _extract_from_csv(self):
        text = self.file.read().decode('utf-8')
        return self._call_gpt_text_api(text)

    def _call_gpt_text_api(self, text):
        prompt = (
            "You're an AI insurance processor. Extract all important claim-related details from the following text. "
            "Format the output in a structured and clean way. "
            "Assume this will be used for generating insurance claims automatically."
        )

        response = self.client.chat.completions.create(
            model="gpt-4",
            temperature=1,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{text}"
                }
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()

    def _get_file_content_type(self):
        return mimetypes.guess_type(self.file.name)[0]
