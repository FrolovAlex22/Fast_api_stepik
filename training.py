import requests


client_cert_path = 'sertificate/client2024test.crt'
client_key_path = 'sertificate/client2024test.key'
response = requests.get('https://slb.medv.ru/api/v2/', cert=(client_cert_path, client_key_path),  verify=True )
print(response)
