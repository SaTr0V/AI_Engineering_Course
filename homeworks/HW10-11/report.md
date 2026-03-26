# HW10-11 – компьютерное зрение в PyTorch: CNN, transfer learning, detection/segmentation

## 1. Кратко: что сделано

Часть A (классификация): Выбран датасет Flowers102 - он содержит 102 класса цветов, что представляет собой сложную задачу классификации. Датасет интересен тем, что имеет официальный train/val/test split и достаточно малое количество обучающих изображений на класс (~10).

Часть B (structured vision): Выбран датасет Pascal VOC с треком detection. Этот датасет является стандартом де-факто для бенчмаркинга детекторов объектов, имеет качественную разметку bounding boxes и хорошо поддерживается в torchvision.

В части A сравнивались 4 эксперимента (C1-C4): простая CNN без аугментаций, простая CNN с аугментациями, ResNet18 head-only, ResNet18 fine-tune.
В части B сравнивались 2 режима инференса (V1-V2): разные пороги уверенности (0.3 и 0.7).

## 2. Среда и воспроизводимость

- Python: 3.14.2
- torch / torchvision: 2.10.0 / 0.25.0
- Устройство (CPU/GPU): GPU (Colab T4)
- Seed: 42
- Как запустить: открыть `HW10-11.ipynb` и выполнить Run All.

## 3. Данные

### 3.1. Часть A: классификация

- Датасет: `Flowers102`
- Разделение: 1020/1020/6149
- Базовые transforms: Resize(256), CenterCrop(224), ToTensor, Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Augmentation transforms: RandomResizedCrop(224), RandomHorizontalFlip, RandomRotation(15), ToTensor, Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- Комментарий: Flowers102 - сложный датасет для классификации из-за большого числа классов (102) и малого количества обучающих примеров на класс (~10 изображений). Изображения имеют размер 224×224 после preprocessing. Задача требует использования transfer learning для достижения хорошей точности.

### 3.2. Часть B: structured vision

- Датасет: `Pascal VOC`
- Трек: `detection`
- Что считается ground truth: Bounding boxes из XML-разметки VOC
- Какие предсказания использовались: FasterRCNN_ResNet50_FPN с фильтрацией по score threshold
- Комментарий: Pascal VOC предоставляет качественную разметку bounding boxes для 20 классов объектов. Использование pretrained FasterRCNN позволяет продемонстрировать работу detection пайплайна без необходимости дообучения модели.

## 4. Часть A: модели и обучение (C1-C4)

- C1 (simple-cnn-base): SimpleCNN (3 conv слоя + FC), без аугментаций, lr=1e-3
- C2 (simple-cnn-aug): SimpleCNN (та же архитектура), с аугментациями, lr=1e-3
- C3 (resnet18-head-only): ResNet18 pretrained, заморожен backbone, обучается только fc, lr=1e-3
- C4 (resnet18-finetune): ResNet18 pretrained, разморожены layer4+fc, lr=1e-4

Дополнительно:

- Loss: CrossEntropyLoss
- Optimizer: Adam 
- Batch size: 64
- Epochs (макс): 10
- Критерий выбора лучшей модели: best_val_accuracy (лучший accuracy на val)

## 5. Часть B: постановка задачи и режимы оценки (V1-V2)

- Модель: FasterRCNN_ResNet50_FPN (pretrained на COCO)
- V1: `score_threshold = 0.3`
- V2: `score_threshold = 0.7`
- Как считался IoU: Стандартная формула IoU = intersection / union для bounding boxes. Матчинг prediction <-> ground truth при IoU >= 0.5.
- Как считались precision / recall:

  - Precision: TP / (TP + FP) = число корректных детекций / число всех предсказаний

  - Recall: TP / (TP + FN) = число корректных детекций / число всех ground truth объектов

  - Mean IoU: среднее IoU по всем matched предсказаниям

## 6. Результаты

Ссылки на файлы в репозитории:

- Таблица результатов: `./artifacts/runs.csv`
- Лучшая модель части A: `./artifacts/best_classifier.pt`
- Конфиг лучшей модели части A: `./artifacts/best_classifier_config.json`
- Кривые лучшего прогона классификации: `./artifacts/figures/classification_curves_best.png`
- Сравнение C1-C4: `./artifacts/figures/classification_compare.png`
- Визуализация аугментаций: `./artifacts/figures/augmentations_preview.png`
- Detection примеры: `./artifacts/figures/detection_examples.png`
- Detection метрики: `./artifacts/figures/detection_metrics.png`

