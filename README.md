# Mini Git

Python으로 구현한 CLI 기반 Mini Git 프로젝트입니다.

Git의 핵심 동작 원리를 이해하기 위해 외부 그래프 라이브러리와 Python의 내장 정렬 함수(`sorted()`, `list.sort()`)를 사용하지 않고 커밋 그래프(DAG), 위상 정렬 기반 로그, 무방향 최단 경로 탐색(BFS), 직접 구현한 병합 정렬(Merge Sort), 역색인(Inverted Index)을 구현합니다.

이를 기반으로 Git의 핵심 기능인 저장소 초기화, 브랜치 관리, 커밋 생성, 그래프 탐색 및 키워드/작성자 검색을 구현하는 것을 목표로 합니다.

---

## 1. 프로젝트 소개

Git은 분산 버전 관리 시스템으로, 커밋 이력을 관리하고 브랜치 병합을 처리하기 위해 내부적으로 그래프 자료구조를 활용합니다.

단순히 Git 명령어를 사용하는 것을 넘어, 커밋 하나하나가 왜 방향성 비순환 그래프(DAG)를 이루는지, 브랜치와 HEAD 포인터가 어떻게 이동하는지, 그래프 탐색 알고리즘이 어떻게 버전 추적에 활용되는지 이해하는 것이 중요합니다.

이 프로젝트에서는 Git의 핵심 원리를 직접 코드로 구현하여 다음 개념을 학습합니다.

* 커밋 노드 구조와 DAG(Directed Acyclic Graph)
* 브랜치 포인터와 HEAD의 참조 메커니즘
* 위상 정렬(Topological Sort)과 Kahn 알고리즘
* 부모 우선 이력 출력(선행 관계 보장 로그)
* 무방향 그래프 변환 및 BFS 최단 경로(Shortest Path) 탐색
* 도달 가능성 기반 모든 조상(Ancestors) 탐색
* 병합 정렬(Merge Sort) 직접 구현 및 안정 정렬(Stable Sort)
* 역색인(Inverted Index)을 통한 $O(1)$ 단위 검색
* CLI(REPL) 명령어 파싱 및 예외 처리

---

## 2. 프로젝트 목표

### 자료구조 및 알고리즘 직접 구현

Python의 표준 정렬 API 및 외부 그래프 패키지에 의존하지 않고 다음 요소를 직접 구현합니다.

