import torch
import torch.nn as nn
import torch.nn.functional as F
import sklearn.metrics as metrics
from tqdm import trange
from sklearn.model_selection import train_test_split
from parameters import parameters


class CNN(nn.Module):
    def __init__(self, word_len):
        super(CNN, self).__init__()
        self.dim = 100
        self.hidden_dim = 50
        self.sen_len = word_len
        self.classes = 4
        self.ci = 1
        self.knum = 64
        self.ktype = 8
        self.ks = list(range(2, 2 + self.ktype))
        self.embed = nn.Embedding(self.sen_len, self.dim)
        self.convs = nn.ModuleList([nn.Conv2d(self.ci, self.knum, (K, self.dim)) for K in self.ks])
        self.dp = nn.Dropout(0.25)
        self.fc1 = nn.Linear(len(self.ks) * self.knum, self.hidden_dim)
        self.fc = nn.Linear(self.hidden_dim, self.classes)

    def forward(self, x):
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
        return x, c


def text_cnn(X, Y, word_len, result_output, device):

    parameter = parameters()
    learn_rate = parameter.lr
    batch_size = parameter.batch_size
    num_epochs_max = parameter.max_epoch
    torch.manual_seed(parameter.random_seed)

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=0)
    X_train = torch.from_numpy(X_train).long().to(device)
    X_test = torch.from_numpy(X_test).long().to(device)
    Y_train = torch.from_numpy(Y_train).long().to(device)
    Y_test = torch.from_numpy(Y_test).long().to(device)
    train_set = torch.utils.data.TensorDataset(X_train, Y_train)
    test_set = torch.utils.data.TensorDataset(X_test, Y_test)
    train_loader = torch.utils.data.DataLoader(dataset=train_set, batch_size=batch_size, shuffle=False)

    net = CNN(word_len).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=learn_rate)

    for epoch in trange(num_epochs_max):
        net.train()
        print('training begin')
        for idx, (x, y) in enumerate(train_loader):
            optimizer.zero_grad()
            preds, _ = net(x)
            loss = criterion(preds, y)
            loss.backward()
            optimizer.step()
        print('test begin')
        net.eval()
        preds, _ = net(X_test)
        predicted = torch.argmax(preds, 1)
        acc = metrics.accuracy_score(Y_test.to(device), predicted.to(device))
        f1 = metrics.f1_score(Y_test.to(device), predicted.to(device))
        auc_ = metrics.roc_auc_score(Y_test.to(device), predicted.to(device))
        cm = metrics.confusion_matrix(Y_test.to(device), predicted.to(device))
        with open(result_output, 'a') as f:
            print("epoch %f:" %(epoch))
            print("epoch %f:"%(epoch), file=f)
            print("Accuracy: %f, F1_score: %f, AUC: %f" %(acc, f1, auc_))
            print("Accuracy: %f, F1_score: %f, AUC: %f" %(acc, f1, auc_), file=f)
            print(cm)
            print(cm, file=f)



