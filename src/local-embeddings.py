from typing import List
from chromadb.config import Settings
import glob
import os

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.document_loaders import UnstructuredHTMLLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma

embeddings_name = 'all-MiniLM-L6-v2'

# Map file extensions to document loaders and their arguments
LOADER_MAPPING = {
    # ".csv": (CSVLoader, {}),
    # ".docx": (Docx2txtLoader, {}),
    # ".docx": (UnstructuredWordDocumentLoader, {}),
    # ".enex": (EverNoteLoader, {}),
    # ".eml": (UnstructuredEmailLoader, {}),
    # ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    # ".md": (UnstructuredMarkdownLoader, {}),
    # ".odt": (UnstructuredODTLoader, {}),
    # ".pdf": (PDFMinerLoader, {}),
    # ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}


def load_single_document(file_path: str) -> Document:
    ext = "." + file_path.rsplit(".", 1)[-1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()[0]

    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(source_dir: str) -> List[Document]:
    # Loads all documents from source documents directory
    all_files = []
    # walk source_dir via os.walk
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            # get the file extension
            ext = os.path.splitext(file)[-1].lower()
            # if the file extension is in the LOADER_MAPPING, add it to the list of files
            if ext in LOADER_MAPPING:
                all_files.append(os.path.join(root, file))

    return [load_single_document(file_path) for file_path in all_files] 


# def load_documents(source_dir: str) -> List[Document]:
#     # Loads all documents from source documents directory
#     all_files = []
#     for ext in LOADER_MAPPING:
#         all_files.extend(
#             glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
#         )
#     return [load_single_document(file_path) for file_path in all_files]

def main():
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_name)

    persist_directory = 'testing-cleaned/persist'
    source_directory = 'email-documents-cleaned'

    # Load documents and split in chunks
    print(f"Loading documents from {source_directory}")
    chunk_size = 500
    chunk_overlap = 50
    documents = load_documents(source_directory)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Loaded {len(documents)} documents from {source_directory}")
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} characters each)")

    # Create and store locally vectorstore
    db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory, client_settings=Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=persist_directory,
        anonymized_telemetry=False
    ))
    db.persist()
    db = None

if __name__ == '__main__':
    main()