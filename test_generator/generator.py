import os
import re
import spacy
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqGeneration
import torch

class TestCaseGenerator:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.template_dir = Path(__file__).parent.parent / "test_templates"
        self.templates = self._load_templates()
        
        # Load pre-trained model
        model_path = Path(__file__).parent / "trained_model"
        if model_path.exists():
            self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
            self.model = AutoModelForSeq2SeqGeneration.from_pretrained(str(model_path))
        else:
            self.tokenizer = AutoTokenizer.from_pretrained("t5-small")
            self.model = AutoModelForSeq2SeqGeneration.from_pretrained("t5-small")
        
        self.supported_frameworks = {
            'robot': self._generate_robot_framework,
            'pytest': self._generate_pytest,
            'unittest': self._generate_unittest
        }
    
    def _load_templates(self):
        """Load and parse test templates"""
        templates = {}
        for template_file in self.template_dir.glob("*.robot"):
            with open(template_file, 'r') as f:
                content = f.read()
                templates[template_file.stem] = self._parse_robot_file(content)
        return templates
    
    def _parse_robot_file(self, content):
        """Parse Robot Framework file content"""
        sections = {}
        current_section = None
        
        for line in content.split('\n'):
            if line.strip().startswith('***'):
                current_section = line.strip().strip('*').strip()
                sections[current_section] = []
            elif current_section and line.strip():
                sections[current_section].append(line)
        
        return sections
    
    def _analyze_prompt(self, prompt):
        """Enhanced prompt analysis with NLP"""
        doc = self.nlp(prompt.lower())
        
        features = {
            'action': None,
            'component': None,
            'validation': None,
            'scenario': None,
            'framework': 'robot'  # default framework
        }
        
        # Extract key information using NLP
        for token in doc:
            if token.dep_ == 'ROOT' and token.pos_ == 'VERB':
                features['action'] = token.text
            if token.dep_ == 'dobj':
                features['component'] = token.text
            
        # Identify testing scenario
        scenarios = {
            'login': ['login', 'signin', 'authenticate'],
            'registration': ['register', 'signup', 'create account'],
            'profile': ['profile', 'account', 'settings']
        }
        
        for scenario, keywords in scenarios.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                features['scenario'] = scenario
                break
        
        # Identify framework preference
        frameworks = {
            'pytest': ['pytest', 'python test'],
            'unittest': ['unittest', 'unit test'],
            'robot': ['robot', 'robotframework']
        }
        
        for framework, keywords in frameworks.items():
            if any(keyword in prompt.lower() for keyword in keywords):
                features['framework'] = framework
                break
        
        return features
    
    def _generate_test_steps(self, features):
        """Generate test steps using the ML model"""
        input_text = f"generate test steps for: {json.dumps(features)}"
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=150,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95
        )
        
        generated_steps = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_steps
    
    def _generate_robot_framework(self, features, steps):
        """Generate Robot Framework test case"""
        test_case = []
        test_case.append(f"*** Test Cases ***")
        test_case.append(f"Test {features['component'].title() if features['component'] else 'Generated'}")
        test_case.append(f"    [Documentation]    Test case for {features['scenario'] if features['scenario'] else 'general'} functionality")
        
        # Add setup
        test_case.append("    Open Browser    \${URL}    \${BROWSER}")
        test_case.append("    Maximize Browser Window")
        
        # Add generated steps
        for step in steps.split('\n'):
            if step.strip():
                test_case.append(f"    {step.strip()}")
        
        # Add teardown
        test_case.append("    [Teardown]    Close Browser")
        
        return "\n".join(test_case)
    
    def _generate_pytest(self, features, steps):
        """Generate pytest test case"""
        test_case = []
        test_case.append("import pytest")
        test_case.append("from selenium import webdriver")
        test_case.append("from selenium.webdriver.common.by import By")
        test_case.append("from selenium.webdriver.support.ui import WebDriverWait")
        test_case.append("from selenium.webdriver.support import expected_conditions as EC\n")
        
        test_case.append("@pytest.fixture")
        test_case.append("def driver():")
        test_case.append("    driver = webdriver.Chrome()")
        test_case.append("    driver.maximize_window()")
        test_case.append("    yield driver")
        test_case.append("    driver.quit()\n")
        
        test_case.append(f"def test_{features['scenario']}(driver):")
        test_case.append('    """')
        test_case.append(f"    Test case for {features['scenario']} functionality")
        test_case.append('    """')
        
        # Convert Robot Framework steps to pytest
        for step in steps.split('\n'):
            if 'Click Element' in step:
                element = step.split('${')[-1].split('}')[0]
                test_case.append(f"    element = WebDriverWait(driver, 10).until(")
                test_case.append(f"        EC.element_to_be_clickable((By.XPATH, {element}))")
                test_case.append("    element.click()")
            elif 'Input Text' in step:
                element = step.split('${')[1].split('}')[0]
                value = step.split('${')[2].split('}')[0]
                test_case.append(f"    element = WebDriverWait(driver, 10).until(")
                test_case.append(f"        EC.presence_of_element_located((By.XPATH, {element}))")
                test_case.append(f"    element.send_keys({value})")
        
        return "\n".join(test_case)
    
    def _generate_unittest(self, features, steps):
        """Generate unittest test case"""
        test_case = []
        test_case.append("import unittest")
        test_case.append("from selenium import webdriver")
        test_case.append("from selenium.webdriver.common.by import By")
        test_case.append("from selenium.webdriver.support.ui import WebDriverWait")
        test_case.append("from selenium.webdriver.support import expected_conditions as EC\n")
        
        test_case.append(f"class Test{features['scenario'].title()}(unittest.TestCase):")
        test_case.append("    def setUp(self):")
        test_case.append("        self.driver = webdriver.Chrome()")
        test_case.append("        self.driver.maximize_window()\n")
        
        test_case.append("    def tearDown(self):")
        test_case.append("        self.driver.quit()\n")
        
        test_case.append(f"    def test_{features['scenario']}(self):")
        test_case.append('        """')
        test_case.append(f"        Test case for {features['scenario']} functionality")
        test_case.append('        """')
        
        # Convert Robot Framework steps to unittest
        for step in steps.split('\n'):
            if 'Click Element' in step:
                element = step.split('${')[-1].split('}')[0]
                test_case.append(f"        element = WebDriverWait(self.driver, 10).until(")
                test_case.append(f"            EC.element_to_be_clickable((By.XPATH, {element}))")
                test_case.append("        element.click()")
            elif 'Input Text' in step:
                element = step.split('${')[1].split('}')[0]
                value = step.split('${')[2].split('}')[0]
                test_case.append(f"        element = WebDriverWait(self.driver, 10).until(")
                test_case.append(f"            EC.presence_of_element_located((By.XPATH, {element}))")
                test_case.append(f"        element.send_keys({value})")
        
        test_case.append("\nif __name__ == '__main__':")
        test_case.append("    unittest.main()")
        
        return "\n".join(test_case)
    
    def generate_test_case(self, prompt, framework=None):
        """Generate a complete test case based on user prompt"""
        # Analyze the prompt
        features = self._analyze_prompt(prompt)
        if framework:
            features['framework'] = framework
        
        # Generate test steps
        steps = self._generate_test_steps(features)
        
        # Generate test case in the specified framework
        generator = self.supported_frameworks.get(features['framework'], self._generate_robot_framework)
        return generator(features, steps)
    
    def get_xpath_guide(self, component):
        """Enhanced XPath guide generation"""
        guides = {
            'email': """
Common XPath patterns for email fields:
1. By type: //input[@type='email']
2. By name: //input[@name='email']
3. By ID: //input[@id='email']
4. By placeholder: //input[@placeholder='Enter email']
5. By class: //input[contains(@class, 'email')]
6. By label: //label[contains(text(),'Email')]/following-sibling::input
7. By aria-label: //input[@aria-label='Email']

Tips for finding the right XPath:
1. Use browser's developer tools (F12)
2. Right-click on the element
3. Choose 'Inspect'
4. Right-click on the highlighted HTML
5. Copy > Copy XPath or Copy > Copy full XPath
""",
            'password': """
Common XPath patterns for password fields:
1. By type: //input[@type='password']
2. By name: //input[@name='password']
3. By ID: //input[@id='password']
4. By placeholder: //input[@placeholder='Enter password']
5. By class: //input[contains(@class, 'password')]
6. By label: //label[contains(text(),'Password')]/following-sibling::input
7. By aria-label: //input[@aria-label='Password']
""",
            'button': """
Common XPath patterns for buttons:
1. By type: //button[@type='submit']
2. By text: //button[text()='Login']
3. By contains text: //button[contains(text(), 'Log')]
4. By class: //button[contains(@class, 'submit')]
5. By role: //button[@role='submit']
6. By aria-label: //button[@aria-label='Submit']
7. By ID: //button[@id='submit-button']
"""
        }
        
        return guides.get(component.lower(), "No specific XPath guide available for this component.")
