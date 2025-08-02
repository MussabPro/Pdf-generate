from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import os
import firebase_admin
from firebase_admin import credentials, storage
from dotenv import load_dotenv
import base64
from datetime import datetime
import io
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    try:
        # Check if Firebase is already initialized
        firebase_admin.get_app()
    except ValueError:
        # Firebase not initialized, so initialize it
        # Try to get service account from environment variable
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        if service_account_json:
            # Parse JSON from environment variable
            service_account_info = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_info)
        else:
            # Fallback to service account file path
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'firebase-service-account.json')
            if os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
            else:
                raise FileNotFoundError("Firebase service account credentials not found")
        
        # Initialize with storage bucket
        bucket_name = os.getenv('FIREBASE_STORAGE_BUCKET')
        firebase_admin.initialize_app(cred, {
            'storageBucket': bucket_name
        })

# Initialize Firebase on startup
initialize_firebase()


def upload_pdf_to_firebase(pdf_bytes, filename):
    """Upload PDF bytes to Firebase Storage and return download URL"""
    try:
        # Get Firebase Storage bucket
        bucket = storage.bucket()
        
        # Create blob with filename
        blob = bucket.blob(f"pdfs/{filename}")
        
        # Upload PDF bytes
        blob.upload_from_string(pdf_bytes, content_type='application/pdf')
        
        # Make the blob publicly accessible
        blob.make_public()
        
        # Return the public URL
        return blob.public_url
        
    except Exception as e:
        raise Exception(f"Failed to upload PDF to Firebase: {str(e)}")


def upload_pdf_to_firebase_secure(pdf_bytes, filename):
    """Upload PDF bytes to Firebase Storage and return a signed URL (more secure)"""
    try:
        from datetime import timedelta
        
        # Get Firebase Storage bucket
        bucket = storage.bucket()
        
        # Create blob with filename
        blob = bucket.blob(f"pdfs/{filename}")
        
        # Upload PDF bytes
        blob.upload_from_string(pdf_bytes, content_type='application/pdf')
        
        # Generate a signed URL that expires in 7 days
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=7),
            method="GET"
        )
        
        return url
        
    except Exception as e:
        raise Exception(f"Failed to upload PDF to Firebase: {str(e)}")


def clean_text_for_pdf(text):
    # Replace common Unicode characters with ASCII equivalents
    replacements = {
        '\u2022': '*',   # bullet point -> asterisk
        '\u2013': '-',   # en dash
        '\u2014': '--',  # em dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...',  # ellipsis
        '\u00b7': '*',   # middle dot -> asterisk
        '\u25cf': '*',   # black circle -> asterisk
        '\u2219': '*',   # bullet operator -> asterisk
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)

    # Remove any remaining non-latin-1 characters
    text = text.encode('latin-1', 'ignore').decode('latin-1')
    return text


