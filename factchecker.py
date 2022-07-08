import lorem
from transformers import pipeline

def CheckFact(claim):
    # Process the claim
    explanations = []
    textGenerator = pipeline("text-generation")
    print(textGenerator("Hello, I am", max_length=30, num_return_sequence=2))
    for i in range(3):
        explanations.append(lorem.sentence())
    return explanations