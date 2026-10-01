# [역할] 따옴표로 감싸진 공백 포함 문자열 및 CLI 인자를 파싱하기 위해 shlex 모듈을 임포트합니다.
import shlex

# [역할] 시스템 종료(sys.exit) 및 표준 에러/출력 보조를 위해 sys 모듈을 임포트합니다.
import sys

# [역할] 커밋 생성 시점의 타임스탬프를 기록하기 위해 datetime 모듈을 임포트합니다.
import datetime

# [역할] 최단 경로(BFS) 및 조상 탐색 큐 자료구조를 위해 deque를 임포트합니다.
from collections import deque

# [역할] 정렬 성능 벤치마크 시간 측정을 위해 time 모듈을 임포트합니다.
import time

# [역할] 커밋 해시 무작위 시드 보조를 위해 random 모듈을 임포트합니다.
import random


# ==========================================
# Commit Node Data Structure
# ==========================================
class Commit:
    """
    [역할] Git의 단일 커밋 노드를 표현하는 클래스입니다.
    [필드]
      - hash: 커밋의 고유 해시 식별자 (문자열)
      - message: 커밋 메시지 (문자열)
      - author: 커밋 작성자 이름 (문자열)
      - timestamp: 커밋 생성 일시 (datetime 객체)
      - parents: 부모 커밋의 해시 목록 (list[str])
    """
    def __init__(self, commit_hash: str, message: str, author: str, timestamp: datetime.datetime, parents: list):
        # [역할] 커밋의 고유 식별자 해시값을 인스턴스 변수에 저장합니다.
        self.hash = commit_hash
        # [역할] 커밋 메시지 문자열을 인스턴스 변수에 저장합니다.
        self.message = message
        # [역할] 커밋 작성자 이름을 인스턴스 변수에 저장합니다.
        self.author = author
        # [역할] 커밋 생성 일시(datetime 객체)를 인스턴스 변수에 저장합니다.
        self.timestamp = timestamp
        # [역할] 부모 커밋들의 해시 리스트를 복사하여 인스턴스 변수에 저장합니다.
        self.parents = list(parents)

    def __repr__(self):
        # [역할] 디버깅 및 객체 출력 시 식별 가능한 문자열을 반환합니다.
        return f"<Commit {self.hash}: {self.message}>"


# ==========================================
# Custom Sorting Algorithm (Merge Sort)
# [제약 준수] sorted(), list.sort() 사용 금지
# ==========================================
def merge_sort(items: list, key_func=lambda x: x) -> list:
    """
    [역할] 분할 정복(Divide and Conquer) 방식의 병합 정렬(Merge Sort)을 직접 구현합니다.
    [특징] O(N log N) 시간 복잡도를 보장하며, 동률 원소의 원래 순서를 보존하는 안정 정렬(Stable Sort)입니다.
    [인자]
      - items: 정렬할 대상 리스트
      - key_func: 비교 기준 키를 추출하는 람다/함수
    [반환] 정렬된 새로운 리스트
    """
    # [상태 검사] 원소 개수가 1개 이하이면 이미 정렬된 상태이므로 복사본을 반환하고 재귀를 종료합니다.
    if len(items) <= 1:
        return list(items)

    # [분할] 리스트의 중간 지점 인덱스를 계산합니다.
    mid = len(items) // 2

    # [재귀 호출] 왼쪽 절반을 재귀적으로 병합 정렬합니다.
    left_sorted = merge_sort(items[:mid], key_func)

    # [재귀 호출] 오른쪽 절반을 재귀적으로 병합 정렬합니다.
    right_sorted = merge_sort(items[mid:], key_func)

    # [병합] 정렬된 두 부분 리스트를 순서대로 병합할 빈 리스트를 생성합니다.
    merged = []
    # [포인터] 왼쪽 리스트 탐색용 인덱스 포인터입니다.
    left_idx = 0
    # [포인터] 오른쪽 리스트 탐색용 인덱스 포인터입니다.
    right_idx = 0

    # [비교 병합] 양쪽 리스트에 원소가 남아있는 동안 비교하며 더 작은 원소를 merged에 추가합니다.
    while left_idx < len(left_sorted) and right_idx < len(right_sorted):
        # [안정 정렬 보장] <= 연산자를 사용하여 값이 같을 경우 왼쪽(앞선 순서)의 원소를 우선 배치합니다.
        if key_func(left_sorted[left_idx]) <= key_func(right_sorted[right_idx]):
            merged.append(left_sorted[left_idx])
            left_idx += 1
        else:
            merged.append(right_sorted[right_idx])
            right_idx += 1

    # [잔여 원소 처리] 왼쪽 리스트에 남은 원소들을 뒤에 추가합니다.
    while left_idx < len(left_sorted):
        merged.append(left_sorted[left_idx])
        left_idx += 1

    # [잔여 원소 처리] 오른쪽 리스트에 남은 원소들을 뒤에 추가합니다.
    while right_idx < len(right_sorted):
        merged.append(right_sorted[right_idx])
        right_idx += 1

    # [반환] 최종 정렬된 리스트를 반환합니다.
    return merged


