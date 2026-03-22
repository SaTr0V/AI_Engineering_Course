# Данные проекта

> Эта папка с данными проекта.

Обучающая выборка состоит из 800 изображений DIV2K и 100 изображений FFHQ. Также, здесь приведено по 10 примеров для обоих датасетов в папках `div2k_samples` и `ffhq_samples`.

The training set consists of 800 DIV2K images and 100 FFHQ images. 10 samples for both datasets are also provided here in `div2k_samples` and `ffhq_samples`.

## Установка необработанных датасетов

Чтобы установить датасеты, выполните соответствующие команды из папки проекта:


**Если вы используете `uv`:**
```bash
uv run download-datasets
```

**Иначе просто выполните:**
```bash
python src/dataset/download.py
```

Когда появится сообщение `"All tasks finished"`, вы можете прервать процесс используя `CTRL+C`.