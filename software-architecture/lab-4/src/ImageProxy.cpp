#include "../include/ImageProxy.h"
#include <QDebug>
#include <QPainter>

ImageProxy::ImageProxy(const QString& filename, int x, int y, int width, int height)
    : filename(filename), x(x), y(y), width(width), height(height) {
    qDebug() << "[Proxy] Создан заместитель (суррогат) для изображения:" << filename;
}

void ImageProxy::draw(QPainter* painter) {
    if (realImage) {
        realImage->draw(painter);
    } else if (painter) {
        painter->save();
        
        // Рисуем рамку (бокс)
        QPen pen(Qt::DashLine);
        pen.setColor(Qt::darkGray);
        pen.setWidth(2);
        painter->setPen(pen);
        painter->drawRect(x, y, width, height);
        
        // Рисуем текст внутри бокса
        painter->setPen(Qt::black);
        painter->drawText(QRect(x, y, width, height), Qt::AlignCenter, 
                          "Placeholder\n[Double Right-Click to Load]\n" + filename);
                          
        painter->restore();
    }
}

void ImageProxy::move(int dx, int dy) {
    if (realImage) {
        realImage->move(dx, dy);
    } else {
        x += dx;
        y += dy;
        qDebug() << "[Proxy] Перемещение ПУСТОГО БОКСА для" << filename << "на новые координаты:" << x << "," << y;
    }
}

void ImageProxy::doubleRightClick() {
    if (!realImage) {
        qDebug() << "[Proxy] Двойной клик правой кнопкой мыши! Загрузка реального изображения с диска...";
        realImage = std::make_unique<RealImage>(filename, x, y, width, height);
    } else {
        realImage->doubleRightClick();
    }
}

QRect ImageProxy::getBounds() const {
    if (realImage) {
        return realImage->getBounds();
    }
    return QRect(x, y, width, height);
}