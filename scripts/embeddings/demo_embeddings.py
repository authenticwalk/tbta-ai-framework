#!/usr/bin/env python3
"""
TBTA Embedding Demo

Interactive CLI to teach and demonstrate embeddings for Bible translation.

Usage:
    python scripts/demo_embeddings.py teach              # What are embeddings?
    python scripts/demo_embeddings.py experiment         # Compare stem vs stem+gloss
    python scripts/demo_embeddings.py match              # Concept-to-Strong's matching
    python scripts/demo_embeddings.py search "phrase"    # User text to concept search

Requirements:
    pip install sentence-transformers numpy
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Missing: pip install sentence-transformers")
    sys.exit(1)

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # scripts/embeddings -> scripts -> tbta-ai-framework
DB_DIR = PROJECT_DIR / "databases"
EMB_BASE_DIR = PROJECT_DIR / "databases" / "embeddings"

# Default embedding provider (can be overridden by --provider)
DEFAULT_PROVIDER = "openai"

# Model config - multilingual performs better on biblical terms (90% vs 80%)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
model: Optional[SentenceTransformer] = None

# OpenAI config
OPENAI_MODEL = "text-embedding-3-small"
OPENAI_DIMS = 512
openai_client = None

# Optional: sqlite-vec for pre-computed embeddings
try:
    import apsw
    import sqlite_vec
    HAS_SQLITE_VEC = True
except ImportError:
    HAS_SQLITE_VEC = False

# Global embedding directory and provider (set by --provider arg)
EMB_DIR: Optional[Path] = None
CURRENT_PROVIDER: str = DEFAULT_PROVIDER

def get_emb_dir() -> Path:
    """Get the current embedding directory."""
    global EMB_DIR
    if EMB_DIR is None:
        EMB_DIR = EMB_BASE_DIR / DEFAULT_PROVIDER
    return EMB_DIR

def set_provider(provider: str):
    """Set the embedding provider/directory."""
    global EMB_DIR, CURRENT_PROVIDER
    CURRENT_PROVIDER = provider
    EMB_DIR = EMB_BASE_DIR / provider
    if not EMB_DIR.exists():
        print(f"  Note: {EMB_DIR} does not exist yet")
        print(f"  Run: python scripts/create_embeddings.py --provider {provider}")


def get_model() -> SentenceTransformer:
    """Lazy-load the local model."""
    global model
    if model is None:
        print(f"Loading model: {MODEL_NAME}")
        import torch
        device = "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
            print("  Using Apple Silicon GPU (MPS)")
        elif torch.cuda.is_available():
            device = "cuda"
            print("  Using NVIDIA GPU (CUDA)")
        model = SentenceTransformer(MODEL_NAME, device=device)
        print(f"  ✓ Model ready ({model.get_sentence_embedding_dimension()} dimensions)\n")
    return model


def get_openai_client():
    """Lazy-load the OpenAI client."""
    global openai_client
    if openai_client is None:
        try:
            import os

            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set. Run: export OPENAI_API_KEY='sk-...'")
            openai_client = OpenAI(api_key=api_key)
            print(f"  ✓ OpenAI client ready ({OPENAI_MODEL}, {OPENAI_DIMS} dims)\n")
        except ImportError:
            raise RuntimeError("OpenAI not installed. Run: pip install openai")
        except Exception as e:
            raise RuntimeError(str(e))
    return openai_client


def encode(texts: List[str]) -> np.ndarray:
    """Encode texts to normalized embeddings using current provider."""
    if CURRENT_PROVIDER == "openai":
        return encode_openai(texts)
    # Local provider
    m = get_model()
    return m.encode(texts, normalize_embeddings=True, convert_to_numpy=True)


def encode_openai(texts: List[str]) -> np.ndarray:
    """Encode texts using OpenAI API."""
    client = get_openai_client()
    if not client:
        raise RuntimeError("OpenAI client not available")
    
    # OpenAI expects non-empty strings
    texts = [t if t.strip() else " " for t in texts]
    
    response = client.embeddings.create(
        model=OPENAI_MODEL,
        input=texts,
        dimensions=OPENAI_DIMS
    )
    
    embeddings = np.array([e.embedding for e in response.data])
    # Normalize
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / norms
    return embeddings


def encode_to_int8(texts: List[str]) -> np.ndarray:
    """Encode texts and quantize to int8 for database queries."""
    embeddings = encode(texts)
    return np.clip(embeddings * 127, -127, 127).astype(np.int8)


def search_vectors(db_path: Path, table: str, query_int8: np.ndarray, limit: int = 10) -> list:
    """
    Search pre-computed vectors using sqlite-vec.
    Returns list of (rowid, distance, metadata...) tuples.
    """
    if not HAS_SQLITE_VEC:
        raise RuntimeError("sqlite-vec not installed")
    
    db = apsw.Connection(str(db_path))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    
    cursor = db.cursor()
    results = list(cursor.execute(f"""
        SELECT rowid, distance, *
        FROM {table}
        WHERE embedding MATCH vec_int8(?)
        ORDER BY distance
        LIMIT ?
    """, [query_int8.tobytes(), limit]))
    
    db.close()
    return results


def has_precomputed_embeddings() -> bool:
    """Check if pre-computed embedding databases exist."""
    emb_dir = get_emb_dir()
    return (
        HAS_SQLITE_VEC and 
        (emb_dir / "concept_vectors.sqlite").exists() and
        (emb_dir / "strongs_vectors.sqlite").exists()
    )


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    return float(np.dot(a, b))


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine distance (1 - similarity)."""
    return 1.0 - cosine_similarity(a, b)


