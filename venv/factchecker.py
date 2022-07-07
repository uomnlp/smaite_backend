import lorem

def CheckFact(claim):
    # Process the claim
    explanations = []
    for i in range(3):
        explanations.append(lorem.sentence())
    return explanations