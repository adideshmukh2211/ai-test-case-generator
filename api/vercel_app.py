from flask import Flask, request, jsonify, send_from_directory
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from test_generator.generator import TestCaseGenerator

app = Flask(__name__)
generator = TestCaseGenerator()

# Serve static files from the templates directory
@app.route('/')
def index():
    return send_from_directory('../templates', 'index.html')

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.json.get('prompt', '')
    framework = request.json.get('framework', 'robot')  # Default to Robot Framework
    
    try:
        # Generate test case
        test_case = generator.generate_test_case(prompt, framework)
        
        # Get component type from prompt for XPath guide
        component_type = 'email' if 'email' in prompt.lower() else \
                        'password' if 'password' in prompt.lower() else \
                        'button' if 'button' in prompt.lower() else None
        
        xpath_guide = generator.get_xpath_guide(component_type) if component_type else ""
        
        return jsonify({
            'test_case': test_case,
            'xpath_guide': xpath_guide,
            'framework': framework
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate test case. Please try again with a different prompt.'
        }), 400

# Error handler for 404
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 3000)))
