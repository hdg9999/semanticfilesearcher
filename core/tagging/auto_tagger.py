from core.tagging.llm_adapters import LLMAdapter
import os

class AutoTagger:
    def __init__(self, adapter: LLMAdapter = None):
        self.adapter = adapter

    def set_adapter(self, adapter: LLMAdapter):
        self.adapter = adapter

    def generate_tags(self, file_path, existing_tags):
        if not self.adapter:
            return []
            
        # 1. 파일 유형에 따른 기본 설명 추출
        desc = self._get_content_summary(file_path)
        
        # 2. 어댑터를 통한 키워드 생성
        # 2. 어댑터를 통한 키워드 생성
        print(f"[AutoTagger] Generating tags for {file_path} using {self.adapter.__class__.__name__}")
        try:
            tags = self.adapter.generate_keywords(desc, existing_tags)
            print(f"[AutoTagger] Generated tags: {tags}")
            return tags
        except Exception as e:
            print(f"[AutoTagger] Error generating tags: {e}")
            return []

    def _get_content_summary(self, file_path):
        # 파일명과 확장자 기반의 간단한 요약 (실제로는 문서 일부 추출 가능)
        name = os.path.basename(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        return f"파일명: {name}, 확장자: {ext} 인 파일입니다."
