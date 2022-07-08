import lorem
from transformers import pipeline

def CheckFact(claim, mode):
    # Process the claim
    explanations = []
    if(mode == "summarize"):
        summarizer = pipeline("summarization")
        result = summarizer(claim, min_length=5, max_length=30)
        for element in result:
            explanations.append(element['summary_text'])
    elif(mode == "generate"):
        textGenerator = pipeline("text-generation")
        result = textGenerator(claim, max_length=30, num_return_sequences=2)
        for element in result:
            explanations.append(element['generated_text'])
    return explanations
    