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
            'Earth tones': 'https://m.media-amazon.com/images/I/61zCP-7ml5L._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71LUlKy0XaL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/71sy8bCwBbL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/715m4TNKR+L._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/612sZN+2cdL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/61f4PbGRu-L._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/5103dVPJtDL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/41DtMANM1DL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/61nUL2DlbvL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61-wxjsPkrL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/71tTpe-eXsL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61-qI48LGbL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/619yATaG-5L._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61G1ufndcCL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/51Vm41EeT1L._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/5184M-9vlaL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/71tTKByumiL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/61QJ56bafzL._AC_UL480_FMwebp_QL65_.jpg',
        },
        'Sweatshirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61HqUGX1DzL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/41eagf0sSXL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61zNzJLUoWL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/615zrXiutFL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/31+Ggy8gkGL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71AuJ5fPcsL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61Enop4LaXL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/51FrfH2ybVL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/31yW9h1lUpL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/71h0PAIMwkL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/51BsijmRsTL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/71sv893QSxL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/41sYgZpEcyL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71BUbrg6myL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61HxkDLUc7L._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/61tdiqPXQHL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/71h0PAIMwkL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/51aR4MSBLXL._AC_UL480_FMwebp_QL65_.jpg',

        }
    },
    'Female': {
        'Dress': {
            'Earth tones': 'https://m.media-amazon.com/images/I/81ySxC6qssL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/51DGD7Dq6RL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/51uqF7aiFiL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/51zwOgjCfwL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61PfMGSv60L._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71mSWSTevFL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/51K+xScNRXL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61c2woB3VtL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/51waCg58IrL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/51egiqAC5cL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/31j6-jywQGL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/71nzbrRQ42L._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/51AUCu28-7L._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/61vhu0KCuaL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/71dhvhuq3tL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/61clcwYCaPL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/51suEsggRLL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/61cp8q+QSdL._AC_UL480_FMwebp_QL65_.jpg',

        },
        'Top': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61cp8q+QSdL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/41i5lrfMdOL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/61mr8EBL5VL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/61wyl1RV3BL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71d1FzGnw8L._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/51IKCnm7-BL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/81ncwhtqAnL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/61JD6PndL9L._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/71uBjOb9nvL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/715WT7FfiDL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/71jTqSeA1OL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/61Y2W-ev2hL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61Au5uUfh9L._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/51TURd4woZL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/51e-tWBYh8L._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/71pOvHDGpPL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/81KpE2l+ehL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/619yCfDUGpL._AC_UL480_FMwebp_QL65_.jpg',

        },
        'Skirt': {
            'Earth tones': 'https://m.media-amazon.com/images/I/61Qv6q9GJoL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71RtBqn02xL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/51R-mFm8QIL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/711-IvDpSBL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/61RmtUM6X7L._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/31b8pSzCLeL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/51TQOulX0aL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/412xULayClL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/51rvxPBRgcL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/41ZNOB-WIVL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/51Eo3AOV0xL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/71g53mhpyEL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/61wjLMG4ypL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71upuZPZKHL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/51IUTj0l7JL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/613gJtL5UtL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/61XwUbXsO-L._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/61kXFS+FrzS._AC_UL480_FMwebp_QL65_.jpg',

        },
        'Blouse': {
            'Earth tones': 'https://m.media-amazon.com/images/I/71-Zg2CQ98L._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/51teuK+OSyL._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/91Td1cyTCpL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/81TNlUuTttL._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/71UbbAZl9FL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/71E0XKO6VnL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/91CHEUs4-YL._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/81ZbNpaHH6L._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/91kfI5y2sJL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61y4jTT6p2L._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/51vKiXdCfxL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/51ZenMjrTHL._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/71tV1tspPlL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/71vhm3ZJn7L._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/81z7w723SML._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/81Q4cLqCKwL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/712E04ducgL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/81M7pVDofuL._AC_UL480_FMwebp_QL65_.jpg',

        },
        'Sweater': {
            'Earth tones': 'https://m.media-amazon.com/images/I/712E04ducgL._AC_UL480_FMwebp_QL65_.jpg',
            'Olive green': 'https://m.media-amazon.com/images/I/71rSzDYj+1L._AC_UL480_FMwebp_QL65_.jpg',
            'Mustard': 'https://m.media-amazon.com/images/I/71J6TBpZOkL._AC_UL480_FMwebp_QL65_.jpg',
            'Terracotta': 'https://m.media-amazon.com/images/I/71rvBI48C4L._AC_UL480_FMwebp_QL65_.jpg',
            'Warm brown': 'https://m.media-amazon.com/images/I/51zjm-jMoiL._AC_UL480_FMwebp_QL65_.jpg',
            'Teal': 'https://m.media-amazon.com/images/I/617KHmKz6CL._AC_UL480_FMwebp_QL65_.jpg',
            'Light blue': 'https://m.media-amazon.com/images/I/61vqillj-6L._AC_UL480_FMwebp_QL65_.jpg',
            'Lavender': 'https://m.media-amazon.com/images/I/71BLbQ7rFQL._AC_UL480_FMwebp_QL65_.jpg',
            'Peach': 'https://m.media-amazon.com/images/I/7101PsjTPmL._AC_UL480_FMwebp_QL65_.jpg',
            'Soft pink': 'https://m.media-amazon.com/images/I/61mGrFb6rlL._AC_UL480_FMwebp_QL65_.jpg',
            'Mint green': 'https://m.media-amazon.com/images/I/51P7rvfLiGL._AC_UL480_FMwebp_QL65_.jpg',
            'Deep red': 'https://m.media-amazon.com/images/I/31Zom1n1U+L._AC_UL480_FMwebp_QL65_.jpg',
            'Navy blue': 'https://m.media-amazon.com/images/I/613717zkXAL._AC_UL480_FMwebp_QL65_.jpg',
            'Emerald green': 'https://m.media-amazon.com/images/I/617KHmKz6CL._AC_UL480_FMwebp_QL65_.jpg',
            'Royal purple': 'https://m.media-amazon.com/images/I/61IWenjqOkL._AC_UL480_FMwebp_QL65_.jpg',
            'Bright orange': 'https://m.media-amazon.com/images/I/816TttlgswL._AC_UL480_FMwebp_QL65_.jpg',
            'Pastel shades': 'https://m.media-amazon.com/images/I/71rUlyDhOeL._AC_UL480_FMwebp_QL65_.jpg',
            'Bold colors': 'https://m.media-amazon.com/images/I/71hxaEY0oKL._AC_UL480_FMwebp_QL65_.jpg',

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

    from waitress import serve
from app import app  # Ensure this matches your Flask app instance

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)