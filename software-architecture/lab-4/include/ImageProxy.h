#pragma once

#include "Image.h"

#include <QString>
#include <memory>

class RealImage;

// Proxy — заместитель. Знает размеры реального изображения (читает
// метаданные файла через QImageReader, без загрузки пикселей) и
// перемещает «бокс» по холсту. Реальный объект создаётся только
// при вызове load() — в нашей задаче это двойной щелчок ПКМ.
class ImageProxy : public Image {
public:
    ImageProxy(const QString& filename, int x, int y);
    ~ImageProxy() override;

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
    std::unique_ptr<RealImage> real_;
};
