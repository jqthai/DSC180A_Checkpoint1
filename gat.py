# -*- coding: utf-8 -*-
"""GAT.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JIr56YA5mu2CJvV1N0aOVRrlgutwPO9m
"""

import os
import torch
os.environ['TORCH'] = torch.__version__
print(torch.__version__)

#!pip install -q torch-scatter -f https://data.pyg.org/whl/torch-${TORCH}.html
#!pip install -q torch-sparse -f https://data.pyg.org/whl/torch-${TORCH}.html
#!pip install -q git+https://github.com/pyg-team/pytorch_geometric.git

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

!pip install torch-geometric
from torch_geometric.data import Data
from torch_geometric.nn import GATConv
from torch_geometric.datasets import Planetoid
import torch_geometric.transforms as T

import matplotlib.pyplot as plt

dataset = Planetoid(root= '/tmp/Cora', name = 'Cora')
dataset.transform = T.NormalizeFeatures()

print(f"Number of Classes in Cora:", dataset.num_classes)
print(f"Number of Node Features in Cora:", dataset.num_node_features)

class GAT(torch.nn.Module):
    def __init__(self):
        super(GAT, self).__init__()
        self.hid = 8
        self.in_head = 8
        self.out_head = 1


        self.conv1 = GATConv(dataset.num_features, self.hid, heads=self.in_head, dropout=0.6)
        self.conv2 = GATConv(self.hid*self.in_head, dataset.num_classes, concat=False,
                             heads=self.out_head, dropout=0.6)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)



device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = "cpu"

model = GAT().to(device)
data = dataset[0].to(device)


optimizer = torch.optim.Adam(model.parameters(), lr=0.005, weight_decay=5e-4)

model.train()
for epoch in range(1000):
    model.train()
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])

    if epoch%200 == 0:
        print(loss)

    loss.backward()
    optimizer.step()

model.eval()
_, pred = model(data).max(dim=1)
correct = float(pred[data.test_mask].eq(data.y[data.test_mask]).sum().item())
acc = correct / data.test_mask.sum().item()
print('Accuracy: {:.4f}'.format(acc))

#try node classification with the IMDB-Binary Dataset
from torch_geometric.datasets import TUDataset
pubmed_dataset = Planetoid(root='data/Planetoid', name='PubMed')

class GAT(torch.nn.Module):
    def __init__(self):
        super(GAT, self).__init__()
        self.hid = 8
        self.in_head = 8
        self.out_head = 1


        self.conv1 = GATConv(pubmed_dataset.num_features, self.hid, heads=self.in_head, dropout=0.6)
        self.conv2 = GATConv(self.hid*self.in_head, pubmed_dataset.num_classes, concat=False,
                             heads=self.out_head, dropout=0.6)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv1(x, edge_index)
        x = F.elu(x)
        x = F.dropout(x, p=0.6, training=self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)


pubmed_model = GAT().to(device)
pubmed_data = pubmed_dataset[0].to(device)

pubmed_model.train()

for epoch in range(1000):
    pubmed_model.train()
    optimizer.zero_grad()
    out = pubmed_model(pubmed_data)
    loss = F.nll_loss(out[pubmed_data.train_mask], pubmed_data.y[pubmed_data.train_mask])

    if epoch%200 == 0:
        print(loss)

    loss.backward()
    optimizer.step()

pubmed_model.eval()
_, pred = pubmed_model(pubmed_data).max(dim=1)
correct = float(pred[pubmed_data.test_mask].eq(pubmed_data.y[pubmed_data.test_mask]).sum().item())
acc = correct / data.test_mask.sum().item()
print('Accuracy: {:.4f}'.format(acc))
