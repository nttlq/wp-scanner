import random
import math
from itertools import combinations
import time
import os
import csv

from colorama import Fore, Back, Style


class FileManager:
    def __init__(self, folder_name):

        self.__folder_path = self.set_folder(folder_name)
        self.__create_folder()
        # self.create_file("gcd.txt")

    def set_folder(self, name: str):
        folder_path = f"labs/public/{name}"
        return folder_path

    @property
    def folder_path(self):
        return self.__folder_path

    def __create_folder(self):
        # print(self.folder_path)
        try:
            os.mkdir(self.folder_path)
        except TypeError:
            raise NotADirectoryError("Invalid path")
        except FileExistsError:
            pass
            # print("Folder already exists")

        return True

    def create_file(self, file_name):
        file_path = f"{self.folder_path}/{file_name}"
        with open(file_path, "w") as file:
            file.write("")
        return True

    def save_file(self, file_name, file_content):
        file_path = f"{self.folder_path}/{file_name}"
        with open(file_path, "w") as file:
            file.write(file_content)
        return True

    def save_to_csv(self, file_name, file_content):
        file_path = f"{self.folder_path}/{file_name}"
        with open(file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["Number a", "Number b", "Result", "Iterations", "Execution time"]
            )
            writer.writerow(
                [
                    file_content["a"],
                    file_content["b"],
                    file_content["Result"],
                    file_content["Iterations"],
                    file_content["Execution Time"],
                ]
            )


def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(
            Fore.BLUE + f"Execution time of {func.__name__}: {execution_time} seconds",
            Style.RESET_ALL,
        )
        return result, execution_time

    return wrapper


