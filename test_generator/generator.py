import os
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import spacy
from dotenv import load_dotenv

load_dotenv()

class TestCaseGenerator:
    def __init__(self):
        self.model_path = os.getenv('MODEL_PATH', 'Salesforce/codet5-base')
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Load pre-trained model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
        self.model.to(self.device)
        
        # Load spaCy model for text processing
        self.nlp = spacy.load('en_core_web_sm')
        
        # Framework templates
        self.supported_frameworks = {
            'robot': self._generate_robot_framework,
            'pytest': self._generate_pytest,
            'unittest': self._generate_unittest
        }
    
    def generate_test_case(self, prompt, framework='robot'):
        """Generate test cases based on the prompt and selected framework"""
        # Process the prompt
        doc = self.nlp(prompt)
        
        # Extract key information
        actions = [token.text for token in doc if token.dep_ == 'ROOT']
        components = [token.text for token in doc if token.dep_ in ('dobj', 'pobj')]
        
        # Create input text for the model
        input_text = f"Generate {framework} test: {prompt}"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt').to(self.device)
        
        # Generate test steps
        outputs = self.model.generate(
            input_ids,
            max_length=200,
            num_return_sequences=1,
            temperature=0.7
        )
        
        # Decode and format the output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Convert to specified framework format
        generator = self.supported_frameworks.get(framework, self._generate_robot_framework)
        return generator(generated_text, components)
    
    def _generate_robot_framework(self, test_steps, components):
        """Convert test steps to Robot Framework format"""
        template = """*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
{test_name}
    [Documentation]    {description}
{steps}"""
        
        formatted_steps = "\n".join([f"    {step}" for step in test_steps.split('\n')])
        return template.format(
            test_name="Test " + " ".join(components).title(),
            description=test_steps.split('\n')[0],
            steps=formatted_steps
        )
    
    def _generate_pytest(self, test_steps, components):
        """Convert test steps to pytest format"""
        template = """import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_{test_name}():
    \"\"\"
    {description}
    \"\"\"
{steps}"""
        
        formatted_steps = "\n".join([f"    {step}" for step in test_steps.split('\n')])
        return template.format(
            test_name="_".join(components).lower(),
            description=test_steps.split('\n')[0],
            steps=formatted_steps
        )
    
    def _generate_unittest(self, test_steps, components):
        """Convert test steps to unittest format"""
        template = """import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By

class Test{test_name}(unittest.TestCase):
    def test_{method_name}(self):
        \"\"\"
        {description}
        \"\"\"
{steps}

if __name__ == '__main__':
    unittest.main()"""
        
        formatted_steps = "\n".join([f"        {step}" for step in test_steps.split('\n')])
        return template.format(
            test_name="".join(c.title() for c in components),
            method_name="_".join(components).lower(),
            description=test_steps.split('\n')[0],
            steps=formatted_steps
        )
    
    def get_xpath_guide(self, component_type):
        """Generate XPath guide for different component types"""
        guides = {
            'email': """Common XPath patterns for email fields:
1. //input[@type='email']
2. //input[contains(@name, 'email')]
3. //input[contains(@id, 'email')]""",
            'password': """Common XPath patterns for password fields:
1. //input[@type='password']
2. //input[contains(@name, 'password')]
3. //input[contains(@id, 'password')]""",
            'button': """Common XPath patterns for buttons:
1. //button[contains(text(), 'Submit')]
2. //input[@type='submit']
3. //button[@type='submit']"""
        }
        return guides.get(component_type, "No specific XPath guide available for this component type.")
