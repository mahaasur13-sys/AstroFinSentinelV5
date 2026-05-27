## A/B Testing API

Сравнение двух торговых сессий через эндпоинт `/api/ab/compare`.

- **Метод:** GET
- **Параметры строки запроса:**
  - `sid_a` – ID первой сессии
  - `sid_b` – ID второй сессии
- **Пример запроса:**
  ```bash
  curl "http://localhost:8000/api/ab/compare?sid_a=7409439d&sid_b=e19fc7dc"
  ```
- **Пример ответа:**
  ```json
  {
    "status": "OK",
    "sid_a": "7409439d",
    "sid_b": "e19fc7dc",
    "mode": "proxy_confidence",
    "mean_a": 0.5,
    "mean_b": 0.5,
    "n_a": 5,
    "n_b": 5,
    "p_value": 1.0,
    "effect_size": 0.0,
    "confidence": "LOW (proxy)",
    "winner": "TIE"
  }
  ```
- **Интерпретация:**
  - `p_value` < 0.05 → статистически значимое различие.
  - `effect_size` (Cohens d): 0.2 – малый, 0.5 – средний, 0.8 – большой.
  - `winner` указывает, какая сессия показала лучший результат, или `TIE`.
