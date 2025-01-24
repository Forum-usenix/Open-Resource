import requests
import csv
import random

# Google Translate API parameters
API_KEY = "your Google API Key"  # Replace with your actual API key
url = "https://translation.googleapis.com/language/translate/v2"

# Call Google Translate API
def translate_text(target, content):
    language_type = ""  # Source language; leave empty for auto-detection
    data = {
        'key': API_KEY,
        'source': language_type,
        'target': target,
        'q': content,
        'format': "text"
    }
    
    try:
        response = requests.post(url, data=data)
        res = response.json()

        if 'data' in res and 'translations' in res['data']:
            translated_text = res['data']['translations'][0]['translatedText']
            print(translated_text)
            return translated_text
        else:
            print(f"Translation API Error: {res}")
            return ""
    except Exception as e:
        print(f"Error calling translation API: {e}")
        return ""

# Read and filter CSV data
def read_and_filter_csv(file_path):
    rows = []

    with open(file_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            response = row.get('response', '').strip().lower()
            selftext = row.get('selftext', '').replace('\n', ' ')  # Remove newline characters

            if response == 'yes':
                row['selftext'] = selftext
                rows.append(row)

    return rows

# Process and translate filtered rows
def process_and_translate(filtered_rows, output_folder):
    for i, row in enumerate(filtered_rows, 1):
        orig_text = row['selftext']
        translated_text = translate_text('en', orig_text)  # Translate to English

        # Write to txt file
        file_name = f"{output_folder}/_{i}_c.txt"
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write("Origin:\n")
            for key, value in row.items():
                f.write(f"{key}: {value}\n")
            f.write(f"\nTranslated Text:\n{translated_text}\n")

# Main function
def main():
    file_path = 'your/csv/file/path'
    output_folder = 'your/output/folder'

    # Read and filter data
    rows = read_and_filter_csv(file_path)
    print(f"Number of filtered rows: {len(rows)}")

    # Process and translate qualifying data
    process_and_translate(rows, output_folder)

if __name__ == '__main__':
    main()