# AI Test Case Generator

A web application that generates Robot Framework test cases based on natural language prompts. Built with Flask, Robot Framework, and Selenium.

## Features

- Generate Robot Framework test cases from natural language descriptions
- Get XPath guidance for web elements
- Modern, responsive UI built with Tailwind CSS
- Ready for Vercel deployment

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   python app.py
   ```
4. Visit http://localhost:5000 in your browser

## Deployment on Vercel

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```
2. Login to Vercel:
   ```bash
   vercel login
   ```
3. Deploy:
   ```bash
   vercel
   ```

## Requirements

- Python 3.12
- Chrome/Firefox WebDriver for Selenium
- Node.js 20.x or higher (for Vercel deployment)

## Contributing

Feel free to open issues and pull requests!
