import torch
import torch.nn as nn
import torch.nn.functional as F

from torchvision.models import resnet34


#################################
# DEEP CONVOLUTIONAL NEURAL NET #
#################################


class ESC50Model(nn.Module):
    '''
    Custom CNN
    '''

    def __init__(self, input_shape, batch_size=16, num_cat=50):
        super().__init__()

        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.conv4 = nn.Conv2d(64, 64, kernel_size=3, stride=1, padding=1)
        self.conv5 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.conv6 = nn.Conv2d(128, 128, kernel_size=3, stride=1, padding=1)
        self.conv7 = nn.Conv2d(128, 256, kernel_size=3, stride=1, padding=1)
        self.conv8 = nn.Conv2d(256, 256, kernel_size=3, stride=1, padding=1)

        self.fcl_1 = nn.Linear(256 * (((input_shape[1] // 2) // 2) // 2) * (((input_shape[2] // 2) // 2) // 2), 500)
        self.fcl_2 = nn.Linear(500, num_cat)

        self.batch_32 = nn.BatchNorm2d(32)
        self.batch_64 = nn.BatchNorm2d(64)
        self.batch_128 = nn.BatchNorm2d(128)
        self.batch_256 = nn.BatchNorm2d(256)

        self.drop_50 = nn.Dropout(0.50)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(self.batch_32(x))
        x = self.conv2(x)
        x = F.relu(self.batch_32(x))
        x = F.max_pool2d(x, kernel_size=2)
        x = self.conv3(x)
        x = F.relu(self.batch_64(x))
        x = self.conv4(x)
        x = F.relu(self.batch_64(x))
        x = F.max_pool2d(x, kernel_size=2)
        x = self.conv5(x)
        x = F.relu(self.batch_128(x))
        x = self.conv6(x)
        x = F.relu(self.batch_128(x))
        x = F.max_pool2d(x, kernel_size=2)
        x = self.conv7(x)
        x = F.relu(self.batch_256(x))
        x = self.conv8(x)
        x = F.relu(self.batch_256(x))
        x = x.view(x.size(0), -1)
        x = F.relu(self.fcl_1(x))
        x = self.drop_50(x)
        x = self.fcl_2(x)

        return x


##############
# RESNET_34  #
##############

class RES:
    '''
    Modified Pretrained ResNet34
    '''

    def __init__(self):

        self.model = resnet34(pretrained=True)

    def gen_resnet(self):

        if torch.cuda.is_available():
            device = torch.device('cuda:0')
        else:
            device = torch.device('cpu')

        model = self.model
        model.fc = nn.Linear(512, 50)
        model.conv1 = nn.Conv2d(1, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        model = model.to(device)

        return model



