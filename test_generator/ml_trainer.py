import torch
from torch.utils.data import Dataset, DataLoader
from transformers import T5ForConditionalGeneration, T5Tokenizer
import json
import os
from pathlib import Path

class TestCaseDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        input_text = f"generate test case: {item['prompt']}"
        target_text = item['test_case']
        
        inputs = self.tokenizer(input_text, padding='max_length', max_length=512, truncation=True, return_tensors='pt')
        targets = self.tokenizer(target_text, padding='max_length', max_length=512, truncation=True, return_tensors='pt')
        
        return {
            'input_ids': inputs.input_ids.squeeze(),
            'attention_mask': inputs.attention_mask.squeeze(),
            'labels': targets.input_ids.squeeze()
        }

class TestCaseTrainer:
    def __init__(self):
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small')
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
    def prepare_training_data(self):
        """Prepare training data from templates and examples"""
        training_data = []
        template_dir = Path(__file__).parent.parent / "test_templates"
        
        # Convert Robot Framework templates to training examples
        for template_file in template_dir.glob("*.robot"):
            with open(template_file, 'r') as f:
                content = f.read()
                test_cases = self._extract_test_cases(content)
                
                for test_case in test_cases:
                    training_data.append({
                        'prompt': test_case['documentation'],
                        'test_case': test_case['steps']
                    })
        
        return training_data
    
    def _extract_test_cases(self, content):
        """Extract test cases from Robot Framework file"""
        test_cases = []
        current_test = None
        
        for line in content.split('\n'):
            if '*** Test Cases ***' in line:
                continue
                
            if line.strip() and not line.startswith(' '):
                if current_test:
                    test_cases.append(current_test)
                current_test = {'name': line.strip(), 'documentation': '', 'steps': []}
                
            elif current_test and line.strip().startswith('[Documentation]'):
                current_test['documentation'] = line.split('    ', 1)[1].strip()
                
            elif current_test and line.strip() and not line.strip().startswith('['):
                current_test['steps'].append(line.strip())
        
        if current_test:
            test_cases.append(current_test)
            
        return test_cases
    
    def train(self, num_epochs=5, batch_size=4):
        """Train the model on the prepared dataset"""
        training_data = self.prepare_training_data()
        dataset = TestCaseDataset(training_data)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=5e-5)
        
        self.model.train()
        for epoch in range(num_epochs):
            total_loss = 0
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                loss = outputs.loss
                total_loss += loss.item()
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            print(f"Epoch {epoch+1}/{num_epochs}, Average Loss: {total_loss/len(dataloader)}")
    
    def save_model(self, path):
        """Save the trained model"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
