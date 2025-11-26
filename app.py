from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('startup.html')

@app.route('/login')
def login():
    print(request.args)

    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/startup')
def startup():
    return render_template('startup.html')

@app.route('/main')
def mb_test():
    return render_template("main.html", Authenticated=True)

if __name__ == "__main__":
    app.run(debug=True)