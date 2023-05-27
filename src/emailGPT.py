from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.llms import GPT4All, LlamaCpp

from langchain.vectorstores import Chroma
from chromadb.config import Settings

embeddings_name = 'all-MiniLM-L6-v2'
persist_directory = 'testing-cleaned/persist'
model_n_ctx = 1024
model_path = 'testing/models/ggml-model-q4_0.bin'

def main():
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=Settings(
        chroma_db_impl='duckdb+parquet',
        persist_directory=persist_directory,
        anonymized_telemetry=False
    ))
    retriever = db.as_retriever()

    # Prepare the LLM
    callbacks = [StreamingStdOutCallbackHandler()]
    llm = LlamaCpp(model_path=model_path, n_ctx=model_n_ctx, callbacks=callbacks, verbose=False)
    # llm = GPT4All(model=model_path, n_ctx=model_n_ctx, backend='gptj', callbacks=callbacks, verbose=False)
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    while True:
        query = input("\nEnter a query: ")
        if query == "exit":
            break

        # Get the answer from the chain
        res = qa(query)
        #print(res)
        print('\n\n')




if __name__ == '__main__':
    main()