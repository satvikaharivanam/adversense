import os
from dotenv import load_dotenv
from agent.tools.model_querier import ModelInterface

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

HF_URL = "https://router.huggingface.co/hf-inference/models/distilbert-base-uncased-finetuned-sst-2-english?provider=hf-inference"


def test_positive():

    mi = ModelInterface(
        url=HF_URL,
        auth_header=f"Bearer {HF_TOKEN}",
        model_type="huggingface",
    )

    result = mi.query_and_parse("This is amazing")

    print(result)

    assert "POSITIVE" in result


if __name__ == "__main__":
    test_positive()
    print("✅ Test passed")