import eng_to_ipa as p

# Define the mapping
mouth_shape_map = {
    'AI': ['A', 'I'],
    'EOU': ['E', 'O', 'U'],
    'WQ': ['W', 'Q'],
    'MBP': ['M', 'B', 'P'],
    'CDGKNRSYZ': ['C', 'D', 'G', 'K', 'N', 'R', 'S', 'Y', 'Z'],
    'CDGJKRSYZ': ['C', 'D', 'G', 'J', 'K', 'N', 'R', 'S', 'Y', 'Z'],
    'FV': ['F', 'V'],
    'Th': ['TH'],
    'L': ['L'],
    'Rest': []
}

# Convert a phoneme to a mouth shape
def phoneme_to_mouth_shape(phoneme):
    for shape, phonemes in mouth_shape_map.items():
        if phoneme in phonemes:
            return shape
    return 'Rest'

# Convert text to mouth shapes
def text_to_mouth_shapes(text):
    ipa = p.convert(text)
    mouth_shapes = [phoneme_to_mouth_shape(ph) for ph in ipa.split()]
    return mouth_shapes

# Example usage
text = input("Enter a sentence: ")
mouth_shapes = text_to_mouth_shapes(text)
print(mouth_shapes)
