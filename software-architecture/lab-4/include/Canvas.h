#pragma once

#include "Image.h"

#include <QPoint>
#include <QWidget>

#include <memory>
#include <vector>

class QMouseEvent;
class QPaintEvent;

// Client — холст графического редактора. Работает с изображениями
// исключительно через интерфейс Subject (Image): рисует, перетаскивает
// ЛКМ, по двойному ПКМ вызывает load() и не различает заместителя
// и реальный объект.
class Canvas : public QWidget {
    Q_OBJECT
public:
    explicit Canvas(QWidget* parent = nullptr);

    void addImage(std::shared_ptr<Image> image);

protected:
    void paintEvent(QPaintEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void mouseDoubleClickEvent(QMouseEvent* event) override;

private:
    std::shared_ptr<Image> hitTest(const QPoint& pos) const;

    std::vector<std::shared_ptr<Image>> images_;
    std::shared_ptr<Image> dragged_;
    QPoint lastPos_;
};
