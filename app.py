from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer as EyeSquareDrawer, RoundedModuleDrawer as EyeRoundedDrawer, CircleModuleDrawer as EyeCircleDrawer
import io
import base64
from PIL import Image, ImageDraw
app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get('url', '')
    logo_data = data.get('logo', '')
    style = data.get('style', 'square')
    eye_style = data.get('eye_style', 'square')
    fg_color = data.get('fg_color', '#000000')
    bg_color = data.get('bg_color', '#ffffff')
    
    if not url:
        return {'error': 'URL is required'}, 400
    
    # Convert hex to RGB
    fg_rgb = tuple(int(fg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    bg_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    
    # Select module drawer based on style
    module_drawer_map = {
        'square': SquareModuleDrawer(),
        'rounded': RoundedModuleDrawer(),
        'circle': CircleModuleDrawer(),
        'gapped': GappedSquareModuleDrawer()
    }
    
    # Select eye (finder pattern) drawer based on style
    eye_drawer_map = {
        'square': EyeSquareDrawer(),
        'rounded': EyeRoundedDrawer(),
        'circle': EyeCircleDrawer()
    }
    
    module_drawer = module_drawer_map.get(style, SquareModuleDrawer())
    eye_drawer = eye_drawer_map.get(eye_style, EyeSquareDrawer())
    
    # Use high error correction only if logo is provided, otherwise use standard
    error_correction = qrcode.constants.ERROR_CORRECT_H if logo_data else qrcode.constants.ERROR_CORRECT_L
    
    # Generate QR code with higher resolution
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=20,  # Increased from 10 to 20 for higher resolution
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create styled image
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=module_drawer,
        eye_drawer=eye_drawer,  # Apply eye styling
        color_mask=SolidFillColorMask(front_color=fg_rgb, back_color=bg_rgb)
    ).convert('RGB')
    
    # If logo is provided, embed it in the center
    if logo_data:
        try:
            # Remove data URL prefix if present
            if 'base64,' in logo_data:
                logo_data = logo_data.split('base64,')[1]
            
            # Decode logo
            logo_bytes = base64.b64decode(logo_data)
            logo = Image.open(io.BytesIO(logo_bytes))
            
            # Calculate sizes
            qr_width, qr_height = img.size
            logo_size = int(qr_width * 0.15)  # Logo is 15% of QR code (smaller for scanning)
            
            # Resize logo
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
            
            # Clear the center area of QR code (balanced size for scanning)
            clear_size = int(logo_size * 1.8)  # Clear area is 80% larger than logo
            clear_pos = ((qr_width - clear_size) // 2, (qr_height - clear_size) // 2)
            
            # Draw a filled rectangle in the center with background color
            draw = ImageDraw.Draw(img)
            draw.rectangle(
                [clear_pos[0], clear_pos[1], clear_pos[0] + clear_size, clear_pos[1] + clear_size],
                fill=bg_rgb,
                outline=bg_rgb,
                width=0
            )
            
            # Draw a thick border around the cleared area
            border_thickness = 6
            draw.rectangle(
                [clear_pos[0], clear_pos[1], clear_pos[0] + clear_size, clear_pos[1] + clear_size],
                fill=None,
                outline=fg_rgb,  # Use foreground color for border
                width=border_thickness
            )
            
            # Resize logo to better fill the cleared area
            final_logo_size = int(clear_size * 0.85)  # Logo fills 85% of cleared area
            logo_resized = logo.resize((final_logo_size, final_logo_size), Image.LANCZOS)
            
            # Create minimal border
            border_size = int(final_logo_size * 0.05)  # Tiny 5% border
            logo_with_border = Image.new('RGB', 
                                         (final_logo_size + border_size * 2, final_logo_size + border_size * 2), 
                                         bg_rgb)
            
            # Paste logo onto border
            logo_border_pos = (border_size, border_size)
            if logo_resized.mode == 'RGBA':
                logo_with_border.paste(logo_resized, logo_border_pos, logo_resized)
            else:
                logo_with_border.paste(logo_resized, logo_border_pos)
            
            # Calculate position to paste logo (center of QR code)
            logo_pos = ((qr_width - logo_with_border.size[0]) // 2, 
                       (qr_height - logo_with_border.size[1]) // 2)
            img.paste(logo_with_border, logo_pos)
        except Exception as e:
            print(f"Error processing logo: {e}")
    
    # Save to bytes buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    # Convert to base64 for embedding in HTML
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return {
        'success': True,
        'image': f'data:image/png;base64,{img_base64}'
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
