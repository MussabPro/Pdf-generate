# PDF Generation API with Firebase Storage

A Flask API for generating professional PDF documents from text content and storing them in Firebase Storage, designed for mental health resources.

## Features

- Generate professionally formatted PDFs with company branding
- Clean text processing for PDF compatibility
- Upload PDFs to Firebase Storage
- Return secure or public download URLs
- RESTful API endpoints
- Health check endpoint

## Firebase Setup

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Firebase Storage in your project
3. Generate a service account key:
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the JSON file as `firebase-service-account.json` in your project root
4. Get your Storage Bucket URL from Firebase Storage settings

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-service-account.json
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

For production (Vercel), you can also use:
```env
FIREBASE_SERVICE_ACCOUNT={"type":"service_account","project_id":"your-project-id",...}
```

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
   cd "d:\Flutter App\Therapy app\Pdf-generate"
   ```

2. Deploy to Vercel:
   ```bash
   vercel
   ```

3. Set up environment variables in the Vercel dashboard:
   - `FIREBASE_SERVICE_ACCOUNT`: Your complete Firebase service account JSON (as a single line string)
   - `FIREBASE_STORAGE_BUCKET`: Your Firebase storage bucket URL

## API Endpoints

### POST /generate-pdf
Generates a PDF from provided text content and uploads to Firebase Storage.

**Request Body:**
```json
{
  "content": "Your text content here...",
  "secure": false  // Optional: true for signed URLs, false for public URLs
}
```

**Response:**
```json
{
  "success": true,
  "download_url": "https://storage.googleapis.com/your-bucket/pdfs/resource_20250803_123456.pdf",
  "filename": "resource_20250803_123456.pdf",
  "content_type": "application/pdf",
  "size": 12345,
  "secure_url": false
}
```

### POST /generate-pdf-with-data
Generates a PDF, uploads to Firebase, and returns both URL and base64 data.

**Request Body:**
```json
{
  "content": "Your text content here...",
  "secure": false  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "download_url": "https://storage.googleapis.com/your-bucket/pdfs/resource_20250803_123456.pdf",
  "pdf_data": "base64_encoded_pdf_data...",
  "filename": "resource_20250803_123456.pdf",
  "content_type": "application/pdf",
  "size": 12345,
  "secure_url": false
}
```

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

2. Set up Firebase:
   - Follow the Firebase Setup section above
   - Place your `firebase-service-account.json` file in the project root

3. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your Firebase configuration.

4. Run the application:
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## File Structure

```
d:\Flutter App\Therapy app\Pdf-generate\
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── vercel.json                # Vercel configuration
├── .vercelignore              # Files to ignore during deployment
├── .env.example               # Environment variables template
├── firebase-service-account.json  # Firebase credentials (not in git)
├── static/
│   └── logo.png              # Company logo
└── README.md                 # This file
```

## URL Types

- **Public URLs**: Accessible by anyone with the link
- **Secure URLs**: Signed URLs that expire after 7 days (more secure)

Use the `secure` parameter in your requests to choose between URL types.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400`: Bad request (missing content, empty content)
- `500`: Server error (PDF generation failed, Firebase upload failed)

## Security Notes

- Keep your Firebase service account credentials secure
- Use secure URLs for sensitive content
- Consider implementing authentication for your API endpoints
- Regularly rotate your Firebase service account keys