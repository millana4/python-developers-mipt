from fastapi import FastAPI
from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional
from datetime import date, datetime
import json
import re

app = FastAPI(
    title="Сервис обращений абонентов",
    description="API для сбора обращений абонентов",
    version="1.0.0"
)


class SubscriberAppeal(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    last_name: str
    first_name: str
    birth_date: date
    phone_number: str
    email: str  # Обычная строка вместо EmailStr

    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        v = v.strip()
        if not v or not v[0].isupper():
            raise ValueError('Фамилия должна начинаться с заглавной буквы')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', v):
            raise ValueError('Фамилия должна содержать только кириллические символы')
        return v

    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        v = v.strip()
        if not v or not v[0].isupper():
            raise ValueError('Имя должно начинаться с заглавной буквы')
        if not re.match(r'^[А-Яа-яЁё\s-]+$', v):
            raise ValueError('Имя должно содержать только кириллические символы')
        return v

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        cleaned = re.sub(r'[\s\(\)\-+]', '', v)
        if not cleaned.isdigit():
            raise ValueError('Номер телефона должен содержать только цифры')
        if len(cleaned) < 10:
            raise ValueError('Номер телефона слишком короткий')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Неверный формат email')
        return v


@app.post("/appeal/", summary="Создать обращение абонента")
async def create_appeal(appeal: SubscriberAppeal):
    appeal_data = appeal.model_dump()
    appeal_data['birth_date'] = appeal_data['birth_date'].isoformat()

    filename = f"appeal_{appeal.last_name}_{appeal.first_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(appeal_data, f, ensure_ascii=False, indent=2)

    return {
        "message": "Обращение успешно создано",
        "filename": filename,
        "data": appeal_data
    }


if __name__ == "__main__":
    import uvicorn
    # посмотреть http://127.0.0.1:8000/docs
    uvicorn.run(app, host="0.0.0.0", port=8000)