# PDF Generation API

A Flask API for generating professional PDF documents from text content, designed for mental health resources.

## Features

- Generate professionally formatted PDFs with company branding
- Clean text processing for PDF compatibility
- RESTful API endpoints
- Health check endpoint

## Deployment on Vercel

### Prerequisites

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

### Deploy

1. Navigate to the project directory:
   ```bash
   cd /Users/mussab/Desktop/Python
   ```

2. Deploy to Vercel:
   ```bash
   vercel
   ```

3. Set up environment variables in the Vercel dashboard:
   - `OPENAI_API_KEY`: Your OpenAI API key

### Environment Variables

Make sure to set the following environment variable in your Vercel project settings:

- `OPENAI_API_KEY`: Your OpenAI API key for text processing

## API Endpoints

### POST /generate-pdf
Generates a PDF from provided text content.

**Request Body:**
```json
{
  "content": "Your text content here..."
}
```

**Response:**
- Returns a PDF file as attachment

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "PDF Generation API"
}
```

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:3000`

## File Structure

```
/Users/mussab/Desktop/Python/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel configuration
├── .vercelignore      # Files to ignore during deployment
└── README.md          # This file
```