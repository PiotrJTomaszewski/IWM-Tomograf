def generate_line(x1, y1, x2, y2):
    """
    Bresenham algorithm has its limitations e.g. it can only generate lines facing one direction.
    This function is a workaround to make sure a correct line will be generated.
    """
    delta_y = abs(y1 - y2)
    delta_x = abs(x1 - x2)
    if delta_y > delta_x:
        points = generate_line(y1, x1, y2, x2)
        for i in range(len(points)):
            points[i] = (points[i][1], points[i][0])
    elif y2 < y1 and x2 < x1:
        points = _bresenham(x1, y1, x1 + delta_x, y1 + delta_y)
        for i in range(len(points)):
            points[i] = (2 * x1 - points[i][0], 2 * y1 - points[i][1])
    elif y2 < y1:
        points = _bresenham(x1, y1, x2, y1 + delta_y)
        for i in range(len(points)):
            points[i] = (points[i][0], 2 * y1 - points[i][1])
    elif x2 < x1:
        points = _bresenham(x1, y1, x1 + delta_x, y2)
        for i in range(len(points)):
            points[i] = (2 * x1 - points[i][0], points[i][1])
    else:
        points = _bresenham(x1, y1, x2, y2)
    return points


def _bresenham(x1, y1, x2, y2):
    """
    This function uses Bresenham algorithm to
    The algorithm assumes that the change in x is greater that the change in y.
    The line can only go down and to the right.
    From: http://www.cs.put.poznan.pl/swilk/pmwiki/uploads/Dydaktyka/bresenham-int.pdf
    """
    delta_x = x2 - x1
    delta_y = y2 - y1
    j = y1
    error = delta_y - delta_x
    points = []
    for i in range(x1, x2 + 1):  # +1 to include the final (last) pixel
        points.append((i, j))
        if error >= 0:
            j += 1
            error -= delta_x
        error += delta_y
    return points


def __test():
    # For test purposes only
    import matplotlib.pyplot as plt
    import numpy as np

    img = np.zeros((200, 200, 3))
    points = generate_line(10, 50, 150, 150)
    for i in range(len(points)):
        img[points[i][0], points[i][1]] = 1
    plt.imshow(img)
    plt.show()


if __name__ == '__main__':
    # For test purposes only
    __test()
