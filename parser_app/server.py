from flask import Flask, request, jsonify
from index_parser import getProductFromDb
from scheduler import run_scheduler
import sys
import traceback

def handle_exception(exc_type, exc_value, exc_traceback):
    # Log the exception
    traceback_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    with open('error.log', 'a') as f:
        f.write(traceback_str)

    # Display a user-friendly error message
    print("Oops, something went wrong. Please try again later.")

sys.excepthook = handle_exception



app = Flask(__name__)

run_scheduler()

@app.route('/getProductFromDbRoute', methods=['GET'])
def getProductFromDbRoute():
    print("getProductFromDb")
    getProductFromDb()
    return jsonify({'message': "done"})

if __name__ == '__main__':
    app.run(debug=True)