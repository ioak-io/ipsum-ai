import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load pre-trained GPT-2 model and tokenizer
model_name = 'gpt2'
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Generate sentences based on input text
def generate_sentences(input_text, num_sentences=5):
  # Tokenize the input text
  input_ids = tokenizer.encode(input_text, add_special_tokens=True, return_tensors='pt')
  input_ids = input_ids.to(device)

  # Generate sentences
  generated_sentences = []
  with torch.no_grad():
    for _ in range(num_sentences):
      outputs = model.generate(
          input_ids=input_ids,
          max_length=100,
          num_return_sequences=1,
          pad_token_id=tokenizer.eos_token_id,
          do_sample=True,
          temperature=0.7
      )
      generated_sentence = tokenizer.decode(outputs[0], skip_special_tokens=True)
      generated_sentences.append(generated_sentence)

  return generated_sentences
