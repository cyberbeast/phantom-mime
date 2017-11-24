from __future__ import print_function

import torch.nn as nn, torch.nn.functional as F, pdb
class QNet(nn.Module):
    def __init__(self):
        super(QNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1)
        self.bn1 = nn.BatchNorm2d(4)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=1)
        self.bn2 = nn.BatchNorm2d(8)
        self.conv3 = nn.Conv2d(8, 16, kernel_size=3, stride=2)
        self.bn3 = nn.BatchNorm2d(16)        
        self.dense1 = nn.Linear(16*4*4, 64)
        self.dense2 = nn.Linear(64, 16)
        self.dense3 = nn.Linear(16, 4)

    def forward(self, inputs):
        pdb.set_trace()
        inputs = F.relu(self.bn1(self.conv1(inputs)))
        inputs = F.relu(self.bn2(self.conv2(inputs)))
        inputs = F.relu(self.bn3(self.conv3(inputs)))
        inputs = self.dense1(inputs.view(inputs.size(0), -1))
        inputs = self.dense2(inputs)
        return self.dense3(inputs)
