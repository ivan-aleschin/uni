#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QDir>
#include <QCoreApplication>
#include <memory>

#include "../include/CanvasWidget.h"
#include "../include/ImageProxy.h"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);

    QMainWindow mainWindow;
    mainWindow.setWindowTitle("Лабораторная работа №4: Паттерн Proxy (Qt6)");
    mainWindow.resize(1100, 800);

    QWidget *centralWidget = new QWidget(&mainWindow);
    QVBoxLayout *layout = new QVBoxLayout(centralWidget);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(0);

    QLabel *hintLabel = new QLabel(
        "<b>Инструкция:</b><br>"
        "1. <b>ЛКМ (удерживать)</b>: Свободное перемещение бокса (Proxy).<br>"
        "2. <b>Двойной ПКМ</b>: Загрузка реального изображения в выбранный бокс.<br>"
        "3. <b>Space/Enter</b> или кнопка <b>Load selected image</b>: резервный способ для тачпада."
    );
    hintLabel->setStyleSheet(
        "background-color: #f0f0f0; "
        "padding: 10px; "
        "border-bottom: 1px solid #ccc; "
        "font-size: 14px;"
    );
    hintLabel->setWordWrap(true);
    layout->addWidget(hintLabel);

    // Панель управления
    QWidget *controls = new QWidget(centralWidget);
    QHBoxLayout *controlsLayout = new QHBoxLayout(controls);
    controlsLayout->setContentsMargins(10, 6, 10, 6);
    controlsLayout->setSpacing(10);

    QLabel *selectHint = new QLabel("Выделите бокс ЛКМ перед загрузкой.");
    QPushButton *loadButton = new QPushButton("Load selected image");

    controlsLayout->addWidget(selectHint);
    controlsLayout->addStretch(1);
    controlsLayout->addWidget(loadButton);

    layout->addWidget(controls);

    // Холст редактора
    CanvasWidget *canvas = new CanvasWidget(centralWidget);
    layout->addWidget(canvas, 1);

    mainWindow.setCentralWidget(centralWidget);

    // Создаем прокси-объекты (файлы лежат в assets рядом с проектом)
    QDir appDir(QCoreApplication::applicationDirPath());
    QString testImagePath = appDir.filePath("../assets/TestImage.xpm");
    QString natureImagePath = appDir.filePath("../assets/Nature.xpm");

    auto image1 = std::make_shared<ImageProxy>(testImagePath, 50, 50, 400, 300);
    auto image2 = std::make_shared<ImageProxy>(natureImagePath, 520, 150, 360, 260);

    canvas->addGraphic(image1);
    canvas->addGraphic(image2);

    QObject::connect(loadButton, &QPushButton::clicked, [canvas]() {
        canvas->loadSelected();
    });

    mainWindow.show();
    return app.exec();
}