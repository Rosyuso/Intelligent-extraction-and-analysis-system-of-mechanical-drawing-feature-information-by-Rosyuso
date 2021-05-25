import torch
state_dict = torch.load('TPS-ResNet-BiLSTM-Attn.pth',map_location=torch.device('cpu'))
for name, weights in state_dict.items():
    print(name, weights.size())  #可以查看模型中的模型名字和权重维度