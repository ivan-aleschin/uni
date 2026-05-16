#pragma once

#include "Image.h"

#include <QImage>
#include <QString>

// RealSubject — реальный объект. Загружает пиксели изображения с диска
// (дорогая операция) и рисует их на холсте.
class RealImage : public Image {
public:
    RealImage(const QString& filename, int x, int y, int width, int height);

    void draw(QPainter* painter) override;
    void move(int dx, int dy) override;
    void load() override;
    QRect bounds() const override;

private:
    QString filename_;
    int x_;
    int y_;
    int width_;
    int height_;
    QImage image_;
};
