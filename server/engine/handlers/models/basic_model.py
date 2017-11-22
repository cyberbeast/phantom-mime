from __future__ import print_function

import torch.nn as nn, torch.nn.functional as F
class QNet(nn.Module):
    def __init__(self):
        super(QNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 4, kernel_size=3, stride=1)
        self.bn1 = nn.BatchNorm2d(4)
        self.conv2 = nn.Conv2d(4, 8, kernel_size=3, stride=2)
        self.bn2 = nn.BatchNorm2d(8)
        self.head = nn.Linear(8*8*8, 4)

    def forward(self, inputs):
        inputs = F.relu(self.bn1(self.conv1(inputs)))
        inputs = F.relu(self.bn2(self.conv2(inputs)))
        return self.head(inputs.view(inputs.size(0), -1))
