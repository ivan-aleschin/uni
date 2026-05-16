#include "RealImage.h"

#include <QPainter>

#include <iostream>

RealImage::RealImage(const QString& filename, int x, int y, int width, int height)
    : filename_(filename), x_(x), y_(y), width_(width), height_(height) {
    std::cerr << "[RealImage] Загрузка пикселей с диска: "
              << filename_.toStdString() << "\n";
    if (!image_.load(filename_)) {
        std::cerr << "[RealImage] Не удалось загрузить файл: "
                  << filename_.toStdString() << "\n";
        return;
    }
    image_ = image_.scaled(width_, height_, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
}

void RealImage::draw(QPainter* painter) {
    if (!image_.isNull()) {
        painter->drawImage(x_, y_, image_);
    }
}

void RealImage::move(int dx, int dy) {
    x_ += dx;
    y_ += dy;
}

void RealImage::load() {
    // Уже загружено в конструкторе. Метод присутствует для соответствия
    // интерфейсу Subject.
}

QRect RealImage::bounds() const {
    return QRect(x_, y_, width_, height_);
}
