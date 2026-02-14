#include <string>
#include <vector>
#include <iostream>
#include <windows.h>
#include <cctype>
using namespace std;

int main() {
    SetConsoleOutputCP(CP_UTF8);
    setlocale(LC_ALL,"rus");
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);

    string text, tmp; //tmp - временное хранения символов для составления слов
    tmp = "";
    cout << "Enter the text using the Russian or English layout: "<< endl;
    getline(cin, text);
    vector <string> arr;

    for (int i = 0; i != text.size(); ++i){
        if (text[i] == ' ') { // Ищем пробелы
            if (tmp != "") {
                arr.push_back(tmp);
                tmp = "";
            }
        } else if (isalnum(text[i])){ //Добавляем буквы, если сивол буква
            tmp += text[i];
        } else if ((text[i] == '-') && isalnum(text[i+1])){ //Символ дефиз оставляем вместе со всем словом
            tmp += text[i];
            continue;
        } else {
            if (tmp != "") { // Вводим симвл, если не пусто
                arr.push_back(tmp);
                tmp = "";
            }
            tmp += text[i];
            arr.push_back(tmp);
            tmp = "";
        }
    }

    for (auto const &element: arr){ //Вывод
        cout << element << " ";
    }

    return 0;
}