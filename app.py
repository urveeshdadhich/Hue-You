from flask import Flask, request, render_template
import cv2
import numpy as np
from sklearn.cluster import KMeans
import os
import requests
import json
import random
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Sample product images for each color and clothing type
SAMPLE_PRODUCTS = {
    'Male': {
        'T-Shirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/71deQmmADuL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71IG7-Xr18L._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61X0s-uiBYL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/81csgfZcMmL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/51KrL0HtdbL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/815WjQKfE7L._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61F6hy-BVqL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/610qQOPKGgL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61zmf1rqU2L._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/41yBoeUWrhL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61Fh0EZ3oYL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/710vk255SSL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/51A1dixZwrL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71FPRBaIoXL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/714zCgmX+JL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/514xJdCinsL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/51pg0J+yXfL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/61zfo184NoL._AC_UL480_FMwebp_QL65_.jpg',
        },
        'Shirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/81BJW9SY8WL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/51T70SlCdbL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/71DkADqhxUL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/510LZJBmcxL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71lbGcR4fHL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71RyUDlMyaL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/51yIybqYFTL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61WZCaPSNaL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61XrZzrrHpL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61E1LIfLCiL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61PM1+3eAqL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/51cNMNimNGL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/61j0SRsNJHL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61BJ1UhwNKL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61OD4n6H-WL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/418NYGZrg6L._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61Il02asbTL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71NSULhtAHL._AC_UL480_FMwebp_QL65_.jpg',
        },
        'Jeans': {
            'Earth tones': 'https://m.media-amazon.com/images/I/4155zVq0G4L._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/81GgBB4n-0L._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/8100-YWG1pL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/51QyV7rAGAL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61heErs06BL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61AEv0hvhmL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/61AEv0hvhmL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/71+R5uSZ5BL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61EhcfY5YKL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/612fsOpD20L._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61q-HzCMCmL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/51Pa4qf3F-L._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/514J9+s9LKL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71IOeN+4G7L._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71hA-y4ZcRL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/41FGWlZExsL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71IpvAWhZxL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/512XOGQUbaL._AC_UL480_FMwebp_QL65_.jpg',
        },
        'Jacket': {
            'Earth tones': 'https://m.media-amazon.com/images/I/41CXl4R2i-L._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
        },
        'Sweatshirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
        }
    },
    'Female': {
        'Dress': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
        },
        'Top': {
            'Earth tones': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
        },
        'Skirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
        },
        'Blouse': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
        },
        'Sweater': {
            'Earth tones': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61qcnAHZP3L._AC_UL320_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61-xQD7oHoL._AC_UL320_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/71tT8J5cFFL._AC_UL320_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61qE0yHqwGL._AC_UL320_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71SU+aCPJ5L._AC_UL320_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71jlppwpjmL._AC_UL320_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61uw5RDxKBL._AC_UL320_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71E6GwEQj0L._AC_UL320_.jpg',
        }
    }
}

def detect_skin_tone(image_path, k=3):
    """Detects the dominant skin tone from an uploaded image."""
    image = cv2.imread(image_path)
    if image is None:
        return None

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    
    if len(faces) == 0:
        face_region = image
    else:
        x, y, w, h = faces[0]
        face_region = image[y:y+h, x:x+w]
    
    face_region = cv2.cvtColor(face_region, cv2.COLOR_BGR2RGB)
    face_region = cv2.resize(face_region, (100, 100))
    pixels = face_region.reshape(-1, 3)
    
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(pixels)
    dominant_color = kmeans.cluster_centers_[np.argmax(np.bincount(kmeans.labels_))]
    
    r, g, b = dominant_color
    if r > 200 and g > 180 and b > 170:
        return 'Fair'
    elif r > 100 and g > 80 and b > 60:
        return 'Medium'
    else:
        return 'Dark'

def recommend_outfit(skin_tone):
    """Recommend outfit colors based on skin tone."""
    skin_tone_mapping = {
        'Fair': ['Pastel shades', 'Light blue', 'Lavender', 'Peach', 'Soft pink', 'Mint green'],
        'Medium': ['Earth tones', 'Olive green', 'Mustard', 'Terracotta', 'Warm brown', 'Teal'],
        'Dark': ['Bold colors', 'Deep red', 'Navy blue', 'Emerald green', 'Royal purple', 'Bright orange']
    }
    return skin_tone_mapping.get(skin_tone, ['Neutral colors'])

def get_product_image(color, gender, clothing_type):
    """Get a sample product image for the given color, gender, and clothing type."""
    try:
        return SAMPLE_PRODUCTS[gender][clothing_type][color]
    except KeyError:
        # Return a default image if the specific combination is not found
        return "https://m.media-amazon.com/images/I/61S2KdLI+nL._AC_UL320_.jpg"

def get_amazon_link(color, gender, clothing_type):
    """Generate Amazon search link for the given color, gender, and clothing type."""
    gender_query = "men" if gender == "Male" else "women"
    search_query = f"{color} {clothing_type} for {gender_query}"
    return f"https://www.amazon.in/s?k={quote_plus(search_query)}"

def get_product_recommendations(colors, gender, clothing_type):
    """Generate product recommendations with images and links."""
    products = []
    for color in colors:
        image_url = get_product_image(color, gender, clothing_type)
        amazon_link = get_amazon_link(color, gender, clothing_type)
        products.append({
            'color': color,
            'clothing_type': clothing_type,
            'image_url': image_url,
            'amazon_link': amazon_link
        })
    return products

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = None
    products = []
    
    if request.method == 'POST':
        # Check if a new file was uploaded
        if 'file' in request.files and request.files['file'].filename:
            file = request.files['file']
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            image_url = file_path
        else:
            # Use existing image from hidden field if no new file is chosen
            image_url = request.form.get('image_url')
            if not image_url:
                return render_template('index.html', error='No file uploaded')

        # Get gender and clothing type from form; set defaults if not provided
        gender = request.form.get('gender', 'Male')
        clothing_type = request.form.get('clothing_type', 'T-Shirt')

        skin_tone = detect_skin_tone(image_url)
        outfit_colors = recommend_outfit(skin_tone) if skin_tone else []
        
        # Generate product recommendations with images for carousel
        products = get_product_recommendations(outfit_colors, gender, clothing_type)
        
        return render_template('index.html', skin_tone=skin_tone, outfit_colors=outfit_colors, 
                               image_url=image_url, selected_gender=gender, 
                               selected_clothing_type=clothing_type, products=products)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)