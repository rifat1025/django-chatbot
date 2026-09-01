import json
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

# ১. এনভায়রনমেন্ট লোড করা
load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")

# ২. Pydantic দিয়ে ডেটা স্ট্রাকচার নির্ধারণ করা
class ProductDetails(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(
        description="Product price as a number without currency symbol"
    )
    features: list[str] = Field(description="List of key product features")


# ৩. Parser ইনিশিয়ালাইজ করা
parser = JsonOutputParser(pydantic_object=ProductDetails)

# ৪. Groq LLM ইনিশিয়ালাইজ করা
llm = ChatGroq(
    groq_api_key=api_key,
    model_name="openai/gpt-oss-120b",  # অথবা "llama-3.1-8b-instant"
    temperature=0,
)

# ৫. প্রম্পট তৈরি (পার্সারের ফরম্যাট ইন্সট্রাকশন সহ)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Extract product details from the text.\n{format_instructions}",
        ),
        ("user", "{input}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# ৬. চেইন তৈরি
chain = prompt | llm | parser


def parse_product(description: str) -> dict:
    result = chain.invoke({"input": description})
    return result


# ৭. টেস্ট রান
description = """The Kees Van Der Westen Speedster is a high-end, single-group espresso machine known for its precision, performance, 
and industrial design. Handcrafted in the Netherlands, it features dual boilers for brewing and steaming, PID temperature control for 
consistency, and a unique pre-infusion system to enhance flavor extraction. Designed for enthusiasts and professionals, it offers 
customizable aesthetics, exceptional thermal stability, and intuitive operation via a lever system. The pricing is approximately $14,499 
depending on the retailer and customization options."""

extracted_data = parse_product(description)
print(json.dumps(extracted_data, indent=2))