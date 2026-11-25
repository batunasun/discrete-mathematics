import fitz  # PyMuPDF
import os

pdf_path = "book.pdf"
out_dir = "ch09_pages"
os.makedirs(out_dir, exist_ok=True)

doc = fitz.open(pdf_path)

# Номын 497-р хуудас нь PDF дээр ойролцоогоор 579-р хуудас (индекс 578) дээр эхэлнэ
start_page = 505  
end_page = 567    

for i in range(start_page, min(end_page, len(doc))):
    page = doc[i]
    # 200 DPI нягтралтайгаар зураг болгох (томьёо, график тод харагдана)
    pix = page.get_pixmap(dpi=200)
    pix.save(f"{out_dir}/page_{i+1:03d}.png")

print("Амжилттай задаллаа!")