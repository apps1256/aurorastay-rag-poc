
import os
import re
from langchain_openai import ChatOpenAI


# Optimized V1 property-aware retrieval
def retrieve_docs(query, k=3, vectorstore=None):
    query_lower = query.lower()

    # Recover the structured property profiles from saved FAISS
    all_docs = list(vectorstore.docstore._dict.values())

    property_docs = [
        doc for doc in all_docs
        if doc.metadata.get("document_type") == "property_profile"
    ]

    property_lookup = {
        doc.metadata["property"].split(",")[0].lower(): doc
        for doc in property_docs
    }

    # Noise complaint routing
    noise_pattern = (
        r"\b(noise|noisy|loud|quiet|disturbance|"
        r"disturbing|neighbor(?:ing)? room|party|parties)\b"
    )

    if re.search(noise_pattern, query_lower):
        quiet_hours_docs = [
            doc for doc in all_docs
            if doc.metadata.get("source", "").endswith(
                "aurorastay_guest_conduct_accessibility_and_resolution_guidelines.pdf"
            )
            and re.search(
                r"\|\s*Quiet hours\s*\|",
                doc.page_content,
                flags=re.IGNORECASE
            )
        ]

        if quiet_hours_docs:
            selected = [quiet_hours_docs[0]]

            for doc in vectorstore.similarity_search(query, k=15):
                if any(
                    existing.page_content == doc.page_content
                    for existing in selected
                ):
                    continue

                selected.append(doc)

                if len(selected) >= k:
                    break

            return selected[:k]

    # Match known property codes and names
    matched_doc = None

    for property_name, doc in property_lookup.items():
        short_name = property_name.replace("ash-", "").strip()
        hotel_name = short_name.split(" ", 1)[-1]

        if (
            property_name in query_lower
            or short_name in query_lower
            or hotel_name in query_lower
        ):
            matched_doc = doc
            break

    # Retrieve supporting policy chunks
    selected = []

    if matched_doc is not None:
        selected.append(matched_doc)

    for doc in vectorstore.similarity_search(query, k=15):
        if doc.metadata.get("document_type") == "property_profile":
            continue

        if any(
            existing.page_content == doc.page_content
            for existing in selected
        ):
            continue

        selected.append(doc)

        if len(selected) >= k:
            break

    return selected[:k]


# Return retrieved chunks in the same format as the notebook
def retrieve(query, k=3, vectorstore=None):
    docs = retrieve_docs(query, k=k, vectorstore=vectorstore)

    return [
        f"Content:\n{doc.page_content}\n\nMetadata:\n{doc.metadata}"
        for doc in docs
    ]


# AuroraStay generation prompt
def generate(query, retrieved_chunks, model):

    prompt = f"""
    You are an AI assistant helping AuroraStay Hotels staff answer
    guest questions using official hotel policy documents.

    User Query:
    {query}

    Retrieved Hotel Policy Information:
    {retrieved_chunks}

    Rules:
    1. Use only information explicitly supported by the retrieved hotel policy information.
    2. Do not use outside knowledge or assumptions.
    3. Include all relevant information needed to answer the guest's question completely.
    4. Do not omit important conditions, exclusions, fees, limits, exceptions, or restrictions.
    5. Focus only on information directly relevant to the user's question.
    6. Do not include unrelated information from the retrieved documents.
    7. Ensure property-specific information applies to the correct hotel.
    8. Distinguish property-specific policies from general hotel policies.
    9. Keep the answer concise, clear, and professional.
    10. Do not invent charges, refunds, cancellation deadlines, amenities, or policy details.
    11. If information is insufficient, say:
        "The available policy documents do not contain enough information to answer this question."
        If retrieved information conflicts, mention the conflict.

    Answer:
    """

    return model.invoke(prompt)


# Complete optimized RAG pipeline
def rag(
    query,
    k=3,
    model_name="gpt-4o-mini",
    temperature=0.0,
    top_p=1.0,
    max_tokens=512,
    vectorstore=None
):
    model = ChatOpenAI(
        model=model_name,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE")
    )

    retrieved_chunks = retrieve(
        query=query,
        k=k,
        vectorstore=vectorstore
    )

    answer = generate(
        query=query,
        retrieved_chunks=retrieved_chunks,
        model=model
    )

    return answer.content, retrieved_chunks