# ==========================================
# Inverted Index (역색인 시스템)
# ==========================================
class InvertedIndex:
    """
    [역할] 커밋 메시지 키워드 및 작성자 기반으로 커밋 해시를 O(1) 수준으로 조회할 수 있는 역색인 테이블입니다.
    """
    def __init__(self):
        # [역할] 소문자 단어 토큰 -> 커밋 해시 리스트 매핑 해시맵
        self.keyword_index = {}
        # [역할] 작성자 이름(소문자) -> 커밋 해시 리스트 매핑 해시맵
        self.author_index = {}

    def index_commit(self, commit: Commit):
        """
        [역할] 새 커밋 노드를 역색인 테이블에 등록합니다.
        """
        # [키워드 토큰화] 커밋 메시지를 공백 기준으로 분리하고 소문자로 정규화합니다.
        tokens = commit.message.strip().split()
        seen_tokens = set()

        for token in tokens:
            # [정규화] 소문자로 변환하고 양 끝 문장부호를 제거합니다.
            clean_token = token.lower().strip(".,!?:;\"'()[]{}")
            # [유효성 검사] 정제된 토큰이 비어있거나 한 커밋 내에서 이미 처리된 토큰이면 중복 방지를 위해 건너뜁니다.
            if not clean_token or clean_token in seen_tokens:
                continue
            seen_tokens.add(clean_token)

            # [인덱스 갱신] 해당 키워드 엔트리가 없으면 빈 리스트를 생성합니다.
            if clean_token not in self.keyword_index:
                self.keyword_index[clean_token] = []
            # [해시 등록] 키워드 리스트에 커밋 해시를 추가합니다.
            self.keyword_index[clean_token].append(commit.hash)

        # [작성자 인덱싱] 작성자명을 소문자로 변환하여 색인합니다.
        author_key = commit.author.lower().strip()
        if author_key not in self.author_index:
            self.author_index[author_key] = []
        self.author_index[author_key].append(commit.hash)

    def search_by_keyword(self, keyword: str) -> list:
        """
        [역할] 키워드로 역색인 테이블을 조회하여 매칭되는 커밋 해시 목록을 반환합니다.
        """
        clean_key = keyword.lower().strip()
        return list(self.keyword_index.get(clean_key, []))

    def search_by_author(self, author: str) -> list:
        """
        [역할] 작성자명으로 역색인 테이블을 조회하여 매칭되는 커밋 해시 목록을 반환합니다.
        """
        clean_author = author.lower().strip()
        return list(self.author_index.get(clean_author, []))


