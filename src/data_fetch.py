# src/data_fetch.py  —  NOAA data download with robust caching
import os, io, requests
import pandas as pd
import numpy as np
from datetime import datetime

# ── Resolve project root regardless of cwd or __file__ format ────
_SRC_DIR     = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_SRC_DIR)

# ── Cache: use /tmp on cloud (read-only src), local data/ otherwise
_IS_CLOUD = "/mount/src" in _PROJECT_DIR or "/app" in _PROJECT_DIR
CACHE_DIR = "/tmp/enso_cache" if _IS_CLOUD else os.path.join(_PROJECT_DIR, "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def purge_stale_cache():
    """
    Delete any cache CSV that contains only pre-2025 data.
    Called once at module import so stale files never block fresh downloads.
    """
    if not os.path.exists(CACHE_DIR):
        return
    for fname in os.listdir(CACHE_DIR):
        if not fname.endswith(".csv"):
            continue
        fpath = os.path.join(CACHE_DIR, fname)
        try:
            df_chk = pd.read_csv(fpath)
            if "date" in df_chk.columns:
                dates = pd.to_datetime(df_chk["date"], errors="coerce").dropna()
                if not dates.empty and dates.max().year < 2025:
                    os.remove(fpath)
                    print(f"  [cache purge] Deleted stale file: {fname} "
                          f"(data ended {dates.max().strftime('%Y-%m')})")
        except Exception:
            pass


# Run purge on every import — fast (just reads header rows)
purge_stale_cache()

TIMEOUT    = 45
CACHE_SECS = 3 * 86400   # 3 days

# ── NOAA free data URLs ───────────────────────────────────────────
URLS = {
    "oni":          "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
    "nino_monthly": "https://www.cpc.ncep.noaa.gov/data/indices/ersst5.nino.mth.91-20.ascii",
    "soi":          "https://www.cpc.ncep.noaa.gov/data/indices/soi",
    "pdo":          "https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/pdo.timeseries.ersstv5.csv",
    "nao":          "https://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/norm.nao.monthly.b5001.current.ascii.table",
}


def _is_stale(path):
    """
    True if file should be re-downloaded. Conditions:
    1. File does not exist
    2. File is older than CACHE_SECS (3 days)
    3. File contains data only up to before 2025 (synthetic fallback data)
    Condition 3 is checked ALWAYS regardless of file age — this catches
    manually-placed synthetic files that have a fresh timestamp.
    """
    if not os.path.exists(path):
        return True
    # Always check data recency first — don't trust file age alone
    try:
        df_check = pd.read_csv(path)
        if "date" in df_check.columns:
            dates = pd.to_datetime(df_check["date"], errors="coerce").dropna()
            if dates.empty:
                return True
            if dates.max().year < 2025:
                print(f"  [cache] {os.path.basename(path)} has data only to "
                      f"{dates.max().strftime('%Y-%m')} — forcing fresh download")
                return True
    except Exception:
        return True   # unreadable = stale
    # Then check age
    age = datetime.now().timestamp() - os.path.getmtime(path)
    return age > CACHE_SECS


# ── ONI ───────────────────────────────────────────────────────────
def fetch_oni() -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "oni.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    try:
        r = requests.get(URLS["oni"], timeout=TIMEOUT)
        r.raise_for_status()
        SEASON_MONTH = {
            "DJF":1,"JFM":2,"FMA":3,"MAM":4,"AMJ":5,"MJJ":6,
            "JJA":7,"JAS":8,"ASO":9,"SON":10,"OND":11,"NDJ":12,
        }
        rows = []
        for line in r.text.strip().splitlines()[1:]:
            p = line.split()
            if len(p) >= 5:
                try:
                    seas, yr, anom = p[0], int(p[1]), float(p[4])
                    rows.append({
                        "season": seas, "year": yr,
                        "total": float(p[2]), "clim": float(p[3]),
                        "anom": anom,
                        "date": pd.Timestamp(year=yr, month=SEASON_MONTH.get(seas,1), day=1),
                    })
                except (ValueError, KeyError):
                    pass
        if not rows:
            raise ValueError("No rows parsed")
        result = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result.to_csv(cache, index=False)
        return result
    except Exception:
        if os.path.exists(cache):
            try:
                df_cached = pd.read_csv(cache, parse_dates=["date"])
                if not df_cached.empty and pd.to_datetime(df_cached["date"].max()).year >= 2025:
                    return df_cached
            except Exception:
                pass
        return _synthetic_oni()  # NOT saved to disk — forces retry on next start


def _synthetic_oni():
    dates = pd.date_range("1990-01-01", periods=438, freq="MS")
    n     = len(dates)
    t     = np.arange(n)
    anom  = 0.9*np.sin(2*np.pi*t/48) + 0.4*np.sin(2*np.pi*t/36) + np.random.default_rng(42).normal(0,.2,n)
    seas  = ["DJF","JFM","FMA","MAM","AMJ","MJJ","JJA","JAS","ASO","SON","OND","NDJ"]
    return pd.DataFrame({
        "season":[seas[i%12] for i in range(n)], "year":dates.year,
        "total":anom+27, "clim":27.0, "anom":anom, "date":dates,
    })


# ── Niño monthly ─────────────────────────────────────────────────
def fetch_nino_monthly() -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "nino_monthly.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    try:
        r = requests.get(URLS["nino_monthly"], timeout=TIMEOUT)
        r.raise_for_status()
        rows = []
        for line in r.text.strip().splitlines()[1:]:
            p = line.split()
            print("condition of NOAA data")
            if len(p) >= 10:
                try:
                    yr, mo = int(p[0]), int(p[1])
                    rows.append({
                        "date": pd.Timestamp(year=yr, month=mo, day=1),
                        "year":yr, "month":mo,
                        "nino12":float(p[2]), "nino12_anom":float(p[3]),
                        "nino3":float(p[4]),  "nino3_anom":float(p[5]),
                        "nino4":float(p[6]),  "nino4_anom":float(p[7]),
                        "nino34":float(p[8]), "nino34_anom":float(p[9]),
                    })
                except (ValueError, IndexError):
                    pass
        if not rows:
            raise ValueError("No rows parsed")
        result = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result.to_csv(cache, index=False)
        return result
    except Exception:
        if os.path.exists(cache):
            try:
                df_cached = pd.read_csv(cache, parse_dates=["date"])
                if not df_cached.empty and pd.to_datetime(df_cached["date"].max()).year >= 2025:
                    return df_cached
            except Exception:
                pass
        return _synthetic_nino()  # NOT saved to disk — forces retry on next start


def _synthetic_nino():
    dates = pd.date_range("1981-01-01", periods=546, freq="MS")
    n     = len(dates)
    rng   = np.random.default_rng(42)
    t     = np.arange(n)
    base  = 0.85*np.sin(2*np.pi*t/48)+0.3*np.sin(2*np.pi*t/36)+rng.normal(0,.15,n)
    return pd.DataFrame({
        "date":dates,"year":dates.year,"month":dates.month,
        "nino12_anom":base*1.3,"nino3_anom":base*1.1,
        "nino34_anom":base,"nino4_anom":base*0.65,
        "nino12":24.5+base*1.3,"nino3":26.5+base*1.1,
        "nino34":27.0+base,"nino4":28.5+base*0.65,
    })


# ── SOI ──────────────────────────────────────────────────────────
def fetch_soi() -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "soi.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    try:
        r = requests.get(URLS["soi"], timeout=TIMEOUT)
        r.raise_for_status()
        rows = []
        for line in r.text.strip().splitlines():
            p = line.split()
            if len(p) >= 13:
                try:
                    yr = int(p[0])
                    for mo, v in enumerate(p[1:13], 1):
                        val = float(v)
                        if val != -999.9:
                            rows.append({"date":pd.Timestamp(yr,mo,1),"year":yr,"month":mo,"soi":val})
                except ValueError:
                    pass
        if not rows:
            raise ValueError("No rows parsed")
        result = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result.to_csv(cache, index=False)
        return result
    except Exception:
        if os.path.exists(cache):
            try:
                df_cached = pd.read_csv(cache, parse_dates=["date"])
                if not df_cached.empty and pd.to_datetime(df_cached["date"].max()).year >= 2024:
                    return df_cached
            except Exception:
                pass
        return _synthetic_soi()  # NOT saved to disk


def _synthetic_soi():
    dates = pd.date_range("1950-01-01", periods=924, freq="MS")
    n     = len(dates)
    t     = np.arange(n)
    soi   = -1.5*np.sin(2*np.pi*t/48)+np.random.default_rng(123).normal(0,.5,n)
    return pd.DataFrame({"date":dates,"year":dates.year,"month":dates.month,"soi":soi})


# ── PDO ──────────────────────────────────────────────────────────
def fetch_pdo() -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "pdo.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    try:
        r = requests.get(URLS["pdo"], timeout=TIMEOUT)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date","pdo"]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna().query("pdo != -99.99").reset_index(drop=True)
        if df.empty:
            raise ValueError("Empty PDO")
        df.to_csv(cache, index=False)
        return df
    except Exception:
        if os.path.exists(cache):
            try:
                return pd.read_csv(cache, parse_dates=["date"])
            except Exception:
                pass
        dates = pd.date_range("1950-01-01", periods=924, freq="MS")
        t     = np.arange(924)
        return pd.DataFrame({"date":dates,"pdo":0.8*np.sin(2*np.pi*t/240)+np.random.default_rng(456).normal(0,.3,924)})


# ── NAO ──────────────────────────────────────────────────────────
def fetch_nao() -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "nao.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    try:
        r = requests.get(URLS["nao"], timeout=TIMEOUT)
        r.raise_for_status()
        rows = []
        for line in r.text.strip().splitlines():
            p = line.split()
            if len(p) >= 13:
                try:
                    yr = int(p[0])
                    for mo, v in enumerate(p[1:13], 1):
                        val = float(v)
                        if abs(val) < 99:
                            rows.append({"date":pd.Timestamp(yr,mo,1),"year":yr,"month":mo,"nao":val})
                except ValueError:
                    pass
        if not rows:
            raise ValueError("No rows")
        result = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
        result.to_csv(cache, index=False)
        return result
    except Exception:
        if os.path.exists(cache):
            try:
                return pd.read_csv(cache, parse_dates=["date"])
            except Exception:
                pass
        dates = pd.date_range("1950-01-01", periods=924, freq="MS")
        t     = np.arange(924)
        return pd.DataFrame({"date":dates,"year":dates.year,"month":dates.month,
                              "nao":0.5*np.sin(2*np.pi*t/60)+np.random.default_rng(789).normal(0,.8,924)})


# ── IOD (approximate) ────────────────────────────────────────────
def fetch_iod(nino_df: pd.DataFrame = None) -> pd.DataFrame:
    cache = os.path.join(CACHE_DIR, "iod.csv")
    if not _is_stale(cache):
        return pd.read_csv(cache, parse_dates=["date"])
    rng = np.random.default_rng(999)
    if nino_df is not None and len(nino_df) > 0:
        n    = len(nino_df)
        enso = nino_df["nino34_anom"].values if "nino34_anom" in nino_df.columns else np.zeros(n)
        iod  = 0.4*enso + 0.6*(0.5*np.sin(2*np.pi*np.arange(n)/48)+rng.normal(0,.3,n))
        result = pd.DataFrame({"date":nino_df["date"].values,"iod":iod})
    else:
        dates = pd.date_range("1981-01-01", periods=546, freq="MS")
        t     = np.arange(500)
        result = pd.DataFrame({"date":dates,"iod":0.5*np.sin(2*np.pi*t/48)+rng.normal(0,.3,500)})
    result.to_csv(cache, index=False)
    return result


# ── Master loader ─────────────────────────────────────────────────
def load_all_data():
    oni  = fetch_oni()
    nino = fetch_nino_monthly()
    soi  = fetch_soi()
    pdo  = fetch_pdo()
    nao  = fetch_nao()
    iod  = fetch_iod(nino)
    return {"oni":oni,"nino":nino,"soi":soi,"pdo":pdo,"nao":nao,"iod":iod}
