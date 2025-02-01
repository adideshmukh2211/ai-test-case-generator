import os
import re
from flask import jsonify
import spacy

class TestCaseGenerator:
    def __init__(self):
        # Load spaCy's small model
        self.nlp = spacy.load('en_core_web_sm')
        
        # Framework templates
        self.supported_frameworks = {
            'robot': self._generate_robot_framework,
            'pytest': self._generate_pytest,
            'unittest': self._generate_unittest
        }
        
        # Load test templates
        self.templates = {
            'login': self._get_login_template,
            'registration': self._get_registration_template,
            'profile': self._get_profile_template
        }
    
    def generate_test_case(self, prompt, framework='robot'):
        """Generate test cases based on the prompt and selected framework"""
        # Process the prompt
        doc = self.nlp(prompt.lower())
        
        # Extract key information
        actions = [token.text for token in doc if token.dep_ == 'ROOT']
        components = [token.text for token in doc if token.dep_ in ('dobj', 'pobj')]
        
        # Identify test type
        test_type = self._identify_test_type(prompt)
        
        # Get template
        template_func = self.templates.get(test_type, self._get_default_template)
        test_steps = template_func()
        
        # Convert to specified framework format
        generator = self.supported_frameworks.get(framework, self._generate_robot_framework)
        return generator(test_steps, components)
    
    def _identify_test_type(self, prompt):
        """Identify the type of test from the prompt"""
        prompt = prompt.lower()
        if any(word in prompt for word in ['login', 'signin', 'log in']):
            return 'login'
        elif any(word in prompt for word in ['register', 'signup', 'sign up']):
            return 'registration'
        elif any(word in prompt for word in ['profile', 'account', 'settings']):
            return 'profile'
        return 'default'
    
    def _get_login_template(self):
        return {
            'name': 'Login Test',
            'steps': [
                'Open Browser    ${URL}    ${BROWSER}',
                'Maximize Browser Window',
                'Input Text    //input[@type="email"]    ${EMAIL}',
                'Input Password    //input[@type="password"]    ${PASSWORD}',
                'Click Button    //button[@type="submit"]',
                'Wait Until Page Contains    Welcome',
                '[Teardown]    Close Browser'
            ]
        }
    
    def _get_registration_template(self):
        return {
            'name': 'Registration Test',
            'steps': [
                'Open Browser    ${URL}/register    ${BROWSER}',
                'Maximize Browser Window',
                'Input Text    //input[@name="username"]    ${USERNAME}',
                'Input Text    //input[@type="email"]    ${EMAIL}',
                'Input Password    //input[@type="password"]    ${PASSWORD}',
                'Input Password    //input[@name="confirm_password"]    ${PASSWORD}',
                'Click Button    //button[@type="submit"]',
                'Wait Until Page Contains    Registration Successful',
                '[Teardown]    Close Browser'
            ]
        }
    
    def _get_profile_template(self):
        return {
            'name': 'Profile Test',
            'steps': [
                'Open Browser    ${URL}/profile    ${BROWSER}',
                'Maximize Browser Window',
                'Input Text    //input[@name="name"]    ${NEW_NAME}',
                'Input Text    //textarea[@name="bio"]    ${NEW_BIO}',
                'Choose File    //input[@type="file"]    ${PROFILE_PICTURE}',
                'Click Button    //button[contains(text(), "Save")]',
                'Wait Until Page Contains    Profile Updated',
                '[Teardown]    Close Browser'
            ]
        }
    
    def _get_default_template(self):
        return {
            'name': 'Default Test',
            'steps': [
                'Open Browser    ${URL}    ${BROWSER}',
                'Maximize Browser Window',
                'Page Should Contain Element    ${ELEMENT}',
                'Click Element    ${ELEMENT}',
                'Wait Until Page Contains    ${EXPECTED_TEXT}',
                '[Teardown]    Close Browser'
            ]
        }
    
    def _generate_robot_framework(self, template, components):
        """Convert test steps to Robot Framework format"""
        test_name = template['name']
        steps = template['steps']
        
        test_case = []
        test_case.append("*** Settings ***")
        test_case.append("Library    SeleniumLibrary")
        test_case.append("")
        test_case.append("*** Variables ***")
        test_case.append("${URL}         http://localhost:3000")
        test_case.append("${BROWSER}     chrome")
        test_case.append("")
        test_case.append("*** Test Cases ***")
        test_case.append(test_name)
        test_case.extend([f"    {step}" for step in steps])
        
        return "\n".join(test_case)
    
    def _generate_pytest(self, template, components):
        """Convert test steps to pytest format"""
        test_name = template['name'].lower().replace(' ', '_')
        steps = template['steps']
        
        test_case = []
        test_case.append("import pytest")
        test_case.append("from selenium import webdriver")
        test_case.append("from selenium.webdriver.common.by import By")
        test_case.append("from selenium.webdriver.support.ui import WebDriverWait")
        test_case.append("from selenium.webdriver.support import expected_conditions as EC")
        test_case.append("")
        test_case.append(f"def test_{test_name}():")
        test_case.append("    driver = webdriver.Chrome()")
        test_case.append("    try:")
        
        for step in steps:
            if 'Open Browser' in step:
                test_case.append('        driver.get("http://localhost:3000")')
            elif 'Input Text' in step or 'Input Password' in step:
                locator = re.search(r'//\S+', step).group()
                test_case.append(f'        element = WebDriverWait(driver, 10).until(')
                test_case.append(f'            EC.presence_of_element_located((By.XPATH, "{locator}"))')
                test_case.append('        )')
                test_case.append('        element.send_keys("test")')
            elif 'Click' in step:
                locator = re.search(r'//\S+', step).group()
                test_case.append(f'        element = WebDriverWait(driver, 10).until(')
                test_case.append(f'            EC.element_to_be_clickable((By.XPATH, "{locator}"))')
                test_case.append('        )')
                test_case.append('        element.click()')
            elif 'Wait Until Page Contains' in step:
                text = step.split('    ')[-1]
                test_case.append(f'        WebDriverWait(driver, 10).until(')
                test_case.append(f'            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), \'{text}\')]"))')
                test_case.append('        )')
        
        test_case.append("    finally:")
        test_case.append("        driver.quit()")
        
        return "\n".join(test_case)
    
    def _generate_unittest(self, template, components):
        """Convert test steps to unittest format"""
        test_name = template['name'].replace(' ', '')
        steps = template['steps']
        
        test_case = []
        test_case.append("import unittest")
        test_case.append("from selenium import webdriver")
        test_case.append("from selenium.webdriver.common.by import By")
        test_case.append("from selenium.webdriver.support.ui import WebDriverWait")
        test_case.append("from selenium.webdriver.support import expected_conditions as EC")
        test_case.append("")
        test_case.append(f"class {test_name}(unittest.TestCase):")
        test_case.append("    def setUp(self):")
        test_case.append("        self.driver = webdriver.Chrome()")
        test_case.append("")
        test_case.append("    def tearDown(self):")
        test_case.append("        self.driver.quit()")
        test_case.append("")
        test_case.append("    def test_main(self):")
        
        for step in steps:
            if 'Open Browser' in step:
                test_case.append('        self.driver.get("http://localhost:3000")')
            elif 'Input Text' in step or 'Input Password' in step:
                locator = re.search(r'//\S+', step).group()
                test_case.append(f'        element = WebDriverWait(self.driver, 10).until(')
                test_case.append(f'            EC.presence_of_element_located((By.XPATH, "{locator}"))')
                test_case.append('        )')
                test_case.append('        element.send_keys("test")')
            elif 'Click' in step:
                locator = re.search(r'//\S+', step).group()
                test_case.append(f'        element = WebDriverWait(self.driver, 10).until(')
                test_case.append(f'            EC.element_to_be_clickable((By.XPATH, "{locator}"))')
                test_case.append('        )')
                test_case.append('        element.click()')
            elif 'Wait Until Page Contains' in step:
                text = step.split('    ')[-1]
                test_case.append(f'        WebDriverWait(self.driver, 10).until(')
                test_case.append(f'            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), \'{text}\')]"))')
                test_case.append('        )')
        
        test_case.append("")
        test_case.append("if __name__ == '__main__':")
        test_case.append("    unittest.main()")
        
        return "\n".join(test_case)
    
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