# ==========================================
# Mini Git Engine (핵심 엔진)
# ==========================================
class MiniGitEngine:
    """
    [역할] Git의 커밋 그래프(DAG), 브랜치, HEAD, 역색인 및 그래프 탐색 알고리즘을 총괄하는 코어 엔진입니다.
    """
    def __init__(self):
        # [역할] 저장소 초기화 여부 플래그
        self.is_initialized = False
        # [역할] 현재 활성 사용자 이름
        self.current_user = None
        # [역할] 현재 체크아웃된 브랜치 이름
        self.current_branch = None
        # [역할] 브랜치 이름 -> 최신 커밋 해시 매핑 딕셔너리
        self.branches = {}
        # [역할] 커밋 해시 -> Commit 객체 매핑 딕셔너리 (O(1) 커밋 조회)
        self.commits = {}
        # [역할] 고유 커밋 해시 발급을 위한 순차 시퀀스 카운터
        self.hash_counter = 0
        # [역할] 역색인 인스턴스 생성
        self.inverted_index = InvertedIndex()

    def generate_hash(self) -> str:
        """
        [역할] 세션 내에서 절대 중복되지 않는 고유 커밋 해시 문자열을 생성합니다.
        """
        self.hash_counter += 1
        # [형식] 카운터 기반 16진수 및 시드 기반 6자리 고유 해시 포맷을 생성합니다.
        random_suffix = random.randint(0x1000, 0xFFFF)
        return f"{self.hash_counter:02x}{random_suffix:04x}"

    def init_repository(self, user_name: str) -> str:
        """
        [역할] INIT 명령을 수행하여 저장소를 초기화하고 main 브랜치를 세팅합니다.
        """
        self.is_initialized = True
        self.current_user = user_name
        self.current_branch = "main"
        # [초기 상태] main 브랜치는 아직 커밋이 없으므로 None을 가리킵니다.
        self.branches = {"main": None}
        self.commits.clear()
        self.hash_counter = 0
        self.inverted_index = InvertedIndex()
        return (
            f"Initialized repository.\n"
            f"Current branch: {self.current_branch}\n"
            f"Current user: {self.current_user}"
        )

    def create_branch(self, branch_name: str) -> str:
        """
        [역할] 현재 HEAD가 가리키는 커밋을 기준으로 새 브랜치를 생성합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."
        if branch_name in self.branches:
            return f"Error: Branch already exists: {branch_name}"

        # [상태 반영] 현재 브랜치의 최신 커밋 해시를 그대로 새 브랜치에 복사합니다.
        current_commit_hash = self.branches.get(self.current_branch)
        self.branches[branch_name] = current_commit_hash
        return f"Created branch: {branch_name}"

    def switch_branch(self, branch_name: str) -> str:
        """
        [역할] HEAD를 다른 브랜치로 전환합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."
        if branch_name not in self.branches:
            return f"Unknown branch: {branch_name}"

        self.current_branch = branch_name
        return f"Switched to branch: {branch_name}"

    def commit(self, message: str, extra_parents: list = None) -> str:
        """
        [역할] 새 커밋 노드를 생성하여 DAG에 등록하고 브랜치 포인터를 전진시킵니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."

        # [부모 결정] 현재 체크아웃된 브랜치의 최신 커밋이 첫 번째 부모가 됩니다.
        head_commit_hash = self.branches.get(self.current_branch)
        parents = []
        if head_commit_hash is not None:
            parents.append(head_commit_hash)

        # [머지 커밋 부모 추가] extra_parents가 제공된 경우 병합 대상 부모를 추가합니다.
        if extra_parents:
            for p in extra_parents:
                if p not in parents:
                    parents.append(p)

        # [노드 생성] 고유 해시를 발급받고 커밋 노드 객체를 조립합니다.
        new_hash = self.generate_hash()
        timestamp = datetime.datetime.now()
        new_commit = Commit(new_hash, message, self.current_user, timestamp, parents)

        # [저장소 및 인덱스 등록]
        self.commits[new_hash] = new_commit
        self.inverted_index.index_commit(new_commit)

        # [브랜치 전진] 현재 브랜치 헤드가 새 커밋을 가리키도록 갱신합니다.
        self.branches[self.current_branch] = new_hash

        return f"[{self.current_branch} {new_hash}] {message}"

    def get_topological_log(self) -> list:
        """
        [역할] 위상 정렬(Topological Sort, Kahn's 알고리즘 변형)을 수행하여
               부모 커밋이 자식 커밋보다 항상 먼저 출력되는 커밋 목록을 생성합니다.
        """
        if not self.commits:
            return []

        # [진입 차수(in-degree) 계산] 부모 -> 자식 방향 그래프로 간주할 때 자식이 부모의 완료를 대기해야 합니다.
        # 각 커밋이 선행되어야 하는 부모 커밋의 수를 in_degree로 정의합니다.
        in_degree = {chash: len(commit.parents) for chash, commit in self.commits.items()}

        # [자식 인접 리스트 생성] parent -> list of children
        children_map = {chash: [] for chash in self.commits}
        for chash, commit in self.commits.items():
            for p in commit.parents:
                if p in children_map:
                    children_map[p].append(chash)

        # [큐 초기화] 부모가 없는 루트 커밋(in_degree == 0)들을 수집합니다.
        # 동일 레벨 안정성을 위해 타임스탬프 순으로 정렬합니다.
        zero_in_degree = [chash for chash, deg in in_degree.items() if deg == 0]
        zero_in_degree = merge_sort(zero_in_degree, key_func=lambda h: self.commits[h].timestamp)

        queue = deque(zero_in_degree)
        sorted_commits = []

        # [위상 정렬 루프]
        while queue:
            current_hash = queue.popleft()
            sorted_commits.append(self.commits[current_hash])

            # [자식 노드 진입 차수 감소]
            for child_hash in children_map[current_hash]:
                in_degree[child_hash] -= 1
                if in_degree[child_hash] == 0:
                    queue.append(child_hash)

        return sorted_commits

    def format_commit(self, commit: Commit) -> str:
        """
        [역할] 커밋 정보를 화면에 출력하기 위한 표준 포맷 문자열로 변환합니다.
        """
        time_str = commit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        # [브랜치 태그 확인] 어떤 브랜치들이 이 커밋을 가리키고 있는지 태그로 부착합니다.
        pointing_branches = [b for b, h in self.branches.items() if h == commit.hash]
        branch_tag = f" [{', '.join(pointing_branches)}]" if pointing_branches else ""
        return (
            f"commit {commit.hash} ({commit.author}, {time_str}){branch_tag}\n"
            f"    {commit.message}"
        )

    def log(self, sort_by: str = None) -> str:
        """
        [역할] LOG 명령을 수행합니다. sort_by 옵션 유무에 따라 위상 정렬 또는 커스텀 정렬 결과를 반환합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."
        if not self.commits:
            return "No commits yet."

        if sort_by == "date":
            # [타임스탬프 기준 Merge Sort]
            all_commits = list(self.commits.values())
            sorted_list = merge_sort(all_commits, key_func=lambda c: c.timestamp)
        elif sort_by == "author":
            # [작성자 이름 기준 Merge Sort]
            all_commits = list(self.commits.values())
            sorted_list = merge_sort(all_commits, key_func=lambda c: (c.author.lower(), c.timestamp))
        elif sort_by is None:
            # [기본: 부모 커밋이 먼저 오는 위상 정렬 순서]
            sorted_list = self.get_topological_log()
        else:
            return f"Invalid sort option: {sort_by}. Use 'date' or 'author'."

        return "\n".join(self.format_commit(c) for c in sorted_list)

    def get_ancestors(self, start_hash: str) -> list:
        """
        [역할] ANCESTORS 명령을 위해 주어진 커밋의 모든 조상 커밋(부모의 부모 등)을 BFS로 탐색하여 반환합니다.
        """
        if start_hash not in self.commits:
            return None

        ancestors = []
        visited = set()
        queue = deque([start_hash])
        visited.add(start_hash)

        while queue:
            curr = queue.popleft()
            commit = self.commits.get(curr)
            if not commit:
                continue

            for parent_hash in commit.parents:
                if parent_hash in self.commits and parent_hash not in visited:
                    visited.add(parent_hash)
                    ancestors.append(self.commits[parent_hash])
                    queue.append(parent_hash)

        # [출력 정렬] 조상 목록을 타임스탬프 순서대로 정렬하여 반환합니다.
        return merge_sort(ancestors, key_func=lambda c: c.timestamp)

    def find_shortest_path(self, start_hash: str, end_hash: str) -> str:
        """
        [역할] 부모-자식 간선을 무방향 간선으로 취급하여 두 커밋 간의 최단 경로(간선 수 최소)를 BFS로 탐색합니다.
        [동률 처리] 최단 경로가 여러 개일 경우 "hash1->hash2->..." 문자열 기준 사전순 최소 경로를 선택합니다.
        """
        if start_hash not in self.commits:
            return f"Unknown commit: {start_hash}"
        if end_hash not in self.commits:
            return f"Unknown commit: {end_hash}"

        if start_hash == end_hash:
            return f"Path: {start_hash}"

        # [무방향 인접 리스트 구축]
        adj = {h: set() for h in self.commits}
        for h, commit in self.commits.items():
            for p in commit.parents:
                if p in adj:
                    adj[h].add(p)
                    adj[p].add(h)

        # [BFS 큐 세팅] queue 원소: (현재_노드, 현재까지의_경로_리스트)
        queue = deque([(start_hash, [start_hash])])
        # [최소 거리 기록 맵] 노드별 최소 도달 거리를 기록하여 동일 레벨 복수 경로를 추적합니다.
        dist_map = {start_hash: 0}
        found_paths = []
        shortest_length = None

        while queue:
            curr, path = queue.popleft()
            curr_dist = len(path) - 1

            # [가지치기] 이미 발견된 최단 경로보다 더 긴 경로는 탐색 중단
            if shortest_length is not None and curr_dist > shortest_length:
                break

            if curr == end_hash:
                shortest_length = curr_dist
                found_paths.append("->".join(path))
                continue

            # [이웃 노드 확장]
            for neighbor in adj[curr]:
                next_dist = curr_dist + 1
                if neighbor not in dist_map or dist_map[neighbor] == next_dist:
                    dist_map[neighbor] = next_dist
                    queue.append((neighbor, path + [neighbor]))

        if not found_paths:
            return "No path"

        # [사전순 최소 경로 선택] merge_sort를 활용하여 사전순 가장 앞선 경로 문자열 선택
        sorted_paths = merge_sort(found_paths, key_func=lambda p: p)
        return f"Path: {sorted_paths[0]}"

    def search_keyword(self, keyword: str) -> str:
        """
        [역할] SEARCH <keyword> 명령을 처리합니다. 역색인을 사용하여 즉시 검색합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."

        matched_hashes = self.inverted_index.search_by_keyword(keyword)
        if not matched_hashes:
            return f"No commits found with keyword: '{keyword}'"

        commits = [self.commits[h] for h in matched_hashes if h in self.commits]
        sorted_commits = merge_sort(commits, key_func=lambda c: c.timestamp)

        result = [f"Found {len(sorted_commits)} commit(s):"]
        for c in sorted_commits:
            result.append(f"- {c.hash}: {c.message} (by {c.author})")
        return "\n".join(result)

    def search_author(self, author: str) -> str:
        """
        [역할] SEARCH --author=<name> 명령을 처리합니다. 역색인을 사용하여 즉시 검색합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."

        matched_hashes = self.inverted_index.search_by_author(author)
        if not matched_hashes:
            return f"No commits found by author: '{author}'"

        commits = [self.commits[h] for h in matched_hashes if h in self.commits]
        sorted_commits = merge_sort(commits, key_func=lambda c: c.timestamp)

        result = [f"Found {len(sorted_commits)} commit(s) by {author}:"]
        for c in sorted_commits:
            result.append(f"- {c.hash}: {c.message} [{c.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
        return "\n".join(result)

    def merge_branch(self, target_branch: str) -> str:
        """
        [보너스 과제] 대상 브랜치를 현재 활성 브랜치로 병합하고 부모가 2개인 머지 커밋을 생성합니다.
        """
        if not self.is_initialized:
            return "Error: Repository not initialized. Run INIT first."
        if target_branch not in self.branches:
            return f"Unknown branch: {target_branch}"
        if target_branch == self.current_branch:
            return "Cannot merge branch into itself."

        target_commit_hash = self.branches[target_branch]
        if target_commit_hash is None:
            return f"Branch '{target_branch}' has no commits to merge."

        current_head = self.branches[self.current_branch]
        if current_head == target_commit_hash:
            return "Already up to date."

        # [머지 커밋 생성] 두 브랜치의 최신 커밋을 부모로 설정합니다.
        merge_msg = f"Merge branch '{target_branch}' into {self.current_branch}"
        return self.commit(merge_msg, extra_parents=[target_commit_hash])


# ==========================================
# Bonus Utilities: Simple Diff & Benchmark
# ==========================================
def simple_diff(file1_path: str, file2_path: str) -> str:
    """
    [보너스 과제] 두 텍스트 파일을 줄 단위로 비교하여 추가(+), 삭제(-), 공통( ) 줄을 출력합니다.
    """
    try:
        with open(file1_path, "r", encoding="utf-8") as f1:
            lines1 = f1.readlines()
        with open(file2_path, "r", encoding="utf-8") as f2:
            lines2 = f2.readlines()
    except Exception as e:
        return f"Error reading files: {e}"

    output = []
    max_len = max(len(lines1), len(lines2))
    for i in range(max_len):
        l1 = lines1[i].rstrip("\r\n") if i < len(lines1) else None
        l2 = lines2[i].rstrip("\r\n") if i < len(lines2) else None

        if l1 == l2:
            output.append(f"  {l1}")
        else:
            if l1 is not None:
                output.append(f"- {l1}")
            if l2 is not None:
                output.append(f"+ {l2}")
    return "\n".join(output)


def benchmark_sorts(n_elements: int = 2000) -> str:
    """
    [보너스 과제] 직접 구현한 병합 정렬(Merge Sort)과 버블 정렬(Bubble Sort)의 실행 시간을 비교합니다.
    """
    import random
    raw_data = [random.randint(1, 100000) for _ in range(n_elements)]

    # 1. 병합 정렬 측정 (O(N log N))
    start_time = time.perf_counter()
    merge_sort(list(raw_data))
    merge_duration = time.perf_counter() - start_time

    # 2. 버블 정렬 구현 및 측정 (O(N^2))
    def bubble_sort(arr):
        a = list(arr)
        n = len(a)
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if a[j] > a[j + 1]:
                    a[j], a[j + 1] = a[j + 1], a[j]
                    swapped = True
            if not swapped:
                break
        return a

    start_time = time.perf_counter()
    bubble_sort(raw_data)
    bubble_duration = time.perf_counter() - start_time

    return (
        f"[Sort Benchmark - N={n_elements}]\n"
        f"- Merge Sort (O(N log N)): {merge_duration:.6f} sec\n"
        f"- Bubble Sort (O(N^2)):     {bubble_duration:.6f} sec\n"
        f"Speedup: {bubble_duration / max(merge_duration, 1e-9):.2f}x faster"
    )


# ==========================================
# CLI REPL Parser and Main Loop
# ==========================================
def execute_command(engine: MiniGitEngine, cmd_line: str) -> str:
    """
    [역할] 입력된 한 줄의 CLI 명령을 토큰화하고 문법 규격에 맞게 파싱하여 실행합니다.
    """
    cmd_line = cmd_line.strip()
    if not cmd_line:
        return ""

    try:
        # [shlex 파싱] 따옴표로 감싸진 인자("Add login feature" 등)를 하나의 토큰으로 정확히 보존합니다.
        tokens = shlex.split(cmd_line)
    except ValueError as ve:
        return f"Invalid args: {ve}"

    if not tokens:
        return ""

    # [명령어 대소문자 무시]
    command = tokens[0].upper()
    args = tokens[1:]

    # 1. INIT <user_name>
    if command == "INIT":
        if len(args) != 1:
            return "Invalid args: Usage: INIT <user_name>"
        return engine.init_repository(args[0])

    # 2. BRANCH <branch_name>
    elif command == "BRANCH":
        if len(args) != 1:
            return "Invalid args: Usage: BRANCH <branch_name>"
        return engine.create_branch(args[0])

    # 3. SWITCH <branch_name>
    elif command == "SWITCH":
        if len(args) != 1:
            return "Invalid args: Usage: SWITCH <branch_name>"
        return engine.switch_branch(args[0])

    # 4. COMMIT <message>
    elif command == "COMMIT":
        if len(args) != 1:
            return 'Invalid args: Usage: COMMIT "<message>"'
        return engine.commit(args[0])

    # 5. LOG [--sort-by=date|author]
    elif command == "LOG":
        sort_by = None
        if len(args) == 1:
            if args[0].startswith("--sort-by="):
                sort_by = args[0].split("=", 1)[1].lower()
            else:
                return "Invalid args: Expected LOG --sort-by=date|author"
        elif len(args) > 1:
            return "Invalid args: Usage: LOG [--sort-by=date|author]"
        return engine.log(sort_by=sort_by)

    # 6. PATH <commit1> <commit2>
    elif command == "PATH":
        if len(args) != 2:
            return "Invalid args: Usage: PATH <commit1> <commit2>"
        return engine.find_shortest_path(args[0], args[1])

    # 7. ANCESTORS <commit_hash>
    elif command == "ANCESTORS":
        if len(args) != 1:
            return "Invalid args: Usage: ANCESTORS <commit_hash>"
        res = engine.get_ancestors(args[0])
        if res is None:
            return f"Unknown commit: {args[0]}"
        if not res:
            return f"Commit {args[0]} has no ancestors (root commit)."
        return f"Ancestors of {args[0]}:\n" + "\n".join(f"- {c.hash}: {c.message}" for c in res)

    # 8. SEARCH <keyword> or SEARCH --author=<name>
    elif command == "SEARCH":
        if len(args) != 1:
            return 'Invalid args: Usage: SEARCH <keyword> OR SEARCH --author=<name>'
        arg = args[0]
        if arg.startswith("--author="):
            author_name = arg.split("=", 1)[1]
            return engine.search_author(author_name)
        else:
            return engine.search_keyword(arg)

    # [보너스] MERGE <branch_name>
    elif command == "MERGE":
        if len(args) != 1:
            return "Invalid args: Usage: MERGE <branch_name>"
        return engine.merge_branch(args[0])

    # [보너스] DIFF <file1> <file2>
    elif command == "DIFF":
        if len(args) != 2:
            return "Invalid args: Usage: DIFF <file1> <file2>"
        return simple_diff(args[0], args[1])

    # [보너스] BENCHMARK [N]
    elif command == "BENCHMARK":
        n = int(args[0]) if args and args[0].isdigit() else 2000
        return benchmark_sorts(n)

    else:
        return f"Unknown command: '{tokens[0]}'. Type help or exit."


def main():
    """
    [역할] REPL 인터페이스 메인 루프를 구동합니다.
    """
    engine = MiniGitEngine()
    print("=== Welcome to Mini Git CLI ===")
    print("Type 'exit' or 'quit' to terminate.\n")

    while True:
        try:
            # [프롬프트 출력 및 사용자 입력 대기]
            prompt_input = input("mini-git> ").strip()

            # [종료 커맨드 확인]
            if prompt_input.lower() in ("exit", "quit"):
                print("Exiting Mini Git. Goodbye!")
                break

            if not prompt_input:
                continue

            # [명령 실행 및 출력]
            output = execute_command(engine, prompt_input)
            if output:
                print(output)

        except (KeyboardInterrupt, EOFError):
            print("\nExiting Mini Git. Goodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()