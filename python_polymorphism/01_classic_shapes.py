# Классический пример полиморфизма
# Разные фигуры — один метод area()

class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Circle:
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14 * self.radius ** 2


# Функции print_area не важно, какая именно фигура передана.
# Главное — чтобы у объекта был метод area().
def print_area(shape):
    print(f"Площадь: {shape.area()}")


if __name__ == "__main__":
    shapes = [
        Rectangle(4, 5),
        Circle(3),
        Rectangle(2, 8),
    ]

    for shape in shapes:
        print_area(shape)
