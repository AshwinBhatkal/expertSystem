from flask import Flask, render_template
import os, subprocess

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/question/<name>')
def get_question(name):
    nameWithDQuotes = "{0}".format(name)
    # return "The possible answers for your query are as below : 1 . ['f-a-5mIBNuJyU2brNiFk', 'Angular is the underlying framework that powers Ionic.'] 2 . ['aua-5mIBNuJyU2brNiEl', 'Check out “Where does the Ionic Framework fit in?” to get a good understanding of Ionic’s core philosophy and goals..'] 3 . ['tua-5mIBNuJyU2brpiHD', 'Ionic comes with the same 700+ Ionicons icons we’ve all come to know and love..'] 4 . ['uOa-5mIBNuJyU2brpiHI', 'Active icons are typically full and thick, where as inactive icons are outlined and thin.'] 5 . ['-Oa-5mIBNuJyU2brrSH7', 'Storage uses a variety of storage engines underneath, picking the best one available depending on the platform..']"
    return subprocess.check_output(['python3', '-m', 'expertSystemwoFeedback', nameWithDQuotes])
    
@app.route('/feedback/<id>')
def get_feedback(id):
    return subprocess.check_output(['python3', 'feedback.py', id])

if __name__ == '__main__':
    app.run(host='localhost', port=8080)
