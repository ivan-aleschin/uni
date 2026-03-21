#pragma once
#include "IGraphic.h"
#include <QString>
#include <QImage>

class RealImage : public IGraphic {
private:
    QString filename;
    int x, y;
    int width, height;
    QImage image;

public:
    RealImage(const QString& filename, int x, int y, int width, int height);
    ~RealImage() override = default;

    void draw(QPainter* painter) override;
    void move(int dx, int dy) override;
    void doubleRightClick() override;
    QRect getBounds() const override;
};