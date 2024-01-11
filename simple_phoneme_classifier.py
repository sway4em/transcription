# Define the phoneme categories based on the image provided
phoneme_categories = {
    'A': 'AI',
    'E': 'E',
    'I': 'AI',
    'O': 'O',
    'U': 'U',
    'WQ': 'W and Q',
    'MBP': 'M, B and P',
    'FV': 'F and V',
    'L': 'L',
    'CDGKNRSTHY': 'C, D, G, K, N, R, S, T, H, Y',
    'other': 'Other'
}

# Create a function to classify text into phoneme types
def classify_phonemes(text):
    # Normalize the text to uppercase
    text = text.upper()
    # Initialize a result list to hold the classification of each character
    classification_result = []
    
    # Classify each character in the text
    for char in text:
        char_classified = False
        for category, members in phoneme_categories.items():
            if char in members:
                classification_result.append((char, category))
                char_classified = True
                break
        
        if not char_classified:
            # If the character is not found in any category, classify it as 'other'
            classification_result.append((char, phoneme_categories['other']))
    
    return classification_result

# Example usage
sample_text = input("Enter a sentence: ") 
out = classify_phonemes(sample_text)
print(out)