
import os
import torch
from backend.app.ml.cnn_encoder import CNNEncoder
from backend.app.ml.transformer_decoder import TransformerDecoder
from transformers import BlipProcessor, BlipForConditionalGeneration

class ModelLoader:
    _instance = None
    
    # Cache models
    blip_processor = None
    blip_model = None
    cnn_encoder = None
    transformer_decoder = None
    vocab = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_blip(self):
        if self.blip_model is None:
            print("Loading BLIP model...")
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            # Move to GPU if available
            self.blip_model.to("cuda" if torch.cuda.is_available() else "cpu")
            print("BLIP model loaded.")
        return self.blip_processor, self.blip_model

    def load_custom_model(self, encoder_path: str, decoder_path: str, vocab_path: str):
        # Placeholder for loading custom .pt checkpoints
        # In a real app, you'd load the state_dict here
        if self.cnn_encoder is None:
            print(f"Loading custom model from {encoder_path}...")
            # self.cnn_encoder = CNNEncoder(...)
            # self.transformer_decoder = TransformerDecoder(...)
            # self.cnn_encoder.load_state_dict(torch.load(encoder_path))
            # self.transformer_decoder.load_state_dict(torch.load(decoder_path))
            pass
        return self.cnn_encoder, self.transformer_decoder

    def get_model(self, model_name: str):
        if model_name.lower() == "blip":
            return self.load_blip()
        elif model_name.lower() == "custom":
            # return self.load_custom_model(...)
            pass
        else:
            raise ValueError(f"Unknown model: {model_name}")

loader = ModelLoader.get_instance()
