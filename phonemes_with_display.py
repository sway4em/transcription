from PIL import Image
import time
import os

# Define the phoneme categories based on the image provided
phoneme_categories = {
    'A': 'AI',
    'E': 'E',
    'I': 'AI',
    'O': 'O',
    'U': 'U',
    'W': 'W and Q',
    'Q': 'W and Q',
    'M': 'M, B and P',
    'B': 'M, B and P',
    'P': 'M, B and P',
    'F': 'F and V',
    'V': 'F and V',
    'L': 'L',
    'C': 'C, D, G, K, N, R, S, T, H, Y',
    'D': 'C, D, G, K, N, R, S, T, H, Y',
    'G': 'C, D, G, K, N, R, S, T, H, Y',
    'K': 'C, D, G, K, N, R, S, T, H, Y',
    'N': 'C, D, G, K, N, R, S, T, H, Y',
    'R': 'C, D, G, K, N, R, S, T, H, Y',
    'S': 'C, D, G, K, N, R, S, T, H, Y',
    'T': 'C, D, G, K, N, R, S, T, H, Y',
    'H': 'C, D, G, K, N, R, S, T, H, Y',
    'Y': 'C, D, G, K, N, R, S, T, H, Y',
    'other': 'Other'
}

# Dictionary with file names for the phoneme images
phoneme_image_files = {
    'AI': 'AI.png',
    'E': 'E.png',
    'O': 'O.png',
    'U': 'U.png',
    'W and Q': 'WQ.png',
    'M, B and P': 'MBP.png',
    'L': 'L.png',
    'F and V': 'FV.png',
    'C, D, G, K, N, R, S, T, H, Y': 'CDGKNRSTHY.png',
    'Other': 'Other.png'
}

# Function to display the image corresponding to the phoneme
def show_phoneme_image(phoneme, base_path):
    file_name = phoneme_image_files.get(phoneme, 'Other.png')
    image_path = os.path.join(base_path, file_name)
    with Image.open(image_path) as img:
        img.show()
        time.sleep(1)

# Function to classify text into phoneme types and display images
def classify_and_show_phonemes(text, base_path):
    text = text.upper()
    for char in text:
        if char.isalpha():
            phoneme_type = next((category for category, members in phoneme_categories.items() if char in members), 'other')
            print(char, phoneme_type)
            show_phoneme_image(phoneme_type, base_path)
        else:
            show_phoneme_image('other', base_path)

if __name__ == "__main__":
    # Define the base path to the folder containing the phoneme images
    base_image_path = 'phoneme_pics'  # You need to update this path
    input_text = input("Enter a sentence: ")
    classify_and_show_phonemes(input_text, base_image_path)
