import asyncio
from oai_interface import Interface
import helper as hlp
import aiohttp

async def main():
    cfg = hlp.load_config()
    llm = cfg.get("llm", {})
    provider = llm.get("provider", "openai")
    print(f"🧠 Провайдер: {provider}")
    print(f"🔗 API base: {llm.get('api_base', '(по умолчанию)')}")
    print(f"💬 Модель: {llm.get('model_chat', '(по умолчанию)')}\n")

    async with aiohttp.ClientSession() as session:
        interface = Interface(session)
        print("✅ Интерфейс инициализирован успешно.")
        print("Введите сообщение (или 'exit' для выхода)\n")

        while True:
            user_input = input("👤 Вы: ")
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Завершение сессии.")
                break

            print("⏳ Отправка запроса модели...")
            try:
                # Отправляем сообщение как chat completion
                response = await interface.test_model(
                    reply=user_input
                )
                print("\n🤖 Ответ модели:\n", response.strip(), "\n")
            except Exception as e:
                print(f"❌ Ошибка: {type(e).__name__}: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
