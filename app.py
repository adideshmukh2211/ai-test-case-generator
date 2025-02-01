from flask import Flask, render_template, request, jsonify
import os
from test_generator.generator import TestCaseGenerator
from test_generator.ml_trainer import TestCaseTrainer

app = Flask(__name__)
generator = TestCaseGenerator()

@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/train', methods=['POST'])
def train_model():
    """Endpoint to trigger model training"""
    try:
        trainer = TestCaseTrainer()
        trainer.train(num_epochs=5)
        trainer.save_model(os.path.join(os.path.dirname(__file__), 'test_generator', 'trained_model'))
        return jsonify({'message': 'Model training completed successfully'})
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to train model'
        }), 400

if __name__ == '__main__':
    # Download spacy model if not already downloaded
    import spacy.cli
    try:
        spacy.load('en_core_web_sm')
    except OSError:
        spacy.cli.download('en_core_web_sm')
    
    app.run(debug=True)
