import io
import time
import logging
from .random_fractal import generate_infinite_fractal_coords
from .fractal import generate_fractal
from PIL import Image

logger = logging.getLogger(__name__)

def get_beatiful_fractal() -> bytes:
    att = 0
    start_time = time.perf_counter()
    matrix = None

    while matrix is None:
        att += 1
        x_min, x_max, y_min, y_max = generate_infinite_fractal_coords()

        logger.debug(f"Попытка номер {att}, координаты: {x_min:.2f}, {x_max:.2f}, {y_min:.2f}, {y_max:.2f}")

        matrix = generate_fractal(800, 800, 100, x_min, x_max, y_min, y_max)

    end_time = time.perf_counter()
    exec_time = (end_time - start_time) * 1000

    logger.info(f'Фрактал сгенерирован за {att} попыток и {exec_time:.2f} мс')

    matrix = (matrix * (255 // 100)).astype('uint8')
    img = Image.fromarray(matrix, mode='L')

    io_buf = io.BytesIO()
    img.save(io_buf, format='PNG')

    return io_buf.getvalue()

