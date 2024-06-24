import torch
import data
import model as m
import utils


#########################
# TRAINING ABSTRACTIONS #
#########################

def prepare_data():
    '''
    Prepare Data:
    1. read in audio meta data
    2. set data loaders for training
    3. save categorical look up tabels
    '''

    train_data, valid_data = data.read_data(data.path)
    train_loader, valid_loader = data.gen_data_loader(train_data, valid_data)
    utils.save_cat_idx(train_data, 'models/idx2cat.pkl')

    return train_loader, valid_loader


def train_CNN(train_loader, valid_loader):
    '''
    Train CNN:
    1. check GPU availabilty
    2. instantiate CNN model
    3. train model
    4. save trained model
    '''

    if torch.cuda.is_available():
        device = torch.device('cuda:0')
    else:
        device = torch.device('cpu')

    model = m.ESC50Model(input_shape=(1, 128, 431),
                         batch_size=16,
                         num_cat=50).to(device)

    trained_model = utils.train(model, train_loader, valid_loader)
    utils.save_model(trained_model, 'models/CNN_Classifier.pth')

    return trained_model


def train_resNet(train_loader, valid_loader):
    '''
    Train ResNet34:
    1. instantiate modified pretrained ResNet34
    2. train model
    3. save model
    '''

    model = m.RES().gen_resnet()

    trained_model = utils.train(model, train_loader, valid_loader,
                                epochs=50,
                                learning_rate=2e-4
                                )
    utils.save_model(trained_model, 'models/resNet.pth')

    return trained_model


if __name__ == '__main__':
    ####################
    # RUN ABSTRACTIONS #
    ####################

    train_loader, valid_loader = prepare_data()
    CNN_model = train_CNN(train_loader, valid_loader)
    resNet_model = train_resNet(train_loader, valid_loader)








