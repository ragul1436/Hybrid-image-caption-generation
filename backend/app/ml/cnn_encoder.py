
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights

class CNNEncoder(nn.Module):
    def __init__(self, embed_size=512):
        super(CNNEncoder, self).__init__()
        # Load pretrained ResNet50
        resnet = models.resnet50(weights=ResNet50_Weights.DEFAULT)
        
        # Remove the last fully connected layer (classification layer)
        modules = list(resnet.children())[:-1] 
        self.resnet = nn.Sequential(*modules)
        
        # Add a final linear layer to project to embedding size
        # ResNet50 output size before FC is 2048
        self.embed = nn.Linear(resnet.fc.in_features, embed_size)
        self.bn = nn.BatchNorm1d(embed_size, momentum=0.01)

    def forward(self, images):
        # images shape: (batch_size, 3, 224, 224)
        with torch.no_grad():
            features = self.resnet(images) # (batch_size, 2048, 1, 1)
        
        features = features.reshape(features.size(0), -1) # (batch_size, 2048)
        features = self.embed(features) # (batch_size, embed_size)
        features = self.bn(features)
        
        return features

class ViTEncoder(nn.Module):
    # Alternative: ViT-Base/16
    def __init__(self, embed_size=512):
        super(ViTEncoder, self).__init__()
        self.vit = models.vit_b_16(weights='DEFAULT')
        self.embed = nn.Linear(768, embed_size) # ViT base has 768 hidden size
    
    def forward(self, images):
        # ... logic for ViT ...
        pass
