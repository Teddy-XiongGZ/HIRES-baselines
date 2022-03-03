import torch
import torch.nn as nn
import torch.nn.functional as F
import sklearn.metrics as metrics
from tqdm import trange
from sklearn.model_selection import train_test_split
from parameters import parameters
from torch.utils.data import Dataset
from text_preprocessing import EPItem
import numpy as np
from scipy.sparse import vstack

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from text_preprocessing import getsentences, mapX2epitem

PADDING_SIZE = 50

learn_rate = 0.001
batch_size = 32
#num_epochs_max = 10

class mydataset(Dataset):
    def __init__(self, itemlist):
        self.itemlist = itemlist

    def __getitem__(self, idx):
        return self.itemlist[idx]

    def __len__(self):
        return len(self.itemlist)
    '''

    def get_split_points(self):
        current = 0
        split_points = []
        split_points.append(current)
        for item in self.itemlist:
            current += len(item)
            split_points.append(current)
        return split_points
    '''

def totensor(coo):
    values = coo.data
    indices = np.vstack((coo.row, coo.col))

    i = torch.LongTensor(indices)
    v = torch.LongTensor(values)
    shape = coo.shape

    return torch.sparse.LongTensor(i, v, torch.Size(shape)).to_dense()

def mycollate_fn(itemlist):
    return (totensor(vstack([item.getdata() for item in itemlist])), \
        torch.LongTensor([item.getlabel() for item in itemlist]), get_split_points(itemlist))

def get_split_points(batch):
    current = 0
    split_points = []
    split_points.append(current)
    for item in batch:
        current += len(item)
        split_points.append(current)
    return split_points


class CNN(nn.Module):
    def __init__(self, word_len, classes):
        super(CNN, self).__init__()
        self.dim = 100
        self.hidden_dim = 50
        self.sen_len = word_len
        self.classes = classes
        self.ci = 1
        self.knum = 64
        self.ktype = 8
        self.ks = list(range(2, 2 + self.ktype))
        self.embed = nn.Embedding(self.sen_len, self.dim)
        self.convs = nn.ModuleList([nn.Conv2d(self.ci, self.knum, (K, self.dim)) for K in self.ks])
        self.dp = nn.Dropout(0.25)
        self.fc1 = nn.Linear(len(self.ks) * self.knum, self.hidden_dim)
        self.fc = nn.Linear(self.hidden_dim, self.classes)

    def forward(self, x, split_points):
        x = self.embed(x)
        x = x.unsqueeze(1)
        x = [F.relu(conv(x)).squeeze(3) for conv in self.convs]
        x = [F.max_pool1d(line, line.size(2)).squeeze(2) for line in x]
        x = torch.cat(x, 1)
        x = self.dp(x)
        x = self.fc1(x)
        x = F.relu(x)
        c = x
        x = self.fc(x)
        x = F.softmax(x, dim=1)
        '''
        ep_score_all = []
        for i in range(1, len(split_points)):
            ep_score_tmp = x[split_points[i-1]:split_points[i]].mean(0).unsqueeze(0)
            #print(ep_score_tmp.shape)
            ep_score_all.append(ep_score_tmp)
        ep_score = torch.cat(ep_score_all, 0)
        return ep_score, c
        '''
        return x, c

def expandlabel(split_points, label):
    label = label.cpu().numpy().tolist()
    expanded_label = []
    assert len(split_points)-1 == len(label)
    for i in range(len(split_points)-1):
        expanded_label.append(torch.LongTensor(label[i:i+1]*(split_points[i+1]-split_points[i])))
    expanded_label = torch.cat(expanded_label, 0)
    return expanded_label

def mergepred(split_points, pred):
    pred = pred.cpu().numpy().tolist()
    newpred = []
    for i in range(len(split_points)-1):
        newpred.append(np.argmax(np.bincount(pred[split_points[i]:split_points[i+1]])))
    newpred = np.array(newpred)
    return newpred

