import os
import re
import json
from datetime import time
from datetime import datetime
from typing import List, Dict, Any

from openai import OpenAI
from dotenv import load_dotenv

from app.service.vector_service import VectorService
from app.service.time_service import TimeService
from app.common.regions import parse_timezone_from_input, REGION_NAME_MAP

load_dotenv()

class AgentService:
    """
    HW-day2 AgentService
    - RAG(VectorDB) + Function Calling(TimeService) 통합
    """


    def __init__(
        self,
        vector_service: VectorService,
        time_service: TimeService,
    ):
        api_key = os.getenv("UPSTAGE_API_KEY")
        if not api_key:
            raise ValueError("UPSTAGE_API_KEY environment variable is required")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )

        self.vector_service = vector_service
        self.time_service = time_service


    # =====================================================
    # Public Entry
    # =====================================================
    def process_query(self, query: str) -> Dict[str, Any]:

        # 1. 지역/타임존 추출
        timezone = parse_timezone_from_input(query)

        # 👉 검색용 쿼리 보정
        search_query = timezone if timezone else query

        # 2️. RAG 검색
        search_results = self.vector_service.search(
            search_query,
            n_results=3
        )
        context = self._prepare_context(search_results)

        # 3. 시간 조회
        time_info = self._get_time_info(query)
        local_dt = datetime.fromisoformat(time_info["datetime"])

        # 4. 통화 가능 여부 판단
        decision = self._make_decision(context, local_dt)

        # 4️. LLM의 설명 출력
        response = self._generate_response(
            query=query,
            context=context,
            time_info=time_info,
            decision=decision
        )

        return {
            "ai_message": response
        }


    # =====================================================
    # Make Decision
    # =====================================================
    def _extract_time_range(self, text: str, label: str) -> tuple[time, time] | None:
        """
        예: '근무 시간은 08:30부터 17:00까지입니다'
        """
        pattern = rf"{label}.*?(\d{{1,2}}:\d{{2}}).*?(\d{{1,2}}:\d{{2}})"
        match = re.search(pattern, text)

        if not match:
            return None

        start = time.fromisoformat(match.group(1))
        end = time.fromisoformat(match.group(2))
        return start, end

    def _make_decision(self, context: str, local_dt: datetime) -> dict:
        work_range = self._extract_time_range(context, "근무 시간")
        lunch_range = self._extract_time_range(context, "점심시간")

        now = local_dt.time()

        # 기본값
        decision = {
            "available": False,
            "reason": "근무 시간 외입니다."
        }

        if not work_range:
            decision["reason"] = "근무 시간 규정을 확인할 수 없습니다."
            return decision

        work_start, work_end = work_range

        if not (work_start <= now <= work_end):
            decision["reason"] = f"근무 시간({work_start.strftime('%H:%M')}~{work_end.strftime('%H:%M')})이 아닙니다."
            return decision

        if lunch_range:
            lunch_start, lunch_end = lunch_range
            if lunch_start <= now <= lunch_end:
                decision["reason"] = f"점심시간({lunch_start.strftime('%H:%M')}~{lunch_end.strftime('%H:%M')})입니다."
                return decision

        decision["available"] = True
        decision["reason"] = "근무 시간 내이며 점심시간이 아닙니다."
        return decision

    # =====================================================
    # RAG Context
    # =====================================================
    def _prepare_context(self, search_results: Dict[str, Any]) -> str:

        documents = search_results.get("documents", [])
        metadatas = search_results.get("metadatas", [])

        # Chroma는 [[...]] 구조
        if not documents or not documents[0]:
            return ""

        docs = documents[0]
        metas = metadatas[0] if metadatas else [{}] * len(docs)

        context_parts = []

        for doc, meta in zip(docs, metas):
            office = meta.get("office_name", "Unknown Office")
            country = meta.get("country", "")
            timezone = meta.get("timezone", "")

            context_parts.append(
                f"[{office} | {country} | {timezone}]\n{doc}"
            )

        return "\n\n".join(context_parts)


    # =====================================================
    # Time Tool
    # =====================================================
    def _get_time_info(self, query: str) -> Dict[str, Any] | None:

        timezone = parse_timezone_from_input(query)
        if not timezone:
            return None

        raw = self.time_service.get_current_time(timezone)
        data = json.loads(raw)

        region_name = REGION_NAME_MAP.get(timezone, timezone)

        return {
            "region": region_name,
            "timezone": timezone,
            "datetime": data["datetime"],
        }


    # =====================================================
    # LLM Generation
    # =====================================================
    def _generate_response(
        self,
        query: str,
        context: str,
        time_info: Dict[str, Any] | None,
        decision: Dict[str, Any],
    ) -> str:

        system_prompt = """
        너는 글로벌 지사의 근무 규정을 설명하는 AI 비서다.

        중요 규칙:
        - 통화 가능 여부는 이미 결정되어 있다.
        - 너는 절대 판단을 바꾸거나 새로 해석하지 않는다.
        - 주어진 Decision과 Time 정보를 그대로 설명만 한다.
        
        답변 형식 규칙:
        1. 첫 문장은 반드시 "네, 가능합니다." 또는 "아니요, 지금은 곤란할 수 있습니다."로 시작한다.
        2. 두 번째 문장에서 현재 지역명(타임존 포함)과 현재 시각을 말한다.
        3. 세 번째 문장에서 근무 규정 또는 점심시간 등 이유를 명확히 설명한다.
        4. 마지막 문장에서 대안 시간이나 권장 행동을 제시한다.
        5. 줄바꿈 없이 한 문단으로 작성한다.
        """


        time_section = (
            f"Current local time:\n"
            f"- Region: {time_info['region']}\n"
            f"- Timezone: {time_info['timezone']}\n"
            f"- Datetime: {time_info['datetime']}\n"
            if time_info else "Current local time: Unknown\n"
        )

        user_prompt = f"""
        Decision:
        - Contact Available: {decision['available']}
        - Reason: {decision['reason']}

        Office Rule Summary:
        {context}

        Current Time Information:
        - Region: {time_info['region']}
        - Timezone: {time_info['timezone']}
        - Datetime: {time_info['datetime']}

        사용자 질문:
        {query}

        위 정보를 바탕으로 규칙에 맞는 한국어 답변을 생성하세요.
        """

        try:
            response = self.client.chat.completions.create(
                model="solar-pro2",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=300,
            )
            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating response: {str(e)}"

    from typing import List

    def add_knowledge_bulk(self, items: List[Any]):
        documents = []
        metadatas = []

        for item in items:
            documents.append(item.description)
            metadatas.append({
                "office_name": item.office_name,
                "timezone": item.timezone,
                "country": item.country,
            })

        self.vector_service.add_documents(documents, metadatas)

    def add_knowledge_batch(self, rules: List[Any]) -> Dict[str, Any]:
        documents = []
        metadatas = []

        for rule in rules:
            text = (
                f"{rule.office_name}의 근무 규정:\n"
                f"{rule.description}"
            )

            metadata = {
                "office_name": rule.office_name,
                "timezone": rule.timezone,
                "country": rule.country,
            }

            documents.append(text)
            metadatas.append(metadata)

        self.vector_service.add_documents(
            documents=documents,
            metadatas=metadatas,
        )

        return {
            "status": "success",
            "count": len(documents),
        }


    def add_knowledge(
            self,
            documents: List[str],
            metadatas: List[Dict[str, Any]] | None = None,
    ):
        self.vector_service.add_documents(
            documents=documents,
            metadatas=metadatas,
        )
        return {"status": "success", "count": len(documents)}


    def get_knowledge_stats(self) -> Dict[str, Any]:
        return self.vector_service.get_collection_info()
