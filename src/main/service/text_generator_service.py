from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Load pre-trained GPT-2 model and tokenizer
model_name = "gpt2"  # You can use other variants of GPT-2 as well
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name,
                                        pad_token_id=tokenizer.eos_token_id)


# Generate sentences based on input text
def generate_sentences(input_text):
  inputs = tokenizer.encode(input_text, return_tensors='pt')
  outputs = model.generate(inputs, max_length=800, do_sample=True, temperature=1, top_k=50)
  text = tokenizer.decode(outputs[0], skip_special_tokens=True)
  sentences = text.split('. ')
  if len(sentences) > 1:
    text_without_last_sentence = '. '.join(sentences[:-1]) + '.'
  else:
    text_without_last_sentence = text
  print(text_without_last_sentence)

  return text_without_last_sentence
