import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO

class AwesomeQRGenerator:
    def __init__(self):
        self.social_icons = {
            'github': 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png',
            'youtube': 'https://www.youtube.com/img/desktop/yt_1200.png',
            'facebook': 'https://static.xx.fbcdn.net/rsrc.php/y8/r/dF5SId3UHWd.svg',
            'twitter': 'https://abs.twimg.com/responsive-web/client-web/icon-ios.77d25eba.png',
            'instagram': 'https://static.cdninstagram.com/rsrc.php/v3/yT/r/5_ytvRKzJTc.png',
            'linkedin': 'https://static.licdn.com/aero-v1/sc/h/eahiplrwoq61f4dm712jqjqrb',
            'whatsapp': 'https://static.whatsapp.net/rsrc.php/v3/yP/r/rYZqPCBaG70.png',
            'telegram': 'https://web.telegram.org/a/telegram-logo.1bcfc5e1.png',
            'discord': 'https://assets-global.website-files.com/6257adef93867e50d84d30e2/62595384e89d1d54d704ece2_3437c10597c1526c3dbd98c737c2bcae.svg'
        }
        
        self.color_presets = {
            'github': ('#000000', '#ffffff'),
            'youtube': ('#FF0000', '#ffffff'),
            'facebook': ('#1877F2', '#ffffff'),
            'twitter': ('#1DA1F2', '#ffffff'),
            'instagram': ('#E4405F', '#ffffff'),
            'linkedin': ('#0A66C2', '#ffffff'),
            'whatsapp': ('#25D366', '#ffffff'),
            'telegram': ('#0088CC', '#ffffff'),
            'discord': ('#5865F2', '#ffffff')
        }
        
    def download_icon(self, platform, size=100):
        """Download social media icon"""
        try:
            if platform in self.social_icons:
                response = requests.get(self.social_icons[platform])
                icon = Image.open(BytesIO(response.content))
                icon = icon.convert("RGBA")
                icon = icon.resize((size, size), Image.Resampling.LANCZOS)
                return icon
            return None
        except:
            return self.create_fallback_icon(platform, size)
    
    def create_fallback_icon(self, platform, size=100):
        """Create a fallback icon if download fails"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse([5, 5, size-5, size-5], fill=self.hex_to_rgb(self.color_presets[platform][0]))
        
        try:
            font = ImageFont.truetype("arial.ttf", size//2)
        except:
            font = ImageFont.load_default()
        
        text = platform[0].upper()
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        draw.text(position, text, fill='white', font=font)
        return img
    
    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def create_gradient_background(self, width, height, colors):
        """Create a gradient background"""
        base = Image.new('RGB', (width, height), colors[0])
        if len(colors) == 1:
            return base
        
        for y in range(height):
            ratio = y / height
            r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
            g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
            b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
            for x in range(width):
                base.putpixel((x, y), (r, g, b))
        return base
    
    def generate_awesome_qr(self, data, platform=None, style='default', 
                          background_colors=None, qr_color=None, 
                          add_logo=True, logo_size=80, output_file='awesome_qr.png'):
        """Generate QR code with all features"""
        
        if platform and platform in self.color_presets:
            fill_color = self.hex_to_rgb(self.color_presets[platform][0])
            back_color = self.hex_to_rgb(self.color_presets[platform][1])
        else:
            fill_color = self.hex_to_rgb('#000000')
            back_color = self.hex_to_rgb('#FFFFFF')
        
        if qr_color:
            fill_color = self.hex_to_rgb(qr_color)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGB')
        
        if style == 'rounded':
            qr_img = self.apply_rounded_corners(qr_img)
        elif style == 'gradient':
            if background_colors:
                bg_colors_rgb = [self.hex_to_rgb(c) for c in background_colors]
            else:
                bg_colors_rgb = [back_color, back_color]
            background = self.create_gradient_background(qr_img.width, qr_img.height, bg_colors_rgb)
            qr_img = Image.blend(background, qr_img, 0.8)
        
        if add_logo and platform:
            logo = self.download_icon(platform, logo_size)
            if logo:
                qr_img = self.add_logo_to_qr(qr_img, logo)
        
        if platform:
            qr_img = self.add_platform_text(qr_img, platform)
        
        qr_img.save(output_file, 'PNG', quality=95)
        print(f"✅ Awesome QR code generated: {output_file}")
        return qr_img
    
    def apply_rounded_corners(self, image, radius=30):
        """Apply rounded corners to the image"""
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
        result = Image.new('RGB', image.size, (255, 255, 255))
        result.paste(image, mask=mask)
        return result
    
    def add_logo_to_qr(self, qr_img, logo):
        """Add logo to the center of QR code"""
        qr_width, qr_height = qr_img.size
        logo_width, logo_height = logo.size
        position = ((qr_width - logo_width) // 2, (qr_height - logo_height) // 2)
        qr_with_logo = qr_img.copy()
        qr_with_logo.paste(logo, position, logo)
        return qr_with_logo
    
    def add_platform_text(self, image, platform):
        """Add platform name below QR code"""
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        text = f"{platform.upper()}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        position = ((image.width - text_width) // 2, image.height - 40)
        shadow_color = (100, 100, 100)
        text_color = self.hex_to_rgb(self.color_presets.get(platform, ('#000000', '#FFFFFF'))[0])
        
        draw.text((position[0]+2, position[1]+2), text, fill=shadow_color, font=font)
        draw.text(position, text, fill=text_color, font=font)
        return image

def get_user_input():
    """Get all inputs from user interactively"""
    
    print("🎯" + "="*60)
    print("           AWESOME QR CODE GENERATOR")
    print("="*60)
    
    # Step 1: Get data for QR code
    print("\n📝 STEP 1: What do you want to encode in QR code?")
    print("   (URL, text, phone number, email, etc.)")
    data = input("👉 Enter your data: ").strip()
    
    if not data:
        print("❌ Error: You must enter some data!")
        return None
    
    # Step 2: Choose social media platform
    print("\n📱 STEP 2: Choose social media platform (or skip for plain QR):")
    platforms = ['github', 'youtube', 'facebook', 'twitter', 'instagram', 
                'linkedin', 'whatsapp', 'telegram', 'discord', 'none']
    
    for i, platform in enumerate(platforms, 1):
        print(f"   {i}. {platform.upper()}")
    
    while True:
        try:
            choice = input("👉 Choose platform (1-10): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 10:
                platform_choice = platforms[int(choice)-1]
                if platform_choice == 'none':
                    platform = None
                else:
                    platform = platform_choice
                break
            else:
                print("❌ Please enter a number between 1-10")
        except:
            print("❌ Invalid input. Please try again.")
    
    # Step 3: Choose style
    print("\n🎨 STEP 3: Choose QR code style:")
    styles = ['default', 'rounded', 'gradient']
    for i, style in enumerate(styles, 1):
        print(f"   {i}. {style.upper()}")
    
    while True:
        try:
            choice = input("👉 Choose style (1-3): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= 3:
                style = styles[int(choice)-1]
                break
            else:
                print("❌ Please enter a number between 1-3")
        except:
            print("❌ Invalid input. Please try again.")
    
    # Step 4: Custom colors (optional)
    print("\n🌈 STEP 4: Custom colors (press Enter to use default):")
    qr_color = input("👉 QR color (hex e.g., #FF0000 for red): ").strip()
    if not qr_color:
        qr_color = None
    
    # Step 5: Logo size
    print("\n📏 STEP 5: Logo size (if using platform):")
    logo_size = input("👉 Logo size (80-150, default 80): ").strip()
    if logo_size.isdigit() and 80 <= int(logo_size) <= 150:
        logo_size = int(logo_size)
    else:
        logo_size = 80
    
    # Step 6: Filename
    print("\n💾 STEP 6: Save file as:")
    default_name = f"{platform}_qr.png" if platform else "my_qr_code.png"
    filename = input(f"👉 Filename (default: {default_name}): ").strip()
    if not filename:
        filename = default_name
    
    if not filename.endswith('.png'):
        filename += '.png'
    
    return {
        'data': data,
        'platform': platform,
        'style': style,
        'qr_color': qr_color,
        'logo_size': logo_size,
        'filename': filename
    }

def main():
    """Main function to run the QR code generator"""
    qr_gen = AwesomeQRGenerator()
    
    print("🚀 WELCOME TO AWESOME QR GENERATOR!")
    print("   Let's create your custom QR code...\n")
    
    while True:
        # Get user inputs
        user_inputs = get_user_input()
        
        if not user_inputs:
            continue
        
        try:
            # Generate QR code
            qr_gen.generate_awesome_qr(
                data=user_inputs['data'],
                platform=user_inputs['platform'],
                style=user_inputs['style'],
                qr_color=user_inputs['qr_color'],
                logo_size=user_inputs['logo_size'],
                output_file=user_inputs['filename']
            )
            
            print(f"\n🎉 SUCCESS! Your QR code has been generated!")
            print(f"📁 File: {user_inputs['filename']}")
            
        except Exception as e:
            print(f"❌ Error generating QR code: {e}")
        
        # Ask if user wants to create another QR
        print("\n" + "="*50)
        another = input("🔄 Create another QR code? (y/n): ").strip().lower()
        if another != 'y':
            print("\n👋 Thank you for using Awesome QR Generator!")
            break

if __name__ == "__main__":
    main()