class Factorization:
    @staticmethod
    def fermat_factorization(n: int) -> tuple[int, int]:
        """Функция принимает число n и возвращает пару множителей этого числа. Внутри функции мы начинаем с x = sqrt(n) + 1 и увеличиваем x на 1, пока x^2 - n не станет полным квадратом. Как только это происходит, мы возвращаем пару (x - y, x + y), где y - это корень из x^2 - n."""

        assert n % 2 != 0  #  is based on the representation of an odd integer

        x: int = math.ceil(math.sqrt(n))

        count: int = 1
        while True:
            # print(Fore.BLUE + "x: ", x, Style.RESET_ALL)
            y_square: int = x**2 - n
            # print(Fore.RED + "y^2: ", y_square, Style.RESET_ALL)
            y: int | float = math.sqrt(y_square)
            # print("y: ", y)
            if y.is_integer():
                return (int(x - y), int(x + y)), count  # Возвращаем пару множителей
            x += 1
            count += 1

    @staticmethod
    def is_prime(n: int) -> bool:
        if n <= 1 or (n % 2 == 0 and n > 2):
            return False
        return all(n % i for i in range(3, int(n**0.5) + 1, 2))

    @staticmethod
    def quadratic_sieve_factorization(n: int, B: int, M: int) -> tuple[int, int]:
        """Basic implementation of the quadratic sieve method"""
        # Find the factor base, consisting of -1 and primes p such that (n|p) = 1
        factor_base = [-1]
        for p in range(2, B + 1):
            if (
                Factorization.is_prime(p)
                and math.gcd(p, n) == 1
                and pow(n, (p - 1) // 2, p) == 1
            ):
                factor_base.append(p)

        # Print the factor base
        # print("Factor base:", factor_base)

        # Find the smooth numbers in the interval [sqrt(n)+1, sqrt(n)+M] by sieving
        smooth_numbers = []
        smooth_vectors = []
        for x in range(int(math.sqrt(n)) + 1, int(math.sqrt(n)) + M + 1):
            y = x**2 - n  # y = x^2 - n
            vector = [0] * len(
                factor_base
            )  # vector of exponents of factor base elements
            for i, p in enumerate(factor_base):
                # print("i:", i, "p:", p, "y:", y, "vector:", vector)
                if p == -1 and y < 0:  # if p is -1 and y is negative
                    y = -y  # multiply y by -1
                    vector[i] = 1  # set the exponent of -1 to 1
                elif p != -1:  # if p is positive
                    while y % p == 0:  # while y is divisible by p
                        y = y // p  # divide y by p
                        vector[i] = (
                            vector[i] + 1
                        ) % 2  # increment the exponent of p modulo 2
            if y == 1:  # if y is fully factored by the factor base
                smooth_numbers.append(x)  # add x to the smooth numbers list
                smooth_vectors.append(vector)  # add vector to the smooth vectors list

        # Print the smooth numbers and vectors
        # print("Smooth numbers:", smooth_numbers)
        # print("Smooth vectors:", smooth_vectors)

        # Find a nontrivial linear combination of smooth vectors that gives the zero vector
        # using Gaussian elimination
        matrix = smooth_vectors  # copy the smooth vectors matrix
        used = [False] * len(smooth_numbers)  # mark which rows are used
        for k in range(len(factor_base)):  # for each column
            for r in range(len(smooth_numbers)):  # for each row
                if (
                    matrix[r][k] == 1 and not used[r]
                ):  # if the element is 1 and the row is not used
                    for i in range(len(smooth_numbers)):  # for each other row
                        if (
                            matrix[i][k] == 1 and r != i
                        ):  # if the element is 1 and the row is different
                            for j in range(len(factor_base)):  # for each column
                                matrix[i][j] = (
                                    matrix[i][j] + matrix[r][j]
                                ) % 2  # add the rows modulo 2
                    used[r] = True  # mark the row as used
                    break  # break the loop

        # Print the matrix after Gaussian elimination
        # print("Matrix after Gaussian elimination:")
        # for row in matrix:
        #    print(row)
        # Find a nontrivial solution by assigning free variables to 1
        # and finding the values of dependent variables
        for r in range(1, len(smooth_numbers) + 1):
            for combination in combinations(range(len(smooth_numbers)), r):
                solution = [0] * len(factor_base)  # initialize the solution vector
                for i in combination:
                    solution = [
                        (solution[j] + matrix[i][j]) % 2
                        for j in range(len(factor_base))
                    ]

                # Find the product of smooth numbers corresponding to the solution vector
                X = math.prod(smooth_numbers[i] for i in combination)

                # Find the product of factor base elements corresponding to the solution vector
                Y = math.prod(
                    factor_base[i] ** (solution[i] / 2) for i in range(len(factor_base))
                )

                # Find the greatest common divisor of X - Y and n
                d = math.gcd(int(X - Y), n)

                # Check if the divisor is nontrivial
                if 1 < d < n:
                    # print("Success: the divisor is nontrivial")
                    # print("Divisor:", d)
                    p = n // d
                    return (d, p)
                else:
                    continue
        else:
            return None

    @staticmethod
    def pollards_factorization(n: int):
        x = 2
        y = 2
        d = 1
        while d == 1:
            x = (x**2 + 1) % n
            y = (y**2 + 1) % n
            y = (y**2 + 1) % n
            d = math.gcd(abs(x - y), n)
        if d == n:
            return None
        else:
            return d, n // d


def main():
    while True:
        n: int = random.randint(10, 100000)
        # n = 187
        if not Factorization.is_prime(n):
            break

    while True:
        try:
            answ: tuple[int, int] = Factorization.fermat_factorization(n)
            break
        except AssertionError:
            while True:
                n: int = random.randint(10, 100000)
                if not Factorization.is_prime(n):
                    break

    print(Back.MAGENTA + "n: ", n, Style.RESET_ALL)
    print(Fore.GREEN + "fermat_factorization: ", Back.GREEN, answ, Style.RESET_ALL)
    print(
        Fore.BLUE + "Is prime p:",
        answ[0][0],
        Factorization.is_prime(answ[0][0]),
        Style.RESET_ALL,
    )
    print(
        Fore.BLUE + "Is prime q:",
        answ[0][1],
        Factorization.is_prime(answ[0][1]),
        Style.RESET_ALL,
    )

    # Define the factor base limit
    B = 80  # 29
    # Define the sieve interval size
    M = 350
    for _ in range(4):
        answ = Factorization.quadratic_sieve_factorization(n, B, M)
        if answ is None:
            B = random.randint(30, 100)
            M = random.randint(350, 550)
        else:
            break

    print(
        Fore.GREEN + "quadratic_sieve_factorization:",
        Back.GREEN,
        answ,
        Style.RESET_ALL,
    )


class Math:
    count = 0

    @staticmethod
    def gcd_recursion(x, y):
        while True:
            global count
            count += 1
            if y == 0:
                return x
            else:
                return Math.gcd_recursion(y, (x % y))

    @measure_time
    @staticmethod
    def gcd(a: int, b: int) -> int:
        count: int = 0
        while b != 0:
            a, b = b, a % b
            count = count + 1
        return a, count

    @staticmethod
    def factors(number: int) -> list:
        factors: list = []
        for i in range(1, abs(int(number)) + 1):
            if number % i == 0:
                factors.append(i)
        return factors


def start():
    file_manager = FileManager("gcd")
    print(Math.factors(91))
    a = 2342353232423523452623609934293912324214
    b = 243432
    (answ, count), execution_time = Math.gcd(a, b)
    result_csv = {
        "a": a,
        "b": b,
        "Result": answ,
        "Iterations": count,
        "Execution Time": execution_time,
    }
    result = f"GCD:\nNumber a: {a}\nNumber b: {b}\nResult: {answ}\nIterations: {count}\nExecution time: {execution_time}"
    file_manager.save_file(
        "gcd.txt",
        result,
    )
    file_manager.save_to_csv(
        "gcd.csv",
        result_csv,
    )
    answ2 = math.gcd(a, b)

    # answ3 = Math.gcd_recursion(a, b)
    print(Back.MAGENTA + "a:", a, "b:", b, Style.RESET_ALL)
    # print(Back.WHITE + "gcd_rec:", answ3, Style.RESET_ALL)
    print(Back.BLUE + "gcd:", answ, Style.RESET_ALL)
    print(Fore.BLUE + "count:", count, Style.RESET_ALL)
    print(Back.GREEN + "math.gcd:", answ2, Style.RESET_ALL)
    from egcd import egcd

    n = 1403
    a3, b3 = Factorization.pollards_factorization(n)
    print(
        Fore.LIGHTMAGENTA_EX + f"Pollards method\nn:{n}\na:{a3}\nb:{b3}",
        Style.RESET_ALL,
    )
    # print(egcd.egcd(15, 26))
    print(Fore.RED + "EGCD:", egcd(7, 11), Style.RESET_ALL)


if __name__ == "__main__":
    # main()
    start()
