import json
import re
from typing import Any

from google import genai
from google.genai import types

from ..config import get_settings

from .catalog import (
    HOME_CATALOG,
    PARTY_CATALOG,
    JEWELRY_CATALOG,
    search_url,
)

from .prompts import (
    home_prompt,
    party_prompt,
    jewelry_prompt,
)


def extract_json(
    text: str,
) -> dict[str, Any]:

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError(
            "Gemini did not return JSON"
        )

    return json.loads(
        match.group(0)
    )


def normalize_result(
    data: dict,
    planner: str,
    budget: int,
    ai_generated: bool,
    note: str | None = None,
) -> dict:

    items = []

    raw_items = data.get(
        "items",
        [],
    )

    for raw in raw_items:

        try:

            platform = str(
                raw.get(
                    "platform",
                    "Amazon",
                )
            )

            title = str(
                raw.get(
                    "title",
                    "Recommendation",
                )
            )

            item = {
                "title": title,

                "category": str(
                    raw.get(
                        "category",
                        "General",
                    )
                ),

                "estimated_price": max(
                    0,
                    int(
                        raw.get(
                            "estimated_price",
                            0,
                        )
                    ),
                ),

                "platform": platform,

                "reason": str(
                    raw.get(
                        "reason",
                        "Fits the requested budget and preferences.",
                    )
                ),

                "search_url": str(
                    raw.get(
                        "search_url",
                        search_url(
                            platform,
                            title,
                        ),
                    )
                ),
            }

            items.append(item)

        except (
            TypeError,
            ValueError,
        ):
            continue

    total = sum(
        item["estimated_price"]
        for item in items
    )

    allocation = {}

    for key, value in (
        data.get("allocation") or {}
    ).items():

        try:
            allocation[str(key)] = max(
                0,
                int(value),
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

    return {
        "planner": planner,

        "budget": budget,

        "allocation": allocation,

        "total_estimated": min(
            total,
            budget,
        ),

        "summary": str(
            data.get(
                "summary",
                "Budget-aware recommendations generated.",
            )
        ),

        "items": items,

        "ai_generated": ai_generated,

        "note": note,
    }


def fallback(
    planner: str,
    budget: int,
    payload: dict,
) -> dict:

    if planner == "home":

        catalog = HOME_CATALOG

        allocation = {
            "furniture": int(
                budget * 0.40
            ),
            "lighting": int(
                budget * 0.20
            ),
            "decor": int(
                budget * 0.20
            ),
            "cooling": int(
                budget * 0.20
            ),
        }

    elif planner == "party":

        catalog = PARTY_CATALOG

        allocation = {
            "catering": int(
                budget * 0.45
            ),
            "decoration": int(
                budget * 0.15
            ),
            "venue": int(
                budget * 0.25
            ),
            "entertainment": int(
                budget * 0.15
            ),
        }

    else:

        catalog = JEWELRY_CATALOG

        allocation = {
            "earrings": int(
                budget * 0.35
            ),
            "necklace": int(
                budget * 0.40
            ),
            "bangles": int(
                budget * 0.25
            ),
        }

    selected_items = []

    running_total = 0

    for (
        title,
        category,
        price,
        platform,
    ) in catalog:

        adjusted_price = price

        if (
            planner == "party"
            and category == "Catering"
        ):

            guests = int(
                payload.get(
                    "guest_count",
                    1,
                )
            )

            adjusted_price = (
                price
                * max(
                    1,
                    min(
                        guests,
                        20,
                    ),
                )
            )

        if (
            running_total
            + adjusted_price
            <= budget
        ):

            selected_items.append(
                {
                    "title": title,

                    "category": category,

                    "estimated_price": adjusted_price,

                    "platform": platform,

                    "reason": (
                        "Selected from the built-in "
                        "PocketSmart demo catalog as "
                        "a budget-compatible option."
                    ),

                    "search_url": search_url(
                        platform,
                        title,
                    ),
                }
            )

            running_total += (
                adjusted_price
            )

    return {
        "planner": planner,

        "budget": budget,

        "allocation": allocation,

        "total_estimated": running_total,

        "summary": (
            "Fallback recommendations are based "
            "on the built-in demo catalog. "
            "Prices are estimates."
        ),

        "items": selected_items,

        "ai_generated": False,

        "note": (
            "Gemini recommendations were unavailable. "
            "No live price or availability is implied."
        ),
    }


async def generate(
    planner: str,
    payload: dict,
    image_bytes: bytes | None = None,
    image_mime: str | None = None,
) -> dict:

    settings = get_settings()

    budget = int(
        payload["budget"]
    )

    if (
        not settings.ai_enabled
        or not settings.gemini_api_key
    ):

        return fallback(
            planner,
            budget,
            payload,
        )

    prompt_functions = {
        "home": home_prompt,
        "party": party_prompt,
        "jewelry": jewelry_prompt,
    }

    prompt_function = prompt_functions[
        planner
    ]

    prompt = prompt_function(
        payload
    )

    try:

        client = genai.Client(
            api_key=settings.gemini_api_key
        )

        contents: list[Any] = [
            prompt
        ]

        if image_bytes:

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=(
                        image_mime
                        or "image/jpeg"
                    ),
                )
            )

        response = await (
            client.aio.models.generate_content(
                model=settings.gemini_model,

                contents=contents,

                config=types.GenerateContentConfig(
                    temperature=0.3,

                    response_mime_type="application/json",
                ),
            )
        )

        response_text = (
            response.text
            or ""
        )

        parsed = extract_json(
            response_text
        )

        result = normalize_result(
            parsed,
            planner,
            budget,
            True,
            (
                "AI-generated estimates. "
                "Verify prices and availability "
                "on the linked platform."
            ),
        )

        if not result["items"]:
            raise ValueError(
                "Gemini returned no items"
            )

        return result

    except Exception:

        return fallback(
            planner,
            budget,
            payload,
        )