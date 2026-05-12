from flask import Flask, render_template, request, send_file
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer, CircleModuleDrawer, GappedSquareModuleDrawer, SquareModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer as EyeSquareDrawer, RoundedModuleDrawer as EyeRoundedDrawer, CircleModuleDrawer as EyeCircleDrawer
import io
import base64
import re
from PIL import Image, ImageDraw
app = Flask(__name__, template_folder='.')

HEX_COLOR_PATTERN = re.compile(r'^#?[0-9a-fA-F]{6}$')


def parse_hex_color(color_value, default_value, field_name):
    normalized_value = (color_value or default_value).strip()

    if not HEX_COLOR_PATTERN.fullmatch(normalized_value):
        raise ValueError(f'{field_name} must be a 6-digit hex color like #0f172a.')

    hex_value = normalized_value.lstrip('#')
    return tuple(int(hex_value[index:index + 2], 16) for index in (0, 2, 4))


def parse_bool_flag(flag_value):
    if isinstance(flag_value, bool):
        return flag_value

    if isinstance(flag_value, str):
        return flag_value.strip().lower() in {'1', 'true', 'yes', 'on'}

    return bool(flag_value)


def apply_transparent_background(img, front_rgb, back_rgb):
    rgba_img = img.convert('RGBA')
    transparent_pixels = []

    for red, green, blue, _ in rgba_img.getdata():
        pixel_rgb = (red, green, blue)

        if pixel_rgb == back_rgb:
            transparent_pixels.append(front_rgb + (0,))
            continue

        if pixel_rgb == front_rgb:
            transparent_pixels.append(front_rgb + (255,))
            continue

        alpha_candidates = []
        for channel_index, front_channel in enumerate(front_rgb):
            background_channel = back_rgb[channel_index]

            if front_channel == background_channel:
                continue

            channel_value = pixel_rgb[channel_index]
            alpha_candidates.append((channel_value - background_channel) / (front_channel - background_channel))

        alpha = sum(alpha_candidates) / len(alpha_candidates) if alpha_candidates else 1
        alpha = max(0, min(1, alpha))
        transparent_pixels.append(front_rgb + (int(round(alpha * 255)),))

    rgba_img.putdata(transparent_pixels)
    return rgba_img

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
    transparent_background = parse_bool_flag(data.get('transparent_background', False))
    
    if not url:
        return {'error': 'URL is required'}, 400
    
    try:
        fg_rgb = parse_hex_color(fg_color, '#000000', 'Foreground color')
        bg_rgb = parse_hex_color(bg_color, '#ffffff', 'Background color')
    except ValueError as exc:
        return {'error': str(exc)}, 400
    
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
    ).convert('RGBA' if transparent_background else 'RGB')

    if transparent_background:
        img = apply_transparent_background(img, fg_rgb, bg_rgb)
    
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
            fill_color = (255, 255, 255, 0) if transparent_background else bg_rgb
            border_color = fg_rgb + (255,) if transparent_background else fg_rgb
            
            # Draw a filled rectangle in the center with background color
            draw = ImageDraw.Draw(img)
            draw.rectangle(
                [clear_pos[0], clear_pos[1], clear_pos[0] + clear_size, clear_pos[1] + clear_size],
                fill=fill_color,
                outline=fill_color,
                width=0
            )
            
            # Draw a thick border around the cleared area
            border_thickness = 6
            draw.rectangle(
                [clear_pos[0], clear_pos[1], clear_pos[0] + clear_size, clear_pos[1] + clear_size],
                fill=None,
                outline=border_color,  # Use foreground color for border
                width=border_thickness
            )
            
            # Resize logo to better fill the cleared area
            final_logo_size = int(clear_size * 0.85)  # Logo fills 85% of cleared area
            logo_resized = logo.resize((final_logo_size, final_logo_size), Image.LANCZOS)
            
            # Create minimal border
            border_size = int(final_logo_size * 0.05)  # Tiny 5% border
            logo_mode = 'RGBA' if transparent_background else 'RGB'
            logo_background = (255, 255, 255, 0) if transparent_background else bg_rgb
            logo_with_border = Image.new(
                logo_mode,
                (final_logo_size + border_size * 2, final_logo_size + border_size * 2),
                logo_background,
            )
            
            # Paste logo onto border
            logo_border_pos = (border_size, border_size)
            if transparent_background:
                logo_resized = logo_resized.convert('RGBA')
                logo_with_border.paste(logo_resized, logo_border_pos, logo_resized)
            elif logo_resized.mode == 'RGBA':
                logo_with_border.paste(logo_resized, logo_border_pos, logo_resized)
            else:
                logo_with_border.paste(logo_resized, logo_border_pos)
            
            # Calculate position to paste logo (center of QR code)
            logo_pos = ((qr_width - logo_with_border.size[0]) // 2, 
                       (qr_height - logo_with_border.size[1]) // 2)
            if transparent_background:
                img.paste(logo_with_border, logo_pos, logo_with_border)
            else:
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
