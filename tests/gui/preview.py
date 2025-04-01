from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QPixmap, QImage
import matplotlib.pyplot as plt
import gdsfactory as gf


class PreviewWindow(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

    def update_preview(self, component):
        """使用matplotlib渲染器件预览"""
        fig, ax = plt.subplots(figsize=(8, 4))
        component.plot(ax)
        ax.set_title(component.name)
        ax.axis('off')

        # 转换为QPixmap
        fig.canvas.draw()
        img = QImage(
            fig.canvas.buffer_rgba(),
            fig.canvas.width(),
            fig.canvas.height(),
            QImage.Format_ARGB32
        )
        self.scene.clear()
        self.scene.addPixmap(QPixmap.fromImage(img))
        plt.close(fig)