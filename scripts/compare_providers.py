#!/usr/bin/env python3
"""
Compare Local vs OpenAI Embeddings for Biblical Terms

Tests:
1. Word-only embeddings
2. Word + definition embeddings
3. Multilingual support (Greek, Hebrew, rare languages)
4. Optional: realistic overlapping definitions (--overlap)
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np

# SIMPLE definitions - clear and distinct
SIMPLE_GROUPS = [
    ("Love/Affection", [
        ("love", "deep caring for someone"),
        ("affection", "warm feelings toward another"),
        ("cherish", "hold dear and value highly"),
        ("ἀγάπη", "Greek: selfless love"),
        ("אַהֲבָה", "Hebrew: love"),
        ("upendo", "Swahili: love"),
        ("kasih", "Indonesian: affection"),
    ]),
    ("Faith/Belief", [
        ("faith", "confident trust in God"),
        ("belief", "acceptance as true"),
        ("trust", "firm reliance"),
        ("πίστις", "Greek: faith"),
        ("אֱמוּנָה", "Hebrew: faithfulness"),
        ("imani", "Swahili: belief"),
        ("iman", "Indonesian: faith"),
    ]),
    ("Sin/Evil", [
        ("sin", "wrongdoing against God"),
        ("evil", "morally bad"),
        ("wickedness", "being morally corrupt"),
        ("ἁμαρτία", "Greek: missing the mark"),
        ("חֵטְא", "Hebrew: sin"),
        ("dhambi", "Swahili: sin"),
        ("dosa", "Indonesian: sin"),
    ]),
    ("Salvation", [
        ("salvation", "being saved or rescued"),
        ("redemption", "being bought back"),
        ("deliverance", "rescue from danger"),
        ("σωτηρία", "Greek: deliverance"),
        ("יְשׁוּעָה", "Hebrew: salvation"),
        ("wokovu", "Swahili: salvation"),
        ("keselamatan", "Indonesian: safety"),
    ]),
    ("Grace/Mercy", [
        ("grace", "undeserved kindness"),
        ("mercy", "not punishing as deserved"),
        ("compassion", "sympathy for suffering"),
        ("χάρις", "Greek: favor"),
        ("חֶסֶד", "Hebrew: steadfast kindness"),
        ("neema", "Swahili: grace"),
        ("kasih karunia", "Indonesian: grace"),
    ]),
    ("Righteousness", [
        ("righteousness", "being morally right"),
        ("holiness", "being sacred and pure"),
        ("purity", "being clean and unstained"),
        ("δικαιοσύνη", "Greek: justice"),
        ("צֶדֶק", "Hebrew: righteousness"),
        ("haki", "Swahili: justice"),
        ("kebenaran", "Indonesian: truth"),
    ]),
    ("Peace/Rest", [
        ("peace", "calm and harmony"),
        ("rest", "relaxation from work"),
        ("calm", "free from disturbance"),
        ("εἰρήνη", "Greek: peace"),
        ("שָׁלוֹם", "Hebrew: wholeness"),
        ("amani", "Swahili: peace"),
        ("damai", "Indonesian: peace"),
    ]),
    ("God/Divine", [
        ("God", "the supreme being"),
        ("Lord", "master and ruler"),
        ("Almighty", "having unlimited power"),
        ("θεός", "Greek: deity"),
        ("אֱלֹהִים", "Hebrew: God"),
        ("Mungu", "Swahili: God"),
        ("Tuhan", "Indonesian: Lord"),
    ]),
    ("Jesus/Messiah", [
        ("Jesus", "the Son of God"),
        ("Christ", "the anointed one"),
        ("Messiah", "the promised deliverer"),
        ("Χριστός", "Greek: anointed"),
        ("מָשִׁיחַ", "Hebrew: anointed one"),
        ("Yesu", "Swahili: Jesus"),
        ("Kristus", "Indonesian: Christ"),
    ]),
    ("Spirit/Holy", [
        ("Spirit", "non-physical being"),
        ("holy", "sacred and set apart"),
        ("divine", "relating to deity"),
        ("πνεῦμα", "Greek: breath/spirit"),
        ("רוּחַ", "Hebrew: wind/spirit"),
        ("Roho", "Swahili: spirit"),
        ("Roh", "Indonesian: spirit"),
    ]),
    ("Prophet/Messenger", [
        ("prophet", "one who proclaims"),
        ("messenger", "one who carries news"),
        ("oracle", "divine message"),
        ("προφήτης", "Greek: spokesperson"),
        ("נָבִיא", "Hebrew: prophet"),
        ("nabii", "Swahili: prophet"),
        ("nabi", "Indonesian: prophet"),
    ]),
    ("Prayer/Worship", [
        ("prayer", "talking to God"),
        ("worship", "showing reverence"),
        ("praise", "expressing approval"),
        ("προσευχή", "Greek: prayer"),
        ("תְּפִלָּה", "Hebrew: prayer"),
        ("sala", "Swahili: prayer"),
        ("doa", "Indonesian: prayer"),
    ]),
    ("Kingdom/Rule", [
        ("kingdom", "territory of a king"),
        ("reign", "period of ruling"),
        ("throne", "royal seat"),
        ("βασιλεία", "Greek: royal rule"),
        ("מַלְכוּת", "Hebrew: kingship"),
        ("ufalme", "Swahili: kingdom"),
        ("kerajaan", "Indonesian: kingdom"),
    ]),
    ("Covenant/Promise", [
        ("covenant", "formal agreement"),
        ("promise", "commitment to do something"),
        ("oath", "sworn statement"),
        ("διαθήκη", "Greek: testament"),
        ("בְּרִית", "Hebrew: covenant"),
        ("agano", "Swahili: covenant"),
        ("perjanjian", "Indonesian: agreement"),
    ]),
    ("Temple/Sanctuary", [
        ("temple", "building for worship"),
        ("sanctuary", "sacred place"),
        ("altar", "table for offerings"),
        ("ναός", "Greek: shrine"),
        ("מִקְדָּשׁ", "Hebrew: holy place"),
        ("hekalu", "Swahili: temple"),
        ("bait suci", "Indonesian: temple"),
    ]),
    ("Heaven/Paradise", [
        ("heaven", "sky or divine realm"),
        ("paradise", "ideal place"),
        ("eternal", "without end"),
        ("οὐρανός", "Greek: sky/heaven"),
        ("שָׁמַיִם", "Hebrew: heavens"),
        ("mbingu", "Swahili: heaven"),
        ("surga", "Indonesian: heaven"),
    ]),
    ("Joy/Gladness", [
        ("joy", "feeling of happiness"),
        ("gladness", "being pleased"),
        ("rejoice", "express happiness"),
        ("χαρά", "Greek: delight"),
        ("שִׂמְחָה", "Hebrew: gladness"),
        ("furaha", "Swahili: joy"),
        ("sukacita", "Indonesian: joy"),
    ]),
    ("Fear/Awe", [
        ("fear", "being afraid"),
        ("awe", "amazed respect"),
        ("reverence", "deep respect"),
        ("φόβος", "Greek: fear"),
        ("יִרְאָה", "Hebrew: fear/awe"),
        ("hofu", "Swahili: fear"),
        ("takut", "Indonesian: fear"),
    ]),
    ("Forgiveness", [
        ("forgive", "stop being angry at"),
        ("pardon", "excuse an offense"),
        ("absolve", "free from blame"),
        ("ἄφεσις", "Greek: release"),
        ("סְלִיחָה", "Hebrew: pardon"),
        ("msamaha", "Swahili: forgiveness"),
        ("pengampunan", "Indonesian: pardon"),
    ]),
    ("Truth/Wisdom", [
        ("truth", "what is factual"),
        ("wisdom", "good judgment"),
        ("knowledge", "information understood"),
        ("ἀλήθεια", "Greek: reality"),
        ("אֱמֶת", "Hebrew: truth"),
        ("ukweli", "Swahili: truth"),
        ("kebenaran", "Indonesian: truth"),
    ]),
]

# OVERLAPPING definitions - realistic natural overlap in meanings
# These are how real definitions would be written, with natural semantic connections
OVERLAP_GROUPS = [
    ("Love/Affection", [
        # Natural: love definitions often mention care, devotion, commitment
        ("love", "to care deeply for someone and desire their good"),
        ("affection", "tender feelings of fondness and attachment"),
        ("cherish", "to care for tenderly and hold in one's heart"),
        ("ἀγάπη", "Greek: selfless love that seeks the good of others"),
        ("אַהֲבָה", "Hebrew: devoted attachment and loyalty"),
        ("upendo", "Swahili: heartfelt care and devotion"),
        ("kasih", "Indonesian: tender care and attachment"),
    ]),
    ("Faith/Belief", [
        # Natural: faith involves trust, confidence, relying on someone
        ("faith", "confident trust in someone or something unseen"),
        ("belief", "holding something to be true with conviction"),
        ("trust", "confident reliance on the character of another"),
        ("πίστις", "Greek: trusting confidence and loyal commitment"),
        ("אֱמוּנָה", "Hebrew: steadfast trust and reliability"),
        ("imani", "Swahili: confident conviction"),
        ("iman", "Indonesian: trusting belief"),
    ]),
    ("Sin/Evil", [
        # Natural: sin definitions mention wrongdoing, falling short, offense
        ("sin", "falling short of what is right, offense against God"),
        ("evil", "that which causes harm and opposes good"),
        ("wickedness", "deliberately choosing to do wrong"),
        ("ἁμαρτία", "Greek: falling short of the goal, missing the mark"),
        ("חֵטְא", "Hebrew: missing the way, going astray"),
        ("dhambi", "Swahili: offense and wrongdoing"),
        ("dosa", "Indonesian: fault and transgression"),
    ]),
    ("Salvation", [
        # Natural: salvation involves being saved FROM something (sin/danger)
        ("salvation", "being rescued from danger or destruction"),
        ("redemption", "being set free by paying a price"),
        ("deliverance", "being rescued from harm or captivity"),
        ("σωτηρία", "Greek: rescue and preservation from harm"),
        ("יְשׁוּעָה", "Hebrew: rescue and victory over enemies"),
        ("wokovu", "Swahili: being saved from danger"),
        ("keselamatan", "Indonesian: safety and rescue"),
    ]),
    ("Grace/Mercy", [
        # Natural: grace/mercy involve kindness despite not deserving it
        ("grace", "kindness given freely to the undeserving"),
        ("mercy", "withholding deserved punishment out of kindness"),
        ("compassion", "feeling moved by another's suffering to help"),
        ("χάρις", "Greek: generous gift freely given"),
        ("חֶסֶד", "Hebrew: loyal kindness beyond obligation"),
        ("neema", "Swahili: unearned favor"),
        ("kasih karunia", "Indonesian: gracious kindness"),
    ]),
    ("Righteousness", [
        # Natural: righteousness involves being right, just, upright
        ("righteousness", "acting in accordance with what is right"),
        ("holiness", "being set apart and morally pure"),
        ("purity", "being free from moral corruption"),
        ("δικαιοσύνη", "Greek: acting justly and being in right standing"),
        ("צֶדֶק", "Hebrew: conformity to the proper standard"),
        ("haki", "Swahili: acting justly and fairly"),
        ("kebenaran", "Indonesian: being right and true"),
    ]),
    ("Peace/Rest", [
        # Natural: peace involves absence of conflict, wholeness, harmony
        ("peace", "freedom from conflict and a state of harmony"),
        ("rest", "ceasing from labor and finding refreshment"),
        ("calm", "a quiet state free from agitation"),
        ("εἰρήνη", "Greek: harmony and well-being"),
        ("שָׁלוֹם", "Hebrew: completeness and well-being in relationships"),
        ("amani", "Swahili: security and harmony"),
        ("damai", "Indonesian: tranquility and harmony"),
    ]),
    ("God/Divine", [
        # Natural: God definitions involve supreme, creator, ruler
        ("God", "the supreme being who created all things"),
        ("Lord", "one who has authority and deserves obedience"),
        ("Almighty", "possessing all power over creation"),
        ("θεός", "Greek: the supreme deity"),
        ("אֱלֹהִים", "Hebrew: the powerful creator"),
        ("Mungu", "Swahili: the supreme creator"),
        ("Tuhan", "Indonesian: the master and ruler"),
    ]),
    ("Jesus/Messiah", [
        # Natural: Messiah involves anointed, chosen, sent to deliver
        ("Jesus", "the one sent to rescue humanity"),
        ("Christ", "the one chosen and set apart for a mission"),
        ("Messiah", "the long-awaited deliverer of the people"),
        ("Χριστός", "Greek: the one anointed for a special purpose"),
        ("מָשִׁיחַ", "Hebrew: the anointed king and deliverer"),
        ("Yesu", "Swahili: the sent rescuer"),
        ("Kristus", "Indonesian: the anointed one"),
    ]),
    ("Spirit/Holy", [
        # Natural: spirit involves breath, life, non-physical nature
        ("Spirit", "the non-physical life force or divine presence"),
        ("holy", "set apart as sacred and belonging to God"),
        ("divine", "having the nature or character of God"),
        ("πνεῦμα", "Greek: breath, wind, or invisible life force"),
        ("רוּחַ", "Hebrew: breath, wind, or animating force"),
        ("Roho", "Swahili: the breath of life"),
        ("Roh", "Indonesian: the animating spirit"),
    ]),
    ("Prophet/Messenger", [
        # Natural: prophet involves speaking for God, proclaiming truth
        ("prophet", "one who speaks on behalf of another"),
        ("messenger", "one sent to deliver important news"),
        ("oracle", "a message from a divine source"),
        ("προφήτης", "Greek: one who speaks forth a message"),
        ("נָבִיא", "Hebrew: one called to proclaim"),
        ("nabii", "Swahili: one who announces"),
        ("nabi", "Indonesian: a spokesman"),
    ]),
    ("Prayer/Worship", [
        # Natural: prayer involves communication, petition, adoration
        ("prayer", "speaking to God to express needs or gratitude"),
        ("worship", "showing honor and devotion to what is supreme"),
        ("praise", "expressing admiration and gratitude"),
        ("προσευχή", "Greek: addressing God with requests"),
        ("תְּפִלָּה", "Hebrew: turning to God in speech"),
        ("sala", "Swahili: calling upon God"),
        ("doa", "Indonesian: speaking requests to God"),
    ]),
    ("Kingdom/Rule", [
        # Natural: kingdom involves authority, domain, subjects
        ("kingdom", "the domain where a ruler's authority extends"),
        ("reign", "the exercise of royal authority"),
        ("throne", "the seat symbolizing royal authority"),
        ("βασιλεία", "Greek: the sphere of royal rule"),
        ("מַלְכוּת", "Hebrew: sovereign rule and dominion"),
        ("ufalme", "Swahili: the ruler's domain"),
        ("kerajaan", "Indonesian: the royal realm"),
    ]),
    ("Covenant/Promise", [
        # Natural: covenant involves agreement, commitment, binding
        ("covenant", "a binding agreement between parties"),
        ("promise", "a declaration of commitment to do something"),
        ("oath", "a solemn pledge to fulfill a commitment"),
        ("διαθήκη", "Greek: a formal arrangement or will"),
        ("בְּרִית", "Hebrew: a binding agreement with obligations"),
        ("agano", "Swahili: a mutual commitment"),
        ("perjanjian", "Indonesian: a formal agreement"),
    ]),
    ("Temple/Sanctuary", [
        # Natural: temple involves sacred space, worship, presence
        ("temple", "a structure dedicated to divine worship"),
        ("sanctuary", "a sacred space set apart for the divine"),
        ("altar", "a structure for presenting offerings"),
        ("ναός", "Greek: a dwelling for the divine"),
        ("מִקְדָּשׁ", "Hebrew: a consecrated place"),
        ("hekalu", "Swahili: a house for worship"),
        ("bait suci", "Indonesian: a sacred house"),
    ]),
    ("Heaven/Paradise", [
        # Natural: heaven involves divine realm, blessed state
        ("heaven", "the realm where the divine dwells"),
        ("paradise", "an ideal state of blessing and happiness"),
        ("eternal", "existing beyond the bounds of time"),
        ("οὐρανός", "Greek: the realm above the earth"),
        ("שָׁמַיִם", "Hebrew: the heights where God dwells"),
        ("mbingu", "Swahili: the realm above"),
        ("surga", "Indonesian: the blessed realm"),
    ]),
    ("Joy/Gladness", [
        # Natural: joy involves happiness, delight, positive emotion
        ("joy", "deep happiness that fills the heart"),
        ("gladness", "the state of being pleased and happy"),
        ("rejoice", "to express happiness openly"),
        ("χαρά", "Greek: gladness and delight"),
        ("שִׂמְחָה", "Hebrew: happiness expressed outwardly"),
        ("furaha", "Swahili: deep happiness"),
        ("sukacita", "Indonesian: inner delight"),
    ]),
    ("Fear/Awe", [
        # Natural: fear involves respect, caution, being overwhelmed
        ("fear", "a response to something powerful or threatening"),
        ("awe", "being overwhelmed by something majestic"),
        ("reverence", "deep respect for something greater"),
        ("φόβος", "Greek: response to what is powerful"),
        ("יִרְאָה", "Hebrew: respectful response to greatness"),
        ("hofu", "Swahili: response to the overwhelming"),
        ("takut", "Indonesian: respectful caution"),
    ]),
    ("Forgiveness", [
        # Natural: forgiveness involves releasing, pardoning, restoring
        ("forgive", "to release someone from the debt of their wrong"),
        ("pardon", "to excuse an offense and not hold it against"),
        ("absolve", "to declare free from guilt or blame"),
        ("ἄφεσις", "Greek: releasing from a debt or obligation"),
        ("סְלִיחָה", "Hebrew: passing over an offense"),
        ("msamaha", "Swahili: releasing from debt"),
        ("pengampunan", "Indonesian: pardoning an offense"),
    ]),
    ("Truth/Wisdom", [
        # Natural: truth involves reality, accuracy, reliability
        ("truth", "what corresponds to reality and fact"),
        ("wisdom", "the ability to apply knowledge rightly"),
        ("knowledge", "accurate understanding of something"),
        ("ἀλήθεια", "Greek: what is real and reliable"),
        ("אֱמֶת", "Hebrew: what is firm and dependable"),
        ("ukweli", "Swahili: what is real"),
        ("kebenaran", "Indonesian: what is accurate"),
    ]),
]


def cosine_distance(a, b):
    """Compute cosine distance between two vectors."""
    return 1.0 - float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def test_clustering(embeddings_by_group):
    """
    Measure how well groups cluster together.
    Returns (avg_in_group_dist, avg_out_group_dist, ratio).
    Lower ratio = better clustering.
    """
    in_group_dists = []
    out_group_dists = []
    
    all_embeddings = []
    group_labels = []
    
    for g_idx, group_embs in enumerate(embeddings_by_group):
        for emb in group_embs:
            all_embeddings.append(emb)
            group_labels.append(g_idx)
    
    all_embeddings = np.array(all_embeddings)
    
    for i in range(len(all_embeddings)):
        for j in range(i + 1, len(all_embeddings)):
            dist = cosine_distance(all_embeddings[i], all_embeddings[j])
            if group_labels[i] == group_labels[j]:
                in_group_dists.append(dist)
            else:
                out_group_dists.append(dist)
    
    avg_in = np.mean(in_group_dists) if in_group_dists else 0
    avg_out = np.mean(out_group_dists) if out_group_dists else 1
    ratio = avg_in / avg_out if avg_out > 0 else float('inf')
    
    return avg_in, avg_out, ratio


def test_provider(provider_name, encode_fn, test_groups, use_definitions=False):
    """Test a provider with either words-only or words+definitions."""
    mode = "word+definition" if use_definitions else "word-only"
    print(f"\n  Testing: {mode}")
    
    embeddings_by_group = []
    for group_name, word_pairs in test_groups:
        if use_definitions:
            texts = [f"{word}: {defn}" for word, defn in word_pairs]
        else:
            texts = [word for word, defn in word_pairs]
        
        embs = encode_fn(texts)
        embeddings_by_group.append(embs)
    
    avg_in, avg_out, ratio = test_clustering(embeddings_by_group)
    
    print(f"    In-group:  {avg_in:.4f}")
    print(f"    Out-group: {avg_out:.4f}")
    print(f"    Ratio:     {ratio:.4f}")
    
    return {
        "mode": mode,
        "in_group": avg_in,
        "out_group": avg_out,
        "ratio": ratio,
    }


def test_local(test_groups):
    """Test local sentence-transformers."""
    print("\n" + "=" * 60)
    print("LOCAL: paraphrase-multilingual-MiniLM-L12-v2")
    print("=" * 60)
    
    from sentence_transformers import SentenceTransformer
    import torch
    
    device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device=device)
    print(f"  Dimensions: {model.get_sentence_embedding_dimension()}")
    print(f"  Device: {device}")
    
    def encode_fn(texts):
        return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    
    result_word = test_provider("local", encode_fn, test_groups, use_definitions=False)
    result_def = test_provider("local", encode_fn, test_groups, use_definitions=True)
    
    return {
        "provider": "local",
        "model": "paraphrase-multilingual-MiniLM-L12-v2",
        "dims": model.get_sentence_embedding_dimension(),
        "word_only": result_word,
        "word_def": result_def,
    }


def test_openai_small(test_groups):
    """Test OpenAI text-embedding-3-small."""
    print("\n" + "=" * 60)
    print("OPENAI: text-embedding-3-small")
    print("=" * 60)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("  ✗ OPENAI_API_KEY not set, skipping")
        return None
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    dims = 512
    print(f"  Dimensions: {dims}")
    
    def encode_fn(texts):
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
            dimensions=dims
        )
        embs = np.array([e.embedding for e in response.data])
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        return embs / norms
    
    result_word = test_provider("openai-small", encode_fn, test_groups, use_definitions=False)
    result_def = test_provider("openai-small", encode_fn, test_groups, use_definitions=True)
    
    return {
        "provider": "openai-small",
        "model": "text-embedding-3-small",
        "dims": dims,
        "word_only": result_word,
        "word_def": result_def,
    }


def test_openai_large(test_groups):
    """Test OpenAI text-embedding-3-large."""
    print("\n" + "=" * 60)
    print("OPENAI: text-embedding-3-large")
    print("=" * 60)
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("  ✗ OPENAI_API_KEY not set, skipping")
        return None
    
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    dims = 1024
    print(f"  Dimensions: {dims}")
    
    def encode_fn(texts):
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=texts,
            dimensions=dims
        )
        embs = np.array([e.embedding for e in response.data])
        norms = np.linalg.norm(embs, axis=1, keepdims=True)
        return embs / norms
    
    result_word = test_provider("openai-large", encode_fn, test_groups, use_definitions=False)
    result_def = test_provider("openai-large", encode_fn, test_groups, use_definitions=True)
    
    return {
        "provider": "openai-large",
        "model": "text-embedding-3-large",
        "dims": dims,
        "word_only": result_word,
        "word_def": result_def,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compare embedding providers for biblical terms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python compare_providers.py                  # Simple definitions
    python compare_providers.py --overlap        # Realistic overlapping definitions
        """
    )
    parser.add_argument(
        "--overlap", 
        action="store_true",
        help="Use realistic overlapping definitions (tests contextual understanding)"
    )
    args = parser.parse_args()
    
    # Choose test groups
    if args.overlap:
        test_groups = OVERLAP_GROUPS
        mode_desc = "OVERLAPPING (realistic natural overlap)"
    else:
        test_groups = SIMPLE_GROUPS
        mode_desc = "SIMPLE (clean, distinct definitions)"
    
    print("=" * 60)
    print("EMBEDDING PROVIDER COMPARISON")
    print("Multilingual Biblical Terms Test")
    print("=" * 60)
    
    total_words = sum(len(words) for _, words in test_groups)
    print(f"\nDefinition mode: {mode_desc}")
    print(f"Test: {len(test_groups)} semantic groups, {total_words} words")
    print("Languages: English, Greek, Hebrew, Swahili, Indonesian")
    
    print("\nSample groups:")
    for name, words in test_groups[:2]:
        print(f"\n  {name}:")
        for word, defn in words[:3]:
            print(f"    {word}: {defn[:50]}...")
    
    results = []
    
    # Test all providers
    local_result = test_local(test_groups)
    if local_result:
        results.append(local_result)
    
    openai_small = test_openai_small(test_groups)
    if openai_small:
        results.append(openai_small)
    
    openai_large = test_openai_large(test_groups)
    if openai_large:
        results.append(openai_large)
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if not results:
        print("\n✗ No results to compare")
        return
    
    # Word-only comparison
    print("\n📊 WORD-ONLY (just the term, no definition)")
    print("-" * 60)
    print(f"| {'Provider':<15} | {'Model':<25} | {'Dims':<5} | {'Ratio':<8} |")
    print(f"|{'-'*17}|{'-'*27}|{'-'*7}|{'-'*10}|")
    
    word_results = [(r["provider"], r["model"], r["dims"], r["word_only"]["ratio"]) for r in results]
    word_results.sort(key=lambda x: x[3])
    
    for provider, model, dims, ratio in word_results:
        print(f"| {provider:<15} | {model[:25]:<25} | {dims:<5} | {ratio:<8.4f} |")
    
    # Word+definition comparison
    print("\n📊 WORD + DEFINITION (term with meaning)")
    print("-" * 60)
    print(f"| {'Provider':<15} | {'Model':<25} | {'Dims':<5} | {'Ratio':<8} |")
    print(f"|{'-'*17}|{'-'*27}|{'-'*7}|{'-'*10}|")
    
    def_results = [(r["provider"], r["model"], r["dims"], r["word_def"]["ratio"]) for r in results]
    def_results.sort(key=lambda x: x[3])
    
    for provider, model, dims, ratio in def_results:
        print(f"| {provider:<15} | {model[:25]:<25} | {dims:<5} | {ratio:<8.4f} |")
    
    # Best overall
    print("\n" + "=" * 60)
    print("🏆 WINNERS")
    print("=" * 60)
    
    best_word = min(results, key=lambda r: r["word_only"]["ratio"])
    best_def = min(results, key=lambda r: r["word_def"]["ratio"])
    
    print(f"\n  Word-only:       {best_word['provider']} (ratio={best_word['word_only']['ratio']:.4f})")
    print(f"  Word+definition: {best_def['provider']} (ratio={best_def['word_def']['ratio']:.4f})")
    
    # Does definition help?
    print("\n📈 DOES ADDING DEFINITION HELP?")
    print("-" * 60)
    for r in results:
        word_ratio = r["word_only"]["ratio"]
        def_ratio = r["word_def"]["ratio"]
        improvement = (word_ratio - def_ratio) / word_ratio * 100
        better = "✓ Yes" if improvement > 0 else "✗ No"
        print(f"  {r['provider']:<15}: {better} ({improvement:+.1f}%)")
    
    # Key insight
    print("\n💡 KEY INSIGHT")
    print("-" * 60)
    if args.overlap:
        print("  Testing with REALISTIC OVERLAPPING definitions.")
        print("  This tests: Can the model understand context, not just match words?")
        print("  Example: 'love' defined as 'care deeply' vs 'grace' as 'kindness'")
        print("  Both use positive words, but should cluster differently.")
    else:
        print("  Testing with SIMPLE DISTINCT definitions.")
        print("  Run with --overlap to test realistic overlapping definitions.")


if __name__ == "__main__":
    main()
