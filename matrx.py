class SparseMatrix:
    def __init__(self, n, m):
        self.n = n  # Количество строк
        self.m = m  # Количество столбцов
        self.values = []  # Ненулевые элементы
        self.columns = []  # Индексы столбцов для ненулевых элементов
        self.row_pointer = [0] * (n + 1)  # Указатели на начало строки

    def add(self, i, j, value):
        """Добавить элемент в матрицу (i, j)"""
        # Индексация строк и столбцов с 1
        value = int(value)
        if value != 0:
            self.values.append(value)
            self.columns.append(j - 1)  # Индексация столбцов с 0
            self.row_pointer[i] += 1

    def build(self):
        """Пересчитываем row_pointer, чтобы указатели на начало строк были верными"""
        for i in range(1, self.n + 1):
            self.row_pointer[i] += self.row_pointer[i - 1]

    def trace(self):
        """Подсчет следа матрицы"""
        trace_sum = 0

        # Находим все элементы в строке i, и если это диагональный элемент, добавляем его к следу
        for i in range(self.n):
            start = self.row_pointer[i]
            end = self.row_pointer[i + 1]
            for j in range(start, end):
                col = self.columns[j]
                if col == i:
                    trace_sum += self.values[j]

        return trace_sum

    def get(self, i, j):
        """Получение элемента по индексу (i, j)"""
        start = self.row_pointer[i - 1]
        end = self.row_pointer[i]
        for k in range(start, end):
            if self.columns[k] == j - 1:
                return int(self.values[k])
        return 0

    def __str__(self):
        """Вывод матрицы"""
        matrix_str = ""
        for i in range(self.n):
            row = [str(self.get(i + 1, j + 1)) for j in range(self.m)]
            matrix_str += " ".join(row) + "\n"
        return matrix_str

    def sum_matrix(self, other):
        """Сложение матриц"""
        if self.n != other.n or self.m != other.m:
            raise ValueError("Размеры матриц не совпадают")

        result = SparseMatrix(self.n, self.m)

        for i in range(self.n):
            start_s = self.row_pointer[i]
            end_s = self.row_pointer[i + 1]
            start_o = other.row_pointer[i]
            end_o = other.row_pointer[i + 1]

            # Указатели на текущие позиции в строках self и other
            ptr_s, ptr_o = start_s, start_o

            while ptr_s < end_s or ptr_o < end_o:
                if ptr_o >= end_o or (ptr_s < end_s and self.columns[ptr_s] < other.columns[ptr_o]):
                    # Добавляем элемент из self, так как он идет раньше
                    result.add(i + 1, self.columns[ptr_s] + 1, self.values[ptr_s])
                    ptr_s += 1
                elif ptr_s >= end_s or (ptr_o < end_o and other.columns[ptr_o] < self.columns[ptr_s]):
                    # Добавляем элемент из other, так как он идет раньше
                    result.add(i + 1, other.columns[ptr_o] + 1, other.values[ptr_o])
                    ptr_o += 1
                else:
                    # Суммируем элементы, так как их столбцы совпадают
                    summed_value = self.values[ptr_s] + other.values[ptr_o]
                    if summed_value != 0:
                        result.add(i + 1, self.columns[ptr_s] + 1, summed_value)
                    ptr_s += 1
                    ptr_o += 1

        result.build()
        return result

    def multiply_by_scalar(self, scalar):
        """Умножение матрицы на скаляр"""
        result = SparseMatrix(self.n, self.m)

        for i in range(self.n):
            start = self.row_pointer[i]
            end = self.row_pointer[i + 1]
            for j in range(start, end):
                result.add(i + 1, self.columns[j] + 1, self.values[j] * scalar)

        result.build()
        return result

    def multiply_matrix(self, other):
        """Умножение матриц"""
        if self.m != other.n:
            raise ValueError("Число столбцов первой матрицы должно быть равно числу строк второй.")

        result = SparseMatrix(self.n, other.m)

        # Транспонируем вторую матрицу для удобного доступа к её столбцам
        other_transposed = SparseMatrix(other.m, other.n)
        for i in range(other.n):
            start = other.row_pointer[i]
            end = other.row_pointer[i + 1]
            for j in range(start, end):
                other_transposed.add(other.columns[j] + 1, i + 1, other.values[j])
        other_transposed.build()

        # Умножение
        for i in range(self.n):
            start_s = self.row_pointer[i]
            end_s = self.row_pointer[i + 1]
            if start_s == end_s:
                continue  # Пропускаем пустые строки

            for j in range(other_transposed.n):
                start_t = other_transposed.row_pointer[j]
                end_t = other_transposed.row_pointer[j + 1]
                if start_t == end_t:
                    continue  # Пропускаем пустые столбцы

                # Скалярное произведение строки из self и столбца из other
                dot_product = 0
                ptr_s, ptr_t = start_s, start_t
                while ptr_s < end_s and ptr_t < end_t:
                    col_s = self.columns[ptr_s]
                    col_t = other_transposed.columns[ptr_t]
                    if col_s < col_t:
                        ptr_s += 1
                    elif col_s > col_t:
                        ptr_t += 1
                    else:
                        dot_product += self.values[ptr_s] * other_transposed.values[ptr_t]
                        ptr_s += 1
                        ptr_t += 1

                if dot_product != 0:
                    result.add(i + 1, j + 1, dot_product)

        result.build()
        return result

    def determinant(self):
        """Вычисления детерминанта матрицы"""
        size = self.n

        # Базовый случай для матрицы 1x1
        if size == 1:
            return self.get(1, 1)

        # Базовый случай для матрицы 2x2
        if size == 2:
            a11 = self.get(1, 1)
            a12 = self.get(1, 2)
            a21 = self.get(2, 1)
            a22 = self.get(2, 2)
            return a11 * a22 - a12 * a21

        # Рекурсивное вычисление для матриц размерности n > 2
        det = 0
        for col in range(size):
            cofactor = ((-1) ** col) * self.get(1, col + 1) * self.get_minor(0, col).determinant()
            det += cofactor

        return det

    def get_minor(self, row_to_exclude, col_to_exclude):
        """Возвращает минор матрицы, исключая строку и столбец"""
        minor = SparseMatrix(self.n - 1, self.m - 1)

        for i in range(self.n):
            if i == row_to_exclude:
                continue  # Пропускаем строку, которую исключаем
            for j in range(self.m):
                if j == col_to_exclude:
                    continue  # Пропускаем столбец, который исключаем
                minor.add(i + 1 if i < row_to_exclude else i, j + 1 if j < col_to_exclude else j,
                          self.get(i + 1, j + 1))

        minor.build()
        return minor

    def is_invertible(self):
        """Проверка, существует ли обратная матрица"""
        if self.determinant() != 0:
            return "Да"
        else:
            return "Нет"