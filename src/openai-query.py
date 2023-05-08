import openai
import crawl as crawl

############# QUERY GLOBAL SETTINGS #############

query_prefix = "You are emailGPT, an AI that can parse email data for you."

query_prefix += "  You have access to the following code:\n\n```"
with open("src/crawl.py") as file:
    query_prefix += file.read()
query_prefix += "\n```\n\n"

# query_prefix += "  You are an expert on the Gmail API provided by Google and convert user queries into gmail API searches."
# query_prefix += "  DO NOT USE TOKENS FOR ANYTHING OTHER THAN GMAIL API CODE."
# query_prefix += "  You are given a query and must return the top result from the Gmail API."
# query_prefix += "  ALWAYS USE THE PYTHON GMAIL API LIBRARY."
# query_prefix += "  Provide working syntax of how to query the gmail API in Python for the provided query."
query_prefix += "  You are given a query and must return a string in the format of a tuple: (query, max_results) that will be used for parameters in crawl.query_email_snippets()."
query_prefix += "  DO NOT PROVIDE ANY OUTPUT THAT IS NOT THE TUPLE FORMAT"
query_prefix += "\n\nQuery:"

###################################################

crawl_service = crawl.setup_gmail_api()

def get_top_result(query, model='text-davinci-002', max_tokens=500):
    api_key = ''
    with open("openai-key.txt") as file:
        api_key = file.read()

    openai.api_key = api_key

    response = openai.Completion.create(
        engine=model,
        prompt=query_prefix + query,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.7,
    )

    top_result = response.choices[0].text.strip()
    top_result = top_result[top_result.index('(') + 1: top_result.index(')')]
    query = top_result[:top_result.index(',')]
    max_results = top_result[top_result.index(',') + 2:]
    return (query, max_results)

if __name__ == '__main__':
    query = "Get the last email that has the word receipt in the subject, return 5"
    result = get_top_result(query)
    print("AI Result:", result)
    crawl.query_email_snippets(crawl_service, result[0], int(result[1]))