def generate_pdf_from_text(content):
    """Generate PDF from provided text content"""

    # Clean the content
    content = clean_text_for_pdf(content)

    # Generate professionally formatted PDF (A4 size)
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_margins(25, 30, 25)

    # Add border around the content area
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.rect(15, 25, 180, 250)

    # Add logo and company name at the top
    pdf.set_y(30)

    # Try to add logo on the left
    try:
        logo_path = 'static/logo.png'
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=25, y=30, w=15, h=15)
        else:
            raise FileNotFoundError("Logo file not found")
    except Exception as e:
        # If logo not found, create a placeholder rectangle
        pdf.set_fill_color(106, 90, 205)
        pdf.rect(25, 30, 15, 15, 'F')

    # Add company name "NeuroLight" on the right of logo
    pdf.set_xy(45, 33)
    pdf.set_text_color(106, 90, 205)
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "NeuroLight", ln=True)

    # Add colored divider line below header
    pdf.set_y(50)
    pdf.set_draw_color(64, 224, 208)
    pdf.set_line_width(2)
    pdf.line(25, 50, 185, 50)

    # Add title/header inside content area
    pdf.set_y(60)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Resource", ln=True, align="C")
    pdf.ln(5)

    # Process content with professional formatting
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        # Check if we need a new page
        if pdf.get_y() > 260:
            pdf.add_page()

            # Add border to new page
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.2)
            pdf.rect(15, 25, 180, 250)

            # Add logo and header to new page
            pdf.set_y(30)
            try:
                logo_path = 'static/logo.png'
                if os.path.exists(logo_path):
                    pdf.image(logo_path, x=25, y=30, w=15, h=15)
                else:
                    raise FileNotFoundError("Logo file not found")
            except Exception as e:
                pdf.set_fill_color(106, 90, 205)
                pdf.rect(25, 30, 15, 15, 'F')

            pdf.set_xy(45, 33)
            pdf.set_text_color(106, 90, 205)
            pdf.set_font("Arial", "B", 18)
            pdf.cell(0, 12, "NeuroLight", ln=True)

            # Add divider line
            pdf.set_y(50)
            pdf.set_draw_color(64, 224, 208)
            pdf.set_line_width(2)
            pdf.line(25, 50, 185, 50)

            # Reset position for content
            pdf.set_y(60)
            pdf.set_text_color(0, 0, 0)

        # Check if line appears to be a heading
        if (line.isupper() and len(line) < 50) or line.endswith(':') or line.startswith('**'):
            pdf.set_font("Arial", "B", 11)
            pdf.ln(2)
            pdf.multi_cell(150, 6, line.replace('**', ''))
            pdf.ln(1)
        elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
            # Format as bullet point
            pdf.set_font("Arial", "", 9)
            pdf.cell(6, 5, "*", ln=False)
            pdf.multi_cell(150, 5, line[1:].strip())
            pdf.ln(1)
        else:
            # Format as regular paragraph
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(150, 5, line)
            pdf.ln(1)

    return pdf


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_from_chat():
    """
    API endpoint to generate PDF from chatbot response and upload to Firebase
    Expects JSON: {"content": "chatbot response text", "secure": true/false (optional)}
    Returns: {"success": true, "download_url": "firebase_url", "filename": "filename.pdf"}
    """
    try:
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({"error": "Missing 'content' in request"}), 400

        content = data['content']
        use_secure_url = data.get('secure', False)  # Optional parameter for secure URLs

        if not content.strip():
            return jsonify({"error": "Content cannot be empty"}), 400

        # Generate PDF
        pdf = generate_pdf_from_text(content)

        # Get PDF output as bytes
        pdf_output = pdf.output(dest='S')

        # Convert to bytes if it's a string
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        if pdf_output is None:
            return jsonify({"error": "Failed to generate PDF output"}), 500

        # Verify PDF has content
        if pdf_output == b'':
            return jsonify({"error": "Generated PDF is empty"}), 500

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_{timestamp}.pdf"

        # Upload to Firebase Storage
        try:
            if use_secure_url:
                download_url = upload_pdf_to_firebase_secure(pdf_output, filename)
            else:
                download_url = upload_pdf_to_firebase(pdf_output, filename)
        except Exception as e:
            return jsonify({"error": f"Failed to upload to Firebase: {str(e)}"}), 500

        return jsonify({
            "success": True,
            "download_url": download_url,
            "filename": filename,
            "content_type": "application/pdf",
            "size": len(pdf_output),
            "secure_url": use_secure_url
        })

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "PDF Generation API"})


@app.route('/generate-pdf-with-data', methods=['POST'])
def generate_pdf_with_data():
    """
    API endpoint to generate PDF and return both Firebase URL and base64 data
    Expects JSON: {"content": "chatbot response text", "secure": true/false (optional)}
    Returns: {"success": true, "download_url": "firebase_url", "pdf_data": "base64_data", "filename": "filename.pdf"}
    """
    try:
        data = request.get_json()

        if not data or 'content' not in data:
            return jsonify({"error": "Missing 'content' in request"}), 400

        content = data['content']
        use_secure_url = data.get('secure', False)

        if not content.strip():
            return jsonify({"error": "Content cannot be empty"}), 400

        # Generate PDF
        pdf = generate_pdf_from_text(content)

        # Get PDF output as bytes
        pdf_output = pdf.output(dest='S')

        # Convert to bytes if it's a string
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1')

        if pdf_output is None:
            return jsonify({"error": "Failed to generate PDF output"}), 500

        # Verify PDF has content
        if pdf_output == b'':
            return jsonify({"error": "Generated PDF is empty"}), 500

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resource_{timestamp}.pdf"

        # Upload to Firebase Storage
        try:
            if use_secure_url:
                download_url = upload_pdf_to_firebase_secure(pdf_output, filename)
            else:
                download_url = upload_pdf_to_firebase(pdf_output, filename)
        except Exception as e:
            return jsonify({"error": f"Failed to upload to Firebase: {str(e)}"}), 500

        # Convert to base64 for JSON response
        pdf_base64 = base64.b64encode(pdf_output).decode('utf-8')

        return jsonify({
            "success": True,
            "download_url": download_url,
            "pdf_data": pdf_base64,
            "filename": filename,
            "content_type": "application/pdf",
            "size": len(pdf_output),
            "secure_url": use_secure_url
        })

    except Exception as e:
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


# For Vercel deployment
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True)
