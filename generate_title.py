from transformers import T5ForConditionalGeneration, T5Tokenizer
import language_tool_python

tool = language_tool_python.LanguageTool('en-US')

# Load the fine-tuned model and tokenizer
model = T5ForConditionalGeneration.from_pretrained("./fine-tuned-t5")
tokenizer = T5Tokenizer.from_pretrained("./fine-tuned-t5")

def generate_title(description):
    # Refined prompt for better clarity
    input_text = f"Create a catchy and relevant YouTube title for the following description: {description}"
    inputs = tokenizer(input_text, return_tensors="pt", max_length=128, truncation=True)

    # Generate a title with adjusted parameters
    output = model.generate(
        **inputs,
        max_length=50,
        top_p=0.9,
        top_k=50,
        temperature=0.7,
        num_return_sequences=1
    )

    # Decode the generated title
    title = tokenizer.decode(output[0], skip_special_tokens=True)
    return title

def check_grammar(title):
    matches = tool.check(title)
    corrected_title = language_tool_python.utils.correct(title, matches)
    return corrected_title

# User input
description = input("Please enter a description for generating a YouTube title: ")
generated_title = generate_title(description)
corrected_title = check_grammar(generated_title)
print(f"Generated title: {corrected_title}")
