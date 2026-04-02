# BCOS Badge Generator

Web tool for generating BCOS certification badges.

## Features

- Enter repo URL or cert ID
- Preview badge
- Copy markdown/HTML embed code
- 3 badge styles: flat, flat-square, for-the-badge

## Usage

Open `index.html` in browser.

## API Endpoints

```
GET /bcos/badge/{cert_id}.svg?style=flat
GET /bcos/badge/{cert_id}.svg?style=flat-square
GET /bcos/badge/{cert_id}.svg?style=for-the-badge
```

## Deploy

Static site - no backend needed. Just host `index.html`.