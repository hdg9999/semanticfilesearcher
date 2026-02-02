import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
from core.embedding.adapter import EmbeddingAdapter
import numpy as np

class QwenEmbeddingAdapter(EmbeddingAdapter):
    def __init__(self, model_name="Qwen/Qwen3-VL-Embedding-2B"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 실제 모델 로드는 필요할 때 하거나 초기화 시 진행 (메모리 고려)
        print(f"Loading {model_name} on {self.device}...")
        # 임베딩 전용 모델이므로 trust_remote_code가 필요할 수 있음
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(model_name, trust_remote_code=True).to(self.device)
        self.model.eval()

    def encode_text(self, text):
        if isinstance(text, str): text = [text]
        
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            # 보통 last_hidden_state의 mean pooling 또는 CLS 토큰 사용
            embeddings = outputs.last_hidden_state.mean(dim=1)
        
        return embeddings.to(torch.float32).cpu().numpy()

    def encode_image(self, image_path):
        if isinstance(image_path, str): image_paths = [image_path]
        else: image_paths = image_path

        # Qwen3-VL-Embedding은 멀티모달 입력을 지원함
        # 구체적인 전처리 방식은 모델 카드 및 관련 라이브러리 참조 필요
        # 여기서는 추상적인 개념 구현을 목표로 함
        embeddings_list = []
        for path in image_paths:
            img = Image.open(path).convert('RGB')
            # 모델의 멀티모달 프로세서가 있을 경우 사용 (예: Qwen2-VL-Processor)
            # 여기서는 텍스트와 동일한 forward 인터페이스를 사용한다고 가정하거나 전처리 로직 포함
            # inputs = self.processor(images=img, return_tensors="pt").to(self.device)
            # outputs = self.model.get_image_features(**inputs)
            
            # 임시 스텁 (실제 구현 시 모델별 가이드라인 준수)
            stub_emb = np.random.randn(self.dimension).astype('float32')
            embeddings_list.append(stub_emb)
            
        return np.array(embeddings_list)

    @property
    def dimension(self) -> int:
        # Qwen3-VL-Embedding-2B의 기본 차원은 2048 (설정에 따라 가변 가능)
        return 2048
