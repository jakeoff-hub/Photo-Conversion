# HEIC Conversion

Convert iPhone photos (`.heic` / `.heif`) and other common images so you can put
them in a PDF, either as pages of a new PDF or as images you insert into an
existing PDF.

**Reads:** HEIC/HEIF, JPG, PNG, WebP, GIF, BMP, TIFF, AVIF (the type is detected
from the file itself, so a wrong extension is fine).
**Saves as:** PDF, JPG, PNG or WebP.

## Option 1: In the browser (no install)

Open `index.html` in any modern browser (Chrome, Edge, Firefox, Safari).

1. Drop in one or more photos.
2. Reorder or remove them with the arrow and ✕ buttons.
3. Under **Save as**, pick PDF, JPG, PNG or WebP. For PDF, also choose a page
   size (same as the photo, US Letter, or A4) and a margin.
4. Click **Download**. A PDF gets one photo per page; several images in another
   format download together as a `.zip`.

Conversion happens entirely in your browser. Photos are never uploaded.

## Option 2: Command line (Python)

```bash
pip install -r requirements.txt

# One PDF, one photo per page
python heic_convert.py IMG_0001.HEIC IMG_0002.HEIC -o photos.pdf

# A whole folder onto US Letter pages with ½-inch margins
python heic_convert.py ~/Pictures/scans -o scans.pdf --page letter --margin 0.5

# Convert to JPG, PNG or WebP (written next to the originals, or into a folder with -o)
python heic_convert.py ~/Pictures/scans --format jpg -o converted/
python heic_convert.py photo.heic --format png
```

Photos are rotated upright using their EXIF orientation. Run
`python heic_convert.py --help` for all options.

## Inserting a photo into an existing PDF

1. Convert the photo to JPG or PNG with either tool above.
2. Open the PDF in Adobe Acrobat, Preview (Mac), or a web editor such as
   Smallpdf or Sejda.
3. Use **Add image** / **Insert image** and choose the JPG.

To add photos as extra pages instead, make a PDF from them and merge it with
your document (Preview: drag pages between sidebars; Acrobat: *Combine Files*).
