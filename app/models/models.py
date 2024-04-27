from typing import Union, Optional
from fastapi import Cookie

from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    name: str
    email: str
    age: int
    is_subscribed: bool


class Feedback(BaseModel):
    name: str
    message: str


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float
