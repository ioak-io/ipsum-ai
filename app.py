from flask import Flask
import nltk

from src.main.controller.similarity_controller import similarity_controller

# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')

app = Flask(__name__)
app.register_blueprint(similarity_controller,
                       url_prefix='/api/similarity/<space>')


@app.route('/')
def index():
    return 'Hello, World!'
