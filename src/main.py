import asyncio
import aiohttp
from dotenv import load_dotenv
import os
from os.path import join, dirname

from core.interface import Interface
from core.brain import Brain
from core.constants import FIRST_SPACE, FEELINGS1
from core.prompts import SANYA_ROLE
from core.agent import Agent
from core.manager import AgentManager
from example_agent import Sanya


async def main():
    async with aiohttp.ClientSession() as session:
        interface = Interface(session)
        brain = Brain(
            base_intentions=FIRST_SPACE,
            feelings=FEELINGS1.copy()
        )
        agent = Sanya(
            id="sanya",
            role=SANYA_ROLE,
            brain=brain,
            interface=interface
        )

        mgr = AgentManager()
        mgr.add_agent(agent)

        while True:
            user_input = input("👤 Вы: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Завершение сессии.")
                break

            print("⏳ Отправка запроса модели...")
            try:
                response = await mgr.send_to_agent("sanya", user_input)
                print(f"\n🤖 {agent.id}\n", response.strip(), "\n")
            except Exception as e:
                print(f"❌ Ошибка: {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    asyncio.run(main())
