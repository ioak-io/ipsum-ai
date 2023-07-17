from flask import Blueprint, jsonify, request
import src.main.service.similarity_service as similarity_service

similarity_controller = Blueprint('similarity_controller', __name__)

# https://www.kaggle.com/code/rowhitswami/keywords-extraction-using-tf-idf-method/input?select=stopwords.txt


@similarity_controller.route('/train', methods=['GET'])
def train(space):
    return similarity_service.train(space)


@similarity_controller.route('/predict', methods=['GET'])
def predict(space):
    return similarity_service.predict(space, "et libero sit himenaeos phasellus blandit aliquam venenatis aptent. vivamus cursus posuere metus auctor pulvinar vehicula risus adipiscing vehicula pulvinarin mi faucibus. urna ultricies cras dapibus taciti dictum tincidunt. mauris scelerisque purus conubia faucibus primis praesent in velit. risus phasellus natoque mattis rutrumaliquam id accumsan ipsum torquent. litora arcu in magnis nostra justo hendrerit risus mattis risus hendrerit habitasse habitasse sodales. morbi erat fermentum class curae ipsum porttitor lacus at montes varius amet in enim. vestibulum tellus praesent nascetur tortor dictumst quam congue cras nisi adipiscing. nascetur malesuada lobortis luctus neque magnis gravida penatibus velit pulvinarin curae dictumst gravida. dapibus non mauris ridiculus ac in ultricies. dictum ullamcorper vitae aliquam elit euismod dis a nascetur odio quam rutrum")


@similarity_controller.route('/populate-keywords', methods=['GET'])
def populate_keywords(space):
    return similarity_service.populate_keywords(space)


@similarity_controller.route('/populate-links', methods=['GET'])
def populate_links(space):
    return similarity_service.populate_links(space)


@similarity_controller.route('/populate', methods=['GET'])
def populate(space):
    similarity_service.populate_keywords(space)
    return similarity_service.populate_links(space)

@similarity_controller.route('/populate/<reference>', methods=['GET'])
def populate_for_note(space, reference):
    return similarity_service.populate_for_note(space, reference)
