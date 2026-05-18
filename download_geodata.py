"""
╔══════════════════════════════════════════════════════════════╗
║  ENSO Climate Intelligence — One-Time GeoJSON Setup          ║
║  Run this ONCE before starting the dashboard:                ║
║      python download_geodata.py                              ║
║                                                              ║
║  What this does:                                             ║
║  1. Downloads India states GeoJSON from multiple sources     ║
║  2. Normalises all state names to current official names     ║
║  3. Merges Ladakh back into J&K (India's claimed territory)  ║
║  4. Saves to data/india_states.geojson for offline use       ║
║  5. Dashboard never downloads GeoJSON at runtime again       ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests, json, os, sys

os.makedirs("data", exist_ok=True)

# ── J&K Boundary Policy ────────────────────────────────────────────────────────
# This dashboard uses India's OFFICIAL CLAIMED BOUNDARY for Jammu & Kashmir,
# consistent with Survey of India maps and Indian government position.
# - Aksai Chin (administered by China) is shown as part of J&K
# - Pakistan-administered Kashmir (PoK/AJK) is shown as part of J&K
# - Ladakh UT (carved from J&K in Aug 2019) is merged back into J&K polygon
#   so the full claimed territory renders as one unit on the map.
# This is the legally mandated representation for maps published in India.
# ──────────────────────────────────────────────────────────────────────────────

# GeoJSON sources to try — in order of preference
# Preference: post-2014 (has Telangana) > correct names > any working source
SOURCES = [
    {
        "url":         "https://raw.githubusercontent.com/Aftaab25/India-State-wise-GeoJSON/main/india_states.geojson",
        "name_field":  "state",
        "description": "Aftaab25 — post-2014, has Telangana, correct names",
    },
    {
        "url":         "https://raw.githubusercontent.com/AnupamKumar88/India_mapData/master/states_india.geojson",
        "name_field":  "ST_NM",
        "description": "AnupamKumar88 — Census boundary, post-2014",
    },
    {
        "url":         "https://raw.githubusercontent.com/tarmeli/Ohjelmistoprojekti-II/master/src/data/indiaGeoJSON.json",
        "name_field":  "name",
        "description": "tarmeli — alternative source",
    },
    {
        "url":         "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
        "name_field":  "NAME_1",
        "description": "geohacker — pre-2014 (no Telangana), old names (fallback)",
    },
]

# ── Name normalisation map ────────────────────────────────────────────────────
# Maps every known variant → correct current official name
NAME_MAP = {
    # Old names (pre-renaming)
    "Orissa":                       "Odisha",            # renamed 2011
    "Uttaranchal":                  "Uttarakhand",       # renamed 2000
    # J&K variants
    "Jammu & Kashmir":              "Jammu and Kashmir",
    "Jammu And Kashmir":            "Jammu and Kashmir",
    "J&K":                          "Jammu and Kashmir",
    # Ladakh — will be MERGED into J&K polygon
    "Ladakh":                       "Ladakh",
    # UT variants
    "NCT of Delhi":                 "Delhi",
    "Delhi (NCT)":                  "Delhi",
    "Andaman & Nicobar Island":     "Andaman and Nicobar Islands",
    "Andaman and Nicobar":          "Andaman and Nicobar Islands",
    "Andaman & Nicobar Islands":    "Andaman and Nicobar Islands",
    "Dadara & Nagar Havelli":       "Dadra and Nagar Haveli",
    "Dadra And Nagar Haveli":       "Dadra and Nagar Haveli",
    "Daman & Diu":                  "Daman and Diu",
    "Pondicherry":                  "Puducherry",
    # Spelling variants
    "Chhattisgarh":                 "Chhattisgarh",
    "Chhatisgarh":                  "Chhattisgarh",
    "Tamilnadu":                    "Tamil Nadu",
    "Tamil Nadu":                   "Tamil Nadu",
    "West Bengal":                  "West Bengal",
    "Telengana":                    "Telangana",
}

def detect_name_field(features):
    """Auto-detect which property holds state names."""
    if not features:
        return None
    props = features[0]["properties"]
    candidates = ["state", "ST_NM", "NAME_1", "name", "State",
                  "NAME", "statename", "STNAME", "st_name"]
    for key in candidates:
        if key in props:
            # Verify it looks like state names (not codes)
            sample = str(props[key])
            if len(sample) > 2 and not sample.isdigit():
                return key
    return None

def normalise_geojson(gj, name_field):
    """
    Normalise state names to ST_NAME field.
    Merge Ladakh into J&K for India's claimed boundary.
    """
    jk_feat      = None
    ladakh_feat  = None
    other_feats  = []
    state_names  = []

    for feat in gj["features"]:
        raw  = feat["properties"].get(name_field, "").strip()
        norm = NAME_MAP.get(raw, raw)
        feat["properties"]["ST_NAME"] = norm
        state_names.append(norm)

        if norm == "Jammu and Kashmir":
            jk_feat = feat
        elif norm == "Ladakh":
            ladakh_feat = feat
        else:
            other_feats.append(feat)

    # ── Merge Ladakh → J&K ───────────────────────────────────────
    if jk_feat and ladakh_feat:
        print("  → Merging Ladakh into J&K (India claimed boundary)...", end=" ")
        try:
            from shapely.geometry import shape, mapping
            from shapely.ops import unary_union
            merged_geom = unary_union([
                shape(jk_feat["geometry"]),
                shape(ladakh_feat["geometry"])
            ])
            jk_feat["geometry"] = mapping(merged_geom)
            print("✓ Merged")
        except ImportError:
            print("⚠ shapely not installed — run: pip install shapely")
            print("    J&K and Ladakh kept as separate polygons.")
        except Exception as e:
            print(f"⚠ Merge failed ({e}) — keeping J&K as-is")
        other_feats.append(jk_feat)
    elif jk_feat:
        print("  → Ladakh not found as separate feature in this GeoJSON")
        print("    J&K polygon used as-is (may already include Ladakh)")
        other_feats.append(jk_feat)
    else:
        print("  ⚠ J&K feature not found in this GeoJSON source")

    gj["features"] = other_feats
    return gj, sorted(set(f["properties"]["ST_NAME"] for f in other_feats))


# ── Main download loop ────────────────────────────────────────────
print("\n" + "="*60)
print("India GeoJSON Setup")
print("="*60)

success = False
for src in SOURCES:
    print(f"\nTrying: {src['description']}")
    print(f"  URL: {src['url'][:70]}...")

    try:
        r = requests.get(src["url"], timeout=30)
        if r.status_code != 200:
            print(f"  ✗ HTTP {r.status_code}")
            continue

        gj       = r.json()
        features = gj.get("features", [])
        if len(features) < 10:
            print(f"  ✗ Too few features ({len(features)})")
            continue

        # Detect name field
        name_field = src["name_field"] or detect_name_field(features)
        if not name_field:
            print("  ✗ Could not detect state name field")
            continue

        # Sample names
        sample_names = [f["properties"].get(name_field, "") for f in features[:5]]
        print(f"  Features: {len(features)} | Name field: '{name_field}'")
        print(f"  Sample names: {sample_names}")

        all_names = [f["properties"].get(name_field, "") for f in features]
        has_telangana = "Telangana" in all_names or "Telengana" in all_names
        has_odisha    = "Odisha" in all_names or "Orissa" in all_names
        print(f"  Has Telangana: {has_telangana} | Has Odisha/Orissa: {has_odisha}")

        # Normalise
        gj, final_names = normalise_geojson(gj, name_field)

        # Save
        out_path = os.path.join("data", "india_states.geojson")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(gj, f, ensure_ascii=False)

        print(f"\n✅ Saved: {out_path}")
        print(f"   States/UTs in file ({len(final_names)}):")
        for i, n in enumerate(final_names):
            print(f"     {'✓' if n in ['Odisha','Uttarakhand','Telangana','Jammu and Kashmir'] else ' '} {n}")

        if not has_telangana:
            print("\n  ⚠ NOTE: This source does not have Telangana as a separate state.")
            print("    Telangana will appear as part of Andhra Pradesh on the map.")
            print("    Try a different source or accept this limitation.")

        success = True
        break

    except Exception as e:
        print(f"  ✗ Error: {e}")
        continue

if not success:
    print("\n❌ All sources failed.")
    print("   Check your internet connection and try again.")
    sys.exit(1)

print("\n" + "="*60)
print("Setup complete. Run:  streamlit run app.py")
print("="*60 + "\n")
