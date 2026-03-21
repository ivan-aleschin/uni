#pragma once

#include <QWidget>
#include <QMouseEvent>
#include <QPaintEvent>
#include <QPoint>
#include <QRect>
#include <QPointF>
#include <vector>
#include <memory>

#include "IGraphic.h"

class CanvasWidget : public QWidget {
    Q_OBJECT

public:
    explicit CanvasWidget(QWidget* parent = nullptr);
    ~CanvasWidget() override = default;

    // Добавление графического объекта (например, ImageProxy) на холст
    void addGraphic(std::shared_ptr<IGraphic> graphic);

    // Загрузить реальное изображение для выбранного объекта
    void loadSelected();

protected:
    // Отрисовка всех объектов
    void paintEvent(QPaintEvent* event) override;

    // Базовые события мыши (работают и для тачпада, и для мыши на большинстве платформ)
    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void mouseDoubleClickEvent(QMouseEvent* event) override;

    // Нормализованный drag & drop (полезно для разных backend'ов/оконных систем)
    void dragEnterEvent(QDragEnterEvent* event) override;
    void dragMoveEvent(QDragMoveEvent* event) override;
    void dropEvent(QDropEvent* event) override;

    // Обработка потери фокуса/ухода курсора для корректного завершения перетаскивания
    void leaveEvent(QEvent* event) override;
    bool event(QEvent* event) override;

private:
    std::vector<std::shared_ptr<IGraphic>> graphics;
    std::shared_ptr<IGraphic> selectedGraphic;

    // Состояние перетаскивания
    bool isDragging = false;
    QPoint lastMousePos;
    QPointF lastMousePosF;

    // Конфигурация UX
    int dragThresholdPx = 2; // минимальное смещение для старта drag

    // Вспомогательные методы
    std::shared_ptr<IGraphic> hitTest(const QPoint& pos) const;
    std::shared_ptr<IGraphic> hitTest(const QPointF& pos) const;

    void beginDrag(const QPointF& pos);
    void updateDrag(const QPointF& pos);
    void endDrag();

    // Унификация «правого двойного клика» для мыши/тачпада
    bool isRightLikeButton(Qt::MouseButton button) const;
    bool isRightLikeButtons(Qt::MouseButtons buttons) const;
};