// Массивы без ошибок: объявление, инициализация, обращение к ячейкам, присваивание.
// флаги: --arrays
// ожидается: panic=0 phrase=0
int main() {
    int a[3];
    int b[5] = {1, 2, 3};
    int c[] = {4, 5};
    int n = 2;
    a[0] = 7;
    a[n] = b[1];
    int x = c[1];
    for (int i = 0; i < n;) {
        if (a[i] == b[i]) return 0;
        c[0] = i;
    }
    if (1 < a[2]) return 1;
    return 2;
}
