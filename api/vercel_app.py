from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import sys
import traceback

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_generator.generator import TestCaseGenerator

app = Flask(__name__, 
           static_folder='../templates/static',
           template_folder='../templates')

generator = TestCaseGenerator()

@app.route('/')
def index():
    try:
        return send_from_directory('../templates', 'index.html')
    except Exception as e:
        app.logger.error(f"Error serving index.html: {str(e)}")
        return jsonify({
            'error': 'Failed to serve index page',
            'details': str(e)
        }), 500

@app.route('/static/<path:path>')
def serve_static(path):
    try:
        return send_from_directory('../templates/static', path)
    except Exception as e:
        app.logger.error(f"Error serving static file {path}: {str(e)}")
        return jsonify({
            'error': 'Failed to serve static file',
            'details': str(e)
        }), 500

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No JSON data received',
                'message': 'Please provide prompt and framework in JSON format'
            }), 400

        prompt = data.get('prompt', '')
        framework = data.get('framework', 'robot')

        if not prompt:
            return jsonify({
                'error': 'No prompt provided',
                'message': 'Please provide a test case description'
            }), 400

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
        app.logger.error(f"Error generating test case: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'Failed to generate test case. Please try again.',
            'details': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred',
        'details': str(e)
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
