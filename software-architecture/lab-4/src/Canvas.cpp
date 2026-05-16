#include "Canvas.h"

#include <QMouseEvent>
#include <QPainter>
#include <QPalette>

Canvas::Canvas(QWidget* parent) : QWidget(parent) {
    setMinimumSize(900, 600);
    setAutoFillBackground(true);
    QPalette pal = palette();
    pal.setColor(QPalette::Window, Qt::white);
    setPalette(pal);
}

void Canvas::addImage(std::shared_ptr<Image> image) {
    images_.push_back(std::move(image));
    update();
}

void Canvas::paintEvent(QPaintEvent*) {
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);
    for (auto& image : images_) {
        image->draw(&painter);
    }
}

void Canvas::mousePressEvent(QMouseEvent* event) {
    if (event->button() != Qt::LeftButton) {
        return;
    }
    dragged_ = hitTest(event->pos());
    lastPos_ = event->pos();
}

void Canvas::mouseMoveEvent(QMouseEvent* event) {
    if (!dragged_ || !(event->buttons() & Qt::LeftButton)) {
        return;
    }
    QPoint delta = event->pos() - lastPos_;
    lastPos_ = event->pos();
    dragged_->move(delta.x(), delta.y());
    update();
}

void Canvas::mouseReleaseEvent(QMouseEvent* event) {
    if (event->button() == Qt::LeftButton) {
        dragged_.reset();
    }
}

void Canvas::mouseDoubleClickEvent(QMouseEvent* event) {
    if (event->button() != Qt::RightButton) {
        return;
    }
    auto target = hitTest(event->pos());
    if (target) {
        target->load();
        update();
    }
}

std::shared_ptr<Image> Canvas::hitTest(const QPoint& pos) const {
    for (auto it = images_.rbegin(); it != images_.rend(); ++it) {
        if ((*it)->bounds().contains(pos)) {
            return *it;
        }
    }
    return nullptr;
}
