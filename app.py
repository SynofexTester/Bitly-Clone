from flask import Flask, render_template, request, redirect, abort
from models import db, URL
from utils import generate_short_code
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        original_url = request.form['original_url']
        if not original_url:
            return render_template('index.html', error="URL is required")
        
        # Check if URL already exists? (Optional, maybe just create new)
        # For this version, let's just create a new one to allow duplicates or tracking
        
        short_code = generate_short_code()
        # Ensure uniqueness (simple loop)
        while URL.query.filter_by(short_code=short_code).first():
            short_code = generate_short_code()
            
        new_url = URL(original_url=original_url, short_code=short_code)
        db.session.add(new_url)
        db.session.commit()
        
        short_url = request.host_url + short_code
        return render_template('index.html', short_url=short_url)
        
    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url_entry = URL.query.filter_by(short_code=short_code).first()
    if url_entry:
        return redirect(url_entry.original_url)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
