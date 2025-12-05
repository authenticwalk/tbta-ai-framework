#!/usr/bin/env python3
"""
TBTA Embedding Generator

Creates vector embeddings for verses, concepts, and Strong's entries
using sentence-transformers or OpenAI and sqlite-vec.

Input:
  - databases/verses.sqlite
  - databases/nodes.sqlite
  - databases/concepts.sqlite
  - databases/strongs.sqlite (optional)
  - .data/strongs/ YAML files (for Strong's data)

Output:
  - databases/embeddings/local/   (sentence-transformers)
  - databases/embeddings/openai/  (OpenAI API)

Requirements:
  pip install sentence-transformers sqlite-vec apsw numpy pyyaml tqdm
  pip install openai  # for OpenAI embeddings

Usage:
    # Local model (default)
    python scripts/create_embeddings.py
    python scripts/create_embeddings.py --provider local --model paraphrase-multilingual-MiniLM-L12-v2
    
    # OpenAI (requires OPENAI_API_KEY env var)
    python scripts/create_embeddings.py --provider openai
    python scripts/create_embeddings.py --provider openai --model text-embedding-3-small --dims 384
"""

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

try:
    import apsw
    import sqlite_vec
    from tqdm import tqdm
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install sqlite-vec apsw numpy pyyaml tqdm")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent.parent  # scripts/embeddings -> scripts -> tbta-ai-framework
DB_DIR = PROJECT_DIR / "databases"
EMB_BASE_DIR = PROJECT_DIR / "databases" / "embeddings"

# Model configs
PROVIDERS = {
    "local": {
        "default_model": "paraphrase-multilingual-MiniLM-L12-v2",
        "default_dims": 384,
    },
    "openai": {
        "default_model": "text-embedding-3-small",
        "default_dims": 512,  # Can reduce from 1536 for cost/speed
    }
}

BATCH_SIZE = 128
MAX_CHARS = 1000


def float32_to_int8(embeddings: np.ndarray) -> np.ndarray:
    """Quantize float32 embeddings to int8 for 4x storage reduction."""
    clipped = np.clip(embeddings, -1.0, 1.0)
    return (clipped * 127).astype(np.int8)


