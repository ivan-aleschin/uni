#include "../include/RealImage.h"
#include <QDebug>
#include <QPainter>

RealImage::RealImage(const QString& filename, int x, int y, int width, int height)
    : filename(filename), x(x), y(y), width(width), height(height) {
    qDebug() << "[RealImage] Загрузка изображения" << filename << "с диска в память...";
    
    // Пытаемся загрузить реальное изображение
    if (!image.load(filename)) {
        qWarning() << "[RealImage] Не удалось найти файл:" << filename << ". Создан плейсхолдер ошибки.";
        // Если картинки нет, создаем заглушку с текстом ошибки
        image = QImage(width, height, QImage::Format_RGB32);
        image.fill(Qt::darkGray);
        QPainter p(&image);
        p.setPen(Qt::white);
        p.drawText(image.rect(), Qt::AlignCenter, "Image Not Found\n" + filename);
    } else {
        // Масштабируем до требуемых размеров
        image = image.scaled(width, height, Qt::KeepAspectRatioByExpanding, Qt::SmoothTransformation);
    }
}

void RealImage::draw(QPainter* painter) {
    if (painter && !image.isNull()) {
        painter->drawImage(x, y, image);
    }
}

void RealImage::move(int dx, int dy) {
    x += dx;
    y += dy;
    qDebug() << "[RealImage] Перемещение реального изображения на новые координаты:" << x << "," << y;
}

void RealImage::doubleRightClick() {
    qDebug() << "[RealImage] Изображение" << filename << "уже загружено.";
}

QRect RealImage::getBounds() const {
    return QRect(x, y, width, height);
}