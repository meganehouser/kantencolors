import struct


class InvalidArgumentException(Exception):
    pass


class Color:
    def __init__(self, r, g, b):
        self.red = r
        self.green = g
        self.blue = b
        self._validate()

    def _validate(self):
        for v in [self.red, self.green, self.blue]:
            if not(0 <= v <= 255):
                raise InvalidArgumentException("invalid color")

    def element_iter(self):
        yield self.red
        yield self.green
        yield self.blue


class Gif:
    def __init__(self, data, width, height, colors):
        self.image_data = data
        self.logical_screen_width = width
        self.logical_screen_height = height
        self.global_color_resolution = len('{:b}'.format(len(colors) )) - 1
        self.colors = colors
        diff_len = pow(2, (self.global_color_resolution + 1)) - len(colors)
        self.colors.extend([Color(0, 0, 0) for _ in range(diff_len)])
        self._validate()

    def _validate(self):
        if not (0 < self.logical_screen_width < 65535):
            raise InvalidArgumentException("invalid widht")
        if not (0 < self.logical_screen_height < 65535):
            raise InvalidArgumentException("invalid height")
        if not (0 <= self.global_color_resolution < 7):
            raise InvalidArgumentException("invalid global color resolution")

    def _global_color_tables(self):
        for color in self.colors:
            yield from color.element_iter()

        pallet_len = pow(2, (self.global_color_resolution))
        for _ in range((pallet_len - len(self.colors)) * 3):
            yield 0

    def _get_header_data(self):
        data = bytearray()
        data.extend(b'GIF')  # signature
        data.extend(b'87a')  # gif version
        data.extend(struct.pack('<H', self.logical_screen_width))
        data.extend(struct.pack('<H', self.logical_screen_height))

        b = 1  # Global Color Table Flag
        b = b << 3 | self.global_color_resolution  # Color Resolution
        b = b << 1 | 0  # Size of Global Color Table
        b = b << 3 | self.global_color_resolution  # Sort Flagn
        data.append(b)

        data.append(0)  # Background Color Index
        data.append(0)  # Pixel Aspect Ratio

        data.extend([b for b in self._global_color_tables()])
        return data

    def _get_image_blocks(self):
        data = bytearray()
        data.append(0x2c)  # Image Separator
        data.extend([0x00, 0x00]) # Image Left Position
        data.extend([0x00, 0x00]) # Image Top Position
        data.extend(struct.pack('<H', self.logical_screen_width))
        data.extend(struct.pack('<H', self.logical_screen_height))
        b = 0 # Local Color Table Flag
        b = b << 1 | 0  # Interlace Flag
        b = b << 1 | 0  # Sort Flag
        b = b << 2 | 0  # Reversed
        b = b << 3 | 0  # Size of Local Color Table
        data.append(b)

        lzw = Lzw(len(self.colors))
        data.append(lzw.minimum_code_size)

        lzw_data = list(lzw.compress(self.image_data))
        lzw_len = len(lzw_data)

        while lzw_len > 0:
            if lzw_len > 255:
                data.append(255)
                data.extend(lzw_data[:255])
                lzw_data = lzw_data[255:]
                lzw_len -= 255
            else:
                data.append(lzw_len)
                data.extend(lzw_data)
                lzw_len = 0

        data.append(0x00)  # Block Terminator
        return data

    def to_bytes(self):
        data = self._get_header_data()
        data.extend(self._get_image_blocks())
        data.append(0x3b)
        return data


class Bits:
    def __init__(self):
        self.bits = []

    def append(self, value, bit_len):
        for i in range(bit_len):
           self.bits.insert(0, (value >> i & 1))

    def to_bytes(self):
        bits = self.bits
        while len(bits) > 0: 
            b = bits[-8:]
            for _ in range(len(b)):
                bits.pop() 

            byte = 0
            for i in range(len(b)):
                byte = (byte << 1) | b[i]

            yield byte


class Lzw:
    def __init__(self, dic_len):
        self.dic_len = dic_len
        self.max_code = (self.dic_len if self.dic_len > 2 else 4)
        self.minimum_code_size = len('{:b}'.format(self.max_code - 1))

    def compress(self, data):
        max_code = self.max_code
        max_code_bits = self.minimum_code_size

        def to_key(add, prev_key=[]):
            tmp = list(prev_key)
            tmp.append(add)
            return tuple(tmp)

        # 辞書初期化
        dic = {}
        for i in range(max_code):
            key = to_key(i)
            dic[key] = i

        # クリアコード
        dic[to_key(max_code)]  = max_code
        clear_code = max_code 

        # エンドコード
        max_code += 1
        dic[to_key(max_code)]  = max_code
        end_code = max_code 
        if max_code >= 1 << max_code_bits and max_code_bits < 12:
            max_code_bits += 1

        # 圧縮
        key = []
        result = Bits()
        result.append(clear_code, max_code_bits)

        for n, c in enumerate(data):
            prev_key = key
            key = to_key(c, prev_key)
            if key in dic:
                continue

            result.append(dic[prev_key], max_code_bits)

            if max_code < 4096:
                max_code += 1
                dic[key] = max_code
                if max_code == 1 << max_code_bits and max_code_bits < 12:
                    max_code_bits += 1

            key = to_key(c)
        else:
            if key in dic:
                result.append(dic[key], max_code_bits)

        result.append(end_code, max_code_bits)
        return result.to_bytes()

if __name__ == '__main__':
    data = [1,1,1,1,1,2,2,2,2,2,
            1,1,1,1,1,2,2,2,2,2,
            1,1,1,1,1,2,2,2,2,2,
            1,1,1,0,0,0,0,2,2,2,
            1,1,1,0,0,0,0,2,2,2,
            2,2,2,0,0,0,0,1,1,1,
            2,2,2,0,0,0,0,1,1,1,
            2,2,2,2,2,1,1,1,1,1,
            2,2,2,2,2,1,1,1,1,1,
            2,2,2,2,2,1,1,1,1,1]

    colors = [Color(255, 255, 255), Color(255, 0, 0), Color(0, 0, 255)]
    g = Gif(data, 10, 10, colors)
    with open("temp.gif", 'wb') as f:
            f.write(g.to_bytes())