class LocalEncoder:
    """Sentence-transformers encoder."""
    
    def __init__(self, model_name: str, dims: int):
        import torch
        from sentence_transformers import SentenceTransformer
        
        device = "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
            print("  Using Apple Silicon GPU (MPS)")
        elif torch.cuda.is_available():
            device = "cuda"
            print("  Using NVIDIA GPU (CUDA)")
        
        self.model = SentenceTransformer(model_name, device=device)
        self.dims = self.model.get_sentence_embedding_dimension()
        print(f"  Model dimensions: {self.dims}")
    
    def encode(self, texts: List[str], batch_size: int = BATCH_SIZE) -> np.ndarray:
        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = self.model.encode(
                batch,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            all_embeddings.append(embeddings)
        return np.vstack(all_embeddings) if all_embeddings else np.array([])


class OpenAIEncoder:
    """OpenAI API encoder."""
    
    def __init__(self, model_name: str, dims: int):
        try:
            from openai import OpenAI
        except ImportError:
            print("Error: pip install openai")
            sys.exit(1)
        
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("Error: Set OPENAI_API_KEY environment variable")
            sys.exit(1)
        
        self.client = OpenAI(api_key=api_key)
        self.model = model_name
        self.dims = dims
        print(f"  OpenAI model: {model_name}")
        print(f"  Dimensions: {dims}")
    
    def encode(self, texts: List[str], batch_size: int = 100) -> np.ndarray:
        """Encode texts using OpenAI API. Batch size limited to avoid rate limits."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            # OpenAI expects non-empty strings
            batch = [t if t.strip() else " " for t in batch]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
                dimensions=self.dims  # text-embedding-3 models support dimension reduction
            )
            
            embeddings = np.array([e.embedding for e in response.data])
            # Normalize (OpenAI embeddings may not be normalized)
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            embeddings = embeddings / norms
            all_embeddings.append(embeddings)
        
        return np.vstack(all_embeddings) if all_embeddings else np.array([])


def get_encoder(provider: str, model_name: str, dims: int):
    """Factory function to get the appropriate encoder."""
    if provider == "openai":
        return OpenAIEncoder(model_name, dims)
    else:
        return LocalEncoder(model_name, dims)


def concat_fields(*fields, max_length: int = MAX_CHARS) -> str:
    """Concatenate non-empty fields with space separator, truncate to max."""
    text = " ".join(str(f).strip() for f in fields if f and str(f).strip())
    return text[:max_length] if max_length and len(text) > max_length else text


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text) if text else ""


def create_verse_embeddings(encoder, dims: int, emb_dir: Path):
    """Create verse embeddings from verses.sqlite."""
    print("\n[1/3] Creating verse embeddings...")
    
    verses_db = DB_DIR / "verses.sqlite"
    nodes_db = DB_DIR / "nodes.sqlite"
    niv_db = DB_DIR / "niv.sqlite"
    output_db = emb_dir / "verse_vectors.sqlite"
    
    if not verses_db.exists():
        print(f"  ✗ verses.sqlite not found")
        return False
    
    if output_db.exists():
        output_db.unlink()
    
    # Connect to source databases
    verses_conn = sqlite3.connect(verses_db)
    verses_cur = verses_conn.cursor()
    
    nodes_conn = None
    niv_conn = None
    
    if nodes_db.exists():
        nodes_conn = sqlite3.connect(nodes_db)
    if niv_db.exists():
        niv_conn = sqlite3.connect(niv_db)
    
    # Get verses
    verses_cur.execute("SELECT book, chapter, verse, verse_text, node_ids FROM verses")
    verses = verses_cur.fetchall()
    
    print(f"  Found {len(verses):,} verses")
    
    # Build text for each verse
    texts = []
    metadata = []
    
    for book, chapter, verse_num, verse_text, node_ids_json in verses:
        # Start with verse text
        parts = [verse_text or ""]
        
        # Add NIV text if available
        if niv_conn:
            niv_cur = niv_conn.cursor()
            niv_cur.execute(
                "SELECT text FROM niv WHERE book=? AND chapter=? AND verse=?",
                (book, chapter, verse_num)
            )
            row = niv_cur.fetchone()
            if row and row[0]:
                parts.append(row[0])
        
        # Add node content if available
        if nodes_conn and node_ids_json:
            node_ids = json.loads(node_ids_json)
            if node_ids:
                nodes_cur = nodes_conn.cursor()
                placeholders = ",".join("?" * len(node_ids))
                nodes_cur.execute(
                    f"SELECT content FROM nodes WHERE node_id IN ({placeholders})",
                    node_ids
                )
                words = [row[0] for row in nodes_cur.fetchall() if row[0]]
                parts.append(" ".join(words))
        
        text = concat_fields(*parts)
        if text:
            texts.append(text)
            metadata.append((book, chapter, verse_num))
    
    print(f"  Encoding {len(texts):,} verses...")
    embeddings = encoder.encode(texts)
    embeddings_int8 = float32_to_int8(embeddings)
    
    # Create output database with vec0
    print("  Creating vector database...")
    db = apsw.Connection(str(output_db))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    
    cursor = db.cursor()
    cursor.execute(f'''
        CREATE VIRTUAL TABLE verse_vectors USING vec0(
            embedding int8[{dims}],
            +book TEXT,
            +chapter INTEGER,
            +verse INTEGER
        )
    ''')
    
    print("  Inserting embeddings...")
    for emb, (book, chapter, verse_num) in tqdm(zip(embeddings_int8, metadata), total=len(metadata), desc="  "):
        cursor.execute(
            "INSERT INTO verse_vectors(embedding, book, chapter, verse) VALUES (vec_int8(?), ?, ?, ?)",
            [emb.tobytes(), book, chapter, verse_num]
        )
    
    db.close()
    verses_conn.close()
    if nodes_conn:
        nodes_conn.close()
    if niv_conn:
        niv_conn.close()
    
    print(f"  ✓ Created {len(texts):,} verse embeddings")
    return True


def create_concept_embeddings(encoder, dims: int, emb_dir: Path):
    """Create concept embeddings from concepts.sqlite."""
    print("\n[2/3] Creating concept embeddings...")
    
    concepts_db = DB_DIR / "concepts.sqlite"
    output_db = emb_dir / "concept_vectors.sqlite"
    
    if not concepts_db.exists():
        print(f"  ✗ concepts.sqlite not found")
        return False
    
    if output_db.exists():
        output_db.unlink()
    
    # Get concepts
    conn = sqlite3.connect(concepts_db)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, stem, gloss, categorization, curated_examples 
        FROM concepts
    """)
    concepts = cursor.fetchall()
    conn.close()
    
    print(f"  Found {len(concepts):,} concepts")
    
    # Build text for each concept
    texts = []
    metadata = []
    
    for cid, stem, gloss, cat, examples in concepts:
        text = concat_fields(stem, gloss, cat, examples)
        if text:
            texts.append(text)
            metadata.append((cid, stem))
    
    print(f"  Encoding {len(texts):,} concepts...")
    embeddings = encoder.encode(texts)
    embeddings_int8 = float32_to_int8(embeddings)
    
    # Create output database
    print("  Creating vector database...")
    db = apsw.Connection(str(output_db))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    
    cursor = db.cursor()
    cursor.execute(f'''
        CREATE VIRTUAL TABLE concept_vectors USING vec0(
            embedding int8[{dims}],
            +concept_id INTEGER,
            +stem TEXT
        )
    ''')
    
    for emb, (cid, stem) in zip(embeddings_int8, metadata):
        cursor.execute(
            "INSERT INTO concept_vectors(embedding, concept_id, stem) VALUES (vec_int8(?), ?, ?)",
            [emb.tobytes(), cid, stem]
        )
    
    db.close()
    print(f"  ✓ Created {len(texts):,} concept embeddings")
    return True


