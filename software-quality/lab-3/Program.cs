// ЛР3, метрика Чепина. Вариант 1, задача 21:
// создать матрицу N x M, заполнить её случайными нулями и единицами,
// проверить, в каких столбцах нули и единицы строго чередуются,
// вывести матрицу и номера таких столбцов. N и M вводятся с клавиатуры.
//
// Комментарии в анализ не входят: листинг в README.md приведён без них,
// номера строк в таблице переменных относятся к нему.
using System;
class Program
{
    static void Main()
    {
        int n, m, i, j;
        int[,] a;
        bool alternate, found;
        Random rnd = new Random();
        Console.Write("Число строк N: ");
        n = int.Parse(Console.ReadLine());
        Console.Write("Число столбцов M: ");
        m = int.Parse(Console.ReadLine());
        a = new int[n, m];
        // Заполняем матрицу и сразу печатаем её построчно.
        // Next(0, 2) возвращает 0 или 1: верхняя граница не включается.
        for (i = 0; i < n; i++)
        {
            for (j = 0; j < m; j++)
            {
                a[i, j] = rnd.Next(0, 2);
                Console.Write("{0,3}", a[i, j]);
            }
            Console.WriteLine();
        }
        // Столбец «чередуется», если никакие два соседних элемента в нём
        // не равны. Как только нашли пару одинаковых соседей, дальше
        // этот столбец можно не смотреть — поэтому alternate стоит
        // в условии внутреннего цикла.
        found = false;
        Console.Write("Столбцы с чередованием:");
        for (j = 0; j < m; j++)
        {
            alternate = true;
            for (i = 1; i < n && alternate; i++)
                if (a[i, j] == a[i - 1, j])
                    alternate = false;
            if (alternate)
            {
                // Столбцы нумеруем с единицы, как принято в условии задачи.
                Console.Write(" " + (j + 1));
                found = true;
            }
        }
        if (!found)
            Console.Write(" таких нет");
        Console.WriteLine();
    }
}
