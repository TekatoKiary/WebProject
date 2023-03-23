def is_under_queen_attack(position, queen_position):
    if type(position) != str or type(queen_position) != str:
        raise TypeError
    for i in [position, queen_position]:
        if len(i) != 2 or int(i[1]) not in range(9) or i[0].lower() not in 'abcdefgh':
            raise ValueError


class Rectangle:
    def __init__(self, width, height):
        for i in (width, height):
            if type(i) != int:
                raise TypeError
            if i < 0:
                raise ValueError
        self.width = width
        self.height = height

    def get_area(self):
        return self.width * self.height

    def get_perimeter(self):
        return self.width * 2 + self.height * 2
