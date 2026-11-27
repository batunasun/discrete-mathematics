import fitz  # PyMuPDF
import os

pdf_path = "book.pdf"
doc = fitz.open(pdf_path)

# Хайчлах бүлгүүдийн хуудасны хязгаар (PDF файлын 0-ээс эхэлсэн индексээр)
chapters = {
    "images/ch09": (505, 567),  # 9-р бүлэг (Номын 497–558-р хуудас)
    "images/ch10": (567, 635),  # 10-р бүлэг (Номын 559–626-р хуудас)
}

def extract_figures(page, out_dir, book_page_num):
    # Хуудасны толгой (header) болон хөл (footer)-ийг алгасах
    page_rect = page.rect
    content_top = 65
    content_bottom = page_rect.height - 50

    rects = []

    # 1. Вектор зураглалуудыг (граф, шугам, хүрээ) цуглуулах
    for d in page.get_drawings():
        r = d["rect"]
        # Хэт жижиг цэг эсвэл бүтэн хуудасны хүрээ, теоремын хайрцгийг алгасах
        if r.y0 < content_top or r.y1 > content_bottom:
            continue
        if r.width > 420 and r.height > 20:  # Теорем, тодорхойлолтын хүрээ эсвэл тусгаарлагч зураас
            continue
        if r.width < 3 and r.height < 3:
            continue
        rects.append(r)

    # 2. Растер зургуудыг цуглуулах
    for img in page.get_images(full=True):
        xref = img[0]
        for r in page.get_image_rects(xref):
            if r.y0 >= content_top and r.y1 <= content_bottom:
                rects.append(r)

    if not rects:
        return 0

    # Ойрхон байгаа элементүүдийг (графын орой, ирмэг, тэмдэглэгээг) нэг хайрцагт нэгтгэх
    merged = True
    margin = 18  # Графын хажуугийн тоо, үсгэн тэмдэглэгээг багтаах зай
    while merged:
        merged = False
        new_rects = []
        used = [False] * len(rects)
        for i in range(len(rects)):
            if used[i]:
                continue
            curr = fitz.Rect(rects[i])
            expanded = fitz.Rect(curr.x0 - margin, curr.y0 - margin, curr.x1 + margin, curr.y1 + margin)
            for j in range(i + 1, len(rects)):
                if not used[j] and expanded.intersects(rects[j]):
                    curr.include_rect(rects[j])
                    expanded = fitz.Rect(curr.x0 - margin, curr.y0 - margin, curr.x1 + margin, curr.y1 + margin)
                    used[j] = True
                    merged = True
            used[i] = True
            new_rects.append(curr)
        rects = new_rects

    # Дээрээс доош дарааллаар эрэмбэлж хадгалах
    rects.sort(key=lambda r: (round(r.y0 / 20), r.x0))
    saved_count = 0
    for idx, r in enumerate(rects, 1):
        # Хэт жижиг дүрсүүдийг алгасах
        if r.width < 25 or r.height < 25:
            continue
        clip = fitz.Rect(
            max(0, r.x0 - 12),
            max(content_top, r.y0 - 12),
            min(page_rect.width, r.x1 + 12),
            min(content_bottom, r.y1 + 12),
        )
        pix = page.get_pixmap(clip=clip, dpi=250)
        filename = f"{out_dir}/p{book_page_num}_fig{idx}.png"
        pix.save(filename)
        saved_count += 1

    return saved_count

for out_dir, (start_idx, end_idx) in chapters.items():
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for p_idx in range(start_idx, min(end_idx, len(doc))):
        book_page = p_idx - 8  # Номын бодит хуудасны дугаар
        total += extract_figures(doc[p_idx], out_dir, book_page)
    print(f"{out_dir}: нийт {total} зураг хайчилж хадгаллаа.")