#include "Canvas.h"
#include "ImageProxy.h"

#include <QApplication>
#include <QCoreApplication>
#include <QDir>
#include <QMainWindow>

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);

    QMainWindow window;
    window.setWindowTitle("ЛР 4 — Proxy. ЛКМ — перетаскивание, двойной ПКМ — загрузка TestImage");

    Canvas* canvas = new Canvas(&window);
    window.setCentralWidget(canvas);

    QString path = QDir(QCoreApplication::applicationDirPath())
                       .filePath("../assets/TestImage.png");
    canvas->addImage(std::make_shared<ImageProxy>(path, 80, 80));

    window.resize(900, 600);
    window.show();
    return app.exec();
}
