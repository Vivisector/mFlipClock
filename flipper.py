import tkinter as tk
from tkinter import PhotoImage
import time
import os


class FlipClockWithImages:
    def __init__(self, root):
        self.root = root
        self.show_seconds = True  # Для отображения секунд по умолчанию
        self.root.overrideredirect(True)  # Убираем рамку окна
        self.root.geometry("820x230+100+100")  # Устанавливаем размер и позицию окна

        # Устанавливаем прозрачность окна
        self.root.attributes("-alpha", 0.7)  # 0.0 - полностью прозрачное, 1.0 - непрозрачное

        # Загружаем картинки для цифр от 0 до 9
        self.digits = []
        for i in range(10):  # 10 картинок для цифр от 0 до 9
            filename = f"images/{i}.png"
            if os.path.exists(filename):
                self.digits.append(PhotoImage(file=filename))
            else:
                print(f"Не удалось найти картинку {filename} в папке 'images'.")
                raise ValueError(f"Не удалось найти картинку {filename} в папке 'images'.")

        # Уменьшаем картинки для секунд
        self.digits_seconds = [digit.subsample(3, 3) for digit in self.digits]  # Уменьшаем на 2x для секунд

        # Создаем холст для отображения
        # self.canvas = tk.Canvas(self.root, width=600, height=200, bg='black')
        self.canvas = tk.Canvas(self.root, width=1200, height=200, bg='black')
        self.canvas.pack()

        # Создаем объекты для отображения часов, минут и секунд
        self.time_display_hour_tens = self.canvas.create_image(150, 100, image=self.digits[0])  # Часы: десятки
        self.time_display_hour_ones = self.canvas.create_image(300, 100, image=self.digits[0])  # Часы: единицы

        self.time_display_minute_tens = self.canvas.create_image(470, 100, image=self.digits[0])  # Минуты: десятки
        self.time_display_minute_ones = self.canvas.create_image(620, 100, image=self.digits[0])  # Минуты: единицы
        if self.show_seconds:
            self.time_display_second_tens = self.canvas.create_image(730, 160,
                                                                     image=self.digits_seconds[0])  # Секунды: десятки
            self.time_display_second_ones = self.canvas.create_image(783, 160,
                                                                     image=self.digits_seconds[0])  # Секунды: единицы

        # Обновляем время
        self.update_time()  # Важно: вызываем обновление времени для начала цикла

        # Перетаскивание окна
        self.offset_x = 0
        self.offset_y = 0

        # Привязываем обработчики событий для перетаскивания
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def on_click(self, event):
        """Запоминаем начальные координаты при нажатии кнопки мыши"""
        self.offset_x = event.x
        self.offset_y = event.y

    def on_drag(self, event):
        """Перемещаем окно в соответствии с движением мыши"""
        delta_x = event.x - self.offset_x
        delta_y = event.y - self.offset_y
        new_x = self.root.winfo_x() + delta_x
        new_y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def flip(self, current_time, new_time):
        """Анимация смены времени с использованием эффекта переворота"""
        for i in range(10):
            self.root.after(i * 50, self.animate_flip, current_time, new_time, i)

    def animate_flip(self, current_time, new_time, step):
        """Реализует шаг анимации с эффектом переворота"""

        # Преобразуем время в строки для каждого из элементов
        current_hour_tens = int(current_time[0])  # Десятки часов
        current_hour_ones = int(current_time[1])  # Единицы часов
        current_minute_tens = int(current_time[3])  # Десятки минут
        current_minute_ones = int(current_time[4])  # Единицы минут
        if self.show_seconds:
            current_second_tens = int(current_time[6])  # Десятки секунд
            current_second_ones = int(current_time[7])  # Единицы секунд

        new_hour_tens = int(new_time[0])  # Десятки часов
        new_hour_ones = int(new_time[1])  # Единицы часов
        new_minute_tens = int(new_time[3])  # Десятки минут
        new_minute_ones = int(new_time[4])  # Единицы минут
        if self.show_seconds:
            new_second_tens = int(new_time[6])  # Десятки секунд
            new_second_ones = int(new_time[7])  # Единицы секунд

        # Обновляем картинки на холсте для часов, минут и секунд
        if step < 5:
            self.canvas.itemconfig(self.time_display_hour_tens, image=self.digits[current_hour_tens])
            self.canvas.itemconfig(self.time_display_hour_ones, image=self.digits[current_hour_ones])
            self.canvas.itemconfig(self.time_display_minute_tens, image=self.digits[current_minute_tens])
            self.canvas.itemconfig(self.time_display_minute_ones, image=self.digits[current_minute_ones])
            if self.show_seconds:
                # Показываем секунды
                self.canvas.itemconfig(self.time_display_second_tens, image=self.digits_seconds[current_second_tens])
                self.canvas.itemconfig(self.time_display_second_ones, image=self.digits_seconds[current_second_ones])

        else:
            self.canvas.itemconfig(self.time_display_hour_tens, image=self.digits[new_hour_tens])
            self.canvas.itemconfig(self.time_display_hour_ones, image=self.digits[new_hour_ones])
            self.canvas.itemconfig(self.time_display_minute_tens, image=self.digits[new_minute_tens])
            self.canvas.itemconfig(self.time_display_minute_ones, image=self.digits[new_minute_ones])
            if self.show_seconds:
                # Показываем секунды
                self.canvas.itemconfig(self.time_display_second_tens, image=self.digits_seconds[new_second_tens])
                self.canvas.itemconfig(self.time_display_second_ones, image=self.digits_seconds[new_second_ones])


    def update_time(self):
        if self.show_seconds:
            # Показываем секунды
            current_time = time.strftime("%H:%M:%S")  # Получаем текущее время

        else:
            # Скрываем секунды
            current_time = time.strftime("%H:%M")  # Получаем текущее время

        self.flip(current_time, current_time)  # анимация замены времени
        self.root.after(1000, self.update_time)  # обновляем каждую секунду


if __name__ == "__main__":
    root = tk.Tk()
    flip_clock = FlipClockWithImages(root)
    root.mainloop()
