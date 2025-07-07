import asyncio
import json
import sys  # Para redirecionamento de print
import requests  # Para suportar chamadas HTTP
import pyodide_http

pyodide_http.patch_all()  # Habilita requests para Pyodide

FPS = 60

async def get_token(api_key):
    url = "https://api.godigibee.io/pipeline/braskem/v1/api-token?apikey={{apiKey}}"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": "{{apiKey}}",
        "client_secret": "{{apiKey}}",  # Substitua por client_secret real se diferente
        "scope": "token-oauth",
        "grant_type": "client_credentials"
    }
    try:
        response = await asyncio.to_thread(
            lambda: requests.post(url.replace("{{apiKey}}", api_key), headers=headers, data=data, timeout=10)
        )
        print(f"Debug - Get Token Response Status: {response.status_code}")
        print(f"Debug - Get Token Response Text: {response.text}")
        response.raise_for_status()
        token_data = response.json()
        token = token_data.get("access_token")
        if not token:
            print("Erro: Nenhum token de acesso retornado.")
            return None
        return token
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token: {e}")
        return None

async def consulta_pedagio(token, api_key, cnpj, doc_transporte):
    # Tenta proxy corsproxy.io como alternativa
    url = "https://corsproxy.io/?https://api.godigibee.io/pipeline/braskem/v1/consulta-pedagio"
    headers = {
        "Authorization": f"Bearer {token}",
        "apiKey": api_key,
        "Origin": "https://leovunschel.github.io"  # Adicionado para ajudar no CORS
    }
    payload = {
        "CNPJ": cnpj,
        "DOC_TRANSPORTE": doc_transporte
    }
    try:
        response = await asyncio.to_thread(
            lambda: requests.post(url, headers=headers, json=payload, timeout=10)
        )
        print(f"Debug - Consulta Pedágio Response Status: {response.status_code}")
        print(f"Debug - Consulta Pedágio Response Text: {response.text}")
        print(f"Debug - Consulta Pedágio Headers: {dict(response.headers)}")  # Converte headers para dict
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na consulta: {e}")
        print(f"Detalhes do erro: Status={getattr(response, 'status_code', 'N/A')}, Text={getattr(response, 'text', 'N/A')}, Headers={getattr(response, 'headers', 'N/A')}")
        return None

async def main(cnpj, doc_transporte):
    api_key = "0zNDZtPILsLDslv04FCnNkjRIpiWBkFi"  # API Key fornecida pela Braskem
    if len(doc_transporte) < 4:
        print("Erro: DOC_TRANSPORTE deve ter pelo menos 4 caracteres.")
        return
    token = await get_token(api_key)
    if not token:
        print("Falha ao obter token.")
        return
    dados = await consulta_pedagio(token, api_key, cnpj, doc_transporte)
    if dados:
        print("Dados de Vale Pedágio:")
        for key, value in dados.items():
            if isinstance(value, dict):
                print(f"{key}:")
                for subkey, subvalue in value.items():
                    print(f"  {subkey}: {subvalue}")
            else:
                print(f"{key}: {value}")
    else:
        print("Nenhum dado retornado pela API.")