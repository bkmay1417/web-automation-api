# scraper_combined.py
from playwright.async_api import async_playwright
import asyncio
import postgreSQL  # tu módulo para PostgreSQL
import uuid

async def scrape_products(task_id=None, lookup_key=None):
    """
    Función principal para scrapear productos.
    task_id: identificador del sitio (ej: "saucedemo" o "practice_site") - obligatorio
    lookup_key: filtro opcional por nombre de producto
    """
    if not task_id:
        raise ValueError("Debes ingresar un task_id válido, por ejemplo 'saucedemo' o 'practice_site'")

    # Asegurar que las tablas existan
    postgreSQL.create_database_if_not_exists()
    postgreSQL.create_tables_if_not_exists()

    products = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        if task_id == "saucedemo":
            # --- Scraper SauceDemo ---
            await page.goto("https://www.saucedemo.com/")
            await page.fill("#user-name", "standard_user")
            await page.fill("#password", "secret_sauce")
            await page.click("#login-button")
            await page.wait_for_selector(".inventory_list")
            items = await page.query_selector_all(".inventory_item")

            if lookup_key:
                encontrado = False
                for item in items:
                    name = await (await item.query_selector(".inventory_item_name")).inner_text()
                    if name.lower() == lookup_key.lower():
                        description = await (await item.query_selector(".inventory_item_desc")).inner_text()
                        price_str = await (await item.query_selector(".inventory_item_price")).inner_text()
                        img_rel = await (await item.query_selector(".inventory_item_img img")).get_attribute("src")
                        price = float(price_str.replace("$", ""))
                        products.append({
                            "name": name,
                            "description": description,
                            "price": price,
                            "image_url": img_rel
                        })
                        encontrado = True
                        break
                if not encontrado:
                    raise ValueError(f"No se encontró ningún producto con el nombre '{lookup_key}'")
            else:
                for item in items:
                    name = await (await item.query_selector(".inventory_item_name")).inner_text()
                    description = await (await item.query_selector(".inventory_item_desc")).inner_text()
                    price_str = await (await item.query_selector(".inventory_item_price")).inner_text()
                    img_rel = await (await item.query_selector(".inventory_item_img img")).get_attribute("src")
                    price = float(price_str.replace("$", ""))
                    products.append({
                        "name": name,
                        "description": description,
                        "price": price,
                        "image_url": img_rel
                    })

        elif task_id == "practice_site":
            # --- Scraper Practice Software Testing ---
            await page.goto("https://practicesoftwaretesting.com")

            # Mover slider a 0-200
            try:
                await page.wait_for_timeout(2000)  # esperar que Angular cargue
                slider_min = await page.wait_for_selector(".ngx-slider-pointer-min", state="visible", timeout=10000)
                slider_max = await page.wait_for_selector(".ngx-slider-pointer-max", state="visible", timeout=10000)
                await page.evaluate("""
                (min_handle, max_handle) => {
                    min_handle.setAttribute('aria-valuenow', '0');
                    min_handle.style.left = '0px';
                    max_handle.setAttribute('aria-valuenow', '200');
                    max_handle.style.left = '124px';
                    min_handle.dispatchEvent(new Event('change'));
                    max_handle.dispatchEvent(new Event('change'));
                }
                """, slider_min, slider_max)
            except Exception as e:
                print(f"No se encontró el slider o no se pudo mover: {e}")

            # Recorrer paginación
            while True:
                await page.wait_for_selector("a.card")
                items = await page.query_selector_all("a.card")

                for item in items:
                    name = await (await item.query_selector(".card-title")).inner_text()
                    price_str = await (await item.query_selector("[data-test='product-price']")).inner_text()
                    img_url = await (await item.query_selector("img.card-img-top")).get_attribute("src")
                    price = float(price_str.replace("$", ""))

                    if lookup_key:
                        if name.lower() == lookup_key.lower():
                            products.append({
                                "name": name,
                                "price": price,
                                "image_url": img_url
                            })
                            break
                    else:
                        products.append({
                            "name": name,
                            "price": price,
                            "image_url": img_url
                        })

                if lookup_key and products:
                    break

                next_button = await page.query_selector("ul.pagination li:last-child:not(.disabled) a.page-link")
                if next_button:
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    break

        await browser.close()

    # Guardar en DB con un job_id único
    job_id = str(uuid.uuid4())
    postgreSQL.create_task(job_id)
    try:
        postgreSQL.insert_data_for_job(job_id, products)
        postgreSQL.update_task_status(job_id, "completed")
    except Exception as e:
        postgreSQL.update_task_status(job_id, "failed", str(e))

    return job_id, products

# Ejecución directa para test
if __name__ == "__main__":
    # Para SauceDemo: scrape_products("saucedemo")
    # Para Practice: scrape_products("practice_site")
    asyncio.run(scrape_products(task_id="practice_site"))
