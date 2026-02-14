#include <iostream>
#include <cmath>

class Figure {
public:
    virtual double calc_square() const = 0;
    virtual double calc_perimeter() const = 0;
};

class Triangle: public Figure {
private:
    double a, b, c;
public:
    double calc_square() const {
        double p = a + b + c;
        return sqrt(p * (p - a) * (p - b) * (p - c));
    }

    double calc_perimeter() const {
        return (a + b + c);
    }

    Triangle(double side_a, double side_b, double side_c) : a(side_a), b(side_b), c(side_c) {}
};

class Ellipse: public Figure {
private:
    double a, b;
public:
    double calc_square() const {
        return (M_PI * a * b);
    }

    double calc_perimeter() const {
        return (4 * (M_PI*a*b + (a - b)*(a - b))/(a + b));
    }

    Ellipse(double side_a, double side_b) : a(side_a), b(side_b) {}
};

class Circle: public Ellipse {
private:
    double r;
public:
    Circle(double radius) : Ellipse(radius, radius) {}
};

class Rectangle: public Figure {
private:
    double a, b;
public:
    double calc_square() const {
        return (a * b);
    }

    double calc_perimeter() const {
        return (2 * (a + b));
    }

    Rectangle(double side_a, double side_b) : a(side_a), b(side_b) {}
};

class Square: public Rectangle {
public:
    Square(double side_a) : Rectangle(side_a, side_a) {}
};

int main() {
    Figure** figure = new Figure*[5];
    std::cout << "Output of the program:\n";
    std::cout << "\nFigure #1 (Triangle):";
    figure[0] = new Triangle(3, 4, 5); //Создаем фигуру
    std::cout << "\nSquare: ";
    std::cout << (figure[0]->calc_square()); //Вычисляем площадь
    std::cout << "\nPerimeter: ";
    std::cout << (figure[0]->calc_perimeter()); //Вычисляем периметр

    std::cout << "\n\nFigure #2 (Ellipse):";
    figure[1] = new Ellipse(4, 5);
    std::cout << "\nSquare: ";
    std::cout << (figure[1]->calc_square());
    std::cout << "\nPerimeter: ";
    std::cout << (figure[1]->calc_perimeter());

    std::cout << "\n\nFigure #3 (Circle):";
    figure[2] = new Circle(5);
    std::cout << "\nSquare: ";
    std::cout << (figure[2]->calc_square());
    std::cout << "\nPerimeter: ";
    std::cout << (figure[2]->calc_perimeter());

    std::cout << "\n\nFigure #4 (Rectangle):";
    figure[3] = new Rectangle(4, 5);
    std::cout << "\nSquare: ";
    std::cout << (figure[3]->calc_square());
    std::cout << "\nPerimeter: ";
    std::cout << (figure[3]->calc_perimeter());

    std::cout << "\n\nFigure #5 (Square):";
    figure[4] = new Square(5);
    std::cout << "\nSquare: ";
    std::cout << (figure[4]->calc_square());
    std::cout << "\nPerimeter: ";
    std::cout << (figure[4]->calc_perimeter());

    delete figure[0];
    delete figure[1];
    delete figure[2];
    delete figure[3];
    delete figure[4];
    delete [] figure;

    return 0;
}