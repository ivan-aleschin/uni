#include "../include/CanvasWidget.h"

#include <QPainter>
#include <QPen>
#include <QColor>
#include <QDragEnterEvent>
#include <QDragMoveEvent>
#include <QDropEvent>
#include <QKeyEvent>
#include <QEvent>
#include <QPalette>
#include <QDebug>

CanvasWidget::CanvasWidget(QWidget* parent)
    : QWidget(parent) {
    setMinimumSize(800, 600);

    // Белый фон
    setAutoFillBackground(true);
    QPalette pal = palette();
    pal.setColor(QPalette::Window, Qt::white);
    setPalette(pal);

    // Удобство для тачпада/мыши
    setMouseTracking(true);
    setFocusPolicy(Qt::StrongFocus);
    setAcceptDrops(true);
}

void CanvasWidget::addGraphic(std::shared_ptr<IGraphic> graphic) {
    graphics.push_back(graphic);
    update();
}

void CanvasWidget::loadSelected() {
    if (!selectedGraphic) return;
    selectedGraphic->doubleRightClick();
    update();
}

void CanvasWidget::paintEvent(QPaintEvent* event) {
    Q_UNUSED(event);
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing);

    for (const auto& graphic : graphics) {
        graphic->draw(&painter);
    }

    // Подсветка выбранного бокса
    if (selectedGraphic) {
        QRect r = selectedGraphic->getBounds();
        QPen pen(QColor(33, 150, 243));
        pen.setWidth(2);
        pen.setStyle(Qt::DashLine);
        painter.setPen(pen);
        painter.setBrush(QColor(33, 150, 243, 30));
        painter.drawRect(r);
    }
}

void CanvasWidget::mousePressEvent(QMouseEvent* event) {
    setFocus();

    // Сбрасываем текущее выделение перед новым выбором
    selectedGraphic = nullptr;
    isDragging = false;

    // Выделяем объект по месту клика
    selectedGraphic = hitTest(event->pos());
    if (selectedGraphic) {
        lastMousePos = event->pos();
        lastMousePosF = event->position();
    }
}

void CanvasWidget::mouseMoveEvent(QMouseEvent* event) {
    if (selectedGraphic && (event->buttons() & Qt::LeftButton)) {
        updateDrag(event->position());
    }
}

void CanvasWidget::mouseReleaseEvent(QMouseEvent* event) {
    if (event->button() == Qt::LeftButton) {
        endDrag();
    }
}

void CanvasWidget::mouseDoubleClickEvent(QMouseEvent* event) {
    if (isRightLikeButton(event->button())) {
        auto target = hitTest(event->pos());
        if (target) {
            selectedGraphic = target;
            selectedGraphic->doubleRightClick();
            update();
        }
    }
}

void CanvasWidget::dragEnterEvent(QDragEnterEvent* event) {
    // В этой лабораторной работе drag&drop не используется,
    // но метод обязателен для стабильной работы событий ввода.
    event->ignore();
}

void CanvasWidget::dragMoveEvent(QDragMoveEvent* event) {
    event->ignore();
}

void CanvasWidget::dropEvent(QDropEvent* event) {
    event->ignore();
}

void CanvasWidget::leaveEvent(QEvent* event) {
    Q_UNUSED(event);
    endDrag();
}

bool CanvasWidget::event(QEvent* event) {
    // Универсальная поддержка клавиатуры: Space/Enter загружают изображение
    if (event->type() == QEvent::KeyPress) {
        auto* ke = static_cast<QKeyEvent*>(event);
        if (ke->key() == Qt::Key_Space || ke->key() == Qt::Key_Return || ke->key() == Qt::Key_Enter) {
            if (selectedGraphic) {
                loadSelected();
                return true;
            }
        }
    }
    return QWidget::event(event);
}

std::shared_ptr<IGraphic> CanvasWidget::hitTest(const QPoint& pos) const {
    for (auto it = graphics.rbegin(); it != graphics.rend(); ++it) {
        if ((*it)->getBounds().contains(pos)) {
            return *it;
        }
    }
    return nullptr;
}

std::shared_ptr<IGraphic> CanvasWidget::hitTest(const QPointF& pos) const {
    return hitTest(pos.toPoint());
}

void CanvasWidget::beginDrag(const QPointF& pos) {
    if (!selectedGraphic) return;
    isDragging = true;
    lastMousePosF = pos;
}

void CanvasWidget::updateDrag(const QPointF& pos) {
    if (!selectedGraphic) return;

    QPointF delta = pos - lastMousePosF;
    if (!isDragging) {
        if (delta.manhattanLength() < dragThresholdPx) {
            return;
        }
        isDragging = true;
    }

    selectedGraphic->move(static_cast<int>(delta.x()), static_cast<int>(delta.y()));
    lastMousePosF = pos;
    update();
}

void CanvasWidget::endDrag() {
    isDragging = false;
}

bool CanvasWidget::isRightLikeButton(Qt::MouseButton button) const {
    return button == Qt::RightButton;
}

bool CanvasWidget::isRightLikeButtons(Qt::MouseButtons buttons) const {
    return buttons & Qt::RightButton;
}