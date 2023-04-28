import openai
from approaches.approach import Approach
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from text import nonewlines

# Simple retrieve-then-read implementation, using the Cognitive Search and OpenAI APIs directly. It first retrieves
# top documents from search, then constructs a prompt with them, and then uses OpenAI to generate an completion 
# (answer) with that prompt.

# "You are an intelligent assistant helping user to find out which credit service is form your need through banking in Vietnam. " + \
# "Use 'you' to refer to the individual asking the questions even if they ask with 'I'. " + \
# "Answer the following question using only the data provided in the sources below. " + \
# "For tabular information return it as an html table. Do not return markdown format. "  + \
# "Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. " + \
# "If you cannot answer using the sources below, say you don't know. " + \
class RetrieveThenReadApproach(Approach):

    template = \
    """You must answer by Vietnamese. 
Assistant intelligent assistant helping user to find out which credit is best user needs through several banks in Vietnam. But you only support the bank you have data, must say don't know if you don't have.
Be brief in your answers, do not duplicate or give redundant information. The answer MUST FOLLOW its bank documents.Some documents have 2 or more languages together, it could be within a cell, quotes, brackets, next new line. Thus MUST only retrieve Vietnamese. For example "Thẻ tín dụng Visa Signature Visa Credit Card Signature" MUST SHORTEN to "Thẻ tín dụng Visa Signature". 
Answer ONLY with the facts listed in the list of sources below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below. 
If asking a clarifying question to the user would help, ask the question. MUST ASK question if there is not enough information or the question is ambiguous for e.g MUST ASK if no bank name provided, you can suggest name you have your own data.
For tabular information or making comparison question, MUST PRINT it out as an html table. DO NOT PRINT markdown format.
The source has mainly tablular and scale by horizontal, veritcal or mix, try to reach the information for the next row or column onwards.
The source must be existed, each reference source has a name followed by colon and the actual information, always include the source name for each fact you use in the response. Use square brakets to reference the source, e.g. [info1.txt]. Don't combine sources, list each source separately, e.g. [info1.txt][info2.pdf].
If the answer is a list of items, print as tabular information, e.g. a list of credit cards. 
""" \
""" \

### Example question and answer:
Question: 'Thẻ Visa Techcombank có bao nhiêu loại?'

Sources:
info1.txt: Có xxx loại thẻ tín dụng và ghi nợ Visa Techcombank.
info2.pdf: Thẻ tín dụng Techcombank Visa Signature

Answer:
Hiện tại có xxx loại thẻ tín dụng và ghi nợ Visa Techcombank, bạn có thể tham khảo ở [info1.txt][info2.pdf]

###
Question: '{q}'?

Sources:
{retrieved}

Answer:
"""

    def __init__(self, search_client: SearchClient, openai_deployment: str, sourcepage_field: str, content_field: str):
        self.search_client = search_client
        self.openai_deployment = openai_deployment
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field

    def run(self, q: str, overrides: dict) -> any:
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 3
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None

        if overrides.get("semantic_ranker"):
            r = self.search_client.search(q, 
                                          filter=filter,
                                          query_type=QueryType.SEMANTIC, 
                                          query_language="en-us", 
                                          query_speller="lexicon", 
                                          semantic_configuration_name="default", 
                                          top=top, 
                                          query_caption="extractive|highlight-false" if use_semantic_captions else None)
        else:
            r = self.search_client.search(q, filter=filter, top=top)
        if use_semantic_captions:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(" . ".join([c.text for c in doc['@search.captions']])) for doc in r]
        else:
            results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
        content = "\n".join(results)

        prompt = (overrides.get("prompt_template") or self.template).format(q=q, retrieved=content)
        completion = openai.Completion.create(
            engine=self.openai_deployment, 
            prompt=prompt, 
            temperature=overrides.get("temperature") or 0.0, 
            max_tokens=1024, 
            n=1, 
            stop=["\n"])

        return {"data_points": results, "answer": completion.choices[0].text, "thoughts": f"Question:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>')}
