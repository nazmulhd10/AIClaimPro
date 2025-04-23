from .file_extractor import FileExtractor

class ClaimProcessor:
    def __init__(self, claim, document_instances):
        self.claim = claim
        self.documents = document_instances  # এটি এখন একটি লিস্ট

    def process(self):
        """Process a single document."""
        try:
            with self.document.document.open(mode='rb') as file:  # ✅ Corrected here
                extractor = FileExtractor(file)
                content = extractor.extract()
                print(f"[Extracted content for {self.document.document.name}]:\n{content}")
        except Exception as e:
            print(f"❌ Error processing document {self.document.document.name}: {e}")

    def process_all(self):
        """Process all uploaded documents for this claim."""
        try:
            for doc in self.documents:
                with doc.document.open(mode='rb') as file:  # ✅ Corrected here
                    extractor = FileExtractor(file)
                    content = extractor.extract()
                    print(f"[Extracted content for {doc.document.name}]:\n{content}")

                    # Future idea: save content to DB if needed

            print("✅ All documents processed successfully.")
        except Exception as e:
            print(f"❌ Error processing documents: {e}")