* Commit 노드 및 DAG 구조
* Inverted Index (키워드/작성자 2종 색인 테이블)
* Merge Sort (안정 정렬, $O(N \log N)$)
* Topological Sort (Kahn's Algorithm 기반)
* BFS 최단 경로 및 조상 탐색 알고리즘

### Git 기능 구현

Git의 핵심적인 형상 관리 및 탐색 명령어를 CLI에서 사용할 수 있도록 구현합니다.

```text
INIT <user_name>
BRANCH <branch_name>
SWITCH <branch_name>
COMMIT <message>
LOG [--sort-by=date|author]
PATH <commit1> <commit2>
ANCESTORS <commit_hash>
SEARCH <keyword>
SEARCH --author=<name>
MERGE <branch_name>
DIFF <file1> <file2>

```

### CLI 구현

사용자가 터미널 환경에서 직관적으로 명령을 내릴 수 있는 REPL 환경을 구현합니다.

```text
mini-git> INIT "Alice"
Initialized repository.
Current branch: main
Current user: Alice

mini-git> COMMIT "Initial commit"
[main 0141e6] Initial commit

```

---

## 3. 개발 환경

* Python 3.10 이상
* macOS / Linux / Windows 환경
* Git / GitHub

별도의 외부 라이브러리 없이 Python 기본 내장 모듈(`shlex`, `datetime`, `collections.deque` 등)만을 사용하여 구현합니다.

---

## 4. 프로젝트 구조

```text
codysseyB5_2/

├── main.py
├── README.md
└── .gitignore

```

단일 엔트리 포인트(`main.py`) 내에서 자료구조, 코어 엔진, 정렬 및 탐색 알고리즘, CLI 인터페이스가 독립된 클래스와 함수로 명확히 분리되어 동작합니다.

---

## 5. 핵심 자료구조

### 5.1 Commit Node & DAG

Git의 커밋 이력은 방향성 비순환 그래프(DAG)를 형성합니다.

각 커밋 노드는 과거의 커밋(부모)을 기반으로만 생성될 수 있으며, 시간의 비가역성에 의해 미래의 커밋을 과거의 부모로 둘 수 없으므로 사이클이 절대 발생하지 않습니다.

커밋 노드는 다음 정보를 가집니다.

```text
hash       : 세션 내 유일한 고유 식별자
message    : 커밋 메시지
author     : 커밋 작성자 이름
timestamp  : 커밋 생성 일시
parents    : 0개 이상의 부모 커밋 해시 리스트

```

저장소는 커밋 해시를 Key로 하는 해시맵(`self.commits`)으로 관리되어 $O(1)$의 빠른 접근을 보장합니다.

---

### 5.2 브랜치와 HEAD 포인터

브랜치는 커밋 객체들의 연속된 집합이 아니라, 특정 커밋 해시를 가리키는 가동 포인터(Reference)입니다.

```text
[Commit A] ← [Commit B] (HEAD -> main)

```

새로운 커밋이 생성되면 현재 HEAD가 가리키는 브랜치 포인터가 새 커밋으로 전진합니다.

과거 커밋에 브랜치명이 붙지 않는 이유는, 브랜치 태그가 오직 해당 브랜치의 최신 커밋(Tip/HEAD)에만 부착되기 때문입니다.

---

### 5.3 Inverted Index (역색인)

모든 커밋 메시지를 매번 전체 순회($O(N)$)하지 않고 원하는 커밋을 즉시 찾기 위해 역색인 구조를 사용합니다.

최소 2종의 색인 테이블을 구축합니다.

```text
keyword_index : 토큰 단어(소문자) → [commit_hash_1, commit_hash_2, ...]
author_index  : 작성자명(소문자) → [commit_hash_1, commit_hash_2, ...]

```

커밋 생성 시점에 메시지를 공백 단위로 토큰화하고 특수문자를 정제하여 색인 테이블에 등록하므로, 검색 시 $O(1)$ 룩업으로 후보군을 빠르게 확보합니다.

---

## 6. 핵심 알고리즘

### 6.1 병합 정렬 (Merge Sort) 직접 구현

Python 표준 라이브러리인 `sorted()`와 `list.sort()`를 배제하고, 분할 정복(Divide and Conquer) 방식의 병합 정렬을 직접 구현했습니다.

* **시간 복잡도**: 최선, 평균, 최악 모두 $O(N \log N)$ 보장
* **안정 정렬(Stable Sort)**: 비교 시 `<=` 연산자를 적용하여 동일한 우선순위를 가진 커밋의 원래 순서가 보존되도록 구현

비교 키 추출 함수(`key_func`)를 인자로 전달받아 날짜 기준(`date`), 작성자 기준(`author`), 사전순 경로 선택 등 다양한 정렬 기준에 유연하게 대응합니다.

---

### 6.2 위상 정렬 (Topological Sort) 기반 LOG

단순 최신순(역방향 스택) 나열이 아니라, 변경 이력의 발생 인과관계를 보여주기 위해 **부모 커밋이 항상 자식 커밋보다 먼저 출력**되도록 위상 정렬(Kahn's Algorithm 변형)을 적용합니다.

```text
[부모 커밋 진입 차수(in-degree) 계산]
                 ↓
      진입 차수가 0인 루트 커밋 큐 삽입
                 ↓
            큐에서 Pop 및 출력
                 ↓
    연결된 자식 커밋들의 in-degree 1 감소
                 ↓
  in-degree가 0이 된 자식 커밋을 큐에 삽입
                 ↓
          큐가 빌 때까지 반복

```

---

### 6.3 최단 경로 (PATH) 탐색

두 커밋 사이의 최단 경로는 **부모-자식 관계를 무방향 간선으로 간주**했을 때의 최소 간선 거리로 정의됩니다.

* 간선의 가중치가 모두 동일(1)하므로 너비 우선 탐색(BFS)을 적용하여 $O(V + E)$에 최단 경로를 보장합니다.
* 최단 경로가 복수 개 존재하는 경우, 경로를 `hash1->hash2->...` 형태의 문자열로 변환한 뒤 직접 구현한 `merge_sort`를 통해 **사전순으로 가장 작은 경로**를 최종 선택합니다.

---

### 6.4 조상 (ANCESTORS) 탐색

특정 커밋 노드로부터 출발하여 `parents` 참조만을 따라 거슬러 올라가는 BFS/DFS 탐색을 수행합니다.

방문 집합(`visited`)을 두어 중복 탐색과 다중 부모 병합 커밋에서의 루프를 방지하고, 도달 가능한 모든 선조 커밋을 빠짐없이 수집하여 타임스탬프 순으로 정렬해 출력합니다.

---

## 7. 명령어 사양

### INIT

저장소를 초기화하고 기본 `main` 브랜치 및 작업 사용자를 설정합니다.

```text
mini-git> INIT "Alice"

Initialized repository.
Current branch: main
Current user: Alice

```

---

### BRANCH

현재 HEAD가 가리키는 커밋 위치를 기준으로 새 브랜치를 생성합니다.

```text
mini-git> BRANCH feature

Created branch: feature

```

---

### SWITCH

작업 브랜치(HEAD)를 지정한 브랜치로 전환합니다.

```text
mini-git> SWITCH feature

Switched to branch: feature

```

---

### COMMIT

현재 브랜치의 최신 커밋을 부모로 삼아 새 커밋 노드를 DAG에 등록하고 역색인을 갱신합니다.

```text
mini-git> COMMIT "Add login feature"

[feature 02c054] Add login feature

```

---

### LOG

커밋 목록을 출력합니다. 기본 호출 시 부모 커밋이 자식 커밋보다 먼저 출력되는 위상 정렬 순서로 나열됩니다.

```text
mini-git> LOG

commit 0141e6 (Alice, 2026-10-01 21:30:02)
    initial commit
commit 02c054 (Alice, 2026-10-01 21:31:18) [feature]
    Add login feature
commit 033821 (Alice, 2026-10-01 21:32:31) [main]
    Add payment feature

```

옵션 플래그를 통해 커스텀 정렬을 지원합니다.

* `LOG --sort-by=date` : 생성 타임스탬프 기준 정렬
* `LOG --sort-by=author` : 작성자 이름 알파벳순 정렬

---

### PATH

두 커밋 노드 사이의 무방향 최단 경로를 탐색합니다.

```text
mini-git> PATH 0141e6 02c054

Path: 0141e6->02c054

```

경로가 존재하지 않을 경우 `No path`를 출력합니다.

---

### ANCESTORS

지정한 커밋에서 도달 가능한 모든 부모 및 상위 조상 커밋들을 출력합니다.

```text
mini-git> ANCESTORS 02c054

Ancestors of 02c054:
- 0141e6: initial commit

```

---

### SEARCH

역색인(Inverted Index)을 조회하여 키워드 또는 작성자에 해당하는 커밋들을 빠르게 검색합니다.

```text
mini-git> SEARCH "login"

Found 1 commit(s):
- 02c054: Add login feature (by Alice)

```

작성자별 검색:

```text
mini-git> SEARCH --author=Alice

Found 3 commit(s) by Alice:
- 0141e6: initial commit [2026-10-01 21:30:02]
- 02c054: Add login feature [2026-10-01 21:31:18]
- 033821: Add payment feature [2026-10-01 21:32:31]

```

---

### MERGE (보너스 기능)

지정한 브랜치를 현재 브랜치로 병합하며, 두 브랜치의 최신 커밋을 부모로 갖는 병합 커밋(부모 2개)을 생성합니다.

```text
mini-git> MERGE feature

[main 04d1a9] Merge branch 'feature' into main

```

---

### DIFF (보너스 기능)

두 텍스트 파일을 줄 단위로 비교하여 추가(+), 삭제(-), 공통( ) 내역을 출력합니다.

```text
mini-git> DIFF file1.txt file2.txt

```

---

## 8. CLI 및 에러 처리

Mini Git은 `shlex` 기반 파서를 통해 큰따옴표/작은따옴표가 포함된 문자열 인자를 공백 보존 상태로 안전하게 분리합니다.

* 대소문자 무시: `INIT`, `init`, `Init` 모두 동일하게 허용
* 표준 예외 메시지 출력:
* `Invalid args: Usage: ...`
* `Unknown branch: <name>`
* `Unknown commit: <hash>`
* `Error: Repository not initialized. Run INIT first.`



---

## 9. 실행 방법

저장소를 복제한 후 Python 인터프리터를 통해 직접 실행합니다.

```bash
git clone https://github.com/SJendministrator/codysseyB5_2.git
cd codysseyB5_2
python main.py

```

실행 시 다음과 같은 대화형 REPL 프롬프트가 나타납니다.

```text
=== Welcome to Mini Git CLI ===
Type 'exit' or 'quit' to terminate.

mini-git>

```

종료 시 `exit` 또는 `quit`을 입력합니다.

---

## 10. 실제 기능 테스트 결과

구현된 Mini Git을 CLI 터미널 환경에서 실행하여 핵심 요구 기능들을 검증했습니다.

### 10.1 저장소 초기화 및 브랜치 커밋 분기 테스트

```text
mini-git> init 'sj'  
Initialized repository.
Current branch: main
Current user: sj

mini-git> commit 'initial commit'
[main 0141e6] initial commit

mini-git> branch feature
Created branch: feature

mini-git> switch feature
Switched to branch: feature

mini-git> commit 'add login feature'
[feature 02c054] add login feature

mini-git> switch main
Switched to branch: main

mini-git> commit "Add payment feature"
[main 033821] Add payment feature

```

`INIT`으로 `main` 브랜치와 활성 사용자를 생성한 후 루트 커밋(`0141e6`)을 생성했습니다.

이후 `feature` 브랜치를 분기하여 별도 커밋(`02c054`)을 수행하고, 다시 `main`으로 전환하여 또 다른 커밋(`033821`)을 작성하여 그래프가 분기(Fork)되는 DAG 형태를 구축했습니다.

---

### 10.2 위상 정렬 로그 및 브랜치 포인터 표기 검증

```text
mini-git> log
commit 0141e6 (sj, 2026-10-01 21:30:02)
    initial commit
commit 02c054 (sj, 2026-10-01 21:31:18) [feature]
    add login feature
commit 033821 (sj, 2026-10-01 21:32:31) [main]
    Add payment feature

```

* **부모 커밋 우선 출력**: 루트 커밋인 `0141e6`이 자식 커밋들보다 가장 먼저 출력되어 위상 정렬 요구사항을 만족했습니다.
* **브랜치 포인터 정상 동작 확인**: 첫 번째 커밋 `0141e6`에는 브랜치 태그가 붙지 않고 최신 커밋인 `02c054`에는 `[feature]`, `033821`에는 `[main]`이 정확히 부착되었습니다. 이는 Git의 브랜치가 커밋 묶음이 아니라 최신 커밋(Tip)만을 가리키는 이동식 포인터이기 때문입니다.

---

### 10.3 최단 경로 및 역색인 검색 테스트

```text
mini-git> path 0141e6 02c054
Path: 0141e6->02c054

mini-git> search 'login'
Found 1 commit(s):
- 02c054: add login feature (by sj)

```

`PATH` 명령을 통해 루트 커밋과 브랜치 커밋 사이의 무방향 최단 연결 경로를 정상 계산하였으며, `SEARCH` 명령 시 역색인 해시맵을 통해 전체 순회 없이 원하는 키워드가 포함된 커밋을 즉시 추출했습니다.

---

### 10.4 커스텀 정렬 알고리즘 검증

```text
mini-git> log --sort-by=author
commit 0141e6 (sj, 2026-10-01 21:30:02)
    initial commit
commit 02c054 (sj, 2026-10-01 21:31:18) [feature]
    add login feature
commit 033821 (sj, 2026-10-01 21:32:31) [main]
    Add payment feature

```

표준 라이브러리(`sorted()`) 없이 직접 작성한 `merge_sort` 함수를 통해 작성자 및 타임스탬프 기준으로 안정 정렬이 올바르게 수행됨을 확인했습니다.

---

### 10.5 테스트 결과 정리

| 테스트 항목 | 검증 내용 | 결과 |
| --- | --- | --- |
| **INIT / USER** | 저장소 생성, main 브랜치 및 사용자 등록 | **정상 동작** |
| **BRANCH / SWITCH** | 브랜치 분기 포인터 생성 및 작업 브랜치 이동 | **정상 동작** |
| **COMMIT (DAG)** | 부모 해시 참조 및 단방향 비순환 관계 구축 | **정상 동작** |
| **Topological LOG** | 부모 노드가 먼저 출력되는 위상 정렬 순서 보장 | **정상 동작** |
| **LOG (--sort-by)** | 병합 정렬 기반 타임스탬프/작성자별 안정 정렬 | **정상 동작** |
| **PATH (BFS)** | 무방향 간선 간 최소 거리 및 사전순 최소 경로 탐색 | **정상 동작** |
| **ANCESTORS** | 다중 부모 및 루트까지의 모든 선조 노드 도달 탐색 | **정상 동작** |
| **SEARCH (Index)** | 토큰화 역색인 기반 키워드 및 작성자 즉시 검색 | **정상 동작** |
| **MERGE (Bonus)** | 2개 이상의 부모를 갖는 병합 노드 생성 | **정상 동작** |
| **DIFF (Bonus)** | 줄 단위 텍스트 비교 및 추가/삭제 마킹 | **정상 동작** |

---

## 11. 제한 사항

학습 및 알고리즘 검증 목적으로 다음 라이브러리 및 기능 사용을 제한합니다.

```text
sorted()
list.sort()
networkx 등 그래프 전용 외부 라이브러리

```

또한 Git의 내부 저장 메커니즘 중 다음 영역은 프로젝트 범위에서 제외하고 메모리 상의 동작으로 구성합니다.

* 실제 파일 blob 및 트리 오브젝트 영속성(파일 저장)
* 원격 저장소와의 네트워크 푸시/풀 통신
* 3-Way 충돌 해결 알고리즘

---

## 12. 학습한 내용

이 프로젝트를 통해 다음 핵심 전산학 이론을 직접 구현하고 체득했습니다.

* **DAG와 버전 관리**: 커밋 그래프가 사이클이 없는 방향성 그래프를 형성하는 필연적 이유와 노드 간 참조 원리
* **참조(Ref) 메커니즘**: 브랜치가 커밋의 집합이 아니라 단일 해시 포인터에 불과하다는 Git의 핵심 설계 철학
* **위상 정렬(Topological Sort)**: 작업 간 선후 관계가 명확한 비순환 그래프에서 의존성을 해치지 않고 순서를 나열하는 기법
* **무방향 최단 경로 탐색(BFS)**: 간선 가중치가 1인 상태에서 최소 변경 단계를 추적하기 위한 너비 우선 탐색 활용
* **안정 정렬과 분할 정복**: 병합 정렬(Merge Sort)을 직접 구현하며 체득한 $O(N \log N)$ 정렬 특성과 데이터 순서 보존
* **역색인(Inverted Index)**: 대용량 데이터베이스 검색 엔진의 핵심인 역색인을 설계하여 $O(N)$ 선형 탐색을 $O(1)$ 룩업으로 최적화하는 방법
* **CLI REPL 구축**: 인자 파싱과 견고한 에러 핸들링을 갖춘 대화형 인터페이스 설계