from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('startup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/startup')
def startup():
    return render_template('startup.html')

@app.route('/main')
def mb_test():
    return render_template("main.html", Authenticated=True, Text=request.remote_addr)

@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", status_code=404, error_message="Page not found.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)