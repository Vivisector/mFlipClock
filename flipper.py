import tkinter as tk
from tkinter import Canvas, PhotoImage
from PIL import Image, ImageTk
import time
import os
import sys

def resource_path(relative_path):
    """Получает правильный путь к ресурсам как для исходного кода, так и для exe."""
    try:
        # Для PyInstaller
        if getattr(sys, 'frozen', False):
            # Получаем путь к временной директории PyInstaller
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)  # Для исходного кода
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"Ошибка при получении пути: {e}")
        return relative_path  # Возвращаем относительный путь, если ошибка

class FlipClockWithImages:
    def __init__(self, root):
        self.root = root
        self.show_seconds = tk.BooleanVar(value=True)  # Используем BooleanVar для привязки к чекбоксу
        self.root.overrideredirect(True)  # Убираем рамку окна

        self.update_window_geometry()  # Обновляем размеры окна

        # Устанавливаем прозрачность окна
        self.root.attributes("-topmost", False)  # Чтобы окно всегда было поверх других
        self.root.attributes("-alpha", 1.0)  # Прозрачность (при необходимости)
        self.root.attributes("-transparentcolor", "black")

        # Основной фрейм для организации элементов
        self.main_frame = tk.Frame(self.root, bg="black")
        self.main_frame.place(relwidth=1, relheight=1)  # Используем place для точного позиционирования
        # self.main_frame.place(width=200, height=100)  # Фиксированные размеры
        # self.main_frame.place(relwidth=0.9, relheight=0.5)  # Половина размеров родительского контейнера

        # Изначальные размеры канвы
        # canvas_width = 622
        canvas_width = 770
        canvas_height = 210
        delta_x = 67 # отступ от левого края канвы
        delta_y = 10  # отступ от левого края канвы
        # Создаем холст для отображения с более компактными размерами
        self.canvas = Canvas(self.main_frame, width=canvas_width, height=canvas_height, bg="black", bd=0,
                             highlightthickness=0)
        self.canvas.place(x=0, y=0)  # Позиционируем холст с точными размерами

        # Добавляем чекбокс под холстом
        self.checkbox_frame = tk.Frame(self.main_frame, bg="black")  # Фрейм для чекбокса
        # self.checkbox_frame.pack(fill="x")
        self.checkbox_frame.place(x=585, y=182)  # Позиционируем чекбокс

        self.seconds_checkbox = tk.Checkbutton(
            self.checkbox_frame,
            text="",
            variable=self.show_seconds,
            command=self.on_seconds_toggle,
            bg="black",
            fg="white",
            selectcolor="gray"
        )
        self.seconds_checkbox.pack(side="left", padx=0, pady=0)

        # Загружаем картинки для цифр от 0 до 9
        self.digits = []
        for i in range(10):  # 10 картинок для цифр от 0 до 9
            # filename = f"images/{i}.png"
            filename = resource_path(f"images/{i}.png")
            if os.path.exists(filename):
                self.digits.append(PhotoImage(file=filename))
            else:
                print(f"Не удалось найти картинку {filename} в папке 'images'.")
                raise ValueError(f"Не удалось найти картинку {filename} в папке 'images'.")

        # Уменьшаем картинки для секунд
        self.digits_seconds = [digit.subsample(3, 3) for digit in self.digits]  # Уменьшаем на 3x для секунд

        # Создаем объекты для отображения часов, минут и секунд
        self.time_display_hour_tens = self.canvas.create_image(150-delta_x, 98+delta_y, image=self.digits[0])  # Часы: десятки
        self.time_display_hour_ones = self.canvas.create_image(300-delta_x, 98+delta_y, image=self.digits[0])  # Часы: единицы

        self.time_display_minute_tens = self.canvas.create_image(460-delta_x, 98+delta_y, image=self.digits[0])  # Минуты: десятки
        self.time_display_minute_ones = self.canvas.create_image(610-delta_x, 98+delta_y, image=self.digits[0])  # Минуты: единицы

        if self.show_seconds:
            self.time_display_second_tens = self.canvas.create_image(650, 143, image=self.digits_seconds[0])
            self.time_display_second_ones = self.canvas.create_image(701, 143, image=self.digits_seconds[0])
        else:
            self.time_display_second_tens = None
            self.time_display_second_ones = None

        # Перетаскивание окна
        self.offset_x = 0
        self.offset_y = 0

        # Привязываем обработчики событий для перетаскивания
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

        # Обновляем время
        self.update_time()  # Важно: вызываем обновление времени для начала цикла

    def on_click(self, event):
        """Запоминаем начальные координаты при нажатии кнопки мыши"""
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        """Перемещаем окно в соответствии с движением мыши"""
        delta_xx = event.x - self.offset_x
        delta_xy = event.y - self.offset_y
        new_x = self.root.winfo_x() + delta_xx
        new_y = self.root.winfo_y() + delta_xy
        self.root.geometry(f"+{new_x}+{new_y}")

    def on_seconds_toggle(self):
        """Обновляет размеры окна при переключении отображения секунд"""
        self.update_window_geometry()
        self.update_time()

    def update_window_geometry(self):
        """Обновляет геометрию окна в зависимости от состояния секунд"""
        if self.show_seconds.get():
            self.root.geometry("735x220")
        else:
            self.root.geometry("629x220")

    def flip(self, current_time, new_time):
        """Анимация смены времени с использованием эффекта переворота"""
        for i in range(10):
            self.root.after(i * 50, self.animate_flip, current_time, new_time, i)

    def animate_flip(self, current_time, new_time, step):
        """Реализует шаг анимации с эффектом переворота"""

        # Проверяем, отображаются ли секунды
        show_seconds = self.show_seconds.get()

        # Преобразуем время в строки для каждого из элементов
        current_hour_tens = int(current_time[0])  # Десятки часов
        current_hour_ones = int(current_time[1])  # Единицы часов
        current_minute_tens = int(current_time[3])  # Десятки минут
        current_minute_ones = int(current_time[4])  # Единицы минут

        # Инициализация секунд только если они есть
        if show_seconds:
            # Если секунды есть, извлекаем их
            current_second_tens = int(current_time[6])  # Десятки секунд
            current_second_ones = int(current_time[7])  # Единицы секунд
        else:
            # Если секунд нет, устанавливаем в 0
            current_second_tens = current_second_ones = 0

        new_hour_tens = int(new_time[0])  # Десятки часов
        new_hour_ones = int(new_time[1])  # Единицы часов
        new_minute_tens = int(new_time[3])  # Десятки минут
        new_minute_ones = int(new_time[4])  # Единицы минут

        # Инициализация секунд только если они есть
        if show_seconds:
            new_second_tens = int(new_time[6])  # Десятки секунд
            new_second_ones = int(new_time[7])  # Единицы секунд
        else:
            new_second_tens = new_second_ones = 0

        # Обновляем картинки на холсте для часов, минут и секунд
        if step < 5:
            self.canvas.itemconfig(self.time_display_hour_tens, image=self.digits[current_hour_tens])
            self.canvas.itemconfig(self.time_display_hour_ones, image=self.digits[current_hour_ones])
            self.canvas.itemconfig(self.time_display_minute_tens, image=self.digits[current_minute_tens])
            self.canvas.itemconfig(self.time_display_minute_ones, image=self.digits[current_minute_ones])
            if show_seconds:
                # Показываем секунды
                self.canvas.itemconfig(self.time_display_second_tens, image=self.digits_seconds[current_second_tens])
                self.canvas.itemconfig(self.time_display_second_ones, image=self.digits_seconds[current_second_ones])

        else:
            self.canvas.itemconfig(self.time_display_hour_tens, image=self.digits[new_hour_tens])
            self.canvas.itemconfig(self.time_display_hour_ones, image=self.digits[new_hour_ones])
            self.canvas.itemconfig(self.time_display_minute_tens, image=self.digits[new_minute_tens])
            self.canvas.itemconfig(self.time_display_minute_ones, image=self.digits[new_minute_ones])
            if show_seconds:
                # Показываем секунды
                self.canvas.itemconfig(self.time_display_second_tens, image=self.digits_seconds[new_second_tens])
                self.canvas.itemconfig(self.time_display_second_ones, image=self.digits_seconds[new_second_ones])

    def update_time(self):
        if self.show_seconds.get():
            current_time = time.strftime("%H:%M:%S")
        else:
            current_time = time.strftime("%H:%M")
        self.flip(current_time, current_time)
        self.root.after(1000, self.update_time)


if __name__ == "__main__":
    root = tk.Tk()
    flip_clock = FlipClockWithImages(root)
    root.mainloop()
