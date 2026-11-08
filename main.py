from agent import Agent


def main():
    agent = Agent()
    try:
        agent.run()
    except KeyboardInterrupt:
        print("Программа прервана пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()