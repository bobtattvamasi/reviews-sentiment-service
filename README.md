# Reviews Sentiment Service

Мини-сервис на FastAPI + SQLite, который принимает отзыв, оценивает его настроение и сохраняет в БД.

## Установка

```bash
pip install fastapi uvicorn
```

## Запуск  

```bash
uvicorn main:app --reload
или
python main.py
```

## Примеры запросов  

### Создать отзыв  
```bash
curl -X POST http://localhost:8000/reviews \
     -H "Content-Type: application/json" \
     -d '{"text":"Мне очень понравилось!"}'
```

### Получить все отзывы  
```bash
curl http://localhost:8000/reviews
```

### Получить только негативные  
```bash
curl http://localhost:8000/reviews?sentiment=negative
```

