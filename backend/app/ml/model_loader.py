
import os
import torch
import logging
from backend.app.ml.cnn_encoder import CNNEncoder
from backend.app.ml.transformer_decoder import TransformerDecoder
from transformers import BlipProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)

class ModelLoader:
    _instance = None
    
    # Cache models
    blip_processor = None
    blip_model = None
    cnn_encoder = None
    transformer_decoder = None
    vocab = None
    load_error = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_blip(self):
        if self.blip_model is None:
            if self.load_error:
                raise RuntimeError(f"Previous model load failed: {self.load_error}")
            
            try:
                logger.info("Loading BLIP model (this may take 1-2 minutes on first load)...")
                # Set environment variables to reduce memory usage
                os.environ['TORCH_HOME'] = '/app/cache'
                os.environ['HF_HOME'] = '/app/cache'
                
                # Reduce memory footprint
                import torch
                torch.set_float32_matmul_precision('medium')
                
                self.blip_processor = BlipProcessor.from_pretrained(
                    "Salesforce/blip-image-captioning-base",
                    cache_dir="/app/cache"
                )
                self.blip_model = BlipForConditionalGeneration.from_pretrained(
                    "Salesforce/blip-image-captioning-base",
                    cache_dir="/app/cache"
                )
                # Move to GPU if available, otherwise keep on CPU
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.blip_model.to(device)
                self.blip_model.eval()  # Set to eval mode
                logger.info(f"BLIP model loaded successfully on {device}")
            except Exception as e:
                self.load_error = str(e)
                logger.error(f"Failed to load BLIP model: {e}", exc_info=True)
                raise ValueError(f"Failed to load BLIP model: {e}")
        
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
