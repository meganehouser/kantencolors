import gif
from collections import OrderedDict


def str_to_Color(color_code):
    color = color_code.strip('#')
    r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
    return gif.Color(r, g, b)


def json_to_data(colors, direction, width, height):
    """
    JSON convert to gif data and colors.
    """

    color_idx = 0
    color_dic = OrderedDict()
    color_data = []

    for elm in colors:
        color = elm['color']
        if color in color_dic:
            idx = color_dic[color]
        else:
            idx = color_idx
            color_dic[color] = idx
            color_idx += 1

    if direction == 'portrait':
        for elm in colors:
            length = width * (height * int(elm['ratio']) * 0.01)
            color_data.extend([color_dic[elm['color']] for _ in range(int(length))])
    else:
        line = []
        for elm in colors:
            length = width * int(elm['ratio']) * 0.01
            line.extend([color_dic[elm['color']] for _ in range(int(length))])

        for _ in range(height):
            color_data.extend(line)

    colors = [str_to_Color(c) for c in color_dic.keys()]

    return (color_data, colors)


def get_image_size(direction):
    if direction == 'portrait':
        return {'height': 500, 'width': 300}
    else:
        return {'height': 300, 'width': 500}


def imagefy(json):
    direction = json['direction']
    size = get_image_size(direction)
    width, height = size['width'], size['height']
    data, colors = json_to_data(json['colors'], direction, width, height)
    print(colors)
    gif_image = gif.Gif(data, width, height, colors)

    return gif_image.to_bytes()
