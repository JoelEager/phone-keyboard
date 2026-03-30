from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '''
        <form action="/submit" method="post">
            <textarea name="text" rows="10" cols="30"></textarea><br>
            <input type="submit" value="Submit">
        </form>
    '''

@app.route('/submit', methods=['POST'])
def submit():
    text = request.form.get('text')
    escaped_text = escape(text)
    return f'Received: {escaped_text}'

def main():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()
