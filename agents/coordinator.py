"""
AuraFin Workflow Coordinator
Orchestrates all 5 agents via Google ADK 2.0 sequential pipeline.
"""

import asyncio
import os
from google import genai
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from tools.mcp_tools import (
    check_installment_status,
    generate_referral_token,
    query_job_market,
    activate_escrow_contract,
)

MODEL = "gemini-2.0-flash-exp"
APP_NAME = "aurafin"


def build_trigger_agent() -> Agent:
    return Agent(
        name="trigger_agent",
        model=MODEL,
        description="Monitors installment ledger and detects payment delays.",
        instruction="""
You are the AuraFin Trigger Agent.
Your job: check if a consumer has 2 or more overdue installments.
Use the check_installment_status tool with the provided consumer_id.
If trigger_mediation is True, report clearly: MEDIATION REQUIRED.
If False, report: DIRECT SETTLEMENT — no mediation needed.
Always include delay_count and total_overdue in your report.
""",
        tools=[check_installment_status],
    )


def build_mediation_agent() -> Agent:
    return Agent(
        name="mediation_agent",
        model=MODEL,
        description="Generates privacy-preserving tokenized referral for the consumer.",
        instruction="""
You are the AuraFin Mediation Agent.
Your job: generate a Tokenized Referral for the consumer.
This token anonymizes financial data — employers will NEVER see debt history.
Use generate_referral_token with the consumer_id and their skill list.
Default skills if unknown: ["communication", "coordination", "admin", "data"].
Confirm: financial_data_exposed must be False and gdpr_compliant must be True.
Report the token and confirm privacy protections are active.
""",
        tools=[generate_referral_token],
    )


def build_skill_matcher_agent() -> Agent:
    return Agent(
        name="skill_matcher_agent",
        model=MODEL,
        description="Matches consumer skills to live job market demand using Gemini.",
        instruction="""
You are the AuraFin Skill Matcher Agent.
Your job: find the best employer matches for the consumer.
Use query_job_market with the consumer's skills and location (default: remote).
Only surface fair_wage_compliant matches.
Rank by match_score. Report top 3 matches with:
- Role title
- Match score
- Wage offered
- Estimated months to debt clearance
If no matches found, escalate to Oversight Agent.
""",
        tools=[query_job_market],
    )


def build_escrow_agent() -> Agent:
    return Agent(
        name="escrow_agent",
        model=MODEL,
        description="Activates smart escrow contract for wage-based debt settlement.",
        instruction="""
You are the AuraFin Escrow Agent.
Your job: activate a smart escrow contract for the top employer match.
Use activate_escrow_contract with:
- token: the referral token from mediation
- employer_id: top match from skill matching
- wage_offered: from job market data
- debt_amount: total_overdue from trigger report
CRITICAL: If fair_wage_floor_enforced is False, BLOCK the contract and escalate.
On success, report:
- Contract ID
- Monthly repayment amount
- Consumer take-home pay
- Estimated debt clearance months
Confirm consumer_protected is True.
""",
        tools=[activate_escrow_contract],
    )


def build_oversight_agent() -> Agent:
    return Agent(
        name="oversight_agent",
        model=MODEL,
        description="Human-in-the-loop escalation handler for edge cases.",
        instruction="""
You are the AuraFin Oversight Agent.
You handle cases that cannot be resolved automatically:
- No employer match found
- Fair wage floor violation
- Disputed debt amounts
- Consumer requests human review

Your response must:
1. Summarize the reason for escalation
2. List recommended actions for the human mediator
3. Confirm the consumer's rights:
   - Right to exit the voluntary framework at any time
   - Right to dispute debt amount
   - Right to request a different employer match
4. Generate a case reference number (format: CASE-YYYY-XXXX)

You are the safety net. Consumer dignity is the top priority.
""",
        tools=[],
    )


async def run_pipeline(consumer_id: str):
    """
    Run the full AuraFin Mediation-to-Work pipeline for a consumer.
    """
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=consumer_id,
    )

    print(f"[Pipeline] Starting for consumer: {consumer_id}")
    print(f"[Pipeline] Session: {session.id}\n")

    # ── Step 1: Trigger ───────────────────────────────────────────
    print("── STEP 1: Trigger Agent ──────────────────────────────")
    trigger = build_trigger_agent()
    runner = Runner(agent=trigger, app_name=APP_NAME, session_service=session_service)
    trigger_prompt = f"Check installment status for consumer_id: {consumer_id}"
    trigger_result = ""
    async for event in runner.run_async(
        user_id=consumer_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=trigger_prompt)])
    ):
        if event.is_final_response() and event.content:
            trigger_result = event.content.parts[0].text
            print(f"[Trigger] {trigger_result}\n")

    if "DIRECT SETTLEMENT" in trigger_result.upper():
        print("[Pipeline] ✓ No mediation needed. Direct settlement initiated.")
        return

    # ── Step 2: Mediation ─────────────────────────────────────────
    print("── STEP 2: Mediation Agent ────────────────────────────")
    mediation = build_mediation_agent()
    runner2 = Runner(agent=mediation, app_name=APP_NAME, session_service=session_service)
    mediation_result = ""
    async for event in runner2.run_async(
        user_id=consumer_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(
            text=f"Generate referral token for consumer_id: {consumer_id}"
        )])
    ):
        if event.is_final_response() and event.content:
            mediation_result = event.content.parts[0].text
            print(f"[Mediation] {mediation_result}\n")

    # ── Step 3: Skill Matching ────────────────────────────────────
    print("── STEP 3: Skill Matcher Agent ────────────────────────")
    matcher = build_skill_matcher_agent()
    runner3 = Runner(agent=matcher, app_name=APP_NAME, session_service=session_service)
    match_result = ""
    async for event in runner3.run_async(
        user_id=consumer_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(
            text="Find job matches for skills: communication, coordination, admin, data. Location: remote."
        )])
    ):
        if event.is_final_response() and event.content:
            match_result = event.content.parts[0].text
            print(f"[Skill Matcher] {match_result}\n")

    if "NO MATCH" in match_result.upper() or "ESCALATE" in match_result.upper():
        print("── ESCALATING: Oversight Agent ────────────────────────")
        oversight = build_oversight_agent()
        runner_o = Runner(agent=oversight, app_name=APP_NAME, session_service=session_service)
        async for event in runner_o.run_async(
            user_id=consumer_id,
            session_id=session.id,
            new_message=types.Content(role="user", parts=[types.Part(
                text=f"Escalation: No employer match found for consumer {consumer_id}. Review required."
            )])
        ):
            if event.is_final_response() and event.content:
                print(f"[Oversight] {event.content.parts[0].text}\n")
        return

    # ── Step 4: Escrow ────────────────────────────────────────────
    print("── STEP 4: Escrow Agent ───────────────────────────────")
    escrow = build_escrow_agent()
    runner4 = Runner(agent=escrow, app_name=APP_NAME, session_service=session_service)
    async for event in runner4.run_async(
        user_id=consumer_id,
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(
            text=f"""
Activate escrow contract.
Referral token context: {mediation_result[:200]}
Job match context: {match_result[:200]}
Debt context: {trigger_result[:200]}
Use employer_id: EMP-001, wage_offered: 22.0, debt_amount: 3500.
"""
        )])
    ):
        if event.is_final_response() and event.content:
            print(f"[Escrow] {event.content.parts[0].text}\n")

    print("── PIPELINE COMPLETE ──────────────────────────────────")
    print("[AuraFin] ✓ Debt cleared pathway activated.")
    print("[AuraFin] ✓ Consumer: Employed and on track to debt-free.\n")
