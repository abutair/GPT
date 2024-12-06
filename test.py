import re

def remove_diacritics(text):
    """
    Remove Arabic diacritical marks from text.
    
    Args:
        text (str): Text containing Arabic diacritics
    
    Returns:
        str: Text with diacritics removed
    """
    # Arabic diacritics to remove
    diacritics = [
        '\u064B',  # Fathatan
        '\u064C',  # Dammatan
        '\u064D',  # Kasratan
        '\u064E',  # Fatha
        '\u064F',  # Damma
        '\u0650',  # Kasra
        '\u0651',  # Shadda
        '\u0652',  # Sukun
        '\u0653',  # Maddah Above
        '\u0654',  # Hamza Above
        '\u0655',  # Hamza Below
        '\u0656',  # Subscript Alef
        '\u0657',  # Inverted Damma
        '\u0658',  # Mark Noon Ghunna
        '\u0659',  # Zwarakay
        '\u065A',  # Vowel Sign Small V Above
        '\u065B',  # Vowel Sign Inverted Small V Above
        '\u065C',  # Vowel Sign Dot Below
        '\u065D',  # Reversed Damma
        '\u065E',  # Fatha with Two Dots
        '\u065F',  # Wavy Hamza Below
        '\u0670',  # Superscript Alef
    ]
    
    # Create a translation table for removal
    remove_chars = str.maketrans('', '', ''.join(diacritics))
    return text.translate(remove_chars)

def extract_poetry_lines(text):
    """
    Extract poetry lines from Arabic text, removing diacritics and explanatory content.
    
    Args:
        text (str): Input text containing mixed content including poetry
    
    Returns:
        list: List of extracted poetry lines
    """
    # Split text into lines
    lines = text.split('\n')
    
    poetry_lines = []
    
    # Common patterns that indicate poetry lines
    poetry_patterns = [
        r'^-\s.*',  # Lines starting with dash
        r'.*[،؛!?].*',  # Lines containing Arabic punctuation
        r'.*[اإأآؤئءيىةوه]\s+[اإأآؤئءيىةوه].*',  # Lines with Arabic word patterns
    ]
    
    # Patterns that indicate explanatory or definitional content
    explanation_patterns = [
        r'^.*:\s.*$',  # Lines containing definitions
        r'^.*\s*[=-]\s*.*$',  # Lines with equals or dash as separator
        r'.*القول.*',  # Common explanation marker
        r'.*يقول.*',  # Another explanation marker
        r'.*معنى.*',  # Meaning indicator
        r'.*تفسير.*',  # Explanation indicator
        r'.*شرح.*',  # Commentary indicator
        r'^.*\s*[،:]\s*[^،]*$',  # Single definition pattern
        r'.*التعبير.*',  # Expression explanation
        r'.*المقصود.*',  # Intended meaning
        r'.*التعريف.*',  # Definition marker
        r'.*أي.*:.*',  # Explanation using 'meaning'
        r'.*شبه.*',  # Similarity expressions
        r'.*مثل.*',  # Comparison expressions
    ]
    
    # Words and phrases to filter out
    filter_phrases = [
        'وشبه الشيء منجذب إليه',
        'شبه الشيء',
        'منجذب إليه',
        'القادح',
        'التعبير',
        'يعني',
        'شرح',
        'import', 'def', 'print', 'return', 'class',
        'function', 'variable', 'string', 'int',
        'file', 'open', 'read', 'write',
    ]
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Skip lines with filtered phrases
        if any(phrase in remove_diacritics(line.lower()) for phrase in filter_phrases):
            continue
            
        # Skip explanatory lines
        if any(re.search(pattern, line) for pattern in explanation_patterns):
            continue
        
        # Check if line matches any poetry pattern
        is_poetry = any(re.search(pattern, line) for pattern in poetry_patterns)
        
        # Additional checks for poetry characteristics
        if (
            is_poetry
            or (len(line.split()) >= 3 and any(c.isalpha() for c in line))  # Minimum word count
            or ('،' in line or '؛' in line)  # Arabic punctuation
            or re.search(r'[\u0600-\u06FF]{5,}', line)  # Continuous Arabic text
        ):
            # Additional filtering
            if not any(char in line for char in ':=-'):  # Skip definitional lines
                poetry_lines.append(line)
    
    # Post-process to remove metadata and clean text
    cleaned_lines = []
    for line in poetry_lines:
        # Remove line numbers and references
        line = re.sub(r'^\d+[\s-]*', '', line)
        line = re.sub(r'\d+$', '', line)
        
        # Remove brackets and parentheses with their content
        line = re.sub(r'\[.*?\]', '', line)
        line = re.sub(r'\(.*?\)', '', line)
        
        # Remove leading dashes and whitespace
        line = re.sub(r'^[-\s]+', '', line)
        
        # Remove quotation marks
        line = line.replace('"', '').replace('"', '').replace('"', '')
        
        # Remove explanatory prefixes
        line = re.sub(r'^[^،]*:\s*', '', line)
        
        # Remove diacritics
        line = remove_diacritics(line)
        
        # Only keep lines that still have content after cleaning
        if line.strip() and len(line.strip()) > 10:  # Minimum length check
            cleaned_lines.append(line.strip())
    
    return cleaned_lines

def main():
    # Read the file content
    with open('poetry.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract poetry lines
    poetry_lines = extract_poetry_lines(content)
    
    # Write results to output file
    with open('extracted_poetry.txt', 'w', encoding='utf-8') as file:
        for line in poetry_lines:
            file.write(line + '\n')
    
    # Print some example lines for verification
    print(f"\nExtracted {len(poetry_lines)} poetry lines. Here are some examples:")
    for line in poetry_lines[:5]:
        print(f"- {line}")

if __name__ == "__main__":
    main()