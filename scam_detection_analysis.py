from openai import OpenAI
import pandas as pd
from collections import Counter
import os
import re

client = OpenAI(
    api_key="your api keys",
    # Replace with the entry point for aihubmix
    base_url="https://api.chatanywhere.tech/v1"
)

system_prompt = \
"""You are an experienced cybercrime investigator with expertise in fraud detection and prevention. Analyze the [post content] to determine if it qualifies as a victim's confirmed scam experience based on these criteria:

1. The post explicitly states they were definitively involved in a scam.
2. The post includes a detailed description of the scam, including but not limited to the process of being scammed, any incurred losses, and specific details or evidence.

If both criteria are met, output Yes. Otherwise, output No.

Output format: Yes/No""" 

example_query_pos = \
"""[post content]

Hello there… I’m a 19 year old college student who is living in Malaysia. I was scammed by someone who offered me $2000. There’s an American woman who dm me on Instagram saying she wants to cash me up with Cash App, but I told her I don’t have Cash App. I have PayPal and Wise only. She told me to give her my PayPal link, and I did… She then said I need to pay her $26/25 to receive the money. She later gave me a website to buy gift cards and told me to send her the code. After I sent the code, she asked for my email to send the payment, claiming I needed to pay $50 to authorize it. I refused, but she pressured me to buy more gift cards. I felt embarrassed and scared to tell my family. I removed my bank account from PayPal to protect myself...

"""

example_output_pos = \
"""[parsing process]

The post describes a clear case of scam victimization. The poster explicitly states they were scammed while attempting to receive $2000. The scam involved multiple payments and gift cards, with the poster expressing feelings of embarrassment and regret. The detailed description meets both criteria for confirmation.

[result]
Yes"""

example_query_neg = \
"""[post content] 

1 hour ago I realized someone changed my password, email, and phone number on my Netflix account. They even subscribed to a £5 plan using my card. How is it possible they did all this without confirmation messages? I don't know what to do. I've talked to a Netflix assistant, changed my password, and requested a refund.

"""

example_output_neg = \
"""[parsing process]

The post details unauthorized changes to the user's Netflix account and an unexpected subscription. However, it lacks an explicit statement of being scammed and a clear narrative of the scam process, failing to meet the criteria for a confirmed scam experience.

[result]
No"""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": example_query_pos},
    {"role": "assistant", "content": example_output_pos},
    {"role": "user", "content": example_query_neg},
    {"role": "assistant", "content": example_output_neg}
]

input_file = '/your/csv/file/path'  # Input file path
output_file = '/your/output/file/path'  # Output file path

# Initialize results list
df = pd.read_csv(input_file)

# Check if output file exists
if os.path.exists(output_file):
    output_df = pd.read_csv(output_file)
    processed_indices = set(output_df['index'])  # Track processed rows
else:
    output_df = pd.DataFrame(columns=list(df.columns) + ['index', 'response'])
    processed_indices = set()

# Iterate through each row in the input file
for index, row in df.iterrows():
    # Skip already processed rows
    if index in processed_indices:
        print(f"Skipping row {index} as it already exists in output.")
        continue
    
    element_example = row['selftext']  # Get current row content
    if not isinstance(element_example, str):
        element_example = str(element_example)  # Convert to string
        if not element_example.strip():
            print(f"Skipping row {index} due to empty content.")
            continue
        
    try:
        # Call API
        chat_completion = client.chat.completions.create(
            messages=messages + [{"role": "user", "content": element_example}],
            temperature=0.8,
            n=5,  # Generate one result
            top_p=0.95,
            model="gpt-4o-mini",
        )

        responses = [chat_completion.choices[i].message.content.strip() for i in range(5)]

        judgments = []
        for response in responses:
            match = re.findall(r"\[result\]\n(Yes|No)", response)
            if match:
                judgments.append(match)

        # Convert inner lists to tuples for counting
        judgments = [tuple(judgment) for judgment in judgments]

        # Count occurrences of judgments
        judgment_counts = Counter(judgments)
        most_common_judgment, count = judgment_counts.most_common(1)[0]

        # Output final result
        print("【Most common judgment】:", most_common_judgment[0])
        print("【Count】:", count)

    except Exception as e:
        print(f"Error processing row {index}: {e}")
        response = "Error occurred"
    
    new_row = {**row.to_dict(), 'index': index, 'response': most_common_judgment[0]}
    new_row_df = pd.DataFrame([new_row])  # Create a one-row DataFrame
    output_df = pd.concat([output_df, new_row_df], ignore_index=True)  # Append results
    
    # Write updated DataFrame to the file
    output_df.to_csv(output_file, index=False)
    print(f"Processed row {index} and saved response.")
