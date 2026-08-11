from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = 'https://www.linkedin.com/jobs/search/'


def build_search_url(keywords: str, location: str) -> str:
    query = urlencode({'keywords': keywords, 'location': location})
    return '{}?{}'.format(BASE_URL, query)


def create_driver(headless: bool) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(options=options)


def text_or_default(card, selector: str, default: str = 'Nao informado') -> str:
    try:
        value = card.find_element(By.CSS_SELECTOR, selector).text.strip()
        return value or default
    except NoSuchElementException:
        return default


def collect_jobs(keywords: str, location: str, limit: int, headless: bool, wait_seconds: int) -> list[dict[str, str]]:
    driver = create_driver(headless)
    try:
        driver.get(build_search_url(keywords, location))
        cards = WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.base-card'))
        )

        jobs: list[dict[str, str]] = []
        seen: set[tuple[str, str, str]] = set()
        for card in cards:
            if len(jobs) >= limit:
                break
            title = text_or_default(card, 'h3.base-search-card__title')
            company = text_or_default(card, 'h4.base-search-card__subtitle')
            job_location = text_or_default(card, 'span.job-search-card__location')
            try:
                link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute('href') or ''
            except NoSuchElementException:
                link = ''

            key = (title, company, job_location)
            if key in seen:
                continue
            seen.add(key)
            jobs.append({
                'titulo': title,
                'empresa': company,
                'localizacao': job_location,
                'link': link,
            })
        return jobs
    except TimeoutException:
        raise RuntimeError('Nenhum cartao de vaga foi encontrado no tempo esperado.')
    finally:
        driver.quit()


def save_jobs(jobs: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(jobs, columns=['titulo', 'empresa', 'localizacao', 'link'])
    if output.suffix.lower() == '.xlsx':
        frame.to_excel(output, index=False)
    else:
        frame.to_csv(output, index=False, encoding='utf-8-sig')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Coleta vagas publicas para fins educacionais.')
    parser.add_argument('--keywords', default='desenvolvedor python', help='Termo pesquisado.')
    parser.add_argument('--location', default='Brasil', help='Localizacao pesquisada.')
    parser.add_argument('--limit', type=int, default=20, help='Numero maximo de vagas.')
    parser.add_argument('--output', type=Path, default=Path('vagas_linkedin.csv'), help='Arquivo CSV ou XLSX de saida.')
    parser.add_argument('--headed', action='store_true', help='Exibe o navegador durante a coleta.')
    parser.add_argument('--wait', type=int, default=10, help='Tempo maximo de espera em segundos.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit < 1:
        raise ValueError('O limite deve ser maior que zero.')

    jobs = collect_jobs(
        keywords=args.keywords,
        location=args.location,
        limit=args.limit,
        headless=not args.headed,
        wait_seconds=args.wait,
    )
    save_jobs(jobs, args.output)
    print('{} vagas salvas em {}'.format(len(jobs), args.output))


if __name__ == '__main__':
    main()
