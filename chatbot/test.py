import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")


class ProductDetails(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(
        description="Product price as a number without currency symbol"
    )
    features: list[str] = Field(
        description="List of key product features"
    )


parser = JsonOutputParser(
    pydantic_object=ProductDetails
)

llm = ChatGroq(
    groq_api_key=api_key,
    model_name="openai/gpt-oss-120b",
    temperature=0,
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extract product details from the text.\n{format_instructions}",
        ),
        ("user", "{input}"),
    ]
).partial(
    format_instructions=parser.get_format_instructions()
)

chain = prompt | llm | parser

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)


def parse_product(description: str):
    return chain.invoke(
        {"input": description}
    )


description = """
The Kees Van Der Westen Speedster is a high-end, single-group espresso machine
known for its precision, performance, and industrial design. Handcrafted in the
Netherlands, it features dual boilers for brewing and steaming, PID temperature
control for consistency, and a unique pre-infusion system to enhance flavor
extraction. Designed for enthusiasts and professionals, it offers customizable
aesthetics, exceptional thermal stability, and intuitive operation via a lever
system. The pricing is approximately $14,499 depending on the retailer and
customization options.
"""

extracted_data = parse_product(description)

print(json.dumps(extracted_data, indent=2))

vector = embeddings.embed_query(
    "espresso machine"
)

print(f"Embedding dimension: {len(vector)}")