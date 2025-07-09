from ytx.core.llm.common import call_llm

if __name__ == "__main__":
    result = call_llm(prompt="Hello, world!", return_raw=True)
    print(result)