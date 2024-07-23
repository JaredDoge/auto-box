import cv2
from time import perf_counter


from pytorch.tool.torch_utils import do_detect
from pytorch.tool.darknet2pytorch import Darknet
from pydantic import BaseModel
from pytorch.tool.utils import *
from collections import OrderedDict


class Arrow(BaseModel):
    image: list


class Machine:

    def __init__(self):
        self.confirmation = None
        self.channel = None
        self.m = None
        self.class_names = None

    def cleanup(self):
        if self.m is not None:
            pass
            # 如果Darknet类有释放资源的方法，调用它
            # self.m.release()
            # self.m = None
            # 清理CUDA缓存（如果有的话）
            # torch.cuda.empty_cache()

    async def startup(self):
        self.m = Darknet('pytorch/yolov4-mish-416.cfg')
        self.m.print_network()
        self.m.load_weights('pytorch/yolov4-mish-416_last.weights')
        self.m.cuda()

        # num_classes = self.m.num_classes
        # if num_classes == 20:
        #     names_file = 'pytorch/data/voc.names'
        # elif num_classes == 80:
        #     names_file = 'pytorch/data/coco.names'
        # else:
        #     names_file = 'pytorch/data/x.names'
        # self.class_names = load_class_names(names_file)
        #
        # self.channel = 30
        # self.confirmation = True

    def predict(self, img):
        now = perf_counter()
        # img = np.array(img)
        img = img.reshape((228, 576, 3)).astype('uint8')
        sized = cv2.resize(img, (416, 416))
        # print(img.shape)
        for i in range(2):
            start = time.time()
            boxes = do_detect(self.m, sized, 0.4, 0.6, True)

        xd = {}
        for b in boxes[0]:
            xd[b[0]] = b[6]

        sortdict = OrderedDict(sorted(xd.items(), key=lambda x: x[0]))
        alphabets = ''
        for s in sortdict:
            # print(s, sortdict[s])
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
