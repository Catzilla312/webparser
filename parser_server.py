from flask import Flask, request, jsonify
from parser_1 import scrapeProducts

app = Flask(__name__)

@app.route('/parser', methods=['GET'])
def parser():
    print("STARTED PARSING")
    result = scrapeProducts()
    print("ENDED PARSING")    
    return jsonify({'message': result})

# @app.route('/add', methods=['POST'])
# def add():
#     data = request.get_json()
#     if not data or 'a' not in data or 'b' not in data:
#         return jsonify({'error': 'Invalid payload.'}), 400
#     a = data['a']
#     b = data['b']
#     try:
#         result = int(a) + int(b)
#         return jsonify({'result': result})
#     except ValueError:
#         return jsonify({'error': 'Invalid parameters.'}), 400

if __name__ == '__main__':
    app.run(debug=True)