def create_strongs_embeddings(encoder, dims: int, emb_dir: Path, strongs_dir: Optional[Path] = None):
    """Create Strong's embeddings from YAML files."""
    print("\n[3/3] Creating Strong's embeddings...")
    
    strongs_db = DB_DIR / "strongs.sqlite"
    output_db = emb_dir / "strongs_vectors.sqlite"
    
    if output_db.exists():
        output_db.unlink()
    
    # Try to find Strong's YAML files
    if strongs_dir is None:
        # Look in common locations
        possible_dirs = [
            PROJECT_DIR.parent / "mybibletoolbox-code" / ".data" / "strongs",
            Path.home() / "projects" / "mybibletoolbox" / "mybibletoolbox-code" / ".data" / "strongs",
        ]
        for d in possible_dirs:
            if d.exists():
                strongs_dir = d
                break
    
    if strongs_dir is None or not strongs_dir.exists():
        print("  ⚠ Strong's YAML directory not found")
        print("    Creating empty strongs_vectors.sqlite")
        
        db = apsw.Connection(str(output_db))
        db.enable_load_extension(True)
        sqlite_vec.load(db)
        db.enable_load_extension(False)
        
        cursor = db.cursor()
        cursor.execute(f'''
            CREATE VIRTUAL TABLE strongs_vectors USING vec0(
                embedding int8[{dims}],
                +strongs_number TEXT
            )
        ''')
        db.close()
        return True
    
    if yaml is None:
        print("  ⚠ PyYAML not installed, skipping Strong's")
        return False
    
    # Find YAML files
    yaml_files = list(strongs_dir.glob("*/[GH]*-strongs.strongs.yaml"))
    print(f"  Found {len(yaml_files):,} Strong's YAML files")
    
    # Load and process
    texts = []
    metadata = []
    strongs_data = []
    
    for filepath in yaml_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Build text
            parts = [
                data.get('strongs_number', ''),
                data.get('lemma', ''),
                data.get('transliteration', ''),
                data.get('definition', ''),
                data.get('derivation', ''),
                data.get('kjv_usage', ''),
            ]
            
            ext = data.get('extended_definition', {})
            if ext:
                parts.extend([
                    ext.get('gloss', ''),
                    strip_html(ext.get('definition', '')),
                ])
            
            etym = data.get('etymology', {})
            if etym:
                parts.append(strip_html(etym.get('lsj_definition', '')))
            
            text = concat_fields(*parts)
            if text:
                texts.append(text)
                metadata.append(data.get('strongs_number', ''))
                strongs_data.append({
                    'strongs_number': data.get('strongs_number', ''),
                    'language': data.get('language', ''),
                    'lemma': data.get('lemma', ''),
                    'definition': data.get('definition', ''),
                    'derivation': data.get('derivation', '')
                })
        except Exception:
            continue
    
    print(f"  Encoding {len(texts):,} Strong's entries...")
    embeddings = encoder.encode(texts)
    embeddings_int8 = float32_to_int8(embeddings)
    
    # Update strongs.sqlite with data
    if strongs_db.exists():
        strongs_conn = sqlite3.connect(strongs_db)
        strongs_cur = strongs_conn.cursor()
        for data in strongs_data:
            strongs_cur.execute('''
                INSERT OR REPLACE INTO strongs (strongs_number, language, lemma, definition, derivation)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['strongs_number'], data['language'], data['lemma'], 
                  data['definition'], data['derivation']))
        strongs_conn.commit()
        strongs_conn.close()
        print(f"  ✓ Updated strongs.sqlite with {len(strongs_data):,} entries")
    
    # Create vector database
    print("  Creating vector database...")
    db = apsw.Connection(str(output_db))
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    
    cursor = db.cursor()
    cursor.execute(f'''
        CREATE VIRTUAL TABLE strongs_vectors USING vec0(
            embedding int8[{dims}],
            +strongs_number TEXT
        )
    ''')
    
    for emb, strongs_num in zip(embeddings_int8, metadata):
        cursor.execute(
            "INSERT INTO strongs_vectors(embedding, strongs_number) VALUES (vec_int8(?), ?)",
            [emb.tobytes(), strongs_num]
        )
    
    db.close()
    print(f"  ✓ Created {len(texts):,} Strong's embeddings")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Generate TBTA embeddings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Local model (default)
    python scripts/create_embeddings.py
    python scripts/create_embeddings.py --provider local
    
    # OpenAI (requires OPENAI_API_KEY)
    python scripts/create_embeddings.py --provider openai
    python scripts/create_embeddings.py --provider openai --dims 384
        """
    )
    parser.add_argument("--provider", choices=["local", "openai"], default="local",
                        help="Embedding provider (default: local)")
    parser.add_argument("--model", help="Model name (default depends on provider)")
    parser.add_argument("--dims", type=int, help="Embedding dimensions (for OpenAI, can reduce)")
    parser.add_argument("--skip-strongs", action="store_true", help="Skip Strong's embeddings")
    parser.add_argument("--strongs-dir", type=Path, help="Path to Strong's YAML directory")
    args = parser.parse_args()
    
    # Get provider config
    provider_config = PROVIDERS[args.provider]
    model_name = args.model or provider_config["default_model"]
    dims = args.dims or provider_config["default_dims"]
    
    # Output directory based on provider
    emb_dir = EMB_BASE_DIR / args.provider
    
    print("=" * 60)
    print("TBTA Embedding Generator")
    print("=" * 60)
    print(f"Provider: {args.provider}")
    print(f"Model: {model_name}")
    print(f"Dimensions: {dims}")
    print(f"Output: {emb_dir}/")
    
    # Create output directory
    emb_dir.mkdir(parents=True, exist_ok=True)
    
    # Load encoder
    print("\nLoading encoder...")
    encoder = get_encoder(args.provider, model_name, dims)
    dims = encoder.dims  # Get actual dims from encoder
    print(f"  ✓ Encoder ready")
    
    # Create embeddings (pass encoder and output dir)
    create_verse_embeddings(encoder, dims, emb_dir)
    create_concept_embeddings(encoder, dims, emb_dir)
    
    if not args.skip_strongs:
        create_strongs_embeddings(encoder, dims, emb_dir, args.strongs_dir)
    
    # Summary
    print("\n" + "=" * 60)
    print("EMBEDDING GENERATION COMPLETE")
    print("=" * 60)
    
    print(f"\nCreated in {emb_dir}/:")
    for name in ["verse_vectors.sqlite", "concept_vectors.sqlite", "strongs_vectors.sqlite"]:
        path = emb_dir / name
        if path.exists():
            size = path.stat().st_size / 1024 / 1024
            print(f"  {name}: {size:.1f} MB")
    
    print("\nExample similarity search:")
    print('''
    import apsw, sqlite_vec, numpy as np
    from sentence_transformers import SentenceTransformer

    # Load model and encode query
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    query = "God's love for humanity"
    query_vec = model.encode(query, normalize_embeddings=True)
    query_int8 = np.clip(query_vec * 127, -127, 127).astype(np.int8)

    # Search
    db = apsw.Connection("embeddings/verse_vectors.sqlite")
    db.enable_load_extension(True)
    sqlite_vec.load(db)

    results = list(db.cursor().execute("""
        SELECT book, chapter, verse, distance
        FROM verse_vectors
        WHERE embedding MATCH vec_int8(?)
        ORDER BY distance
        LIMIT 10
    """, [query_int8.tobytes()]))

    for book, ch, vs, dist in results:
        print(f"{book} {ch}:{vs} (distance={dist:.3f})")
    ''')


if __name__ == "__main__":
    main()

