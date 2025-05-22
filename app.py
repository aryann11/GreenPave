from flask import Flask, render_template
from feature1.app import feature1_bp
from feature2.app import feature2_bp
from feature3.app import feature3_bp
from feature4.app import feature4_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(feature1_bp, url_prefix='/feature1')
app.register_blueprint(feature2_bp, url_prefix='/feature2')
app.register_blueprint(feature3_bp, url_prefix='/feature3')
app.register_blueprint(feature4_bp, url_prefix='/feature4')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)