def text_cnn(X, Y, result_output, device, Xt=None, Yt=None):

    parameter = parameters()
    learn_rate = parameter.lr
    batch_size = parameter.batch_size
    num_epochs_max = parameter.max_epoch

    torch.backends.cudnn.deterministic = True
    torch.manual_seed(parameter.random_seed)
    if device != 'cpu':
        torch.cuda.manual_seed(parameter.random_seed)
    np.random.seed(parameter.random_seed)

    if Xt:
        X_train = X
        Y_train = Y
        X_test = Xt
        Y_test = Yt
    else:
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    # X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)

    tokenizer = Tokenizer(num_words=None)
    tokenizer.fit_on_texts(getsentences(X_train))
    word_list = tokenizer.word_index
    word_len = len(word_list) + 20
    corpus_seq = tokenizer.texts_to_sequences(getsentences(X_train))
    corpus_seq = pad_sequences(corpus_seq, maxlen=PADDING_SIZE)
    X_train_data = np.array(corpus_seq)
    mapX2epitem(X_train, X_train_data)
    corpus_seq = tokenizer.texts_to_sequences(getsentences(X_test))
    corpus_seq = pad_sequences(corpus_seq, maxlen=PADDING_SIZE)
    X_test_data = np.array(corpus_seq)
    mapX2epitem(X_test, X_test_data)

    train_dataset = mydataset(X_train)
    test_dataset = mydataset(X_test)
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, collate_fn = mycollate_fn)
    test_loader = torch.utils.data.DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=False, collate_fn = mycollate_fn)
    
    '''
    X_train = torch.from_numpy(X_train).long().to(device)
    X_test = torch.from_numpy(X_test).long().to(device)
    Y_train = torch.from_numpy(Y_train).long().to(device)
    Y_test = torch.from_numpy(Y_test).long().to(device)
    train_set = torch.utils.data.TensorDataset(X_train, Y_train)
    test_set = torch.utils.data.TensorDataset(X_test, Y_test)
    train_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=batch_size, shuffle=False)
    '''
    net = CNN(word_len,len(set(Y))).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=learn_rate, weight_decay=1e-5)
    #scheduler = torch.optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.9)



    for epoch in trange(num_epochs_max):
        net.train()
        train_loss = []
        print('training begin')
        for idx, (x, y, split_points) in enumerate(train_loader):
            optimizer.zero_grad()
            preds, _ = net(x.to(device), split_points)
            y = expandlabel(split_points, y)
            loss = criterion(preds, y.to(device))
            loss.backward()
            optimizer.step()
            train_loss.append(loss.item())
            #scheduler.step()
        #print('[epoch %d] training loss: %.3f' % (epoch + 1, np.mean(train_loss)))
        print('test begin')
        net.eval()
        Y_test = []
        predicted = []
        valid_loss = []
        for idx, (x, y, split_points) in enumerate(test_loader):
            preds, _ = net(x.to(device), split_points)
            y_expanded = expandlabel(split_points, y)
            loss = criterion(preds, y_expanded.to(device))
            preds = torch.argmax(preds, 1)
            
            preds = mergepred(split_points, preds)
            predicted += preds.tolist()
            Y_test += list(y.detach().cpu().numpy())
            valid_loss.append(loss.item())
        #print('[epoch %d] test loss: %.3f' % (epoch + 1, np.mean(train_loss)))
        acc = metrics.accuracy_score(Y_test, predicted)
        #f1 = metrics.f1_score(Y_test, predicted)
        #auc_ = metrics.roc_auc_score(Y_test, predicted)
        cm = metrics.confusion_matrix(Y_test, predicted)
        if net.classes == 2:
            pos_acc = (cm[1][1])/(np.sum(cm[1]))
        else:
            pos_acc = (cm[1][1]+cm[2][2]+cm[3][3])/(np.sum(cm[1]+cm[2]+cm[3]))
        with open(result_output, 'a') as f:
            print("epoch %f:" %(epoch))
            print("epoch %f:"%(epoch), file=f)
            print("Accuracy: %f, positive acc: %f" %(acc, pos_acc))
            print("Accuracy: %f, positive acc: %f" %(acc, pos_acc), file=f)
            print('[epoch %d] training loss: %.3f' % (epoch + 1, np.mean(train_loss)), file=f)
            print('[epoch %d] training loss: %.3f' % (epoch + 1, np.mean(train_loss)))
            print('[epoch %d] test loss: %.3f' % (epoch + 1, np.mean(valid_loss)), file=f)
            print('[epoch %d] test loss: %.3f' % (epoch + 1, np.mean(valid_loss)))
            print(cm)
            print(cm, file=f)



