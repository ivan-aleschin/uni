#include "ImageProxy.h"
#include "RealImage.h"

#include <QImageReader>
#include <QPainter>
#include <QPen>

#include <iostream>

ImageProxy::ImageProxy(const QString& filename, int x, int y)
    : filename_(filename), x_(x), y_(y) {
    // Читаем только метаданные файла, чтобы знать размеры реального
    // изображения, но не загружать сами пиксели.
    QImageReader reader(filename_);
    QSize size = reader.size();
    if (!size.isValid()) {
        std::cerr << "[ImageProxy] Не удалось прочитать размеры файла "
                  << filename_.toStdString() << ", использую 400x300\n";
        size = QSize(400, 300);
    }
    width_ = size.width();
    height_ = size.height();
    std::cerr << "[ImageProxy] Создан заместитель " << width_ << "x" << height_
              << " для " << filename_.toStdString() << "\n";
}

ImageProxy::~ImageProxy() = default;

void ImageProxy::draw(QPainter* painter) {
    if (real_) {
        real_->draw(painter);
        return;
    }
    painter->save();
    QPen pen(Qt::darkGray);
    pen.setWidth(2);
    pen.setStyle(Qt::DashLine);
    painter->setPen(pen);
    painter->setBrush(Qt::NoBrush);
    painter->drawRect(x_, y_, width_, height_);
    painter->setPen(Qt::black);
    painter->drawText(QRect(x_, y_, width_, height_), Qt::AlignCenter,
                      filename_ + QString("\n%1×%2\n(двойной ПКМ — загрузить)")
                                      .arg(width_).arg(height_));
    painter->restore();
}

void ImageProxy::move(int dx, int dy) {
    x_ += dx;
    y_ += dy;
    if (real_) {
        real_->move(dx, dy);
    }
}

void ImageProxy::load() {
    if (real_) {
        return;
    }
    std::cerr << "[ImageProxy] Двойной ПКМ — создаю RealImage\n";
    real_ = std::make_unique<RealImage>(filename_, x_, y_, width_, height_);
}

QRect ImageProxy::bounds() const {
    return QRect(x_, y_, width_, height_);
}
