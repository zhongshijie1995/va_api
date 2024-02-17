import os
import shutil

import cv2
from loguru import logger as log
from ultralytics import YOLO, settings

from tools import pic_tools, datetime_tools, json_tools


class Models:
    def __init__(self, data: str = 'data', data_ext: str = 'data_ext'):
        self.data = data
        self.data_ext = data_ext
        self.model_dict = {}

    @staticmethod
    def get_model_type(name: str):
        return name.split('_')[0]

    def load_model(self, name: str, weights: str):
        if Models.get_model_type(name) == 'YOLO':
            self.model_dict[name] = YOLO(weights)

    def get_model(self, name: str):
        if name not in self.model_dict:
            self.load_model(name, os.path.join(self.data, name, 'weights.pt'))
        return self.model_dict.get(name)

    def pred(self, name: str, source: str):
        # 提取预测
        details = []
        model = self.get_model(name)
        if Models.get_model_type(name) == 'YOLO':
            predicts = model.predict(source)
            for predict in predicts:
                boxes = predict.boxes
                details.append({
                    'cls': [predict.names[i] for i in boxes.cls.tolist()],
                    'conf': boxes.conf.tolist(),
                    'xyxy': boxes.xyxy.tolist()
                })
        # 标记预测
        mark = cv2.imread(source)
        for detail in details:
            for i in range(len(detail.get('cls'))):
                xyxy = detail.get('xyxy')[i]
                x1, y1, x2, y2 = [int(i) for i in xyxy]
                cv2.rectangle(mark, (x1, y1), (x2, y2), color=[255, 0, 0], thickness=1)
                cv2.putText(mark, '%s %.2f' % (detail.get('cls')[i], detail.get('conf')[i]), (x1, y1 + 5),
                            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=[255, 0, 0], thickness=1,
                            lineType=cv2.LINE_AA)
        mark = pic_tools.cv2_to_base64(mark)
        return details, mark

    @staticmethod
    def train():
        log.info('训练任务扫描')
        status_path = 'data/status.json'
        status = json_tools.load(status_path)
        if 'train_task' not in status:
            log.info('扫描发现：无训练任务')
            return
        for idx, train_task in enumerate(status.get('train_task')):
            if train_task.get('status') != 0:
                continue
            # 提取训练任务
            name, weights, train_args = train_task.get('name'), train_task.get('weights'), train_task.get('train_args')
            log.info('发现训练任务: {}', name)
            # 抢占训练任务
            status['train_task'][idx]['status'] = 1
            status['train_task'][idx]['status_datetime'].append(datetime_tools.datetime_str())
            json_tools.save(status, status_path)
            log.info('已抢占训练任务: {}', name)
            # 执行训练任务
            if Models.get_model_type(name) == 'YOLO':
                # 进行训练
                settings.reset()
                settings.update({
                    'datasets_dir': 'data_ext/datasets',
                    'weights_dir': 'data_ext/weights',
                    'runs_dir': 'data_ext/runs',
                })
                model = YOLO(weights)
                train_result = model.train(None, **train_args)
                # 备份权重
                shutil.move(weights, '%s.%s' % (weights, datetime_tools.datetime_str(with_symbol=False)))
                # 更新权重
                shutil.copy(os.path.join(train_result.save_dir, 'weights', 'best.pt'), weights)
                # 更新训练任务
                status['train_task'][idx]['status'] = 2
                status['train_task'][idx]['status_datetime'].append(datetime_tools.datetime_str())
                status['train_task'][idx]['results_dict'] = train_result.results_dict
                status['train_task'][idx]['save_dir'] = str(train_result.save_dir)
                json_tools.save(status, status_path)
                log.info('已更新训练任务: {}', name)
        return
