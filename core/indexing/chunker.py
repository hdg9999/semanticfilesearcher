import re

class TextChunker:
    """
    텍스트를 최대 토큰(문자) 수에 맞게 분할하는 유틸리티 클래스입니다.
    기본적으로 단락, 줄바꿈, 문장, 단어 단위로 쪼개며, 지정된 chunk_size 이하가 되도록 합니다.
    """
    def __init__(self, chunk_size=1500, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # 분할 우선순위: 문단(이중 줄바꿈) -> 줄바꿈 -> 문장 기호 -> 띄어쓰기 -> 글자
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def split_text(self, text):
        """텍스트를 입력받아 청크 문자열 리스트를 반환합니다."""
        if not text:
            return []
        
        return self._split_text(text, self.separators)

    def _split_text(self, text, separators):
        # 텍스트가 청크 사이즈 내에 들어온다면 그대로 반환
        if len(text) <= self.chunk_size:
            return [text]

        # 사용할 구분자 선택
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            if _s == "":
                separator = _s
                break
            if _s in text:
                separator = _s
                new_separators = separators[i + 1:]
                break

        # 구분자로 텍스트 분할
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # 한 글자씩 분할

        # 쪼갠 조각들을 사이즈에 맞춰 병합
        good_splits = []
        for s in splits:
            if s:
                good_splits.append(s)

        chunks = []
        current_chunk = []
        current_length = 0

        for s in good_splits:
            s_len = len(s) + (len(separator) if current_length > 0 else 0)
            
            # 현재 조각 자체가 chunk_size보다 크면 더 작은 구분자로 재귀 분할
            if s_len > self.chunk_size and new_separators:
                # 현재까지 모은 게 있으면 추가
                if current_chunk:
                    chunk_text = separator.join(current_chunk)
                    chunks.append(chunk_text)
                    current_chunk = []
                    current_length = 0
                
                # 큰 조각 재귀 분할
                sub_chunks = self._split_text(s, new_separators)
                chunks.extend(sub_chunks)
                continue

            # 조각을 더했을 때 한계치를 초과하면 현재 청크를 확정
            if current_length + s_len > self.chunk_size and current_chunk:
                chunk_text = separator.join(current_chunk)
                chunks.append(chunk_text)
                
                # Overlap만큼 유지하기 위해 끝에서부터 채움
                overlap_length = 0
                overlap_chunk = []
                for chunk_part in reversed(current_chunk):
                    part_len = len(chunk_part) + (len(separator) if overlap_length > 0 else 0)
                    if overlap_length + part_len <= self.chunk_overlap:
                        overlap_chunk.insert(0, chunk_part)
                        overlap_length += part_len
                    else:
                        break
                
                current_chunk = overlap_chunk
                current_length = overlap_length

            current_chunk.append(s)
            current_length += len(s) + (len(separator) if len(current_chunk) > 1 else 0)

        # 남은 청크 처리
        if current_chunk:
            chunk_text = separator.join(current_chunk)
            chunks.append(chunk_text)

        return chunks
