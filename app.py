from flask import Flask, render_template, request, jsonify
from robot.api import TestSuite
import os

app = Flask(__name__)

def generate_test_cases(prompt):
    # Create test cases based on the prompt
    suite = TestSuite('Generated Tests')
    test = suite.tests.create(f'Test: {prompt}')
    
    if 'email' in prompt.lower():
        test.keywords.create('Open Browser', args=['${URL}', 'chrome'])
        test.keywords.create('Maximize Browser Window')
        test.keywords.create('Input Text', args=['${email_field}', '${test_email}'])
        test.keywords.create('Click Element', args=['${submit_button}'])
        test.keywords.create('Page Should Contain', args=['${success_message}'])
        test.keywords.create('Close Browser')
        
        xpath_guide = """
To find XPath for email validation:
1. Right-click on the email input field
2. Click 'Inspect'
3. In the developer tools, right-click on the highlighted HTML
4. Go to Copy > Copy XPath
Common XPath patterns for email fields:
- //input[@type='email']
- //input[@name='email']
- //input[contains(@class, 'email')]
"""
        return {
            'test_case': str(test),
            'xpath_guide': xpath_guide
        }
    
    # Add more test case patterns here
    return {'test_case': str(test), 'xpath_guide': ''}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt', '')
    result = generate_test_cases(prompt)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