# =============================================================================
# DEMO 1: TEACH - What Are Embeddings?
# =============================================================================

def demo_teach():
    """
    Teach what embeddings are with visual examples.
    """
    print("=" * 70)
    print("WHAT ARE EMBEDDINGS?")
    print("=" * 70)
    
    print("""
Embeddings convert text into NUMBERS (vectors) that capture MEANING.

Key insight: Similar meanings → Similar numbers → Close in vector space
""")
    
    # Example words - pairs of similar/opposite
    # Format: (word, similar_word, different_word)
    word_groups = [
        ("love", "affection", "hatred"),
        ("God", "Lord", "devil"),
        ("forgive", "pardon", "condemn"),
        ("praise", "worship", "curse"),
        ("joy", "happiness", "sorrow"),
    ]
    
    all_words = [w for group in word_groups for w in group]
    print(f"Encoding {len(all_words)} words: {', '.join(all_words)}\n")
    
    embeddings = encode(all_words)
    
    # Show vector snippets
    print("-" * 70)
    print("STEP 1: Each word becomes a vector of 384 numbers")
    print("-" * 70)
    for i, word in enumerate(all_words[:4]):
        vec = embeddings[i]
        snippet = ", ".join(f"{v:.3f}" for v in vec[:5])
        print(f'  "{word:12}" → [{snippet}, ... {384-5} more]')
    print()
    
    # Show similarity for each group
    print("-" * 70)
    print("STEP 2: Similar words have CLOSE vectors (low distance)")
    print("-" * 70)
    
    for group in word_groups:
        word_a, word_b, word_c = group
        idx_a = all_words.index(word_a)
        idx_b = all_words.index(word_b)
        idx_c = all_words.index(word_c)
        
        dist_ab = cosine_distance(embeddings[idx_a], embeddings[idx_b])
        dist_ac = cosine_distance(embeddings[idx_a], embeddings[idx_c])
        
        print(f"\n  {word_a} ↔ {word_b}: {dist_ab:.3f} (should be similar)")
        print(f"  {word_a} ↔ {word_c}: {dist_ac:.3f} (should be different)")
        
        if dist_ab < dist_ac:
            print(f"    \033[92m✓ Correct!\033[0m '{word_a}' is closer to '{word_b}' ({dist_ab:.3f}) than '{word_c}' ({dist_ac:.3f})")
        else:
            print(f"    \033[91m✗ Surprising!\033[0m '{word_a}' is closer to '{word_c}' ({dist_ac:.3f}) than '{word_b}' ({dist_ab:.3f})")
    
    # Full similarity matrix
    print("\n" + "-" * 70)
    print("STEP 3: Full Similarity Matrix (lower = more similar)")
    print("-" * 70)
    
    # Show just first 8 words to fit terminal
    show_n = min(8, len(all_words))
    print("\n" + " " * 12, end="")
    for word in all_words[:show_n]:
        print(f"{word[:8]:>9}", end="")
    print()
    
    for i, word_i in enumerate(all_words[:show_n]):
        print(f"{word_i:12}", end="")
        for j in range(show_n):
            dist = cosine_distance(embeddings[i], embeddings[j])
            if i == j:
                print(f"{'---':>9}", end="")
            elif dist < 0.3:
                print(f"\033[92m{dist:>9.3f}\033[0m", end="")  # Green for similar
            elif dist > 0.7:
                print(f"\033[91m{dist:>9.3f}\033[0m", end="")  # Red for different
            else:
                print(f"{dist:>9.3f}", end="")
        print()
    
    print("""
\n\033[92mGreen\033[0m = Similar meaning (distance < 0.3)
\033[91mRed\033[0m = Different meaning (distance > 0.7)
""")
    
    print("-" * 70)
    print("KEY TAKEAWAY")
    print("-" * 70)
    print("""
Embeddings let us:
  1. Compare ANY texts by meaning (not just exact words)
  2. Find similar verses, concepts, or translations
  3. Work across languages (English ↔ Greek ↔ Hebrew concepts)
""")
    
    # Interactive section
    print("=" * 70)
    print("TRY IT YOURSELF!")
    print("=" * 70)
    print("""
Enter word triplets to test: word, similar, different
Examples:
  - red, crimson, blue           (colors)
  - happy, joyful, sad           (emotions)
  - king, queen, peasant         (royalty)
  - angel, messenger, demon      (biblical)
  - λόγος, word, silence         (Greek!)

Type 'quit' to exit, 'suggest' for ideas
""")
    
    suggestions = [
        ("red", "crimson", "blue"),
        ("happy", "joyful", "sad"),
        ("king", "queen", "peasant"),
        ("angel", "messenger", "demon"),
        ("bread", "food", "stone"),
        ("light", "brightness", "darkness"),
        ("father", "parent", "stranger"),
        ("lamb", "sheep", "wolf"),
        ("temple", "sanctuary", "marketplace"),
        ("wisdom", "knowledge", "foolishness"),
    ]
    
    while True:
        try:
            user_input = input("\nEnter triplet (word, similar, different): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break
        
        if not user_input or user_input.lower() == 'quit':
            print("\nGoodbye!")
            break
        
        if user_input.lower() == 'suggest':
            print("\nSuggested triplets to try:")
            for w, s, d in suggestions:
                print(f"  {w}, {s}, {d}")
            continue
        
        # Parse input
        parts = [p.strip() for p in user_input.split(",")]
        if len(parts) != 3:
            print("  Please enter exactly 3 words separated by commas")
            continue
        
        word_a, word_b, word_c = parts
        
        # Encode and compare
        try:
            test_embeddings = encode([word_a, word_b, word_c])
            dist_ab = cosine_distance(test_embeddings[0], test_embeddings[1])
            dist_ac = cosine_distance(test_embeddings[0], test_embeddings[2])
            
            print(f"\n  {word_a} ↔ {word_b}: {dist_ab:.3f}")
            print(f"  {word_a} ↔ {word_c}: {dist_ac:.3f}")
            
            if dist_ab < dist_ac:
                print(f"  \033[92m✓ Correct!\033[0m '{word_a}' is closer to '{word_b}' than '{word_c}'")
            else:
                print(f"  \033[91m✗ Surprising!\033[0m '{word_a}' is closer to '{word_c}' than '{word_b}'")
        except Exception as e:
            print(f"  Error: {e}")


# =============================================================================
# DEMO: COMPARE MODELS - Which embedding model works best?
# =============================================================================

def demo_compare_models(quick: bool = False):
    """
    Compare different embedding models on biblical word pairs.
    """
    print("=" * 70)
    print("MODEL COMPARISON: Which embedding model works best?")
    print("=" * 70)
    
    # Models to compare
    if quick:
        models_to_test = [
            ("all-MiniLM-L6-v2", 384, "Small, fast, general"),
            ("all-mpnet-base-v2", 768, "Medium, higher quality"),
        ]
    else:
        models_to_test = [
            ("all-MiniLM-L6-v2", 384, "Small, fast, general"),
            ("all-mpnet-base-v2", 768, "Medium, higher quality"),
            ("paraphrase-multilingual-MiniLM-L12-v2", 384, "Multilingual"),
        ]
    
    # Test word pairs - biblical terms
    test_pairs = [
        ("love", "affection", "hatred"),
        ("God", "Lord", "devil"),
        ("forgive", "pardon", "condemn"),
        ("praise", "worship", "curse"),
        ("joy", "happiness", "sorrow"),
        ("faith", "belief", "doubt"),
        ("salvation", "redemption", "damnation"),
        ("prophet", "messenger", "deceiver"),
        ("holy", "sacred", "profane"),
        ("blessing", "favor", "curse"),
    ]
    
    print(f"\nTesting {len(test_pairs)} biblical word pairs across {len(models_to_test)} models\n")
    print("Word pairs: similar should be closer than opposite\n")
    
    results = {}
    
    for model_name, dims, description in models_to_test:
        print(f"\n{'='*70}")
        print(f"MODEL: {model_name}")
        print(f"  Dimensions: {dims}")
        print(f"  Description: {description}")
        print("=" * 70)
        
        try:
            import torch
            device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
            test_model = SentenceTransformer(model_name, device=device)
            
            # Get all unique words
            all_words = list(set(w for group in test_pairs for w in group))
            embeddings = test_model.encode(all_words, normalize_embeddings=True, convert_to_numpy=True)
            word_to_idx = {w: i for i, w in enumerate(all_words)}
            
            correct = 0
            total = len(test_pairs)
            
            for word_a, word_b, word_c in test_pairs:
                idx_a = word_to_idx[word_a]
                idx_b = word_to_idx[word_b]
                idx_c = word_to_idx[word_c]
                
                dist_ab = 1.0 - float(np.dot(embeddings[idx_a], embeddings[idx_b]))
                dist_ac = 1.0 - float(np.dot(embeddings[idx_a], embeddings[idx_c]))
                
                is_correct = dist_ab < dist_ac
                if is_correct:
                    correct += 1
                    mark = "\033[92m✓\033[0m"
                else:
                    mark = "\033[91m✗\033[0m"
                
                print(f"  {mark} {word_a} → {word_b} ({dist_ab:.3f}) vs {word_c} ({dist_ac:.3f})")
            
            accuracy = 100 * correct / total
            results[model_name] = {
                "accuracy": accuracy,
                "correct": correct,
                "total": total,
                "dims": dims
            }
            
            print(f"\n  Accuracy: {correct}/{total} ({accuracy:.1f}%)")
            
        except Exception as e:
            print(f"  Error loading model: {e}")
            results[model_name] = {"accuracy": 0, "error": str(e)}
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\n| Model | Dims | Accuracy |")
    print(f"|-------|------|----------|")
    for model_name, data in results.items():
        if "error" not in data:
            print(f"| {model_name[:30]:30} | {data['dims']:4} | {data['accuracy']:5.1f}%   |")
    
    # Find best
    best = max(results.items(), key=lambda x: x[1].get("accuracy", 0))
    print(f"\n\033[92mBest model: {best[0]} ({best[1]['accuracy']:.1f}% accuracy)\033[0m")
    
    print("""
\nNOTES:
  - More dimensions = more nuance but slower & larger storage
  - Multilingual models work across Greek/Hebrew/English
  - Consider testing with your actual TBTA data for best results
""")


# =============================================================================
# DEMO 2: EXPERIMENT - Does Adding Gloss Help?
# =============================================================================

def demo_experiment():
    """
    Compare embedding strategies: does adding definition improve clustering?
    """
    print("=" * 70)
    print("EXPERIMENT: Does Adding Definition Help Embeddings?")
    print("=" * 70)
    
    print("""
Question: When embedding a concept, is it better to use:
  - Just the word: "love"
  - Word + definition: "love: strong affection for someone"
  - Word + definition + Greek: "love: affection (ἀγάπη)"

Test: Do SIMILAR concepts cluster closer together?
""")
    
    # Define semantic groups - concepts that SHOULD be close
    semantic_groups = [
        {
            "name": "Love/Affection",
            "words": ["love", "affection", "care", "cherish"],
            "definitions": [
                "love: strong feeling of caring about someone",
                "affection: warm feeling of fondness",
                "care: to feel concern for someone",
                "cherish: to hold dear and protect"
            ]
        },
        {
            "name": "Anger/Wrath", 
            "words": ["anger", "wrath", "fury", "rage"],
            "definitions": [
                "anger: strong feeling of displeasure",
                "wrath: intense anger, often divine",
                "fury: wild uncontrolled anger",
                "rage: violent uncontrollable anger"
            ]
        },
        {
            "name": "Faith/Belief",
            "words": ["faith", "belief", "trust", "confidence"],
            "definitions": [
                "faith: complete trust in God",
                "belief: acceptance that something is true",
                "trust: firm reliance on someone",
                "confidence: feeling certain about something"
            ]
        },
        {
            "name": "Sin/Evil",
            "words": ["sin", "evil", "wickedness", "transgression"],
            "definitions": [
                "sin: act against God's will",
                "evil: morally wrong or bad",
                "wickedness: state of being evil",
                "transgression: violation of a law or command"
            ]
        },
        {
            "name": "Peace/Rest",
            "words": ["peace", "rest", "calm", "tranquility"],
            "definitions": [
                "peace: freedom from disturbance",
                "rest: state of relaxation",
                "calm: absence of agitation",
                "tranquility: state of peace and quiet"
            ]
        },
    ]
    
    print(f"Testing {len(semantic_groups)} semantic groups\n")
    
    def test_clustering(texts_by_group: list) -> float:
        """
        Measure how well groups cluster together.
        Returns average ratio of in-group vs out-group distance.
        Lower = better clustering.
        """
        all_texts = [t for group in texts_by_group for t in group]
        embeddings = encode(all_texts)
        
        # Calculate in-group and out-group distances
        in_group_dists = []
        out_group_dists = []
        
        idx = 0
        for g, group in enumerate(texts_by_group):
            group_size = len(group)
            group_embeddings = embeddings[idx:idx + group_size]
            
            # In-group distances
            for i in range(group_size):
                for j in range(i + 1, group_size):
                    dist = cosine_distance(group_embeddings[i], group_embeddings[j])
                    in_group_dists.append(dist)
            
            # Out-group distances (compare to other groups)
            other_idx = 0
            for og, other_group in enumerate(texts_by_group):
                if og == g:
                    other_idx += len(other_group)
                    continue
                other_embeddings = embeddings[other_idx:other_idx + len(other_group)]
                for ge in group_embeddings:
                    for oe in other_embeddings:
                        dist = cosine_distance(ge, oe)
                        out_group_dists.append(dist)
                other_idx += len(other_group)
            
            idx += group_size
        
        avg_in = np.mean(in_group_dists)
        avg_out = np.mean(out_group_dists)
        ratio = avg_in / avg_out  # Lower = better (in-group closer than out-group)
        
        return avg_in, avg_out, ratio
    
    # Strategy 1: Words only
    print("-" * 70)
    print("STRATEGY 1: Word Only")
    print("-" * 70)
    words_by_group = [g["words"] for g in semantic_groups]
    avg_in, avg_out, ratio = test_clustering(words_by_group)
    print(f"  In-group distance:  {avg_in:.3f} (similar concepts)")
    print(f"  Out-group distance: {avg_out:.3f} (different concepts)")
    print(f"  Ratio: {ratio:.3f} (lower = better clustering)")
    word_ratio = ratio
    
    # Strategy 2: Word + Definition
    print("\n" + "-" * 70)
    print("STRATEGY 2: Word + Definition")
    print("-" * 70)
    defs_by_group = [g["definitions"] for g in semantic_groups]
    avg_in, avg_out, ratio = test_clustering(defs_by_group)
    print(f"  In-group distance:  {avg_in:.3f} (similar concepts)")
    print(f"  Out-group distance: {avg_out:.3f} (different concepts)")
    print(f"  Ratio: {ratio:.3f} (lower = better clustering)")
    def_ratio = ratio
    
    # Strategy 3: Word + Definition + Greek/Hebrew
    print("\n" + "-" * 70)
    print("STRATEGY 3: Word + Definition + Greek")
    print("-" * 70)
    greek_groups = [
        ["love: affection (ἀγάπη)", "affection: fondness (φιλία)", "care: concern (μέριμνα)", "cherish: protect (θάλπω)"],
        ["anger: displeasure (ὀργή)", "wrath: divine anger (θυμός)", "fury: wild anger (ὀργή)", "rage: violent anger (θυμός)"],
        ["faith: trust (πίστις)", "belief: acceptance (πίστις)", "trust: reliance (πεποίθησις)", "confidence: certainty (παρρησία)"],
        ["sin: transgression (ἁμαρτία)", "evil: bad (πονηρός)", "wickedness: evil (κακία)", "transgression: violation (παράβασις)"],
        ["peace: calm (εἰρήνη)", "rest: relaxation (ἀνάπαυσις)", "calm: quiet (γαλήνη)", "tranquility: peace (ἡσυχία)"],
    ]
    avg_in, avg_out, ratio = test_clustering(greek_groups)
    print(f"  In-group distance:  {avg_in:.3f} (similar concepts)")
    print(f"  Out-group distance: {avg_out:.3f} (different concepts)")
    print(f"  Ratio: {ratio:.3f} (lower = better clustering)")
    greek_ratio = ratio
    
    # Summary
    print("\n" + "=" * 70)
    print("RESULTS: Which strategy clusters concepts best?")
    print("=" * 70)
    
    results = [
        ("Word only", word_ratio),
        ("Word + Definition", def_ratio),
        ("Word + Def + Greek", greek_ratio),
    ]
    
    # Sort by ratio (lower is better)
    results.sort(key=lambda x: x[1])
    
    print(f"\n| Strategy            | Cluster Ratio | Rank |")
    print(f"|---------------------|---------------|------|")
    for rank, (name, ratio) in enumerate(results, 1):
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉"
        print(f"| {name:19} | {ratio:13.3f} | {medal}    |")
    
    best = results[0]
    print(f"\n\033[92mBest strategy: {best[0]} (ratio={best[1]:.3f})\033[0m")
    
    print("""
\nInterpretation:
  - Lower ratio = similar concepts are closer, different concepts are farther
  - Adding definitions helps disambiguate (e.g., "love" alone is vague)
  - Greek adds cross-lingual signal for biblical terms
""")


# =============================================================================
# DEMO 3: MATCH - Concept to Strong's Suggestions
# =============================================================================

def demo_match():
    """
    Find Strong's suggestions for concepts without mappings.
    Uses pre-computed Strong's embeddings from sqlite-vec if available.
    """
    print("=" * 70)
    print("CONCEPT → STRONG'S MATCHING")
    print("=" * 70)
    
    concepts_db = DB_DIR / "concepts.sqlite"
    strongs_db = DB_DIR / "strongs.sqlite"
    strongs_vec_db = get_emb_dir() / "strongs_vectors.sqlite"
    
    if not concepts_db.exists() or not strongs_db.exists():
        print(f"Error: Need {concepts_db} and {strongs_db}")
        return
    
    use_precomputed = HAS_SQLITE_VEC and strongs_vec_db.exists()
    
    if use_precomputed:
        print("\n✓ Using pre-computed Strong's embeddings (fast!)\n")
    else:
        print("\n⚠ No pre-computed embeddings. Run: python scripts/create_embeddings.py\n")
    
    # Load concepts WITHOUT Strong's mappings
    conn = sqlite3.connect(concepts_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, stem, sense, gloss, brief_gloss 
        FROM concepts 
        WHERE (strongs_mappings IS NULL OR strongs_mappings = '[]')
          AND gloss IS NOT NULL
          AND gloss != ''
          AND stem NOT GLOB '[0-9]*'
          AND stem NOT GLOB '.[0-9]*'
          AND LENGTH(stem) > 2
        ORDER BY RANDOM()
        LIMIT 50
    """)
    unmapped = cursor.fetchall()
    conn.close()
    
    # Load Strong's metadata
    conn = sqlite3.connect(strongs_db)
    cursor = conn.cursor()
    cursor.execute("SELECT strongs_number, language, lemma, definition FROM strongs")
    strongs_lookup = {}
    for sid, lang, lemma, defn in cursor.fetchall():
        strongs_lookup[sid] = {"lang": lang, "lemma": lemma, "definition": defn}
    conn.close()
    
    print(f"Found {len(unmapped)} concepts without Strong's mappings")
    print(f"Matching against {len(strongs_lookup)} Strong's entries\n")
    
    print("-" * 70)
    print("SUGGESTED MAPPINGS (Top 3 per concept)")
    print("-" * 70)
    
    results = []
    
    if use_precomputed:
        # Use pre-computed embeddings
        db = apsw.Connection(str(strongs_vec_db))
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        
        for cid, stem, sense, gloss, brief in unmapped[:20]:
            # Encode just this concept
            concept_text = f"{stem}: {gloss}"
            concept_int8 = encode_to_int8([concept_text])[0]
            
            # Search Strong's vectors
            matches = list(db.cursor().execute("""
                SELECT strongs_number, distance
                FROM strongs_vectors
                WHERE embedding MATCH vec_int8(?)
                ORDER BY distance
                LIMIT 3
            """, [concept_int8.tobytes()]))
            
            print(f"\n{stem} ({sense}): {(gloss or '')[:50]}...")
            for sid, dist in matches:
                s = strongs_lookup.get(sid, {"lang": "?", "lemma": "?", "definition": ""})
                lang_emoji = "🇮🇱" if s["lang"] == "hebrew" else "🇬🇷"
                print(f"  {lang_emoji} {sid}: {s['lemma']} - {(s['definition'] or '')[:35]}... ({dist:.1f})")
            
            results.append({
                "concept_id": cid,
                "stem": stem,
                "sense": sense,
                "suggestions": [{"strongs": sid, "distance": dist} for sid, dist in matches]
            })
        
        db.close()
    else:
        # Fall back to on-the-fly encoding
        strongs_data = []
        strongs_texts = []
        for sid, data in strongs_lookup.items():
            text = f"{data['lemma'] or ''} {data['definition'] or ''}"
            if text.strip():
                strongs_data.append({"id": sid, **data})
                strongs_texts.append(text)
        
        print("Encoding Strong's entries (slow)...")
        strongs_embeddings = encode(strongs_texts)
        
        concept_texts = [f"{row[1]}: {row[3]}" for row in unmapped]
        print("Encoding unmapped concepts...")
        concept_embeddings = encode(concept_texts)
        
        for i, (cid, stem, sense, gloss, brief) in enumerate(unmapped[:20]):
            distances = [cosine_distance(concept_embeddings[i], se) for se in strongs_embeddings]
            sorted_idx = np.argsort(distances)
            top3 = [(strongs_data[j], distances[j]) for j in sorted_idx[:3]]
            
            print(f"\n{stem} ({sense}): {(gloss or '')[:50]}...")
            for data, dist in top3:
                lang_emoji = "🇮🇱" if data["lang"] == "hebrew" else "🇬🇷"
                print(f"  {lang_emoji} {data['id']}: {data['lemma']} - {(data['definition'] or '')[:35]}... ({dist:.3f})")
            
            results.append({
                "concept_id": cid,
                "stem": stem,
                "sense": sense,
                "suggestions": [{"strongs": d["id"], "distance": dist} for d, dist in top3]
            })
    
    print("\n" + "-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"\n✓ Found suggestions for {len(results)} unmapped concepts")


# =============================================================================
# DEMO 4: SEARCH - User Text to Concepts
# =============================================================================

def demo_search(query: str):
    """
    Search for concepts matching user text.
    Uses pre-computed embeddings from sqlite-vec if available.
    """
    print("=" * 70)
    print(f"SEARCHING: \"{query}\"")
    print("=" * 70)
    
    use_precomputed = has_precomputed_embeddings()
    
    if use_precomputed:
        print("\n✓ Using pre-computed embeddings (fast!)\n")
        _search_with_precomputed(query)
    else:
        print("\n⚠ No pre-computed embeddings found.")
        print("  Run: python scripts/create_embeddings.py")
        print("  Falling back to on-the-fly encoding (slow)...\n")
        _search_on_the_fly(query)


def _search_with_precomputed(query: str):
    """Search using pre-computed sqlite-vec embeddings."""
    concepts_db = DB_DIR / "concepts.sqlite"
    strongs_db = DB_DIR / "strongs.sqlite"
    concept_vec_db = get_emb_dir() / "concept_vectors.sqlite"
    strongs_vec_db = get_emb_dir() / "strongs_vectors.sqlite"
    
    # Load concept metadata for display
    conn = sqlite3.connect(concepts_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, stem, sense, gloss, strongs_mappings FROM concepts")
    concept_lookup = {}
    for cid, stem, sense, gloss, strongs in cursor.fetchall():
        concept_lookup[cid] = {
            "stem": stem, "sense": sense, "gloss": gloss,
            "strongs": json.loads(strongs) if strongs else []
        }
    conn.close()
    
    # Load Strong's metadata
    strongs_lookup = {}
    if strongs_db.exists():
        conn = sqlite3.connect(strongs_db)
        cursor = conn.cursor()
        cursor.execute("SELECT strongs_number, language, lemma, definition FROM strongs")
        for sid, lang, lemma, defn in cursor.fetchall():
            strongs_lookup[sid] = {"lang": lang, "lemma": lemma, "definition": defn}
        conn.close()
    
    # Encode query to int8
    print("Encoding query...")
    query_int8 = encode_to_int8([query])[0]
    
    # Search concepts
    print("\n" + "-" * 70)
    print("CONCEPT MATCHES (from pre-computed embeddings)")
    print("-" * 70)
    
    db = apsw.Connection(str(concept_vec_db))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    
    results = list(db.cursor().execute("""
        SELECT concept_id, stem, distance
        FROM concept_vectors
        WHERE embedding MATCH vec_int8(?)
        ORDER BY distance
        LIMIT 10
    """, [query_int8.tobytes()]))
    db.close()
    
    print(f"\nTop 10 concepts matching \"{query}\":\n")
    for rank, (cid, stem, dist) in enumerate(results, 1):
        c = concept_lookup.get(cid, {"sense": "?", "gloss": "", "strongs": []})
        strongs_str = ", ".join(c["strongs"][:3]) if c["strongs"] else "none"
        print(f"  {rank:2}. {stem} ({c['sense']})")
        print(f"      Gloss: {(c['gloss'] or '')[:50]}...")
        print(f"      Strong's: {strongs_str}")
        print(f"      Distance: {dist:.3f}")
        print()
    
    # Search Strong's
    if strongs_vec_db.exists() and strongs_lookup:
        print("-" * 70)
        print("STRONG'S MATCHES (from pre-computed embeddings)")
        print("-" * 70)
        
        db = apsw.Connection(str(strongs_vec_db))
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        
        results = list(db.cursor().execute("""
            SELECT strongs_number, distance
            FROM strongs_vectors
            WHERE embedding MATCH vec_int8(?)
            ORDER BY distance
            LIMIT 5
        """, [query_int8.tobytes()]))
        db.close()
        
        print(f"\nTop 5 Strong's entries matching \"{query}\":\n")
        for sid, dist in results:
            s = strongs_lookup.get(sid, {"lang": "?", "lemma": "?", "definition": ""})
            lang_emoji = "🇮🇱" if s["lang"] == "hebrew" else "🇬🇷"
            print(f"  {lang_emoji} {sid}: {s['lemma']}")
            print(f"     {(s['definition'] or '')[:60]}...")
            print(f"     Distance: {dist:.3f}")
            print()


def _search_on_the_fly(query: str):
    """Fallback: encode concepts on the fly (slow)."""
    concepts_db = DB_DIR / "concepts.sqlite"
    
    if not concepts_db.exists():
        print(f"Error: Need {concepts_db}")
        return
    
    # Load all concepts
    conn = sqlite3.connect(concepts_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, stem, sense, gloss, brief_gloss, strongs_mappings
        FROM concepts 
        WHERE gloss IS NOT NULL AND gloss != ''
    """)
    concepts = cursor.fetchall()
    conn.close()
    
    print(f"Searching {len(concepts)} concepts...\n")
    
    # Prepare concept embeddings
    concept_data = []
    concept_texts = []
    for cid, stem, sense, gloss, brief, strongs in concepts:
        concept_data.append({
            "id": cid, "stem": stem, "sense": sense, 
            "gloss": gloss, "brief": brief,
            "strongs": json.loads(strongs) if strongs else []
        })
        concept_texts.append(f"{stem}: {gloss}")
    
    print("Encoding concepts (this takes a while)...")
    concept_embeddings = encode(concept_texts)
    
    print("\n" + "-" * 70)
    print("CONCEPT MATCHES")
    print("-" * 70)
    
    query_embedding = encode([query])[0]
    distances = [cosine_distance(query_embedding, ce) for ce in concept_embeddings]
    sorted_idx = np.argsort(distances)
    
    print(f"\nTop 10 concepts matching \"{query}\":\n")
    for rank, i in enumerate(sorted_idx[:10], 1):
        c = concept_data[i]
        dist = distances[i]
        strongs_str = ", ".join(c["strongs"][:3]) if c["strongs"] else "none"
        print(f"  {rank:2}. {c['stem']} ({c['sense']})")
        print(f"      Gloss: {(c['gloss'] or '')[:50]}...")
        print(f"      Strong's: {strongs_str}")
        print(f"      Distance: {dist:.3f}")
        print()


# =============================================================================
# DEMO 6: ANALYZE - Word-by-word verse analysis
# =============================================================================

def demo_analyze(verse: str, top_n: int = 3):
    """
    Analyze a verse word-by-word, matching each to concepts.
    """
    print("=" * 70)
    print("VERSE ANALYSIS: Word-by-Word Concept Matching")
    print("=" * 70)
    print(f"\nVerse: \"{verse}\"\n")
    
    concepts_db = DB_DIR / "concepts.sqlite"
    concept_vec_db = get_emb_dir() / "concept_vectors.sqlite"
    
    use_precomputed = HAS_SQLITE_VEC and concept_vec_db.exists()
    
    if use_precomputed:
        print("✓ Using pre-computed concept embeddings\n")
    else:
        print("⚠ No pre-computed embeddings. Run: python scripts/create_embeddings.py\n")
    
    # Load concept metadata - EXCLUDE concepts marked DELETE
    conn = sqlite3.connect(concepts_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, stem, sense, gloss, strongs_mappings 
        FROM concepts 
        WHERE gloss NOT LIKE '%DELETE%' 
          AND gloss NOT LIKE '%delete%'
          AND gloss IS NOT NULL
    """)
    concept_lookup = {}
    valid_concept_ids = set()
    for cid, stem, sense, gloss, strongs in cursor.fetchall():
        concept_lookup[cid] = {
            "stem": stem, "sense": sense, "gloss": gloss,
            "strongs": json.loads(strongs) if strongs else []
        }
        valid_concept_ids.add(cid)
    conn.close()
    
    # Stopwords - function words that don't have semantic meaning
    STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
        "into", "through", "during", "before", "after", "above", "below",
        "between", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "each", "every",
        "both", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "but", "and", "or", "if", "because", "until", "while", "that",
        "which", "who", "whom", "this", "these", "those", "am", "it", "its",
        "us", "we", "our", "you", "your", "he", "him", "his", "she", "her",
        "they", "them", "their", "what", "any", "also"
    }
    
    # Tokenize verse
    import re
    words = re.findall(r"[A-Za-z]+(?:'[a-z]+)?", verse)
    
    print("-" * 70)
    print(f"Analyzing {len(words)} words...")
    print("-" * 70)
    
    # Distance threshold - above this, match is unreliable
    GOOD_MATCH_THRESHOLD = 105
    WEAK_MATCH_THRESHOLD = 115
    
    if use_precomputed:
        db = apsw.Connection(str(concept_vec_db))
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        
        for word in words:
            word_lower = word.lower()
            
            # Skip very short words
            if len(word) <= 2:
                print(f"\n\033[90m{word}\033[0m")
                print("  \033[90m(skipped - too short)\033[0m")
                continue
            
            # Skip stopwords/function words
            if word_lower in STOPWORDS:
                print(f"\n\033[90m{word}\033[0m")
                print("  \033[90m(skipped - function word)\033[0m")
                continue
            
            # Encode this word
            word_int8 = encode_to_int8([word_lower])[0]
            
            # Search concepts - get more than needed to filter DELETE
            results = list(db.cursor().execute("""
                SELECT concept_id, stem, distance
                FROM concept_vectors
                WHERE embedding MATCH vec_int8(?)
                ORDER BY distance
                LIMIT ?
            """, [word_int8.tobytes(), top_n * 3]))
            
            # Filter to valid concepts only
            filtered = [(cid, stem, dist) for cid, stem, dist in results if cid in valid_concept_ids][:top_n]
            
            print(f"\n\033[1m{word}\033[0m")
            
            if not filtered:
                print("  \033[91m(no matches found)\033[0m")
                continue
            
            for rank, (cid, stem, dist) in enumerate(filtered, 1):
                c = concept_lookup.get(cid, {"sense": "?", "gloss": "", "strongs": []})
                strongs_str = ", ".join(c["strongs"][:2]) if c["strongs"] else ""
                gloss_short = (c["gloss"] or "")[:45]
                
                # Highlight if stem matches word
                match_marker = "→" if stem.lower() == word_lower else " "
                
                # Color code by distance
                if dist < GOOD_MATCH_THRESHOLD:
                    color = "\033[92m"  # Green - good match
                elif dist < WEAK_MATCH_THRESHOLD:
                    color = "\033[93m"  # Yellow - okay match
                else:
                    color = "\033[91m"  # Red - weak match
                
                print(f"  {match_marker} {color}{stem}_{c['sense']}\033[0m: {gloss_short}...")
                if strongs_str:
                    print(f"      Strong's: {strongs_str}")
                print(f"      Distance: {dist:.1f}")
        
        db.close()
    else:
        # Fallback: load all concepts and encode on the fly
        conn = sqlite3.connect(concepts_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, stem, sense, gloss FROM concepts 
            WHERE gloss IS NOT NULL 
              AND gloss NOT LIKE '%DELETE%'
        """)
        concepts = cursor.fetchall()
        conn.close()
        
        concept_texts = [f"{row[1]}: {row[3]}" for row in concepts]
        print(f"Encoding {len(concepts)} concepts (slow)...")
        concept_embeddings = encode(concept_texts)
        
        for word in words:
            word_lower = word.lower()
            
            if len(word) <= 2:
                print(f"\n\033[90m{word}\033[0m")
                print("  \033[90m(skipped - too short)\033[0m")
                continue
            
            if word_lower in STOPWORDS:
                print(f"\n\033[90m{word}\033[0m")
                print("  \033[90m(skipped - function word)\033[0m")
                continue
            
            word_embedding = encode([word_lower])[0]
            distances = [cosine_distance(word_embedding, ce) for ce in concept_embeddings]
            sorted_idx = np.argsort(distances)
            
            print(f"\n\033[1m{word}\033[0m")
            for rank, i in enumerate(sorted_idx[:top_n], 1):
                cid, stem, sense, gloss = concepts[i]
                c = concept_lookup.get(cid, {"strongs": []})
                strongs_str = ", ".join(c["strongs"][:2]) if c.get("strongs") else ""
                gloss_short = (gloss or "")[:45]
                match_marker = "→" if stem.lower() == word_lower else " "
                
                dist = distances[i]
                if dist < 0.4:
                    color = "\033[92m"  # Green
                elif dist < 0.6:
                    color = "\033[93m"  # Yellow
                else:
                    color = "\033[91m"  # Red
                
                print(f"  {match_marker} {color}{stem}_{sense}\033[0m: {gloss_short}...")
                if strongs_str:
                    print(f"      Strong's: {strongs_str}")
                print(f"      Distance: {dist:.3f}")
    
    print("\n" + "-" * 70)
    print("LEGEND")
    print("-" * 70)
    print("  → = exact stem match")
    print("  \033[92mGreen\033[0m = good match (distance < 105)")
    print("  \033[93mYellow\033[0m = okay match (105-115)")
    print("  \033[91mRed\033[0m = weak match (> 115)")
    print("  \033[90mGray\033[0m = skipped (function word or too short)")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="TBTA Embedding Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Default (local embeddings)
    python scripts/demo_embeddings.py teach
    python scripts/demo_embeddings.py search "God loved the world"
    
    # Use OpenAI embeddings
    python scripts/demo_embeddings.py --provider openai search "God loved"
    python scripts/demo_embeddings.py --provider openai analyze "The Lord is my shepherd"
        """
    )
    
    # Global provider argument
    parser.add_argument("--provider", choices=["local", "openai"], default="openai",
                        help="Which embeddings to use (default: openai)")
    
    subparsers = parser.add_subparsers(dest="command", help="Demo mode")
    
    # Teach
    teach_parser = subparsers.add_parser("teach", help="What are embeddings?")
    
    # Compare models
    compare_parser = subparsers.add_parser("compare", help="Compare different embedding models")
    compare_parser.add_argument("--quick", action="store_true", help="Quick comparison (fewer models)")
    
    # Experiment
    exp_parser = subparsers.add_parser("experiment", help="Compare stem vs stem+gloss")
    
    # Match
    match_parser = subparsers.add_parser("match", help="Concept-to-Strong's matching")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search concepts by text")
    search_parser.add_argument("query", help="Text to search for")
    
    # Analyze verse word-by-word
    analyze_parser = subparsers.add_parser("analyze", help="Analyze verse word-by-word")
    analyze_parser.add_argument("verse", help="Verse text to analyze")
    analyze_parser.add_argument("--top", type=int, default=3, help="Top N matches per word")
    
    args = parser.parse_args()
    
    # Set embedding provider
    set_provider(args.provider)
    
    if args.command == "teach":
        demo_teach()
    elif args.command == "compare":
        demo_compare_models(quick=args.quick)
    elif args.command == "experiment":
        demo_experiment()
    elif args.command == "match":
        demo_match()
    elif args.command == "search":
        demo_search(args.query)
    elif args.command == "analyze":
        demo_analyze(args.verse, top_n=args.top)
    else:
        parser.print_help()
        print("\n\nQuick start: python scripts/demo_embeddings.py teach")


if __name__ == "__main__":
    main()