Короткая сводка (6-10 строк):

- Лучший эксперимент части A: C4 (ResNet18 fine-tune)
- Лучшая `val_accuracy`: 0.8824
- Итоговая `test_accuracy` лучшего классификатора: 0.8523
- Что дали аугментации (C2 vs C1): C2 показал худший результат (0.1 vs 0.18) - на малом датасете аугментации навредили.
- Что дал transfer learning (C3/C4 vs C1/C2): значительное улучшение (C3=0.83, C4=0.88 против C1=0.18)
- Что оказалось лучше: head-only или partial fine-tuning: Fine-tuning (C4) лучше head-only (C3) на ~5%
- Что показал режим V1 во второй части: Precision=0.409, Recall=0.939, Mean IoU=0.814
- Что показал режим V2 во второй части: Precision=0.664, Recall=0.865, Mean IoU=0.777
- Как интерпретируются метрики второй части: при повышении порога precision растёт, recall падает.

## 7. Анализ

Простая CNN (C1/C2): простая CNN показала низкие результаты на Flowers102. Это объясняется недостаточной ёмкостью модели для 102 классов и малым количеством обучающих данных. Модель быстро переобучилась (train accuracy ~0.97, val accuracy ~0.18).

Аугментации: аугментации не дали улучшения, а наоборот ухудшили результат. На датасете с ~10 изображениями на класс агрессивные аугментации (RandomResizedCrop, RandomRotation) искажают и без того ограниченную информацию. Для таких малых датасетов нужны более осторожные аугментации или сильная регуляризация.

Pretrained ResNet18: Transfer learning дал огромный прирост. Pretrained веса содержат общие визуальные признаки (edges, textures, shapes), которые универсальны для задач классификации изображений.

Head-only vs Fine-tuning: Partial fine-tuning (C4) превзошёл head-only (C3). Разморозка layer4 позволила модели адаптировать высокоуровневые признаки под специфику датасета.

Detection метрики: выбранные метрики (precision, recall, mean IoU) хорошо подходят для оценки детектора. Precision показывает качество предсказаний, recall - полноту обнаружения, IoU - точность локализации.

V1 vs V2: при переходе от threshold=0.3 к threshold=0.7 precision вырос с 0.409 до 0.664, recall упал с 0.939 до 0.865. То есть более высокий порог отсеивает ненадёжные предсказания, повышая точность, но пропуская больше объектов.

Ошибки модели: наиболее показательные ошибки - путаница между визуально похожими классами цветов (например, разные виды лилий или роз). Для detection - ложные срабатывания на низком пороге и пропуск мелких объектов на высоком пороге.

## 8. Итоговый вывод

Базовый конфиг классификации: для production я бы выбрал C4 (ResNet18 fine-tune) как базовый конфиг. Он даёт лучший баланс между точностью и вычислительной эффективностью. Для ещё лучших результатов можно рассмотреть ResNet50 или EfficientNet.

Transfer learning: главное, что я понял про transfer learning - это критически важный инструмент для задач с малым количеством данных. Pretrained веса экономят время обучения и дают значительный прирост точности. Partial fine-tuning часто оптимален - позволяет адаптировать модель под задачу без риска catastrophic forgetting.

Detection/Segmentation и метрики: для detection/segmentation задач важно понимать trade-off между precision и recall. Выбор порога уверенности зависит от приложения: для безопасности нужен высокий recall, для пользовательского опыта — высокий precision. Mean IoU хорошо дополняет эти метрики, показывая качество локализации.

## 9. Приложение (опционально)

Дополнительные графики:
- `./artifacts/figures/c1_history.png` — кривые обучения C1
- `./artifacts/figures/c2_history.png` — кривые обучения C2
- `./artifacts/figures/c3_history.png` — кривые обучения C3
- `./artifacts/figures/c4_history.png` — кривые обучения C4

Наблюдения:
- C1 показал явное переобучение (train acc ~0.97, val acc ~0.18)
- C2 не смог обучиться из-за агрессивных аугментаций на малом датасете
- C3 и C4 показали стабильное обучение без переобучения
- C4 достиг train accuracy 100% к 5 эпохе, но val accuracy продолжал расти до 88%
