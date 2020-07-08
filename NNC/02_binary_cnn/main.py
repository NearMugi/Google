import sys

import nnabla as nn
import nnabla.functions as F
import nnabla.parametric_functions as PF

def network(x, test=False):
    # Input:x -> 1,28,28
    # Convolution -> 16,24,24
    h = PF.convolution(x, 16, (5,5), (0,0), name='Convolution')
    # MaxPooling -> 16,12,12
    h = F.max_pooling(h, (2,2), (2,2))
    # Tanh
    h = F.tanh(h)
    # Convolution_2 -> 8,8,8
    h = PF.convolution(h, 8, (5,5), (0,0), name='Convolution_2')
    # MaxPooling_2 -> 8,4,4
    h = F.max_pooling(h, (2,2), (2,2))
    # Tanh_2
    h = F.tanh(h)
    # Affine -> 10
    h = PF.affine(h, (10,), name='Affine')
    # Tanh_3
    h = F.tanh(h)
    # Affine_2 -> 1
    h = PF.affine(h, (1,), name='Affine_2')
    # Sigmoid
    h = F.sigmoid(h)
    return h

def nnc_sample(request):
    import cv2
    import struct
    import json

    # リクエストデータ(JSON)を変換
    request_json = request.get_json()

#    print(request_json['studyData']['data'])

    if request_json and 'studyData' in request_json:
        binary = request_json['studyData']['data']
        with open('/tmp/results.nnp', 'wb') as f:
            for b in binary:
                f.write(struct.pack("B", b))

    else:
        return 'No studyData'

    if request_json and 'inputData' in request_json:
        binary = request_json['inputData']['data']
        with open('/tmp/image.png', 'wb') as f:
            for b in binary:
                f.write(struct.pack("B", b))
    else:
        return 'No inputData'

    # load parameters
    nn.load_parameters('/tmp/results.nnp')

    # Prepare input variable
    x=nn.Variable((1,1,28,28))

    # Let input data to x.d
    # x.d = ...
    img = cv2.imread('/tmp/image.png',0)
    x.d = img

    # Build network for inference
    y = network(x, test=True)

    # Execute inference
    y.forward()
    print(y.d)

    ret = json.dumps(y.d.tolist(), ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
    return ret