from sklearn.externals import joblib
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import CustomObjectScope
from tensorflow.keras.initializers import glorot_uniform
from flask import Flask, request, jsonify
from string import digits


app = Flask(__name__)

session = tf.Session()
graph = tf.get_default_graph()
model = joblib.load('model/sklearn_pipeline.pkl')
with graph.as_default():
    with session.as_default():
        session.run(tf.global_variables_initializer())
        with CustomObjectScope({'GlorotUniform': glorot_uniform()}):
            model.named_steps['classifier'].model = load_model('model/keras_model.h5')

def remove_digits(s):
    remove_digits = str.maketrans('', '', digits)
    res = s.translate(remove_digits)
    return res


@app.route('/predict', methods=['POST'])
def infer():
    text = request.json['text']
    text = remove_digits(text)
    with graph.as_default():
            with session.as_default():
                pred = model.predict([text])
    le = LabelEncoder()
    le.fit_transform(['positive', 'negative'])
    pred = le.inverse_transform(pred)[0]
    response = {'Sentiment': pred}
    return jsonify(response)

@app.route('/')
def index():
    return "This is just an index page and nothing else!"
