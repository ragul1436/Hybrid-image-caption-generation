
import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)

class TransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model=512, nhead=8, num_decoder_layers=6, dim_feedforward=2048, dropout=0.1, max_len=100):
        super(TransformerDecoder, self).__init__()
        
        self.d_model = d_model
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout, max_len=max_len)
        
        decoder_layer = nn.TransformerDecoderLayer(d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, dropout=dropout)
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_decoder_layers)
        
        self.fc_out = nn.Linear(d_model, vocab_size)
        self.dropout = nn.Dropout(dropout)
        
        self.max_len = max_len

    def forward(self, features, captions, tgt_mask=None, tgt_key_padding_mask=None):
        """
        features: (batch_size, embed_size) - from CNN Encoder
        captions: (batch_size, seq_length) - target captions (integers)
        """
        # Embed captions
        # captions shape: (batch_size, seq_len) -> (seq_len, batch_size) for transformer
        embeddings = self.embedding(captions).permute(1, 0, 2) # (seq_len, batch, d_model)
        embeddings = self.pos_encoder(embeddings)
        
        # Features shape: (batch_size, d_model) -> (1, batch_size, d_model)
        # We treat the image feature as a memory key/value for the decoder
        features = features.unsqueeze(0) 
        
        output = self.transformer_decoder(
            tgt=embeddings, 
            memory=features, 
            tgt_mask=tgt_mask, 
            tgt_key_padding_mask=tgt_key_padding_mask
        ) # (seq_len, batch, d_model)
        
        # Project to vocab size
        output = self.fc_out(output) # (seq_len, batch, vocab_size)
        
        return output
    
    def generate_caption(self, features, vocab, max_len=20, device='cpu', method='beam_search', beam_width=5):
        # Implementation of generation logic (greedy or beam search)
        # This is a placeholder for the complex generation loop
        # In a real scenario, this would loop token by token
        pass

class LSTMDecoder(nn.Module):
    # Fallback LSTM
    pass
