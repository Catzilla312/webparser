from flask import Flask, request, jsonify
from parser import scrapeProducts,getProductFromDb
from scheduler import run_scheduler
app = Flask(__name__)
run_scheduler()

@app.route('/parser', methods=['GET'])
def parser():
    print("STARTED PARSING")
    result = scrapeProducts()
    print("ENDED PARSING")    
    return jsonify({'message': result})

@app.route('/getProductFromDbRoute', methods=['GET'])
def getProductFromDbRoute():
    print("getProductFromDb")
    getProductFromDb()
    return jsonify({'message': "done"})

if __name__ == '__main__':
    app.run(debug=True)