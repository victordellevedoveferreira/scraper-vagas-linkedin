from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time

options = Options()
driver = webdriver.Chrome(options=options)

vaga = "desenvolvedor python"
url = f"https://www.linkedin.com/jobs/search/?keywords={vaga}&location=Brazil&geoId=106057199"

driver.get(url)
time.sleep(4)

vagas = driver.find_elements(By.CLASS_NAME, "base-card")

print(f"Encontrei {len(vagas)} vagas!\n")

lista_vagas = []

for vaga in vagas:
    try:
        # Título
        try:
            titulo = vaga.find_element(By.CLASS_NAME, "base-search-card__title").text.strip()
        except:
            titulo = "Não informado"

        # Empresa
        try:
            empresa = vaga.find_element(By.CLASS_NAME, "base-search-card__subtitle").text.strip()
            if empresa == "":
                empresa = "Não informado"
        except:
            empresa = "Não informado"

        # Localização
        try:
            localizacao = vaga.find_element(By.CLASS_NAME, "job-search-card__location").text.strip()
        except:
            localizacao = "Não informado"

        # Link
        try:
            link = vaga.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = "Não informado"

        lista_vagas.append({
            "Título": titulo,
            "Empresa": empresa,
            "Localização": localizacao,
            "Link": link
        })
    except:
        pass

driver.quit()

tabela = pd.DataFrame(lista_vagas)
tabela.to_excel("vagas_linkedin.xlsx", index=False)

print(f"✅ Arquivo salvo com {len(tabela)} vagas!")
print("📁 Procura o arquivo 'vagas_linkedin.xlsx' na pasta scraper-vagas")