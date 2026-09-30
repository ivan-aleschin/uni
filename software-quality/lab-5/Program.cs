// ЛР5, процедурно-ориентированные метрики. Вариант 1, задача 16:
// выяснить, сколько простых чисел находится в интервале [n, m], и вывести
// их на экран. Для определения, является ли очередное число простым,
// составить функцию.
//
// Комментарии в расчёт не входят: в README.md листинг приведён без них,
// и номера строк во всех таблицах относятся именно к тому листингу.
using System;
class Program
{
    // Функция из условия: true, если x простое.
    // Простое — натуральное число больше 1, у которого нет делителей,
    // кроме 1 и самого себя. Поэтому всё, что меньше 2 (включая 0 и
    // отрицательные числа), сразу не простое.
    public static bool isPrime(int x)
    {
        int d;
        if (x < 2)
            return false;
        // Делители достаточно искать до корня из x: если x = a * b и a > корня,
        // то b < корня и нашёлся бы раньше. Условие записано как d <= x / d,
        // а не d * d <= x, чтобы d * d не переполнило int на больших x.
        for (d = 2; d <= x / d; d++)
            if (x % d == 0)
                return false;
        return true;
    }
    public static void Main()
    {
        int n, m, i, count;
        char rep;
        do
        {
            Console.Write("n = ");
            n = int.Parse(Console.ReadLine());
            Console.Write("m = ");
            m = int.Parse(Console.ReadLine());
            Console.WriteLine("Простые числа из интервала [{0}, {1}]:", n, m);
            // Перебираем все числа интервала и про каждое спрашиваем функцию.
            // Если n > m, цикл не выполнится ни разу и count останется 0.
            for (i = n, count = 0; i <= m; i++)
                if (isPrime(i))
                {
                    Console.Write("{0} ", i);
                    count++;
                }
            Console.WriteLine();
            Console.WriteLine("Количество простых чисел: {0}", count);
            Console.Write("\nДля повтора нажмите клавишу Y: ");
            rep = char.Parse(Console.ReadLine());
            Console.WriteLine();
        } while (rep == 'Y' || rep == 'y');
    }
}
