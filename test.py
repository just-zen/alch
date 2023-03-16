from requests import get

print(get('http://localhost:5000/api/v2/news').json())

print(get('http://localhost:5000/api/v2/news/1').json())

print(get('http://localhost:5000/api/v2/news/999').json())
