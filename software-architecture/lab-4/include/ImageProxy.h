#pragma once
#include "IGraphic.h"
#include "RealImage.h"
#include <QString>
#include <memory>

class ImageProxy : public IGraphic {
private:
    std::unique_ptr<RealImage> realImage;
    QString filename;
    int x, y;
    int width, height;

public:
    ImageProxy(const QString& filename, int x, int y, int width, int height);
    ~ImageProxy() override = default;

    void draw(QPainter* painter) override;
    void move(int dx, int dy) override;
    void doubleRightClick() override;
    QRect getBounds() const override;
};