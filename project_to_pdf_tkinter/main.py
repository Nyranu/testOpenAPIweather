import os
import textwrap
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

import fitz
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


class ProjectToPdfApp:
    ALLOWED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".scss", ".json",
        ".md", ".txt", ".yml", ".yaml", ".xml", ".java", ".c", ".cpp", ".h",
        ".cs", ".go", ".rs", ".php", ".sql",
    }

    IGNORED_DIRS = {
        ".git", ".idea", ".vscode", "node_modules", ".venv", "venv", "env",
        "__pycache__", "dist", "build", ".next", "out", "target", "bin", "obj",
    }

    MAX_FILE_SIZE = 1 * 1024 * 1024

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Project to PDF (Tkinter)")
        self.root.geometry("1000x760")

        self.selected_folder: Path | None = None
        self.output_dir = Path(__file__).resolve().parent / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pdf_regular_font, self.pdf_bold_font, self.pdf_mono_font = self.register_pdf_fonts()

        self.pdf_path: Path | None = None
        self.pdf_doc: fitz.Document | None = None
        self.current_page = 0
        self.total_pages = 0
        self.tk_preview_image = None
        self.zoom_level = 1.5
        self.min_zoom = 0.5
        self.max_zoom = 4.0
        self.zoom_step = 0.25

        self._build_ui()

    def register_pdf_fonts(self) -> tuple[str, str, str]:
        regular_candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]
        bold_candidates = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        ]
        mono_candidates = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Supplemental/Courier New.ttf",
        ]

        regular_font = self._register_font_from_candidates("AppRegular", regular_candidates, fallback="Helvetica")
        bold_font = self._register_font_from_candidates("AppBold", bold_candidates, fallback="Helvetica-Bold")
        mono_font = self._register_font_from_candidates("AppMono", mono_candidates, fallback="Courier")

        return regular_font, bold_font, mono_font

    def _register_font_from_candidates(self, font_name: str, candidates: list[str], fallback: str) -> str:
        for font_path in candidates:
            if Path(font_path).exists():
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    return font_name
                except Exception:
                    continue
        return fallback

    def _build_ui(self):
        top_frame = tk.Frame(self.root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        select_btn = tk.Button(top_frame, text="Выбрать папку", command=self.select_folder)
        select_btn.pack(side=tk.LEFT)

        self.folder_label = tk.Label(
            top_frame,
            text="Папка не выбрана",
            anchor="w",
            justify=tk.LEFT,
            wraplength=780,
            padx=10,
        )
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.preview_frame = tk.Frame(self.root, bd=1, relief=tk.SOLID, bg="#f7f7f7")
        self.preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.preview_canvas = tk.Canvas(self.preview_frame, bg="#f7f7f7", highlightthickness=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        self.preview_canvas.create_text(
            20,
            20,
            anchor=tk.NW,
            text="PDF пока не создан",
            fill="#666",
            font=("Arial", 14),
        )

        preview_v_scroll = tk.Scrollbar(self.preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        preview_v_scroll.grid(row=0, column=1, sticky="ns")
        preview_h_scroll = tk.Scrollbar(self.preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        preview_h_scroll.grid(row=1, column=0, sticky="ew")

        self.preview_canvas.configure(yscrollcommand=preview_v_scroll.set, xscrollcommand=preview_h_scroll.set)
        self.preview_frame.grid_rowconfigure(0, weight=1)
        self.preview_frame.grid_columnconfigure(0, weight=1)
        self.preview_canvas.config(scrollregion=self.preview_canvas.bbox(tk.ALL))

        bottom_frame = tk.Frame(self.root, padx=10, pady=10)
        bottom_frame.pack(fill=tk.X)

        convert_btn = tk.Button(bottom_frame, text="Конвертировать в PDF", command=self.convert_project_to_pdf)
        convert_btn.pack(side=tk.LEFT)

        prev_btn = tk.Button(bottom_frame, text="Предыдущая страница", command=self.previous_page)
        prev_btn.pack(side=tk.LEFT, padx=(20, 5))

        next_btn = tk.Button(bottom_frame, text="Следующая страница", command=self.next_page)
        next_btn.pack(side=tk.LEFT)

        self.page_label = tk.Label(bottom_frame, text="Страница 0 / 0", padx=15)
        self.page_label.pack(side=tk.LEFT)

        zoom_out_btn = tk.Button(bottom_frame, text="Уменьшить", command=self.zoom_out)
        zoom_out_btn.pack(side=tk.LEFT, padx=(10, 5))

        zoom_in_btn = tk.Button(bottom_frame, text="Увеличить", command=self.zoom_in)
        zoom_in_btn.pack(side=tk.LEFT, padx=5)

        zoom_reset_btn = tk.Button(bottom_frame, text="Сбросить масштаб", command=self.reset_zoom)
        zoom_reset_btn.pack(side=tk.LEFT, padx=5)

        self.zoom_label = tk.Label(bottom_frame, text="Масштаб: 150%", padx=10)
        self.zoom_label.pack(side=tk.LEFT)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Выберите папку проекта")
        if not folder:
            return

        self.selected_folder = Path(folder)
        self.folder_label.config(text=str(self.selected_folder))

    def convert_project_to_pdf(self):
        if not self.selected_folder:
            messagebox.showwarning("Папка не выбрана", "Сначала выберите папку с проектом.")
            return

        files = self.collect_project_files(self.selected_folder)
        if not files:
            messagebox.showwarning("Нет файлов", "Не найдено подходящих текстовых файлов для PDF.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.pdf_path = self.output_dir / f"project_report_{timestamp}.pdf"

        try:
            self.generate_pdf(self.selected_folder, files, self.pdf_path)
        except Exception as error:
            messagebox.showerror("Ошибка создания PDF", f"Не удалось создать PDF:\n{error}")
            return

        self.load_pdf_preview(self.pdf_path)

    def collect_project_files(self, root_folder: Path) -> list[Path]:
        collected: list[Path] = []

        for current_root, dirs, files in os.walk(root_folder):
            dirs[:] = [directory for directory in dirs if directory not in self.IGNORED_DIRS]
            current_path = Path(current_root)

            for file_name in files:
                path = current_path / file_name

                if path.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                    continue

                try:
                    if path.stat().st_size > self.MAX_FILE_SIZE:
                        continue
                except OSError:
                    continue

                collected.append(path)

        return sorted(collected)

    def read_text_file(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1251"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue

        return path.read_text(encoding="utf-8", errors="replace")

    def generate_pdf(self, project_root: Path, files: list[Path], output_pdf: Path):
        _, page_height = A4
        margin = 40
        line_height = 12
        max_chars_per_line = 100
        code_wrapper = textwrap.TextWrapper(
            width=max_chars_per_line,
            replace_whitespace=False,
            drop_whitespace=False,
            break_long_words=True,
            break_on_hyphens=False,
        )

        pdf = canvas.Canvas(str(output_pdf), pagesize=A4)

        y = page_height - margin
        pdf.setFont(self.pdf_bold_font, 16)
        pdf.drawString(margin, y, "Отчёт по проекту")

        y -= 25
        pdf.setFont(self.pdf_regular_font, 10)
        pdf.drawString(margin, y, f"Путь: {project_root}")
        y -= 15
        pdf.drawString(margin, y, f"Создан: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        y -= 25
        pdf.setFont(self.pdf_bold_font, 12)
        pdf.drawString(margin, y, "Список файлов:")
        y -= 18

        pdf.setFont(self.pdf_regular_font, 9)
        for file_path in files:
            relative_path = file_path.relative_to(project_root).as_posix()
            for line in textwrap.wrap(relative_path, width=110):
                if y <= margin:
                    pdf.showPage()
                    y = page_height - margin
                    pdf.setFont(self.pdf_regular_font, 9)
                pdf.drawString(margin + 10, y, f"- {line}")
                y -= line_height

        for file_path in files:
            pdf.showPage()
            y = page_height - margin

            rel_path = file_path.relative_to(project_root).as_posix()
            pdf.setFont(self.pdf_bold_font, 12)
            pdf.drawString(margin, y, rel_path)
            y -= 18

            try:
                content = self.read_text_file(file_path)
            except Exception:
                messagebox.showwarning("Предупреждение", f"Не удалось прочитать файл:\n{file_path}")
                continue

            pdf.setFont(self.pdf_mono_font, 8)
            for original_line in content.splitlines() or [""]:
                wrapped_lines = code_wrapper.wrap(original_line) or [""]
                for wrapped in wrapped_lines:
                    if y <= margin:
                        pdf.showPage()
                        y = page_height - margin
                        pdf.setFont(self.pdf_mono_font, 8)
                    pdf.drawString(margin, y, wrapped)
                    y -= line_height

        pdf.save()

    def load_pdf_preview(self, pdf_path: Path):
        try:
            if self.pdf_doc is not None:
                self.pdf_doc.close()

            self.pdf_doc = fitz.open(str(pdf_path))
        except Exception as error:
            self.pdf_doc = None
            self.current_page = 0
            self.total_pages = 0
            self.tk_preview_image = None
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                20,
                20,
                anchor=tk.NW,
                text="PDF не удалось открыть",
                fill="#666",
                font=("Arial", 14),
            )
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox(tk.ALL))
            self.page_label.config(text="Страница 0 / 0")
            messagebox.showerror("Ошибка открытия PDF", f"Не удалось открыть PDF:\n{error}")
            return

        self.current_page = 0
        self.total_pages = len(self.pdf_doc)
        self.zoom_level = 1.5

        if self.total_pages == 0:
            messagebox.showwarning("Пустой PDF", "Созданный PDF не содержит страниц.")
            return

        self.update_zoom_label()
        self.preview_canvas.xview_moveto(0)
        self.preview_canvas.yview_moveto(0)
        self.render_current_page()

    def update_zoom_label(self):
        self.zoom_label.config(text=f"Масштаб: {int(self.zoom_level * 100)}%")

    def zoom_in(self):
        if self.pdf_doc is None:
            return
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_step)
            self.update_zoom_label()
            self.render_current_page()

    def zoom_out(self):
        if self.pdf_doc is None:
            return
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_step)
            self.update_zoom_label()
            self.render_current_page()

    def reset_zoom(self):
        if self.pdf_doc is None:
            return
        self.zoom_level = 1.5
        self.update_zoom_label()
        self.render_current_page()

    def render_current_page(self):
        if self.pdf_doc is None or self.total_pages == 0:
            return

        try:
            page = self.pdf_doc.load_page(self.current_page)
            matrix = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=matrix)

            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            self.tk_preview_image = ImageTk.PhotoImage(image)
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_preview_image)
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox(tk.ALL))
            self.page_label.config(text=f"Страница {self.current_page + 1} / {self.total_pages}")
            self.update_zoom_label()
        except Exception as error:
            messagebox.showerror("Ошибка отображения", f"Не удалось отрисовать страницу PDF:\n{error}")

    def next_page(self):
        if self.pdf_doc is None:
            return
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.preview_canvas.xview_moveto(0)
            self.preview_canvas.yview_moveto(0)
            self.render_current_page()

    def previous_page(self):
        if self.pdf_doc is None:
            return
        if self.current_page > 0:
            self.current_page -= 1
            self.preview_canvas.xview_moveto(0)
            self.preview_canvas.yview_moveto(0)
            self.render_current_page()


if __name__ == "__main__":
    root = tk.Tk()
    app = ProjectToPdfApp(root)
    root.mainloop()
