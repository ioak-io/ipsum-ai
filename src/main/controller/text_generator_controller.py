from flask import Blueprint, request, jsonify

from src.main.service import similarity_service
from src.main.service.text_generator_service import generate_sentences

text_generator_controller = Blueprint('text_generator_controller', __name__)

# https://www.kaggle.com/code/rowhitswami/keywords-extraction-using-tf-idf-method/input?select=stopwords.txt


@text_generator_controller.route('/generate', methods=['POST'])
def generate_text():
  data = request.get_json()
  input_text = data.get('input_text', '')

  generated_sentences = generate_sentences(input_text)
  response = {'generated_sentences': generated_sentences}
  return jsonify(response)
