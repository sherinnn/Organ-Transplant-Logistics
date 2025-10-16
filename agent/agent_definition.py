import os
import requests
from strands import Agent, tool
from strands.models import BedrockModel
from dotenv import load_dotenv

# === Optional imports for memory ===
try:
    from bedrock_agentcore.memory import MemoryClient
    from strands.hooks import HookProvider, HookRegistry, MessageAddedEvent, AgentInitializedEvent
    MEMORY_AVAILABLE = True
except ImportError:
    print("⚠️ AgentCore Memory SDK not installed — running without memory.")
    MEMORY_AVAILABLE = False

# ================================
# ⚙️ Setup & Environment
# ================================
load_dotenv()
GATEWAY_URL = "http://127.0.0.1:8000/mcp"
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# ================================
# 🌤️ Weather Tool
# ================================
@tool
def weather_tool(origin_city: str, dest_city: str):
    """Get weather forecast between two cities."""
    try:
        payload = {"origin": {"city": origin_city}, "dest": {"city": dest_city}}
        print(f"📡 Weather Request → {payload}")
        resp = requests.post(f"{GATEWAY_URL}/get_weather_forecast", json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Weather error: {e}")
        return {"error": str(e)}

# ================================
# ✈️ Flight Tool
# ================================
@tool
def flight_tool(origin: str, dest: str, date: str):
    """Get flight details for organ transport."""
    try:
        payload = {"origin": origin, "dest": dest, "date": date}
        print(f"📡 Flight Request → {payload}")
        resp = requests.post(f"{GATEWAY_URL}/get_flight_info", json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ Flight error: {e}")
        return {"error": str(e)}

# ================================
# 🧩 Optional AgentCore Memory Hook
# ================================
class AgentCoreMemoryHookProvider(HookProvider):
    def __init__(self, memory_client, memory_id, actor_id="agent", session_id="default"):
        self.client = memory_client
        self.memory_id = memory_id
        self.actor_id = actor_id
        self.session_id = session_id

    def register_hooks(self, registry: HookRegistry):
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)

    def on_message_added(self, event):
        """Store last user+agent message into memory."""
        last_msg = event.agent.messages[-1]
        role = last_msg.get("role")
        text = last_msg.get("content")[0].get("text", "")
        self.client.create_event(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=self.session_id,
            messages=[(text, role)]
        )
        print(f"🧠 Stored memory event ({role}): {text[:80]}...")

    def on_agent_initialized(self, event):
        """Retrieve last few turns from memory and inject context."""
        events = self.client.list_events(
            memory_id=self.memory_id,
            actor_id=self.actor_id,
            session_id=self.session_id,
            max_results=5
        )
        if events:
            context = []
            for ev in events:
                for text, role in ev["messages"]:
                    context.append(f"{role.upper()}: {text}")
            past_context = "\n".join(context)
            event.agent.system_prompt += "\n\n🧠 **Recent Memory Context:**\n" + past_context
            print("🔁 Injected memory context into system prompt.")

# ================================
# 🩺 Agent System Prompt
# ================================
SYSTEM_PROMPT = """
You are **OrganMatch**, an AI coordination assistant for optimizing organ donation and transplantation logistics.

Your mission:
- Help transplant coordinators assess environmental and transport readiness.
- Use weather and flight data to ensure timely, safe, and efficient organ delivery.
- Present data clearly with structured summaries and actionable recommendations.

Guidelines:
1. Always prioritize organ viability, recipient safety, and time sensitivity.
2. Warn clearly if conditions are risky (weather, delay, etc.).
3. Keep communication factual, structured, and calm.
4. Avoid clinical recommendations — your role is coordination.
5. Format output with headers, icons (🌤️ ✈️ ⚠️ ✅), and clarity.
"""

# ================================
# 🤖 Build Agent
# ================================
def build_agent():
    model = BedrockModel(model_id="anthropic.claude-3-sonnet-20240229-v1:0")

    hooks = []
    if MEMORY_AVAILABLE:
        try:
            print("🧠 Initializing AgentCore Memory...")
            mem_client = MemoryClient(region_name=AWS_REGION)
            memory = mem_client.create_memory_and_wait(
                name="OrganMatchMemory",
                description="Short-term memory for OrganMatch agent",
                strategies=[],
                event_expiry_days=7,
            )
            memory_id = memory["id"]
            hooks.append(AgentCoreMemoryHookProvider(mem_client, memory_id))
            print(f"✅ Memory initialized (ID: {memory_id})")
        except Exception as e:
            print(f"⚠️ Memory setup failed: {e}")

    return Agent(
        name="OrganMatch",
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[weather_tool, flight_tool],
        hooks=hooks if hooks else None
    )

# ================================
# 🚀 Run Agent
# ================================
def main():
    agent = build_agent()
    print("\n🫀 OrganMatch Agent is Online.")
    print("Type your query (e.g. 'Create transport plan from LAX to JFK for Oct 20') or 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"):
            print("👋 Exiting OrganMatch.")
            break

        try:
            result = agent(query)
            print("\nAgent:", result, "\n")
        except Exception as e:
            print(f"❌ Agent error: {e}\n")

if __name__ == "__main__":
    main()
