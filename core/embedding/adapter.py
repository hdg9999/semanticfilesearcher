from abc import ABC, abstractmethod
import numpy as np
from typing import List, Union

class EmbeddingAdapter(ABC):
    """
    임베딩 모델을 위한 추상화 인터페이스.
    향후 모델 교체 시 이 클래스를 상속받아 구현함으로써 유연성을 확보합니다.
    """
    
    @abstractmethod
    def encode_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """텍스트를 벡터로 변환합니다."""
        pass
    
    @abstractmethod
    def encode_image(self, image_path: Union[str, List[str]]) -> np.ndarray:
        """이미지 파일을 벡터로 변환합니다."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """모델의 출력 벡터 차원 수를 반환합니다."""
        pass
