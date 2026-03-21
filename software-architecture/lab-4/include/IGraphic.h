#pragma once

#include <QPainter>
#include <QRect>

class IGraphic {
public:
    virtual ~IGraphic() = default;

    // Отрисовка графического объекта (бокса или реального изображения)
    virtual void draw(QPainter* painter) = 0;

    // Перемещение графического объекта
    virtual void move(int dx, int dy) = 0;

    // Обработка двойного клика (загрузка реального изображения)
    virtual void doubleRightClick() = 0;

    // Получение границ объекта для проверки клика мыши
    virtual QRect getBounds() const = 0;
};