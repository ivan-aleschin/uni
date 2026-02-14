#include <vector>
#include <iostream>
#include <windows.h>
#include <string>

using namespace std;

struct Lesson;
struct Student;

struct Student {
    string name{""};
    int course{0};
    string group{""};
    vector<Lesson*> lessons;
    void add(Lesson* lesson);
    void print();

    ~Student() {
        //cout << "Студент " << name << " удален!" << endl;
    }
};

struct Lesson {
    string name{""}, time{""}, lecturer{""};
    vector<Student*> students;
    void print();

    ~Lesson() {
        //cout << "Пара " << name << " удален!" << endl;
    }
};

void Student::print() {
    cout << "Имя: " << name << endl;
    cout << "Курс: " << course << endl;
    cout << "Группа: " << group << endl;
    cout << "Пары, на которые ходит этот студент: " ;
    for (int i = 0; i < lessons.size(); ++i) {
        cout << i + 1 << ") " << lessons[i]->name << " ";
    }
}
void Lesson::print() {
    cout << "Имя: " << name << endl;
    cout << "Время: " << time << endl;
    cout << "Лектор: " << lecturer << endl;
    cout << "Студенты, которые ходят на этот предмет: " ;
    for (int i = 0; i < students.size(); ++i) {
        cout <<  i + 1 << ") " << students[i]->name << " ";
    }
    cout << "\n";
}

void Student::add(Lesson* lesson) {
    lessons.push_back(lesson);
    lesson->students.push_back(this);
}

int main()
{
    SetConsoleOutputCP(CP_UTF8);

    int tmp{0};
    Lesson matan, analMech, physics;
    Student petya, vanya, sasha;

    matan = {"Matan", "10:45-12:10", "Redkozubova"};
    analMech = {"Anal.Mech", "12:20-13:45", "Municina"};
    physics = {"Physics", "13:55-15:20", "Gavrikov"};
    petya = {"Petya", 3, "B02-911"};
    vanya = {"Vanya", 2, "B04-006"};
    sasha = {"Sasha", 1, "B05-011"};
    vanya.add(&matan);
    vanya.add(&analMech);
    petya.add(&matan);
    petya.add(&analMech);
    petya.add(&physics);
    sasha.add(&matan);
    sasha.add(&physics);

    vector<Student> students{petya, vanya, sasha};
    vector<Lesson> lessons{matan, analMech, physics};

    cout << "Выберите, о чём или о ком информацию вы хотите получить: " << endl;
    cout << "Студент - нажмите 1; Пара - нажмите 2: " << endl;
    cin >> tmp;
    switch (tmp) {
        case 1:
            for(int i = 0; i <students.size(); i++){
                cout << i + 1 << ") " << students[i].name << " ";
            }
            cout << "\n";
            cout << "Выберите студента из предложенных(Цифрами 1-3): " << endl;
            cin >> tmp;
            switch (tmp) {
                case 1:
                    petya.print();
                    break;
                case 2:
                    vanya.print();
                    break;
                case 3:
                    sasha.print();
                    break;
            }
            break;
        case 2:
            for(int i = 0; i <lessons.size(); i++){
                cout << i + 1 << ") " << lessons[i].name << " ";
            }
            cout << "\n";
            cout << "Выберите предмет из предложенных(Цифрами 1-3): " << endl;
            cin >> tmp;
            switch (tmp) {
                case 1:
                    matan.print();
                    break;
                case 2:
                    analMech.print();
                    break;
                case 3:
                    physics.print();
                    break;
            }
            break;
    }

    return 0;
}
