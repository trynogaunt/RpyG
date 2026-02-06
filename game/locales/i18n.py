import json
import os
from dataclasses import dataclass
from typing import Dict, Any, Optional


def _get_deep(d: Dict[str, Any], key: str) -> Optional[Any]:
    keys = key.split(".")
    current: Any = d
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current

@dataclass
class I18n:
    locale: str = "fr"
    fallback_locale: str = "en"
    
    def __post_init__(self):
        
    
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.locales_path = os.path.join(base_path)
        self.translations :  Dict[str, Any] = {}
        self.fallback_translations : Dict[str, Any] = {}
        self._cache : Dict[str, Any] = {}
        
        self.load_translations()    
    
    
    def load_translations(self):
        self.translations = self._load_locale_file(self.locale) or {}
        self.fallback_translations = self._load_locale_file(self.fallback_locale) or {}
        
        if not self.translations and self.locale != self.fallback_locale:
            print(f"Warning: No translations found for locale '{self.locale}'. \n Falling back to '{self.fallback_locale}'.")
            
        if not self.fallback_translations:
            print(f"Warning: No translations found for fallback locale '{self.fallback_locale}'.")
        
        if not self.translations and not self.fallback_translations:
            print("Warning: No translations found for both primary and fallback locales. All keys will return the key itself.")
            
        self._cache.clear()
    
    def _load_locale_file(self, locale: str) -> Optional[Dict[str, Any]]:
        path = os.path.join(self.locales_path, f"{locale}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                translations = json.load(f)
                return translations if isinstance(translations, dict) else {}
        except FileNotFoundError:
            print(f"Warning: Translation file for locale '{locale}' not found.")
            return {}
    
    def _resolve(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
        val = _get_deep(self.translations, key)
        if val is None:
            val = _get_deep(self.fallback_translations, key)
        if val is None:
            val = key
        self._cache[key] = val
        return val
        
    def t(self, key, count: Optional[int] = None, **kwargs):
        val = self._resolve(key)
        if isinstance(val, dict):
            n = count if count is not None else 1
            form = "one" if n == 1 else "other"
            val = val.get(form) or val.get("other") or val.get("one") or key
        if not isinstance(val, str):
            val = str(val)
        
        try:
            if count is not None and "count" not in kwargs:
                kwargs["count"] = count
            return val.format(**kwargs)
        except KeyError as e:
            missing = e.args[0] if e.args else "unknown"
            return f"{val} [Missing variable: {missing}]"