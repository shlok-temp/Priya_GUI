from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import pyrebase as pb
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import FileReaderForm
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, img_as_float, img_as_ubyte
import rasterio
from skimage import exposure, filters
from io import BytesIO
from PIL import Image

image = None
# Create your views here.
def show_GUI(request):
    global image
    image = None
    if request.method == "POST":
        form = FileReaderForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file'].open("r")
            byte_stream = BytesIO(file.read())
            image = return_showing_image(Image.open(byte_stream))
            return redirect("show_image")
    else:
        form = FileReaderForm()      
        return render(request, 'manage_user/image_uploader.html', {'form': form})

def return_showing_image(im_path):
    image = np.asarray(im_path, dtype=np.uint8)
    ans = None
    def rgb_to_hsi(image):  # image is a 3D numpy array representing an RgB image
        R, G, B = image[:,:,0], image[:,:,1], image[:,:,2]
        I = (R + G + B) / 3
        S = 1 - np.min(image, axis=2) / (I + 1e-8)  # Avoid division by zero
        num = 0.5 * ((R - G) + (R - B))
        den = np.sqrt(abs((R - G)**2 + (R - B) * (G - B)))
        H = np.arccos(num / (den+10))  # Avoid division by zero
        H[B > G] = 2 * np.pi - H[B > G]
        H = H / (2 * np.pi)  # Normalize to [0, 1]
        return H, S, I

    def hsi_to_rgb(H, S, I):
        R, G, B = np.zeros_like(H), np.zeros_like(H), np.zeros_like(H) #making an array and assigning it as zero.
        H = H * 360  # Convert to degrees
        for i in range(H.shape[0]):
            for j in range(H.shape[1]):
                h = H[i, j]
                if h < 120:
                    B[i, j] = I[i, j] * (1 - S[i, j])
                    R[i, j] = I[i, j] * (1 + S[i, j] * np.cos(np.radians(h)) / np.cos(np.radians(60 - h)))
                    G[i, j] = 3 * I[i, j] - (R[i, j] + B[i, j])
                elif h < 240:
                    h -= 120
                    R[i, j] = I[i, j] * (1 - S[i, j])
                    G[i, j] = I[i, j] * (1 + S[i, j] * np.cos(np.radians(h)) / np.cos(np.radians(60 - h)))
                    B[i, j] = 3 * I[i, j] - (R[i, j] + G[i, j])
                else:
                    h -= 240
                    G[i, j] = I[i, j] * (1 - S[i, j])
                    B[i, j] = I[i, j] * (1 + S[i, j] * np.cos(np.radians(h)) / np.cos(np.radians(60 - h)))
                    R[i, j] = 3 * I[i, j] - (G[i, j] + B[i, j])
        return np.stack([R, G, B], axis=2)

    # Load and normalize image

    # Convert RGB to HSI
    H, S, I = rgb_to_hsi(image)
    #S = np.clip(S, 0, 255)  # Boost Saturation
    modified_image = hsi_to_rgb(H, S, I)
    print(modified_image)
    #modified_image = np.clip(modified_image, 0, 255)  # Clamp values to [0, 1]
    #modified_image = img_as_ubyte(modified_image)  # Convert to 8-bit unsigned integers
    image = Image.fromarray(np.uint8(image))
    modified_image = Image.fromarray(np.uint8(modified_image))
    print(modified_image)
    images = [Image.open(r"C:\Users\Hp\Downloads\WhatsApp Image 2024-11-28 at 21.13.50_d03ef46c.jpg"), Image.open(r"C:\Users\Hp\Downloads\WhatsApp Image 2024-11-28 at 21.14.24_1bff9480.jpg")]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    return(new_im)

def show_image(request):
    # Create or load a PIL Image object (for demonstration, creating a blank image)
    # image = Image.new('RGB', (200, 100), color='blue')  # Replace with your image logic
    global image
    print("here")
    if image is None:
        redirect('home')
    # # Save the image to a BytesIO object
    buffer = BytesIO()
    image.save(buffer, format='PNG')  # Change format as needed (e.g., JPEG)
    buffer.seek(0)

    # Return the image as an HTTP response
    return HttpResponse(buffer, content_type='image/png')