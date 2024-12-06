import os
from openai import AzureOpenAI
from openai.types.chat import ChatCompletion

# Azure OpenAI settings
client = AzureOpenAI(
    api_key = 'a3316ecd521d43ad9e5bcc6ce644c896',  
    api_version = "2023-05-15",
    azure_endpoint = "https://abutair-openai.openai.azure.com/"
)

def list_available_models():
    try:
        models = client.models.list()
        print("Available models:")
        for model in models:
            print(f"- {model.id}")
    except Exception as e:
        print(f"Error listing models: {str(e)}")

def read_text_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file: {str(e)}")
        return ""

def split_text(text: str, chunk_size: int = 4000) -> list:
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def extract_poetry_from_chunk(chunk: str) -> str:
    try:
        response: ChatCompletion = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": "You are a poetry expert. Extract only the poetic lines from the given text. and don't tranlsate or change any of them just extract what you think it poetry."},
                {"role": "user", "content": f"Extract only the poetry from the following text:\n\n{chunk}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in extract_poetry_from_chunk: {str(e)}")
        return ""

def extract_poetry(text: str) -> str:
    chunks = split_text(text)
    extracted_poetry = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1} of {len(chunks)}...")
        poetry = extract_poetry_from_chunk(chunk)
        if poetry:
            extracted_poetry.append(poetry)
    return "\n\n".join(extracted_poetry)

def save_to_file(content: str, output_path: str) -> None:
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Poetry successfully saved to {output_path}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")

def main(input_path: str, output_path: str) -> None:
    list_available_models()

    # Read text from file
    input_text = read_text_file(input_path)
    
    if not input_text:
        print("Failed to read text from the input file. Please check the file and its permissions.")
        return

    # Extract poetry using Azure OpenAI
    poetry = extract_poetry(input_text)
    
    if poetry:
        # Save poetry to file
        save_to_file(poetry, output_path)
    else:
        print("No poetry was extracted. Check the Azure OpenAI service response.")

if __name__ == "__main__":
    input_path = "Kotobati_extracted.txt"  # Change this to your input text file name
    output_path = "poetry.txt"
    main(input_path, output_path)