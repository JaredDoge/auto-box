import cv2
from time import perf_counter


from pytorch.tool.torch_utils import do_detect
from pytorch.tool.darknet2pytorch import Darknet
from pydantic import BaseModel
from collections import OrderedDict


class Arrow(BaseModel):
    image: list


class Machine:

    def __init__(self):
        self.m = None

    def cleanup(self):
        pass

    async def startup(self):
        self.m = Darknet('pytorch/yolov4-mish-416.cfg')
        self.m.print_network()
        self.m.load_weights('pytorch/yolov4-mish-416_last.weights')
        self.m.cpu()


    def predict(self, img):
        now = perf_counter()
        img = img.reshape((228, 576, 3)).astype('uint8')
        sized = cv2.resize(img, (416, 416))
        for i in range(2):
            boxes = do_detect(self.m, sized, 0.4, 0.6)

        xd = {}
        for b in boxes[0]:
            xd[b[0]] = b[6]

        sortdict = OrderedDict(sorted(xd.items(), key=lambda x: x[0]))
        alphabets = ''
        for s in sortdict:
            if sortdict[s] == 0:
                alphabets += 'u'
            if sortdict[s] == 1:
                alphabets += 'd'
            if sortdict[s] == 2:
                alphabets += 'l'
            if sortdict[s] == 3:
                alphabets += 'r'

        print(f'{perf_counter()-now=}')
        return alphabets
