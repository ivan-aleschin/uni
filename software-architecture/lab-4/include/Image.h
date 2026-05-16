#pragma once

#include <QRect>

class QPainter;

// Subject — общий интерфейс для RealImage и ImageProxy.
// Клиент работает только с этим интерфейсом и не различает заместителя
// и реальный объект.
class Image {
public:
    virtual ~Image() = default;

    virtual void draw(QPainter* painter) = 0;
    virtual void move(int dx, int dy) = 0;
    virtual void load() = 0;
    virtual QRect bounds() const = 0;
};
