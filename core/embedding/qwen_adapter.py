import torch
from transformers import AutoModel, AutoProcessor
from PIL import Image
from core.embedding.adapter import EmbeddingAdapter
import numpy as np

class QwenEmbeddingAdapter(EmbeddingAdapter):
    def __init__(self, model_name="Qwen/Qwen3-VL-Embedding-2B"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.default_instruction = "Represent the user's input."
        
        # 실제 모델 로드는 필요할 때 하거나 초기화 시 진행 (메모리 고려)
        print(f"Loading {model_name} on {self.device}...")
        
        # transformers 5.2.0 버그 우회 패치: NoneType 반복 에러 방지
        try:
            import transformers.models.auto.video_processing_auto as vpa
            if not hasattr(vpa, '_patched_for_qwen'):
                original_get = vpa.video_processor_class_from_name
                def patched_get(class_name):
                    # vpa.VIDEO_PROCESSOR_MAPPING_NAMES 내 None 값을 빈 문자열로 처리하여 'in' 구문 에러 방지
                    if hasattr(vpa, 'VIDEO_PROCESSOR_MAPPING_NAMES'):
                        for k, v in vpa.VIDEO_PROCESSOR_MAPPING_NAMES.items():
                            if v is None:
                                vpa.VIDEO_PROCESSOR_MAPPING_NAMES[k] = ""
                    return original_get(class_name)
                vpa.video_processor_class_from_name = patched_get
                vpa._patched_for_qwen = True
        except Exception:
            pass

        # 임베딩 전용 모델이므로 trust_remote_code가 필요할 수 있음
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True, padding_side='right')
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.model.eval()

    @staticmethod
    def _pooling_last(hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        flipped_tensor = attention_mask.flip(dims=[1])
        last_one_positions = flipped_tensor.argmax(dim=1)
        col = attention_mask.shape[1] - last_one_positions - 1
        row = torch.arange(hidden_state.shape[0], device=hidden_state.device)
        return hidden_state[row, col]

    def encode_text(self, text):
        if isinstance(text, str): text = [text]
        
        embeddings_list = []
        for t in text:
            conversation = [
                {"role": "system", "content": [{"type": "text", "text": self.default_instruction}]},
                {"role": "user", "content": [{'type': 'text', 'text': t}]}
            ]
            
            text_prompt = self.processor.apply_chat_template(
                conversation, add_generation_prompt=True, tokenize=False
            )
            
            inputs = self.processor(
                text=[text_prompt], padding=True, return_tensors='pt'
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                emb = self._pooling_last(outputs.last_hidden_state, inputs.attention_mask)
            
            emb = emb.to(torch.float32).cpu().numpy().squeeze()
            if emb.ndim == 0: emb = np.expand_dims(emb, 0)
            elif emb.ndim > 1: emb = emb.flatten()
            embeddings_list.append(emb)
            
        return np.array(embeddings_list)

    def encode_image(self, image_path):
        if isinstance(image_path, str): image_paths = [image_path]
        else: image_paths = image_path

        embeddings_list = []
        for path in image_paths:
            try:
                img = Image.open(path).convert('RGB')
                conversation = [
                    {"role": "system", "content": [{"type": "text", "text": self.default_instruction}]},
                    {"role": "user", "content": [{'type': 'image', 'image': img}]}
                ]
                
                text_prompt = self.processor.apply_chat_template(
                    conversation, add_generation_prompt=True, tokenize=False
                )
                
                inputs = self.processor(
                    text=[text_prompt], images=[img], padding=True, return_tensors='pt'
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    emb = self._pooling_last(outputs.last_hidden_state, inputs.attention_mask)
                
                emb = emb.to(torch.float32).cpu().numpy().squeeze()
                if emb.ndim == 0: emb = np.expand_dims(emb, 0)
                elif emb.ndim > 1: emb = emb.flatten()
                
                embeddings_list.append(emb)
            except Exception as e:
                print(f"Error encoding image {path} with model: {e}")
                stub_emb = np.random.randn(self.dimension).astype('float32')
                embeddings_list.append(stub_emb)
            
        return np.array(embeddings_list)

    @property
    def dimension(self) -> int:
        if "8B" in self.model_name:
            return 4096
        return 2048
