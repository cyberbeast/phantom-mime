from __future__ import print_function

import torch.nn as nn, torch.nn.functional as F

class QNet(nn.Module):
    def __init__(self):
        super(QNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm2d(32)
        self.head = nn.Linear(32*22*22, 4)

    def forward(self, inputs):
        inputs = F.relu(self.bn1(self.conv1(inputs)))
        inputs = F.relu(self.bn2(self.conv2(inputs)))
        inputs = F.relu(self.bn3(self.conv3(inputs)))
        return self.head(inputs.view(inputs.size(0), -1))
