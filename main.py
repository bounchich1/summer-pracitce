"""Программа для обработки изображений """
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox

import cv2
from PIL import Image, ImageTk
import numpy as np

MAX_WIDTH = 800
MAX_HEIGHT = 600


def resize_image(image):
    """Функция изменения масштаба изображения для корректного отображения в рамках окна программы """
    height, width = image.shape[:2]
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        if width / height > MAX_WIDTH / MAX_HEIGHT:
            new_width = MAX_WIDTH
            new_height = int(MAX_WIDTH * height / width)
        else:
            new_height = MAX_HEIGHT
            new_width = int(MAX_HEIGHT * width / height)
        resized_image = cv2.resize(image, (new_width, new_height))
    else:
        resized_image = image
    return resized_image


def upload_image():
    """Функция загрузки изображения"""
    global img, canvas_img, img_pil, img_tk, drawing, rect_start
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not file_path:
        return

    try:
        img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение. Пожалуйста, выберите правильный файл изображения. Ошибка: {e}")
        return

    if img is None:
        messagebox.showerror("Ошибка", "Не удалось загрузить изображение. Пожалуйста, выберите правильный файл изображения.")
        return

    if len(img.shape) == 3 and img.shape[2] == 4:
        # Convert the image from RGBA to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    img = resize_image(img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    canvas.config(width=img_tk.width(), height=img_tk.height())
    canvas.create_image(0, 0, anchor=NW, image=img_tk)
    canvas_img = img.copy()

    # Reset drawing state
    drawing = False
    rect_start = None


def capture_image():
    """Функция снимка изображения с веб-камеры"""
    global img, canvas_img, img_pil, img_tk, drawing, rect_start
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Ошибка", "Не удалось получить доступ к веб-камере. "
                                       "Пожалуйста, проверьте веб-камеру и повторите попытку.")
        return

    ret, frame = cap.read()
    cap.release()

    if not ret:
        messagebox.showerror("Ошибка", "Не удалось захватить изображение с веб-камеры.")
        return

    img = frame
    img = resize_image(img)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)

    canvas.config(width=img_tk.width(), height=img_tk.height())
    canvas.create_image(0, 0, anchor=NW, image=img_tk)
    canvas_img = img.copy()

    # Reset drawing state
    drawing = False
    rect_start = None


def toggle_rectangle_drawing():
    """Функция перегключения рисования прямоугольников"""
    global drawing_rectangles, img
    if img is None:
        messagebox.showerror("Ошибка", "Нет изображния для обработки.")
        return
    drawing_rectangles = not drawing_rectangles
    if drawing_rectangles:
        draw_rect_button.config(text="Закончить рисовать прямоугольники")
    else:
        draw_rect_button.config(text="Начать рисовать прямоугольники")


def draw_rectangle_with_mouse(event):
    """Функция рисования прямоугольников мышкой"""
    global rect_start, rect_id
    if drawing_rectangles:
        if rect_start is None:
            rect_start = (event.x, event.y)
        else:
            canvas.delete(rect_id)
            rect_id = canvas.create_rectangle(rect_start[0], rect_start[1], event.x, event.y, outline="blue", width=2)


def stop_draw_rectangle(event):
    """Функция остановки рисования прямоугольников"""
    global rect_start, rect_id, img
    if drawing_rectangles and rect_start is not None:
        x1, y1 = rect_start
        x2, y2 = event.x, event.y
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        update_canvas(img)
        rect_start = None


def sharpen_image():
    """Функция увеличения резкости изображения"""
    if img is None:
        messagebox.showerror("Ошибка", "Нет изображния для обработки.")
        return

    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened_img = cv2.filter2D(img, -1, kernel)
    update_canvas(sharpened_img)


def select_red_intensity():
    """Функция маски по интенсивности красного"""
    if img is None:
        messagebox.showerror("Ошибка", "Нет изображния для обработки.")
        return

    try:
        red_intensity = simpledialog.askinteger("Ввод", "Введите предел интенсивности красного (0-255):", minvalue=0,
                                                maxvalue=255)
        if red_intensity is None:
            return
        red_channel = img[:, :, 2]
        mask = cv2.inRange(red_channel, red_intensity, 255)
        result_img = cv2.bitwise_and(img, img, mask=mask)
        update_canvas(result_img)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось применить маску интенсивности:")


