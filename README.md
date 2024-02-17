# va_api

## 1. 快速开始
### 1.1 安装依赖
```shell
pip install -r req.txt
```

### 1.2 准备外置文件目录

#### 文件目录树
```
data
    |-  “[模型类型]_[数据集名称]”
        datasets.yaml
        weights.pt
    status.json
data_ext
    |-  datasets
        |-  “[模型类型]_[数据集名称]”
            images
            labels
...
main.py
README.md
...
```

#### 使用模板
```shell
cp -r data_template/data ./
cp -r data_template/data_ext ./
```


### 1.3 启动服务
```shell
python -m uvicorn main:app --reload
```

## 2. 预测
### 2.1 使用模板
```shell
curl -H "Content-Type: application/json" -X POST -d '{"name": "YOLO_coco128-seg", "source": "data_template/test1.jpg"}' "http://localhost:8000/pred"
```

## 3. 训练
### 3.1 数据标注（在图形化操作系统中）
```shell
labelImg
```
1. 点击`YOLO`或`CreateML`或`PascalVOC`，使得选中数据集类型为`YOLO`。
2. 在标注工具中`Open Dir`选择数据集的图片源目录。
2. 在标注工具中`Change Save Dir`选择数据集的标注保存目录。
3. 使用`Create RectBox`->`Save`->`Next Image`进行数据标注。

### 3.2 编辑datasets.yaml
```yaml
path: YOLO_coco128-seg # 数据集路径
train: images/train2017 # 训练数据集合
val: images/train2017 # 验证数据集合
test: # 测试数据集合（可选）
names:
  0: 类别0 # 对象序号: 对象名称
  1: 类别1 # 对象序号: 对象名称
download: # 下载数据集地址（可选）
```
1. 需要注意`names`字段的顺序需要与标注数据集中的`class.txt`保持一致。

### 3.3 安置预训练权重
1. 保证数据集路径下存在`weights.pt`预训练全权重，可从`data_template`中提取。

### 3.3 编辑status.json
```json5
{
  "train_task": [
    {
      "status": 0, /* 待训练-0 训练中-1 训练完成-2 */
      "status_datetime": [], /* 状态转换时间 */
      "name": "YOLO_coco128-seg", /* 模型名称 */
      "weights": "data/YOLO_coco128-seg/weights.pt", /* 预训练权重文件目录 */
      "train_args": {
        "data": "data/YOLO_coco128-seg/datasets.yaml", /* 数据集描述文件目录 */
        "epochs": 1, /* 迭代次数 */
        "device": "mps" /* 无-CPU cuda- mps-苹果M芯片GPU */
      }
    }
  ]
}
```
### 3.4 自动开始训练
1. 模型训练将会由定时任务自动调起。
