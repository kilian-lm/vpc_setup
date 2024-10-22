from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__, static_folder='static')

# Configuration for APIs (use environment variables)
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')
HAVEIBEENPWNED_API_KEY = os.environ.get('HAVEIBEENPWNED_API_KEY')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/make_yourself_aware')
def make_yourself_aware():
    return render_template('make_yourself_aware.html')

@app.route('/monitor')
def monitor():
    return render_template('monitor.html')

@app.route('/save_encrypt')
def save_encrypt():
    return render_template('save_encrypt.html')

@app.route('/act')
def act():
    return render_template('act.html')

@app.route('/coders')
def coders():
    return render_template('coders.html')

# Existing routes for search and breach checking...

@app.route('/search_name', methods=['POST'])
def search_name():
    name = request.form['name']
    results = google_search(name)
    return render_template('search_results.html', results=results, query=name)

def google_search(query):
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}'
    response = requests.get(url)
    return response.json().get('items', [])

@app.route('/check_breach', methods=['POST'])
def check_breach():
    email = request.form['email']
    breaches = haveibeenpwned(email)
    return render_template('breach_results.html', breaches=breaches, email=email)

def haveibeenpwned(email):
    headers = {
        'hibp-api-key': HAVEIBEENPWNED_API_KEY,
        'user-agent': 'PersonalSecurityDashboard'
    }
    url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

if __name__ == '__main__':
    app.run(debug=True)
