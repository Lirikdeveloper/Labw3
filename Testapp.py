import base64
import io
import os
import matplotlib.pyplot as plt
import requests
from flask import Flask, render_template, request, abort
from PIL import Image

app = Flask(__name__)
UPLOAD_FOLDER = './upload'  # папка для загруженных файлов
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
RECAPTCHA_SITE_KEY = '6LcOhgImAAAAAHkWgyRL8Dp9-AF1_P9cgxiWdb5j'
@app.route('/')
def index():
    return render_template('index1.html', sitekey=RECAPTCHA_SITE_KEY)

@app.route('/result', methods=['POST'])
def result():
    # Get the uploaded image
    recaptcha_response = request.form.get('g-recaptcha-response')
    if not recaptcha_response:
        abort(400, 'reCAPTCHA verification failed')
    payload = {
        'secret': '6LcOhgImAAAAALXMHXngn2pRZIzrNGy0tdRx05Tv',
        'response': recaptcha_response
    }
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', payload).json()
    if not response['success']:
        abort(400, 'reCAPTCHA verification failed')

    file = request.files['image']
    if not file:
        abort(400, 'No file was uploaded')
    angle = int(request.form['angle'])
    image = Image.open(file)
    image.save('upload/orig.jpg')
    width, height = image.size
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.seek(0)
    colors = image.getcolors(width * height)
    colors = sorted(colors, key=lambda c: -c[0])
    colors = colors[:10]
    labels = [f'#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}' for c in colors]
    values = [c[0] for c in colors]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=labels)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    buf3 = io.BytesIO()
    fig.savefig(buf3, format='PNG')
    buf3.seek(0)
    colorgraph_64 = base64.b64encode(buf3.getvalue()).decode()
    plot_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'plot_orig.png')
    plt.savefig(plot_filename)

    img1 = image.crop((0, 0, width // 2, height // 2))
    img2 = image.crop((width // 2, 0, width, height // 2))
    img3 = image.crop((0, height // 2, width // 2, height))
    img4 = image.crop((width // 2, height // 2, width, height))

    # Rotate the image counterclockwise
    img1 = img1.rotate(angle, expand=True)
    img2 = img2.rotate(angle, expand=True)
    img3 = img3.rotate(angle, expand=True)
    img4 = img4.rotate(angle, expand=True)

    # Create a new image with the same size as the original image
    new_img = Image.new('RGB', (width, height))

    # Paste the 4 rotated images into the new image
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (width // 2, 0))
    new_img.paste(img3, (0, height // 2))
    new_img.paste(img4, (width // 2, height // 2))
    buf = io.BytesIO()
    new_img.save(buf, format='PNG')
    buf.seek(0)
    rotate_image = base64.b64encode(buf.getvalue()).decode()
    new_img.save('upload/rotated.jpg')

    # Get the selected color channels
    red = 'red' in request.form
    green = 'green' in request.form
    blue = 'blue' in request.form

    # Split the image into color channels
    if red:
        r, g, b =  new_img.split()
        r_image = Image.merge('RGB', (r, Image.new('L', r.size, 0) , Image.new('L', r.size, 0)))
        buffer1 = io.BytesIO()
        r_image.save(buffer1, format='PNG')
        buffer1.seek(0)
        img_r64 = base64.b64encode(buffer1.getvalue()).decode()
        r_image.save('upload/r_image.jpg')
        colors = r_image.getcolors(width * height)
        colors = sorted(colors, key=lambda c: -c[0])
        colors = colors[:10]
        labels = [f'#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}' for c in colors]
        values = [c[0] for c in colors]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=labels)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        buf1 = io.BytesIO()
        fig.savefig(buf1, format='PNG')
        buf1.seek(0)
        colorgraph_r64 = base64.b64encode(buf1.getvalue()).decode()
        plot_red = os.path.join(app.config['UPLOAD_FOLDER'], 'plot_red.png')
        plt.savefig(plot_red)
    if green:
        r, g, b =  new_img.split()
        g_image = Image.merge('RGB', (Image.new('L', g.size, 0), g, Image.new('L', g.size, 0)))
        buffer2 = io.BytesIO()
        g_image.save(buffer2, format='PNG')
        buffer2.seek(0)
        img_g64 = base64.b64encode(buffer2.getvalue()).decode()
        g_image.save('upload/g_image.jpg')
        colors = g_image.getcolors(width * height)
        colors = sorted(colors, key=lambda c: -c[0])
        colors = colors[:10]
        labels = [f'#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}' for c in colors]
        values = [c[0] for c in colors]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=labels)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        buf2 = io.BytesIO()
        fig.savefig(buf2, format='PNG')
        buf2.seek(0)
        colorgraph_g64 = base64.b64encode(buf2.getvalue()).decode()
        plot_gr = os.path.join(app.config['UPLOAD_FOLDER'], 'plot_gr.png')
        plt.savefig(plot_gr)
    if blue:
        r, g, b =  new_img.split()
        b_image = Image.merge('RGB', (Image.new('L', b.size, 0), Image.new('L', b.size, 0), b))
        buffer3 = io.BytesIO()
        b_image.save(buffer3, format='PNG')
        buffer3.seek(0)
        img_b64 = base64.b64encode(buffer3.getvalue()).decode()
        b_image.save('upload/b_image.jpg')
        colors = b_image.getcolors(width * height)
        colors = sorted(colors, key=lambda c: -c[0])
        colors = colors[:10]
        labels = [f'#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}' for c in colors]
        values = [c[0] for c in colors]
        fig, ax = plt.subplots()
        ax.bar(labels, values, color=labels)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        buf3 = io.BytesIO()
        fig.savefig(buf3, format='PNG')
        buf3.seek(0)
        colorgraph_b64 = base64.b64encode(buf3.getvalue()).decode()
        plot_bl = os.path.join(app.config['UPLOAD_FOLDER'], 'plot_bl.png')
        plt.savefig(plot_bl)

    # Render the result template with the original and split images
    return render_template('result1.html', img_64=img_64,rotate_image=rotate_image, red=red, green=green, blue=blue, img_r64=img_r64,  img_g64=img_g64, img_b64=img_b64,colorgraph_64=colorgraph_64, colorgraph_r64=colorgraph_r64, colorgraph_g64=colorgraph_g64, colorgraph_b64=colorgraph_b64)

if __name__ == '__main__':
    app.run(debug=True)