# QR Code Generator
<img width="1295" height="811" alt="qr" src="https://github.com/user-attachments/assets/9767ebfa-2c9b-4d84-9faa-61a2a4403a26" />

A modern web-based QR code generator built with Flask and Python. Generate customizable QR codes for URLs and WiFi networks with various styling options, colors, and logo embedding.

![QR Code Generator](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## Features

- 🔗 **URL QR Codes** - Convert any website link into a scannable QR code
- 📶 **WiFi QR Codes** - Generate QR codes for automatic WiFi connection
- 🎨 **Custom Styling** - 4 QR code styles (Square, Rounded, Circle, Gapped)
- 👁️ **Corner Customization** - 3 finder pattern styles
- 🎨 **Color Picker** - Customize foreground and background colors
- 🖼️ **Logo Embedding** - Add your logo to the center of URL QR codes
- 📱 **Responsive Design** - Works on desktop and mobile devices
- ⬇️ **High Resolution** - Download QR codes in high quality PNG format
- 🐳 **Docker Support** - Easy deployment with Docker

## Screenshots

The application features a clean, modern interface with:
- Side-by-side layout (form on left, preview on right)
- Real-time QR code preview
- Intuitive style selection cards
- Color customization with live preview

## Requirements

- Python 3.11 or higher
- Docker (optional, for containerized deployment)

## Installation

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd qr
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

### Option 2: Manual Python Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd qr
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Creating a URL QR Code

1. Select **URL** as the QR code type
2. Enter your website URL (e.g., `https://example.com`)
3. (Optional) Upload a logo image
4. Customize the QR code style and colors
5. Click **Generate QR Code**
6. Download the generated QR code

### Creating a WiFi QR Code

1. Select **WiFi** as the QR code type
2. Enter your WiFi network name (SSID)
3. Enter the WiFi password
4. Select the security type (WPA/WPA2, WEP, or No Password)
5. Customize the QR code style and colors
6. Click **Generate QR Code**
7. Share the QR code - devices can scan it to connect automatically

### Customization Options

- **QR Code Style**: Choose between Square, Rounded, Circle, or Gapped module patterns
- **Corner Squares Style**: Customize the three finder patterns (Square, Rounded, Circle)
- **Colors**: Pick custom foreground and background colors
- **Logo**: Add a logo to URL QR codes (square images work best)

## Project Structure

```
qr/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Frontend HTML with CSS and JavaScript
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md           # This file
```

## Dependencies

- **Flask 3.0.0** - Web framework
- **qrcode 7.4.2** - QR code generation with styling support
- **Pillow 10.1.0** - Image processing for logos and customization
- **gunicorn 21.2.0** - Production WSGI server

## Configuration

### QR Code Settings

The application generates QR codes with the following default settings:
- **Box size**: 20 pixels (high resolution)
- **Border**: 4 modules
- **Error correction**: HIGH (with logo), LOW (without logo)

You can modify these settings in `app.py` if needed.

## Development

To run in development mode:

```bash
python app.py
```

The Flask development server will start with debug mode enabled.

For production deployment, use Gunicorn (already configured in Docker):

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- QR code generation powered by [python-qrcode](https://github.com/lincolnloop/python-qrcode)
- Image processing by [Pillow](https://python-pillow.org/)
- Web framework by [Flask](https://flask.palletsprojects.com/)