def update_canvas(image):
    """Функция обновления холства"""
    global img, canvas_img, img_pil, img_tk
    img = image
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(image=img_pil)
    canvas.config(width=img_tk.width(), height=img_tk.height())
    canvas.create_image(0, 0, anchor=NW, image=img_tk)
    canvas_img = img.copy()


def save_image():
    """Функция сохранения изображения"""
    if img is None:
        messagebox.showerror("Ошибка", "Нет изображения для сохранения.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                             filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"),
                                                        ("All files", "*.*")])
    if not file_path:
        return
    try:
        cv2.imencode('.jpg', img)[1].tofile(file_path)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить изображение {e}")


def show_channel(channel):
    """Функция показа канала - красного, зеленого или синего"""
    if img is None:
        messagebox.showerror("Ошибка", "Нет изображния для обработки.")
        return

    if channel not in [0, 1, 2]:
        messagebox.showerror("Ошибка", "Указан недопустимый канал.")
        return

    channel_img = np.zeros_like(img)
    channel_img[:, :, channel] = img[:, :, channel]
    update_canvas(channel_img)


root = Tk()
root.title("Приложение обработки изображения")
root.minsize(1280, 720)

root.config(bg='#2b2b2b')

img = None
canvas_img = None
drawing = False
prev_x, prev_y = None, None
line_thickness = 1
rect_start = None
rect_id = None
drawing_rectangles = False

canvas = Canvas(root, bg='#3c3c3c')  # Set canvas background color
canvas.pack()

canvas.bind("<Button-1>", draw_rectangle_with_mouse)
canvas.bind("<B1-Motion>", draw_rectangle_with_mouse)
canvas.bind("<ButtonRelease-1>", stop_draw_rectangle)

button_frame = Frame(root, bg='#2b2b2b')  # Set button frame background color
button_frame.pack()

button_style_1 = {
    'bg': '#4c4c4c',
    'fg': 'white',
    'font': ('Arial', 12),
    'relief': 'raised',
    'borderwidth': 3,
    'width': 30,
    'activebackground': '#5c5c5c',
    'activeforeground': 'white'
}
button_style_2 = {
    'bg': '#4c4c4c',
    'fg': 'white',
    'font': ('Arial', 12),
    'relief': 'raised',
    'borderwidth': 3,
    'width': 50,
    'activebackground': '#5c5c5c',
    'activeforeground': 'white'
}
upload_button = Button(button_frame, text="Загрузить изобржание", command=upload_image, **button_style_2)
upload_button.grid(row=0, column=0, padx=10, pady=5)

capture_button = Button(button_frame, text="Снять изображение", command=capture_image, **button_style_2)
capture_button.grid(row=0, column=1, padx=10, pady=5)

draw_rect_button = Button(button_frame, text="Начать рисовать прямоугольники", command=toggle_rectangle_drawing,
                          **button_style_1)
draw_rect_button.grid(row=1, column=0, padx=5, pady=5)

sharpen_button = Button(button_frame, text="Повысить резкость", command=sharpen_image, **button_style_1)
sharpen_button.grid(row=1, column=1, padx=5, pady=5)

red_intensity_button = Button(button_frame, text="Выделить красную интеснивность",
                              command=select_red_intensity, **button_style_1)
red_intensity_button.grid(row=2, column=0, padx=5, pady=5)

red_channel_button = Button(button_frame, text="Показать красный канал",
                            command=lambda: show_channel(2), **button_style_1)
red_channel_button.grid(row=2, column=1, padx=5, pady=5)

green_channel_button = Button(button_frame, text="Показать зеленый канал",
                              command=lambda: show_channel(1), **button_style_1)
green_channel_button.grid(row=3, column=1, padx=5, pady=5)

blue_channel_button = Button(button_frame, text="Показать голубой канал",
                             command=lambda: show_channel(0), **button_style_1)
blue_channel_button.grid(row=4, column=1, padx=5, pady=5)

save_button = Button(button_frame, text="Сохранить изображение", command=save_image, **button_style_2)
save_button.grid(row=5, column=0, padx=10, pady=5)

root.mainloop()
