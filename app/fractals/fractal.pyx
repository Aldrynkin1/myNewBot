import numpy as np
cimport numpy as cnp
import logging

cy_logger = logging.getLogger(__name__)

cdef inline int calculate_pixels(double cx, double cy, int max_iter) noexcept:
    cdef double zx = 0.0;
    cdef double zy = 0.0;
    cdef double zx_new = 0.0;
    cdef int cur_iter = 0;

    while (zx * zx + zy * zy <= 4) and cur_iter != max_iter:
        zx_new = zx * zx - zy * zy + cx;
        zy = 2.0 * zx * zy + cy;
        zx = zx_new;

        cur_iter += 1;

    return cur_iter

cdef int fill_matrix(int[:, :] res, int w, int h, 
                        int max_iter,
                            double x_min, double x_max, 
                                double y_min, double y_max) noexcept:
    cdef int x, y, current_iter, has_black = 0, has_background = 0

    for y in range(h):
        for x in range(w):
            current_iter = calculate_pixels(x_min + x * (x_max - x_min) / w, y_min + y * (y_max - y_min) / h, max_iter)

            res[y, x] = current_iter

            if current_iter == max_iter:has_black = 1
            if current_iter < 5:has_background = 1

    return 1 if (has_black and has_background) else 0

def generate_fractal(int w, int h, int max_iter,
                         double x_min, double x_max,
                            double y_min, double y_max):
    res_np = np.zeros((h, w), dtype=np.int32)

    if fill_matrix(res_np, w, h, max_iter, x_min, x_max, y_min, y_max):
        return res_np

    cy_logger.debug("Перерисовка фрактала из-за его монотонности")
    return None