"""Build a retrieval plan from entity matches and query intent.

The router does not query data stores or generate answers.
"""
from entity_index import build_entity_index
from tier1_matcher import match_entities
from tier2_classifier import classify_intent
from tier3_fallback import fallback_plan

_INDEX = None


def get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = build_entity_index()
    return _INDEX


def route(question: str) -> dict:
    index = get_index()

    entities = match_entities(question, index)             # Tier 1
    plan = classify_intent(question, entities)             # Tier 2

    if plan["confidence"] == "ambiguous":                  # Tier 3 (LLM) only when needed
        t3 = fallback_plan(question)
        t3["tier"] = "tier3"
        t3["tier3_source"] = t3.pop("source")
        t3["details"]["tier1_entities"] = entities
        return t3

    plan["tier"] = "tier2"
    return plan


# Small manual smoke-test harness.
TEST_QUESTIONS = [
    "How many coils failed quality testing?",
    "Which equipment produced coil C10234?",
    "What does the SOP for hot rolling mill startup say?",
    "Why did the Reheating Furnace fail last month?",
    "What does IS 2062 cover?",
    "Show me all deviations linked to the Coiler Unit",
    "Has EQ-RHF-01 had any recent failures and what was the root cause?",
    "What's going on with production?",
    "Tell me about quality issues this quarter",
    "Is everything okay?",
]

if __name__ == "__main__":
    tier_counts = {"tier2": 0, "tier3": 0}
    rows = []

    for q in TEST_QUESTIONS:
        plan = route(q)
        ents = plan["details"].get("matched_entities", plan["details"].get("tier1_entities", []))
        ent_str = ", ".join(f"{e['entity_type']}:{e['entity_id']}('{e['matched_text']}')" for e in ents) or "-"
        tier = plan["tier"] + (f"/{plan['tier3_source']}" if plan["tier"] == "tier3" else "")
        tier_counts[plan["tier"]] += 1
        rows.append((q, tier, plan["layers"], plan["confidence"]))

        print("=" * 86)
        print(f"Q: {q}")
        print(f"   entities   : {ent_str}")
        print(f"   layers     : {plan['layers']}")
        print(f"   confidence : {plan['confidence']}")
        print(f"   plan tier  : {tier}")
        if plan["tier"] == "tier3":                     # show the REAL model output
            d = plan["details"]
            print(f"   model      : {plan.get('model', '-')}")
            print(f"   reason     : {d.get('reason', '-')}")
            print(f"   focus      : structured_systems={d.get('structured_systems', [])} "
                  f"graph_focus={d.get('graph_focus', '')!r} "
                  f"document_filters={d.get('document_filters', {})}")
            print(f"   search_text: {d.get('search_text', '-')!r}")
            if d.get("error"):
                print(f"   error      : {d['error']}")

    print("\n" + "=" * 100)
    print("FINAL SUMMARY TABLE")
    print("=" * 100)
    print(f"  {'question':<52} {'tier':<20} {'layers':<28} confidence")
    print("  " + "-" * 98)
    for q, tier, layers, conf in rows:
        qs = (q[:49] + "...") if len(q) > 52 else q
        print(f"  {qs:<52} {tier:<20} {','.join(layers):<28} {conf}")

    unresolvable = [(q, tier) for q, tier, _, conf in rows if conf == "unresolvable"]
    print(f"\n  resolved at Tier 2 (rules, no LLM) : {tier_counts['tier2']}/10")
    print(f"  needed Tier 3 fallback             : {tier_counts['tier3']}/10")
    print(f"  UNRESOLVABLE even after Tier 3     : {len(unresolvable)}/10")
    for q, tier in unresolvable:
        print(f"    - {q!r}  [{tier}]")
    if unresolvable:
        print("  ^ the synthesizer must ask a clarifying question for these instead of attempting an answer.")
